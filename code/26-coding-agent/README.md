# Capstone — a long-running coding-agent harness

Companion code for **Harness Engineering, Post 26 — "Capstone: a long-running, trusted coding-agent harness."**

This ties the series together. It is a driver that takes a **spec** (an ordered list of tasks, each with an objective verifier) and runs it to completion across many fresh contexts, getting better as it goes and stopping for the right reason.

| Concern | Module | From |
|---------|--------|------|
| Long-horizon Ralph driver (fresh context per task) | `driver.py` | Posts 18, 19 |
| Planner / generator / independent evaluator | `driver.py` | Post 12 |
| The ratchet (every failure becomes a durable rule) | `memory.py` | Post 10 |
| Durable state: workspace + per-task commits | `core.py` | Post 08 |
| Observability: nested trace spans | `observe.py` | Post 21 |
| Cost & latency meter with a budget ceiling | `cost.py` | Posts 19, 23 |

## The loop

```
plan(spec) -> tasks
  for each task, in a fresh context:
    attempt: generate -> evaluate (independent) -> pass? commit : learn a rule, retry
  stop when: the spec is complete · a task is unfixable · the budget is spent
```

Only two things cross between tasks: the **workspace** (committed, git-like) and the **ratchet's learned rules**. That is the context bridge that lets a build outgrow a single window (Post 18). The generator proposes and a separate evaluator judges, so nothing grades its own work (Post 12).

## Run it

```bash
python -m coding_agent     # offline demo (add src to PYTHONPATH, or `pip install -e .`)
python -m pytest -q        # 8 passed
```

The demo runs a two-task build. The generator gets `add` wrong first; the evaluator rejects it; the ratchet learns a rule; the next attempt reads the rule and fixes it:

```
build.run  [stop.reason=spec_complete]
  task [task=add passed=True]
    attempt [index=1 outcome=fail]   generate -> evaluate(ok=False)
    attempt [index=2 outcome=pass]   generate -> evaluate(ok=True)   <- rule applied
  task [task=is_even passed=True]
    attempt [index=1 outcome=pass]

rules learned: ['[add] previously failed: add(2, 3) == -1, expected 5']
cost         : $0.0193 · 6000 in (4500 cached) · 900 out · 4.5s
```

## Where to take it next

Everything here is offline and deterministic so the *architecture* is legible. To make it live, swap the scripted generator for a model call (the Build #1 loop), run the evaluator's tests in the Build #2 sandbox, gate risky commits behind the Build #2 approval gate, and A/B two driver configurations on a fixed spec set (Post 22). The shape does not change; only the four seams become real.

MIT-licensed, like all code in this series.
