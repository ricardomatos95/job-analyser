"""A tiny evaluation: for known queries, check whether the expected source
file shows up in the top-k results. Gives a real, quotable metric:
"precision@3 of X%". Run: python -m app_agent.rag.eval_retrieval

Test cases are queries already verified by hand against the real corpus,
not guessed blind.
"""

from app_agent.rag.build_index import build_index
from app_agent.rag.retrieve import retrieve_proof_points

TEST_CASES = [
    {
        "query": "experience building agent-based multi-step AI systems",
        "expected_source": "cv.md",
    },
    {
        "query": "Azure billing cost attribution pipeline",
        "expected_source": "article-digest.md",
    },
    {
        "query": "enterprise Copilot user adoption and coaching program",
        "expected_source": "article-digest.md",
    },
    {
        "query": "Azure and Power Platform certifications",
        "expected_source": "cv.md",
    },
    # add more as the corpus grows
]


def run_eval(top_k: int = 3) -> float:
    hits = 0
    for case in TEST_CASES:
        results = retrieve_proof_points(case["query"], top_k=top_k)
        sources = [r["source"] for r in results]
        if case["expected_source"] in sources:
            hits += 1
        else:
            print(f"MISS: {case['query']!r} -> got {sources}, expected {case['expected_source']!r}")

    precision_at_k = hits / len(TEST_CASES)
    print(f"precision@{top_k}: {precision_at_k:.0%} ({hits}/{len(TEST_CASES)})")
    return precision_at_k


if __name__ == "__main__":
    build_index()
    run_eval()
