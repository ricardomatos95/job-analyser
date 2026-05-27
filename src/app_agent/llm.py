from langchain_openai import ChatOpenAI
from app_agent.config import get_settings


def get_chat_model(temperature: float = 0.2):
    settings = get_settings()
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        api_key=settings.openai_api_key,
    )
