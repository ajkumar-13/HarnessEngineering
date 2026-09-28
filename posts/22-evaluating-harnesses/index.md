# 22 · Evaluating harnesses — Terminal-Bench, SWE-bench, harness A/B

> **TL;DR.** Harness quality is not measured on single outputs; it is measured on whole trajectories and their outcomes. The question is not "was that a good answer" but "did the run resolve the task", scored across a fixed set of real jobs and repeated often enough to see the spread. This post covers the agentic benchmarks that score whole runs (Terminal-Bench, SWE-bench and kin), the `pass@1` / `pass@k` / `pass^k` family and which member of it matches a deployment, how to build an internal eval harness whose graders you have actually tested, how to A/B a harness change with the model held constant and then tell a real difference from sampling noise, the production funnel that turns evals into dollars, and how to avoid the benchmark overfit that makes a proxy the target.
>
> **After reading this you will be able to:**
> - Distinguish output evaluation from trajectory and outcome evaluation, and pick the right unit for the thing you changed.
> - Build an internal eval harness of fixed tasks whose graders survive a null baseline and an oracle baseline.
> - A/B two harness configs on that set and say whether the observed lift survives a paired significance test.
> - Guard an eval set against overfit with a held-out split and production metrics that outrank any benchmark.

![Two panels side by side above a decision table. On the left, an output eval scores one completion from one prompt on a numeric scale, listing the graders it can use and what one score cannot see. On the right, a trajectory and outcome eval runs a whole multi-step agent run, twelve iterations re-reading about 277,000 input tokens, and asks whether the task resolved, such as tests passing or a pull request merging. The table below maps what you changed to which eval, its unit, and when it runs.](diagrams/01-output-vs-trajectory.svg)
*The unit moved from one answer to one run: harness quality lives on the right.*

Context Engineering, Post 20 built evaluation from the token side as a four-layer pyramid: deterministic unit checks at the base, component fixtures above them, end-to-end gold tasks above those, and online production metrics at the top, with a single completion as the unit at the lower layers. This post is the trajectory companion. The unit here is one **run** across many loop iterations, and the verdict is not a quality score on a sentence but a binary on an outcome: did the task actually resolve. Two of that pyramid's rules survive the change of unit unaltered, and both return below: every production incident becomes a permanent fixture, and the online layer outranks every offline one.

---

## 1. Output evals versus trajectory and outcome evals

An **output eval** takes one prompt, samples one completion, and scores it against an exact match, a regular expression, a rubric, or a model judge. The unit is fixed: one answer in, one number out. It is cheap, repeatable, and the right tool for tuning a prompt.

A harness is not a prompt. A single run calls the model dozens of times, executes shell commands, edits files, spawns sub-agents, and hits verification gates ([Post 03](../03-the-agent-loop/index.md)). Scoring the final message of that run misses almost everything that makes a harness good or bad: whether it recovered from a failed test, whether it looped without progress, whether it stopped when it should. Those are properties of the **trajectory**, not the output.

So harness evaluation changes the unit. A **trajectory eval** scores what happened during the run, such as steps taken, tokens burned, or whether a gate fired (§9). An **outcome eval** scores the end state against the world: do the tests pass, does the code compile, is the pull request (PR) mergeable. The outcome eval matters most, because it is objective and it is what the user actually wanted, and most of this post is about measuring it well.

This is also why per-step verification and whole-run evaluation are different jobs. Verification ([Post 11](../11-verification-loops/index.md)) is a gate inside a single run that decides whether to continue; an outcome eval sits outside the run and asks whether the finished run was any good. One steers a live agent, the other grades a dead one, and they use the same graders pointed at different moments.

The distinction only pays for itself when it resolves a decision, and the decision is always the same one: something changed, so what do you run? Every row of the table is argued somewhere below.

| What you changed | Which eval | The unit | The grader | When it runs |
|---|---|---|---|---|
| Prompt wording | Output eval (Context Engineering, Post 20) | one completion | rubric or model judge | every commit |
| A tool schema | A subset of the internal set | one run | schema validation ([Post 06](../06-tools-bash-code/index.md) §7) plus the objective grader | every PR |
| A harness component | An A/B with a per-task diff (§7) | the same task under both configs | objective grader | every PR that touches the loop |
| The model version | The frozen set as a regression gate (§7) | one run per task per seed | objective grader | every model upgrade |
| Nothing: live traffic | The production funnel (§10) | a merged unit of work | merge, revert, rework | continuously |

