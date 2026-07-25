"""Retrieve the proof points most relevant to a given query (e.g. a JD requirement)."""

import chromadb
from sentence_transformers import SentenceTransformer

from app_agent.rag.build_index import ARCHETYPE_KEYWORDS, COLLECTION_NAME, DB_PATH, EMBEDDING_MODEL

_model: SentenceTransformer | None = None
_collection = None


def _get_collection():
    global _model, _collection
    if _collection is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=DB_PATH)
        _collection = client.get_or_create_collection(COLLECTION_NAME)
    return _model, _collection


def retrieve_proof_points(query: str, top_k: int = 3, archetype: str | None = None) -> list[dict]:
    """archetype, if given, must be one of ARCHETYPE_KEYWORDS' keys
    (e.g. "agentic_ai_engineer") and restricts results to chunks tagged with it."""
    if archetype is not None and archetype not in ARCHETYPE_KEYWORDS:
        raise ValueError(f"Unknown archetype: {archetype!r}. Known: {list(ARCHETYPE_KEYWORDS)}")

    model, collection = _get_collection()
    query_embedding = model.encode([query]).tolist()
    where = {f"archetype_{archetype}": True} if archetype else None
    results = collection.query(query_embeddings=query_embedding, n_results=top_k, where=where)

    matches = []
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        matches.append(
            {
                "text": doc,
                "source": meta["source"],
                "heading": meta["heading"],
                "distance": distance,
            }
        )
    return matches


if __name__ == "__main__":
    query = "experience building agent-based multi-step AI systems"
    for match in retrieve_proof_points(query):
        print(f"[{match['source']} — {match['heading']}] (distance={match['distance']:.3f})")
        print(match["text"][:200], "...\n")
