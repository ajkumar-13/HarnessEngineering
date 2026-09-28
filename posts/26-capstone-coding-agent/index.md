# 26 · Capstone — a long-running, trusted coding-agent harness

> **TL;DR.** This is the whole series in one machine: a coding agent that takes a spec, runs it to completion across many fresh contexts, separates planning from generation from evaluation, learns from each failure, meters its own cost, and records everything it does. No single piece is new; the capstone is the assembly. The companion is [`code/26-coding-agent/`](../../code/26-coding-agent/): 429 lines across seven modules, offline, with an eight-test suite that passes without provider credentials. Several components the architecture calls for are left as seams rather than shipped, and this post names each one and where it wires in. The point it proves is the thesis of the series: the model is fixed, and the harness is what improves.
>
> **After reading this you will be able to:**
> - Assemble a long-horizon, self-verifying coding agent from the series' components, in an order where each step is testable.
> - Explain how durable state and a ratchet let a build outgrow a single context window.
> - Run a harness A/B on a fixed spec set with the model held constant, and read the verdict as resolved-rate against cost.
> - Name what this capstone does not implement, and say exactly where each missing gate would wire in.

![The full capstone architecture: a spec feeds a Ralph driver that runs each task through planner, generator, and independent evaluator; tool calls pass through hooks, sandbox, and approval; the workspace and ratchet persist across tasks; a tracer and cost meter run throughout; and traces feed an evaluation-and-fix improvement loop.](diagrams/01-capstone-architecture.svg)
*The target architecture: every component of Parts I to V in one harness. The companion implements the five modules of §1; the three gates in the middle are the seam §5 describes and says to fill first.*

The series began with an equation: `Agent = Model + Harness` (Trivedy, 2026), which [Post 01](../01-from-context-to-harness/index.md) opens on. Twenty-five posts later, the harness has a name for every part. This capstone puts them together into the thing the whole series was pointed at: a coding agent you could leave running.

---

## 1. The product spec

The target is a harness that accepts a **spec** (an ordered list of tasks, each with an objective check) and drives it to completion or stops for a nameable reason. It must run builds larger than one context window, verify its own work, guard its tools, remember its mistakes, stay inside a budget, and leave a trace of everything. Each of those adjectives maps to exactly one component already built.

The companion keeps the whole thing offline and deterministic so the *architecture* is legible: a scripted generator stands in for a model, and the eight-test suite passes with no application programming interface (API) key and no network. Legibility is bought at a price, and the price is that the guard layer is architectural rather than implemented. §5 names it; §12 lists it next to every other limitation.

### Where five of the series' components physically live

The capstone is five modules, and each one is a post you have already read:

| Module | What it holds | Posts |
|---|---|---|
| `core.py` | the spec as source of truth; the versioned workspace; the verifier | [08](../08-state-filesystem-git/index.md), [11](../11-verification-loops/index.md), [18](../18-long-horizon-ralph/index.md) |
| `driver.py` | the long-horizon loop: fresh context per task, separated roles, layered exits | [03](../03-the-agent-loop/index.md), [12](../12-planner-generator-evaluator/index.md), [18](../18-long-horizon-ralph/index.md), [19](../19-loop-engineering/index.md) |
| `memory.py` | the ratchet: a failure becomes a rule later attempts read | [10](../10-continual-learning-ratchet/index.md), [13](../13-hooks-enforcement/index.md) |
| `observe.py` | nested spans; the whole build as one trace tree | [21](../21-observability-traces/index.md), [22](../22-evaluating-harnesses/index.md) |
| `cost.py` | the meter, the cache discount, the budget ceiling | [05](../05-agent-failure-modes/index.md), [19](../19-loop-engineering/index.md), [23](../23-economics-haas/index.md) |

Two of those rows are not obvious. **[Post 05](../05-agent-failure-modes/index.md) against `cost.py`**: the budget ceiling is the harness fix for the doom loop, one of the six recurring failure modes ([Post 05](../05-agent-failure-modes/index.md) §2), and a doom loop is stopped not by a better model but by something outside the loop that counts. **[Post 13](../13-hooks-enforcement/index.md) against `memory.py`**: [Post 10](../10-continual-learning-ratchet/index.md) §4 gives the ratchet three teeth, a line in a memory file, a hook that enforces the rule, and a reviewer check that catches the regression, and this companion ships only the first. Its absence is the same absence §5 is about, because a rule that suggests is not a rule that enforces ([Post 13](../13-hooks-enforcement/index.md) §5).

The roles of [Post 12](../12-planner-generator-evaluator/index.md) live inside `driver.py` rather than in a module of their own, because separation of planner, generator and evaluator is a property of *how the driver calls them*, not a thing you can put in a file.

---

## 2. Layout

The whole companion is 429 lines of source and 104 lines of tests. Reading it top to bottom takes about twenty minutes, which is the argument for building a harness by hand once before renting one:

```
code/26-coding-agent/
├── pyproject.toml                 # no runtime dependencies; pytest for dev
├── README.md
├── src/coding_agent/
│   ├── __init__.py         (20)   # the public surface, re-exported
│   ├── __main__.py         (52)   # the offline demo: python -m coding_agent
│   ├── core.py             (73)   # Workspace, Task, Spec, VerifyResult, verifier
│   ├── driver.py          (135)   # plan() and build(): the Ralph loop
│   ├── memory.py           (36)   # Ratchet: learn(), as_context()
│   ├── observe.py          (63)   # Span, Tracer: nested spans, render()
│   └── cost.py             (50)   # CostMeter: pricing, cache discount, ceiling
└── tests/
    └── test_coding_agent.py (104) # eight tests, no network, no API key
```