Read the table top to bottom and the cost rises, the feedback slows, and the authority of the answer increases. That ordering is §11's ranking rule in compact form: a production outcome outranks an internal eval, which outranks a public benchmark.

---

## 2. Agentic benchmarks: Terminal-Bench, SWE-bench and kin

The public agentic benchmarks are outcome evals at scale. Each task is a real job with an objective grader, and a score is earned only by a whole run that resolves it.

**Terminal-Bench** is the one this series leans on hardest. It is a benchmark of terminal work run by Stanford, the Laude Institute and Snorkel AI, and version 2.0 is 89 hard, human-verified tasks spanning software engineering, machine learning, security, data processing, scientific computing and system administration (Terminal-Bench, 2025). Each task runs in its own container under **Harbor**, an execution framework that spins up the sandbox, runs the agent, and scores the resulting machine state, which is what makes third-party runs comparable rather than anecdotal. The detail worth pausing on is the shape of a leaderboard row: it carries a **model** column and an **agent** column, so an entry is a scaffold paired with a set of weights, not a model on its own. The benchmark's own reporting unit is `Agent = Model + Harness` (Trivedy, LangChain, 2026), and anyone who reads that leaderboard as a model ranking is ignoring half of every row.

**SWE-bench** is the older and more-quoted example (Jimenez et al., 2024). Each task is a genuine GitHub issue from a real Python project, paired with the tests the merged fix later had to pass; the original set is 2,294 instances from twelve repositories. The agent gets the repository at the pre-fix commit and the issue text, and must produce a patch, graded by running tests rather than by reading prose. The grading contract has two halves and only the first is usually quoted. An instance resolves when every **FAIL_TO_PASS** test now passes *and* every **PASS_TO_PASS** test still does: the benchmark grades the fix and the absence of collateral damage in one verdict. That second half is its own answer to the fixed-five-broke-three problem §7 warns about, built into the grader rather than left to the reader.

The family kept being re-cut, and each cut answers a defect in the one before it.

| Variant | Size | What it changed | Why |
|---|---|---|---|
| SWE-bench (Jimenez et al., 2024) | 2,294 instances, 12 repositories | the original | issue plus hidden tests as an objective grader |
| SWE-bench Lite | 300 instances | a cheaper subset | full-set cost put it out of reach for small teams |
| SWE-bench Verified (OpenAI, 2024) | 500 instances | validation by expert engineers | under-specified issues and over-specific tests in the original |
| SWE-bench Pro (Deng, Da et al., 2025) | 1,865 problems, 41 repositories | public (11 repos), held-out (12), commercial (18) | longer horizons, and splits that resist contamination |

The 2026 status matters more than the sizes. In February 2026 OpenAI announced that it no longer reports SWE-bench Verified, and recommended that other developers stop too (OpenAI, 2026). The stated grounds were saturation, with the state of the art moving only from 74.9% to 80.9% over six months, and contamination: an audit of 138 hard tasks found the test design or problem statement flawed in 59.4% of them, and a frontier model solving tasks classified as nearly impossible turned out to be reasoning from release-note details that appear nowhere in the problem statement. That is §11's argument happening in public to the field's most-cited coding benchmark.

Two properties still make benchmarks of this shape the right instrument for harness work. They score trajectories through outcomes, so a clever prompt that talks a good game but never runs the tests scores zero. And the evidence they carry is the evidence a harness engineer needs: on Terminal-Bench 2.0 the same model, with only the harness changed, moved from 52.8% to 66.5%, a gain of 13.7 points and roughly twenty-five leaderboard places, with the weights pinned at `gpt-5.2-codex` (Trivedy, LangChain, 2026). On 89 tasks that is 47 resolved rising to 59: twelve jobs the same weights could always do that the old harness never elicited. That swing is the whole reason to evaluate harnesses at all, and [Post 04](../04-harness-beats-model/index.md) grades the evidence for it in detail.

