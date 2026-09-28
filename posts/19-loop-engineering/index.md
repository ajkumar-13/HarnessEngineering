# 19 · Loop engineering — designing the loop that prompts the agent

> **TL;DR.** The 2026 shift is from *prompting the agent* to *designing the loop that prompts it for you*. A well-engineered loop carries **layered exits** so it stops for the right reason: the verifier confirms the goal, or a hard iteration cap, a token/time budget, or no-progress detection catches it first. A bare `while not done` loop has only one of these and trusts the model's word for it. Loop engineering also composes loops (an inner verify loop inside an outer task loop), treats a failed call as a retry rather than an exit, and puts a hard ceiling on runaway spend.
>
> **After reading this you will be able to:**
> - Move from writing prompts to designing the loop and its exit conditions.
> - Give a loop four layered exits, one intended and three guards, and say what each must leave behind.
> - Enforce a budget before the call that would breach it, and make every guard exit resumable.
> - Compose an inner verification loop inside an outer task loop, and allocate one budget across both.

![On the left, the loop and the bare `while not model_says_done()` it replaces, which has one exit and the worst one. In the centre, the four exits checked in order after every turn, each with what makes it fire, what it means and what it leaves behind: the verifier confirming the goal against ground truth, a hard max-iterations cap at 12, a token or wall-clock budget of 200,000, and no-progress detection over a 3-repeat window. On the right, the stop, naming which of the four reasons returned so the run is debuggable. A panel records that the cap and the stall window are the loop companion's defaults in code/03-agent-loop.](diagrams/01-layered-exits.svg)
*Design the loop, not each prompt: layered exits so it stops for the right reason, not by luck.*

---

## 1. Stop prompting, design the loop

For most of the field's history, "using a large language model (LLM) well" meant writing a better prompt. The 2026 reframe is that once a model runs in a loop, the leverage moves from the prompt to the **loop itself** (Osmani, 2026). You are no longer prompting the agent at each step; you are designing the machine that prompts it for you, over and over, until it is done. That machine is what this whole series has been building, and **loop engineering** is the discipline of designing its control flow.

The line that carried the reframe is Peter Steinberger's: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents" (quoted in Osmani, 2026). Boris Cherny, who leads Claude Code at Anthropic, describes his own working day in the same terms: "I don't prompt Claude anymore. I have loops running that prompt Claude and figuring out what to do. My job is to write loops" (quoted in Osmani, 2026). Neither is a claim about model capability. Both are claims about where a practitioner's attention goes once the model is good enough to be driven rather than steered, and the answer is that it goes into the driver.

One difference is worth naming rather than glossing over. Osmani places loop engineering one floor *above* agent harness engineering: the harness is the thing that runs, and the loop is what runs it on a timer, spawns helpers, and feeds it work (Osmani, 2026). This series places it inside instead. The loop is the harness's control flow, the wiring between the eleven components rather than a storey above them ([Post 02](../02-anatomy-of-a-harness/index.md)), because every exit designed here is enforced by the same runtime that dispatches the tools and applies the hooks. Nothing about the practice changes; where you file it decides who owns the exits, and here that owner is the harness.

In practice the reframe means the interesting decisions are no longer wording but structure: when does the loop act, what does it feed back, and above all *when does it stop*. [Post 03](../03-the-agent-loop/index.md) §7 argued that the agent failures practitioners name most often are exits gone wrong rather than reasoning gone wrong; loop engineering is taking that seriously and designing the stopping deliberately.

---

## 2. Layered exits

A loop needs more than one way out, and the ways out should be layered rather than pooled. Four of them cover the loop's *internal* stopping (tosea.ai, 2026):

- **① The verifier confirms the goal.** The intended exit: a check against ground truth says the work is done ([Post 11](../11-verification-loops/index.md)). This is the only exit that means success.
- **② A hard max-iterations cap.** The infinite-loop backstop, so the loop cannot run forever even if nothing else fires.
- **③ A token or time budget.** The cost ceiling, so a run cannot spend past what you allow, provided the check happens *before* the spend rather than after it (§4).
- **④ No-progress detection.** The thrashing guard, which stops a doom loop ([Post 05](../05-agent-failure-modes/index.md)) when successive iterations stop changing anything.

The layering buys two things. The first is a split: one of the four is the intended exit and the other three are guards, so a run that exits on ②, ③ or ④ did not finish and is a run you need to look at. The second is one ordering that genuinely matters. Check the goal first, so a run that has just succeeded is not cut off by a guard it was about to satisfy. Between the three guards the order is close to arbitrary, and exit ② is usually not a check at all: it is the bound on the `for` statement, reached structurally once everything else has failed to fire.

These are also only the exits the loop can reach on its own. A run can be stopped from outside it too: a human interrupting mid-flight to steer it ([Post 15](../15-human-in-the-loop/index.md) §6), or an approval request that nobody answers before its timeout expires ([Post 15](../15-human-in-the-loop/index.md) §8). Those belong to the human-oversight surface rather than to the loop's own control flow, and a third candidate, an unrecoverable provider error, turns out not to be an exit at all (§6).

The exits differ in what they mean, and they differ more in what they oblige the loop to leave behind:

| Exit | What fires it | What it means | What the run must leave behind |
|---|---|---|---|
| ① verified goal | a check against ground truth passes ([Post 11](../11-verification-loops/index.md)) | success, and the only exit that does | the result |
| ② iteration cap | the loop's turn bound is exhausted | did not converge in the turns allowed | the result so far, plus a resumable position (§8) |
| ③ budget | the next call would cross the ceiling (§4) | ran out of what the task was worth | the same, plus the spend to date |
| ④ no-progress | the chosen stall signal repeats (§5) | busy without moving | the same, plus the repeating signature |

Those numbers have to come from somewhere, and none of them is guessed. The cap and the budget are sized from the run's own cost model, which [Post 03](../03-the-agent-loop/index.md) §8 works through with real token counts and [Post 23](../23-economics-haas/index.md) §3 states as a rule: you do not pick a ceiling by guessing a safe maximum, you pick it from what one run of this task is worth. The stall window comes from how many consecutive repeats a legitimate retry can produce, which is why [Post 03](../03-the-agent-loop/index.md) §9 defends a window of three rather than one. This post takes those numbers as given and asks what the loop does with them.

---

## 3. Loop engineering versus a bare while-loop

The naive loop is `while not model_says_done(): step()`. It has exactly one exit, and it is the worst one: the model's own claim that it is finished, which is victory declaration ([Post 05](../05-agent-failure-modes/index.md)) with no guard around it. It cannot stop for running out of budget, cannot notice it is thrashing, and trusts the very judgement Part III spent five posts learning not to trust.

An engineered loop makes the exits explicit, prioritised, and instrumented. It is still short:

```python
def run_loop(step, goal_met, tokens_spent, *, max_iters=20, token_budget=200_000):
    """Drive `step` with four layered exits, so the loop stops for the right reason.

    `tokens_spent` is required rather than optional: a meter you can forget to
    pass is a ceiling that silently defaults to off.
    """
    last, stalls = None, 0
    for i in range(1, max_iters + 1):                # exit 2: hard iteration cap
        state = step()                               # one iteration (Post 03)
        if goal_met(state):                          # exit 1: the intended exit, goal verified
            return "done", i
        if tokens_spent() > token_budget:            # exit 3: in arrears; §4 sharpens this
            return "over-budget", i
        stalls = stalls + 1 if state == last else 0  # exit 4: no-progress detection
        if stalls >= 2:
            return "no-progress", i
        last = state
    return "max-iters", max_iters
```

Every path out returns a *reason*, which is what makes the loop debuggable: "over-budget at iteration 12" tells you something a silent stop never could ([Post 21](../21-observability-traces/index.md)). The difference between this and the bare loop is not lines of code; it is that the loop's behaviour is designed instead of accidental.

Two of those lines are weaker than they look, and the next two sections take them apart in turn: the budget check that runs after the money is gone, and the stall test that compares the wrong thing.

---

## 4. Reserve before you spend

Look closely at where exit ③ sits in that snippet: `tokens_spent() > token_budget` runs *after* `step()`. That loop cannot spend without bound, but it can overshoot the ceiling by up to one iteration's worth, and because per-iteration cost climbs across a run ([Post 23](../23-economics-haas/index.md) §1), the iteration that crosses the line is a late and expensive one rather than an average one. A ceiling enforced only in arrears is not a ceiling, it is a notification.

The arithmetic is worth doing once, using the run model the series already carries: a task whose first turn sends about 6,000 tokens and whose twelfth sends about 40,000, growing by roughly 3,100 tokens a turn as each response and each observation is appended to a history that is re-sent in full every turn ([Post 03](../03-the-agent-loop/index.md) §8). Set the ceiling at 200,000 tokens and watch the last three iterations:

| Iteration | Tokens sent | Cumulative | Arrears check, after the call | Reserved check, 37,000 held back |
|---|---|---|---|---|
| 9 | 30,800 | 165,600 | under the line | under the line |
| 10 | 33,900 | 199,500 | under the line | under the line |
| 11 | 37,000 | 236,500 | fires, 36,500 past the line | stops before the call, at 199,500 |

The arrears loop reports that it enforced a 200,000-token ceiling and hands you a bill for 236,500, an 18% overrun on the one number the guard existed to hold. The reserved loop stops 500 tokens short of the line. Checking before spending is barely more code:

```python
if tokens_spent() + estimated_next_call() > token_budget:
    return "budget-exhausted", i          # stop BEFORE the call that would breach it
state = step()
```

The estimate does not have to be exact; it has to be conservative, and the harness already knows every term. A serviceable reserve is the size of the history you are about to send (you have just assembled it), plus the largest tool result you allow back, plus the `max_tokens` you set for the reply. Keeping that reserve small enough to be usable is one of the practical arguments for offloading big tool outputs to disk rather than into the window ([Post 09](../09-context-management-loop/index.md)): a harness that lets a 60,000-token log into the history must reserve for it on every subsequent turn. Prompt caching pushes the error the safe way, because most of the reserved prefix is re-read at the cached rate rather than the full one ([Post 23](../23-economics-haas/index.md) §4), so a reserve stated in tokens overestimates the money.

The same reasoning applies to wall-clock deadlines, and more sharply, because a call already in flight cannot be un-started. If a run must be finished by a deadline, the check is "is there time for another iteration?" rather than "is the deadline past?"

This is not a hypothetical failure in someone else's code. The loop companion this series ships, [`code/03-agent-loop/`](../../code/03-agent-loop/), does exactly the arrears version: `run()` adds `resp.tokens` to `tokens_used` and only then tests `tokens_used >= token_budget`, so its ceiling can be crossed by the whole iteration that crossed it. That is the teaching version of the loop, and it is the concrete example this section is about.

---

## 5. What you compare decides what you detect

Exit ④ compares this iteration's state to the last one. That comparison is doing all the work, and `state == last` is the weakest version of it: it catches an agent that is exactly repeating itself and misses an agent wandering in productive-looking circles.

Better signals, in rough order of how much they cost to compute:

- **The tool-call signature.** Tool name plus normalised arguments. Repeating the same call with the same arguments is the classic doom loop and is cheap to spot. It is eight lines in the loop companion, [`code/03-agent-loop/`](../../code/03-agent-loop/), where `_signature()` builds "a stable fingerprint of a turn's tool calls" with `json.dumps(..., sort_keys=True)`, so that two identical calls whose argument dictionaries serialise in a different order do not read as progress ([Post 05](../05-agent-failure-modes/index.md) §6 walks the same code as the doom loop's trace signature).
- **The observable effect.** Did anything change on disk: a diff, a new commit, a test that flipped? An agent making calls that change nothing is stalled regardless of how varied the calls look. The Ralph loop builds its detector on exactly this, comparing the repository head before and after each iteration and counting the passes that left it unmoved, because a loop that commits once per task already has the progress record it needs ([Post 18](../18-long-horizon-ralph/index.md) §8).
- **The verifier's score.** If the check reports a distance rather than a boolean, no improvement across several iterations is stalling even when every iteration does something. This is the only one of the three the series does not ship as code, and it is the one that catches an agent doing genuinely different work that gets no closer.

Pick the signal that matches the failure you actually see, and be explicit that a detector tuned to one shape of stall will not catch another. Two or three iterations of tolerance before firing is the usual setting: enough that a legitimate retry after a transient error is not mistaken for a stall.

---

## 6. A failed call is not an exit

Errors are missing from the model of the loop so far, and they are the cheapest way to defeat all four exits at once. A retry storm burns iterations, burns tokens, and produces a *changing* state on every pass, so the stall detector never fires. A loop that treats every failure as a stop condition is fragile; a loop that treats none of them as one runs away.

The classification is the design decision, and it is short:

| What came back | What it is | What the loop should do |
|---|---|---|
| A 429 rate-limit response | transport, and certainly transient | retry with bounded backoff; charge the wait to the wall-clock budget |
| A 529 or 503 overloaded response | transport, usually transient | the same, with a lower attempt ceiling |
| A timeout with no response | transport, and possibly duplicated work | retry only where repeating the call is safe |
| A 400 malformed-request response | a harness bug | stop and surface it: retrying cannot fix it |
| A `refusal` or `max_tokens` stop reason | a turn outcome, not an error | handle it as [Post 03](../03-the-agent-loop/index.md) §4 sets out; never retry blindly |

Three rules make retries safe inside a loop that has exits. **Separate the attempt counter from the iteration counter**, so a provider error retried three times is one iteration rather than three, and a flaky hour does not eat the cap that exists to bound *work*:

```python
attempts = 0
while True:
    try:
        resp = model.respond(system, messages, tools)
        break                              # one iteration, however many attempts
    except TransientError:                 # 429, 529, timeout
        attempts += 1
        if attempts > max_attempts:        # a retry budget, not a fifth exit
            return "provider-unavailable", i
        sleep(backoff(attempts))           # spends wall-clock, not tokens
```

**Charge what you actually spent.** Whether a failed call is billed at all depends on where it failed, but the retry certainly is: it re-sends the whole history, so a call retried three times pays for that history three times. A budget that counts only successful calls under-reports a bad hour by exactly the amount you most want to see.

**Do not let the retry budget hide inside the time budget.** Backoff consumes wall-clock without consuming tokens, which is precisely why exit ③'s two forms are not interchangeable: a run that spends twenty minutes sleeping between attempts is nowhere near its token ceiling and may be well past its deadline. When a software development kit (SDK) is doing the retrying for you, find out how many attempts it makes and whether they count against your budget, because it has already decided this on your behalf ([Post 20](../20-sdk-landscape/index.md) §5).

---

## 7. Composing loops

Real systems are loops inside loops. The verification loop of [Post 11](../11-verification-loops/index.md) gets *one step* right by generating and retrying until a check passes. The Ralph loop of [Post 18](../18-long-horizon-ralph/index.md) makes *progress across steps* by doing one task per fresh context. Put the first inside the second and you have the standard composition:

![An outer task loop, one task per pass, containing an inner verify-and-retry loop: pick the next task from the spec, generate then verify with a retry cap of three to five attempts, then commit and advance so the outer loop has its progress record. Below, a table re-deciding the same four exits at each scale, showing what goal, iteration cap, budget and no-progress each mean for the inner loop getting one step right against the outer loop making progress across steps. Three panels compare a fixed per-task share of the budget against a shared pool with a per-task cap, and name the hazard nobody names: an inner loop that burns its retry budget and fails looks like progress, because the state changed on every pass.](diagrams/02-nested-loops.svg)
*The inner loop gets one step right; the outer loop makes progress across steps.*

Each loop carries all four exits at its own scale, and deciding what each one means at each scale is most of the design work:

| Exit | Inner loop, getting one step right | Outer loop, making progress across steps |
|---|---|---|
| ① goal | the step's check passes: tests green, the diff applies ([Post 11](../11-verification-loops/index.md)) | `converged()`: the acceptance gate passes on every criterion ([Post 18](../18-long-horizon-ralph/index.md) §8) |
| ② iteration cap | a retry cap of three to five, because a sixth attempt at the same step rarely differs | a task cap across the whole run |
| ③ budget | a per-step share, or a draw against a shared pool (below) | the run ceiling, which is the one the invoice sees |
| ④ no-progress | the same tool signature repeating (§5) | no new commit, or commits that alternate rather than accumulate ([Post 18](../18-long-horizon-ralph/index.md) §8) |

Budget allocation is the part with no default answer. Two policies work. A **fixed per-task share** divides the run ceiling by the task count up front: 200,000 tokens across ten tasks is 20,000 each, predictable and easy to reason about, and wasteful, because a task that needs 30,000 fails while the headroom left over by nine cheap tasks sits unused. A **shared pool with a per-task cap** lets each task draw what it needs from the run ceiling but never more than some fraction of it, which spends the headroom and accepts that one pathological task can take a fifth of the run before its cap stops it. The choice is the interactive-versus-background call of [Post 23](../23-economics-haas/index.md) §2: a run with a human waiting wants predictable per-task limits, a dispatched background run can afford the pool.

The composition also has a hazard nobody names. An inner loop that burns its full retry budget and then fails presents as *progress* to a naive outer detector, because the state changed on every inner pass. The outer detector must watch the inner loop's **outcome**, not its activity: three tasks in a row ending in `retries-exhausted` is a stalled run, however busy the transcript looks. Nesting is not the only composition available, either. Splitting the work across a planner, a generator and an evaluator ([Post 12](../12-planner-generator-evaluator/index.md)) solves the same control problem by role rather than by depth, and [Post 18](../18-long-horizon-ralph/index.md)'s closing section puts the two together: each Ralph iteration usually contains all three roles.

---

## 8. A guard exit is a handoff, not a full stop

Exits ②, ③, and ④ all mean the same thing: *the run did not finish, and something caught it.* What happens next is a design decision most loops never make, and defaulting to "raise and exit" throws away everything the run bought.

![Two bands: exit 1, the verifier confirming the goal, returns a result; exits 2, 3 and 4 return a result and a resumable position. Below, three panels for checkpointing the work, saying what it was doing, and escalating if it warrants it, each with what happens if you skip it, and captions carrying both rules of thumb: a guard exit returns a resumable position as well as a result, and a budget must be checked before the call that would breach it.](diagrams/03-after-a-guard-exit.svg)
*What a guard exit owes the next run: a checkpoint on an iteration boundary, a handoff someone can read, and an escalation when the reason warrants one.*

Three things a guard exit should do before it returns.

**Checkpoint the work.** A run stopped at the budget ceiling has produced real partial progress: commits, files, a half-finished refactor. If that state is durable ([Post 08](../08-state-filesystem-git/index.md)), the run is *resumable*. If it is not, the whole spend is forfeit, which is a strange thing to accept from a guard whose purpose was to save money. Two details make the checkpoint real. It has to sit on an **iteration boundary**, because a guard that fires mid-tool-call leaves half-applied state that nothing downstream can interpret, which is exactly why the Ralph loop commits once per task ([Post 18](../18-long-horizon-ralph/index.md) §2). And the resumption is a **fresh context** rather than a continuation: the transcript is gone, so the resumed run reads the spec and the handoff file to find out where it is ([Post 18](../18-long-horizon-ralph/index.md) §5). "Raise the ceiling and restart" only works if the context bridge was written on the way out.

**Say what it was doing.** The stop reason is necessary and not sufficient. "over-budget at iteration 12" plus the current handoff file (what is done, what was next, what was blocked) is the difference between a human resuming in a minute and a human re-deriving the state from a trace.

**Escalate to a person when the reason warrants it.** No-progress and budget-exhausted are exactly the escalation triggers of [Post 15](../15-human-in-the-loop/index.md) §9. A loop that stops silently and waits to be noticed wastes the wall-clock time between the stall and the discovery, which is often much larger than the run itself.

The rule of thumb: **the intended exit returns a result; a guard exit returns a result *and* a resumable position.**

---

## 9. Guardrails against runaway spend

The exit that turns loop engineering from tidy to essential is the **budget** (③). A loop multiplies cost: every iteration is another model call over a growing context, and a loop with no ceiling can spend without bound if it never converges. With the reserve of §4 in place the guardrail is structural rather than advisory, because the loop becomes unable to make the call that would cross the line.

What that ceiling does *not* bound is the number of runs. In June 2026 Uber capped employee spend on agentic coding tools at $1,500 per person per tool per month, after exhausting its entire annual artificial intelligence (AI) budget in about four months. The company had previously encouraged staff to use the tools as much as possible and ranked usage on internal leader boards; the new caps are trackable on a per-employee dashboard and can be exceeded with permission (TechCrunch, 2026). Every individual run in that story may well have stopped politely at its own ceiling. Per-token pricing multiplied by enthusiastic use is what emptied the budget, and no per-run exit can see that.

So there are three ceilings rather than one, and they are enforced in different places:

- **Per-run**, which is exit ③: the loop's own reserve check, and the only one this post can implement.
- **Per-agent per-period**, which is Uber's cap: a meter outside the loop that counts across runs and refuses to start the next one. This is the ceiling that bounds a scheduled job relaunching a well-behaved loop two hundred times overnight.
- **Per-fleet**, which is what a swarm of parallel agents needs ([Post 17](../17-parallel-agents-shared-repo/index.md)): a shared pool that many concurrent loops draw from, so ten agents each respecting a 200,000-token ceiling cannot quietly spend two million between them.

One conversion trap sits underneath all three. A token count is not a cost, because input, output and cached-read tokens are priced differently and often by an order of magnitude ([Post 23](../23-economics-haas/index.md) §4). A token ceiling is a proxy for a money ceiling, the mapping is not linear, and a run that shifts its mix towards output or invalidates its cached prefix costs more at the same token count. Meter in tokens, because that is what the loop can count; set the number from money.

This is a safety concern as much as an economic one. A runaway loop is how a small misconfiguration becomes a large bill or a swarm of wasted work overnight. Hoping a loop will stop on its own is not loop engineering; making it unable to overrun is.

---

## Common pitfalls

- **Getting the goal exit wrong, in either direction.** A bare `while not done` loop has one exit and it is the model's own word, which is victory declaration with no guard around it; a loop with a cap and a budget but no verified goal runs to the cap even when it succeeded at iteration three, and reports a guard exit for a run that finished. The goal exit needs ground truth, and it needs to exist (§2, §3; Post 11).
- **Checking the budget after the call.** A ceiling enforced in arrears is a notification, not a ceiling; reserve for the next iteration and stop before it, or expect the overrun to be the most expensive iteration in the run (§4).
- **A no-progress detector that only spots exact repeats.** Compare tool-call signatures or effects on disk, or you will miss an agent wandering in circles, and you will kill an agent that is legitimately polling (§5).
- **Treating a transient failure as an exit.** A 429 is a retry with bounded backoff, not a stop condition; count attempts separately from iterations, and do not let backoff hide from the wall-clock budget (§6).
- **One budget for nested loops.** An inner loop with no share of the ceiling can starve every task after it; decide between a fixed share and a capped pool rather than discovering the policy in production (§7).
- **A guard exit that leaves nothing behind.** A run stopped at the ceiling should leave a checkpoint on an iteration boundary, a handoff file, and a stop reason someone can act on. Without the first two the guard converted spend into nothing; without the third the run cannot be debugged or escalated (§8; Posts 15, 21).
- **A per-run ceiling mistaken for a spend limit.** Per-run, per-agent-per-period and per-fleet are three different controls, and only the first lives inside the loop (§9).

---

## Further reading

- Osmani, A., "Loop engineering" (2026): the shift from prompting the agent to designing the loop that prompts it, and the source of the Steinberger and Cherny lines quoted in §1.
- tosea.ai, "What Is Loop Engineering? A Complete Guide from Prompt to Harness Engineering" (2026): the layered-exit taxonomy that §2 numbers.
- Greyling, C., "Loop Engineering" (2026): an unattended loop as a small system of five capabilities (scheduling, worktrees, skills, plugins and connectors, sub-agents) held together by persistent state, rather than as one long prompt.
- TechCrunch, "Uber caps employee AI spending after blowing through budget in four months" (2026): the per-person, per-tool, per-month ceiling that no per-run exit can give you.
- Anthropic, "Building effective agents" (2024): the loop these exits bound, described as models "using tools based on environmental feedback in a loop", where it is "common to include stopping conditions (such as a maximum number of iterations)".
- Context Engineering, Post 05: per-call token cost and prompt caching, the single-call basis for the run-level ceilings in §4 and §9.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 20 — The SDK & framework landscape](../20-sdk-landscape/index.md)**: what the major SDKs give you, loop, exits and retry policy included, so you rarely write this by hand.
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: the loop and its four stop conditions, with the sizing arithmetic this post takes as given.
- **[Post 18 — Long-horizon & multi-context execution](../18-long-horizon-ralph/index.md)**: the Ralph loop as the outer loop in the composition, and the context bridge a resumed run reads.
