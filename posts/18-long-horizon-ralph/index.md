# 18 · Long-horizon & multi-context execution — Ralph loops and context bridging

> **TL;DR.** Some tasks are bigger than any single context window, no matter how well you manage it. The answer is not a bigger window but the **Ralph loop**: reset to a fresh context against a written spec, do one task, commit, and repeat, with all the state living on disk. The spec is the source of truth and the window is disposable, so progress accumulates in the repository while each context stays small. Convergence is judged by an acceptance gate rather than by the agent's own report, and the loop needs a stop condition or it never ends.
>
> **After reading this you will be able to:**
> - Recognise when a task has outgrown one context window rather than one agent.
> - Run a Ralph loop: fresh context, one task, commit, repeat against a spec.
> - Bridge context across resets with a spec and a handoff file, and price the reset.
> - Size an iteration to one verifiable increment, and keep the goalposts out of the agent's reach.

![Across the top, the three things on disk that survive every reset: the human-owned spec, the handoff the loop writes, and the repository behind a gate, with the window itself marked disposable. Below, the cycle: a fresh context reads spec and handoff, does one task, verifies and commits one increment, then resets, discarding the window and carrying nothing. Three panels close it: the literal shell form of the loop, which has no state, no iteration count and no convergence check; the guards that make it safe to leave running, a max_iters hard cap, a stale cap of three iterations with no new commit, and a check that the spec has not moved; and the reported record, a $50,000 contract delivered for about $297 of inference, marked as the technique author's own account rather than a benchmark.](diagrams/01-ralph-loop.svg)
*The window is disposable; the spec on disk is the source of truth. Repeat until the spec is satisfied.*

---

## 1. Work that outgrows one window

[Post 17](../17-parallel-agents-shared-repo/index.md) handled work that was too *much* for one agent. This post handles work that is too *big* for one context: building a whole project, a refactor that touches hundreds of files, a task whose full state simply will not fit in a window however carefully you compact it ([Post 09](../09-context-management-loop/index.md)).

Trying to hold such a task in one long-running context fails predictably. The window fills, context rot sets in, and the agent starts cutting corners as it runs low on room, which is context anxiety ([Post 05](../05-agent-failure-modes/index.md)).

The obvious reply is to wait for a larger window. It does not settle the question, because the horizon moves with the hardware. METR's measurement of task length puts a number on the movement: the duration of software task a frontier model completes with 50% reliability has been doubling roughly every seven months since 2019 (Kwa et al., 2025). Ambition tracks capability, so the jobs people hand an agent grow at about the rate the windows do, and the ratio that actually matters, task size over window size, stays stubbornly near one.

The cheaper fixes also run out before the hard cases do, and that is a reported finding rather than a prediction. Anthropic's account of building long-running agents states plainly that compaction on its own is not sufficient at this length, and that even a frontier coding model looping across multiple context windows on high-level prompts alone falls short (Anthropic, 2025). [Post 09](../09-context-management-loop/index.md) built a ladder for a filling window: offload, then clear, then compact, then reset. This post starts on the last rung and asks what an architecture looks like when the reset is not an emergency measure but the ordinary thing that happens between every unit of work.

---

## 2. The Ralph loop

That architecture has a name. The **Ralph loop** runs the same prompt against a written spec, lets the agent do *one* task in a fresh context, commits the result, wipes the context, and repeats (Huntley, 2025). The spec on disk is the source of truth; the window is a scratchpad thrown away every iteration.

The name is Ralph Wiggum, from *The Simpsons*, and the joke carries the argument. Huntley's own framing is that "the technique is deterministically bad in an undeterministic world" (Huntley, 2025). The loop makes no attempt to be clever about where it is or what it learned last time, because it threw both away. What it has instead is a written spec and a repository, and it re-reads them every time. The honest description of the method is brute force plus persistence, and the reason to take it seriously is that it has met real work: Huntley reports delivering a $50,000 contract as a tested and reviewed minimum viable product for roughly $297 of inference (Huntley, 2025). That is one reported outcome from the technique's author rather than a benchmark, and it is worth reading as one.

Its canonical form is a single line of shell, and it is worth seeing before any abstraction is laid over it:

```bash
while :; do cat PROMPT.md | claude-code ; done
```

There is no state in that command, no iteration count, no convergence check, and no stop condition. Everything that makes it work sits in `PROMPT.md`, in the repository it runs against, and in the fact that the agent process exits and starts again. Everything that follows in this post is the set of guards you add once you point that loop at work you care about.

Written out, the driver is still small, because all the state is external:

```python
def ralph(read_spec, run_one_task, converged, *, max_iters=50):
    """One task per fresh context against a spec on disk; commit; repeat."""
    for i in range(1, max_iters + 1):
        spec = read_spec()        # source of truth, re-read into a clean window
        run_one_task(spec)        # a FRESH context does the next piece, then commits
        if converged():           # the acceptance gate, not the agent's self-report
            return i
        # the context is discarded here; only the repo and the spec persist
    raise RuntimeError(f"did not converge in {max_iters} iterations")
```

Nothing in the loop remembers anything between iterations, and that is the point. Each pass starts clean, reads the current state from disk, advances it by one task, and writes it back. The agent's memory is the repository, not the window. Note the shape of `converged`: it takes no argument at all. It is a function of the *work*, not of the spec's account of itself, and section 8 is about why that distinction is load-bearing.

![One iteration's context stacked stable-first: system prompt, spec, handoff, repository state, and this iteration's work, with the first two tagged cached and bracketed as the prefix, beside a panel sizing a task against the window limit and a panel on which files the loop may edit.](diagrams/03-inside-one-iteration.svg)
*One iteration, opened up. The left-hand stack is section 4, the sizing panel is section 3, and the permissions panel is section 6.*

---

## 3. Sizing one task, and the re-entry tax

The driver above is barely a dozen lines. Deciding what goes in `run_one_task` is where the design actually lives, because every iteration pays a **fixed cost** before it does anything useful: read the spec, read the handoff, orient in the repository. Call that the re-entry tax, and split it in two, because the halves behave nothing alike.

The **frozen half** is the system prompt and the spec. It is byte-identical on every iteration, so it can be served from a prompt cache at roughly a tenth of the input price. Section 4 is about the conditions under which that actually happens, because they are narrower than they look.

The **volatile half** is orientation in a repository that just changed: the version history, the handoff file, the current state of the files the next task touches, the last test run. None of it caches, because none of it is the same twice.

Slice too **large** and the iteration overflows its window, which is the problem you were solving. Slice too **small** and the volatile half dominates. An iteration that burns four thousand uncacheable tokens working out where the repository is in order to change one line is mostly overhead, and a hundred such iterations is a hundred repeats of that cost with nothing amortising it. The frozen half is not what makes an over-small slice wasteful; re-reading a cached spec is nearly free. Re-orienting in a repository that moved is not.

The workable heuristic is to size a task to **one verifiable increment**: the smallest change that leaves the repository in a state where the tests can say yes or no. That definition does the work because it is the same boundary the commit and the verification gate already use, so the loop, the version history, and the check all agree on what a unit of progress is. Section 9 gives the same rule a second job.

---

## 4. Keeping the reset cheap: the frozen prefix and the cache clock

A Ralph loop rebuilds its context from scratch fifty times, which sounds ruinous. Two decisions settle whether it is, and most designs make the first and skip the second.

The first is ordering. If each iteration assembles its context **stable first, volatile last** (system prompt, then spec, then handoff, then current repository state) the leading portion is byte-identical across iterations and can be served from the provider's prompt cache rather than paid for in full. This is the Context Engineering series' "freeze the prefix" rule (Context Engineering, Post 05) applied to an architecture that would otherwise look like its worst case. Put the volatile handoff above the fixed spec and you invalidate the prefix on every iteration, turning a cheap reset into an expensive one for no benefit.

The second decision is the one the design usually fails on, because ordering is necessary and not sufficient. A cached entry has a lifetime, and the clock runs from the *start* of the request that writes or reads it, so the model's own generation time counts against it (Anthropic, "Prompt caching", 2025; [Post 23](../23-economics-haas/index.md) §4). The default lifetime is five minutes. A Ralph iteration that writes a feature and runs a test suite routinely takes longer than that, which means a perfectly ordered prefix is stone cold on the next iteration, and every reset pays the write premium with no read to amortise it.

Price it out. Take a frozen prefix of 12,000 tokens over 50 iterations, at the mid-tier rate the sibling series uses ($3 per million input tokens), with cache reads at about 0.1x that rate, five-minute writes at 1.25x, and one-hour writes at 2x (Anthropic, "Prompt caching", 2025):

| Iteration cadence | Cache tier | Writes | Reads | Prefix cost over 50 iterations |
|---|---|---|---|---|
| any | none configured | n/a | n/a | $1.80 |
| under 5 minutes apart | five-minute (default) | 1 × $0.045 | 49 × $0.0036 | **$0.22** |
| about 8 minutes apart | five-minute (default) | 50 × $0.045 | none | **$2.25** |
| about 8 minutes apart | one-hour | 1 × $0.072 | 49 × $0.0036 | **$0.25** |

The third row is the finding. A loop whose iterations run eight minutes apart on the default tier pays about 25% *more* for its frozen prefix than a loop with no caching configured at all, and every part of that loop looks correctly designed from the inside. Nothing in the trace says "cache miss"; the bill simply arrives.

The rule is therefore two-part: order the prefix stable first, then choose the cache lifetime from the iteration's wall-clock length rather than from the number of iterations. If iterations finish in well under five minutes, the default tier is strictly cheaper and refreshes itself on every read. If they run longer, either buy the longer lifetime or keep the entry warm with a cheap read while the iteration is still working. The iteration count tells you how much the decision is worth; only the clock tells you which way it goes.

---

## 5. Context bridging: the spec and the handoff

For the loop to work, everything an iteration needs must survive the reset, on disk. Two artefacts carry it:

- **The spec** is the fixed source of truth: what to build, the acceptance criteria, the constraints. It is written once and read into every fresh context.
- **The handoff file** ([Post 08](../08-state-filesystem-git/index.md)) is the moving state: what is done, what is next, any decisions made along the way. Each iteration updates it, so the next fresh context can tell where it is without re-deriving the whole history.

Together they are the **context bridge**. A fresh window is not starting from nothing; it reads the spec to know the goal, and the handoff plus the repository to know the current position. The quality of these two files decides how cheaply a new context re-enters the work. A vague spec or a thin handoff forces each iteration to rediscover context and drift, which is exactly what the loop is supposed to prevent.

The split is stable enough that independent practitioners arrive at the same two files under different names. Osmani's survey of long-running agents describes a plan file (`prd.json`) alongside a rolling record of what happened (`progress.txt`), which is this separation with the labels changed (Osmani, 2026). Anthropic's reference harness calls them `feature_list.json` and `claude-progress.txt` (Anthropic, 2025). One file is the contract and the other is the lab notebook. Keeping them apart is what makes the next section's rule expressible at all: you cannot grant two different write permissions to two things stored in one file.

---

## 6. Who may write to the spec

This is the question that decides whether a Ralph loop converges on what you asked for or on something else, and it is easy to get wrong by being helpful.

The spec is the only thing in the system that says what "done" means. If the agent may rewrite it, then an iteration that cannot satisfy a requirement has a second way out: change the requirement. Nothing about that is malicious. An agent asked to make the spec and the code agree will quite reasonably edit whichever is easier. The effect, though, is that the loop marks its own homework, and the convergence check starts returning true against a spec that has quietly drifted toward whatever got built.

The rule is not "the agent may never touch the spec", because a machine-readable spec is also the progress ledger, and something has to record that a criterion now holds. The rule is a **narrow write channel**: the loop may flip exactly one field per criterion, the pass bit, and nothing else. What "done" *means* stays human-owned. Anthropic's harness implements precisely this, prompting coding agents "to edit this file only by changing the status of a `passes` field", reinforced with the blunt instruction that "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality" (Anthropic, 2025).

The file format is a soft guardrail in its own right, and the reasoning behind it is worth borrowing. Anthropic chose JavaScript Object Notation (JSON) for the feature list rather than Markdown because "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files" (Anthropic, 2025). A structured file with an explicit schema resists casual rewriting in a way a prose document does not: changing one field of one record is a local, deliberate act, whereas a Markdown spec invites exactly the fluent rewriting the model applies to every other document it edits.

Written out, the permissions look like this, and the table is worth keeping because every row has a different enforcement mechanism and only one of them is a rule in a prompt:

| Artefact | Who writes | Who reads | What enforces it |
|---|---|---|---|
| Spec criteria (what "done" means) | a human, between runs | every iteration | structural diff across the iteration; the driver stops if a criterion moved |
| The pass bit on each criterion | the loop, one field per criterion | the driver's progress report | the same structural diff: only that field may differ |
| Handoff / progress file | the loop, freely | the next iteration | nothing; it is a log, and a bad entry costs one iteration |
| Repository source | the loop, freely | the loop and the gate | the commit plus the acceptance gate ([Post 11](../11-verification-loops/index.md)) |
| Tests | the loop may add, never edit or delete | the gate | a pre-commit hook rejecting a diff that removes an assertion ([Post 13](../13-hooks-enforcement/index.md)) |

The first two rows are one deterministic check, and that is the reason to prefer a structural diff over a hash of the whole file. Hashing the bytes forbids the pass bit too, so the guard fires on every honest iteration and the loop can never record progress. Diff the criteria and leave the bit alone; the driver in section 8 shows the check.

Specs do need to change: requirements were wrong, or something turned out impossible. Route that through the handoff. An iteration that cannot satisfy a criterion writes down why and stops, a human amends the spec, and the loop restarts. You lose a little autonomy and keep the property that makes the whole architecture trustworthy, which is that the goalposts sit somewhere the runner cannot reach ([Post 15](../15-human-in-the-loop/index.md)).

---

## 7. A reference design for a multi-context build

Putting it together gives a way to build something larger than a window, and there is a documented instance to copy from rather than a sketch. Anthropic's long-running harness builds a working clone of the claude.ai web application across many context windows, and it uses exactly the vocabulary above (Anthropic, 2025).

An **initialiser agent** runs once, before the loop starts. It expands a short product prompt into three things: a machine-readable spec, over 200 features for that build, each one starting out unsatisfied; an `init.sh` that later sessions run on boot to bring the environment up; and a progress file. One feature looks roughly like this:

```json
{"features": [
  {"id": "auth-001",
   "title": "A signed-out visitor can create an account with email and password",
   "acceptance": "Sign up, confirm the address, land on the conversation list.",
   "priority": 1,
   "passes": false}
]}
```

Every subsequent **coding-agent** session then runs the same re-entry ritual: work out where it is, read the version history and the progress file, pick the highest-priority incomplete feature, build that one feature, verify it, commit, and update the progress file. Then the context is discarded and the next session starts the ritual over.

Two things in that design are easy to skim past and both are load-bearing. The first is that the decomposition is paid **once**, in a session that is not part of the loop. Turning a paragraph of product intent into 200 acceptance criteria is expensive, and doing it inside the loop would mean re-deriving it fifty times; doing it before the loop is exactly what keeps the per-iteration re-entry tax as small as section 3 claims it can be. The second is that the spec is machine-readable, which turns an abstract "is it done?" into something countable: features passing over features total, a number the driver can log every iteration and a human can read at a glance.

![An upper chart of context used inside one window: eight sawtooth teeth, each filling as a task runs and dropping to the frozen prefix at the reset, against a straight dashed climb representing a single unmanaged context that crosses the window limit and overflows. A lower chart shows progress on disk as a staircase that only ever rises, one commit per verifiable increment, capped by the driver at fifty iterations. Below them, what the reset costs: a table pricing a 12,000-token frozen prefix over fifty iterations at $3 per million input tokens, comparing no cache at $1.80 against a five-minute cache tier at $0.22 when iterations run under five minutes apart and $2.25 when they run about eight minutes apart, and a one-hour tier at $0.25.](diagrams/02-multi-context-timeline.svg)
*A single context climbs into overflow; the Ralph loop keeps each window small while the build grows on disk.*

> One tooth of that sawtooth, [animated](../../assets/animations/02-context-reset.svg): the window fills, everything in it goes at once rather than draining, and the only thing that crosses the boundary is the file.

Two curves come out of that arrangement. Context usage is a **sawtooth**, rising within an iteration and dropping to the baseline at each reset, always bounded below the window limit; progress is a **staircase**, rising monotonically as commits accumulate. A single unbounded context climbs straight into overflow instead. The Ralph loop trades the comfort of one continuous context for the ability to run arbitrarily long.

### The gate underneath the staircase has to be end to end

The staircase is only as honest as the gate beneath it, and this is where the reference design paid for its experience. Anthropic found that the agent would make code changes and test them with unit tests or `curl` commands while failing to notice that the feature did not work end to end, and fixed it by moving the gate to browser automation that exercises each feature the way a human user would (Anthropic, 2025).

The consequence is specific to this architecture. In a single session, a feature that passes its unit tests and does not work is caught by whoever is watching. In a Ralph loop nobody is watching: the pass bit flips, the commit lands, the staircase steps up, and the next fresh context reads a progress file that says the feature is done. Fifty iterations later there is a monotone progress curve over a product that does not run. That is victory declaration ([Post 05](../05-agent-failure-modes/index.md)) laundered through fifty commits, and it is far harder to spot than the single-session version because every individual step looks like progress. Whatever the acceptance gate is ([Post 11](../11-verification-loops/index.md)), on this architecture it has to exercise the feature the way the user will, not the way the code does.

---

## 8. Convergence, stopping, and the guards that enforce it

A loop that resets forever needs a clear answer to "when is it done?", and the spec provides it: all acceptance criteria met. What matters is *who says so*. Convergence is measured by running the criteria, not by reading the spec's own account of itself, and that is why `converged()` in section 2 takes no argument. The pass bits orient the next iteration and feed the progress report; the stop condition runs the gate.

Three ways the loop fails need guarding, and all three become cheap the moment each iteration commits.

The loop might **never converge**, so it carries a hard iteration cap (stop condition ②) and a no-progress detector (stop condition ④) from [Post 03](../03-the-agent-loop/index.md)'s four stop conditions. "No new progress" needs a definition, and in a loop that commits once per task the definition is already on disk: no new commit. The version history *is* the progress record, so the detector reads the current commit rather than trying to infer momentum from a transcript that was thrown away at the last reset.

It might **thrash**, redoing or undoing work. The same commit-per-iteration discipline makes that visible: a thrashing loop produces commits that alternate rather than accumulate, and a diff against the commit two back says so in one command.

And it might **move the goalposts**, which section 6 covered and which is checked the same way: capture the criteria before the iteration, compare after, and stop if anything other than a pass bit moved.

All three fit in one driver, and it is short enough to keep in front of you:

```python
import json, pathlib, subprocess

SPEC = pathlib.Path("spec/feature_list.json")

def criteria(spec):
    """Everything in the spec except the one field an iteration may flip."""
    return {f["id"]: {k: v for k, v in f.items() if k != "passes"}
            for f in json.loads(spec.read_text())["features"]}

def head():
    out = subprocess.run(["git", "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip()

def converged():
    """The acceptance gate, run here rather than trusted from the spec."""
    return subprocess.run(["./acceptance.sh"]).returncode == 0

def ralph(*, max_iters=50, stale_cap=3):
    stale = 0
    for i in range(1, max_iters + 1):
        goalposts, before = criteria(SPEC), head()
        subprocess.run(["agent", "--prompt", "PROMPT.md"])   # a fresh context
        if criteria(SPEC) != goalposts:
            return i, "spec-moved"       # the loop rewrote what done means
        if converged():
            return i, "converged"
        stale = stale + 1 if head() == before else 0
        if stale >= stale_cap:
            return i, "no-progress"
    return max_iters, "max-iters"
```

Two details there are worth naming. `subprocess.run` is where the reset physically happens: the fresh context is a fresh process, so no state can leak between iterations even by accident, and the reset becomes something visible in the code rather than a comment claiming it. And `spec-moved` is a return value rather than an exception, because it is a legitimate outcome that needs a human rather than a crash. It converts a subtle correctness problem into a loud one, which is the same move a deterministic hook makes ([Post 13](../13-hooks-enforcement/index.md)).

The same shape, with planning, a ratchet, cost metering and tracing wired in, is what the capstone builds: [`code/26-coding-agent/src/coding_agent/driver.py`](../../code/26-coding-agent/src/coding_agent/driver.py) is the version that runs.

---

## 9. After convergence: who reviews fifty commits

The loop stopping is not the work finishing. A converged Ralph run hands a human a body of work built over hours without supervision, and somebody has to accept it. Osmani names the problem plainly: "Auditing 24 hours of autonomous activity is a real human-time problem" (Osmani, 2026). It is the cost the architecture creates in exchange for the autonomy it buys, and it appears nowhere in the token bill.

The only thing that makes it tractable is the shape the loop already produces. One commit per verifiable increment, each attached to the spec criterion it satisfies, is a review *series* rather than a review *endpoint*. A reviewer can walk it in the order it was built, stop at the first commit that looks wrong, and know that everything before it cleared the same gate. Against the alternative, one enormous diff with no internal structure, that is the difference between an afternoon and a week.

This gives section 3's sizing rule a second and independent justification. A slice is not only the unit the window can hold and the unit the gate can judge; it is also the unit a human can review in one sitting. If a slice is too large to review, it is too large, whatever the window says. And it shifts the human-in-the-loop question ([Post 15](../15-human-in-the-loop/index.md)) on this architecture away from "which actions need approval" and toward "what shape must the finished work arrive in", which is a design decision taken before the loop starts rather than an interruption during it.

---

## 10. Where this overlaps planner and evaluator

The Ralph loop rarely runs a bare generator. Each iteration usually contains the three roles of [Post 12](../12-planner-generator-evaluator/index.md): a planner decides *which* task is next from the spec and the current state, a generator does it, and an evaluator checks whether the iteration made real progress and whether the criteria now hold. The reset is what keeps those roles cheap, because each runs in a clean window rather than a bloated one, and it is also what keeps the evaluator honest, since an evaluator sharing a context with the generator has already read the generator's reasoning and tends to agree with it.

Seen this way, the Ralph loop is the outer loop and the planner/generator/evaluator pass is the inner one, which is precisely the composition that [Post 19](../19-loop-engineering/index.md) is about: designing the loop that drives the agent, rather than prompting each step by hand. Both loops end up in the same machine in [Post 26](../26-capstone-coding-agent/index.md), where this driver runs the build.

---

## Common pitfalls

- **Slicing iterations by feel.** Too large overflows the window; too small pays the uncacheable half of the re-entry tax over and over. Size to one verifiable increment (§3).
- **Keeping state in the window.** Anything not written to disk is lost at the reset. The spec, the handoff and the repository are the memory (§2, §5).
- **Letting the agent edit what "done" means.** An agent that can move the goalposts will satisfy the convergence check by rewriting it. Criteria human-owned, pass bit loop-owned, handoff loop-owned (§6).
- **Hashing the whole spec rather than diffing its criteria.** A whole-file hash forbids the pass bit too, so the guard fires on every honest iteration. Diff the criteria and leave the bit alone (§6, §8).
- **Choosing the cache tier from the iteration count.** The entry's lifetime runs from the request's start, so an eight-minute iteration on the default tier pays the write premium fifty times and never once reads (§4).
- **A unit-test gate on a long-horizon build.** Fifty green commits over a product that does not run is victory declaration with nobody present to catch it. The gate has to be end to end (§7).
- **No convergence check and no no-progress detector.** Without an acceptance gate, an iteration cap and a stale-commit counter, the loop runs until the budget does (§8).

---

## Further reading

- Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'" (2025): the plain loop against a spec with a fresh context each iteration, its canonical one-line form, and one reported delivery.
- Anthropic, "Effective harnesses for long-running agents" (2025): the initialiser and coding-agent split, the three on-disk artefacts, the pass-bit write rule, and the end-to-end verification finding.
- Addy Osmani, "Long-running Agents" (2026): the plan-file and progress-file split, and the human cost of auditing a long autonomous run.
- Kwa, T. et al., "Measuring AI Ability to Complete Long Software Tasks" (METR, 2025): the doubling time of the task length a frontier model completes at 50% reliability.
- Anthropic, "Prompt caching" documentation (2025): the read and write multipliers and the two lifetime tiers this loop's reset economics turn on.
- Context Engineering, Post 05: the economics of a cached stable prefix at the single-call level, the token-side companion to this run-level view.
- awesome-harness-engineering (2026): the Agent Loop and state-persistence sections.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 19 — Loop engineering](../19-loop-engineering/index.md)**: designing the loop that drives the agent, of which the Ralph loop is one shape.
- **[Post 26 — Capstone: a long-running coding-agent harness](../26-capstone-coding-agent/index.md)**: where this driver is built for real, alongside the planner and evaluator roles, the ratchet, and cost guardrails.
- **[Post 09 — Context management inside the loop](../09-context-management-loop/index.md)**: the reset move this post turns into an architecture.
- **[Post 12 — Planner / generator / evaluator](../12-planner-generator-evaluator/index.md)**: the roles that usually run inside each Ralph iteration.
