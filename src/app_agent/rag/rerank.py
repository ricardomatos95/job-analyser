"""Second-pass re-ranking: ask the LLM to re-score a batch of vector-search
candidates against the query, then keep only the top-k by that score.

Vector search (cosine distance) is fast but purely lexical-semantic; an LLM
pass can weigh context the embedding alone misses (e.g. seniority framing,
implicit relevance). Costs one extra LLM call per query.
"""

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


def rerank_proof_points(query: str, candidates: list[dict], top_k: int = 3) -> list[dict]:
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