Nothing imports anything outside the standard library. Every module in this list is a component the series argued for, and a reader checking whether the argument survived contact with code should be able to do that without resolving a dependency tree first. The largest file is the driver, and it is largest because it is the only place the components meet. The demo entry point is `__main__.py`: it builds a two-task spec, hands it a scripted generator, and prints the commits, the learned rules, the cost line and the trace tree. Every number quoted in the rest of this post comes from running it.

---

## 3. The long-horizon driver

The engine is a Ralph loop: reset to a fresh context against a written spec, do one task, commit, repeat (Huntley, 2025), treated at length in [Post 18](../18-long-horizon-ralph/index.md). Each task gets plan, generate, evaluate, and on success commit; on failure, learn and retry. The context is discarded between tasks so it never rots, while two durable stores carry the thread forward.

![Three task contexts run left to right, each fresh and discarded at the end; below them, the workspace and the ratchet persist and accumulate, so state and lessons cross the resets. Each durable store shows what it holds after every task: the workspace going from parser.py committed, to unchanged and re-read, to parser.py plus the task 3 file; the ratchet going from one rule learned from the failure, to that rule injected and obeyed, to two rules carried into every later context.](diagrams/02-multi-context-run.svg)
*The context resets each task; the workspace and the ratchet do not.*

This is how a build outgrows one window. The spec is the source of truth, the workspace is versioned state ([Post 08](../08-state-filesystem-git/index.md)) that accumulates as git-like commits, and the ratchet is the learning that survives a reset. Reset to stay sharp; persist to keep progress.

The whole loop is one function, and it is short enough to read in full:

```python
# code/26-coding-agent/src/coding_agent/driver.py
def build(spec: Spec, generator: Generator, *,
          workspace: Optional[Workspace] = None,
          ratchet: Optional[Ratchet] = None,
          cost: Optional[CostMeter] = None,
          tracer: Optional[Tracer] = None,
          max_attempts: int = 3,
          learn_after: int = 1,
          rule_from: Callable[[Task, str], str] = _default_rule,
          tokens_per_attempt: tuple = (2000, 1500, 300),  # (input, cached, output)
          seconds_per_attempt: float = 1.5) -> BuildResult:
    workspace = workspace if workspace is not None else Workspace()
    ratchet = ratchet if ratchet is not None else Ratchet()
    cost = cost if cost is not None else CostMeter()
    commits: List[Commit] = []
    completed: List[str] = []
    in_tok, cached_tok, out_tok = tokens_per_attempt

    with _maybe_span(tracer, "build.run", spec_tasks=len(spec.tasks)) as run_span:
        for task in plan(spec):
            with _maybe_span(tracer, "task", task=task.name) as task_span:
                feedback: Optional[str] = None
                passed = False

                for attempt in range(1, max_attempts + 1):
                    # budget is an economic stop condition, checked before spend
                    if cost.over_budget():
                        run_span.set("stop.reason", "budget")
                        return BuildResult(False, completed, commits, ratchet.rules,
                                           cost, "budget", task.name,
                                           tracer.root if tracer else None)

                    with _maybe_span(tracer, "attempt", index=attempt) as att:
                        with _maybe_span(tracer, "generate"):
                            files = generator(task, feedback, ratchet.as_context())
                            workspace.files.update(files)
                            cost.add(input_tokens=in_tok, cached_tokens=cached_tok,
                                     output_tokens=out_tok, seconds=seconds_per_attempt)

                        with _maybe_span(tracer, "evaluate") as ev:
                            verdict = task.verify(workspace)
                            ev.set("ok", verdict.ok)

                        if verdict.ok:
                            att.set("outcome", "pass")
                            commits.append(Commit(task.name, workspace.snapshot()))
                            completed.append(task.name)
                            passed = True
                            break

                        att.set("outcome", "fail")
                        feedback = verdict.report
                        if attempt >= learn_after:
                            ratchet.learn(rule_from(task, verdict.report))

                task_span.set("passed", passed)
                if not passed:
                    run_span.set("stop.reason", "task_failed")
                    return BuildResult(False, completed, commits, ratchet.rules,
                                       cost, "task_failed", task.name,
                                       tracer.root if tracer else None)

        run_span.set("stop.reason", "spec_complete")
    return BuildResult(True, completed, commits, ratchet.rules, cost,
                       "spec_complete", None, tracer.root if tracer else None)
```

Two loops, nested. The outer one walks the spec's tasks; the inner one is the verify-and-retry loop of [Post 11](../11-verification-loops/index.md). That is exactly the composition [Post 19](../19-loop-engineering/index.md) §7 describes, with `max_attempts` bounding the inner loop and the spec bounding the outer one.

### What actually stops it

A series whose recurring claim is that most agent bugs are stop-condition bugs ([Post 03](../03-the-agent-loop/index.md) §7) owes the reader an exit list rather than a gesture at one. The companion has three, and the fourth is missing:

| Exit | What fires it | `stop_reason` | Where it maps in [Post 19](../19-loop-engineering/index.md) §2 |
|---|---|---|---|
| the spec verifies | every task's verifier passed | `spec_complete` | ① the intended exit, and the only success |
| a task is unfixable | `max_attempts` attempts all failed | `task_failed` | ② the hard iteration cap |
| the budget is spent | `cost.over_budget()` at the top of an attempt | `budget` | ③ the token or money ceiling |
| *no-progress* | *nothing; not implemented* | *not applicable* | ④ the thrashing guard, absent |

The fourth row is the honest one. `max_attempts=3` is an iteration cap, not a no-progress detector: a generator that returns the identical wrong file three times burns all three attempts, and the harness never notices that nothing changed between them. Adding the detector is two lines against the workspace snapshot, and doing it yourself is the fastest way to feel the difference between exit ② and exit ④.

