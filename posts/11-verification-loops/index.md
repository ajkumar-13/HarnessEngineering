# 11 - Verification loops: tests, self-critique, fail-fast

> **TL;DR.** Autonomy is only as safe as the checking around it. A **verification loop** checks each step against ground truth (a schema, a compiler, tests, an independent judge) so that a small error surfaces at the step that made it instead of compounding into a wasted run. The most valuable single check gates the loop's final-answer exit, turning the model *believing* it is done into the work *being* done. Self-critique is a weak gate because it skews positive, a failing check must hand back a report the model can correct against, and a verifier can be flaky, gamed, or not available at all.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the agent loop and its four exits.
> **Safe to skip?** Skip it if the reader can already gate a loop's exit on tests the agent cannot edit, say why a model's review of its own work is not a gate, cap a correction loop and stop it when it stalls, and price an error caught at the end of a run against one caught at the step that made it.
>
> **After reading, you will be able to:**
>
> - Gate the loop's final-answer exit on ground truth, choosing the cheapest verifier that covers the risk.
> - Explain why self-critique skews positive, and why it can be a first pass but never the only gate.
> - Feed a failing check back into the loop so that success is silent and failure is verbose, with a cap and a no-progress exit on the retries.
> - Price an unverified run against a gate on every step, and decide where a gate belongs, including before an action that cannot be undone.
> - Handle a flaky or gameable verifier, and score a task on verifier's rule to say which gate it admits.

