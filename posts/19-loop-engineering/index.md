# 19 - Loop engineering: designing the loop that prompts the agent

> **TL;DR.** Once a model runs in a loop, the leverage moves from the prompt to the loop that prompts it. A well-engineered loop carries **layered exits**: the final answer, which verification confirms, and three guards (an iteration cap, a budget reserved before it is spent, no-progress detection), each of which leaves a position a second run can resume from. A bare `while not done` loop has only the first and takes the model's word for it. Loop engineering also retries transient failures instead of exiting on them, nests a verify loop inside a task loop, and caps spend that no single run can see.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the agent loop and its four exits.
> **Safe to skip?** Skip it if the reader can already stop a run before the call that would cross its budget, say which stall signal a no-progress detector should compare, keep a provider's rate limit from eating the iteration cap, and resume a run that a guard stopped from a file rather than from its transcript.
>
> **After reading, you will be able to:**
>
> - Give a loop four layered exits in the order they are checked, one intended and three guards, and say what each guard exit must leave behind.
> - Reserve budget before the call that would breach a ceiling, and treat a transient failure as a retry with backoff rather than as an exit.
> - Choose what a no-progress detector compares, a tool-call signature, an effect on disk or a verifier score, from the stall it has to catch.
> - Compose an inner verification loop inside an outer task loop, deciding each exit and the split of one budget at both scales.
> - Turn a guard exit into a handoff a second run resumes from, and place per-run, per-period and per-fleet ceilings on spend.

![One turn of the loop, reason, act, observe, with its exits in the order they are checked: before the model call, exit (2) when no turns are left and exit (3) when the next call would cross the budget; after it, exit (1), a verified final answer, then exit (4), no progress. Exit (1) leaves the result, each guard a handoff; a red dashed path shows a doom loop without (4) running on to (2).](diagrams/01-layered-exits.svg)

*One exit means the work is done; the other three catch a run that is not converging, and each of those owes the next run a place to start.*

---

## 1. The question: what does an engineered loop carry that a bare one does not?

