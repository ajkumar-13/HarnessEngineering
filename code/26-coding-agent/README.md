# 26 - Capstone: a long-running coding-agent harness

Companion code for [26 - Capstone: a long-running, trusted coding-agent harness](../../posts/26-capstone-coding-agent/index.md), the last post of the Harness Engineering series.

The capstone ties the series together. It is a driver that takes a **spec** (an ordered list of tasks, each with an objective verifier) and runs it to completion across fresh contexts, learning from each failure and stopping for a named reason. Everything is offline and deterministic: a scripted generator stands in for a model, and nothing imports anything outside the Python standard library.

| Concern | Module | From |
|---|---|---|
| The long-horizon driver: a fresh context per task, three stop reasons | `driver.py` | [18 - Long-horizon and multi-context execution: Ralph loops and context bridging](../../posts/18-long-horizon-ralph/index.md), [19 - Loop engineering: designing the loop that prompts the agent](../../posts/19-loop-engineering/index.md) |
| Planner, generator and an independent evaluator | `driver.py` | [12 - Planner, generator, evaluator: separating the roles](../../posts/12-planner-generator-evaluator/index.md) |
| The ratchet: a failure becomes a rule later attempts read | `memory.py` | [10 - Continual learning and the ratchet: every mistake becomes a rule](../../posts/10-continual-learning-ratchet/index.md) |
| Durable state: the workspace and a commit per task | `core.py`, `driver.py` | [08 - State and the filesystem: durable memory and git as state](../../posts/08-state-filesystem-git/index.md) |
| Observability: nested trace spans | `observe.py` | [21 - Observability and trace-driven repair: seeing what the harness did](../../posts/21-observability-traces/index.md) |
| A cost meter with a budget ceiling | `cost.py` | [19 - Loop engineering: designing the loop that prompts the agent](../../posts/19-loop-engineering/index.md), [23 - The economics of a harness and Harness-as-a-Service](../../posts/23-economics-haas/index.md) |

## The loop

```
plan(spec) -> tasks
  for each task, in a fresh context:
    attempt: generate -> evaluate (independent) -> pass? commit : learn a rule, retry
  stop when: the spec is complete, a task is out of attempts, or the budget is spent
```

Each generator call is handed three things: the task, the last failure report on that task (reset to none at every new task), and the rules the ratchet has learned. Only the workspace and the rules cross from one task to the next. The generator proposes and the task's verifier judges, so nothing grades its own work.

The three stop reasons map onto the series' four exits: `spec_complete` is exit (1), `task_failed` is exit (2) counted per task (there is no run-wide iteration cap), and `budget` is exit (3). There is no exit (4), no progress: a generator that returns the same wrong file on every attempt uses them all.

## Run it

From inside `code/26-coding-agent/`:

```bash
uv run --extra dev pytest -q        # 8 passed
uv run python -m coding_agent       # the offline demo
```

The demo runs a two-task build. The generator gets `add` wrong on its first attempt, the evaluator rejects it, the ratchet learns a rule, and the next attempt reads the rule and passes; `is_even` passes first time. It prints:

```
succeeded    : True  (spec_complete)
completed    : ['add', 'is_even']
commits      : ['add', 'is_even']
rules learned: ['[add] previously failed: add(2, 3) == -1, expected 5']
cost         : $0.0193 · 6000 in (4500 cached) · 900 out · 4.5s

== trace ==
build.run  [spec_tasks=2 stop.reason=spec_complete]
  task  [task=add passed=True]
    attempt  [index=1 outcome=fail]
      generate
      evaluate  [ok=False]
    attempt  [index=2 outcome=pass]
      generate
      evaluate  [ok=True]
  task  [task=is_even passed=True]
    attempt  [index=1 outcome=pass]
      generate
      evaluate  [ok=True]
```

The token counts are the driver's defaults (`tokens_per_attempt=(2000, 1500, 300)` per attempt), priced at $3 and $15 per million input and output tokens with cached input at 0.1 times the input rate. The meter has no cache-write term.

## The rules file

`Ratchet(path=...)` appends each new rule to a file as it is learned, and nothing in the package reads that file back. A new `Ratchet(path=...)` starts with an empty rule list, so a restarted process repeats mistakes an earlier one already learned from, and appends the same rules again. To carry learning across a restart, read the file back into `Ratchet(rules=..., path=...)`, without duplicate lines. The post's `snippets/spec_run.py` shows both.

## What it leaves out

The generator makes no tool calls, so there are no hooks, no permissions, no sandbox and no approval gate; the verifier runs `exec` on the generated source in the driver's own process, which is safe only while the generator is a script. The planner keeps the spec's order and nothing else, the workspace is a dictionary with no rollback, and the build is one agent. The post names where each missing piece wires into `build()`, and the order to add them in.

MIT-licensed, like all code in this series.
