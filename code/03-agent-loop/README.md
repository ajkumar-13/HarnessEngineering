# 03 - The agent loop

The runnable companion to [03 - The agent loop: ReAct, control loops, and stopping](../../posts/03-the-agent-loop/index.md). A minimal **reason, act, observe** loop with the four exits of the series, in plain Python with no runtime dependencies: `loop.py` is 77 lines, `models.py` 109 and `tools.py` 66.

## What is here

| File | What it is |
|------|-----------|
| `src/agent_loop/loop.py` | The loop: `run(...)` with all four exits. Read this first. |
| `src/agent_loop/models.py` | The `Model` protocol, an offline `ScriptedModel`, and an `AnthropicModel` adapter for real runs. |
| `src/agent_loop/tools.py` | Two small tools, `calculator` and `echo`; the calculator walks the abstract syntax tree instead of calling `eval`. |
| `src/agent_loop/__main__.py` | An offline demo, `python -m agent_loop`. |
| `tests/` | Seven tests: one per exit, plus the tool-result feedback, the calculator sandbox and an unknown tool. They need no API key. |

The message format is the Anthropic Messages format: the loop's `messages` list is what the Messages API takes, so the real adapter passes it through unchanged.

## Quickstart (offline, no API key)

From this directory:

```bash
uv run python -m agent_loop       # one reason, act, observe, answer cycle
uv run --extra dev pytest -q      # the seven tests, offline
```

The demo prints:

```text
[user     ] What is (2 + 3) * 4?
[assistant] [{'type': 'text', 'text': "I'll compute that."}, {'type': 'tool_use', 'id': 'tu_1', 'name': 'calculator', 'input': {'expression': '(2 + 3) * 4'}}]
[user     ] [{'type': 'tool_result', 'tool_use_id': 'tu_1', 'content': '20'}]
[assistant] [{'type': 'text', 'text': 'The result is 20.'}]

answer      : The result is 20.
stop_reason : completed
iterations  : 2
tokens_used : 18
```

## The four exits

`run()` checks exits (1), (3) and (4), in that order, after every model call, and takes (2) when its `for` runs out (see `loop.py`); it returns a `Result` with the answer, the `StopReason`, the iterations, the tokens used and the transcript:

1. **`COMPLETED`**: the final answer. In this teaching version it fires when the model asks for no tool; the post explains why a shipping loop also reads the provider's `stop_reason`.
2. **`MAX_ITERS`**: the iteration cap, `max_iters=12` by default, so that a loop always ends.
3. **`BUDGET`**: a token ceiling, `token_budget=None` (off) by default. It is checked after the call that spends the tokens, so a run can end over budget by up to one turn.
4. **`NO_PROGRESS`**: the same tool calls for `no_progress_window` turns running (3 by default), fingerprinted from the calls only.

```python
from agent_loop import run, ScriptedModel, tool_response, text_response, DEFAULT_TOOLS

model = ScriptedModel([
    tool_response("calculator", {"expression": "(2 + 3) * 4"}, tokens=12),
    text_response("The result is 20.", tokens=6),
])
result = run(model, DEFAULT_TOOLS, "What is (2 + 3) * 4?", max_iters=8, token_budget=10_000)
print(result.answer, result.stop_reason.value)   # -> The result is 20. completed
```

The post's `snippets/four_exits.py` drives `run()` to each of the four exits in turn; from the series root, `uv run python posts/03-the-agent-loop/snippets/four_exits.py`.

## Driving it with a real model

```bash
uv run --extra anthropic python -c "from agent_loop import run, AnthropicModel, DEFAULT_TOOLS; print(run(AnthropicModel(), DEFAULT_TOOLS, 'What is (2 + 3) * 4? Use the calculator.', max_iters=8).answer)"
```

with `ANTHROPIC_API_KEY` set in the environment (`export ANTHROPIC_API_KEY=...`, or `setx ANTHROPIC_API_KEY ...` on Windows). `AnthropicModel` defaults to the model id `claude-sonnet-5`; pass `model=` to choose another. The adapter is not exercised by the offline tests, which cover the `ScriptedModel` path only.

## Left out on purpose

Reading `stop_reason` for the final answer, the `is_error` flag on a failed tool's result, and streaming turns (all three in post 03); verification of the answer (post 11); hooks and enforcement (post 13); sandboxing beyond the calculator (post 14); and context compaction (post 09). This is the loop and its exits, and nothing else.