The abort semantics deserve stating too, because a reader will otherwise assume the friendlier version. When a task exhausts its attempts, `build()` returns immediately with `succeeded=False`: it does not skip the task, escalate it, or carry on with the rest of the spec. What it does do is return `completed` and `commits` intact, so the verified work is still in hand and the run has a resumable position, which is the behaviour [Post 19](../19-loop-engineering/index.md) §8 argues every guard exit should have. A production driver adds two policies on top: skip-and-continue for tasks the rest of the spec does not depend on, and escalate-to-human for the ones it does ([Post 15](../15-human-in-the-loop/index.md) §9).

---

## 4. Planner, generator, evaluator

Inside each task the roles are separated ([Post 12](../12-planner-generator-evaluator/index.md)). A **planner** sequences the work, a **generator** proposes code, and an **independent evaluator** judges it against the task's objective check. The separation is the whole reliability argument: an agent grading its own output skews positive, so the evaluator is a different component with its own ground truth ([Post 11](../11-verification-loops/index.md)). In the capstone the evaluator is the task's verifier, and only a candidate it passes is committed.

The planner is the role to be honest about, because in the companion it does nothing:

```python
# code/26-coding-agent/src/coding_agent/driver.py
def plan(spec: Spec) -> List[Task]:
    """The planner. Here it preserves order; a real planner would decompose and
    sequence. Separated out so the role is explicit (Post 12)."""
    return list(spec.tasks)
```

An identity function is a stand-in, not a planner. It is also the least bad thing to leave hollow, because the planner is the one role with no independent check on it ([Post 12](../12-planner-generator-evaluator/index.md) §8): an evaluator catches a bad generation, but nothing in the architecture catches a badly decomposed spec except a person reading it. A stub that visibly does nothing is easier to notice than a planner that quietly decomposes badly, and the seam is in the right place for a real one to be dropped in.

The evaluator is the opposite case, and it is where the companion earns its keep:

```python
# code/26-coding-agent/src/coding_agent/core.py
def python_function_verifier(path: str, fn_name: str, cases) -> Verifier:
    """Build a verifier that execs a workspace file and runs cases against a
    function it defines. Exceptions are reported, never propagated."""
    cases = list(cases)

    def verify(ws: Workspace) -> VerifyResult:
        source = ws.files.get(path)
        if source is None:
            return VerifyResult(False, f"no file at {path!r}")
        ns: dict = {}
        try:
            exec(compile(source, path, "exec"), ns)
        except Exception as exc:
            return VerifyResult(False, f"{path} import error: {type(exc).__name__}: {exc}")
        fn = ns.get(fn_name)
        if not callable(fn):
            return VerifyResult(False, f"no callable {fn_name!r} in {path}")
        for args, expected in cases:
            try:
                got = fn(*args)
            except Exception as exc:
                return VerifyResult(False, f"{fn_name}{args!r} raised {type(exc).__name__}")
            if got != expected:
                return VerifyResult(False, f"{fn_name}{args!r} == {got!r}, expected {expected!r}")
        return VerifyResult(True)

    return verify
```

Count the `VerifyResult(False, ...)` branches: five, each naming a different reason, and the last carrying the actual value alongside the expected one. That verbosity is load-bearing, and the chain it starts is the most important one in the companion. On the demo's first attempt the verifier returns `VerifyResult(False, "add(2, 3) == -1, expected 5")`. That exact string becomes `feedback` on the next attempt, and the ratchet renders it into a rule: `[add] previously failed: add(2, 3) == -1, expected 5`. A verifier that returned a bare boolean, or a report reading "test failed", would produce a rule that teaches nothing, and the ratchet of §6 would climb on noise. The rule that "success is silent, failures are verbose" ([Post 11](../11-verification-loops/index.md) §4) is usually presented as a courtesy to the generator; here it is the precondition for learning at all.

Note also what the verifier never does: raise. Every exception in the model-written code is caught and converted into a report, because an evaluator that propagates the generator's exception kills the run at the exact moment it had something useful to say.

---

## 5. The guards, and the seam where they belong

In the target architecture, every tool call the generator makes runs the Build #2 gauntlet ([Post 25](../25-build-harness-plus/index.md)): a deterministic **hook** can block it ([Post 13](../13-hooks-enforcement/index.md)), a **sandbox** bounds what it can reach ([Post 14](../14-permissions-sandboxes/index.md)), and an **approval gate** escalates the irreversible to a person ([Post 15](../15-human-in-the-loop/index.md)). A long-running agent is a long-running attack surface, so the guards are what make "leave it running" a sentence you can say without flinching.

**The companion does not ship any of them.** The generator it takes is typed `Callable[[Task, Optional[str], str], dict]`: it returns a dictionary of files and makes no tool calls, so there is nothing for a gauntlet to stand in front of. The gauntlet is real and lives in [`code/25-harness-plus/`](../../code/25-harness-plus/); this build is where you would wire it in, and §11 lists that as seam two. The wiring points are concrete rather than hand-wavy, which is the useful thing to take from this section:

| Gate | Where it wires into `build()` | What it stops | From |
|---|---|---|---|
| pre-tool hook | before `workspace.files.update(files)` | a generated write to a path the run may not touch | [Post 13](../13-hooks-enforcement/index.md) |
| sandbox | around `task.verify(workspace)` | the evaluator's own execution of model-written code | [Post 14](../14-permissions-sandboxes/index.md) |
| approval gate | before `commits.append(...)` | an irreversible commit nobody looked at | [Post 15](../15-human-in-the-loop/index.md) |

