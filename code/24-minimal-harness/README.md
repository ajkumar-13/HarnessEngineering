# 24 - Build #1: a minimal agent harness

The runnable companion to [24 - Build #1: a minimal agent harness from scratch](../../posts/24-build-minimal-harness/index.md). A minimal harness is small once the earlier posts are in place: four primitives wired together, in plain Python with no runtime dependencies.

| Primitive | Module | From |
|-----------|--------|------|
| The loop: reason, act, observe | `harness.py` | [03 - The agent loop: ReAct, control loops, and stopping](../../posts/03-the-agent-loop/index.md) |
| A schema-validated tool registry and a deny-listed bash tool | `tools.py` | [06 - Tools as the agent's hands: bash, code, and schemas](../../posts/06-tools-bash-code/index.md) |
| A verification gate, so that "done" means "verified" | `verify.py` | [11 - Verification loops: tests, self-critique, fail-fast](../../posts/11-verification-loops/index.md) |
| Layered exits: `completed`, `max_iters`, `budget`, `no_progress` | `harness.py` | posts 03 and [19 - Loop engineering: designing the loop that prompts the agent](../../posts/19-loop-engineering/index.md) |

`models.py` holds the model seam: `ModelResponse`, the offline `ScriptedModel` and the live `AnthropicModel`. The package is offline by design: driven by a `ScriptedModel` and an injected tool runner, it touches no network and needs no API key. Swapping in `AnthropicModel()` and `subprocess_runner` makes it live.

## The idea

A bare loop exits when the model *says* it is done, which is a victory declaration waiting to happen ([05 - Agent failure modes: victory declaration, context anxiety, doom loops](../../posts/05-agent-failure-modes/index.md)). Build #1's loop does not exit on a final answer alone: a candidate answer goes through the verification gate first. If the gate passes, the run stops as `completed` with `verified` true. If it fails, the failure report is fed back into the loop as the next observation and the agent tries again; success is silent and failures are verbose. A rejected answer still counts against the token budget, so the budget exit fires on that path as well as on the tool-call path.

```text
model -> final answer? --no--> run tools -> observe -> loop
              | yes
              v
       verification gate --pass--> completed, verified
              | fail
              v
   append the report, check the budget, keep looping
```

## Run it

From this directory:

```bash
uv run --extra dev pytest -q         # the ten tests: the gate and every exit, no API key
uv run python -m minimal_harness     # the offline demo
```

The demo has the agent write a buggy `is_palindrome`, the gate reject it with `is_palindrome('abc',) == True, expected False`, the agent fix it, and only then the run stop with `stop_reason : completed` after 4 iterations and 54 scripted tokens. To drive it live, install the `anthropic` extra (`uv run --extra anthropic ...`), set `ANTHROPIC_API_KEY`, and pass `AnthropicModel()` as the model; its default model identifier is `claude-sonnet-5`.

## What was deliberately left out

Build #1 is the honest minimum. It has no hooks, no real sandbox, no sub-agents, no human approval gate and no observability, and its bash tool runs commands with `shell=True` behind a deny list of eight patterns, which is a pre-filter, not a boundary. The verifier execs candidate code in-process, in the harness's own interpreter. [25 - Build #2: add hooks, sandbox, and sub-agents](../../posts/25-build-harness-plus/index.md) adds the hardening layers around each tool call. The workspace is an in-memory dictionary, and a run with no verifier reports `verified` true; the post explains both.

MIT licensed, like all code in this series.
