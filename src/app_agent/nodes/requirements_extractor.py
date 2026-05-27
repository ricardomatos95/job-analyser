from langchain_core.prompts import ChatPromptTemplate
from app_agent.llm import get_chat_model
from app_agent.models import JobRequirements
from app_agent.prompts import REQUIREMENTS_EXTRACTION_PROMPT


def extract_requirements(job_text: str) -> JobRequirements:
    llm = get_chat_model(temperature=0.0)
    structured_llm = llm.with_structured_output(JobRequirements)
    prompt = ChatPromptTemplate.from_template(REQUIREMENTS_EXTRACTION_PROMPT)
    chain = prompt | structured_llm
    return chain.invoke({"job_text": job_text})
