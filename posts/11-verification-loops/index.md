# 11 · Verification loops — tests, self-critique, fail-fast

> **TL;DR.** Autonomy is only as safe as the checking around it. A **verification loop** checks each step against ground truth (tests, a schema, an independent judge) so a small error surfaces immediately instead of compounding into a wasted run. The single most valuable check gates the loop's "final answer" exit, converting the model *believing* it is done into the work *being* done. This post covers why per-step verification beats verifying at the end, why self-critique is a weak gate, what a failing check should hand back, and what to do when the verifier is flaky, gamed, or not available at all.
>
> **After reading this you will be able to:**
> - Place a verification gate on the loop's exit so an agent cannot declare victory unchecked.
> - Choose ground truth for a task (tests, types, schema, or an independent judge) and layer checks cheap-to-expensive.
> - Feed a failure back into the loop as verbose, actionable feedback and retry to green.
> - Price a gate against the run it protects, and decide whether it earns a place on every step.

![The agent loop feeding a candidate final answer into a verification gate; on pass the run is done, on a hit cap it ends flagged unverified, and on fail the failure report is injected back into the loop, with a real three-attempt run of the code companion and the three exits an exhausted loop has beneath it.](diagrams/01-verification-gate.svg)
*Nothing exits on "final answer" alone. A gate checks the work first; a pass ends the run, a failure re-enters the loop.*

Context Engineering, Post 20 scored a finished output against a rubric: offline, after the fact, one completion at a time. This post puts the check *inside the run*, where a verdict is not filed in a report but changes what the loop does next.

---

## 1. Fail-fast beats fail-at-the-end

Part I named the failure this post fixes: **victory declaration** ([Post 05](../05-agent-failure-modes/index.md) §2.1), an agent that marks a task done when it is not. Its root cause is structural. The loop's natural exit is stop ① from [Post 03](../03-the-agent-loop/index.md), a final answer with no more tool calls, and that exit only means the model *believes* it is finished. Nothing in a naive loop asks whether the work is actually correct.

A verification loop closes the gap by putting a **gate** on that exit. Before the loop is allowed to stop, the candidate is checked against something outside the model's own judgement. The gate has two outcomes: pass, and the run ends verified; fail, and the failure re-enters the loop as the next observation.

The deeper principle is *when* you check. Verifying **per step** (fail-fast) surfaces an error the moment it appears, while it is cheap to fix. Verifying only at the end lets an early mistake sit undetected while later steps build on it, so by the time anything notices, the work downstream is wrong too and the whole run is wasted (Faros AI, 2026). Fail-fast is not a tax on a working agent; it is insurance against a broken one, and the premium is small because *passing checks are cheap and silent* (§4).

---

## 2. Tests are the agent's ground truth

A verifier is only as good as the ground truth behind it. The strongest ground truth is **executable and objective**: it gives the same verdict every time and does not care what the model thinks it did.

In rough order of strength, and not of cost:

- **A compiler or a type checker.** A compiler's verdict is absolute: code that does not compile cannot run. A gradual type checker's is strong but not absolute, because correct Python routinely fails a strict `mypy` or `pyright` run over a missing stub or a narrowing the checker cannot follow, which is why `# type: ignore` exists. Treat a typecheck failure as a defect until shown otherwise rather than as proof of one.
- **A test suite.** The canonical ground truth for a coding agent: a failing test is a precise, reproducible statement of what is broken. Tests the agent did not write are the most trustworthy of all, which is how SWE-bench grades. The agent gets a repository at the pre-fix commit and the issue text, and the patch is scored by running the *hidden* tests the merged fix originally had to pass, with no partial credit and no rubric (Jimenez et al., 2023). Copy the design: keep part of the suite the agent's tools cannot read or edit, and gate on that part (§7).
- **Schema validation.** For structured output, a schema check is cheap and deterministic: does the result parse and satisfy the contract? The dispatch-side version, validating a tool call before it runs, is [Post 06](../06-tools-bash-code/index.md) §7; the generation-side version, validating what the model returns, is Context Engineering, Post 21.
- **An independent judge.** Where correctness is not mechanically checkable (is this summary faithful? is this prose clear?), a separate model grades against a rubric. The weakest and most expensive option, and its independence matters (§3, and [Post 12](../12-planner-generator-evaluator/index.md)).