The caveat is the one the February 2026 announcement makes concrete. A public benchmark is a shared, static target: invaluable for calibration against the field, but its publicity invites the overfit §11 warns about, and its tasks rarely match your product. That is why you also build your own.

---

## 3. `pass@1`, `pass@k`, `pass^k`: what the number promises

Benchmark scores are reported in a small family of metrics that look interchangeable and are not. The difference is between a number that predicts production and a number that flatters it.

| Metric | Definition | What it measures | When to quote it |
|---|---|---|---|
| `pass@1` | the fraction of tasks resolved on a single attempt | one-shot capability | the closest member of the family to a single production run |
| `pass@k` | the fraction resolved by *at least one* of k attempts | discovery under retry | only when the harness really retries and something picks the winner |
| `pass^k` | the fraction resolved by *all* k attempts | consistency across repeats | when a user gets one run and cannot choose which one they got |

`pass@k` for k greater than one is the member most likely to mislead. It counts a task as resolved if any attempt succeeded, which is the right question when a human or a verifier will sift k candidates and the wrong question when a user gets whatever the first run produced. Quoting a `pass@8` figure for a one-shot deployment overstates the system by however much luck contributed.

`pass^k` is the counterpart, formalised in tau-bench as a reliability measure over repeated trials (Yao et al., 2024). Its numbers are sobering: on that benchmark's retail domain, state-of-the-art function-calling agents succeeded on under 50% of tasks on a single attempt and dropped below 25% at `pass^8`, so requiring eight consecutive successes halved the apparent capability. Nothing about the agent changed between those two figures; only the question did.

Computing all three from the same seed matrix is a few lines, and it is the cheapest way to stop quoting the flattering one by accident:

```python
# results[task_id] is a list of booleans, one per seed: did that run resolve?
def pass_at_1(results):                        # mean over every individual run
    runs = [r for seeds in results.values() for r in seeds]
    return sum(runs) / len(runs)

def pass_at_k(results, k):                     # at least one of k succeeded
    return sum(any(seeds[:k]) for seeds in results.values()) / len(results)

def pass_pow_k(results, k):                    # ALL k succeeded
    return sum(all(seeds[:k]) for seeds in results.values()) / len(results)
```

The rule: report `pass@1` as the headline, report `pass^k` beside it at whatever k a user is likely to hit in the same workflow, and quote `pass@k` only with the retry mechanism named. Reliability, not one-shot capability, is the wall most agents hit in production, and the gap between the first row of that table and the third is the size of the wall.

---

## 4. Building an internal eval harness

An internal eval harness is a fixed set of tasks representative of your product, each with an objective grader, that you can run on demand. It is the SWE-bench idea, scoped to the jobs your agent actually does.

Three ingredients make it trustworthy, and §5 adds a fourth that most teams skip.

- **A fixed task set.** The tasks must not drift between runs, or you cannot compare two harness versions. Freeze them, version them, and grow the set only by adding, never by quietly editing. The richest source is your own history: every trace that exposed a real failure ([Post 21](../21-observability-traces/index.md)) becomes a task, and every failure mode ([Post 05](../05-agent-failure-modes/index.md)) becomes a category to cover. This is the run-level form of the sibling series' ratchet, where every production incident becomes a permanent offline fixture (Context Engineering, Post 20); here the fixture is a whole task rather than a prompt.
- **Objective graders.** Prefer graders that inspect the world, not the transcript. Did the test suite pass, did the file get the expected line, did the service return 200. A grader that runs code is worth ten that read prose, because it cannot be talked into a pass. Reserve model judges for genuinely subjective tasks, keep the judge independent of the agent that produced the work, because an author grading its own output skews positive ([Post 11](../11-verification-loops/index.md)), and remember that even an independent judge carries biases of its own, catalogued on the token side as the four judge failure modes (Context Engineering, Post 20).
- **Repeatable execution.** Each task runs in a clean, isolated workspace ([Post 17](../17-parallel-agents-shared-repo/index.md) for worktree isolation, [Post 14](../14-permissions-sandboxes/index.md) for the sandbox boundary) so runs do not contaminate each other, and each is repeated across several seeds because agent runs are stochastic. Report resolved-rate as a mean over seeds with its spread, and `pass^k` beside it (§3).

