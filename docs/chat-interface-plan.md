# Planned: interactive chat command (`app-agent chat`)

> Not yet implemented. Saved here to revisit later — see conversation history for full context on why this was scoped this way.

## Context

The RAG/multi-provider LLM work (PR #1) is merged and working. The next step is a conversational entry point instead of the flag-based CLI — type something like "Hey please review this JD: ..." in a terminal and have it work, plus ask follow-up questions about a result ("why is my fit score only 55", "make the recruiter message shorter") without re-pasting everything.

Decided when this was scoped: conversational memory (not just one-shot request/response), and it's fine for `app-agent` to require explicit subcommands going forward (`app-agent run --text-file ...` / `app-agent chat`) now that there's more than one command.

## Approach

### 1. New models (`models.py`)
```python
class ChatIntent(BaseModel):
    action: Literal["analyze_job", "followup", "chitchat"]
    job_text: str | None = None
    job_url: str | None = None
```
One structured-output LLM call per user message classifies what they want and extracts the JD text/URL if present — same pattern as every other node (`get_chat_model().with_structured_output(...)`), so free-form phrasing ("hey can you check this JD out: ...") works without hand-written regex/heuristics.

### 2. New prompts (`prompts.py`)
- `CHAT_INTENT_PROMPT` — classify the message into `analyze_job` / `followup` / `chitchat`, given the raw message and whether a pack is already active.
- `CHAT_FOLLOWUP_PROMPT` — given the last `ApplicationPack` (JSON), recent conversation history, and the new message, produce a free-text answer. This is a plain `llm.invoke()` (no structured output) since follow-ups are open-ended conversational text, not a fixed schema.

### 3. New module: `src/app_agent/chat.py`
- `run_chat()` — the REPL loop: `build_graph()` once, then loop on `console.input("You: ")` (Rich, matching `approval.py`'s existing style) until `exit`/`quit`.
- `classify_intent(message, has_active_pack)` → `ChatIntent`.
- `answer_followup(message, pack, history)` → `str`.
- `summarize_pack(pack)` → short conversational summary (fit score, top selling points, top gaps) printed after an analysis run, instead of dumping raw JSON at the user.
- State kept in-memory for the session only: `last_pack: ApplicationPack | None`, `history: list[dict]` (capped to the last ~10 turns when building the follow-up prompt).

**Reuse, not reimplementation:** the `analyze_job` path builds a `JobInput` (existing model) from the extracted text/URL and calls the *exact same* `graph.invoke(...)` used by `cli.py`'s `run` command today — full reuse of requirements extraction, RAG retrieval + re-ranking, matching, gap analysis, and asset generation. No pipeline logic is duplicated.

**Scope boundary, stated explicitly:** follow-ups are advisory/conversational only — the assistant can explain or draft a rewritten snippet in its reply, but it does not mutate `last_pack`'s fields in place. Making edits persist back into the stored pack would need another structured-parsing step to know which field changed and how; that's a reasonable v2, not v1.

**Known, expected UX quirk:** the existing human-approval checkpoint (`approval.py`) still fires mid-conversation during `analyze_job` — it prints the full JSON panel and asks `Approve this application pack? [y/N]:` inline in the chat. This isn't hidden or special-cased; it's the same human-in-the-loop checkpoint the graph has always had, just now appearing inside a chat session instead of a single CLI run.

### 4. `cli.py`
Add:
```python
@app.command()
def chat():
    """Interactive chat: paste a JD or URL, ask follow-up questions about results."""
    run_chat()
```
The existing `run` command is untouched. Typer will now require the subcommand name (`app-agent run ...` / `app-agent chat`) since there are two commands.

### 5. Tests
- `tests/test_chat.py`: a fast unit test for `summarize_pack()` (pure formatting, no LLM) and `format_history()` if extracted as its own helper.
- One `@pytest.mark.integration` test for `classify_intent()` — a message containing a URL should classify as `analyze_job` with `job_url` populated; a message like "what does that fit score mean" with `has_active_pack=True` should classify as `followup`.

### 6. Docs
`README.md`: update the `## Run` section's invocation from bare `app-agent --text-file ...` to `app-agent run --text-file ...`, and add an `app-agent chat` example.

## Verification (once implemented)
1. `pytest -v` — new tests pass alongside existing suite.
2. Manual: `app-agent chat`, type a message pasting a JD in natural language (e.g. "hey can you look at this JD for me: ...") — confirm it classifies as `analyze_job`, runs the graph, hits the approval prompt, and prints a conversational summary (not raw JSON).
3. Manual: follow-up message afterward (e.g. "what's my biggest gap?") — confirm it answers using the stored pack without asking you to repeat the JD.
4. Manual: `exit` cleanly quits the loop.
