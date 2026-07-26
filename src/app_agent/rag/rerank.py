"""Second-pass re-ranking: ask the LLM to re-score a batch of vector-search
candidates against the query, then keep only the top-k by that score.

Vector search (cosine distance) is fast but purely lexical-semantic; an LLM
pass can weigh context the embedding alone misses (e.g. seniority framing,
implicit relevance). One call per requirement, kept deliberately small (a
handful of short candidate snippets) — on a local model, a single call that
batches every requirement's candidates together processes the same total
tokens but as one long, unreportable block; several small calls finish
faster individually and let progress be reported as each one completes.
"""

from collections.abc import Callable

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app_agent.llm import get_chat_model

RERANK_PROMPT = """
Score how relevant each candidate proof point is to the query, from 0 (irrelevant)
to 10 (directly proves the query's requirement).

Query:
{query}

Candidates:
{candidates}
"""


class RerankedMatch(BaseModel):
    chunk_index: int = Field(description="Index of the candidate in the input list")
    relevance_score: int = Field(ge=0, le=10)


class RerankResult(BaseModel):
    ranked: list[RerankedMatch]


def _rerank_one(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    if not candidates:
        return []

    llm = get_chat_model(temperature=0.0)
    structured_llm = llm.with_structured_output(RerankResult)
    prompt = ChatPromptTemplate.from_template(RERANK_PROMPT)
    chain = prompt | structured_llm

    candidates_text = "\n\n".join(
        f"[{i}] ({c['source']} — {c['heading']})\n{c['text'][:500]}"
        for i, c in enumerate(candidates)
    )
    result = chain.invoke({"query": query, "candidates": candidates_text})

    scores = {m.chunk_index: m.relevance_score for m in result.ranked}
    ordered = sorted(
        range(len(candidates)), key=lambda i: scores.get(i, -1), reverse=True
    )
    return [candidates[i] for i in ordered[:top_k]]


def rerank_proof_points(
    requirement_candidates: dict[str, list[dict]],
    top_k: int = 3,
    on_progress: Callable[[int, int], None] | None = None,
) -> dict[str, list[dict]]:
    items = list(requirement_candidates.items())
    reranked: dict[str, list[dict]] = {}

    for i, (requirement, candidates) in enumerate(items):
        reranked[requirement] = _rerank_one(requirement, candidates, top_k)
        if on_progress:
            on_progress(i + 1, len(items))

    return reranked