One run of the harness produces a table: per task, per seed, did it resolve, at what token and dollar cost, in how many iterations. Fix that shape early, because §7 differences it, §8 tests it, and §9 reads its non-binary columns.

---

## 5. Validating the grader before you trust it

A resolved-rate is only as good as the test that produced it, and a grader is a program written by people thinking about the agent rather than about the grader. Two baseline runs, one degenerate and one ideal, catch most of what goes wrong, and both are cheap because neither calls a model.

```python
# Run before the set is trusted, and again whenever a task is added.
for task in TASK_SET:
    if task.grade(EMPTY_RUN):                  # an agent that did nothing at all
        raise BadTask(f"{task.id}: passes without the work being done")
    if not task.grade(task.reference_solution):
        raise BadTask(f"{task.id}: the known-good solution fails its own grader")
```

The **empty agent** must score zero on every task. Any task it passes is checking something the agent never had to do: a test that was already green, an assertion on a file the fixture ships, a grader that greps for a word the prompt itself contains. The **oracle** applies the known-good solution and must score one on every task. Any task it fails is broken rather than hard, and every run against it is a false negative that will be blamed on the harness. SWE-bench applies the second of these to its own instances, checking that the gold patch turns the FAIL_TO_PASS tests green before an instance joins the set.

Skipping the practice is not hypothetical. UTBoost augmented the test suites of SWE-bench instances and found 36 whose tests were insufficient, which between them had let through 345 patches the original graders scored as correct; correcting those affected 24.4% of SWE-bench Verified leaderboard entries for 11 ranking changes, and 40.9% of SWE-bench Lite entries for 18 (Yu et al., 2025). A quarter of the entries on a flagship leaderboard were reporting the grader rather than the agent.

Two operational hazards round the section out. A **flaky test inside the graded suite** produces noise indistinguishable from a harness regression, so run each grader twice against the unchanged workspace and quarantine anything that disagrees with itself. And every grader needs a **wall-clock and resource budget**, because a hung test suite reports as a failure and blames the harness for an infrastructure problem, which is wrong in the direction that makes you change working code.

---

## 6. Sizing the set and scheduling the runs

"A fixed set, repeated a few times" is not a plan until it has dimensions, and the dimensions follow from arithmetic rather than taste. Take the run-cost model this series already carries: a twelve-iteration task re-reads roughly 277,000 input tokens across the run, about $0.83 at an illustrative $3 per million ([Post 23](../23-economics-haas/index.md), with the working in [Post 03](../03-the-agent-loop/index.md) §8). A 60-task set at three seeds under two harness configs is 60 × 3 × 2 = 360 runs, so roughly $300 of model spend for one complete A/B sweep. At four minutes of wall clock a run that is 24 machine-hours, which is 72 minutes at 20-way parallelism and an overnight job at four-way. The constants are illustrative; the arithmetic is what turns "run the evals" into a line item somebody can approve.

The cost is what forces a cadence gradient rather than one setting for everything:

| Cadence | What runs | Runs per sweep | Wall clock at 20-way | Illustrative spend |
|---|---|---|---|---|
| Every harness diff | 15-task smoke subset, 1 seed, both configs | 30 | ~6 minutes | ~$25 |
| Nightly, and on every model upgrade | full 60-task set, 3 seeds, both configs | 360 | ~72 minutes | ~$300 |
| At release | held-out split, 3 seeds, shipping config only | ~90 | ~18 minutes | ~$75 |

The set size is not a matter of taste either, because it fixes the smallest lift you can detect (§8). Twenty tasks is a smoke test, not an experiment: nothing short of a landslide separates two configs on that many, so a team that ships on a two-point difference over twenty tasks is reading noise. Choose the size from the effect you need to see, then pay for it or accept that you cannot see it.

---

## 7. A/B-testing a harness change

Once the task set is fixed, a harness change becomes a controlled experiment: change one component, hold everything else constant, run both configs on identical tasks, and compare.

