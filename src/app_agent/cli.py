from pathlib import Path
import typer
from rich.console import Console
from app_agent.chat import run_chat
from app_agent.graph import build_graph
from app_agent.models import JobInput

app = typer.Typer(help="Forward-Deployed GenAI Workflow Agent")
console = Console()


@app.command()
def chat():
    """Interactive chat: paste a JD or URL, ask follow-up questions about results."""
    run_chat()


@app.command()
def run(
    text_file: str = typer.Option(None, help="Path to a text file containing a job description."),
    url: str = typer.Option(None, help="Job posting URL."),
    output: str = typer.Option("examples/sample_application_pack.md", help="Output markdown file."),
):
    if not text_file and not url:
        raise typer.BadParameter("Provide either --text-file or --url")

    if text_file:
        content = Path(text_file).read_text(encoding="utf-8")
        job_input = JobInput(source_type="text", content=content)
    else:
        job_input = JobInput(source_type="url", content=url)

    graph = build_graph()
    result = graph.invoke({"job_input": job_input})
    pack = result["application_pack"]

    markdown = render_application_pack(pack)
    Path(output).write_text(markdown, encoding="utf-8")
    console.print(f"Application pack written to {output}")


def render_application_pack(pack) -> str:
    return f"""# Application Intelligence Pack

## Role

{pack.requirements.job_title}

## Company

{pack.requirements.company or "Unknown"}

## Fit Score

{pack.match_analysis.overall_fit_score}/100

## Strongest Selling Points

{chr(10).join(f"- {item}" for item in pack.match_analysis.strongest_selling_points)}

## Critical Gaps

{chr(10).join(f"- {item}" for item in pack.gap_analysis.critical_gaps)}

## Manageable Gaps

{chr(10).join(f"- {item}" for item in pack.gap_analysis.manageable_gaps)}

## Mitigation Strategy

{chr(10).join(f"- {item}" for item in pack.gap_analysis.mitigation_strategy)}

## Tailored CV Bullets

{chr(10).join(f"- {item}" for item in pack.generated_assets.cv_bullets)}

## Recruiter Message

{pack.generated_assets.recruiter_message}

## Interview Prep Questions

{chr(10).join(f"- {item}" for item in pack.generated_assets.interview_prep_questions)}

## Interview Talking Points

{chr(10).join(f"- {item}" for item in pack.generated_assets.interview_talking_points)}

## Approval Status

Approved: {pack.approved}

Reviewer notes: {pack.reviewer_notes or "None"}
"""


if __name__ == "__main__":
    app()
