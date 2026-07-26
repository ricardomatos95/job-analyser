"""Second-pass re-ranking: ask the LLM to re-score every requirement's vector-search
candidates in a single batched call, then keep only the top-k per requirement.

Vector search (cosine distance) is fast but purely lexical-semantic; an LLM pass can
weigh context the embedding alone misses (e.g. seniority framing, implicit relevance).

Batched across all requirements in one call instead of one call per requirement, to
cut round trips (each round trip has fixed overhead, which dominates on local models).
num_ctx is set explicitly to fit the batch — local models default to a much smaller
runtime context window than they support, which would otherwise silently truncate
the prompt instead of erroring.
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app_agent.llm import get_chat_model

BATCH_RERANK_PROMPT = """
For each requirement below, score how relevant each of its candidate proof points is,
from 0 (irrelevant) to 10 (directly proves the requirement).

Score candidates only against the requirement they are listed under. Reference each
requirement and candidate using the requirement_index and chunk_index exactly as given.

{requirements_block}
"""


class RerankedMatch(BaseModel):
    chunk_index: int = Field(description="Index of the candidate within its requirement's candidate list")
    relevance_score: int = Field(ge=0, le=10)


class RequirementRanking(BaseModel):
    requirement_index: int = Field(description="Index of the requirement in the input list")
    ranked: list[RerankedMatch]


class BatchRerankResult(BaseModel):
    rankings: list[RequirementRanking]


def rerank_proof_points(
    requirement_candidates: dict[str, list[dict]],
    top_k: int = 3,
    num_ctx: int = 16384,
) -> dict[str, list[dict]]:
    requirements = [r for r, candidates in requirement_candidates.items() if candidates]
    if not requirements:
        return {r: [] for r in requirement_candidates}

    blocks = []
    for i, requirement in enumerate(requirements):
        candidates = requirement_candidates[requirement]
        candidates_text = "\n".join(
            f"  [{j}] ({c['source']} — {c['heading']})\n  {c['text'][:500]}"
            for j, c in enumerate(candidates)
        )
        blocks.append(f"Requirement [{i}]: {requirement}\nCandidates:\n{candidates_text}")

    llm = get_chat_model(temperature=0.0, num_ctx=num_ctx)
    structured_llm = llm.with_structured_output(BatchRerankResult)
    prompt = ChatPromptTemplate.from_template(BATCH_RERANK_PROMPT)
    chain = prompt | structured_llm
    result = chain.invoke({"requirements_block": "\n\n".join(blocks)})

    rankings_by_requirement = {r.requirement_index: r.ranked for r in result.rankings}
    reranked = {r: [] for r in requirement_candidates}
    for i, requirement in enumerate(requirements):
        candidates = requirement_candidates[requirement]
        scores = {m.chunk_index: m.relevance_score for m in rankings_by_requirement.get(i, [])}
        ordered = sorted(range(len(candidates)), key=lambda j: scores.get(j, -1), reverse=True)
        reranked[requirement] = [candidates[j] for j in ordered[:top_k]]

    return reranked
