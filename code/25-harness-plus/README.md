# 25 - Build #2: hooks, sandbox, and sub-agents

The runnable companion to [25 - Build #2: add hooks, sandbox, and sub-agents](../../posts/25-build-harness-plus/index.md). Build #1's loop and tool registry ([24 - Build #1: a minimal agent harness from scratch](../../posts/24-build-minimal-harness/index.md)) with four bounded layers added around each tool call, all recorded by a tracer, in plain Python with no runtime dependencies.

## What is here

| Layer | Module | From | What it does |
|-------|--------|------|--------------|
| Hooks | `hooks.py` | [post 13](../../posts/13-hooks-enforcement/index.md) | A pre-tool deny-list of five patterns blocks a matching call before it runs, on any tool. |
| Sandbox | `sandbox.py` | [post 14](../../posts/14-permissions-sandboxes/index.md) | The bash tool refuses shell control characters, a first token not on the allow-list, any `..`, and absolute paths outside the jail, then runs an argument list with no shell and a timeout. |
| Approval | `approval.py` | [post 15](../../posts/15-human-in-the-loop/index.md) | A call to a tool marked `sensitive` waits for a decider's verdict. |
| Sub-agent | `subagent.py` | [post 16](../../posts/16-multi-agent-orchestration/index.md) | A `delegate` tool runs a sub-task through a caller-supplied `spawn` and returns only the answer. |
| Tracing | `observe.py` | [post 21](../../posts/21-observability-traces/index.md) | The run is recorded as a nested span tree held in memory. |

`harness.py` holds the loop and `_gated_dispatch`, which fixes the order for every tool call: the hook first, then the approval gate, then the call itself. The sandbox is not a step in that order but a check inside the bash tool, so `write_file` and `delegate` calls execute with no sandbox. Each tool span is tagged `blocked` (hook), `denied` (approval), `refused` (sandbox) or `ok`. `tools.py` and `models.py` carry Build #1's registry, schema validation and `ScriptedModel`. There is no verifier: `run()` takes none, and a final answer ends the run.

## Quickstart (offline)

From this directory:

```bash
uv run python -m harness_plus        # one guarded run, printed as a trace tree
uv run --extra dev pytest -q         # the thirteen tests
```

The demo scripts five model turns: `rm -rf /` (blocked by the hook), `curl http://example.com` (refused by the sandbox), a delegated sub-task (answered by a sub-agent in its own span), a sensitive `write_file` (approved), and a final answer. Its runner is a stand-in that executes nothing. It ends by printing:

```text
agent.run  [task=Do the guarded task. stop.reason=completed]
  iteration  [index=1]
    model.call  [tokens=10]
    tool.bash  [args={'command': 'rm -rf /'} outcome=blocked]
  iteration  [index=2]
    model.call  [tokens=10]
    tool.bash  [args={'command': 'curl http://example.com'} outcome=refused]
  iteration  [index=3]
    model.call  [tokens=10]
    tool.delegate  [args={'subtask': 'what is 2 + 2?'} outcome=ok]
      subagent.run  [task=what is 2 + 2? stop.reason=completed]
        iteration  [index=1]
          model.call  [tokens=6]
  iteration  [index=4]
    model.call  [tokens=10]
    tool.write_file  [args={'path': 'notes.md', 'content': 'done'} outcome=ok]
  iteration  [index=5]
    model.call  [tokens=6]
```

## What the sandbox is, and is not

The sandbox is a policy check in the agent's own process, not an operating-system boundary. The jail is a path-token filter: absolute tokens are compared with the jail by path components (`PurePosixPath`), so `/worksecrets` is not inside `/work`; `..` is refused by a substring test; relative paths are never compared; and `subprocess_runner` passes no `cwd=` and no `env=`, so a relative path runs wherever the harness process runs. The default allow-list is `echo`, `ls`, `cat` and `git`. The demo opts `python` and `pytest` in, and the module's own note says why that is dangerous: allow-listing an interpreter allow-lists everything it can run. There is no network isolation and no ephemeral runtime. Post 14's tier table says what a real boundary adds.

## Left out on purpose

- **A verification gate.** Build #1 has one; this build isolates the hardening layers, and the capstone of post 26 brings the gate back.
- **A persistent audit record.** The span tree lives in memory and ends with the process.
- **An approval timeout.** `review` calls the decider synchronously, with no default when nobody answers; post 15's `snippets/async_approval.py` adds one around this gate.
- **Hooks after the call.** `HookRegistry` holds only pre-tool hooks.
- **Forwarded limits for the sub-agent.** The demo's `spawn` passes the tracer only, so the child gets the default limits and its tokens never reach the parent's counter; the post's `snippets/spawn_limits.py` shows a spawn that forwards the gates, a cap and the remaining budget.

MIT licensed.
