# Job Application Analyser

Paste in a job posting and this tool tells you how good a fit you are, what's missing from
your background, and drafts the material you'd actually need to apply — tailored CV bullets,
a recruiter message, and interview prep notes.

It checks its claims against your real experience before drafting anything, so treat what it
produces as a strong first draft you review, not something to send unchecked.

## What you get back

For any job posting, it produces:

- **A fit score** (0–100) — a quick read on how well you match the role
- **Your strongest selling points** for that specific role
- **Gaps** — split into "critical" (worth addressing head-on) and "manageable" (worth
  acknowledging but not a dealbreaker) — plus suggestions for handling them
- **Tailored CV bullets** for this specific job
- **A recruiter outreach message**
- **Interview prep questions and talking points**

Before anything is finalized, you're asked to approve it — you always get a chance to review
(and reject, if it's off) before results are saved.

## Getting started

You'll need:
- Python 3.11 or later
- Either [Ollama](https://ollama.com) installed (runs the AI model for free on your own
  computer) — or an API key from OpenAI or Anthropic (Claude), if you'd rather use one of
  those instead

**1. Install**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

This sets up an isolated Python environment, installs the project, and creates your local
settings file (`.env`).

**2. Choose your AI provider**

By default the project uses Ollama, running a model on your own computer — free, private, no
account needed. Just pull the model once:

```bash
ollama pull qwen3:14b
```

If you'd rather use OpenAI or Claude instead (usually faster, but costs money and sends your
data to their servers), open `.env`, set `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic`,
and add your API key.

**3. Build the local knowledge base**

The tool backs up its claims about you with real examples from your background instead of
making things up. Build that index once (and again any time you update the examples in
`data/proof_points/`):

```bash
python -m app_agent.rag.build_index
```

**4. Fill in your profile**

Edit `candidate_profile.yaml` at the project root with your own background, strengths, and
target roles — this is what every job posting gets compared against.

## Using it

**Chat mode** (recommended) — a conversation, like talking to an assistant:

```bash
app-agent chat
```

Paste a job description or link in your own words ("hey can you check this JD for me: ..."),
and it'll analyze it, show you a summary, and let you ask follow-up questions afterward
("why is my fit score only 55?", "make the recruiter message shorter") without re-pasting
anything. While it's working you'll see a running status of what it's doing, since a full
analysis can take a few minutes on a local model. Type `exit` to leave.

**One-shot mode** — analyze a single JD and write the result straight to a file:

```bash
app-agent run --text-file path/to/job-description.txt
```

(or `--url <link>` instead of a file). Partway through, you'll be asked to approve the result
before it's saved — that's expected, not a bug.

## A note on accuracy

This tool drafts content using AI — treat it as a starting point, not a finished product.
Always read what it produces before using it: check that claims about your experience are
actually true, and that nothing has been exaggerated or invented. Don't paste in confidential
employer information — stick to public job postings.

---

## Technical details

*For anyone curious how it works under the hood — not needed to just use the tool.*

### Stack

- **LangGraph** — orchestrates the multi-step agentic pipeline as a graph rather than a single
  prompt chain.
- **LLM provider** — OpenAI, Claude (Anthropic), or a local model via Ollama, selected by
  `LLM_PROVIDER` in `.env`. Defaults to Ollama.
- **sentence-transformers** (`all-MiniLM-L6-v2`) + **ChromaDB** — open-weight embeddings and a
  local vector store for proof-point retrieval (`src/app_agent/rag/`).
- **LangSmith** — tracing/observability across the graph run.
- **Pytest** — test coverage for the pipeline stages.

### Architecture

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

`app-agent chat` wraps the same graph with an intent-classification step in front (decide
whether a message is a new job to analyze, a follow-up question, or small talk) and a
conversational follow-up step after, so results can be discussed without re-running the
pipeline.

### RAG: proof-point retrieval

Candidate matching is grounded in a small vector-search corpus (`data/proof_points/*.md`)
rather than dumping the whole candidate profile into every prompt. `retrieve_proof_points()`
pulls the top candidates per requirement via vector search, optionally filtered by archetype
(`agentic_ai_engineer`, `ai_solutions_architect`, `end_user_computing` — see
`src/app_agent/rag/build_index.py`), then `rerank_proof_points()` does a second LLM pass —
batched across all of the JD's requirements in a single call — to re-score before the top-k
per requirement are handed to the Profile Matcher node.

Check retrieval quality directly:

```bash
python -m app_agent.rag.retrieve          # example query, prints top matches
python -m app_agent.rag.eval_retrieval    # precision@3 over a small labeled test set
```

### Test

```bash
pytest -v
```

`tests/test_gap_analyzer.py`, `tests/test_requirements_extractor.py`, and parts of
`tests/test_chat.py` are marked `@pytest.mark.integration` — they make real LLM calls (via
whatever `LLM_PROVIDER` is set in `.env`), so they're slower and need a working provider. Run
everything except those with `pytest -v -m "not integration"`.

### Security notes

- Do not commit `.env`.
- Do not include confidential employer data.
- Use synthetic or public job postings only.
- Review outputs manually before use — generated content can include claims not present in
  your actual source material (see e.g. fabricated metrics observed in local testing); verify
  anything asset-generation produces before using it externally.