![A pipeline diagram above a significance test. One fixed task set, 60 tasks at 3 seeds for 360 runs a sweep, feeds two branches: Harness A configured with no verify gate and Harness B configured with a verify gate added. A banner notes the model is held fixed across both. Both branches run the same tasks and produce a per-task win count, converging into a Compare box that records a net of 4 tasks, a 6.7-point lift and a sign test of p = 0.39, and calls that not yet a verdict. Below, two sign-test cases on the same 12 discordant pairs return p = 0.39 and p = 0.039.](diagrams/02-harness-ab-pipeline.svg)
*One controlled variable, one verdict: the gate lifts resolved-rate enough to justify its extra spend.*

The variable under test is a single harness component: a stop condition, a hook, a tool, a verification gate. The model is **held fixed**, because if you change the model and the harness together you learn nothing about either, and the tasks are held fixed. Only the one component moves, so any difference in resolved-rate is attributable to it.

The runner below is the whole comparison, and the one structural thing it adds to a naive version is the seed loop that keeps §4's promise about spread:

```python
# A/B two harness configs on one fixed task set, with the model held fixed.
SEEDS = (0, 1, 2)                              # every task is run once per seed

def resolved(task, config, seed):
    result = agent_loop(task, model="fixed-model-v1", config=config, seed=seed)
    return bool(task.grade(result))            # objective grader, no rubric

A = {"verify_gate": False}                     # Harness A: no verification gate
B = {"verify_gate": True}                      # Harness B: plus a verification gate

wins_a = wins_b = ties = 0
rate_a, rate_b = [], []
for task in TASK_SET:                          # fixed, versioned, never edited
    a = [resolved(task, A, s) for s in SEEDS]  # one result per seed, not one run
    b = [resolved(task, B, s) for s in SEEDS]
    mean_a, mean_b = sum(a) / len(SEEDS), sum(b) / len(SEEDS)
    rate_a.append(mean_a)
    rate_b.append(mean_b)
    if mean_a > mean_b: wins_a += 1            # discordant pair: A resolved more
    elif mean_b > mean_a: wins_b += 1
    else: ties += 1
    print(f"{task.id:20} A={mean_a:.2f} B={mean_b:.2f}")

n = len(TASK_SET)
print(f"resolved  A={sum(rate_a) / n:.0%}  B={sum(rate_b) / n:.0%}")
print(f"A-only wins={wins_a}  B-only wins={wins_b}  ties={ties}")
```

The per-task win/loss list matters as much as the aggregate. An aggregate that says "Harness B is two points better" can hide the fact that B fixed five tasks and broke three; the per-task diff shows which tasks each config won, which is where you learn what the gate actually did. A change that lifts the mean while regressing tasks you care about is often the wrong change, and only the row-by-row view reveals it. The counts it accumulates, `wins_a` and `wins_b`, are the discordant pairs, and §8 turns them into a verdict.

Cost belongs in the verdict too. A verification gate that adds thirteen points of resolved-rate for thirteen cents per resolved task is usually worth shipping; the same gate for ten times the cost may not be. Each branch of the diagram above emits a cost per resolved task alongside its rate, which is why its compare box reports both and why a compare box that reads only the rate is giving you half a verdict.

The same machinery runs in reverse, and that is where it earns its keep in production. A model upgrade is a harness A/B with the roles swapped: hold the harness fixed and change the model. Providers update models continually, and a new version can silently shift tool-call formatting, stop-condition behaviour, or a prompt the old model handled, regressions no single-output eval will catch. So run the frozen task set as a **regression gate on every model upgrade**, not only on harness diffs: pin the model version, and promote a new one only when the set holds or improves, enforced as a gate rather than as a convention ([Post 13](../13-hooks-enforcement/index.md)). The trace that first exposed a failure ([Post 21](../21-observability-traces/index.md)) becomes the task that guards its return, and schema validation ([Post 06](../06-tools-bash-code/index.md) §7) absorbs a changed tool-call shape before it reaches the loop.

---

## 8. Knowing when a difference is real

Every number in §7 is an estimate from a sample, so the first question a verdict has to answer is whether the difference could be a coin flip. The tally the runner already computed is the input to that test.

A two-sided **sign test** on the discordant pairs asks exactly that. Ties carry no information about direction and drop out; what remains is the tasks where the two configs disagreed, and the null hypothesis is that either side won each of those with equal probability.