For most of the field's history, using a large language model (LLM) well meant writing a better prompt. Addy Osmani's "Loop Engineering" (O'Reilly Radar, 22 June 2026, first on his blog) argues that once a model runs in a loop the leverage point moves from the prompt to the loop itself. The practitioner is no longer prompting the agent at each step but designing the machine that prompts it, over and over, until it is done. That machine is what this series has been building, and **loop engineering** is the discipline of designing its control flow.

Osmani builds the case on two practitioners' lines, each linked to a post on X. Peter Steinberger: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents." Boris Cherny, head of Claude Code at Anthropic: "I don't prompt Claude anymore. I have loops running that prompt Claude and figuring out what to do. My job is to write loops" (both quoted in Osmani, 2026). Neither is a claim about model capability. Both say where a practitioner's attention goes once the model is good enough to be driven rather than steered, and the answer is that it goes into the driver.

One difference is worth naming. Osmani writes that loop engineering "sits one floor above the harness": the harness runs one agent, and the loop is "the harness but it runs on a timer, it spawns little helpers, and it feeds itself". This series places it inside instead: the loop is component 01 of the eleven ([post 02](../02-anatomy-of-a-harness/index.md)), and every exit designed here is enforced by the same runtime that dispatches the tools and applies the hooks. The practice does not change; where it is filed decides who owns the exits, and here the owner is the harness.

The interesting decisions are then structural rather than verbal: when the loop acts, what it feeds back, and above all **when it stops**. [Post 03](../03-the-agent-loop/index.md) argued that stop conditions are the main design surface of the loop, as the series' argument rather than a measurement. This post takes that seriously and designs the stopping deliberately.

---

## 2. Layered exits

A loop needs more than one way out, layered rather than pooled. The taxonomy of tosea.ai's guide (16 June 2026) names four: "a verifier that confirms the goal is met, a hard maximum-iteration cap, a token or time budget, and no-progress detection". They are the four exits of post 03, numbered as the series numbers them everywhere ([notation guide](../../notation_guide.md)):

- **(1) Final answer.** The intended exit: the model finishes, and a check against ground truth confirms the work ([post 11](../11-verification-loops/index.md)). It is the only exit that means success.
- **(2) Iteration cap.** The backstop, so the loop ends even if nothing else fires.
- **(3) Budget.** The cost ceiling in tokens or wall-clock seconds, provided it is checked *before* the spend rather than after it.
- **(4) No progress.** The thrashing guard, which stops a doom loop ([post 05](../05-agent-failure-modes/index.md)) when successive iterations stop changing anything.

The layering buys two things. The first is a split: exit (1) is the intended exit and the other three are guards, so a run that takes (2), (3) or (4) did not finish and is a run someone needs to look at. The second is an order. The companion of post 03 checks (1), (3) and (4) after each model call, in that order, and takes (2) when its `for` statement runs out of turns. Checking (1) first means a run that has just succeeded is not cut off by a guard tripped by the same call. Section 4 moves (3) in front of the call, which is the one change to that order this post makes; the figure at the top draws the result.

These are the exits the loop reaches on its own. A human interrupting a run, or an approval that times out, stops it from outside, on the oversight surface of [post 15](../15-human-in-the-loop/index.md); a provider error turns out not to be an exit at all (section 6).

The exits differ in what they mean, and more in what they oblige the run to leave behind:

| Exit | What fires it | What it means | What the run must leave behind |
|---|---|---|---|
| (1) final answer | the model finishes and a check against ground truth passes | success, and the only exit that means it | the result |
| (2) iteration cap | the loop's turn bound is exhausted | did not converge in the turns allowed | the result so far, plus a resumable position |
| (3) budget | the next call would cross the ceiling | ran out of what the task was worth | the same, plus the spend to date |
| (4) no progress | the chosen stall signal repeats | busy without moving | the same, plus the repeating signature |

None of the numbers behind them should be guessed: post 03 sizes the cap and the budget from the run's token arithmetic, and [post 23](../23-economics-haas/index.md) derives a ceiling from what one run of the task is worth. This post takes those numbers as given and asks what the loop does with them.

---

## 3. Loop engineering against a bare while-loop

The naive loop is `while not model_says_done(): step()`. It has exactly one exit and it is the worst one: the model's own claim that it is finished, which is victory declaration ([post 05](../05-agent-failure-modes/index.md)) with no guard around it. It cannot stop for running out of budget, cannot notice that it is thrashing, and trusts the judgement Part III spent five posts learning not to trust.

An engineered loop makes the exits explicit, ordered and named. It is still short; `snippets/run_loop.py` holds it:

```python
def run_loop(step, goal_met, tokens_spent, *, max_iters=20, token_budget=200_000, window=3):
    """Drive `step` with four layered exits and return (stop reason, iterations).

    `tokens_spent` is required rather than optional: a meter that can be left
    out is a ceiling that silently defaults to off.
    """
    recent = []
    for i in range(1, max_iters + 1):                # exit (2): the bound on the for statement
        state = step()                               # one iteration of the loop
        if goal_met(state):                          # exit (1): checked first, the intended exit
            return "completed", i
        if tokens_spent() >= token_budget:           # exit (3): in arrears, after the spend
            return "budget", i
        recent = (recent + [state])[-window:]        # exit (4): the last `window` states identical
        if len(recent) == window and len(set(recent)) == 1:
            return "no_progress", i
    return "max_iters", max_iters
```

Driven by four scripted runs, one written to reach each exit, it prints:

```text
run                               stop reason  iterations
goal reached at step 5              completed           5
50 tokens a step, budget 120           budget           3
the same state every step         no_progress           3
new states, no goal, cap 6          max_iters           6
```

Every path out returns a *reason*, spelt as the series spells it in code and traces, which is what makes a run debuggable: "`budget` at iteration 11" says something a silent stop never could ([post 21](../21-observability-traces/index.md)). The difference from the bare loop is not lines of code; it is that the loop's behaviour is designed instead of accidental. Two of those lines are weaker than they look, and the next two sections take them apart.

---

## 4. Reserve before spending

Exit (3) in that sketch runs *after* `step()`, and so does the companion's: `run()` adds the response's tokens to `tokens_used` and only then tests `tokens_used >= token_budget`. Such a loop cannot spend without bound, but it can overshoot the ceiling by a whole iteration, and because each request re-sends a growing history, the iteration that crosses the line is a late, expensive one. A ceiling enforced only in arrears is a notification, not a ceiling.

The arithmetic is worth doing once, on the series' running example, which is illustrative rather than measured: the first request sends 6,000 input tokens and each later one 3,100 more, so request $n$ sends $6{,}000 + 3{,}100(n - 1)$ and the twelfth sends 40,100 ([post 23](../23-economics-haas/index.md)). With a ceiling of 200,000 input tokens, `snippets/layered_loop.py` runs the companion's `run()` and a controller that reserves before each call; the last three iterations go:

| Iteration | Tokens sent | Cumulative | Checked after the call | Reserved before the call |
|---|---|---|---|---|
| 9 | 30,800 | 165,600 | under the line | under the line |
| 10 | 33,900 | 199,500 | under the line | under the line |
| 11 | 37,000 | 236,500 | fires, 36,500 past the line | refused before it is made, at 199,500 |

The arrears loop reports that it enforced a 200,000-token ceiling and bills 236,500, about 18% over on the one number the guard existed to hold. The reserved loop stops 500 tokens short. Because the companion's `run()` cannot be edited, the controller works at the call boundary: it is a model wrapper that refuses the call before making it, and the snippet records the refusal as exit (3), `budget`. The check is four lines:

```python
        need = request_size(n)                       # the history about to be sent: assembled, so known
        if self.spent + need > self.budget:          # exit (3), reserved: stop BEFORE the call that would breach it
            self.refused = (n, need)
            raise BudgetReserve(n)
```

The estimate does not have to be exact; it has to be conservative, and the harness knows every term. A serviceable reserve is the history about to be sent (the harness has just assembled it), plus the largest tool result it allows back, plus the `max_tokens` it set for the reply. Keeping that reserve usable is one more argument for offloading large tool outputs to disk ([post 09](../09-context-management-loop/index.md)): a harness that lets a 60,000-token log into the history has to reserve for it on every later turn. Prompt caching errs the safe way after the first write, since a cached prefix is re-read at a tenth of the input rate (Anthropic pricing page, consulted October 2026), so a reserve stated in uncached tokens overestimates the money.

A wall-clock deadline needs the same treatment and more, because a call already in flight cannot be un-started. The check is "is there time for another iteration?", never "is the deadline past?".

---

## 5. What is compared decides what is detected

Exit (4) compares this iteration with the last ones, and that comparison does all the work. `state == last` is the weakest version: it catches an agent repeating itself exactly and misses one wandering in productive-looking circles. Three better signals, in rising order of cost:

- **The tool-call signature.** Tool name plus normalised arguments. The companion's `_signature` builds it with `json.dumps(..., sort_keys=True)`, so two identical calls whose arguments serialise in a different order do not read as progress; [post 05](../05-agent-failure-modes/index.md) walks the same check as the doom loop's trace signature.
- **The effect on disk.** Did anything change: a diff, a new commit, a test that flipped? An agent whose calls change nothing is stalled however varied the calls look. The Ralph loop builds its detector on exactly this, counting iterations that leave no new commit, because a loop that commits once per task already has its progress record ([post 18](../18-long-horizon-ralph/index.md)).
- **The verifier's score.** If the check reports a distance (failing tests, say) rather than a pass, no improvement across a window is a stall even when every iteration does something. It catches an agent doing genuinely different work that gets no closer.

`snippets/stall_signals.py` runs each signal over four scripted traces, firing when the last three values are identical, the companion's window:

```text
trace                                  signature  effect on disk  verifier score
doom loop: the same call                  turn 3          turn 3          turn 3
wandering: new calls, no edits             never          turn 3          turn 3
busy edits, no closer                      never           never          turn 3
healthy: tests 3, 2, 1, 0                  never           never           never
```

Each signal catches what the one before it misses, and each costs more: a string, a hash of the working tree, a verifier that returns a number. Each also misfires in its own way: an agent polling a build changes nothing on disk, and a refactor that must land before any test improves holds the score flat. Pick the signal that matches the stall actually seen; a detector tuned to one shape of stall will not catch another. The window must be wide enough that a legitimate retry is not mistaken for a stall, which is why post 03 defends three.

---

## 6. A failed call is not an exit

Errors are missing from the model of the loop so far, and they are the cheapest way to defeat all four exits at once. A retry storm burns iterations and wall-clock and produces a *changing* state on every pass, so the stall detector never fires. A loop that treats every failure as a stop is fragile; one that treats none as a stop runs away.

The classification is the design decision. Anthropic's application programming interface (API) errors page (consulted October 2026) gives the codes:

| What came back | What it is | What the loop should do |
|---|---|---|
| 429 `rate_limit_error` | transient for a rate limit; a 429 from a monthly spend cap carries no `retry-after` header and keeps failing | retry with bounded backoff, honouring `retry-after`; treat the spend-cap case as a budget stop |
| 529 `overloaded_error`, 500 `api_error` | transient on the provider's side | the same, with a lower attempt ceiling |
| 504 `timeout_error`, or no response | transient, and possibly duplicated work | retry only where repeating the call is safe |
| 400 `invalid_request_error` | a harness bug, or an organisation's spend limit reached | stop and surface it: retrying cannot fix either |
| a `refusal` or `max_tokens` stop reason | a turn outcome, not an error | handle it as post 03 sets out; never retry blindly |

Three rules make retries safe inside a loop that has exits. **Count attempts apart from iterations**, so a provider error retried twice is one iteration rather than three, and a flaky hour does not eat the cap that exists to bound *work*. The controller in `snippets/layered_loop.py` wraps the call:

```python
        attempt = 0
        while True:
            try:
                resp = self.model.respond(system, messages, tools)
                break                                # one iteration, however many attempts it took
            except TransientError as err:            # 429, 529, a timeout: worth another attempt
                attempt += 1
                if attempt >= self.max_attempts:     # a retry budget, not a fifth exit: the run ends as an error
                    raise RetriesExhausted(n) from err
                delay = self.base * 2 ** (attempt - 1) * (1 + self.rng.random())   # backoff with jitter
                self.retries.append((n, attempt, err.kind, delay))
                time.sleep(delay)                    # spends wall-clock, not tokens
```

A run whose provider stays down ends with the stop reason `error`, the fifth value [post 21](../21-observability-traces/index.md) records for a run that raised, rather than with a guard exit that would misreport why it stopped.

**Charge what was actually spent.** Read the meter from the provider's reported usage rather than from a count of successful responses, and charge an attempt whose fate is unknown, a timeout with no response, at its estimate.

**Keep backoff inside the time budget.** Backoff consumes wall-clock without consuming tokens, which is why exit (3)'s two forms are not interchangeable: a run that sleeps twenty minutes between attempts is nowhere near its token ceiling and may be well past its deadline. A software development kit (SDK) that retries for the harness has already decided this: Anthropic's client SDK retries connection errors, rate limits and 5xx server errors twice by default with exponential backoff, configurable through `max_retries` (API errors page, consulted October 2026), and that wait comes out of the wall-clock budget without passing through the loop's counters ([post 20](../20-sdk-landscape/index.md)).

---

## 7. Composing loops

Real systems are loops inside loops. The verification loop of [post 11](../11-verification-loops/index.md) gets *one step* right by generating and retrying until a check passes. The Ralph loop of [post 18](../18-long-horizon-ralph/index.md) makes *progress across steps*, one task per fresh context. Put the first inside the second and the result is the standard composition, drawn below.

![An outer task loop containing an inner verify-and-retry loop: pick the next task, generate and check it through a purple gate with retries, then commit and advance. One run budget feeds both. The inner loop reports verified or unverified to the outer one, and a red unverified card marks the stall: busy retries look like progress unless the outer detector reads outcomes.](diagrams/02-nested-loops.svg)

*The inner loop gets one step right; the outer loop makes progress across steps, and it must read the inner loop's outcome rather than its activity.*

Each loop carries all four exits at its own scale, and deciding what each means at each scale is most of the design work:

| Exit | Inner loop, getting one step right | Outer loop, making progress across steps |
|---|---|---|
| (1) final answer | the step's check passes: tests green, the diff applies | the acceptance gate passes on every criterion of the spec |
| (2) iteration cap | an attempt cap, five by default in post 11's companion | a task cap across the whole run |
| (3) budget | a per-task share, or a draw against a shared pool | the run ceiling, the one the invoice sees |
| (4) no progress | the same failure report repeating | no new commit, or commits that alternate rather than accumulate |

Budget allocation is the part with no default answer. Two policies work, shown here with illustrative numbers. A **fixed per-task share** divides the run ceiling by the task count up front: 200,000 tokens across ten tasks is 20,000 each, predictable and wasteful, because a task that needs 30,000 fails while the headroom nine cheap tasks left sits unused. A **shared pool with a per-task cap** lets each task draw what it needs but never more than a set fraction, say a fifth, which spends the headroom and accepts that one pathological task can take that fifth before its cap stops it. The choice follows the interactive-against-background split of post 23: a run with a person waiting wants predictable per-task limits, a dispatched background run can afford the pool.

The composition has one easily missed hazard. An inner loop that burns its attempts and fails presents as *progress* to a naive outer detector, because the state changed on every inner pass. The outer detector must watch the inner loop's **outcome**, not its activity: three tasks in a row ending unverified is a stalled run, however busy the transcript looks. Splitting the work across a planner, a generator and an evaluator ([post 12](../12-planner-generator-evaluator/index.md)) solves the same control problem by role rather than by depth.

---

## 8. A guard exit is a handoff, not a full stop

Exits (2), (3) and (4) mean the same thing: *the run did not finish, and something caught it.* What happens next has to be decided: defaulting to "raise and exit" throws away everything the run bought. A guard exit owes the next run three things.

**A checkpoint of the work.** A run stopped at its ceiling has produced real partial progress: commits, files, a half-finished refactor. If that state is durable ([post 08](../08-state-filesystem-git/index.md)) the run is resumable; if not, the whole spend is forfeit, a strange outcome for a guard whose purpose was to save money. The checkpoint has to sit on an **iteration boundary**, because a guard that fires mid-tool-call leaves half-applied state nothing downstream can interpret, which is why the Ralph loop commits once per task. And the resumption is a **fresh context**, not a continuation: the transcript is gone, so the resumed run reads the spec and the handoff file to find out where it is.

**A record of what it was doing.** The stop reason is necessary and not sufficient. "`budget` at iteration 10" plus a handoff file in post 08's four fields (spec, done, next, and a checkable state) is the difference between a person resuming in a minute and a person re-deriving the state from a trace. Post 08's other rule applies too: the handoff counts as written only once it has been read back.

**An escalation when the reason warrants one.** Post 15's escalation triggers fire *before* these exits: on the second identical call, one turn ahead of exit (4), and at a budget threshold set below exit (3). When a guard exit fires anyway, a loop that stops silently and waits to be noticed wastes the time between the stall and its discovery, which can be longer than the run.

`snippets/layered_loop.py` runs the whole sequence on the illustrative run above, migrating thirteen modules with one tool call each. The reserve refuses run 1's call 11, and run 1 writes the handoff and stops; run 2 is a fresh call to the companion's `run()` built from the file alone, and it finishes on exit (1). On the way, call 4 meets a rate limit and an overload, both retried without costing an iteration. The figure draws the two runs.

![Two runs, one bar per model call. Run 1 makes ten calls from 6,000 to 33,900 input tokens, call 4 retried twice; the purple reserve gate refuses call 11, 37,000 tokens, at 199,500 spent: exit (3), budget. A green handoff file records m01 to m10 done, m11 to m13 next. Run 2, built from the file, makes four calls, 42,600 tokens, and ends on exit (1).](diagrams/03-after-a-guard-exit.svg)

*The guard stops the run before the call that would cross the line, and the handoff file is all the second run needs to finish the work.*

The rule of thumb: **the intended exit returns a result; a guard exit returns a result and a resumable position.**

---

## 9. Guardrails against runaway spend

The exit that turns loop engineering from tidy to essential is (3), budget. A loop multiplies cost: every iteration is another model call over a growing context, and a loop with no ceiling can spend without bound if it never converges. With the reserve of section 4 the guardrail is structural rather than advisory, because the loop becomes unable to make the call that would cross the line.

What that ceiling does *not* bound is the number of runs. TechCrunch (Lucas Ropek, 2 June 2026, relaying Bloomberg) reported that Uber had set a monthly cap of 1,500 dollars per employee per agentic coding tool, Claude Code and Cursor among them, trackable on a dashboard each employee can see and exceedable with permission in certain cases. The company had earlier encouraged staff to use the tools "as much as possible", ranked usage on internal leader boards, and, as its chief technology officer disclosed in April, used up its annual artificial intelligence (AI) budget in four months. The figures are reported at one remove. Every run in that story may have stopped at its own ceiling; use multiplied by per-token pricing emptied the budget, and no per-run exit can see that.

So there are three ceilings rather than one, enforced in different places:

- **Per run**, which is exit (3): the loop's own reserve check, and the only one this post implements.
- **Per agent per period**, which is Uber's kind of cap: a meter outside the loop that counts across runs and refuses to start the next one. Providers ship one: Anthropic's API returns a 400 once an organisation reaches a spend limit it set. It is the ceiling that bounds a scheduled job relaunching a well-behaved loop two hundred times overnight.
- **Per fleet**, which is what a swarm of parallel agents needs ([post 17](../17-parallel-agents-shared-repo/index.md)): a shared pool that many concurrent loops draw from, so that ten agents each respecting a 200,000-token ceiling cannot quietly spend two million between them.

One conversion trap sits under all three: a token count is not a cost. At the Claude Sonnet 4.6 rates on Anthropic's pricing page (consulted October 2026), input costs 3 dollars per million tokens, output 15 and a cache read 0.30, so one token can cost fifty times another. A token ceiling is a proxy for a money ceiling, the mapping is not fixed, and a run that shifts its mix towards output or invalidates its cached prefix costs more at the same token count (`ctx-005`). Meter in tokens, because that is what the loop can count; set the number from money.

A runaway loop is how a small misconfiguration becomes a large bill or a night of wasted work: hoping a loop will stop is not loop engineering; making it unable to overrun is.

---

## 10. Make it run

The plan's exercise for this post is to wrap the loop of post 03 in the controller and show a guard exit writing a handoff that a second run resumes from. The three snippets run offline from the series root with the standard library; `layered_loop.py` and `stall_signals.py` import the companion from `code/03-agent-loop/src` unchanged:

```bash
uv run python posts/19-loop-engineering/snippets/run_loop.py
uv run python posts/19-loop-engineering/snippets/layered_loop.py
uv run python posts/19-loop-engineering/snippets/stall_signals.py
```

The first and the last print the tables quoted above. `layered_loop.py`, the exercise, prints both budgets, the two retries, the handoff and both runs in under a second:

```text
illustrative run: request n sends 6,000 + 3,100 (n - 1) input tokens; ceiling 200,000
run                                      stop_reason  iterations    tokens
companion run(), budget after the call        budget          11   236,500
run 1, reserve before the call                budget          10   199,500
  refused call 11: 199,500 spent + 37,000 next = 236,500 > 200,000
  call 4, attempt 1: rate_limit_error (429), retried after 0.017 s
  call 4, attempt 2: overloaded_error (529), retried after 0.036 s
  handoff written, read back: Done m01, m02, m03, m04, m05, m06, m07, m08, m09, m10 (10 of 13). Next m11, m12, m13
run 2, fresh context from the handoff      completed           4    42,600
  answer: All 13 modules migrated.
provider down on call 2, 4 attempts            error           1     6,000
arrears overshoot: 36,500 tokens, 18.2% past the ceiling
```

Run 1's two retries leave its iteration count at ten. To try a variation, raise `BUDGET` to 400,000 and both loops finish the task in one run of 14 iterations and 366,100 tokens, so no handoff is written. Then set the controller's `max_attempts` to 2: call 4 ends run 1 as an `error` with three modules done, the handoff records that instead, and run 2 is itself stopped on `budget`, because ten modules plus the answer no longer fit one ceiling.

---

## 11. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A budget checked after the call.** The dashboard says the ceiling held, and the invoice shows a run one late iteration over it.
- **A retry counted as an iteration.** A bad hour of rate limits ends ordinary runs on `max_iters`, and the team investigates a model failure that is really the provider's.
- **A stall detector on signatures alone.** An agent reads a different file every turn for forty turns and is stopped only by the cap.
- **An outer detector watching activity.** Every task ends unverified after five busy attempts, and the run reads as progress until the budget runs out.
- **A guard exit with no handoff.** The run stops at its ceiling, the next run starts from the spec, and the first ten modules are migrated a second time.
- **A per-run ceiling taken for a spend limit.** Every run stops on time, a scheduler starts two hundred of them, and the monthly bill arrives with no exit having fired.

---

## Common pitfalls

1. **Getting the goal exit wrong in either direction.** The bare loop's only exit is the model's word; a loop with a cap and a budget but no verified goal runs on after succeeding and reports a guard exit for a run that finished.
2. **Checking the budget after the call.** A ceiling enforced in arrears is a notification; reserve for the next call and stop before it.
3. **Treating a transient failure as an exit.** Retry with bounded backoff, count attempts apart from iterations, and keep the waiting inside the wall-clock budget.
4. **One budget for nested loops with no policy.** Decide between a fixed per-task share and a capped pool before production decides it.
5. **A guard exit that leaves nothing behind.** Without a checkpoint and a handoff the guard converts spend into nothing; without a stop reason the run cannot be debugged or escalated.
6. **A per-run ceiling mistaken for a spend limit.** Per run, per agent per period and per fleet are three controls, and only the first lives inside the loop.

---

## Further reading

- Addy Osmani, "Loop Engineering" (O'Reilly Radar, 22 June 2026, first published on his blog): the shift from prompting the agent to designing the loop that prompts it, the Steinberger and Cherny lines, and loop engineering placed "one floor above the harness".
- tosea.ai, "What Is Loop Engineering? A Complete Guide from Prompt to Harness Engineering (2026)" (16 June 2026): layered exits, the verifier, the cap, the budget and no-progress detection.
- Cobus Greyling, "Loop Engineering" (Medium, 9 June 2026): an unattended loop as five building blocks (scheduling, worktrees, skills, plugins and connectors, sub-agents) held together by persistent state, rather than as one long prompt.
- Lucas Ropek, "Uber caps employee AI spending after blowing through budget in 4 months" (TechCrunch, 2 June 2026): the per-employee, per-tool, per-month ceiling that no per-run exit provides.
- Anthropic, "Building effective agents" (19 December 2024): agents as "LLMs using tools based on environmental feedback in a loop", where "it's also common to include stopping conditions".
- Anthropic, API errors page and pricing page (consulted October 2026): the error codes, the SDK's default retries, and the rates behind section 9.
- `ctx-005` (`context-engineering`): the price of one call and prompt caching, the single-call basis for the run-level ceilings here.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 20 - The SDK and framework landscape: Agent SDK, LangGraph, and peers](../20-sdk-landscape/index.md):** what the major SDKs already decide about exits, retries and budgets, and how to read those defaults before adopting one.
- **[Post 24 - Build #1: a minimal agent harness from scratch](../24-build-minimal-harness/index.md):** the loop, its layered exits and a verification gate assembled into one runnable harness.
