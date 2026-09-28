# 06 · Tools and bash

The runnable companion to [Post 06 — Tools as the agent's hands](../../posts/06-tools-bash-code/index.md). Schema validation, a validate-then-dispatch registry, and one general-purpose `bash` tool with a deny-list — all offline-testable.

## What's here

| File | What it is |
|------|-----------|
| `src/tools/schema.py` | A tiny JSON-Schema-subset validator — the tool *contract*. |
| `src/tools/registry.py` | `Tool` + `ToolRegistry.dispatch()` — validate, then execute; never raises. |
| `src/tools/bash_tool.py` | One general tool: `bash`, with a deny-list and an **injectable runner**. |
| `src/tools/__main__.py` | Offline demo — `python -m tools`. |
| `tests/` | Schema accept/reject, deny-list blocking, dispatch validation. **No API key, no real shell.** |

The `bash` runner is injected, so the whole test suite runs without touching a real shell — dangerous commands are asserted *blocked before execution*.

## Quickstart (offline)

```bash
cd code/06-tools-and-bash
python -m pip install -e ".[dev]"

python -m tools     # safe command runs; dangerous one blocked; malformed one rejected
pytest -q
```

Expected demo output (abridged):

```
[safe     ] dispatch('bash', {'command': 'echo hello from the bash tool'})
            -> hello from the bash tool
[dangerous] dispatch('bash', {'command': 'rm -rf /'})
            -> blocked: command matches a deny-list rule (\brm\s+-[rf])
[malformed] dispatch('bash', {'cmd': 'echo oops'})
            -> error: invalid input: $: missing required property 'command'; $: unexpected property 'cmd'
```

## The idea in three lines

```python
from tools import ToolRegistry, make_bash_tool

reg = ToolRegistry([make_bash_tool()])     # one general tool, deny-listed
reg.dispatch("bash", {"command": "ls"})    # validate -> execute -> observation string
```

`dispatch()` validates the model's tool call against the schema, executes only if it passes, and returns every outcome — success, block, validation error, or a tool exception — as a string the loop can feed back to the model.

## What's deliberately left out

Real sandboxing (allow-lists, isolation, network egress — Post 14), progressive disclosure of many tools / MCP (Post 07), and parallel tool execution (Post 06 §5). This is the tool *contract* and one safe general tool — nothing else.
