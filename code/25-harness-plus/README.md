# Build #2 — hooks, sandbox, sub-agents

Companion code for **Harness Engineering, Post 25 — "Build #2: add hooks, sandbox, and sub-agents."**

Build #1 (Post 24) was the honest minimum: loop + tools + a verification gate + stop conditions. Build #2 keeps that engine and hardens it into something you would let run unattended. Each addition is small, bounded, and separately tested.

| Layer | Module | From | What it does |
|-------|--------|------|--------------|
| Hooks | `hooks.py` | Post 13 | A pre-tool deny-list blocks a dangerous call *before* it runs |
| Sandbox | `sandbox.py` | Post 14 | The bash tool runs behind an allow-list + path jail + timeout |
| Approval | `approval.py` | Post 15 | A sensitive tool call pauses for a human verdict |
| Sub-agent | `subagent.py` | Post 16 | A `delegate` tool runs a sub-task in its own fresh context |
| Tracing | `observe.py` | Post 21 | The whole run is recorded as a nested span tree |

The order matters and is enforced in `harness.py`: for every tool call the loop runs the **hook** first, then the **approval** gate, then executes (the bash tool's own **sandbox** enforces the jail). A `delegate` call spawns a **sub-agent**, and every step is wrapped in a **tracer** span.

## Run it

```bash
python -m harness_plus     # offline demo (add src to PYTHONPATH, or `pip install -e .`)
python -m pytest -q        # 13 passed
```

The demo runs one guarded task and prints the trace tree:

```
agent.run  [stop.reason=completed]
  iteration [index=1]
    model.call
    tool.bash      [outcome=blocked]      <- deny-list hook stopped `rm -rf /`
  iteration [index=2]
    tool.bash      [outcome=ok]           <- sandbox refused `curl` (not allow-listed)
  iteration [index=3]
    tool.delegate  [outcome=ok]
      subagent.run [stop.reason=completed] <- sub-agent, its own context, nested span
  iteration [index=4]
    tool.write_file[outcome=ok]           <- sensitive call, approved
```

## The point

None of these four layers makes the model smarter. Each shrinks the **blast radius** of a model that is wrong: a hook makes a class of mistakes structurally impossible, a sandbox bounds what any command can reach, an approval gate keeps a human on irreversible actions, and a sub-agent isolates a sub-task's context. The tracer is what lets you see all of it after the fact and ratchet the next fix (Post 21). The capstone (**Post 26**) assembles these into a long-running coding agent.

MIT-licensed, like all code in this series.
