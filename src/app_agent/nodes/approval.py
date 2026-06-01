from rich.console import Console
from rich.panel import Panel
from app_agent.models import ApplicationPack, ApprovalDecision

console = Console()


def request_human_approval(pack: ApplicationPack) -> ApprovalDecision:
    console.print(Panel(pack.model_dump_json(indent=2), title="Generated Application Pack"))
    response = console.input("Approve this application pack? [y/N]: ").strip().lower()

    if response == "y":
        return ApprovalDecision(approved=True, reviewer_notes="Approved by human reviewer.")

    notes = console.input("Enter reviewer notes: ").strip()
    return ApprovalDecision(approved=False, reviewer_notes=notes or "Rejected without notes.")