The middle row is the alarming one, and it should be said plainly rather than left for a reader to find. `python_function_verifier` runs `exec(compile(source, path, "exec"), ns)` on generator-written source, in the driver's own process, with no jail, no timeout and no allow-list. That is precisely the pattern [Post 24](../24-build-minimal-harness/index.md) §10 flags in Build #1 and [Post 25](../25-build-harness-plus/index.md) §4 exists to replace. It is safe here only because the generator is a scripted stand-in whose output is a literal in `__main__.py`; swap in a model and it stops being safe in the same instant, which is why the evaluator's `exec` is the capstone's most dangerous line and the one seam to fill first.

Build #2's own history is the argument for treating this as urgent rather than tidy. Three guardrail bugs shipped in that companion and were found by probing rather than by reading ([Post 25](../25-build-harness-plus/index.md) §10), and two of them are the ones that bite here: an allow-list that checked a command's first token and then ran the raw string through a shell, so `echo hi; curl http://evil` walked straight through it, and a sandbox refusal that came back as an ordinary return value and therefore landed in the trace tagged `ok`, making the third of four gates the one you could not see fire ([Post 14](../14-permissions-sandboxes/index.md) §5). Both bugs survived a passing test suite. A gate you cannot see fire is a gate you do not have, and a gate you have not written is not improved by a diagram that draws it.

---

## 6. Memory and the ratchet

The capstone's defining feature is that it *improves within a run*. When a task fails, the driver asks the **ratchet** to learn a rule ([Post 10](../10-continual-learning-ratchet/index.md)). The rule is appended to a memory store and injected into the generator's context on every later attempt and every later task. The store is 36 lines:

```python
# code/26-coding-agent/src/coding_agent/memory.py
@dataclass
class Ratchet:
    """An append-only list of learned rules, optionally mirrored to a file."""
    rules: List[str] = field(default_factory=list)
    path: Optional[str] = None

    def learn(self, rule: str) -> bool:
        """Record a rule if it is new. Returns True if it was added."""
        if rule in self.rules:
            return False
        self.rules.append(rule)
        if self.path is not None:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(rule + "\n")
        return True

    def as_context(self) -> str:
        """Render the rules for injection into the generator (a pilot's
        checklist, not a style guide)."""
        if not self.rules:
            return ""
        lines = "\n".join(f"- {r}" for r in self.rules)
        return "Learned rules (do not repeat past mistakes):\n" + lines
```

The demo shows the mechanism plainly: the generator gets `add` wrong, the evaluator rejects it, the ratchet records the lesson, and the next attempt reads that lesson and fixes it. A mistake becomes a durable constraint, with no model update at all. Three things about this implementation are worth knowing before you run one past task three.

**There is no "worth remembering" filter.** `build()` ships `learn_after=1`, so a rule is recorded after *every* failed attempt, and the only de-duplication is `learn()`'s exact-string match: two failures whose reports differ by one integer produce two rules. Raising `learn_after` is the crude version of [Post 10](../10-continual-learning-ratchet/index.md) §3's "earn each line" rule; the real filter is a person deciding which failures generalise beyond the task that produced them.

**There is no pruning and no size bound.** Every rule ever learned is rendered by `as_context()` into every generator call for the rest of the run. On a fifty-task build with one failure apiece, that is fifty rules injected into every later attempt, most of them about tasks already committed and verified. [Post 10](../10-continual-learning-ratchet/index.md) §9 has the name for what that becomes: the memory file turns into exactly the context clutter it was meant to prevent. A production ratchet drops a rule when the task it belongs to is committed, or promotes it into a hook and deletes the line.

**Rules are volatile, and the spec is not.** The rules block grows on every failure, so it is the most volatile thing in the context; the spec is byte-identical on every task. Put the rules above the spec and you invalidate the cached prefix on every attempt, which turns the cheap resets of §3 into expensive ones and costs the multiplier in §8's table. Stable first, volatile last ([Post 18](../18-long-horizon-ralph/index.md) §4). The ratchet is the one component here whose placement in the context stack is a cost decision as much as a correctness one.

One field earns a mention because durability is the point. `Ratchet(path=...)` mirrors every rule to a file as it is learned: without it, learning survives a context reset and dies with the process; with it, learning survives a restart, which is the difference between a run that improves and a fleet that does ([Post 08](../08-state-filesystem-git/index.md)).

---

## 7. Observability and harness A/B

The whole run is wrapped in a tracer ([Post 21](../21-observability-traces/index.md)), so it renders as one span tree: the build, each task, each attempt, and the generate and evaluate pair inside each attempt. This is the demo's actual output, unabridged:

```
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

Twelve lines, and the run's whole story is in the nesting: `add` took two attempts and the second passed, `is_even` passed first time, and the run ended for the right reason. That is the trace tree of [Post 21](../21-observability-traces/index.md) §4 at the smallest scale it is still useful at, and the shape scales, because a fifty-task build is read the same way, by scanning for `outcome=fail` lines and descending only there.

The trace is not just a post-mortem. It is the raw material of evaluation ([Post 22](../22-evaluating-harnesses/index.md)): score whole trajectories on a fixed spec set, and A/B two driver configurations with the model held fixed.

### Running the A/B

The companion exposes exactly the knobs an A/B would vary: `max_attempts`, `learn_after`, `rule_from` and `tokens_per_attempt`. Vary one, hold the scripted generator (this build's "model") and the spec fixed, and the protocol of [Post 22](../22-evaluating-harnesses/index.md) §7 runs offline in a few lines:

```python
# generator is the demo's, from __main__.py; mkspec() builds its two-task spec
for learn_after in (1, 99):                    # the ratchet on, then off
    cost = CostMeter(budget_usd=1.00)
    res = build(mkspec(), generator, workspace=Workspace(), ratchet=Ratchet(),
                cost=cost, learn_after=learn_after, max_attempts=3)
    print(learn_after, res.succeeded, res.stop_reason, res.completed, cost.summary())
