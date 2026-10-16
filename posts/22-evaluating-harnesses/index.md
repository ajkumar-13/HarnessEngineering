# 22 - Evaluating harnesses: Terminal-Bench, SWE-bench, harness A/B

> **TL;DR.** A harness is measured on whole runs, not single outputs: the question is not "was that a good answer" but "did the run resolve the task", scored by an objective grader across a fixed set of tasks, each run several times. The public agentic benchmarks score runs this way, and the member of the `pass@1`, `pass@k`, `pass^k` family a team quotes decides what the number promises. An internal eval set earns trust only after its graders survive an empty run and an oracle, and a harness change is settled by an A/B with the model held fixed, paired by task, whose interval says whether the lift is callable. Production outcomes outrank every offline number.
>
> **Prerequisites:** [post 11](../11-verification-loops/index.md), the verification gate and the verifier ladder whose graders an eval reuses.
> **Safe to skip?** Skip it if the reader can already validate a grader before trusting it, size an eval set for the lift that matters, and call or decline a harness A/B from a paired interval.
>
> **After reading, you will be able to:**
>
> - Distinguish output evals from trajectory and outcome evals, and pick the eval and its unit from what changed.
> - Read a benchmark score by its grading contract and its metric, choosing between `pass@1`, `pass@k` and `pass^k` for a deployment.
> - Build an internal eval set of fixed tasks and validate its graders with an empty run, an oracle and a re-grade before trusting them.
> - A/B a harness change with the model held fixed, compute the paired difference and its interval, and say whether the result is callable.
> - Size and schedule an eval sweep, and rank production funnel metrics above internal evals and benchmarks to guard against overfit.

![Two panels. Left, an output eval: one prompt, one completion, one score from a rubric or a judge, blind to how the answer was reached. Right, one agent run drawn as five turns of reason, act and observe; a test fails at turn 3 and the run recovers; a verification gate passes before exit (1), completed. A trajectory eval reads the path: turns, tokens, gate fires and the stop reason. An outcome eval reads the world the run left: do the tests pass.](diagrams/01-output-vs-trajectory.svg)

*The unit moves from one answer to one run: harness quality lives in the path and in the world the run leaves behind.*

---

## 1. Output evals versus trajectory and outcome evals

How is harness quality measured on whole trajectories and outcomes, and how is a real improvement told from sampling noise? The sibling series built evaluation from the token side as a pyramid of four tiers, unit, component, end-to-end and online, with a golden set and a regression gate in continuous integration (CI), and a single completion as the unit at the lower tiers (`ctx-020`). This post is its run-level companion: the unit is one **run** across many loop iterations, and the verdict is a binary on an outcome. Two of that pyramid's rules survive the change of unit unaltered and return below: every production incident becomes a permanent fixture, and the online tier is the source of truth.

An **output eval** takes one prompt, samples one completion, and scores it by exact match, a regular expression, a rubric or a model judge. One answer in, one number out: cheap, repeatable, and the right tool for tuning a prompt.

A harness is not a prompt. One run calls the model many times, executes commands, edits files, and passes or fails gates ([post 03](../03-the-agent-loop/index.md)). Scoring the final message misses what makes a harness good or bad: whether it recovered from a failed test, looped without progress, or stopped when it should. Those are properties of the **trajectory**.

So harness evaluation changes the unit, as the figure at the top draws. A **trajectory eval** scores what happened during the run: turns taken, tokens spent, which gates fired, why the loop stopped. An **outcome eval** scores the end state against the world: do the tests pass, does the code build, is the pull request (PR) mergeable. The outcome eval carries the verdict, because it is objective and it is what the user wanted; the trajectory explains it.

Per-step verification and whole-run evaluation are different jobs. The verification gate of [post 11](../11-verification-loops/index.md) sits inside a run and decides whether it may stop; an outcome eval sits outside and grades the finished run. Often they use the same graders, pointed at different moments.

The distinction pays for itself when it settles what to run after a change:

| What changed | Which eval | The unit | The grader | When it runs |
|---|---|---|---|---|
| Prompt wording | Output eval (`ctx-020`) | one completion | rubric or model judge | every commit |
| A tool schema | A subset of the internal set | one run | schema validation ([post 06](../06-tools-bash-code/index.md)) plus the objective grader | every PR |
| A harness component | A paired A/B | the same task under both configurations | objective grader | every PR that touches the loop |
| The model version | The frozen set as a regression gate | one run per task per seed | objective grader | every model upgrade |
| Nothing: live traffic | The production funnel | a merged unit of work | merge, revert, rework | continuously |

Read top to bottom, the cost rises, the feedback slows, and the authority of the answer grows: a production outcome outranks an internal eval, which outranks a public benchmark.

---

## 2. Agentic benchmarks: Terminal-Bench, SWE-bench and kin