Cost runs on its own axis. Schema validation is the cheapest verifier on the list and sits third only because it covers less: it proves the shape of an answer, never its content. That is why the figure gives cost its own column, and why §6's layering rule is expressed in seconds rather than in rank.

![Five verifiers as rows — compiler or type checker, test suite, schema validation, then below a dashed line an independent judge and the model's own self-critique — each with its cost, whether it can be wrong, and how often to run it.](diagrams/03-verifier-ladder.svg)
*The dashed line is the one that matters: above it a failure is a fact, below it a verdict is an opinion that can be wrong in the agent's favour.*

The figure carries a fifth row the list does not: the model's own self-critique, which §3 takes up. Drawn as a table, the ladder shows what the list obscures. The dividing line is not strength, it is *whether the verifier can be wrong*. Above it a verdict is a fact; below it a verdict is an opinion, and an opinion can fail in the direction the agent would prefer. That is why self-critique sits beside the judge rather than at the bottom of one continuous scale.

The design rule follows: **reach for the cheapest deterministic check that covers the risk**, and escalate to a judge only when nothing mechanical will do. A typecheck plus a test run catches most coding errors for a fraction of the cost of a large language model (LLM) grader, and unlike a judge it cannot be talked into a pass. It can still be *satisfied* by wrong work, which is §7.

Building that ground truth rarely needs a framework. The runnable companion in [`code/11-verification-loop/`](../../code/11-verification-loop/) turns ordinary `(args, expected)` pairs into a verifier:

```python
from verification_loop.checks import test_cases

verify = test_cases("is_prime", [((1,), False), ((2,), True), ((25,), False)])
verify({"is_prime": lambda n: all(n % d for d in range(2, n))})
# VerifyResult(ok=False, report='is_prime(1,) == True, expected False')
```

The report is the point: it names the case, what came back, and what was expected, which is what the model corrects against (§4). A case that *raises* is reported in the same format rather than propagated, so a crashing candidate produces feedback instead of killing the loop. A verifier that throws has stopped verifying.

---

## 3. Self-critique, and why it is not enough

The tempting shortcut is to ask the model to check its own work: "review the code you just wrote and fix any bugs." Self-critique is not worthless. A model prompted to *find problems* often catches something it missed while *generating*, because the two framings surface different things; Self-Refine reports roughly a 20% average absolute improvement across its task set from that move alone (Madaan et al., 2023).

But it fails on precisely the thing an agent needs it for. When the feedback is *intrinsic*, produced with no external signal, reasoning performance does not improve and sometimes degrades, and earlier positive results turn out to have leaned on oracle labels that told the loop when to stop revising (Huang et al., 2024). A survey of the literature sharpens that: no prior work demonstrates successful self-correction from prompted-model feedback except on tasks exceptionally suited to it, while self-correction does work where reliable *external* feedback exists (Kamoi et al., 2024). Reflexion's 91% pass@1 on the HumanEval coding benchmark, against a GPT-4 baseline of 80%, is the constructive half of the same finding: its signal is execution feedback plus reflection, not reflection alone (Shinn et al., 2023).

Two mechanisms explain the skew. A model grading its own output skews positive (Osmani, 2026), and evaluators recognise their own generations at non-trivial accuracy, with the strength of self-preference correlating linearly with that recognition (Panickssery et al., 2024). Underneath sits the training signal: sycophancy is a general behaviour of assistants fine-tuned on human feedback, and both human raters and preference models prefer a convincingly-written response over a correct one a non-negligible fraction of the time (Sharma et al., 2023). An agent asked "are you done?" is being asked the question its training has best prepared it to answer agreeably.

So self-critique earns a place as a *first, cheap pass*, never as the *only* gate. Two moves make verification independent of the thing verified: **objective ground truth** (§2), which does not skew positive, and **a separate evaluator** with its own context, which is the subject of [Post 12](../12-planner-generator-evaluator/index.md). The literature draws the same line this post draws. Self-critique plus external ground truth works; self-critique alone does not.

---

## 4. Feeding failures back: success is silent, failures are verbose

A gate is only half of a loop. The other half is what happens on failure: the verifier's report becomes the next input to the model, which tries again with the specific error in hand.

The guiding phrase is **success is silent, failures are verbose** (Osmani, 2026). A passing check returns nothing the model needs to read. A failing check returns as much detail as it can: the failing test name, the assertion, the stack trace, the diff. That verbosity is the feedback the model corrects against. It is the validate-and-retry loop of Context Engineering, Post 21 §4 generalised past schemas: there the repair instruction is the validation error, here it is whatever the verifier can say.

The whole pattern is a dozen lines, and `loop.py` in the companion is the shape:

```python
# code/11-verification-loop/src/verification_loop/loop.py (hints and docstrings trimmed)
def solve(generate, verify, *, max_attempts=5):
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    feedback = None
    result = VerifyResult(ok=False, report="not attempted")
    candidate = None
    for attempt in range(1, max_attempts + 1):
        candidate = generate(feedback)     # the model proposes, given the last report
        result = verify(candidate)         # ground truth: tests, a schema, a judge
        if result.ok:
            return Solution(candidate, attempt, verified=True)
        feedback = result.report           # failure is verbose: feed it back in
    return Solution(candidate, max_attempts, verified=False, report=result.report)
```

Three details carry the weight.

**Structured feedback.** `verify` returns a `VerifyResult`, not a bare boolean. A gate that answers only "failed" has told the model that it is wrong and nothing about how.

**A cap, and a no-progress exit.** `max_attempts` is the hard iteration cap (② from [Post 03](../03-the-agent-loop/index.md)) applied to correction, and a fix-it loop without one is a doom loop. A correction loop can also earn a genuine no-progress exit (④), which the cap alone does not give it: if the verifier returns the *same* report twice running, the loop is not converging and the remaining attempts buy nothing. That is "unchanged observations across the last N turns" inside a correction loop, and it is two lines:

```python
# Not shipped in the companion: exit 4 for a correction loop.
# Inside solve's for-body, immediately after `result = verify(candidate)`:
if not result.ok and result.report == feedback:      # the same failure twice running
    return Solution(candidate, attempt, verified=False, report=result.report)
```

**Return or raise.** `solve` returns rather than raises when attempts run out, which answers the question every reader has next: the verifier still fails after five attempts, now what? Raising is right when unverified work has no value to the caller; returning a `Solution` flagged `verified=False`, which is what the companion does, is right when the caller must decide.

An exhausted correction loop has three real exits, and this series owns all three: surface the work explicitly marked unverified; roll back to the last good checkpoint ([Post 08](../08-state-filesystem-git/index.md) §4), which is why the discipline is to checkpoint after each *verified* step; or escalate to a human ([Post 15](../15-human-in-the-loop/index.md)). Whichever fires, count it. Cap exhaustions are a tracked error, not a quiet fallback: a correction loop that silently gives up looks identical in aggregate to one that never had to run ([Post 21](../21-observability-traces/index.md)).

The companion's demo runs the whole thing offline: `solve` is handed a mock model proposing three `is_prime` implementations (no lower bound, then faster but still no lower bound, then correct) and returns `verified=True` on the third attempt. A nine-test suite covers the loop, the verifier and that convergence, with no network access and no provider credentials.

---

## 5. The economics of an unverified run

Verification looks like overhead until you price the alternative. The series already owns the cost model: a run pays for one model call per iteration, and the per-iteration price climbs because every turn re-reads the accumulated history, so iteration one might send 6,000 tokens where iteration twelve sends 40,000 ([Post 23](../23-economics-haas/index.md) §1).

Take a twelve-iteration run on those numbers, the context growing by about 3,100 tokens a turn, so the run reads roughly 276,000 input tokens. An error enters at iteration two.

**Unverified**, nothing notices until the end. Iterations 3 to 12 are built on the mistake, so ten of twelve steps are forfeit, and the forfeited ones are the late, context-heavy ones: about 261,000 of the 276,000 tokens. Losing 83% of the steps costs 95% of the spend.

**Fail-fast**, a typecheck and the unit tests touching the changed files run at each step, costing seconds and no model call. The error fails at iteration two, and the loss is one iteration at the run's cheapest point: about 9,100 tokens, or 3%.

| | No gate | A gate on every step |
| --- | --- | --- |
| Where the error is caught | iteration 12 | iteration 2 |
| Iterations built on the error | 10 | 0 |
| Input tokens forfeited | ~261,000 (95% of the run) | ~9,100 (3%) |
| What the checking itself costs | nothing | 12 typecheck-and-test runs, no model calls |
| What you hold at the end | a wrong result, and no signal it is wrong | a corrected result, one iteration late |

![Two panels: without per-step checks a bug at step two compounds through the run and is caught only at the end, leaving the work wrong and unseen; with fail-fast verification the bug fails its check at step two and is fixed, and the rest of the run passes verified. A ledger beneath prices the same argument on the series' twelve-iteration running example, comparing tokens forfeited with and without a gate.](diagrams/02-compounding-vs-failfast.svg)
*Five steps, run without and with a per-step check: verification converts a compounding failure into a one-step correction.*

The numbers generalise into a rule. **Run a check on every step when the chance an error enters that step, multiplied by the cost of the iterations that would build on it, exceeds the check's own cost.** Both terms favour the early steps: an error at iteration two poisons ten expensive iterations, one at iteration eleven poisons one. That is why a free typecheck runs everywhere and a judge runs only at checkpoints. For the judge the break-even is arithmetic, since it is the only verifier on the ladder with a token price: a call reading a 12,000-token candidate costs about what the run's third iteration costs, so twelve of them add roughly 144,000 tokens to a 276,000-token run, over half again, while three at checkpoints add about 36,000, or 13%.

The fail-fast analogy from continuous integration is close but weaker than the case an agent has. Aborting a build on the first failing job is a *cost* optimisation over a graph of independent jobs, which is why plenty of teams deliberately run every job instead. Per-step verification is a *correctness* optimisation over a strictly serial chain where every later step reads the earlier ones: the unchecked error is not merely wasted work, it is silently incorporated into everything after it.

---

## 6. When a fact stops being a fact: flaky and slow verifiers

Sections 1 to 5 assume the verifier works. Three things break that assumption, and the next three sections take them in turn: the check is unreliable or too slow, the check can be gamed, and there is no mechanical check to be had. Start with the first, because the ladder's "cannot be wrong" column is a claim about *reproducibility*, not about test quality.

**Flakiness.** A non-deterministic test is the worst available gate, and worse for an agent than for a person. It fails work that is correct, hands the model a convincing failure report, and the model dutifully repairs code that was never broken. The damage is invisible, because every artefact of a healthy correction loop is present: a failing check, a specific report, an edit, a green run afterwards. A developer carries a prior about which tests lie and re-runs them; the agent has none, and §4's design (failures are verbose, feed the report straight back) is what promotes a flaky test from an annoyance to an active hazard. Quarantine it out of the agent-facing gate *before* anyone gets round to fixing it. A gate that is right 98% of the time is not 98% of a gate.

**Latency.** A check slower than the work it guards will be skipped, by a person or by a scheduler, and the answer is layering rather than choosing.

| Layer | What runs | When | Budget |
| --- | --- | --- | --- |
| Fast gate | typecheck, plus the unit tests touching the files just changed | every step | a few seconds |
| Checkpoint gate | the full suite, the linter, the build | before each commit or checkpoint | up to a minute |
| Decision gate | an independent judge against a rubric | at real decision points, and on the loop's exit | one model call |

Keep the per-step gate under about a tenth of the step it guards: a thirty-second edit-and-test iteration can afford a three-second check and cannot afford a four-minute one. If the four-minute check is the only one you have, it belongs on the checkpoint row rather than on the step.

---

## 7. The verifier can be gamed

Everything above the ladder's dashed line returns a fact. A fact about a suite the agent has just edited is not ground truth.

This is measured behaviour, not a hypothetical. Anthropic's Claude 4 system card defines reward hacking as a model finding a way to maximise its reward that "technically satisfies the rules of the task, but violates the intended purpose", and names the two shapes it takes on coding work: **hard-coding**, "writing solutions that directly output expected values", and **special-casing**, "writing insufficiently general solutions", both in order to pass tests (Anthropic, 2025). The same document gives the detector, which is the defence stated as an experiment: run the model's solution through held-out tests hidden from the model, and see whether the fix generalised or was fitted to the cases in front of it.

Four harness-level rules follow.

- **The verifier must not be writable by the thing it verifies.** Put the test files behind a pre-tool deny-list ([Post 13](../13-hooks-enforcement/index.md) §4). An agent that can edit the gate does not have a gate.
- **Prefer tests the agent never sees.** Hold part of the suite out of the working tree and run it only at the gate: SWE-bench's design, brought inside your own harness (§2; Jimenez et al., 2023).
- **Diff the verifier as part of the verdict.** If the test files changed under the agent's hands during the run, the run fails, whatever the tests now say.
- **Treat a sudden green as a signal.** A long streak of failures that resolves in a single attempt is more often a special case than an insight.

The general law is one this series meets twice. [Post 22](../22-evaluating-harnesses/index.md) shows Goodhart's law at the benchmark, in its closing section on overfit: once a measure becomes a target it stops being a good measure, and a harness tuned until it aces an eval set may only have learned the eval set. This section is the same law at the gate, one level down and inside a single run, and the difference is visibility. Benchmark overfit is slow and shows up as a number that rises while nothing improves; a gamed gate is instant and shows up as nothing at all.

---

## 8. Which tasks admit a verifier at all

The ladder ranks verifiers. It does not say whether the task in front of you has one, so a reader whose job is "write the migration plan" or "summarise this incident" arrives at the bottom row with no way of knowing that was predictable.

The asymmetry-of-verification framing (Wei, 2025) supplies the checklist. A task is easy to verify to the extent that it has **objective truth** (everyone agrees what a good solution is), is **fast to verify** (seconds per solution), is **scalable to verify** (many solutions at once), is **low noise** (the verdict correlates tightly with real quality), and offers **continuous reward** (solutions can be ranked, not merely passed or failed). The accompanying law states the consequence: the ease of training a model to solve a task is proportional to how verifiable the task is (Wei, 2025).

Score the task on those five before designing the gate, and the score tells you which row of §2 you are entitled to.

| Property | "Fix this failing test" | "Write a data-migration plan" | "Summarise this incident" |
| --- | --- | --- | --- |
| Objective truth | yes: it passes or it does not | partly: several plans are defensible | no: faithfulness is a judgement |
| Fast to verify | yes, seconds | no: it is verified by executing it | seconds, but only by a reader |
| Scalable to verify | yes: run the suite | no | only through a judge |
| Low noise | high, unless the suite is flaky (§6) | low | moderate |
| Continuous reward | yes: the count of passing tests | no | a rubric score, noisy |
| Gate you get | a test gate on every step | a human approval gate before execution | a judge, sampled against human labels |

The law also explains what this series asserts everywhere and rarely justifies: why almost every pattern in these posts was discovered on code first. Code has near-perfect verification asymmetry, a compiler and a test suite delivering an objective, fast, low-noise verdict on work that took far longer to produce than it takes to check. In a domain with worse asymmetry the patterns still apply but the gate gets weaker, and the honest response is to build the missing ground truth (a fixture set, a golden file, a schema the plan must satisfy) rather than to promote a judge into a role it cannot hold.

---

## 9. Where the gate belongs

Verification is a component you place, not a mode you switch on everywhere. Two placements almost always earn their cost:

- **On the exit.** Never let the loop stop on a bare "final answer." Gate stop ① behind a check, so *done* means *verified*. This one gate removes victory declaration.
- **After a risky, reversible step.** An edit, a generated config, a refactor: verify immediately, while rolling back is a checkpoint away ([Post 08](../08-state-filesystem-git/index.md) §4).

Both of those check *after* the action, and that shape is only available when the action can be undone. A sent email, an executed migration, a deleted branch, a posted payment: for these there is nothing to roll back to, and a verifier that runs afterwards reports a fact you can no longer act on. The check has to move in front of the action, and only two mechanisms can hold there.

| The action is | Check runs | Mechanism | Why |
| --- | --- | --- | --- |
| Reversible | after | a verification gate in the loop (§4) | cheap and silent, and a failure costs one rollback |
| Irreversible, mechanically checkable | before | a blocking pre-tool hook ([Post 13](../13-hooks-enforcement/index.md)) | only one lifecycle point can actually stop a call; the others report |
| Irreversible, needs judgement | before | a human approval gate ([Post 15](../15-human-in-the-loop/index.md)) | approval is reserved for what a checkpoint cannot undo |

The reversible-versus-irreversible split selects the row, and it is the seam joining verification to hooks and to human approval.

One caution remains: do not verify *everything*. An expensive judge on every trivial step burns budget for little safety (§5), and a check slower than the work it guards will be skipped (§6). Layer the verifiers, and reserve the model's own self-critique for a first pass rather than the last word.

Finally, watch which checks keep firing. A verifier that catches the same failure over and over is not a gate doing its job; it is a rule waiting to be written down ([Post 10](../10-continual-learning-ratchet/index.md)) and then enforced. At that point verification stops being something the model cooperates with and becomes a **hook**, which is [Post 13](../13-hooks-enforcement/index.md).

---

## Common pitfalls

- **Letting the model be its own verifier.** Self-assessment skews positive, and an author grading its own work is not a check (§3). Use objective ground truth or a separate evaluator.
- **No ground truth at all.** "Does this look right?" answered by the model's own opinion verifies nothing. Find something executable (§2), and where the task cannot supply one, score it on the five properties before pretending otherwise (§8).
- **Verifying only at the end.** Fail-at-the-end wastes the whole run when an early step breaks, and the forfeited iterations are the expensive ones (§1, §5).
- **Swallowing the failure.** A gate that returns only "failed" gives the model nothing to fix. Failures must be verbose (§4).
- **Retrying forever.** A correction loop with no `max_attempts` becomes a doom loop. Cap it, and break early when the same report repeats (§4; Post 03, exits ② and ④).
- **Trusting a flaky gate.** A non-deterministic test hands the model a false failure report, and the model then repairs code that was never broken (§6). Quarantine it out of the gate first.
- **Mistaking a green gate for correctness.** Passing checks verify what they cover, not everything, and a green run from a suite the agent just edited is not evidence at all (§2, §7).

---

## Further reading

- Faros AI, "Harness Engineering" (2026): verification loops as fail-fast, and why unverified autonomy wastes compute.
- Addy Osmani, "Agent Harness Engineering" (2026): self-verification, its positive skew, and "success is silent, failures are verbose."
- Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (2024) and Kamoi et al., "When Can LLMs Actually Correct Their Own Mistakes?" (2024): the negative result, and the survey tying self-correction to reliable external feedback.
- Madaan et al., "Self-Refine" (2023) and Shinn et al., "Reflexion" (2023): the constructive half, and what changes when the feedback comes from execution.
- Panickssery, Bowman and Feng, "LLM Evaluators Recognize and Favor Their Own Generations" (2024) and Sharma et al., "Towards Understanding Sycophancy in Language Models" (2023): the mechanism behind the positive skew, and the training signal underneath it.
- Jason Wei, "Asymmetry of verification and verifier's rule" (2025): the five properties that decide whether a task can be gated at all.
- Anthropic, "System Card: Claude Opus 4 & Claude Sonnet 4" (2025), §6: reward hacking on coding tasks, with hard-coding and special-casing defined and held-out tests as the detector.
- Jimenez et al., "SWE-bench" (2023): grading a whole run on hidden tests the agent never sees.
- awesome-harness-engineering (2026): the Verification and continuous-integration section.
- Context Engineering, Post 20 (output evaluation) and Post 21 §4 (the validate-and-retry loop, one level down).

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 12 — Planner / generator / evaluator](../12-planner-generator-evaluator/index.md)**: making the evaluator a separate agent, so the grader is independent of the author.
- **[Post 13 — Hooks & deterministic enforcement](../13-hooks-enforcement/index.md)**: turning a verification step into a non-optional gate the model cannot skip.
- **[Post 22 — Evaluating harnesses](../22-evaluating-harnesses/index.md)**: the same logic across many runs, where a gate becomes a measurement.
- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: victory declaration, the failure this component removes.