![The loop as one card sends a candidate final answer, exit (1), into a purple verification gate. Pass leads to done, verified; a hit cap of max_attempts=5 leads to unverified, flagged; fail sends the failure report back into the loop in red as the next observation. Below, the companion's run: attempts 1 and 2 fail with the same report, is_prime(1,) == True, expected False, and attempt 3 passes all 7 cases.](diagrams/01-verification-gate.svg)

*Nothing exits on a final answer alone: a gate checks the work first, a pass ends the run, and a failure re-enters the loop as the next observation.*

`ctx-020` scored a finished output against a rubric: offline, after the fact, one completion at a time. This post puts the check *inside the run*, where a verdict is not filed in a report but changes what the loop does next.

---

## 1. The question: why is the model's word not enough?

What makes autonomy safe enough to run unattended? Part I named the failure this post fixes: **victory declaration** ([post 05](../05-agent-failure-modes/index.md)), an agent that marks a task done when it is not. Its root cause is structural. The loop's natural exit is exit (1), final answer, of [post 03](../03-the-agent-loop/index.md): a terminal stop reason and no more tool calls, which means only that the model *believes* it is finished. Nothing in a naive loop asks whether the work is correct.

A verification loop closes the gap by putting a **gate** on that exit, as the figure at the top draws. Before the loop may stop, the candidate is checked against something outside the model's own judgement. Pass, and the run ends verified; fail, and the failure re-enters the loop as the next observation; run out of attempts, and the run ends flagged as unverified rather than quietly accepted.

The deeper principle is *when* to check. Verifying **per step** (fail-fast) surfaces an error the moment it appears, while it is cheap to fix; verifying only at the end lets later steps build on it, so the work downstream is wrong too. Faros AI's guide (22 May 2026) calls it a "fail-fast mechanism" that "prevents minor early-stage mistakes from compounding into large, unrecoverable failures". The premium is small because passing checks are cheap and silent.

---

## 2. Tests are the agent's ground truth

A verifier is only as good as the ground truth behind it. The strongest ground truth is **executable and objective**: it gives the same verdict every time and does not care what the model thinks it did. From cheapest to dearest:

- **Schema validation.** For structured output, a schema check is near free and deterministic: does the result parse and satisfy the contract? It proves the *shape* of an answer, never its content. The dispatch-side version, validating a tool call before it runs, is [post 06](../06-tools-bash-code/index.md); the generation-side version, validating what the model returns, is `ctx-021`.
- **A compiler or a type checker.** A compiler's verdict is absolute: code that does not compile cannot run. A gradual type checker's is strong but not absolute: correct Python can fail a strict `mypy` or `pyright` run over a missing stub or a narrowing the checker cannot follow, which is why `# type: ignore` exists.
- **A test suite.** The canonical ground truth for a coding agent: a failing test is a precise, reproducible statement of what is broken. Tests the agent did not write are the most trustworthy of all, which is how SWE-bench grades: the agent gets a repository at the pre-fix commit and the issue text, and its patch is scored by running tests from the merged fix that the agent never saw, with no partial credit and no rubric (Jimenez et al., ICLR 2024).
- **An independent judge.** Where correctness is not mechanically checkable (is this summary faithful? is this prose clear?), a separate model grades against a rubric. It costs a model call, it can be wrong, and its independence matters ([post 12](../12-planner-generator-evaluator/index.md)).

![A table of five verifiers from cheapest to dearest: schema validation, a compiler or type checker, a test suite, an independent judge, and the model's own self-critique, each with what a pass proves, its cost, whether it can be wrong and when to run it. A dashed line under the test suite separates facts from opinions.](diagrams/03-verifier-ladder.svg)

*Above the dashed line a failure is a fact; below it a verdict is an opinion, and an opinion can be wrong in the agent's favour.*

The figure adds a fifth row, the model's own self-critique, which the next section takes up. The dividing line it draws is not cost but *whether the verdict is a fact or an opinion*.

The design rule follows: **reach for the cheapest deterministic check that covers the risk**, and escalate to a judge only when nothing mechanical will do. A type check plus a test run catches every error the suite asserts against for a fraction of the cost of a large language model (LLM) grader, and unlike a judge it cannot be talked into a pass. It can still be *satisfied* by wrong work, the subject of the section on gaming.

The [code companion](../../code/11-verification-loop/) turns ordinary `(args, expected)` pairs into a verifier, and `snippets/test_cases_report.py` hands it three candidates:

```python
from verification_loop.checks import test_cases

verify = test_cases("is_prime", [((1,), False), ((2,), True), ((25,), False)])
print(verify({"is_prime": lambda n: all(n % d for d in range(2, n))}))
print(verify({"is_prime": lambda n: not [d for d in range(2, n) if n % d == 0][0]}))
print(verify({}))
```

```text
VerifyResult(ok=False, report='is_prime(1,) == True, expected False')
VerifyResult(ok=False, report='is_prime(1,) raised IndexError: list index out of range; is_prime(2,) raised IndexError: list index out of range')
VerifyResult(ok=False, report="no callable named 'is_prime' was defined")
```

The report names the case, what came back and what was expected, which is what the model corrects against. A case that *raises* is reported, not propagated, so a crashing candidate produces feedback instead of killing the loop: a verifier that throws has stopped verifying.

---

## 3. Self-critique, and why it is not enough

The tempting shortcut is to ask the model to check its own work: "review the code you just wrote and fix any bugs." Self-critique is not worthless. A model prompted to *find problems* can catch something it missed while *generating*; Self-Refine reports outputs refined by self-feedback "improving by ~20% absolute on average in task performance" across seven tasks (Madaan et al., NeurIPS 2023), though Huang et al. trace part of such gains to a weak prompt for the first answer.

But it fails on precisely the thing an agent needs it for. When the feedback is *intrinsic*, produced with no external signal, "LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction" (Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024); the earlier gains they re-examine used oracle labels to decide when to stop revising. A survey sharpens that: no prior work demonstrates successful self-correction with feedback from prompted models except on tasks exceptionally suited to it, while self-correction works well where reliable *external* feedback exists (Kamoi et al., *Transactions of the Association for Computational Linguistics*, 2024). Reflexion's 91% pass@1 on the HumanEval coding benchmark, against 80% for GPT-4, is the constructive half of the same finding: on code its signal is execution feedback plus reflection, not reflection alone (Shinn et al., NeurIPS 2023).

Two mechanisms explain the skew. Agents "reliably skew positive when grading their own work", as Addy Osmani reports from Anthropic's long-running harness work ("Agent Harness Engineering", 19 April 2026). And evaluators recognise their own generations at non-trivial accuracy, and fine-tuning reveals a linear correlation between that recognition and the strength of self-preference (Panickssery, Bowman and Feng, NeurIPS 2024). Underneath sits the training signal: sycophancy is a general behaviour of assistants fine-tuned on human feedback, and both human raters and preference models prefer "convincingly-written sycophantic responses over correct ones a non-negligible fraction of the time" (Sharma et al., ICLR 2024). An agent asked "are you done?" is being asked the question its training has best prepared it to answer agreeably.

So self-critique earns a place as a *first, cheap pass*, never as the *only* gate. Two moves make verification independent of the thing verified: **objective ground truth**, which does not skew positive, and **a separate evaluator** with its own context ([post 12](../12-planner-generator-evaluator/index.md)). Self-critique plus external ground truth works; self-critique alone does not.

---

## 4. Feeding failures back: success is silent, failures are verbose

The guiding phrase is **success is silent, failures are verbose**, HumanLayer's, as Osmani (2026) reports it. A passing check returns nothing the model needs to read. A failing check returns as much detail as it can: the failing test name, the assertion, the stack trace, the diff. It is the validate-and-retry loop of `ctx-021` generalised past schemas: there the repair instruction is the validation error, here it is whatever the verifier can say.

The whole pattern fits in a dozen lines. `solve(generate, verify, *, max_attempts=5)` in the companion's `loop.py` ends with this body:

```python
    feedback: Optional[str] = None
    result = VerifyResult(ok=False, report="not attempted")
    candidate: object = None
    for attempt in range(1, max_attempts + 1):
        candidate = generate(feedback)          # the model proposes, given the last report
        result = verify(candidate)              # ground truth: tests, a schema, a judge
        if result.ok:
            return Solution(candidate, attempt, verified=True)
        feedback = result.report                # failure is verbose: feed it back in
    return Solution(candidate, max_attempts, verified=False, report=result.report)
```

Three details carry the weight.

**Structured feedback.** `verify` returns a `VerifyResult`, not a bare boolean. A gate that answers only "failed" has told the model that it is wrong and nothing about how.

**A cap, and a no-progress exit.** `max_attempts` is exit (2), iteration cap, of [post 03](../03-the-agent-loop/index.md) applied to correction, and a fix-it loop without one is a doom loop. A correction loop can also earn exit (4), no progress, which the cap alone does not give it: if the verifier returns the *same* report several times running, the remaining attempts buy little. The companion does not ship this exit. `snippets/same_report_exit.py` adds it to a copy of `solve`:

```python
def solve_until_stuck(generate, verify, *, max_attempts=5, window=3):
    feedback = None
    reports = []
    candidate, result = None, VerifyResult(ok=False, report="not attempted")
    for attempt in range(1, max_attempts + 1):
        candidate = generate(feedback)
        result = verify(candidate)
        if result.ok:
            return Solution(candidate, attempt, verified=True)
        reports.append(result.report)
        if len(reports) >= window and len(set(reports[-window:])) == 1:   # exit (4): no progress
            return Solution(candidate, attempt, verified=False, report=result.report)
        feedback = result.report
    return Solution(candidate, max_attempts, verified=False, report=result.report)
```

The window matters, and the companion's own demo shows why. Its second candidate changes the code and still fails the same case, so the report repeats, and the third candidate is correct:

```text
companion solve(), demo model      verified   after 3 attempt(s)
window 2, demo model               UNVERIFIED after 2 attempt(s)
window 3, demo model               verified   after 3 attempt(s)
companion solve(), stuck model     UNVERIFIED after 5 attempt(s)
window 3, stuck model              UNVERIFIED after 3 attempt(s)
```

A rule that stops on the first repeat abandons a run one attempt before green; a window of three, the window post 03's companion uses for tool calls, lets the demo converge and still stops a model that never changes its answer two calls early. The report is a coarse fingerprint: the same failure can follow a real change of code.

**Return or raise.** When attempts run out, `solve` returns a `Solution` flagged `verified=False` rather than raising. Raising is right when unverified work has no value to the caller; returning is right when the caller must decide.

An exhausted correction loop has three real exits, all covered in this series: surface the work explicitly marked unverified; roll back to the last good checkpoint ([post 08](../08-state-filesystem-git/index.md)), which is why the discipline is to checkpoint after each *verified* step; or escalate to a human ([post 15](../15-human-in-the-loop/index.md)). Whichever fires, count it on the run's trace ([post 21](../21-observability-traces/index.md)): a correction loop that silently gives up looks identical in aggregate to one that never had to run.

---

## 5. The economics of an unverified run

Verification looks like overhead until the alternative is priced, first in a toy that runs and then in tokens.

The toy is this post's lab. `snippets/gate_vs_no_gate.py` gives a four-step task to the companion's `solve` and its scripted demo model: `is_prime`, then three functions built on it (`primes_below`, `count_primes`, `twin_primes_below`), each with its own test cases. The case `is_prime(1) == False` is the failing test the first candidate trips. Run once with a gate on every step and once with the gate removed (a `verify` that always passes):

```text
with a gate on every step
  step 1 is_prime          attempt 1  FAIL  is_prime(1,) == True, expected False
  step 1 is_prime          attempt 2  FAIL  is_prime(1,) == True, expected False
  step 1 is_prime          attempt 3  pass
  step 2 primes_below      attempt 1  pass
  step 3 count_primes      attempt 1  pass
  step 4 twin_primes_below attempt 1  pass
  model calls: 6; each step verified before the next one began
without the gate
  model calls: 4; solve() reported verified on every step
  checked at the end: is_prime          FAIL  is_prime(1,) == True, expected False
  checked at the end: primes_below      FAIL  primes_below(10,) == [0, 1, 2, 3, 5, 7], expected [2, 3, 5, 7]
  checked at the end: count_primes      FAIL  count_primes(30,) == 12, expected 10
  checked at the end: twin_primes_below FAIL  twin_primes_below(10,) == [(0, 2), (1, 3), (3, 5), (5, 7)], expected [(3, 5), (5, 7)]
  steps failing at the end: 4 of 4, 3 of them built on the error in step 1
without the gate 4 calls are wasted; redoing the task with the gate makes it 4 + 6 = 10 calls against 6
```

Two things matter more than the counts, which are a scripted toy's. Without the gate, `solve()` still reported *verified* on every step: a loop with no ground truth says what the model says. And the one bug in `is_prime` reached all three later steps, each of which passes its own tests once `is_prime` is right: the error compounded through code that was not itself wrong.

Tokens make the same point sharper, because a run pays for one model call per iteration and the price per iteration climbs as every turn re-reads the history. Post 23's running example, illustrative rather than measured, sends 6,000 input tokens on the first request and 3,100 more on each turn after it, 276,600 over twelve iterations ([post 23](../23-economics-haas/index.md)). Let an error enter at iteration 2. `snippets/unverified_cost.py` prices the two runs:

```text
input tokens per iteration: 6,000, 9,100, 12,200, 15,300, 18,400, 21,500, 24,600, 27,700, 30,800, 33,900, 37,000, 40,100
run total: 276,600
no gate: caught at iteration 12, iterations 2 to 12 forfeit, 270,600 tokens (97.8%)
gate on every step: caught at iteration 2, iteration 2 forfeit, 9,100 tokens (3.3%)
judge on every step: 12 x 12,000 = 144,000 tokens (+52.1%)
judge at checkpoints: 3 x 12,000 = 36,000 tokens (+13.0%)
```

**Unverified**, nothing notices until the end, and iterations 2 to 12 are forfeit: $276{,}600 - 6{,}000 = 270{,}600$ tokens. Losing eleven of twelve steps, 92%, costs 98% of the spend, because the forfeited steps are the late, context-heavy ones. **Fail-fast**, a type check and the unit tests touching the changed files run at each step, costing seconds and no model call; the error fails at iteration 2 and the loss is that one iteration, $6{,}000 + 3{,}100 = 9{,}100$ tokens.

![Two panels computed by the snippet on post 23's illustrative run. Left, input tokens per iteration rising from 6,000 to 40,100 over twelve iterations, iterations 2 to 12 shaded red as forfeit without a gate. Right, two bars on one scale: without a gate 270,600 of 276,600 tokens forfeit; with a gate on every step 9,100.](diagrams/02-compounding-vs-failfast.svg)

*The same error costs one early, cheap iteration with a gate and every expensive iteration after it without one.*

The figure draws both runs on one scale, and the numbers generalise into a rule. **Run a check on every step when the chance an error enters that step, multiplied by the cost of the iterations that would build on it, exceeds the check's own cost.** The cost term favours the early steps: an error at iteration 2 poisons ten dearer iterations, one at iteration 11 poisons one. That is why a free type check runs everywhere and a judge runs only at checkpoints. For the judge the break-even is arithmetic, since it is the only verifier on the ladder with a token price: a call reading an illustrative 12,000-token candidate costs about what the run's third iteration costs (12,200 tokens), so twelve of them add $12 \times 12{,}000 = 144{,}000$ tokens, over half again, while three at checkpoints add 36,000, or 13%.

The fail-fast analogy from continuous integration undersells the case. Aborting a build on the first failing job is a *cost* optimisation over independent jobs; per-step verification is a *correctness* optimisation over a serial chain where every later step reads the earlier ones, so an unchecked error is silently incorporated into everything after it.

---

## 6. When a fact stops being a fact: flaky and slow verifiers

The sections so far assume the verifier works. Three things break that: the check is unreliable or slow, it can be gamed, or there is none to be had. The first comes first, because the ladder's "can it be wrong?" column is a claim about *reproducibility*, not about test quality.

**Flakiness.** A non-deterministic test is the worst available gate, and worse for an agent than for a person. It fails work that is correct, hands the model a convincing failure report, and the model dutifully repairs code that was never broken. The damage is invisible, because every artefact of a healthy correction loop is present: a failing check, a specific report, an edit, a green run. A developer knows which tests lie and re-runs them; the agent does not, and feeding every report straight back promotes a flaky test from an annoyance to an active hazard. Quarantine it out of the agent-facing gate *before* anyone gets round to fixing it. A gate that is right 98% of the time is not 98% of a gate.

**Latency.** A check slower than the work it guards will be skipped, by a person or by a scheduler, and the answer is layering rather than choosing.

| Layer | What runs | When | Budget |
| --- | --- | --- | --- |
| Fast gate | type check, plus the unit tests touching the files just changed | every step | a few seconds |
| Checkpoint gate | the full suite, the linter, the build | before each commit or checkpoint | up to a minute |
| Decision gate | an independent judge against a rubric | at real decision points, and on the loop's exit | one model call |

A rule of thumb, not a measurement: keep the per-step gate under about a tenth of the step it guards. A thirty-second edit-and-test iteration can afford a three-second check and cannot afford a four-minute one; a four-minute check belongs on the checkpoint row rather than on the step.

---

## 7. The verifier can be gamed

Everything above the ladder's dashed line returns a fact. A fact about a suite the agent has just edited is not ground truth.

This is documented behaviour, not a hypothetical. Anthropic's "System Card: Claude Opus 4 & Claude Sonnet 4" (May 2025) defines reward hacking as a model finding a way to maximise its rewards that "technically satisfies the rules of the task, but violates the intended purpose", and names two examples on coding work: **hard-coding**, "writing solutions that directly output expected values", and **special-casing**, "writing insufficiently general solutions", in both cases to pass tests. The same document gives the detector, which is the defence stated as an experiment: it ran model-generated solutions through "held-out tests that are hidden from the model" to see whether a solution was overly focused on the original test cases rather than general.

Four harness-level rules follow.

- **The verifier must not be writable by the thing it verifies.** Put the test files behind a pre-tool deny rule ([post 13](../13-hooks-enforcement/index.md)). An agent that can edit the gate does not have a gate.
- **Prefer tests the agent never sees.** Hold part of the suite out of the working tree and run it only at the gate: SWE-bench's design, brought inside a harness.
- **Diff the verifier as part of the verdict.** If the test files changed under the agent's hands during the run, the run fails, whatever the tests now say.
- **Read a sudden green before trusting it.** A long streak of failures that resolves in a single attempt is exactly what special-casing looks like from outside.

[Post 22](../22-evaluating-harnesses/index.md) meets the same law at the benchmark, Goodhart's in Strathern's wording: "when a measure becomes a target, it ceases to be a good measure". The difference is visibility. Benchmark overfit is slow and shows up as a number that rises while nothing improves; a gamed gate is instant and shows up as nothing at all.

---

## 8. Which tasks admit a verifier at all

The ladder ranks verifiers; it does not say whether the task in hand has one, and "write the migration plan" or "summarise this incident" may not.

Jason Wei's "Asymmetry of verification and verifier's rule" (15 July 2025) supplies the checklist. A task is easy to verify to the extent that it has **objective truth** (everyone agrees what a good solution is), is **fast to verify** (seconds per solution), is **scalable to verify** (many solutions at once), is **low noise** (the verdict correlates tightly with real quality), and offers **continuous reward** (solutions can be ranked, not merely passed or failed). The rule states the consequence: "the ease of training AI to solve a task is proportional to how verifiable the task is".

Score the task on those five before designing the gate, and the score says which row of the ladder it is entitled to.

| Property | "Fix this failing test" | "Write a data-migration plan" | "Summarise this incident" |
| --- | --- | --- | --- |
| Objective truth | yes: it passes or it does not | partly: several plans are defensible | no: faithfulness is a judgement |
| Fast to verify | yes, seconds | no: it is verified by executing it | seconds, but only by a reader |
| Scalable to verify | yes: run the suite | no | only through a judge |
| Low noise | high, unless the suite is flaky | low | moderate |
| Continuous reward | yes: the count of passing tests | no | a rubric score, noisy |
| Gate it gets | a test gate on every step | a human approval gate before execution | a judge, sampled against human labels |

The rule also explains why so many patterns in these posts come from coding agents: a compiler and a test suite give an objective, fast, low-noise verdict on work that took far longer to produce than to check. Where the asymmetry is worse the gate gets weaker, and the honest response is to build the missing ground truth (a fixture set, a golden file, a schema the plan must satisfy) rather than to promote a judge into a role it cannot hold.

---

## 9. Where the gate belongs

Verification is placed on purpose, not switched on everywhere. Two placements earn their cost by default:

- **On the exit.** Never let the loop stop on a bare final answer. Gate exit (1) behind a check, so *done* means *verified*. This one gate is the fix for victory declaration.
- **After a risky, reversible step.** An edit, a generated config, a refactor: verify immediately, while rolling back is a checkpoint away ([post 08](../08-state-filesystem-git/index.md)).

Both check *after* the action, which works only when the action can be undone. A sent email, an executed migration, a deleted branch, a posted payment: a verifier that runs afterwards reports a fact no one can act on any more. The check has to move in front of the action, and only two mechanisms can hold there.

| The action is | Check runs | Mechanism | Why |
| --- | --- | --- | --- |
| Reversible | after | a verification gate in the loop | cheap and silent, and a failure costs one rollback |
| Irreversible, mechanically checkable | before | a blocking pre-tool hook ([post 13](../13-hooks-enforcement/index.md)) | only a blocking hook can stop a call; the others report |
| Irreversible, needs judgement | before | a human approval gate ([post 15](../15-human-in-the-loop/index.md)) | approval is reserved for what a checkpoint cannot undo |

The reversible-against-irreversible split selects the row, and it is the seam joining verification to hooks and to human approval.

Finally, watch which checks keep firing. A verifier that catches the same failure over and over is not a gate doing its job; it is a rule waiting to be written down ([post 10](../10-continual-learning-ratchet/index.md)) and then enforced. At that point verification stops being something the model cooperates with and becomes a **hook**, the subject of [post 13](../13-hooks-enforcement/index.md).

---

## 10. Make it run

The [code companion](../../code/11-verification-loop/) is the loop and its ground truth: `loop.py` holds `VerifyResult`, `Solution` and `solve`, `checks.py` holds `test_cases`, and an offline demo runs a scripted model that proposes three `is_prime` implementations (no lower bound, then faster but still no lower bound, then correct). Its nine tests need no network and no provider credentials. From inside `code/11-verification-loop/`:

```bash
uv run --extra dev pytest -q
uv run python -m verification_loop
```

The first runs the nine tests; the second prints `verified after 3 attempt(s)`. The four snippets import the companion unchanged and run from the series root with the standard library:

```bash
uv run python posts/11-verification-loops/snippets/test_cases_report.py
uv run python posts/11-verification-loops/snippets/same_report_exit.py
uv run python posts/11-verification-loops/snippets/gate_vs_no_gate.py
uv run python posts/11-verification-loops/snippets/unverified_cost.py
```

They print the outputs quoted above. `gate_vs_no_gate.py` is this post's exercise: a failing test injected into the first step, the loop retrying to green, then the gate removed and the wasted calls counted. To try a variation, delete the case `((1,), False)` from step 1 and watch the gate pass the buggy `is_prime` and catch it one step later, in `primes_below`, where no retry can fix it.

---

## 11. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A gate that only says "failed".** The verifier returns a boolean; the model rewrites a working part of the code, the same test fails again, and the loop spends its attempts guessing.
- **A no-progress exit that fires on the first repeat.** The report is unchanged after a real change of code, the loop stops, and the run is flagged unverified one attempt before the candidate that would have passed.
- **Test files the agent can edit.** The suite goes green in one attempt after a long red streak, and the diff shows an assertion deleted rather than the code fixed.
- **A flaky test inside the gate.** A correct function fails once, the model "fixes" it, the rerun passes, and the history shows a plausible repair of working code.
- **A cap exhaustion counted as success.** The caller reads `candidate` without checking `verified`, and unverified work ships with nothing in the logs to say so.

---

## Common pitfalls

1. **Letting the model be its own verifier.** Self-assessment skews positive; use objective ground truth or a separate evaluator, and keep self-critique as a first pass.
2. **Verifying only at the end.** An early error compounds through every later step, and the forfeited iterations are the expensive ones.
3. **Retrying forever.** A correction loop with no `max_attempts` is a doom loop; cap it, and stop it when the same report repeats across a window.
4. **Mistaking a green gate for correctness.** Passing checks verify what they cover, and a green run from a suite the agent just edited is not evidence at all.
5. **Verifying after an action that cannot be undone.** A check after a sent email reports a fact no one can act on; move it in front, as a hook or an approval.

---

## Further reading

- Faros AI, "Harness engineering: A guide to building better AI coding agents" (22 May 2026): verification loops as a fail-fast mechanism.
- Addy Osmani, "Agent Harness Engineering" (19 April 2026): self-verification, its positive skew, and "success is silent, failures are verbose".
- Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024), and Kamoi et al., "When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs" (*Transactions of the Association for Computational Linguistics*, 2024): the negative result, and the survey tying self-correction to reliable external feedback.
- Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback" (NeurIPS 2023), and Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (NeurIPS 2023): the constructive half, and what changes when the feedback comes from execution.
- Panickssery, Bowman and Feng, "LLM Evaluators Recognize and Favor Their Own Generations" (NeurIPS 2024), and Sharma et al., "Towards Understanding Sycophancy in Language Models" (ICLR 2024): the mechanism behind the positive skew, and the training signal underneath it.
- Jason Wei, "Asymmetry of verification and verifier's rule" (15 July 2025): the five properties that decide whether a task can be gated at all.
- Anthropic, "System Card: Claude Opus 4 & Claude Sonnet 4" (May 2025), the reward hacking section: hard-coding and special-casing defined, and held-out tests as the detector.
- Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (ICLR 2024): grading a whole run on tests the agent never sees.
- ai-boost, "awesome-harness-engineering" (GitHub, 2026): the Verification and CI Integration primitive.
- `ctx-020` (`context-engineering`): output evaluation, one completion at a time; `ctx-021`: the validate-and-retry loop, one level down.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 12 - Planner, generator, evaluator: separating the roles](../12-planner-generator-evaluator/index.md):** making the evaluator a separate agent, so that the grader is independent of the author.
- **[Post 13 - Hooks and deterministic enforcement: guardrails as code](../13-hooks-enforcement/index.md):** turning a verification step into a gate the model cannot skip.