The public agentic benchmarks are outcome evals at scale. Each task is a real job with an objective grader, and only a whole run that resolves it scores.

**Terminal-Bench** is the one this series leans on hardest. It is a benchmark of command-line work, a joint project of Stanford University and the Laude Institute, and version 2.0 (7 November 2025) is 89 hard, human-verified tasks, each run in its own container with a human-written oracle solution and tests that check the container's final state (Terminal-Bench, 2025). Runs go through **Harbor**, the framework released with it to run those containers reproducibly and at scale. The leaderboard has a model column and an agent column, so an entry is a harness paired with a set of weights: read as a model ranking, it ignores half of every row. The benchmark also fixes itself: Terminal-Bench 2.1 (6 May 2026) was released "to fix issues in 28 of the 89 tasks in Terminal-Bench 2.0", among them instructions that did not match the tests. Terminal-Bench 3.0 (30 July 2026) then started a new, harder set of 74 tasks, so a Terminal-Bench score compares only with scores on the same version.

**SWE-bench** is the older and more-quoted example (Jimenez et al., ICLR 2024). Each task is a real GitHub issue from a Python project with the tests its merged fix had to pass; the original set is 2,294 instances from twelve repositories. The agent gets the repository at the pre-fix commit and the issue text, and must produce a patch, graded by running tests. The grading contract has two halves: an instance resolves when every **FAIL_TO_PASS** test now passes *and* every **PASS_TO_PASS** test still does. The benchmark grades the fix and the absence of collateral damage in one verdict, the "fixed five, broke three" problem built into the grader.

The family kept being re-cut, each cut answering a defect in the one before.

| Variant | Size | What it changed | Why |
|---|---|---|---|
| SWE-bench (Jimenez et al., 2024) | 2,294 instances, 12 repositories | the original | an issue plus hidden tests as an objective grader |
| SWE-bench Lite | 300 instances | a smaller subset from the same authors | to lower evaluation cost |
| SWE-bench Verified (OpenAI, 13 August 2024) | 500 instances | screened by expert engineers | under-specified issues and over-specific tests in the original |
| SWE-Bench Pro (Deng, Da, Pan et al., 2025) | 1,865 problems, 41 repositories | public (11 repositories), held-out (12), commercial (18) | longer horizons, and splits that resist contamination |

The 2026 status matters more than the sizes. In "Why SWE-bench Verified no longer measures frontier coding capabilities" (23 February 2026), OpenAI wrote "we have stopped reporting SWE-bench Verified scores, and we recommend that other model developers do so too", and recommended SWE-Bench Pro instead. Its grounds were saturation, the state of the art moving "from 74.9% to 80.9% in the last 6 months", and flawed or contaminated tasks: an audit of 138 problems that OpenAI o3 did not consistently solve found "59.4% of the 138 problems contained material issues in test design and/or problem description", and on one Django task GPT-5.2's reasoning drew on the release notes for a parameter the problem statement does not explicitly require. That is benchmark overfit happening in public to the field's most-cited coding benchmark.

Two properties still make benchmarks of this shape the right instrument for harness work. They score trajectories through outcomes, so a run that talks well but never makes the tests pass scores zero. And they carry the evidence a harness engineer needs: in "Improving Deep Agents with harness engineering" (LangChain blog, 17 February 2026), Trivedy reports `deepagents-cli` moving from 52.8% to 66.5% on Terminal-Bench 2.0 with the model fixed at `gpt-5.2-codex`, a gain of 13.7 points, graded firm. On 89 tasks that is $0.528 \times 89 \approx 47$ resolved rising to $0.665 \times 89 \approx 59$: twelve jobs the same weights could do that the old harness never drew out. The article states the leaderboard move as "Top 30 to Top 5"; the score is the number that carries the argument, as [post 04](../04-harness-beats-model/index.md) argues in grading this evidence. SWE-agent's interface ablation (Yang et al., NeurIPS 2024), 18.0% against 11.0% on SWE-bench Lite with GPT-4 Turbo fixed, is the same kind of evidence, graded controlled there.

The caveat is the one the February 2026 announcement makes concrete. A public benchmark is a shared, static target: invaluable for calibration against the field, but its publicity invites overfit, and its tasks rarely match a team's product. Hence the internal set.

---

## 3. `pass@1`, `pass@k`, `pass^k`: what the number promises

| Metric | Definition | What it measures | When to quote it |
|---|---|---|---|
| `pass@1` | the chance one trial resolves the task, averaged over tasks | one-shot capability | the member closest to one production run |
| `pass@k` | the chance *at least one* of $k$ trials resolves it | discovery under retry | only when the harness really retries and something picks the winner |
| `pass^k` | the chance *all* $k$ trials resolve it | consistency across repeats | when users meet the agent repeatedly and every run has to work |

