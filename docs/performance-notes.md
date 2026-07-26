# Performance Notes: Local-Model Latency Fix

## The problem

`app-agent chat` was taking 10+ minutes on a local Ollama model (`qwen3:14b`) and producing
no output in between — a real run was killed after 21+ minutes still stuck on a single call.

## Diagnosis

The first hypothesis was wrong: proof-point reranking had just been changed from one LLM call
per JD requirement to a single call batching every requirement together, on the theory that
fewer round trips would be faster. On a local, already-warm Ollama instance that's backwards —
there's no meaningful per-call network/queueing overhead to save, so batching just produced one
much larger, completely unreportable call instead of several small, individually fast ones.

Reverting the batching only partially explained the slowdown. The actual dominant cost, found
by testing a trivial prompt directly against the Ollama API:

```json
{"response": "Hello.", "eval_count": 314, "total_duration": 9001221709}
```

314 generated tokens (~9s) to say one word — because `qwen3:14b` is a "thinking" model that
generates a hidden chain-of-thought before every response by default. That tax applies to
every LLM call in the pipeline (extraction, reranking, matching, gap analysis, asset
generation), not just reranking. `langchain-ollama` exposes a `reasoning` parameter that maps
to Ollama's `think` API option; setting `reasoning=False` skips the chain-of-thought entirely.

## Before / after

Measured on the same hardware (Apple Silicon, 36GB unified memory, `qwen3:14b` Q4_K_M) against
the same local Ollama instance.

| Call | Thinking mode on (before) | Thinking mode off (after) |
|---|---|---|
| Trivial prompt ("say hello") | 9.0s (314 tokens) | 0.3s |
| Requirements extraction (real JD, 12 requirements) | 69s | 11.7s |
| Proof-point rerank, per requirement (avg) | ~10.8s/call | ~1.4s/call |
| Full pipeline, batched rerank + thinking on | did not complete (killed after 21+ min) | — |
| Full pipeline, per-requirement rerank + thinking off | — | 160.7s (~2.5 min) |

Full-run breakdown (extraction through pack assembly, 12 requirements, thinking off):

| Stage | Cumulative | Stage time |
|---|---|---|
| Extract requirements | 11.4s | 11.4s |
| Retrieve + rerank (12 requirements) | 74.0s | 62.6s |
| Match profile | 101.0s | 27.0s |
| Analyze gaps | 113.9s | 12.9s |
| Generate assets | 160.7s | 46.8s |

## What changed

- `get_chat_model()` (`src/app_agent/llm.py`) defaults to `reasoning=False` for the Ollama
  provider. Callers can still opt back into reasoning per call if a specific node's output
  quality needs it.
- Proof-point reranking (`src/app_agent/rag/rerank.py`) is back to one small call per
  requirement rather than a single batched call.
- `retrieve_proof_points_node` (`src/app_agent/graph.py`) accepts an `on_progress` callback,
  threaded through `build_graph()`, so `app-agent chat` reports live progress
  (`reranking proof points 2/12...`) as each requirement finishes instead of going silent for
  the whole node.

## Takeaway

For local models, round-trip count matters far less than total tokens generated. A "thinking"
model's hidden reasoning tokens dominate that total, so for bounded extraction/scoring/drafting
tasks (not open-ended problem solving), disabling reasoning mode is the highest-leverage
latency fix available — well ahead of batching or reducing call count.
