from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app_agent.config import get_settings


def get_chat_model(temperature: float = 0.2):
    settings = get_settings()

    if settings.llm_provider == "openai":
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )

    if settings.llm_provider == "anthropic":
        return ChatAnthropic(
            model=settings.anthropic_model,
            temperature=temperature,
            api_key=settings.anthropic_api_key,
        )

    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            temperature=temperature,
            base_url=settings.ollama_base_url,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")