`pass@k` for $k > 1$ is the member most likely to mislead. It counts a task resolved if any attempt succeeded: the right question when a verifier sifts $k$ candidates, the wrong one when a user gets whatever the first run produced. A `pass@8` figure quoted for a one-shot deployment overstates the system by however much luck contributed.

`pass^k` is the counterpart, defined in τ-bench as "the chance that all k i.i.d. task trials are successful, averaged across tasks" (Yao et al., 2024). Its numbers are sobering: `gpt-4o` with function calling resolved about 61% of the benchmark's retail tasks at `pass^1` and about 25% at `pass^8`.

Both have unbiased estimators that use all $n$ trials of a task, not only the first $k$: with $c$ successes in $n$ trials, `pass@k` is $1 - \binom{n-c}{k} / \binom{n}{k}$ (Chen et al., 2021) and `pass^k` is $\binom{c}{k} / \binom{n}{k}$, each averaged over tasks (Yao et al., 2024). `snippets/pass_family.py` computes all three:

```python
def pass_at_1(counts, n):
    """Mean single-trial success; counts[t] is c, the successes of task t in n trials."""
    return sum(c / n for c in counts) / len(counts)


def pass_at_k(counts, n, k):
    """At least one of k trials succeeds: 1 - C(n - c, k) / C(n, k), averaged over tasks."""
    return sum(1 - comb(n - c, k) / comb(n, k) for c in counts) / len(counts)


def pass_hat_k(counts, n, k):
    """All k trials succeed: C(c, k) / C(n, k), averaged over tasks."""
    return sum(comb(c, k) / comb(n, k) for c in counts) / len(counts)
```

On ten illustrative tasks run eight times each, it prints:

```text
10 tasks, 8 trials each, successes per task: [8, 8, 7, 6, 5, 4, 3, 2, 1, 0]
pass@1 = 0.550
  k   pass@k   pass^k   (pass@1)^k
  1   0.550    0.550    0.550
  2   0.700    0.400    0.303
  4   0.820    0.280    0.092
  8   0.900    0.200    0.008
```

One agent, three honest numbers: 55% on one try, 90% if eight tries may be sifted, 20% if all eight must work. The last column is a trap: raising the pooled `pass@1` to the eighth power gives 0.8%, because `pass^k` is an average of per-task reliabilities, and the two tasks that never fail carry it. The independence the formula assumes holds within a task, not across tasks of different difficulty.

The rule: report `pass@1` as the headline, `pass^k` beside it at the $k$ a user is likely to meet, and `pass@k` only with the retry mechanism named. Reliability, not one-shot capability, is the wall agents hit in production, and the gap between `pass@1` and `pass^k` is its size.

---

## 4. Building an internal eval harness

An internal eval harness is a fixed set of tasks representative of the product, each with an objective grader, run on demand: the SWE-bench idea, scoped to the jobs the agent actually does. Three ingredients make it trustworthy, and the next section adds a fourth that is easy to skip.

- **A fixed task set.** Tasks must not drift between runs, or two harness versions cannot be compared. Freeze them, version them, and grow the set only by adding, never by quietly editing. The richest source is the team's own history: every trace that exposed a real failure ([post 21](../21-observability-traces/index.md)) becomes a task, and every failure mode of [post 05](../05-agent-failure-modes/index.md) becomes a category to cover. This is the run-level form of the sibling's rule that every incident becomes a permanent fixture (`ctx-020`); the fixture here is a whole task.
- **Objective graders.** Prefer graders that inspect the world, not the transcript: did the suite pass, did the file get the line, did the service answer. Keep model judges for genuinely subjective tasks, independent of the agent that did the work ([post 12](../12-planner-generator-evaluator/index.md)), and remember that an independent judge has failure modes of its own: position bias, verbosity bias, self-preference and rubric drift (`ctx-020`).
- **Repeatable execution.** Each run gets a clean, isolated workspace ([post 17](../17-parallel-agents-shared-repo/index.md) for worktrees, [post 14](../14-permissions-sandboxes/index.md) for the sandbox), so runs cannot contaminate each other, and each task runs under several seeds, because agent runs are stochastic.

One sweep produces a table: per task, per seed, per configuration, did it resolve, at what token and dollar cost, in how many iterations, and why it stopped. Fix that shape early: the A/B differences it, the significance test reads it, and the trajectory metrics come from its non-binary columns.

---

## 5. Validating the grader before trusting it

A resolved-rate is only as good as the grader that produced it, and a grader is a program written by people thinking about the agent rather than the grader. Three cheap checks catch the grossest faults, and none calls a model. `snippets/grader_check.py` runs them over six small tasks, three with a grader flawed on purpose:

```python
# Run before the set is trusted, and again whenever a task is added.
def validate(task_set):
    bad = []
    for task in task_set:
        if task.grade(EMPTY_RUN):
            bad.append((task.id, "passes without the work being done"))
        if not task.grade(task.reference):
            bad.append((task.id, "the known-good solution fails its own grader"))
        if task.grade(task.reference) != task.grade(task.reference):
            bad.append((task.id, "disagrees with itself on an unchanged workspace"))
    return bad
```

The **empty agent** must score zero on every task. A task it passes checks something the agent never had to do: a test already green, an assertion on a file the fixture ships, a grep for a word the prompt contains. The **oracle** applies the known-good solution and must score one. A task it fails is broken rather than hard, and every run against it is a false negative blamed on the harness. SWE-bench applies the second check to its own instances: a candidate joins the set only if the gold patch turns at least one test from failing to passing. The **re-grade** runs the grader twice on an unchanged workspace: a flaky test inside the graded suite produces noise indistinguishable from a harness regression, so anything that disagrees with itself is quarantined. The snippet prints:

```text
validating 6 tasks with an empty run, the reference solution and a re-grade
  BadTask mention-harness: passes without the work being done
  BadTask bump-patch: the known-good solution fails its own grader
  BadTask summarise-log: disagrees with itself on an unchanged workspace
sound: set-port, add-slugify, rename-flag
12 hand-labelled candidates on the sound tasks: 6 right, 6 wrong
false passes 3 of 6 wrong candidates; false fails 1 of 6 right ones
```

The last two lines are the check the baselines cannot make. Twelve candidate solutions, labelled right or wrong by hand, are scored by the three graders that passed: half the wrong ones get through (a config with the port set twice, a `slugify` that returns `"hello-world"` for every input, a wrong flag name that contains the right one), and one right one fails on a missing space. A grader that survives its baselines can still be too weak, and only labelled examples measure it.

At scale, UTBoost augmented the tests of SWE-bench instances and "identified 36 task instances with insufficient test cases and uncovered 345 erroneous patches" that the original graders had passed; the corrections changed 40.9% of SWE-bench Lite and 24.4% of SWE-bench Verified leaderboard entries, for 18 and 11 ranking changes (Yu et al., ACL 2025). A quarter of the entries on a flagship leaderboard were partly reporting the grader rather than the agent.

One operational hazard rounds the section out: every grader needs a **wall-clock and resource budget**, because a hung suite reports as a failure and blames the harness for an infrastructure problem, wrong in the direction that changes working code.

---

## 6. Sizing the set and scheduling the runs

"A fixed set, repeated a few times" is not a plan until it has dimensions, and those follow from arithmetic. Take the series' running example of a run, the twelve-iteration task of [post 03](../03-the-agent-loop/index.md) that re-reads 276,600 input tokens, at $3 per million input tokens, the Claude Sonnet 4.6 rate (Anthropic pricing page, consulted October 2026). Four minutes a run and 20 runs in parallel are illustrative. `snippets/sweep_plan.py` prices four cadences, the input side only ([post 23](../23-economics-haas/index.md) prices the whole run):

```text
one run: 276,600 input tokens at $3.00 per million = $0.83
cadence                             runs  machine-hours  wall-clock at 20-way  input spend
every harness diff: smoke subset       30            2.0                8 min       $24.89
nightly and every model upgrade       360           24.0               72 min      $298.73
at release: held-out split             90            6.0               20 min       $74.68
sized to call a 5.4-point lift      1,872          124.8              376 min    $1,553.39
```

By hand: 60 tasks at three seeds under two configurations is $60 \times 3 \times 2 = 360$ runs, $360 \times 0.83 \approx 299$ dollars, and $360 \times 4 = 1{,}440$ machine-minutes, 72 minutes at 20-way. The cost forces a cadence gradient rather than one setting for everything: a smoke subset on every diff, the full set nightly, the held-out split only at release.

The last row is the easiest to skip. The size of the set fixes the smallest lift it can detect, and the A/B of the next two sections needs about 312 tasks at three seeds to call a real 5.4-point lift four times in five. Twenty tasks is a smoke test, not an experiment, as [post 20](../20-sdk-landscape/index.md)'s small A/B showed when a true 6.2-point lift measured as 1.0. Choose the size from the effect that matters, then pay for it or accept that it cannot be seen.

---

## 7. A/B-testing a harness change

With the task set fixed, a harness change becomes a controlled experiment: change one component, hold everything else, run both configurations on identical tasks, and compare.

The variable is one harness component: a stop condition, a hook, a tool, a verification gate. The model is **held fixed**, because changing model and harness together teaches nothing about either, and so are the tasks and seeds. `snippets/ab_runner.py` is the experiment with stand-ins for the two arms: harness A runs each task once; harness B adds a verification gate that costs a check, catches three wrong results in ten, and earns one more attempt. Because the stand-ins are defined, B's true lift is known, which a real A/B never knows. The runner is the loop over tasks, configurations and seeds:

```python
def run(p, config, rng):
    """One run of a task under one harness config, with the model held fixed: (resolved, input tokens)."""
    ok, tokens = rng.random() < p, ATTEMPT
    if config["verify_gate"]:
        tokens += GATE
        if not ok and rng.random() < CATCH:      # the gate catches a wrong result: one more attempt
            ok, tokens = rng.random() < p, tokens + ATTEMPT
    return ok, tokens


# A/B two harness configs on one fixed task set, every task once per seed, the model held fixed.
def ab(tasks, seeds, salt="sweep-1"):
    rows = []
    for t, p in enumerate(tasks):                        # fixed, versioned, never edited
        row = {}
        for name, config in CONFIGS.items():
            runs = [run(p, config, random.Random(f"{salt}|{t}|{s}|{name}")) for s in range(seeds)]
            row[name] = (sum(ok for ok, _ in runs), sum(tokens for _, tokens in runs))
        rows.append(row)                                 # resolved of `seeds`, and tokens, per arm
    return rows
```

In a real runner, `run` calls the agent loop under the configuration and the task's grader scores the workspace; everything downstream is the same. The per-task rows matter as much as the aggregate. "B is two points better" can hide that B fixed five tasks and broke three, and only the row-by-row view shows which tasks each configuration won, which is where a team learns what the gate actually did. [Post 04](../04-harness-beats-model/index.md)'s tally of exactly that case is the skeleton this runner fills in.

Cost belongs in the verdict too. In the run below B's gate lifts resolved-rate by 6.7 points and costs $1.88 per resolved task against A's $1.78, at the token sizes above: a judgement, not a formula, and a comparison that reads only the rate gives half a verdict.

The same machinery runs in reverse. A model upgrade is an A/B with the roles swapped: hold the harness, change the model. A new model version can shift tool-call formatting or stop behaviour in ways no single-output eval catches, so the frozen set runs as a **regression gate on every model upgrade**: pin the version, and promote a new one only when the set holds or improves, enforced as a gate rather than a convention ([post 13](../13-hooks-enforcement/index.md)).

---

## 8. Knowing when a difference is real

Every number in an A/B is an estimate from a sample, so a verdict first has to say whether the difference could be noise. Two tools read the runner's rows. A **sign test** on the discordant tasks (those where the arms resolved different numbers of seeds) asks whether the split could be a coin flip; ties carry no direction and drop out. The **paired difference** takes B minus A per task, averages it, and puts a 95% interval on the mean:

```python
def sign_test(wins_a, wins_b):
    """Two-sided p-value on the discordant pairs: could this split be a coin flip?"""
    n, k = wins_a + wins_b, min(wins_a, wins_b)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0


def paired(rows, seeds):
    """The per-task paired differences, B minus A, and the mean lift with its 95% t interval."""
    d = [(r["B"][0] - r["A"][0]) / seeds for r in rows]
    lift, se = statistics.mean(d), statistics.stdev(d) / math.sqrt(len(d))
    half = t95(len(d) - 1) * se
    return d, lift, lift - half, lift + half
```

Run from the series root, the snippet prints in about six seconds:

```text
60 tasks x 3 seeds = 180 runs per arm; the model is held fixed
arm  resolved   rate   input tokens/run  cost/resolved
  A   84/180   46.7%           276,600  $1.78
  B   96/180   53.3%           335,017  $1.88
B-only wins 23, A-only wins 12, ties 25; sign test p = 0.09
measured lift +6.7 points; standard error 5.3 points with runs as independent, 4.4 paired by task
95% interval on the paired lift: -2.1 to +15.5 points (bootstrap -1.7 to +15.0)
true lift, from the stand-ins' definition: +5.4 points
verdict: not callable
sizing: detecting the true lift four times in five takes about 312 tasks at 3 seeds
called in B's favour over 200 fresh experiments: 60 tasks 26%, 312 tasks 81%
unpaired, 50 different tasks per arm near 50%: 95% interval +/- 19.6 points
one seed, 60 tasks, B-only 8 against A-only 4: lift +6.7 points, sign test p = 0.388; split 10 to 2: p = 0.039
```

The figure below draws the run. Read it in order:

