from typing import TypedDict
from langgraph.graph import END, StateGraph
from app_agent.models import (
    ApplicationPack,
    CandidateProfile,
    GapAnalysis,
    GeneratedAssets,
    JobInput,
    JobRequirements,
    MatchAnalysis,
)
from app_agent.nodes.input_loader import load_job_input
from app_agent.nodes.requirements_extractor import extract_requirements
from app_agent.nodes.profile_matcher import load_candidate_profile, match_profile
from app_agent.nodes.gap_analyzer import analyze_gaps
from app_agent.nodes.asset_generator import generate_assets
from app_agent.nodes.approval import request_human_approval
from app_agent.rag.retrieve import retrieve_proof_points
from app_agent.rag.rerank import rerank_proof_points


class AgentState(TypedDict, total=False):
    job_input: JobInput
    job_text: str
    candidate_profile: CandidateProfile
    requirements: JobRequirements
    retrieved_proof_points: dict[str, list[dict]]
    match_analysis: MatchAnalysis
    gap_analysis: GapAnalysis
    generated_assets: GeneratedAssets
    application_pack: ApplicationPack
    approved: bool
    reviewer_notes: str | None
    rectify_target: str | None


def input_loader_node(state: AgentState) -> AgentState:
    return {"job_text": load_job_input(state["job_input"])}


def requirements_node(state: AgentState) -> AgentState:
    return {"requirements": extract_requirements(state["job_text"])}


def retrieve_proof_points_node(state: AgentState) -> AgentState:
    """For each JD requirement, retrieve the most relevant real proof points
    instead of handing the whole candidate profile to the matching step.
    Vector search pulls a wider candidate pool (top 10), then an LLM
    re-ranking pass narrows it to the top 3 actually passed to matching."""
    retrieved = {}
    for req in state["requirements"].requirements:
        candidates = retrieve_proof_points(req.requirement, top_k=10)
        retrieved[req.requirement] = rerank_proof_points(req.requirement, candidates, top_k=3)
    return {"retrieved_proof_points": retrieved}


def profile_match_node(state: AgentState) -> AgentState:
    profile = load_candidate_profile()
    return {
        "candidate_profile": profile,
        "match_analysis": match_profile(
            profile,
            state["requirements"],
            state.get("retrieved_proof_points"),
        ),
    }


def gap_analysis_node(state: AgentState) -> AgentState:
    return {"gap_analysis": analyze_gaps(state["match_analysis"])}


def asset_generation_node(state: AgentState) -> AgentState:
    return {
        "generated_assets": generate_assets(
            state["requirements"],
            state["match_analysis"],
            state["gap_analysis"],
        )
    }


def pack_builder_node(state: AgentState) -> AgentState:
    pack = ApplicationPack(
        requirements=state["requirements"],
        match_analysis=state["match_analysis"],
        gap_analysis=state["gap_analysis"],
        generated_assets=state["generated_assets"],
    )
    return {"application_pack": pack}


def approval_node(state: AgentState) -> AgentState:
    decision = request_human_approval(state["application_pack"])
    pack = state["application_pack"]
    pack.approved = decision.approved
    pack.reviewer_notes = decision.reviewer_notes
    return {
        "approved": decision.approved,
        "reviewer_notes": decision.reviewer_notes,
        "application_pack": pack,
        "rectify_target": decision.rectify_target if decision.rectify else None,
    }


def route_after_approval(state: AgentState) -> str:
    if state.get("approved"):
        return END
    rectify_target = state.get("rectify_target")
    if rectify_target == "gap_analysis":
        return "analyze_gaps"
    if rectify_target == "profile_match":
        return "match_profile"
    return END


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("load_input", input_loader_node)
    graph.add_node("extract_requirements", requirements_node)
    graph.add_node("retrieve_proof_points", retrieve_proof_points_node)
    graph.add_node("match_profile", profile_match_node)
    graph.add_node("analyze_gaps", gap_analysis_node)
    graph.add_node("generate_assets", asset_generation_node)
    graph.add_node("build_pack", pack_builder_node)
    graph.add_node("approve", approval_node)

    graph.set_entry_point("load_input")
    graph.add_edge("load_input", "extract_requirements")
    graph.add_edge("extract_requirements", "retrieve_proof_points")
    graph.add_edge("retrieve_proof_points", "match_profile")
    graph.add_edge("match_profile", "analyze_gaps")
    graph.add_edge("analyze_gaps", "generate_assets")
    graph.add_edge("generate_assets", "build_pack")
    graph.add_edge("build_pack", "approve")
    graph.add_conditional_edges(
        "approve",
        route_after_approval,
        {END: END, "analyze_gaps": "analyze_gaps", "match_profile": "match_profile"},
    )

    return graph.compile()
