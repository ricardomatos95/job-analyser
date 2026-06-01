from langchain_core.prompts import ChatPromptTemplate
from app_agent.llm import get_chat_model
from app_agent.models import GeneratedAssets, GapAnalysis, JobRequirements, MatchAnalysis
from app_agent.prompts import ASSET_GENERATION_PROMPT


def generate_assets(
    job_requirements: JobRequirements,
    match_analysis: MatchAnalysis,
    gap_analysis: GapAnalysis,
) -> GeneratedAssets:
    llm = get_chat_model(temperature=0.3)
    structured_llm = llm.with_structured_output(GeneratedAssets)
    prompt = ChatPromptTemplate.from_template(ASSET_GENERATION_PROMPT)
    chain = prompt | structured_llm
    return chain.invoke(
        {
            "job_requirements": job_requirements.model_dump_json(indent=2),
            "match_analysis": match_analysis.model_dump_json(indent=2),
            "gap_analysis": gap_analysis.model_dump_json(indent=2),
        }
    )