- **The lift is real and not callable.** B is better by construction, by 5.4 points; 360 runs measured 6.7, and the paired interval runs from −2.1 to +15.5 points, crossing zero. The bootstrap over tasks agrees, and so does the sign test at $p = 0.09$. The verdict is "not callable": not that B is no better, but that this set cannot tell.
- **Pairing narrows the interval.** Treating the 360 runs as independent gives a standard error of 5.3 points; differencing each task against itself removes the task-difficulty variance and gives 4.4. The comparison only gets worse unpaired: two configurations run on 50 *different* tasks each, both near 50%, have an interval of about ±19.6 points ($1.96 \times \sqrt{2 \times 0.25 / 50}$), so no realistic harness change is visible at all. Miller's recommendation is the same, "We therefore recommend using the paired version of the standard error estimate wherever practicable", and he adds that when tasks come in related groups, "clustered standard errors can be over 3X larger than naive standard errors" (Miller, "Adding Error Bars to Evals", 2024), which matters for any set built from a few tasks per repository.
- **The set was too small before it ran.** At this spread about 312 tasks are needed to call the true lift four times in five, $n = ((1.96 + 0.84)\,s_d / \Delta)^2$ with $s_d$ the standard deviation of the per-task differences and $\Delta$ the lift to detect. Two hundred fresh 60-task experiments call it 26% of the time; 312-task experiments, 81%.
- **One seed makes it worse.** The last line works the case that gets shipped: on 60 tasks at one seed, B winning 8 tasks outright against A's 4 is a net of 4 tasks, a 6.7-point lift that reads like a win, and the sign test returns $p = 0.388$: a fair coin splits 12 that unevenly about two times in five. Split 10 to 2, the same twelve discordant tasks give $p = 0.039$. The headline lift reads the same in kind and the evidence does not.

