from app_agent.rag.build_index import build_index
from app_agent.rag.retrieve import retrieve_proof_points


def test_build_index_chunks_proof_point_corpus():
    chunk_count = build_index()
    assert chunk_count > 0


def test_retrieve_finds_relevant_proof_point():
    build_index()
    matches = retrieve_proof_points("Azure billing cost attribution pipeline", top_k=3)

    assert len(matches) == 3
    assert matches[0]["heading"] == "ESA Azure Cost-Center Billing Pipeline"
    assert matches[0]["source"] == "article-digest.md"
