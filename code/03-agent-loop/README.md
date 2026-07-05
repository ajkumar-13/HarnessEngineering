# 03 · Agent loop

The runnable companion to [Post 03 — The agent loop](../../posts/03-the-agent-loop/index.md). A minimal **reason → act → observe** loop with the four layered stop conditions, in ~120 lines of plain Python.

## What's here

| File | What it is |
|------|-----------|
| `src/agent_loop/loop.py` | The loop. `run(...)` with all four stop conditions — read this first. |
| `src/agent_loop/models.py` | The `Model` protocol, an offline `ScriptedModel`, and a real `AnthropicModel`. |
| `src/agent_loop/tools.py` | Two tiny tools (`calculator`, `echo`); the calculator is AST-sandboxed, not `eval`. |
| `src/agent_loop/__main__.py` | An offline demo — `python -m agent_loop`. |
| `tests/` | One test per stop condition. Runs with **no API key**. |

The message format is **Anthropic-native**: the loop's `messages` list is exactly what you'd send to the Messages API, so the real adapter is a thin pass-through.

## Quickstart (offline, no API key)

```bash
cd code/03-agent-loop
python -m pip install -e ".[dev]"

python -m agent_loop      # watch one reason -> act -> observe -> answer cycle
pytest -q                 # every stop condition, offline
```

Expected demo output (abridged):

```
[user     ] What is (2 + 3) * 4?
[assistant] [{'type': 'text', ...}, {'type': 'tool_use', 'name': 'calculator', ...}]
[user      ] [{'type': 'tool_result', 'tool_use_id': 'tu_1', 'content': '20'}]
[assistant] [{'type': 'text', 'text': 'The result is 20.'}]

answer      : The result is 20.
stop_reason : completed
iterations  : 2
```

## The four stop conditions

`run()` checks these every turn (see `loop.py`):

1. **`COMPLETED`** — the model returned no tool call: a final answer. The exit you want.
2. **`MAX_ITERS`** — a hard iteration cap; the backstop so a loop always terminates.
3. **`BUDGET`** — a token ceiling; iterations are a poor proxy for cost.
4. **`NO_PROGRESS`** — the same tool call repeated for `no_progress_window` turns: thrashing.

```python
from agent_loop import run, ScriptedModel, tool_response, text_response, DEFAULT_TOOLS

model = ScriptedModel([
    tool_response("calculator", {"expression": "(2 + 3) * 4"}, tokens=12),
    text_response("The result is 20.", tokens=6),
])
result = run(model, DEFAULT_TOOLS, "What is (2 + 3) * 4?", max_iters=8, token_budget=10_000)
print(result.answer, result.stop_reason.value)   # -> The result is 20. completed
```

## Driving it with a real model

```bash
python -m pip install -e ".[anthropic]"
export ANTHROPIC_API_KEY=...        # Windows: setx ANTHROPIC_API_KEY ...
```

```python
from agent_loop import run, AnthropicModel, DEFAULT_TOOLS

result = run(AnthropicModel(model="claude-sonnet-5"), DEFAULT_TOOLS,
             "What is (2 + 3) * 4? Use the calculator.", max_iters=8)
print(result.answer)
```

`AnthropicModel` is a real adapter but is **not** exercised by the offline test suite (it needs a key). The `ScriptedModel` path is what the tests guarantee.

## What's deliberately left out

Verification of the answer (Post 11), hooks and enforcement (Post 13), sandboxing beyond the calculator (Post 14), context compaction (Post 09), and streaming turns (Post 03 §6). This is the loop and its exits — nothing else.
