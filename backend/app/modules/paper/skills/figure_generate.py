from .base import PaperSkillContext, PaperSkillResult
from .utils import write_artifact


STEP_ID = "06_figure_generate"


def run(ctx: PaperSkillContext) -> PaperSkillResult:
    figures_dir = f"{ctx.latex_dir}/figures"
    try:
        from app.services.figure_generator import generate_all_figures
        figure_entries = generate_all_figures(figures_dir, ctx.paper.get("title", "Paper"))
        summary = f"{len(figure_entries)} figure(s)"
    except Exception as exc:
        figure_entries = []
        summary = f"warning: {str(exc)[:200]}"

    summary_lines = [
        "# Figure Generate",
        f"count: {len(figure_entries)}",
    ]
    artifacts = write_artifact(
        ctx.paper_id,
        STEP_ID,
        {"figures": figure_entries},
        summary_lines,
    )
    return PaperSkillResult(
        name="figure_generate",
        summary=summary,
        artifacts=artifacts,
        data={"figure_entries": figure_entries},
    )
