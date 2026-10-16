# 26 - Capstone: a long-running, trusted coding-agent harness

> **TL;DR.** The capstone assembles the series into one coding agent: a driver that takes a spec of tasks, each with an objective check, runs every task in a fresh context with the planner, generator and evaluator kept apart, turns each failure into a rule, meters its cost against a ceiling and traces every step. The companion [`code/26-coding-agent/`](../../code/26-coding-agent/) does it offline in 429 lines across seven modules with eight tests, and leaves tools, hooks, permissions and orchestration as named seams rather than drawing them as done. Its one experiment holds the scripted model fixed, moves one knob of the harness, and takes the demo spec from no tasks resolved to both, on a set far too small to call.
>
> **Prerequisites:** [post 25](../25-build-harness-plus/index.md), the hardened build; [post 10](../10-continual-learning-ratchet/index.md), the ratchet; [post 12](../12-planner-generator-evaluator/index.md), the three roles; [post 18](../18-long-horizon-ralph/index.md), the loop that outgrows one window.
> **Safe to skip?** Skip it if the reader can already run a spec to completion across fresh contexts with an independent evaluator, a ratchet and a cost ceiling, and can say exactly what such a build leaves unguarded.
>
> **After reading, you will be able to:**
>
> - Run the capstone's driver on a spec across fresh contexts, and say which of the eleven components each module of the companion holds.
> - Follow one failure from the verifier's report to a learned rule and the attempt that passes, and say why a restart forgets a rule the rules file still holds.
> - Map the companion's three stop reasons onto the four exits, and read from its eight tests what each pins and what it leaves unseen.
> - Run a harness A/B with the model held fixed, read it as resolved rate against cost, and say why a two-task set cannot be called.
> - Price a run from the cost meter with and without its cached prefix, and name the cache writes the meter leaves out.
> - Name every seam the capstone leaves open and where each wires into the driver, describe its deployment shape, and order the work to ship next.

![The component map of post 02 with the capstone placed on it. Seven components are held by a companion module: 01 loop and 04 context management and 10 long-horizon patterns by driver.py, 03 state and 06 verification by core.py, 05 memory by memory.py, 11 observability by observe.py, with cost.py named on the loop as its budget exit. Four are dashed seams the companion does not ship: 02 tools, 07 hooks, 08 permissions and 09 orchestration.](diagrams/01-capstone-architecture.svg)

*Seven of the eleven components are code in the capstone; the four drawn dashed are seams, named where they would wire in rather than drawn as done.*

The series began with an equation, `Agent = Model + Harness`, which Trivedy set out in "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026) and [post 01](../01-from-context-to-harness/index.md) opens on. Twenty-five posts later the harness has a name for every part, and this capstone puts the parts together.

---

## 1. The question: what does the whole series look like as one machine?

How do the components of the series assemble into one coding agent that runs across many contexts, verifies itself, learns, meters its cost and records everything? The target is a harness that accepts a **spec** (an ordered list of tasks, each with an objective check) and drives it to completion or stops for a nameable reason. It must outgrow one context window, verify its own work, guard its tools, remember its mistakes, stay inside a budget and leave a trace; each requirement is a component the series has built.

The companion keeps the whole thing offline and deterministic so the *architecture* is legible: a scripted generator stands in for a model, and the eight tests pass with no application programming interface (API) key and no network. The price of legibility is that the guard layer is a named seam rather than code. The figure at the top places the eleven components of [post 02](../02-anatomy-of-a-harness/index.md) and marks which ones the companion holds.

### Where the components physically live

The capstone is five working modules plus a package surface and a demo, and each working module is a post already read:

| Module | What it holds | Component | Posts |
|---|---|---|---|
| `core.py` | the spec, the workspace, the verifier | 03 state, 06 verification | [08](../08-state-filesystem-git/index.md), [11](../11-verification-loops/index.md), [18](../18-long-horizon-ralph/index.md) |
| `driver.py` | `plan()` and `build()`: the per-task reset, the roles, the stop reasons | 01 loop, 04 context management, 10 long-horizon patterns | [03](../03-the-agent-loop/index.md), [12](../12-planner-generator-evaluator/index.md), [18](../18-long-horizon-ralph/index.md), [19](../19-loop-engineering/index.md) |
| `memory.py` | the ratchet: a failure becomes a rule later attempts read | 05 memory | [10](../10-continual-learning-ratchet/index.md), [13](../13-hooks-enforcement/index.md) |
| `observe.py` | nested spans; the whole build as one trace tree | 11 observability | [21](../21-observability-traces/index.md), [22](../22-evaluating-harnesses/index.md) |
| `cost.py` | the meter, the cache discount, the budget ceiling | the budget exit of 01 loop | [05](../05-agent-failure-modes/index.md), [19](../19-loop-engineering/index.md), [23](../23-economics-haas/index.md) |

Four components have no module: 02 tools, because the generator returns a dictionary of files and makes no tool calls; 07 hooks and 08 permissions, because there is then no tool call to stand in front of; and 09 orchestration, because the capstone is one agent.

