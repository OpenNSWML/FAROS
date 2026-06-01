from app.modules.paper.storage import write_paper_file
from .base import PaperSkillContext, PaperSkillResult
from .utils import build_bibtex, build_main_tex, copy_template_assets, write_artifact


STEP_ID = "07_assemble_latex"


def run(ctx: PaperSkillContext) -> PaperSkillResult:
    outline = ctx.get("outline", {})
    sections = ctx.get("sections", [])
    refs = outline.get("references", [])

    copy_template_assets(ctx.venue, ctx.paper_id)
    main_tex = build_main_tex(outline, sections, ctx.venue)
    write_paper_file(ctx.paper_id, "main.tex", main_tex)

    bibtex = build_bibtex(refs)
    write_paper_file(ctx.paper_id, "refs.bib", bibtex)

    readme_content = f"# {outline.get('title', ctx.paper.get('title', 'Paper'))}\n\n"
    readme_content += f"**Paper type:** {ctx.paper_type}  \n"
    readme_content += f"**Target venue:** {ctx.venue_cfg['name']}  \n\n"
    readme_content += "## Build Instructions\n\n"
    readme_content += "```bash\n# Option 1: latexmk (recommended)\nlatexmk -pdf main.tex\n\n"
    readme_content += "# Option 2: manual\npdflatex main.tex\nbibtex main\npdflatex main.tex\npdflatex main.tex\n```\n\n"
    readme_content += "## Structure\n\n```\n"
    readme_content += "main.tex          # Main document\n"
    readme_content += "refs.bib          # Bibliography\n"
    readme_content += "sections/         # Individual sections\n"
    for s in sections:
        readme_content += f"  {s['id']}.tex      # {s.get('title', s['id'])}\n"
    readme_content += "figures/          # Generated figures\n"
    readme_content += "```\n"
    write_paper_file(ctx.paper_id, "README.md", readme_content)

    summary_lines = [
        "# Assemble LaTeX",
        f"sections: {len(sections)}",
        f"refs: {len(refs)}",
    ]
    artifacts = write_artifact(
        ctx.paper_id,
        STEP_ID,
        {"sections": len(sections), "references": len(refs)},
        summary_lines,
    )
    return PaperSkillResult(
        name="assemble_latex",
        summary="LaTeX assembled",
        artifacts=artifacts,
        data={},
    )