```python
from math import comb

def sign_test(wins_a, wins_b):
    """Two-sided p-value on the discordant pairs: could this be a coin flip?"""
    n, k = wins_a + wins_b, min(wins_a, wins_b)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)

print(sign_test(4, 8))    # 0.388 on 12 discordant pairs: indistinguishable from noise
print(sign_test(2, 10))   # 0.039 on the same 12 pairs: a lift worth acting on
```

Work the first case through, because it is the one that gets shipped. On a 60-task set, 8 tasks won only by B against 4 won only by A is a net of 4 tasks, a 6.7-point lift, and a result most teams would announce. On 12 discordant pairs the two-sided sign test returns p = 0.39: a fair coin produces a split at least that lopsided about two times in five. The same 12 pairs split 10 to 2 gives p = 0.039, a different situation entirely. The headline lift is identical in kind and the evidence is not, and nothing in the aggregate resolved-rate distinguishes them.

The second number is about how the comparison is arranged. Run the two configs as **independent** samples on a 50-task set, each landing near 50%, and the 95% interval on the difference of the two rates is about ±20 points: no realistic harness change is visible at all, and the experiment was doomed before it started. Running both configs on the *same* tasks and differencing per task removes the task-difficulty variance that dominates that interval, which is the central practical recommendation of the standard treatment of eval statistics: conduct inference on question-level paired differences rather than on population-level summary statistics (Miller, 2024). That work also notes that when tasks arrive in related groups, clustered standard errors can be over three times the naive ones, which matters for any eval set built by taking several tasks from each of a few repositories.

The rule is short. Report the lift, the discordant-pair counts, and a p-value or an interval; pair every comparison by construction; and treat an unpaired A/B as untrustworthy rather than as weak evidence. Significance is not the last word either, because a difference can be real and still too small to pay for, which is what §10 is for.

---

## 9. Reading the trajectory, not only the outcome

The outcome eval says *whether* the harness got better. It never says *which component* made it better, and that is what the next change depends on. The trajectory metrics answer it, and they cost almost nothing to collect because [Post 21](../21-observability-traces/index.md)'s spans already carry every field.

Six are worth reporting beside the binary:

- **Iterations to resolution.** The distribution, not the mean. A gate that resolves the same tasks in nine turns instead of fourteen is a real improvement the resolved-rate cannot see.
- **Tokens per resolved task.** The economic version of the same number, and the one that feeds §10.
- **Tool-call error rate.** A rising rate is a tool-contract problem ([Post 06](../06-tools-bash-code/index.md)), not a model problem.
- **Redundant-read rate.** Repeated identical tool calls are the doom-loop signature ([Post 05](../05-agent-failure-modes/index.md)), visible in an eval sweep long before a user reports one.
- **Gate-fire counts.** A gate that never fires is not protecting anything; one that fires constantly is a symptom rather than a fix.
- **The distribution of stop reasons.** Runs ending in `COMPLETED`, `MAX_ITERS`, `BUDGET` and `NO_PROGRESS` in different proportions between two configs tell you what changed even when the resolved-rate did not move.

The trap is that every one of these is trivially gamed in the wrong direction. "Fewer steps" is achieved by giving up sooner, "fewer tokens" by not reading the file, "no gate fires" by removing the gate. None may become a target or a gate in its own right, which is Goodhart's law arriving early (§11). The outcome decides; the trajectory explains.

---

## 10. Production metrics: the staged funnel

Benchmarks and internal evals are proxies you run before shipping. Once a harness is live, the truth is in production metrics, and the useful ones are outcomes with money attached.

![Three narrowing stages, runs attempted, results a human accepted, and work that actually shipped, each carrying one illustrative week of counts and an arrow to its metric: first-pass success rate, defect-escape rate, and dollars per merged PR. Beneath them a ledger for the same week prices Harness A at $49 a merged PR against Harness B at $54.](diagrams/03-production-funnel.svg)
*Each stage is a stricter filter, and each metric only means something relative to the stage above it.*

The three metrics come from Faros AI's staged instrumentation guidance, where dollars per merged PR is available almost immediately while first-pass success and defect-escape rate require linking agent sessions to pull requests (Faros AI, 2026). Arranged as a funnel they read as three narrowing filters:

- **First-pass success rate.** Of the runs attempted, what fraction produced a result a human accepted without rework. This is the internal eval's resolved-rate (§4), measured on live traffic rather than a frozen set.
- **Defect-escape rate.** Of the results accepted, what fraction later turned out wrong: a reverted PR, a reopened ticket, a regression caught downstream. A high first-pass rate with a high escape rate means plausible work that does not hold, which is worse than an honest failure.
- **Dollars per merged PR.** The end-to-end unit cost: spend on model tokens, retries, and human review, divided by the units of work that actually shipped.

Most teams can compute the cost number long before either quality number, which is why cost-only verdicts are the common failure and why a cheap harness can look like a good one for a whole quarter.

The claim worth testing is that a harness can win on resolved-rate and still be the worse system, and it only becomes believable with the arithmetic on the page. Take one week, all figures illustrative, with review priced at a loaded $120 an hour: fifteen minutes to review an accepted result, five to triage a rejected one, and forty-five to redo one that was reverted.

| One week, illustrative | Harness A | Harness B (heavier verification) |
|---|---|---|
| Runs attempted | 200 | 200 |
| Accepted without rework | 118 (59% first-pass) | 132 (66% first-pass) |
| Later reverted | 9 (7.6% escape) | 14 (10.6% escape) |
| Net shipped | 109 | 118 |
| Model spend, at $0.85 and $2.55 a run | $170 | $510 |
| Human review and rework | $5,170 | $5,900 |
| **Dollars per merged PR** | **$49** | **$54** |

B wins the eval by seven points of first-pass rate and loses the ledger by about 11%. Two things did it: the heavier verification loop tripled the model spend per run, and the extra accepted work carried a worse escape rate, so five more reverts ate the review saving. Hold B's escape rate down to A's 7.6% and it lands at about $50 a merge, a tie rather than a win, so the model spend alone was enough to cancel a seven-point lift.

That is also why defect-escape rate is the metric that keeps the funnel honest. The cheapest way to raise first-pass acceptance is to produce work that looks right under review, and escape rate is the only stage that catches it afterwards. A harness A/B (§7) predicts a lift; the funnel confirms whether it survived contact with real traffic and whether it was worth its cost. When the two disagree, the funnel wins, and the disagreement is itself a measure of how far your eval set has drifted from the product.

---

## 11. Guarding against benchmark overfit

Every benchmark is a proxy, and every proxy invites Goodhart's law: once a measure becomes a target, it stops being a good measure (Strathern, 1997, restating Goodhart, 1975). A harness tuned until it aces a benchmark may have learned the quirks of that benchmark rather than gained general skill. The failure is silent, because the number keeps rising while real performance does not.

The standard defence is a **held-out set**. Split the task set into a development split you tune against and an evaluation split you touch rarely and never optimise on directly. Report both. When the dev split climbs and the held-out split does not follow, you have overfit, and the gap between them is the size of it. Three mechanics make that more than a principle:

- **Retire on inspection, not on a schedule.** A held-out task is spent the moment somebody reads it in a post-mortem, because looking at why it failed is optimisation whether or not anything changes as a result. Rotate a fresh batch in when a task has been read, and expect the held-out line to step down when you do.
- **Plot the gap, do not read it once.** The dev-minus-held-out gap tracked across tuning rounds shows up as a trend several rounds before either number looks wrong on its own. A gap that widens monotonically is overfit accumulating.
- **Split at scale if the stakes justify it.** SWE-bench Pro keeps eleven public repositories, twelve held out, and eighteen commercial ones that are never published at all (Deng, Da et al., 2025), so the numbers people quote and the numbers that discriminate come from different sets by construction.

Overfit runs in two directions, and the held-out split defends against only one. The first is tuning to the tasks, which is what OpenAI's February 2026 withdrawal of SWE-bench Verified documents: saturation plus evidence that frontier models had already seen the answers, so the score reflected exposure rather than capability (OpenAI, 2026). The second is a grader too weak to catch a wrong answer, which UTBoost measured on the same benchmark family (Yu et al., 2025) and which §5's two baseline runs exist to prevent. A number can be inflated because the agent learned the test, or because the test could not tell. Both look like progress.

