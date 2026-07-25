# Forward-Deployed GenAI Workflow Agent

This project is a LangGraph-based agentic workflow that converts a job posting into an Application Intelligence Pack.

## Features

- Job posting extraction from text or URL
- Structured requirement extraction
- RAG-based proof-point retrieval (embeddings + vector search + re-ranking) feeding candidate matching
- Candidate profile matching
- Gap analysis
- Tailored CV bullet generation
- Recruiter outreach generation
- Interview preparation generation
- Human approval checkpoint
- LangSmith tracing
- Pytest test suite

## Stack

- **LangGraph** — orchestrates the multi-step agentic pipeline as a graph rather than a single prompt chain.
- **LLM provider** — OpenAI, Claude (Anthropic), or a local model via Ollama, selected by `LLM_PROVIDER` in `.env`. Defaults to Ollama (local, no API key required).
- **sentence-transformers** (`all-MiniLM-L6-v2`) + **ChromaDB** — open-weight embeddings and a local vector store for proof-point retrieval (`src/app_agent/rag/`).
- **LangSmith** — tracing/observability across the graph run.
- **Pytest** — test coverage for the pipeline stages.

## Architecture

```mermaid
flowchart LR
    A[Job URL or Text] --> B[Input Loader]
    B --> C[Requirements Extractor]
    C --> C2[Retrieve Proof Points]
    C2 --> D[Profile Matcher]
    D --> E[Gap Analyzer]
    E --> F[Asset Generator]
    F --> G[Human Approval]
    G --> H[Application Pack]
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

`.env` defaults to `LLM_PROVIDER=ollama` (no API key needed — requires [Ollama](https://ollama.com) running locally with a model pulled, e.g. `ollama pull qwen3:14b`). To use OpenAI or Anthropic instead, set `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic` in `.env` and fill in the matching API key.

## RAG: proof-point retrieval

Candidate matching is grounded in a small vector-search corpus (`data/proof_points/*.md`) rather than dumping the whole candidate profile into every prompt. Build (or rebuild, after editing the corpus) the local index:

```bash
python -m app_agent.rag.build_index
```

This embeds each `## `-delimited section with `sentence-transformers` and stores it in `./rag_store/` (gitignored, regenerated on demand — not committed). At query time, `retrieve_proof_points()` pulls the top candidates via vector search, optionally filtered by archetype (`agentic_ai_engineer`, `ai_solutions_architect`, `end_user_computing` — see `src/app_agent/rag/build_index.py`), then `rerank_proof_points()` does a second LLM pass to re-score before the top-k are handed to the Profile Matcher node.

Check retrieval quality directly:

```bash
python -m app_agent.rag.retrieve          # example query, prints top matches
python -m app_agent.rag.eval_retrieval    # precision@3 over a small labeled test set
```

## Run

Full sequence from a clean checkout:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                       # defaults to local Ollama, no key needed
ollama pull qwen3:14b                       # skip if you're using OpenAI/Anthropic instead
python -m app_agent.rag.build_index         # builds the local proof-point vector index
app-agent --text-file examples/sample_job.txt
```

`--url <job-posting-url>` works instead of `--text-file` too. Partway through the run you'll be prompted `Approve this application pack? [y/N]:` in the terminal — this is a real interactive checkpoint, not a hang. The final result is written to `examples/sample_application_pack.md` (override with `--output <path>`).

## Test

```bash
pytest -v
```

`tests/test_gap_analyzer.py` and `tests/test_requirements_extractor.py` are marked `@pytest.mark.integration` — they make real LLM calls (via whatever `LLM_PROVIDER` is set in `.env`), so they're slower and need a working provider. Run everything except those with `pytest -v -m "not integration"`.

## Security Notes

- Do not commit `.env`.
- Do not include confidential employer data.
- Use synthetic or public job postings only.
- Review outputs manually before use — generated content can include claims not present in your actual source material (see e.g. fabricated metrics observed in local testing); verify anything asset-generation produces before using it externally.
