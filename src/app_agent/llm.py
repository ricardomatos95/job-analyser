from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app_agent.config import get_settings


def get_chat_model(temperature: float = 0.2, num_ctx: int | None = None):
    """num_ctx only applies to the ollama provider — it sizes the context window
    (and therefore KV-cache memory) for that call instead of relying on Ollama's
    smaller runtime default, which would otherwise silently truncate long prompts."""
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
            num_ctx=num_ctx,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")
