import time

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END
from rich.console import Console

from app_agent.graph import AgentState, build_graph, route_after_approval
from app_agent.llm import get_chat_model
from app_agent.models import ApplicationPack, ChatIntent, JobInput
from app_agent.prompts import CHAT_FOLLOWUP_PROMPT, CHAT_INTENT_PROMPT

NODE_LABELS: dict[str, str] = {
    "load_input": "Loading job input",
    "extract_requirements": "Extracting requirements from the JD",
    "retrieve_proof_points": "Retrieving & reranking proof points",
    "match_profile": "Matching your profile against requirements",
    "analyze_gaps": "Analyzing gaps",
    "generate_assets": "Generating CV bullets, recruiter message & prep notes",
    "build_pack": "Assembling the application pack",
    "approve": "Awaiting your approval",
}

ORDERED_NODES = [
    "load_input",
    "extract_requirements",
    "retrieve_proof_points",
    "match_profile",
    "analyze_gaps",
    "generate_assets",
    "build_pack",
    "approve",
]


def run_analysis(graph, job_input: JobInput, console: Console) -> AgentState:
    """Runs the graph via stream() instead of invoke() so each node's completion is
    reported as it happens. Without this a chat session goes silent for the entire
    pipeline run, which on local models can take minutes."""
    final_state: AgentState = {}
    node_start = time.monotonic()
    console.print(f"[dim]-> {NODE_LABELS[ORDERED_NODES[0]]}...[/dim]")

    for update in graph.stream({"job_input": job_input}, stream_mode="updates"):
        for node_name, node_output in update.items():
            elapsed = time.monotonic() - node_start
            console.print(f"[dim]   done ({elapsed:.0f}s)[/dim]")
            final_state.update(node_output)

            if node_name == "approve":
                target = route_after_approval(node_output)
            else:
                pos = ORDERED_NODES.index(node_name)
                target = ORDERED_NODES[pos + 1] if pos + 1 < len(ORDERED_NODES) else END

            if target != END:
                console.print(f"[dim]-> {NODE_LABELS[target]}...[/dim]")
            node_start = time.monotonic()

    return final_state


def classify_intent(message: str, has_active_pack: bool) -> ChatIntent:
    llm = get_chat_model(temperature=0.0)
    structured_llm = llm.with_structured_output(ChatIntent)
    prompt = ChatPromptTemplate.from_template(CHAT_INTENT_PROMPT)
    chain = prompt | structured_llm
    return chain.invoke({"message": message, "has_active_pack": has_active_pack})


def format_history(history: list[dict], limit: int = 10) -> str:
    recent = history[-limit:]
    return "\n".join(f"{turn['role']}: {turn['content']}" for turn in recent)


def answer_followup(message: str, pack: ApplicationPack, history: list[dict]) -> str:
    llm = get_chat_model(temperature=0.3)
    prompt = ChatPromptTemplate.from_template(CHAT_FOLLOWUP_PROMPT)
    chain = prompt | llm
    response = chain.invoke(
        {
            "pack": pack.model_dump_json(indent=2),
            "history": format_history(history),
            "message": message,
        }
    )
    return response.content


def summarize_pack(pack: ApplicationPack) -> str:
    lines = [
        f"Fit score: {pack.match_analysis.overall_fit_score}/100",
        "",
        "Top selling points:",
        *(f"  - {item}" for item in pack.match_analysis.strongest_selling_points[:3]),
        "",
        "Top gaps:",
        *(f"  - {item}" for item in pack.gap_analysis.critical_gaps[:3]),
    ]
    return "\n".join(lines)


def run_chat() -> None:
    console = Console()

    def report_rerank_progress(done: int, total: int) -> None:
        console.print(f"[dim]   reranking proof points {done}/{total}...[/dim]")

    graph = build_graph(on_proof_point_progress=report_rerank_progress)
    last_pack: ApplicationPack | None = None
    history: list[dict] = []

    console.print("[bold]app-agent chat[/bold] — paste a JD or ask a question. Type 'exit' to quit.")

    while True:
        message = console.input("You: ").strip()
        if not message:
            continue
        if message.lower() in {"exit", "quit"}:
            break

        history.append({"role": "user", "content": message})
        intent = classify_intent(message, has_active_pack=last_pack is not None)

        if intent.action == "analyze_job":
            job_input = JobInput(
                source_type="url" if intent.job_url else "text",
                content=intent.job_url or intent.job_text or message,
            )
            final_state = run_analysis(graph, job_input, console)
            last_pack = final_state.get("application_pack")
            reply = (
                summarize_pack(last_pack)
                if last_pack
                else "Something went wrong — no application pack was produced."
            )

        elif intent.action == "followup":
            reply = (
                answer_followup(message, last_pack, history)
                if last_pack is not None
                else "I don't have an active application pack yet — paste a job description first."
            )

        else:
            reply = "I'm here to analyze job postings — paste a JD or a link to get started."

        console.print(f"Agent: {reply}")
        history.append({"role": "assistant", "content": reply})
