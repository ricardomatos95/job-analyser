import json

import yaml
from langchain_core.prompts import ChatPromptTemplate
from app_agent.llm import get_chat_model
from app_agent.models import CandidateProfile, JobRequirements, MatchAnalysis
from app_agent.prompts import PROFILE_MATCH_PROMPT


def load_candidate_profile(path: str = "candidate_profile.yaml") -> CandidateProfile:
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return CandidateProfile(**data)


def match_profile(
    candidate_profile: CandidateProfile,
    job_requirements: JobRequirements,
    retrieved_proof_points: dict[str, list[dict]] | None = None,
) -> MatchAnalysis:
    llm = get_chat_model(temperature=0.1)
    structured_llm = llm.with_structured_output(MatchAnalysis)
    prompt = ChatPromptTemplate.from_template(PROFILE_MATCH_PROMPT)
    chain = prompt | structured_llm
    return chain.invoke(
        {
            "candidate_profile": candidate_profile.model_dump_json(indent=2),
            "job_requirements": job_requirements.model_dump_json(indent=2),
            "retrieved_proof_points": json.dumps(retrieved_proof_points or {}, indent=2),
        }
    )