![Two panels computed by the post's A/B snippet, illustrative. Left, sixty tasks binned by B's resolved fraction minus A's over three seeds, from minus one to plus one: 25 ties, 23 favour B and 12 favour A. Right, the measured lift of 6.7 points with its paired 95 percent interval from minus 2.1 to plus 15.5, crossing zero, the wider interval with runs treated as independent, and the true lift of 5.4 points; below, bars for how often fresh experiments call the lift: 26 percent at 60 tasks, 81 percent at 312.](diagrams/02-paired-lift.svg)

*A real 5.4-point lift, measured at 6.7 on sixty tasks, with an interval that still holds zero: the set, not the harness, decided the verdict.*

The rule is short. Report the lift, the discordant counts, and the paired interval; pair every comparison by construction; size the set before running it; and treat an unpaired A/B as untrustworthy rather than as weak evidence. A callable lift can still be too small to pay for, which is what the funnel is for.

---

## 9. Reading the trajectory, not only the outcome

The outcome eval says *whether* the harness got better. It never says *which component* made it better, and the next change depends on that. The trajectory metrics answer it, and they cost little to collect because [post 21](../21-observability-traces/index.md)'s spans already carry every field. Six are worth reporting beside the binary:

- **Iterations to resolution.** The distribution, not the mean. A gate that resolves the same tasks in nine turns instead of fourteen is an improvement the resolved-rate cannot see.
- **Tokens per resolved task.** The economic form of the same number, and the input to the funnel.
- **Tool-call error rate.** A rising rate is a tool-contract problem ([post 06](../06-tools-bash-code/index.md)), not a model problem.
- **Repeated identical tool calls.** The doom-loop signature of [post 05](../05-agent-failure-modes/index.md), visible in a sweep long before a user reports it.
- **Gate-fire counts.** A gate that never fires protects nothing; one that fires constantly is a symptom rather than a fix.
- **The distribution of stop reasons.** Runs ending at exit (1) `completed`, (2) `max_iters`, (3) `budget` and (4) `no_progress` in different proportions between two configurations show what changed even when the resolved-rate did not move.

Each is trivially gamed: "fewer steps" by giving up sooner, "fewer tokens" by not reading the file, "no gate fires" by removing the gate, so none may become a target of its own. The outcome decides; the trajectory explains.

---

## 10. Production metrics: the staged funnel

Benchmarks and internal evals are proxies run before shipping. Once a harness is live, the truth is in production metrics, and the useful ones are outcomes with money attached. Faros AI's "Harness engineering: A guide to building better AI coding agents" (22 May 2026) stages them: dollars per merged PR ("What each shipped PR costs in AI fees") comes from data a team already has, while first-pass success ("How often the agent solves a real implementation task on the first try") and defect escape ("How often bugs trace back to agent work") need agent sessions linked to pull requests, which Faros calls "the hardest piece of infrastructure to build". Arranged as a funnel, they read as three narrowing filters, drawn in the figure below:

- **First-pass success rate.** Of the runs attempted, the share accepted without rework: the internal eval's resolved-rate, measured on live traffic.
- **Defect-escape rate.** Of the results accepted, the share that later turned out wrong: a reverted PR, a reopened ticket, a regression downstream. A high first-pass rate with a high escape rate means plausible work that does not hold, worse than an honest failure.
- **Dollars per merged PR.** Spend divided by the units of work that shipped.

The claim worth testing is that a harness can win on resolved-rate and still be the worse system, and it becomes believable only with the arithmetic on the page. `snippets/funnel.py` runs one week, all figures illustrative, and adds the human time Faros's AI-fee figure leaves out, at a loaded $120 an hour: fifteen minutes to review an accepted result, five to triage a rejected one, and forty-five to redo a reverted one.

| One week, illustrative | Harness A | Harness B (heavier verification) |
|---|---|---|
| Runs attempted | 200 | 200 |
| Accepted without rework | 118 (59% first-pass) | 132 (66% first-pass) |
| Later reverted | 9 (7.6% escape) | 14 (10.6% escape) |
| Net shipped | 109 | 118 |
| Model spend, at $0.85 and $2.55 a run | $170 | $510 |
| Human review and rework | $5,170 | $5,900 |
| **Dollars per merged PR** | **$48.99** | **$54.32** |

![Three stages narrowing from runs attempted to results accepted to work shipped, with a purple gate between each, human review and the later revert, and one illustrative week of counts for two harnesses: A 200, 118 and 109; B 200, 132 and 118. Each gate carries its metric: first-pass success 59 against 66 percent, defect escape 7.6 against 10.6 percent. Dollars per merged pull request, model spend plus human time, close the funnel: A 48.99, B 54.32.](diagrams/03-production-funnel.svg)

*Each stage is a stricter filter, and each metric means something only relative to the stage above it.*

B wins the first-pass rate by seven points and loses the ledger by 10.9% per merged PR. Two things did it: the heavier verification tripled the model spend per run, and the extra accepted work carried a worse escape rate, so five more reverts cost 45 minutes each. `snippets/funnel.py` puts the result in one number: B's nine extra merges cost $118.89 each, more than twice A's average. Hold B's escape rate at A's 7.6%, ten reverts instead of fourteen, and it lands at $49.59 a merge, a tie rather than a win: the model spend alone cancelled a seven-point lift.

That is why defect escape keeps the funnel honest. The cheapest way to raise first-pass acceptance is work that looks right under review, and escape is the stage that catches it afterwards. An A/B predicts a lift; the funnel confirms whether it survived real traffic and was worth its cost. When the two disagree, the funnel wins, and the disagreement measures how far the eval set has drifted from the product.

---

## 11. Guarding against benchmark overfit

Every benchmark is a proxy, and every proxy invites Goodhart's law in Strathern's wording: "when a measure becomes a target, it ceases to be a good measure" (Strathern, 1997, restating Goodhart's 1975 observation). A harness tuned until it aces a benchmark may have learned that benchmark's quirks rather than gained general skill, and the failure is silent: the number keeps rising while real performance does not.

The standard defence is a **held-out split**: tune against a development split, touch an evaluation split rarely, never optimise on it, and report both. When the development split climbs and the held-out split does not follow, the harness has overfit, and the gap is the size of it. Three mechanics make that more than a principle:

- **Retire on inspection, not on a schedule.** A held-out task is spent the moment somebody reads it in a post-mortem, because looking at why it failed is optimisation whether or not anything changes. Rotate a fresh batch in, and expect the held-out line to step down when it arrives.
- **Plot the gap; do not read it once.** The development-minus-held-out gap tracked across tuning rounds shows a trend several rounds before either number looks wrong; a gap that widens round after round is overfit accumulating.
- **Split at scale when the stakes justify it.** SWE-Bench Pro keeps eleven public repositories, twelve held out and eighteen commercial ones whose problems are not public (Deng, Da, Pan et al., 2025), so the numbers people quote and the numbers that discriminate come from different sets by construction.

Overfit runs in two directions, and a held-out split defends against only one. The first is the agent learning the test: OpenAI's withdrawal of SWE-bench Verified documents a model drawing on release notes for a parameter its problem statement did not explicitly require. The second is a test too weak to tell, which UTBoost measured on the same family and which the grader checks exist to catch. Both look like progress.

So weight the metrics rather than averaging them: a production outcome outranks an internal eval, which outranks a public benchmark; a public task set may already sit in a model's training data; and a benchmark is calibration against the field, not the objective. The benchmark says a harness is in the game; only the funnel says it is winning. The eval set needs a named owner: a set nobody owns drifts from the product, invisibly until the funnel and the eval disagree.

---

## 12. Make it run

The plan's exercise for this post is to run the A/B runner over two harness configurations on one fixed task set with several seeds, compute the paired difference and its interval, and state whether the result is callable. The five snippets run offline from the series root with the standard library:

```bash
uv run python posts/22-evaluating-harnesses/snippets/ab_runner.py
uv run python posts/22-evaluating-harnesses/snippets/pass_family.py
uv run python posts/22-evaluating-harnesses/snippets/grader_check.py
uv run python posts/22-evaluating-harnesses/snippets/sweep_plan.py
uv run python posts/22-evaluating-harnesses/snippets/funnel.py
```

`ab_runner.py` is the exercise and prints the output quoted in the significance section in about six seconds; the others print what their sections quote in under a second. To try variations: set `SEEDS = 10` in `ab_runner.py` and watch the paired interval narrow on the same sixty tasks; set `CATCH = 0.5` and the true lift grows to 9.0 points, which this run calls but only 60% of fresh 60-task experiments would; and in `grader_check.py`, tighten the `set-port` grader to read the last `port` line and watch one false pass disappear.

---

## 13. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A grader that greps the transcript.** The agent writes "all tests pass" in its last message, the grader matches it, and the resolved-rate climbs while the suite in the workspace is red.
- **A task added without its baselines.** A new task's fixture already satisfies the grader; every configuration resolves it, and it dilutes every lift on the set until someone runs the empty agent.
- **A lift announced from one seed.** B beats A by seven points on sixty tasks; next week's run of the same two configurations shows the opposite sign, and nobody can say which harness is better.
- **The model upgraded mid-experiment.** The provider alias moves to a new version between the A and B sweeps, and the measured lift is partly the model's.
- **A held-out task read in a post-mortem and kept.** The team fixes the failure it showed; the held-out score rises and no longer measures generalisation.
- **A `pass@8` in the launch note.** The figure assumed eight attempts and a picker; users get one attempt and a `pass@1` the note never mentioned.

---

## Common pitfalls

1. **Scoring the final output of a run.** A harness is a trajectory; grading only its last message misses the recovery, the loops and the stop. Grade the world the run left, and read the trajectory beside it.
2. **Trusting a grader nobody tested.** An empty agent that passes a task, an oracle that fails one, or a grader that disagrees with itself means the number is measuring the grader.
3. **Changing the model and the harness together.** With two variables moving, the A/B teaches nothing about either; pin the model version for the length of the experiment.
4. **Shipping on an unpaired or unsized difference.** A 6.7-point lift on sixty tasks can sit inside an interval that holds zero; pair by task, size the set for the lift that matters, and say "not callable" when the interval crosses zero.
5. **Resolved-rate without cost.** A lift that triples the model spend can raise the dollars per merged PR; the verdict is always outcome against cost.
6. **Optimising on the held-out split.** Tuning against it measures memorisation, not generalisation, and a task read in a post-mortem is already spent.

---

## Further reading

- C. E. Jimenez, J. Yang, et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (ICLR 2024): 2,294 issues from twelve Python repositories, and the FAIL_TO_PASS plus PASS_TO_PASS grading contract.
- OpenAI, "Introducing SWE-bench Verified" (13 August 2024): the 500-instance subset screened by expert engineers, and what they found wrong with the originals.
- OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities" (23 February 2026): the saturation and contamination case for retiring it.
- X. Deng, J. Da, E. Pan, et al., "SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?" (arXiv, 2025): 1,865 problems over 41 repositories, split public, held-out and commercial.
- B. Yu, Y. Zhu, P. He, D. Kang, "UTBoost: Rigorous Evaluation of Coding Agents on SWE-Bench" (ACL 2025): what a grader too weak to catch a wrong patch does to a leaderboard.
- S. Yao, N. Shinn, P. Razavi, K. Narasimhan, "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" (arXiv, 2024): `pass^k` and its unbiased estimator.
- M. Chen et al., "Evaluating Large Language Models Trained on Code" (arXiv, 2021): the unbiased `pass@k` estimator.
- E. Miller, "Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations" (arXiv, 2024): paired standard errors, clustered standard errors, and power analysis for eval sets.
- Terminal-Bench, version 2.0 (Stanford University and the Laude Institute, 7 November 2025) and 2.1 (6 May 2026): 89 containerised tasks under Harbor, and the leaderboard that pairs an agent with a model.
- J. Yang, C. E. Jimenez, et al., "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" (NeurIPS 2024): how much the interface around a fixed model moves resolved-rate.
- V. Trivedy, "Improving Deep Agents with harness engineering" (LangChain blog, 17 February 2026): the harness-only A/B on Terminal-Bench 2.0 that this post's method generalises.
- Faros AI, "Harness engineering: A guide to building better AI coding agents" (22 May 2026): the staged production metrics.
- M. Strathern, "'Improving ratings': audit in the British University system" (*European Review*, 1997): the formulation of Goodhart's law this post uses.
- `ctx-020`, "Evaluation": the four-tier pyramid and the judge's failure modes, the output-eval companion to this view.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 23 - The economics of a harness and Harness-as-a-Service](../23-economics-haas/index.md):** the dollars per merged PR of the funnel become a full cost model, and cost per successful run the number that decides.
- **[Post 26 - Capstone: a long-running, trusted coding-agent harness](../26-capstone-coding-agent/index.md):** a coding agent built, traced and A/B-tested with the model held fixed, by this post's method.
