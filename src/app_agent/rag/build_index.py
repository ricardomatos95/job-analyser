"""Chunk the proof-point corpus, embed it, and store it in a local vector DB.

Run once, and re-run whenever data/proof_points/*.md changes:
    python -m app_agent.rag.build_index
"""

import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

SOURCE_DIR = Path("data/proof_points")
DB_PATH = "./rag_store"
COLLECTION_NAME = "proof_points"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Archetypes mirror career-ops/modes/_profile.md's "Adaptive Framing" table.
# Keyword match against a chunk's own text — no LLM call needed at index time.
ARCHETYPE_KEYWORDS = {
    "agentic_ai_engineer": [
        "langgraph", "langchain", "agent", "agentic", "automation",
        "human-in-the-loop", "hitl", "llm",
    ],
    "ai_solutions_architect": [
        "azure", "power platform", "fabric", "foundry", "architecture",
        "data warehouse", "api-driven", "pipeline", "enterprise integration",
    ],
    "end_user_computing": [
        "adoption", "governance", "change management", "training",
        "enablement", "coaching", "utilization", "rollout",
    ],
}


def tag_archetypes(text: str) -> dict[str, bool]:
    lowered = text.lower()
    return {
        f"archetype_{archetype}": any(kw in lowered for kw in keywords)
        for archetype, keywords in ARCHETYPE_KEYWORDS.items()
    }


def chunk_markdown(text: str, source_name: str) -> list[dict]:
    """Split a markdown file into chunks along '## ' headers."""
    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section or len(section) < 40:
            continue
        heading_match = re.match(r"## (.+)", section)
        heading = heading_match.group(1) if heading_match else "Untitled"
        chunks.append({"text": section, "source": source_name, "heading": heading})
    return chunks


def build_index() -> int:
    all_chunks: list[dict] = []
    for path in sorted(SOURCE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_markdown(text, path.name))

    if not all_chunks:
        raise RuntimeError(f"No chunks found under {SOURCE_DIR}/ — nothing to index.")

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    client = chromadb.PersistentClient(path=DB_PATH)
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    collection.add(
        ids=[f"chunk-{i}" for i in range(len(all_chunks))],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[
            {"source": c["source"], "heading": c["heading"], **tag_archetypes(c["text"])}
            for c in all_chunks
        ],
    )

    print(f"Stored {len(all_chunks)} chunks in {DB_PATH}/ under collection '{COLLECTION_NAME}'.")
    return len(all_chunks)


if __name__ == "__main__":
    build_index()
