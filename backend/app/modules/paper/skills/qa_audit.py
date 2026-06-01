from .base import PaperSkillContext, PaperSkillResult
from .utils import write_artifact


STEP_ID = "09_qa_audit"


def run(ctx: PaperSkillContext) -> PaperSkillResult:
    outline_issues = ctx.get("outline_gate_issues", [])
    evidence_gates = ctx.get("evidence_gates", {})
    summary_lines = [
        "# QA / Audit",
        f"outline_issues: {len(outline_issues)}",
        f"evidence_all_pass: {evidence_gates.get('all_pass')}",
    ]
    artifacts = write_artifact(
        ctx.paper_id,
        STEP_ID,
        {
            "outline_issues": outline_issues,
            "evidence_gates": evidence_gates,
        },
        summary_lines,
    )
    return PaperSkillResult(
        name="qa_audit",
        summary="complete",
        artifacts=artifacts,
        data={"qa_summary": {"outline_issues": outline_issues, "evidence_gates": evidence_gates}},
    )
