from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app_agent.config import get_settings


def get_chat_model(temperature: float = 0.2, num_ctx: int | None = None, reasoning: bool | None = False):
    """num_ctx and reasoning only apply to the ollama provider.

    num_ctx sizes the context window (and therefore KV-cache memory) for that call
    instead of relying on Ollama's smaller runtime default, which would otherwise
    silently truncate long prompts.

    reasoning defaults to False: "thinking" models like qwen3 otherwise generate a
    hidden chain-of-thought before every response — measured at ~30x slower per call
    (9s vs 0.3s for a trivial prompt) — which isn't worth the cost for the bounded
    extraction/scoring/drafting tasks every node in this pipeline does. Pass
    reasoning=True for a specific call if a node's output quality needs it.
    """
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
            reasoning=reasoning,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")
