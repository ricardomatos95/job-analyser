from langchain_core.prompts import ChatPromptTemplate
from app_agent.llm import get_chat_model
from app_agent.models import GapAnalysis, MatchAnalysis
from app_agent.prompts import GAP_ANALYSIS_PROMPT


def analyze_gaps(match_analysis: MatchAnalysis) -> GapAnalysis:
    llm = get_chat_model(temperature=0.1)
    structured_llm = llm.with_structured_output(GapAnalysis)
    prompt = ChatPromptTemplate.from_template(GAP_ANALYSIS_PROMPT)
    chain = prompt | structured_llm
    return chain.invoke(
        {"match_analysis": match_analysis.model_dump_json(indent=2)}
    )