Two of the rows are not obvious. **[Post 05](../05-agent-failure-modes/index.md) against `cost.py`**: a doom loop is stopped not by a better model but by something outside the loop that counts. The budget ceiling bounds what a doom loop can cost; the fix the series names for it is exit (4), no progress, which this companion lacks (the driver's stop reasons, below, show the gap). **[Post 13](../13-hooks-enforcement/index.md) against `memory.py`**: [post 10](../10-continual-learning-ratchet/index.md) gives the ratchet three teeth, a line in a memory file, a hook that enforces the rule and a reviewer check that catches the regression, and this companion ships only the first. Its absence is the same absence as the missing guards, because a rule that suggests is not a rule that enforces.

The roles of [post 12](../12-planner-generator-evaluator/index.md) live inside `driver.py` rather than in a module of their own, because the separation of planner, generator and evaluator is a property of *how the driver calls them*, not a thing that can be put in a file.

---

## 2. The layout

`snippets/line_count.py` reads the companion without importing it and prints its layout, counting lines as `wc -l` does:

```text
code/26-coding-agent/
  src/coding_agent/
    __init__.py           20   the public surface, re-exported
    __main__.py           52   the offline demo: python -m coding_agent
    core.py               73   Workspace, Task, Spec, VerifyResult, the verifier
    driver.py            135   plan() and build(): the long-horizon loop
    memory.py             36   Ratchet: learn(), as_context()
    observe.py            63   Span, Tracer: nested spans, render()
    cost.py               50   CostMeter: prices, cache discount, ceiling
  tests/
    test_coding_agent.py 104   8 tests
source: 429 lines across 7 modules; tests: 104 lines
imports from outside the standard library: none
```

The last line is checked, not asserted: the snippet parses every import with `ast`. A reader checking whether the series' argument survived contact with code can do so without resolving a dependency tree. The driver is the largest file because it is the only place the components meet, and `__main__.py` is the demo: a two-task spec, a scripted generator, and a printout of the commits, the learned rules, the cost line and the trace tree.

---

## 3. The long-horizon driver

The engine is a Ralph loop: start each iteration from a fresh context against a written spec and do one task (Huntley, "Ralph Wiggum as a 'software engineer'", 14 July 2025), treated at length in [post 18](../18-long-horizon-ralph/index.md). Each task gets plan, generate, evaluate, and on success a commit; on failure, a lesson and a retry. Only two durable stores carry the thread from one task to the next: the workspace, committed task by task, and the ratchet's rules.

In this companion a "context" is concrete: it is the three arguments the driver hands each generator call, the task, the last failure report on that task, and the rendered rules. Nothing else reaches the generator, so every call starts from those three and nothing the previous call saw. The whole loop is one function, short enough to read in full, from `driver.py`:

```python
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
                                           cost, "budget", task.name, tracer.root if tracer else None)

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

Two loops, nested: the outer one walks the spec's tasks, and the inner one is the verify-and-retry loop of [post 11](../11-verification-loops/index.md), bounded by `max_attempts`, the composition [post 19](../19-loop-engineering/index.md) describes. Note `feedback = None` at the top of each task: the failure report crosses attempts of one task and never crosses tasks, while the rules cross both.

`snippets/spec_run.py` runs the demo's spec through `build()` unchanged, with a wrapper that records what each generator call was handed:

```text
Part 1: the demo's spec, one line per generator call
  call 1: task add      handed no report, 0 rule(s); wrote calc.py; verdict fail; commits 0
  call 2: task add      handed last report, 1 rule(s); wrote calc.py; verdict pass; commits 1
  call 3: task is_even  handed no report, 1 rule(s); wrote parity.py; verdict pass; commits 2
rules learned: ['[add] previously failed: add(2, 3) == -1, expected 5']
commits: ['add', 'is_even']; files in the last commit: ['calc.py', 'parity.py']
cost: $0.0193, 6000 in (4500 cached), 900 out, 4.5 s
stop reason: spec_complete -> exit (1), completed
```

![Three generator calls left to right, each a fresh context showing what the driver handed it: call 1 on task add with no report and 0 rules, verdict fail in red; call 2 on add with the last report and 1 rule, verdict pass; call 3 on is_even with no report and 1 rule, verdict pass. Below, the state after each call: the ratchet holds 1 rule after each call, commits rise 0, 1, 2, and the cost meter reads 0.00645, 0.01290 and 0.01935 dollars. Unlike post 18's figure, which plots a Ralph window's tokens, this one shows what each call of the capstone's driver is handed.](diagrams/02-multi-context-run.svg)

*The failure report crosses attempts and stops at the task boundary; the rule, the workspace and the meter cross everything.*

The figure draws that run call by call. In call 3 the report is gone, because it belonged to `add`, but the rule is still there. That is how a build outgrows one window: the spec is the source of truth, the workspace is versioned state ([post 08](../08-state-filesystem-git/index.md)), and the ratchet is the learning that survives a reset.

### What actually stops it

The series argues, from which failures have been named rather than from a measurement, that stop conditions are the loop's main design surface ([post 03](../03-the-agent-loop/index.md)), so a capstone owes the reader an exit list rather than a gesture at one. The companion has three stop reasons, and they map onto the four exits like this:

| Stop reason | What fires it | The exit it maps to |
|---|---|---|
| `spec_complete` | every task's verifier passed | exit (1), `completed`, and the only success; gated by the verifier, never by the generator's word |
| `task_failed` | one task used all `max_attempts` attempts | exit (2), `max_iters`, but per task: there is no run-wide iteration cap |
| `budget` | `cost.over_budget()` at the top of an attempt | exit (3), `budget` |
| none | nothing; not implemented | exit (4), `no_progress`, absent |

The second row hides a scale. The cap counts attempts per task, so a spec of fifty tasks at `max_attempts=3` may run up to $50 \times 3 = 150$ attempts before any exit fires, and only the budget bounds the whole run.

The fourth row is the honest one. `max_attempts=3` is an iteration cap, not a no-progress detector: a generator that returns the identical wrong file three times burns all three attempts, and the harness never notices. The A/B later in this post counts it: with the ratchet off, attempts 2 and 3 on `add` repeat attempt 1 byte for byte, and a check comparing each candidate with the one before would have stopped the run an attempt sooner.

When a task exhausts its attempts, `build()` returns at once with `succeeded=False`: it does not skip the task, escalate it, or carry on. It does return `completed` and `commits` intact, so the verified work is in hand and the run has a resumable position, as [post 19](../19-loop-engineering/index.md) argues every guard exit should. A production driver adds skip-and-continue for tasks nothing depends on and escalate-to-human for the rest ([post 15](../15-human-in-the-loop/index.md)).

---

## 4. Planner, generator, evaluator

Inside each task the roles are separated ([post 12](../12-planner-generator-evaluator/index.md)). A **planner** sequences the work, a **generator** proposes code, and an **independent evaluator** judges it against the task's objective check. The separation is the reliability argument: an agent grading its own output skews positive, so the evaluator is a different component with its own ground truth ([post 11](../11-verification-loops/index.md)). In the capstone the evaluator is the task's verifier, and only a candidate it passes is committed.

The planner is the role to be honest about, because in the companion it does nothing:

```python
def plan(spec: Spec) -> List[Task]:
    """The planner. Here it preserves order; a real planner would decompose and
    sequence. Separated out so the role is explicit (Post 12)."""
    return list(spec.tasks)
```

An identity function is a stand-in, not a planner. It is also the least bad role to leave hollow, because the planner is the one role with no independent check on it ([post 12](../12-planner-generator-evaluator/index.md)): an evaluator catches a bad generation, but only a person reading the spec catches a bad decomposition. A stub that visibly does nothing is easier to notice than a planner that quietly decomposes badly.

The evaluator is the opposite case, and it is where the companion earns its keep. From `core.py`:

```python
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

Count the `VerifyResult(False, ...)` branches: five, each naming a different reason, and the last carrying the actual value beside the expected one. That verbosity is load-bearing. On the demo's first attempt the verifier returns `VerifyResult(False, "add(2, 3) == -1, expected 5")`; that exact string becomes `feedback` on the next attempt, and the ratchet renders it into the rule `[add] previously failed: add(2, 3) == -1, expected 5`. A verifier that returned a bare boolean, or a report reading "test failed", would produce a rule that teaches nothing, and the ratchet would climb on noise. "Success is silent, failures are verbose" ([post 11](../11-verification-loops/index.md)) is usually presented as a courtesy to the generator; here it is the precondition for learning at all.

Note also what the verifier never does: raise. Every exception in the model-written code is caught and turned into a report, because an evaluator that propagates the generator's exception kills the run at the moment it had something useful to say.

---

## 5. The guards, and the seam where they belong

In the target architecture, every tool call the generator makes runs the gauntlet of [post 25](../25-build-harness-plus/index.md): a deterministic **hook** can block it ([post 13](../13-hooks-enforcement/index.md)), a **sandbox** bounds what it can reach ([post 14](../14-permissions-sandboxes/index.md)), and an **approval gate** escalates the irreversible to a person ([post 15](../15-human-in-the-loop/index.md)). A long-running agent is a long-running attack surface, so the guards are what make "leave it running" a defensible sentence.

**The companion ships none of them.** The generator it takes is typed `Callable[[Task, Optional[str], str], dict]`: it returns a dictionary of files and makes no tool calls, so there is nothing for a gauntlet to stand in front of. The gauntlet lives in [`code/25-harness-plus/`](../../code/25-harness-plus/); this build is where it would be wired in, and the wiring points are concrete:

| Gate | Where it wires into `build()` | What it stops | From |
|---|---|---|---|
| pre-tool hook | before `workspace.files.update(files)` | a generated write to a path the run may not touch | [post 13](../13-hooks-enforcement/index.md) |
| sandbox | around `task.verify(workspace)` | the evaluator's own execution of model-written code | [post 14](../14-permissions-sandboxes/index.md) |
| approval gate | before `commits.append(...)` | an irreversible commit nobody looked at | [post 15](../15-human-in-the-loop/index.md) |

The middle row is the alarming one, and it should be said plainly. `python_function_verifier` runs `exec(compile(source, path, "exec"), ns)` on generator-written source, in the driver's own process, with no jail, no timeout and no allow-list. Build #1's verifier does the same, and [post 24](../24-build-minimal-harness/index.md) names it among what that build leaves out. Build #2 does not fix it: its `Sandbox` checks the command strings of a `bash` tool (shell control characters, a first-token allow-list, `..`, absolute paths outside the jail), and the module's own note warns that allow-listing an interpreter allow-lists everything it can run. So the sandbox row is not "wrap the verifier in Build #2's sandbox"; it is "run the verifier out of process, under a timeout, inside one of the isolation tiers of [post 14](../14-permissions-sandboxes/index.md)". The `exec` is safe here only because the generator is a scripted stand-in whose output is a literal in `__main__.py`; swap in a model and it stops being safe in the same instant, which makes it the capstone's most dangerous line and the first seam to fill.

Build #2's own history says this is urgent rather than tidy. Its companion shipped guardrail bugs that a passing suite missed and probing found ([post 25](../25-build-harness-plus/index.md)), among them an allow-list that let `echo hi; curl http://evil.example` through a shell, and a sandbox refusal that landed in the trace tagged `ok`. A gate that cannot be seen to fire cannot be trusted ([post 14](../14-permissions-sandboxes/index.md)), and a gate never written is not improved by a diagram that draws it.

---

## 6. Memory and the ratchet

The capstone's defining feature is that it *improves within a run*. When a task fails, the driver asks the **ratchet** to learn a rule ([post 10](../10-continual-learning-ratchet/index.md)). The rule is appended to a list and injected into the generator's context on every later attempt and every later task. The store and its write path, from `memory.py`:

```python
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
```

The read path is `as_context()`, which renders the list under "Learned rules (do not repeat past mistakes):" for the generator. A mistake becomes a constraint with no model update at all. Three properties matter before it runs past a handful of tasks, and all three say the class is the mechanism, not the discipline.

**There is no "worth remembering" filter.** `build()` ships `learn_after=1`, so a rule is recorded after *every* failed attempt, and the only de-duplication is `learn()`'s exact-string match: two failures whose reports differ by one integer produce two rules. Raising `learn_after` is the crude version of post 10's "earn each line"; the real filter is a person deciding which failures generalise beyond the task that produced them.

**There is no pruning and no size bound.** Every rule ever learned is rendered by `as_context()` into every generator call for the rest of the run. On an illustrative fifty-task build with one failure apiece, that is fifty rules injected into every later attempt, most of them about tasks already committed and verified, which is the memory file turning into the clutter it was meant to prevent ([post 10](../10-continual-learning-ratchet/index.md)). A production ratchet drops a rule when its task is committed, or promotes it into a hook and deletes the line.

**Rules are volatile, and the spec is not.** The rules block grows on every failure, while the spec is byte-identical on every task, so a context that puts the rules above the spec breaks the cached prefix whenever a rule is added. Stable first, volatile last ([post 18](../18-long-horizon-ralph/index.md)). The companion leaves that order to the generator, which receives the rules as a separate argument.

### What the rules file survives

`Ratchet(path=...)` mirrors every rule to a file as it is learned, and it is tempting to read that as learning that survives a restart. It is not, because nothing in the companion reads the file back: a new `Ratchet(path=...)` starts with an empty list and keeps appending. Part 2 of `snippets/spec_run.py` runs the demo three times against one rules file, as three processes would:

```text
Part 2: one rules file, three processes
  first process               rules at start 0; failed attempts 1; lines in the file 1 (1 distinct)
  restart, Ratchet(path=...)  rules at start 0; failed attempts 1; lines in the file 2 (1 distinct)
  restart, rules read back    rules at start 1; failed attempts 0; lines in the file 2 (1 distinct)
```

The restart repeats the mistake the first process already paid for, and appends the same rule a second time, because `learn()` de-duplicates against the list in memory, not against the file. Only a caller that reads the file back into `Ratchet(rules=..., path=...)`, as post 10's snippet does, gets a restart that passes first time; part 2 also de-duplicates, which repairs a file an earlier restart has already doubled. The file is a durable record a later run can reload, not a restore, and the difference is the difference between a run that improves and a fleet that does ([post 08](../08-state-filesystem-git/index.md)).

---

## 7. Observability and harness A/B

The whole run is wrapped in a tracer ([post 21](../21-observability-traces/index.md)), so it renders as one span tree: the build, each task, each attempt, and the generate and evaluate pair inside each attempt. `snippets/spec_run.py` prints the demo's tree unabridged:

```text
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

Twelve lines, and the run's story is in the nesting: `add` took two attempts, `is_even` one, and the run ended on exit (1). A fifty-task build is read the same way, by scanning for `outcome=fail` and descending only there. The trace is also the raw material of evaluation ([post 22](../22-evaluating-harnesses/index.md)): score whole trajectories on a fixed spec set, and A/B two driver configurations with the model held fixed.

### Running the A/B

The companion exposes the knobs an A/B would vary: `max_attempts`, `learn_after`, `rule_from` and `tokens_per_attempt`. `snippets/ab_demo.py` varies one, holds the scripted generator (this build's "model") and the spec fixed, and runs both arms:

```python
    for learn_after in (1, 99):                    # the ratchet on, then off
        cost, seen = CostMeter(budget_usd=1.00), {}
        res = build(mkspec(), watch(generator, seen), workspace=Workspace(), ratchet=Ratchet(),
                    cost=cost, learn_after=learn_after, max_attempts=3)
        repeats = sum(a == b for c in seen.values() for a, b in zip(c, c[1:]))
        results[learn_after] = (res, cost, repeats)
```

`learn_after=99` is the ratchet switched off: no attempt reaches the threshold, so no rule is learned and the generator never sees the lesson. `watch` records each candidate so that repeats can be counted. The snippet prints:

```text
the model is held fixed; only learn_after moves
  learn_after=1 (ratchet on)    resolved 2 of 2; spec_complete; completed ['add', 'is_even']; spend $0.0193; per completed task $0.0097; repeated candidates 0
  learn_after=99 (ratchet off)  resolved 0 of 2; task_failed; completed []; spend $0.0193; per completed task none completed; repeated candidates 2
per task, resolved (on/off): add 1/0, is_even 1/0 (never attempted when off)
discordant pairs 2: 2 for the ratchet, 0 against; sign test p = 0.50: not callable
the fewest discordant pairs, all one way, that reach p < 0.05: 6
```

Both arms spend the same money on the same three attempts. One finishes the spec; the other finishes nothing, because it retries the same wrong file until the per-task cap fires, and it never reaches `is_even` at all. Read in post 22's vocabulary, the paired result is two discordant tasks, both favouring the ratchet, and a two-sided sign test gives $p = 2 \times (1/2)^2 = 0.50$: **not callable**. A two-task set cannot call anything, however large the lift, because even a clean sweep needs six discordant pairs before $2 \times (1/2)^6 = 0.031$ falls under 0.05.

There is a second caveat, and it is the more important one. The scripted generator is built to obey any rule that names its task, so the lift is designed in: the demo shows the mechanism of a harness A/B, one component moved with the model held fixed and judged on resolved rate against cost, not evidence about any model. The evidence at production scale is someone else's. LangChain moved `deepagents-cli` from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points, with the model held fixed at `gpt-5.2-codex`, in leaderboard terms from just outside the top 30 into the top 5 (Trivedy, "Improving Deep Agents with harness engineering", LangChain blog, 17 February 2026). That result is graded firm in this series: one model, one benchmark, a harness change in between.

![A four-stage cycle of cards: the harness run emits a trace; the trace localises a failure to attempt 1 of add, at evaluate, ok=False; an A/B with the model held fixed decides whether a change helps, here 2 of 2 resolved against 0 of 2 at the same 0.0193 dollars, p = 0.50, not callable; the ratchet keeps the fix as a rule in memory and as a task in the fixed set; and the changed harness runs again.](diagrams/03-eval-observability-loop.svg)

*Trace to localise, A/B to decide, ratchet to keep: the model stays fixed and the harness is what changes.*

The figure draws the loop the trace and the A/B form together, and its last arrow is a mechanism. When a trace exposes a failure, the spec that produced it becomes a task in the fixed set, and from then on it guards against the regression's return ([post 22](../22-evaluating-harnesses/index.md), [post 21](../21-observability-traces/index.md)). That is the ratchet applied to the harness rather than to the run: a failure that is only fixed can come back, and one that is also in the set cannot come back quietly.

---

## 8. Cost guardrails

Loops multiply cost, so the driver carries a **cost meter** ([post 23](../23-economics-haas/index.md)) that sums tokens and seconds across every attempt, prices them with a discount for the cached re-read of the stable prefix, and enforces a budget ceiling. The ceiling is both an economic control and a stop condition ([post 19](../19-loop-engineering/index.md)). The meter's defaults are the Claude Sonnet 4.6 rates, $3 per million input tokens and $15 per million output tokens with a cache read at 0.1 times the input rate (Anthropic, "Pricing", consulted October 2026). `snippets/cost_table.py` takes the demo's cost line apart with the companion's own `CostMeter`:

```text
the demo, as the meter prices it: $0.0193 for 6000 in (4500 cached), 900 out
cached share of input: 75%; output: 13% of the tokens, $0.0135 = 70% of the money

run shape (3 attempts)          input : output       75% cached   no cache   penalty
  the demo, generation-heavy     6,000 : 900    ( 6.7 to 1)   $0.0193     $0.0315    1.63x
  a context-heavy task          12,000 : 1,200  (10.0 to 1)   $0.0297     $0.0540    1.82x
  a long-horizon re-read        24,000 : 1,200  (20.0 to 1)   $0.0414     $0.0900    2.17x
```

The token counts are the driver's defaults, `tokens_per_attempt=(2000, 1500, 300)`, not a measured run, and the two larger shapes are illustrative. With that said, three things follow.

**Three quarters of the input is the cached prefix, and caching is worth less than that suggests.** Each task re-reads the spec, which need not cost full price because the spec sits in a byte-stable prefix ([post 18](../18-long-horizon-ralph/index.md); the single-call economics are `ctx-005`). Removing the cache gives $(6{,}000 \times 3 + 900 \times 15) / 10^6 = \$0.0315$ against $0.0193$, a factor of 1.63. The penalty grows with how input-heavy the run is, because caching discounts only the input side.

**Output is 13% of the tokens and 70% of the money.** At $15 against $3 per million, the 900 output tokens cost $0.0135 of the $0.0193. That asymmetry is why "keep generations tight" is a cost control and not a style preference.

**The meter prices reads and never writes.** A cache read is charged at 0.1 times the input rate, but a prefix has to be written before it can be read, at 1.25 times on the five-minute tier and 2 times on the one-hour tier, and an entry not read inside its lifetime expires and is written again (Anthropic, "Prompt caching", consulted October 2026). `cost.py` has no write term at all, so it bills even the first attempt as a cache hit. The same script prices the demo's three attempts with the writes put back:

```text
the write side the meter omits (the demo's attempts, five-minute tier)
  as metered: every attempt reads                           $0.0193  (-39% against no cache, $0.0315)
  one write, then reads within five minutes                 $0.0245  (-22% against no cache, $0.0315)
  a write every attempt, each more than five minutes apart  $0.0349  (+11% against no cache, $0.0315)
```

The last row bites a Ralph driver specifically: an attempt that writes a feature and runs a test suite can take longer than five minutes, and then every attempt pays the write premium for a read that never comes, 11% *more* than not caching at all, the trap [post 18](../18-long-horizon-ralph/index.md) prices on its own grid. The metered figure is the most caching can buy.

**The ceiling is checked at the top of each attempt, before that attempt spends.** No attempt begins once the budget is gone, but nothing is reserved for the attempt about to run: the check is `spent >= ceiling`, so the attempt that crosses the line still completes, and the overshoot is bounded by one attempt, as in [Build #1](../24-build-minimal-harness/index.md). [Post 19](../19-loop-engineering/index.md) has the four-line check that reserves an estimate for the next call and so never crosses; on its illustrative run an arrears check overran a 200,000-token ceiling by about 18%.

The meter is also what makes the A/B quantitative: almost any harness change can buy reliability by spending more, so a comparison without a cost per completed task prefers the expensive option.

---

## 9. The tests

Eight tests in 104 lines, no network and no API key; `uv run --extra dev pytest -q` reports `8 passed` in well under a second, fast enough to run on every edit. The ratchet's test carries the comment "it took a second attempt: the fix used the learned rule", and no assertion checks it. What each of the eight pins down, and what it leaves open:

| Test | What it pins | What it leaves open |
|---|---|---|
| `test_build_completes_a_passing_spec` | one task, one commit, `spec_complete` | failure handling |
| `test_ratchet_learns_from_failure_then_the_fix_lands` | a failure produces a rule, and the run then succeeds | *how many* attempts, so a regression to three would pass |
| `test_unfixable_task_stops_the_build` | exit (2), per task: attempts exhaust, nothing completed | whether the run is resumable |
| `test_budget_ceiling_stops_the_run` | exit (3) fires at a pre-attempt check | the one-attempt overshoot |
| `test_ratchet_is_append_only_and_dedupes` | `learn()` ignores an exact repeat | near-duplicates, and the file across a restart |
| `test_cost_meter_prices_and_discounts_cache` | the pricing arithmetic, cached and fresh separately | the write premium, which the meter omits |
| `test_trace_tree_has_the_expected_shape` | one span of each kind, `stop.reason` on the root | the values inside the tree |
| `test_commits_snapshot_growing_workspace` | state accumulates: commit two carries both files | rollback, because there is none |

### What the suite structurally cannot see

A suite is blind in the shape of the questions it asks ([post 25](../25-build-harness-plus/index.md)), and three blind spots here are structural.

**Every generator in the suite is a pure function of its arguments.** Nothing exercises a generator that calls a tool, writes outside the workspace, or runs for an unbounded time, so the missing gates cost the suite nothing.

**The verifier's `exec` is never given hostile input.** Every source string the tests hand it is a well-formed function written by the test author. A generator that emitted `import os` followed by a system call would have it executed, and all eight tests would still pass. That is the shape of Build #2's allow-list bug: a boundary tested only with the traffic its author anticipated is tested for correctness, not for safety.

**The trace test asserts shape, not content.** `tracer.count("evaluate") == 1` passes whether the span says `ok=True` or `ok=False`. That is the bug post 25 records as the gate that could not be seen to fire, and this suite repeats it.

---

## 10. Deployment shape

In production the harness is a service. What changes is where each durable thing lives, what starts a run, and where a person sits.

| Store | In the companion | In production |
|---|---|---|
| the spec | `Spec`, built in `__main__.py` | a versioned file in the repository, which is what makes it a source of truth rather than a prompt ([post 18](../18-long-horizon-ralph/index.md)) |
| the workspace | `Workspace.files`, a dictionary | a git branch; real worktrees and merges are [post 17](../17-parallel-agents-shared-repo/index.md) |
| the ratchet | `Ratchet()`, in memory | a rules file in the repository, read back at start: reviewable, diffable, prunable ([post 10](../10-continual-learning-ratchet/index.md)) |

The first row carries a design decision worth copying. Anthropic's long-running harness keeps its spec as `feature_list.json`, over 200 features each starting as failing, and prompts the coding agent to edit that file "only by changing the status of a passes field" (Young, "Effective harnesses for long-running agents", Anthropic Engineering, 26 November 2025). Constraining *how* the agent may write to the spec is what stops a struggling agent from lowering the bar ([post 18](../18-long-horizon-ralph/index.md)). The third row is not the one-line change it looks like: a path alone only records, and the read-back at start is the part that carries learning across a restart.

### What starts a run, and where the person sits

A timer that restarts a long-horizon build from zero every hour throws away the resumable position the driver keeps. A trigger that hands the driver a position (the spec, the branch, the rules file, the last stop reason) resumes rather than restarts, which turns a stop into a handoff ([post 19](../19-loop-engineering/index.md)); whether the trigger is a timer or a repository event is a preference. The service surface is small: an endpoint that accepts a spec and returns a run identifier, one that reports status and stop reason, and a stream of spans to an observability backend ([post 21](../21-observability-traces/index.md)).

The approval gate becomes a pull request (PR), the deployment-shaped version of [post 15](../15-human-in-the-loop/index.md): the agent commits to a branch of its own and opens a PR, and a person approves the merge. It is a good gate because it is the review interface engineering teams already use, and because it is asynchronous, which post 15 argues for over a blocking prompt.

### Does this shape actually ship

Two accounts from model providers describing their own systems, both graded reported. Anthropic's long-running harness splits the driver in two: an **initialiser agent** whose first session sets up the environment (an `init.sh` script, a `claude-progress.txt` log and an initial git commit), and a **coding agent** that makes incremental progress in every later session, committing "with descriptive commit messages" so that git can "revert bad code changes and recover working states" (Young, 2025). That is this capstone's driver with the setup step factored out, and the factoring is worth copying, because setup happens once and has nothing to do with any one feature.

OpenAI's account is about throughput: an internal beta of roughly a million lines, none of it written by hand, across roughly 1,500 pull requests opened and merged (Lopopolo, "Harness engineering: leveraging Codex in an agent-first world", OpenAI blog, 11 February 2026; InfoQ, 21 February 2026, reports the same experiment as five months long). Nothing was held fixed in it, so it says that the shape ships, not that the harness beats the model.

The build-against-rent choice of [post 23](../23-economics-haas/index.md) applies to all of it: the same architecture can run on a team's own infrastructure or on a Harness-as-a-Service (HaaS) runtime, Trivedy's name for a harness API that returns a customisable runtime rather than a completion ("The Claude Code SDK and the Birth of HaaS", 23 September 2025). What does not change is the shape on the component map; only where it runs, and who is on call when it stops.

---

## 11. What to ship next

Four seams take the companion from legible to live: the scripted generator becomes a model call (the [Build #1](../24-build-minimal-harness/index.md) loop dropped into `generator`); the evaluator moves out of process, under a timeout, inside an isolation tier; risky commits route through the approval gate, the PR of the deployment shape; and two driver configurations are A/B tested on a spec set large enough to call. None changes the architecture, and the eight offline tests stay green throughout as the contract.

### The order to build it in

Nobody should build the capstone in the order this post presents it. Assembled all at once it is ten moving parts that cannot be debugged together (the eight steps below, with the three guards of step 5 counted one apiece). Built in this order, each step is testable and earns the next:

1. **The loop, with a hard iteration cap.** Nothing else works until the thing terminates ([post 03](../03-the-agent-loop/index.md)).
2. **The verification gate.** Until "done" means "verified", every later component is polishing an agent that misreports finishing ([post 11](../11-verification-loops/index.md)).
3. **The remaining exits: budget and no progress.** Now the loop stops for a nameable reason every time ([post 19](../19-loop-engineering/index.md)).
4. **The trace.** Everything after this is easier to debug; everything before it was small enough not to need it ([post 21](../21-observability-traces/index.md)).
5. **The guards: hook, sandbox, approval.** In that order, cheapest and most certain first ([post 13](../13-hooks-enforcement/index.md), [post 14](../14-permissions-sandboxes/index.md), [post 15](../15-human-in-the-loop/index.md)).
6. **Durable state and the reset.** Only now is a run worth resuming, which is what makes long-horizon work possible ([post 08](../08-state-filesystem-git/index.md), [post 18](../18-long-horizon-ralph/index.md)).
7. **The ratchet, with its file read back.** It needs failures to learn from, and steps 1 to 6 produce failures legible enough to learn the right lesson from ([post 10](../10-continual-learning-ratchet/index.md)).
8. **Evaluation and A/B.** Last, because it measures everything above it, and measuring a system with no exits and no traces measures noise ([post 22](../22-evaluating-harnesses/index.md)).

One rule sits behind the ordering: **each component should be observable before it is relied upon.** That is why the trace comes before the guards and the evaluation comes last, and it is the difference between a harness that was built and a harness that can be reasoned about.

---

## 12. What this build teaches, and what it cannot do

What it teaches is one claim in three currencies. The A/B states it in resolved rate: one knob moved, zero tasks to two, model unchanged, on a set too small to call. The cost table states it in money: the same attempts 1.63 times apart with and without a cached prefix. The driver states it in control flow: a build larger than a window finishes because state is durable and the window is disposable. None needed a better model, and all three reproduce offline in under a second.

What it cannot do is a longer list, and a capstone that hides it is a brochure:

- **It ships no guards.** No hook, no sandbox, no approval gate, and no tools for them to guard; the evaluator's in-process `exec` on model-written source is why the sandbox comes first among them.
- **It has no no-progress detector.** Three stop reasons, not four exits: a generator returning the identical wrong file three times burns three attempts and is never told it is thrashing.
- **The workspace is versioned, not git, and the planner is an identity function.** Commits are snapshots of a dictionary, with no rollback, and `plan()` preserves the spec's order and nothing else.
- **The ratchet never forgets and never reloads.** Append-only, unpruned, without provenance, injected in full into every later attempt, and mirrored to a file that nothing reads back.
- **It is one agent, which is a small regression.** [Build #2](../25-build-harness-plus/index.md) ships a `delegate` sub-agent and the capstone does not carry it forward, because a Ralph driver already gets its context isolation from the per-task reset; carried forward, it would arrive as a tool of the loop dropped into `generator`, where Build #2 registers it. Orchestration proper stays out on the usual grounds ([post 16](../16-multi-agent-orchestration/index.md)).
- **The evaluator is a verifier, not a judge.** Objective ground truth wherever it reaches; the model-as-judge machinery of [post 12](../12-planner-generator-evaluator/index.md) is what gets added when the check needs judgement, and it brings four hazards with it: three biases the paper that named the method examined (position, verbosity, self-enhancement; Zheng et al., NeurIPS 2023, who judged their self-enhancement data too limited to establish it) and rubric drift, which that paper does not measure.
- **Nothing here is multi-tenant.** One spec, one workspace, one budget. Fleets are a control-plane problem ([post 14](../14-permissions-sandboxes/index.md)).

That is the closing claim of the series. The model is a fixed, powerful component that a harness builder mostly does not control; everything that *is* controlled is the harness, and this capstone is what it looks like with most of the parts present and the missing ones named rather than drawn.

---

## 13. Make it run

The companion's eight tests and its demo run from inside `code/26-coding-agent/`:

```bash
uv run --extra dev pytest -q
uv run python -m coding_agent
```

The first reports `8 passed`; the second prints the commits, the learned rule, the cost line and the trace tree. The four snippets run from the series root with the standard library, importing the companion unchanged where they use it:

```bash
uv run python posts/26-capstone-coding-agent/snippets/spec_run.py
uv run python posts/26-capstone-coding-agent/snippets/ab_demo.py
uv run python posts/26-capstone-coding-agent/snippets/cost_table.py
uv run python posts/26-capstone-coding-agent/snippets/line_count.py
```

`spec_run.py` is this post's exercise: the two-task spec run to completion across fresh contexts, then the rules file across three processes. `ab_demo.py` is the A/B with the model held fixed, `cost_table.py` the cost tables, and `line_count.py` the layout; each prints the outputs quoted above in well under a second. To try a variation, change `max_attempts=3` to `max_attempts=1` in `ab_demo.py` and watch the ratchet-on arm fail too, because a rule learned after the only attempt has no attempt left to help; then, in `spec_run.py`, drop the `dict.fromkeys` from the read-back and watch the restart start with two copies of one rule.

---

## 14. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A model wired in before the evaluator moves out of process.** The first candidate that writes `import os` and a system call runs inside the driver, with the driver's permissions, during what the trace calls `evaluate`.
- **A rules file trusted to restore learning.** The service restarts, the agent repeats a mistake fixed last week, and the rules file shows the same line twice.
- **Rules rendered above the spec.** Every failure adds a rule, the cached prefix breaks at the first differing byte, and the bill per attempt climbs while the meter, which only prices reads, keeps reporting the discount.
- **The per-task cap read as a run cap.** A fifty-task spec at `max_attempts=3` may run a hundred and fifty attempts before any exit but the budget fires, and the ceiling was sized for fifty.
- **A two-task A/B shipped as a result.** The lift is 100 points, the sign test says $p = 0.50$, and the change goes out on a difference no set that size could have called.
- **A green suite taken as a safety review.** Eight tests pass while the verifier executes anything handed to it and the trace test would pass with every `ok` it records inverted.

---

## Common pitfalls

1. **Building it in the order this post presents it.** Assembled all at once it is ten moving parts that cannot be debugged; each should be observable before it is relied upon.
2. **Reading the component map as an inventory.** Four components are seams, and the verifier the capstone does ship execs model-written code in the driver's own process: the shortest path from a reference implementation to a remote-execution hole.
3. **An iteration cap mistaken for a no-progress detector.** `max_attempts` bounds work per task, not thrashing; the same wrong file three times is a stall the companion cannot see.
4. **Learning that does not persist, or never stops accumulating.** A rules file nobody reads back is a record, not memory, and fifty unpruned rules in every attempt are the clutter the memory file was meant to prevent.
5. **Treating the cache discount as a guarantee.** The meter bills every attempt as a cache read; the write premium and the five-minute expiry can make a slow driver pay more than no cache at all.
6. **Comparing harness changes without a paired test or a cost per completed task.** A two-task set cannot call a difference, and a comparison that ignores the bill prefers whichever change spends more.

---

## Further reading

- Justin Young, "Effective harnesses for long-running agents" (Anthropic Engineering, 26 November 2025): the initialiser and coding-agent split, `feature_list.json` and its `passes` field, and the per-session artefacts the deployment shape borrows.
- Ryan Lopopolo, "Harness engineering: leveraging Codex in an agent-first world" (OpenAI blog, 11 February 2026), with InfoQ's summary of 21 February 2026: the internal beta of roughly a million lines, reported.
- Vivek Trivedy, "Improving Deep Agents with harness engineering" (LangChain blog, 17 February 2026): the harness-only Terminal-Bench 2.0 result, graded firm.
- Vivek Trivedy, "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026): the equation this series and this capstone are built on.
- Vivek Trivedy, "The Claude Code SDK and the Birth of HaaS (Harness as a Service)" (vtrivedy.com, 23 September 2025): where the name Harness-as-a-Service comes from.
- Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'" (personal blog, 14 July 2025): the plain loop against a spec that the driver hardens.
- Anthropic, "Prompt caching" and "Pricing" (Claude documentation, consulted October 2026): the read discount, the write premium and the cache lifetime behind the cost tables, at the Claude Sonnet 4.6 rates.
- Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023): the judge biases the evaluator seam inherits once a judge replaces the verifier.
- `ctx-005` (`context-engineering`, "The economics of context: pricing, caching, and latency"): prompt caching and the stable prefix at the level of one call.
- The companion code, [`code/26-coding-agent/`](../../code/26-coding-agent/): offline, 429 lines across seven modules, eight tests.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 01 - From context to harness: the third era](../01-from-context-to-harness/index.md):** the opening equation reads differently once every term in it has a module, a test and a seam.
- **[Post 02 - The anatomy of a harness](../02-anatomy-of-a-harness/index.md):** the component map this capstone fills in, now with seven of its eleven boxes in working code and four named as the work still to do.