So weight the metrics rather than averaging them. A real production outcome outranks an internal eval, which outranks a public benchmark; keep contamination in mind, because a public task set may already sit in a model's training data; and treat any public benchmark as calibration against the field rather than as the objective. The benchmark tells you that you are in the game; only the funnel tells you that you are winning it.

One closing note on ownership. Agent evaluation is a young field without the settled standard output evals enjoy, so treat the eval harness as a living system with a named owner rather than a rig you build once. An eval set with no owner drifts away from the product it represents, and the drift stays invisible until the funnel and the eval disagree (§10), by which point you have been steering on the wrong number for as long as the drift took.

---

## Common pitfalls

- **Scoring the final output of a run.** A harness is a trajectory, and grading only its last message misses the recovery, the loops, and the stop behaviour (§1).
- **Quoting `pass@k` for a one-shot deployment.** It counts a task resolved if any of k attempts worked, which is not what a user gets. Report `pass@1`, and `pass^k` beside it (§3).
- **Graders that read the transcript.** A grader that inspects the model's own account of its work can be talked into a pass. Grade the world, not the words (§4).
- **Trusting a grader nobody tested.** An empty agent that passes a task, or an oracle that fails one, means the number is measuring the grader (§5).
- **Changing the model and the harness together.** If two variables move at once, the A/B teaches you nothing about either (§7).
- **Shipping on an unpaired or untested difference.** A 6.7-point lift on twelve discordant pairs can be a coin flip, and two independent 50-task runs cannot resolve anything under twenty points (§8).
- **Resolved-rate without cost.** A lift that triples the dollars per merged PR may not be worth shipping. The verdict is always outcome against cost (§7, §10).
- **Optimising on the held-out set.** Tuning against a split stops measuring generalisation and starts measuring memorisation, and a task read in a post-mortem is already spent (§11).

---

## Further reading

- Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (ICLR 2024): 2,294 issues from twelve Python repositories, and the two-sided FAIL_TO_PASS plus PASS_TO_PASS grading contract.
- OpenAI, "Introducing SWE-bench Verified" (August 2024): the 500-instance human-validated subset, and what expert review found wrong with the originals.
- OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities" (February 2026): the saturation and contamination case for retiring it.
- Deng, Da et al., "SWE-Bench Pro" (2025): 1,865 long-horizon problems over 41 repositories, split public, held-out and commercial as a contamination defence.
- Yu et al., "UTBoost: Rigorous Evaluation of Coding Agents on SWE-Bench" (ACL 2025): what a grader too weak to catch a wrong patch does to a leaderboard.
- Yao et al., "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" (2024): the `pass^k` reliability metric, and the drop from under 50% at one attempt to under 25% at eight.
- Miller, "Adding Error Bars to Evals" (2024): paired differences, clustered standard errors, and power analysis for eval sets.
- Terminal-Bench documentation (2025): 89 containerised terminal tasks under the Harbor runner, with leaderboard rows pairing an agent scaffold with a model.
- Yang et al., "SWE-agent" (2024): how much the interface around a fixed model moves resolved-rate.
- Faros AI, "Harness Engineering" (2026): the staged production metrics, cost per merged PR first and the quality metrics once sessions link to pull requests.
- Strathern, "'Improving ratings': audit in the British University system" (1997): the formulation of Goodhart's law this post uses.
- Context Engineering, Post 20: the four-layer eval pyramid from the token side, the output-eval companion to this view.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 23 — The economics of a harness & HaaS](../23-economics-haas/index.md)**: the dollars-per-merged-PR funnel here becomes a full cost model and the basis for harness-as-a-service.
- **[Post 26 — Capstone](../26-capstone-coding-agent/index.md)**: a coding agent built and then evaluated with exactly this task-set-and-grader machinery.
- **[Post 21 — Observability & trace-driven repair](../21-observability-traces/index.md)**: replays and regression sets grow into these evals, and its spans are what §9 reads.
- **[Post 04 — Why the harness beats the model](../04-harness-beats-model/index.md)**: the evidence these benchmarks produced, graded for how much weight each figure can carry.
