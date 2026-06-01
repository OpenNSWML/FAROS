"""
Paper orchestrator using skill-based pipeline.

Each skill emits intermediate artifacts under: artifacts/<step>.{json,md}
"""

import logging
import time
from typing import Any, Dict

from app.core.settings import get_settings
from app.llm.provider_client import get_provider_client
from app.modules.paper.storage import add_log, get_paper, get_paper_latex_dir, update_paper
from app.modules.paper.skills import PaperSkillContext, PaperSkillLeader, build_default_skill_chain
from app.modules.paper.skills.constants import VENUE_CONFIGS
from app.modules.paper.skills.utils import ensure_artifacts_dir

logger = logging.getLogger(__name__)


def generate_paper(paper_id: str) -> Dict[str, Any]:
    paper = get_paper(paper_id)
    if not paper:
        raise ValueError(f"Paper not found: {paper_id}")

    settings = get_settings()
    provider_name = paper.get("providerName") or settings.get_active_provider()
    model = paper.get("model") or settings.get_active_model(provider_name)
    paper_type = paper.get("paperType", "algorithm")
    venue = paper.get("targetVenue", "generic")
    venue_cfg = VENUE_CONFIGS.get(venue, VENUE_CONFIGS["generic"])

    update_paper(paper_id, {"status": "generating"})
    step_log = []

    def _log(msg: str) -> None:
        add_log(paper_id, msg)
        step_log.append({"time": time.time(), "msg": msg})
        logger.info(f"[{paper_id}] {msg}")

    try:
        client = get_provider_client(provider_name)
        latex_dir = get_paper_latex_dir(paper_id)
        artifacts_dir = ensure_artifacts_dir(paper_id)

        ctx = PaperSkillContext(
            paper_id=paper_id,
            paper=paper,
            settings=settings,
            provider_name=provider_name,
            model=model,
            paper_type=paper_type,
            venue=venue,
            venue_cfg=venue_cfg,
            client=client,
            latex_dir=latex_dir,
            artifacts_dir=artifacts_dir,
            data={},
            step_log=step_log,
        )

        leader = PaperSkillLeader(paper_id, _log)
        skills = build_default_skill_chain()
        leader.run(ctx, skills)

        outline = ctx.get("outline", {})
        references = outline.get("references", [])
        sections = outline.get("sections", [])
        figure_entries = ctx.get("figure_entries", [])
        evidence_gates = ctx.get("evidence_gates", {})
        pdf_available = ctx.get("pdf_available", False)

        update_paper(paper_id, {
            "status": "completed",
            "targetVenue": venue,
            "templateId": venue,
            "evidenceGates": evidence_gates,
            "figureCount": len(figure_entries),
            "sectionCount": len(sections),
            "referenceCount": len(references),
            "pdfAvailable": pdf_available,
        })
        _log("Paper generation completed successfully")

    except Exception as exc:
        logger.error(f"Paper generation failed: {exc}", exc_info=True)
        update_paper(paper_id, {"status": "failed"})
        add_log(paper_id, f"FAILED: {str(exc)[:500]}")
        raise

    return get_paper(paper_id)
