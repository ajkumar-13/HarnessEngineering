# 06 - Tools and bash

The runnable companion to [06 - Tools as the agent's hands: bash, code, and schemas](../../posts/06-tools-bash-code/index.md). Schema validation, a validate-then-dispatch registry, and one general-purpose `bash` tool with a deny-list, in plain Python with no runtime dependencies: `schema.py` is 66 lines, `registry.py` 51 and `bash_tool.py` 64.

## What is here

| File | What it is |
|------|-----------|
| `src/tools/schema.py` | A small validator for a JSON Schema subset (`type`, `properties`, `required`, `enum`, `additionalProperties`, `items`): the tool contract. |
| `src/tools/registry.py` | `Tool` and `ToolRegistry.dispatch()`: validate, then execute; every outcome is returned as a string, and nothing raises. |
| `src/tools/bash_tool.py` | One general tool, `bash`, with a deny-list of 12 patterns checked before the command runs, and an injectable runner. |
| `src/tools/__main__.py` | An offline demo, `python -m tools`. |
| `tests/` | Fifteen tests: the schema accepting and rejecting, the deny-list blocking, and dispatch validating before it runs. No API key and no real shell. |

The `bash` runner is injected, so the test suite never touches a real shell: a dangerous command is asserted to be blocked before execution by a runner that records what reaches it.

## Quickstart (offline, no API key)

From this directory:

```bash
uv run python -m tools            # a safe command runs; a dangerous one is blocked; a malformed one is rejected
uv run --extra dev pytest -q      # the fifteen tests
```

The demo's safe command, `echo hello from the bash tool`, goes to the real shell through the default runner; the other two never reach it. The demo prints:

```text
tools exposed to the model:
  - bash: Run a shell command and return its combined stdout/stderr....

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
reg.dispatch("bash", {"command": "ls"})    # validate, execute, return an observation string
```

`dispatch()` validates the model's tool call against the schema, executes it only if it passes, and returns every outcome (success, block, validation error, or a tool exception) as a string the loop can feed back to the model.

## What the deny-list does not do

The deny-list matches spellings, not effects. It blocks `rm -rf /`, while `rm --recursive --force /`, `find / -delete` and a Python one-liner calling `shutil.rmtree` pass it; the post's `snippets/deny_list_bypass.py` shows this against the shipped patterns (from the series root, `uv run python posts/06-tools-bash-code/snippets/deny_list_bypass.py`). The suite does not test these bypasses: it tests what the deny-list blocks. The boundary that holds is the operating-system sandbox of post 14.

## Left out on purpose

Real sandboxing (allow-lists, isolation, no network egress: post 14), progressive disclosure of many tools and of Model Context Protocol (MCP) servers (post 07), the `is_error` flag on a failed result (post 03), and parallel tool execution (the section on parallel tool calls in post 06). This is the tool contract and one general tool, and nothing else.