```

`learn_after=99` is the ratchet switched off: no attempt ever reaches the threshold, so no rule is ever learned, so the generator never sees the lesson. The verdict:

| Config | Resolved | Stop reason | Tasks completed | Spend | Cost per completed task |
|---|---|---|---|---|---|
| `learn_after=1` (ratchet on) | 2 of 2 | `spec_complete` | `['add', 'is_even']` | $0.0193 | $0.0097 |
| `learn_after=99` (ratchet off) | 0 of 2 | `task_failed` | `[]` | $0.0193 | undefined: nothing completed |

Both configurations spend the same money and burn the same three attempts. One finishes the spec; the other finishes nothing, because it retries the same wrong file until the cap fires. That is the series' central claim reduced to a number a reader can reproduce offline: the model held fixed, one harness component moved, and the resolved-rate from zero to one hundred per cent at identical cost.

The same experiment at production scale gives the headline result this series cites. LangChain moved `deepagents-cli` from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points that carried it from roughly the top thirty of the leaderboard into the top five, with the model held fixed at `gpt-5.2-codex` (Trivedy, LangChain, 2026). None of that was a better model.

![A four-stage cycle: the harness run emits traces; traces feed evaluation and A/B; failures localise to a component and become a ratcheted fix; the fix changes the harness and the run repeats. Below, the span tree the demo actually prints: a build run over two spec tasks ending with stop.reason spec_complete, the add task passing on its second attempt after the first failed its evaluation, and is_even passing first time. A panel gives what the tree buys: the shape is the eval, the failure has an address at attempt 1 of add at evaluate, and that attempt becomes a replay the next harness cannot lose.](diagrams/03-eval-observability-loop.svg)
*The model is fixed; the loop around it ratchets upward.*

The second arrow on that diagram is worth stating as a mechanism rather than leaving as a caption. When a trace exposes a failure, the fix is not only a code change: the spec that produced the failure becomes a task in the fixed set, and from then on it guards the regression's return ([Post 22](../22-evaluating-harnesses/index.md) §4, [Post 21](../21-observability-traces/index.md) §7). That is the ratchet of §6 applied to the harness rather than to the run. A failure that is only fixed can come back; a failure that is fixed and added to the set cannot come back quietly.

---

## 8. Cost guardrails

Loops multiply cost, so the driver carries a **cost meter** ([Post 23](../23-economics-haas/index.md)) that sums tokens and seconds across every attempt, prices them with a discount for the cached re-read of the stable prefix, and enforces a budget ceiling. The ceiling is both an economic control and a stop condition ([Post 19](../19-loop-engineering/index.md) §9), and an autonomous agent without one is a bill waiting to happen. The demo's cost line is worth reading closely, because it shows the architecture paying for itself:

```
cost : $0.0193 · 6000 in (4500 cached) · 900 out · 4.5s
```

**Three quarters of the input was cached.** That is the freeze-the-prefix rule doing its work ([Post 18](../18-long-horizon-ralph/index.md) §4, itself inherited from Context Engineering, Post 05): each task starts a fresh context and re-reads the spec, which sounds like paying full price repeatedly and is not, because the spec sits in a byte-stable prefix.

How much that discipline is worth is smaller than the headline suggests. Removing the cache from the demo's numbers gives `6000 × $3/M + 900 × $15/M = $0.0315` against the actual $0.0193: a factor of 1.63, not several times over. The multiplier grows with how input-heavy the run is, because caching only discounts the input side:

| Run shape | input : output | with a 75% cached prefix | with no cache | penalty |
|---|---|---|---|---|
| the demo, generation-heavy | 6,000 : 900 (6.7 to 1) | $0.0193 | $0.0315 | 1.63× |
| a context-heavy task | 10,000 : 1,000 (10 to 1) | $0.0248 | $0.0450 | 1.82× |
| a long-horizon re-read | 20,000 : 1,000 (20 to 1) | $0.0345 | $0.0750 | 2.17× |

The last row is the reason prefix discipline matters more the longer the horizon: a driver that re-reads a large spec on every one of fifty tasks is the shape where losing the cache costs most.

**Output is a seventh of input and most of the money.** At $3 and $15 per million tokens, the 900 output tokens cost $0.0135 of the $0.0193: 70% of the bill from 13% of the tokens. That asymmetry is the reason "keep generations tight" is a cost control and not a style preference.

**The 0.1× multiplier is real, and the meter models only half of it.** `cost.py` hard-codes `cache_discount = 0.1`, and a cache read is indeed charged at 0.1 times the base input rate (Anthropic, 2025). What the meter omits is the write side: a cache *write* costs 1.25 times base at the five-minute time-to-live and 2 times base at the hour, and a prefix not re-read inside its window expires and is paid for again. That bites a Ralph driver specifically, because a task that writes a feature and runs a test suite routinely takes longer than five minutes. [Post 18](../18-long-horizon-ralph/index.md) §4 prices the grid and finds a case where the default tier costs 25% *more* than no caching at all. Seventy-five per cent cached is the ceiling of what caching buys, not the number a slow driver will see.

**The ceiling is checked at the top of each attempt, before that attempt spends.** `if cost.over_budget(): stop` sits above the generate-and-evaluate pair, so no attempt begins once the budget is gone. What it does *not* do is reserve for the attempt about to run: the check is `spent >= ceiling`, so the attempt that crosses the line still completes, and the overshoot is bounded by one attempt exactly as in [Build #1](../24-build-minimal-harness/index.md). That is a defensible choice for a legible reference implementation and a poor one for a long-horizon production run, where attempts get expensive and there are many of them. [Post 19](../19-loop-engineering/index.md) §4 has the version that reserves an estimate for the next call and therefore never crosses at all, and prices the difference: an arrears check on a growing context overran a 200,000-token ceiling by 18%. Upgrading the meter is a two-line change and worth making before you point this at a real budget.

The meter is also what makes the eval loop of §7 quantitative. "Did that change help?" is unanswerable without a cost per completed task, because almost any harness change can buy reliability by spending more, and a comparison that ignores the bill will always prefer the expensive option.

---

## 9. Tests

Eight tests, 104 lines, no network and no API key. `python -m pytest -q` reports `8 passed` in about two hundredths of a second, which matters more than it sounds: a suite this fast gets run on every edit, and that is the only kind that catches a regression while the change is still in your head.

Three of the eight are worth reading in full, because between them they pin most of what this post claims about the driver:

```python
# code/26-coding-agent/tests/test_coding_agent.py
def test_ratchet_learns_from_failure_then_the_fix_lands():
    # buggy until a rule about 'add' exists in memory, then correct
    def gen(task, feedback, memory):
        return {"calc.py": ADD_OK if "[add]" in memory else ADD_BUG}

    ratchet = Ratchet()
    res = build(Spec([_add_task()]), gen, ratchet=ratchet, max_attempts=3)
    assert res.succeeded is True
    assert res.rules_learned                       # a rule was recorded
    assert any("[add]" in r for r in res.rules_learned)
    # it took a second attempt: the fix used the learned rule
    assert res.completed == ["add"]


def test_budget_ceiling_stops_the_run():
    # a tiny budget: the very first attempt's cost exceeds it on the next check
    cost = CostMeter(budget_usd=0.00001)
    # first task passes but spends; a second task's pre-attempt check trips budget
    spec = Spec([_add_task(), _add_task()])
    res = build(spec, _good_gen, cost=cost, max_attempts=2)
    assert res.stop_reason == "budget"
    assert res.succeeded is False


def test_trace_tree_has_the_expected_shape():
    tracer = Tracer()
    spec = Spec([_add_task()])
    res = build(spec, _good_gen, tracer=tracer)
    assert res.trace is not None
    assert tracer.count("build.run") == 1
    assert tracer.count("task") == 1
    assert tracer.count("generate") == 1
    assert tracer.count("evaluate") == 1
    assert res.trace.attributes.get("stop.reason") == "spec_complete"
```

What each of the eight pins down, and what it deliberately leaves alone:

| Test | What it pins | What it leaves open |
|---|---|---|
| `test_build_completes_a_passing_spec` | one task, one commit, `spec_complete` | failure handling |
| `test_ratchet_learns_from_failure_then_the_fix_lands` | a failure produces a rule; the rule changes the next attempt | *how many* attempts, so a regression to three would pass |
| `test_unfixable_task_stops_the_build` | exit ②: attempts exhaust, nothing committed | whether the run is resumable |
| `test_budget_ceiling_stops_the_run` | exit ③ fires before an attempt, not after | the one-attempt overshoot of §8 |
| `test_ratchet_is_append_only_and_dedupes` | `learn()` is idempotent on an exact repeat | near-duplicates, not handled at all |
| `test_cost_meter_prices_and_discounts_cache` | the pricing arithmetic, cached and fresh separately | the write premium, which the meter omits |
| `test_trace_tree_has_the_expected_shape` | one span of each kind, `stop.reason` on the root | the values inside the tree |
| `test_commits_snapshot_growing_workspace` | state accumulates: commit two carries both files | rollback, because there is none |

### What the suite structurally cannot see

This is the part worth taking away, and [Post 25](../25-build-harness-plus/index.md) §10 is the reason to write it down. A suite is blind in the shape of the questions it asks, and three blindnesses here are structural rather than accidental.

**Every generator in the suite is a pure function of its arguments.** All eight tests inject a scripted generator that returns a literal, so nothing ever exercises a generator that calls a tool, writes outside the workspace, or takes an unbounded amount of time. That is exactly why the missing gates of §5 cost the suite nothing: a test suite cannot fail on a component you did not write.

**The verifier's `exec` is never given hostile input.** Every source string the tests hand it is a well-formed function definition written by the test author. A generator that emitted `import os` followed by a system call would have it executed, and all eight tests would still pass. That is the same failure shape as Build #2's allow-list bug: a boundary tested only with the traffic you anticipate is tested for correctness, not for safety.

**The trace test asserts shape, not content.** `tracer.count("evaluate") == 1` passes whether the span says `ok=True` or `ok=False`. That is the precise bug [Post 25](../25-build-harness-plus/index.md) §10 records under "the gate you could not see fire", reproduced here in a suite written after that lesson was learned.

---

## 10. Deployment shape

In production the harness is a service, not a script. What changes is not the architecture but where each durable thing lives, what starts a run, and where a person sits.

### What is durable, and where

| Store | In the companion | In production |
|---|---|---|
| the spec | `Spec`, built in `__main__.py` | a versioned file in the repository, which is what makes it a source of truth rather than a prompt ([Post 18](../18-long-horizon-ralph/index.md) §5) |
| the workspace | `Workspace.files`, a dictionary | a git branch; real worktrees and merges are [Post 17](../17-parallel-agents-shared-repo/index.md) §5 |
| the ratchet | `Ratchet()`, in memory | `Ratchet(path=...)` on a repository file: reviewable, diffable, prunable ([Post 10](../10-continual-learning-ratchet/index.md) §9) |

The first row carries a design decision worth copying. Anthropic's reference harness stores the spec as `feature_list.json`, a list of features each carrying a pass status, and instructs the coding agent to edit that file only by flipping the status field (Anthropic, 2025). Constraining *how* the agent may write to the spec is what stops a struggling agent from lowering the bar ([Post 18](../18-long-horizon-ralph/index.md) §6). The third row is the one-line change with the largest payoff here: without a path, everything the run learned dies with the process.

### What starts a run, and where the person sits

A schedule and a webhook are both defensible, and they differ in one property that matters. A cron entry that restarts a long-horizon build from zero every hour has thrown away the resumable position §3 works to preserve. A trigger that hands the driver a position instead (the spec, the branch, the rules file, the last stop reason) resumes rather than restarts, which is what turns a stop into a handoff ([Post 19](../19-loop-engineering/index.md) §8). Whether the trigger is a timer or a pull-request event is a preference; whether it resumes is not. The service surface around it is small: an endpoint that accepts a spec and returns a run identifier, one that reports status and stop reason, and a stream of spans to an observability backend ([Post 21](../21-observability-traces/index.md) §10).

The approval gate becomes a pull request, which is the deployment-shaped version of [Post 15](../15-human-in-the-loop/index.md): the agent commits to a branch of its own and opens a request, and a person approves the merge. It is a good gate because it is the review interface every engineering organisation already has, and because it is asynchronous, which is what [Post 15](../15-human-in-the-loop/index.md) argues for over a blocking prompt.

### Does this shape actually ship

Two existence proofs, both from model providers describing their own systems. Anthropic's long-running harness splits the driver in two: an **initialiser agent** that runs once to set up the environment, and a **coding agent** that runs in every later session to make incremental progress, each session leaving artefacts for the next (the feature list with its statuses, a rolling `claude-progress.txt`, and descriptive git commits that make rollback possible) (Anthropic, 2025). That is this capstone's driver with the setup step factored out, and the factoring is worth copying, because environment setup is expensive, idempotent, and has nothing to do with the spec.

OpenAI's account is the throughput answer: a five-month internal experiment in which a production beta of roughly a million lines was built with no line written by hand, across about 1,500 merged pull requests (OpenAI, 2026; the same figures reported by InfoQ, 2026). The people involved were not writing code; they were designing the environment that made the code reliable.

The build-versus-rent choice from [Post 23](../23-economics-haas/index.md) §9 applies to all of it: the same architecture can run on your own infrastructure or on a Harness-as-a-Service (HaaS) runtime that returns a whole agent run rather than a completion (Osmani, 2026). What does not change is the shape on the diagram; only where it runs, and who is on call when it stops.

---

## 11. What to ship next

Four seams take the companion from legible to live. The scripted generator becomes a model call, which is the [Build #1](../24-build-minimal-harness/index.md) loop dropped into `generator`. The in-process evaluator runs its tests inside the [Build #2](../25-build-harness-plus/index.md) sandbox, which retires the `exec` of §5. Risky commits route through the approval gate, which is the pull request of §10. And two driver configurations get A/B'd on a real spec set, which is §7's experiment with a model instead of a script. None of those changes the architecture, and the eight offline tests stay green throughout as the contract while the seams are filled in.

### The order to build it in

Reading the capstone as a finished object hides the most useful thing about it, which is that nobody should build it in the order this post presents it. Assembled all at once it is ten moving parts you cannot debug: the eight steps below, with the three guards in step 5 counted one apiece. Built in this order, each step is testable and each earns the next:

1. **The loop, with a hard iteration cap.** Nothing else works until the thing terminates ([Post 03](../03-the-agent-loop/index.md)).
2. **The verification gate.** Until "done" means "verified", every later component is polishing an agent that lies about finishing ([Post 11](../11-verification-loops/index.md)).
3. **The remaining exits: budget and no-progress.** Now the loop stops for a nameable reason every time ([Post 19](../19-loop-engineering/index.md)).
4. **The trace.** Everything after this is much easier to debug; everything before it was small enough not to need it ([Post 21](../21-observability-traces/index.md)).
5. **The guards: hook, sandbox, approval.** In that order, cheapest and most certain first ([Posts 13](../13-hooks-enforcement/index.md) to [15](../15-human-in-the-loop/index.md)).
6. **Durable state and the reset.** Only now is a run worth resuming, which is what makes long-horizon work possible ([Posts 08](../08-state-filesystem-git/index.md), [18](../18-long-horizon-ralph/index.md)).
7. **The ratchet.** It needs failures to learn from, and steps 1 to 6 produce failures legible enough to learn the right lesson from ([Post 10](../10-continual-learning-ratchet/index.md)).
8. **Evaluation and A/B.** Last, because it measures everything above it, and measuring a system with no exits and no traces measures noise ([Post 22](../22-evaluating-harnesses/index.md)).

One rule sits behind the ordering: **each component should be observable before it is relied upon.** That is why the trace comes before the guards and the eval comes last, and it is the difference between a harness you built and a harness you can reason about.

---

## 12. What this build teaches, and what it cannot do

What it teaches is one claim in three currencies. §7 states it in resolved-rate: one knob moved, zero tasks to two, model unchanged. §8 states it in money: the same architecture priced with and without a cached prefix, 1.63 times apart. §3 states it in control flow: a build larger than a context window finishes because state is durable and the window is disposable. None of the three needed a better model, and all three are reproducible offline in under a second.

What it cannot do is a longer list, and a capstone that hides it is a brochure:

- **It ships no guards.** No hook, no sandbox, no approval gate. §5 says where each wires in, and the evaluator's in-process `exec` on model-written source is why the sandbox is first among them.
- **It has no no-progress detector.** Three exits, not four ([Post 19](../19-loop-engineering/index.md) §2): an agent returning the identical wrong file three times burns three attempts and is never told it is thrashing.
- **The workspace is versioned, not git,** and the planner is an identity function. Commits are an abstraction over a dictionary ([Post 17](../17-parallel-agents-shared-repo/index.md)), and `plan()` preserves the spec's order and nothing else (§4).
- **The ratchet never forgets.** Append-only, unpruned, no provenance, injected in full into every later attempt (§6; [Post 10](../10-continual-learning-ratchet/index.md) §9).
- **It is one agent, and that is a small regression.** [Build #2](../25-build-harness-plus/index.md) §6 ships a bounded `delegate` sub-agent and the capstone does not carry it forward, because a Ralph driver already gets its context isolation from the per-task reset. That is a reason and not an excuse. Orchestration proper stays out on the usual grounds ([Post 16](../16-multi-agent-orchestration/index.md) §3).
- **The evaluator is a verifier, not a judge.** Objective ground truth wherever it reaches; the model-as-judge machinery of [Post 12](../12-planner-generator-evaluator/index.md) §6 is what you add when the check needs judgement, and it brings four documented hazards with it, three of them measured biases.
- **Nothing here is multi-tenant.** One spec, one workspace, one budget. Fleets are a control-plane problem ([Post 14](../14-permissions-sandboxes/index.md) §6).

That is the closing claim of *Harness Engineering*. The model is a fixed, powerful component you mostly do not control. Everything you *do* control is the harness, and this capstone is what it looks like when most of the parts are present, each doing its job, and the missing ones are named rather than drawn. Build it once by hand, and you will never again mistake a harness problem for a model problem.

---

## Common pitfalls

- **Building it in the order this post presents it.** Assembled all at once it is ten moving parts you cannot debug; each should be observable before it is relied upon (§11).
- **Reading the hero diagram as an inventory, and trusting the verifier that follows from it.** The figure draws three gates the companion does not ship, and the verifier it does ship execs model-written code in the driver's own process: the shortest path from a legible reference implementation to a live remote-execution hole (§5, §12; Posts 14, 25).
- **An iteration cap mistaken for a no-progress detector.** `max_attempts` bounds work, not thrashing; the same wrong file three times is a stall the companion cannot see (§3; Post 19 §2).
- **Putting volatile state above the spec, or treating the cache discount as a guarantee.** A long-horizon run re-reads its spec on every task, so the growing rules block belongs below it; and the 0.1 times read rate is a ceiling, not a promise, once the write premium and the five-minute expiry are counted (§6, §8; Post 18 §4).
- **Learning that does not persist, or never stops accumulating.** A lesson that dies with the process is not learning, and fifty un-pruned rules injected into every attempt are the clutter the memory file was meant to prevent (§6; Post 10).
- **A test suite that only asks "does this work?"** Structural assertions pass while every value in the trace is wrong, and a boundary tested with expected traffic is tested for correctness rather than safety (§9; Post 25 §10).
- **Comparing harness changes without a cost per completed task, or blaming the model.** Almost any change buys reliability by spending more, so a comparison that ignores the bill prefers the expensive option; and every gain measured here came from the harness with the model held fixed (§7, §8; Posts 04, 22).

---

## Further reading

- **Anthropic.** "Effective harnesses for long-running agents." *Anthropic Engineering*, 26 November 2025. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents — the initialiser-plus-coding-agent split, `feature_list.json`, and the per-session artefacts §10 borrows.
- **OpenAI.** "Harness engineering: leveraging Codex in an agent-first world." *OpenAI blog*, 2026. https://openai.com/index/harness-engineering/ — the five-month, million-line existence proof behind §10's deployment shape.
- **Trivedy, V.** "Improving Deep Agents with harness engineering." *LangChain blog*, 17 February 2026: the harness-only Terminal-Bench result quoted in §7, with the model held fixed.
- **Huntley, G.** "Ralph Wiggum as a 'software engineer'." *Personal blog*, 14 July 2025. https://ghuntley.com/ralph/ — the loop §3 implements.
- **Anthropic.** "Prompt caching" documentation, 2025: the read discount, the write premium and the time-to-live behind §8's table.
- **Trivedy, V.** "The Anatomy of an Agent Harness." *LangChain*, 10 March 2026: the equation this series and this capstone are built on.
- Posts [03](../03-the-agent-loop/index.md), [08](../08-state-filesystem-git/index.md), [10](../10-continual-learning-ratchet/index.md) to [15](../15-human-in-the-loop/index.md), [17](../17-parallel-agents-shared-repo/index.md) to [19](../19-loop-engineering/index.md), and [21](../21-observability-traces/index.md) to [25](../25-build-harness-plus/index.md): the components this capstone assembles, each named at the point it is used.
- The companion code: [`code/26-coding-agent/`](../../code/26-coding-agent/), offline-runnable, 429 lines, eight tests.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 01 — From context to harness](../01-from-context-to-harness/index.md)**: re-read the opening equation now that every term has a component.
- **[Post 02 — The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: the component map this capstone completes, and the entries §5 leaves open.
- **[Post 25 — Build #2](../25-build-harness-plus/index.md)**: the gauntlet this build points at but does not contain; read its §10 before filling the seam.
- **[CHEATSHEET.md](../../CHEATSHEET.md)**: the eleven components, the failure-mode taxonomy and the ratchet principle on one printable page, which is the thing to keep once the series is finished.
- **[GLOSSARY.md](../../GLOSSARY.md)**: every term this series coined or borrowed, in one place.
- **[The series README](../../README.md)**: the full table of contents, and the Context Engineering series it builds on. The sibling series' own capstone, an email reply agent, is the natural pair to this one: the same discipline applied to a context problem rather than a runtime one.
