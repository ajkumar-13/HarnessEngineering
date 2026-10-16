# 23 - The economics of a harness and Harness-as-a-Service

> **TL;DR.** An agent run pays for one model call per loop iteration, and each call re-reads a context that grew the turn before, so an uncached run's input bill grows with the square of its iteration count. Two levers move it: budget ceilings cap how many times the loop turns, and a rolling prompt-cache breakpoint bills the re-read history at a tenth of the input rate, so the bill grows nearly linearly. The number that decides whether an agent ships is cost per successful run, and beside a person's review time the model bill can be the small term. Harness-as-a-Service (HaaS) products rent the loop itself, which adds a runtime meter to the token bill rather than replacing it.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the agent loop, its four exits and the token arithmetic of one run.
> **Safe to skip?** Skip it if the reader can already price an agent run uncached and with a rolling cache breakpoint, derive a budget ceiling from a run's worth, and compute cost per successful run and a build-versus-rent crossover.
>
> **After reading, you will be able to:**
>
> - Price one agent run from its iteration count and growing context three ways: uncached, with a cached static head, and with a rolling cache breakpoint.
> - Explain why an uncached run's input bill grows with the square of its iterations, and what breaks a rolling breakpoint mid-run.
> - Set a latency budget by who is waiting and a budget ceiling from what a run is worth, enforced before the call that would cross it.
> - Compute cost per successful run and cost per unit shipped, and rank two harnesses by them rather than by cost per run.
> - Compare a model API, an SDK the team hosts and a hosted agent runtime by what each bills for, and work a build-versus-rent crossover.

![Computed cumulative dollars against loop iterations 1 to 40 for one illustrative run at Claude Sonnet 4.6 rates: uncached curves up to 0.94 dollars at 12 iterations and 8.33 at 40, a cached static head runs just below, and a rolling breakpoint rises almost straight, 0.33 and 1.60.](diagrams/01-loop-cost.svg)

*Uncached, the bill bends upward with the square of the iterations; a breakpoint that moves with the conversation straightens it.*

---

## 1. The question: what does a loop cost?

What decides whether an agent ships, cost per run or cost per successful run, and which levers move either? The sibling series priced the single call (`ctx-005`); this post prices the **run**, the whole loop turning until one of its exits fires.

A single completion is priced once: input tokens in, output tokens out, one invoice line. An agentic run pays that invoice once per iteration ([post 03](../03-the-agent-loop/index.md)), so a task that resolves in twelve iterations pays for twelve model calls. That is the first fact of harness economics.

The second fact is that the calls grow. Each turn appends the model's output and the tool result to the history, and the run pays for the whole history again at every step. The series' running example, illustrative rather than measured, sends 6,000 input tokens on the first request and appends about 600 tokens of output and 2,500 of tool result per turn, so request $n$ sends $6{,}000 + 3{,}100(n - 1)$ tokens and the twelfth sends 40,100.

The third fact is the price gap between the two token classes. On Anthropic's pricing page (consulted October 2026), Claude Sonnet 4.6 costs 3 dollars per million input tokens and 15 per million output tokens, and Claude Haiku 4.5 costs 1 and 5: output is five times input on both, because generating is one forward pass per token while reading a prompt is done in parallel (`ctx-005`). In a loop the gap compounds, because **every output token is paid once at the output rate and then re-read as input on every later turn**. `snippets/loop_cost.py` prices a 600-token narration emitted at iteration 3: about 0.009 dollars to generate, then re-read on nine later turns, 5,400 input tokens and 0.0162 dollars uncached. Reading it back costs nearly twice what writing it did.

Tool results obey the same rule and are larger. A 12,000-token test log returned at iteration 3 sits in requests 4 to 12: 108,000 input tokens, 0.324 dollars uncached, a third of what the whole running example costs without it, and 0.074 dollars on the rolling breakpoint of the fourth section. That is the economic case for offloading tool output, the cheapest rung of [post 09](../09-context-management-loop/index.md), and the same move [post 08](../08-state-filesystem-git/index.md) prices at about 1,700 to 1 in what a run carries.

Together the three give the shape of the bill. Input cost is the iteration count times the *average* request, and the average grows with the count, so uncached the input bill grows with **the square of the iteration count**. The hero figure draws it from `snippets/loop_cost.py`: the uncached line bends upward, and the rolling-breakpoint line of the fourth section is nearly straight.

---

## 2. Latency budget for an autonomous run

Wall-clock time multiplies the same way. A run's latency is dominated by its sequential model calls and its sequential tool calls, because **the loop's decision chain is serial**: the model cannot choose iteration two's action until iteration one's tool result returns. At an illustrative two seconds per model call and one second per tool call, twelve iterations are 36 seconds of sequential work before any slow tool.

The chain is serial; the work inside a link need not be. A model can emit several `tool_use` blocks in one turn, and a harness that runs independent ones concurrently waits for the slowest rather than the sum ([post 06](../06-tools-bash-code/index.md)). Sub-agent fan-out cuts the wall clock to the slowest worker plus the synthesis and pays in tokens, every worker carrying its own preamble ([post 16](../16-multi-agent-orchestration/index.md)), so it fits a budget generous in dollars and tight in minutes.

The growing context stretches latency as well as cost, because a larger input takes longer to prefill. A cache read skips the prefill of the cached span, so the breakpoint of the fourth section shortens the wait as well as the bill: at iteration 12 of the running example a warm cache leaves 3,100 of 40,100 tokens to prefill. Streaming does less inside a loop than in a chat. A streaming harness can start a tool as soon as that tool's block is complete rather than after the last token ([post 03](../03-the-agent-loop/index.md)), so the saving is whatever the response holds after its first complete call; the rest of streaming's value is on the final answer, where a person is reading.

Who is waiting then sets the budget, and the three modes differ by orders of magnitude. The figures in the table are illustrative ranges, not measurements:

| Mode | Who is waiting | Latency budget | Iterations that fit | What the budget buys |
|---|---|---|---|---|
| **Interactive** | a person at a prompt | seconds to about a minute | roughly 5 to 15 | one attempt, a fast gate, an early escalation |
| **Background** | a queue | minutes to hours | tens to low hundreds | retries, full verification, a sub-agent or two |
| **Long-horizon** | a schedule | hours to days | thousands, across many contexts | resets, handoffs, and the loop of [post 18](../18-long-horizon-ralph/index.md) |

A harness serving two of these needs a ceiling for each; one ceiling for both ships a tool that hangs or a job that quits early. [Post 19](../19-loop-engineering/index.md) makes the same split when it allocates a budget across composed loops: a run with a person waiting wants predictable per-task limits, a dispatched background run can afford a shared pool.

---

## 3. Budget ceilings as guardrails

[Post 19](../19-loop-engineering/index.md) introduced the token ceiling and the wall-clock ceiling as layered exits; exit (3), budget, is the one the invoice sees. Here the same ceiling is an **economic** control, and that changes how the number is chosen. What it counts has to be precise: a ceiling of 200,000 *cumulative billed tokens across the whole run* is a promise about spend, a different quantity from a 200,000-token window one call may fill. A wall-clock ceiling is the same promise for latency and rented compute.

A ceiling is derived from what one run is worth, and the worth of a run is not the worth of a success, because failed runs are billed too. If a resolved task is worth an illustrative 2.00 dollars and the harness resolves 55% of what it attempts, a run started is worth 1.10 dollars on average, and a ceiling above that lets a run spend more than runs return. Pricing the ceiling at the value of a success funds the failures out of the margin; the seventh section makes that denominator explicit.

Two ways the instrument fails silently carry over from post 19. The first is **enforcement in arrears**. A ceiling tested after the call overshoots by up to one iteration, and the iteration that crosses the line is a late, expensive one: uncached, the running example's twelfth iteration costs 0.129 dollars against the first one's 0.027, nearly five times as much. The fix is to reserve the estimated cost of the next call and stop before making it, as post 19 does. A rolling breakpoint also shrinks the error, because it makes the per-iteration cost nearly flat: 0.0315 dollars for the first iteration and 0.0317 for the twelfth.

The second is **spend with nothing to show for it**. A run stopped at its ceiling with no durable checkpoint forfeits the whole amount ([post 08](../08-state-filesystem-git/index.md)), which makes checkpointing an economic requirement: post 19's guard exit that writes a handoff turns a hard stop into a pause that a second tranche of budget can resume.

A cheaper instrument sits beside the ceiling. A ceiling caps what a run *can spend*; a per-step verification gate caps what it can *waste*. [Post 11](../11-verification-loops/index.md) prices the running example with an error entering at iteration 2 and nothing checking until the end: losing eleven of twelve steps, 92%, costs 98% of the spend, because the forfeited steps are the late, context-heavy ones.

---

## 4. Prompt caching across loop iterations

The largest single lever on run cost is prompt caching, and it works differently in a loop than in one call. The mechanism is a **prefix match**: "Prompt caching references the entire prompt: `tools`, `system`, and `messages` (in that order), up to and including the block designated with `cache_control`" (Anthropic, "Prompt caching", Claude Platform documentation, consulted October 2026), so a change at any position misses every entry that includes it. The multipliers, from the same page and Anthropic's pricing page (consulted October 2026), at Claude Sonnet 4.6's rates:

| Token class | Multiplier on base input | Dollars per million, Claude Sonnet 4.6 | When it is paid |
|---|---|---|---|
| Uncached input | 1.0× | 3.00 | no breakpoint covers it, or a miss |
| Cache write, five-minute lifetime | 1.25× | 3.75 | the first request that stores a span |
| Cache write, one-hour lifetime | 2.0× | 6.00 | the same, on the long-lived tier |
| Cache read | 0.1× | 0.30 | every later request that reuses the span |
| Output | not a multiplier | 15.00 | once, at generation; then re-read as input |

A single call has nothing to reuse within itself; caching pays there only across repeated calls that share a prefix (`ctx-005`). In a loop the reuse is structural, because the prefix is re-read every iteration whether or not any traffic repeats.

### The prefix is not the head; it is everything that already happened

The usual mental model treats the cacheable region as a small static head of system prompt and tool schemas. That is the single-call model, and in a loop it leaves most of the money on the table, because **a loop only appends**: nothing before the newest turn changes, so the whole prior conversation is a stable prefix for the next request.

The provider exposes that directly. A request may define up to four cache breakpoints, so spans that change at different rates cache separately, and the agent pattern keeps the last one on the final block of the newest turn and moves it forward every iteration. Automatic caching does the moving: "With automatic caching, the cache point moves forward automatically as conversations grow. Each new request caches everything up to the last cacheable block, and previous content is read from cache" (Anthropic, "Prompt caching"). The four are worth spending deliberately, one per rate of change:

```text
request layout, front (most stable) to back (most volatile)
  tools      schemas, change on deploy              breakpoint 1
  system     prompt and durable rules               breakpoint 2
  context    spec, memory file, exemplars           breakpoint 3
  history    turns 1 to n-1, never edited           read from cache
  turn n     the observation just returned          breakpoint 4, moves every iteration
```

This is what makes the quadratic term of the first section survivable: the history is still re-read every turn, but at 0.1× rather than 1.0×, so the term that grows with the square of the iteration count grows against a rate ten times smaller.

### What breaks it

**A rewrite of the history.** A compaction, a re-sorted tool list, an injected timestamp, a memory file edited mid-run: each changes bytes already cached, so every entry from the change onward is a miss. The multiplier is why this is the most expensive invisible mistake a loop makes: the largest line on the bill goes from a 0.1× read to a 1.25× write, twelve and a half times the price for the same tokens. Nothing in the response text says so; only the provider's usage counts do, `cache_read_input_tokens` and `cache_creation_input_tokens` beside `input_tokens`, which is why they belong on every model-call span ([post 21](../21-observability-traces/index.md)). [Post 09](../09-context-management-loop/index.md) works the exact bill of a compaction, which is more forgiving than the usual telling: tools and system render before messages, so what is lost is the history's cache from the rewrite onward plus the write premium on the new prefix. Hence **compact rarely and deeply**: a shallow compaction pays nearly the full write premium for almost no read saving.

**The clock.** The default lifetime is five minutes, and "The lifetime is measured from the start of the request that writes or reads the cache entry, not from the end of its response" (Anthropic, "Prompt caching"), with every read refreshing it at no charge. A loop whose tool call is a full test suite, or an approval gate waiting on a person, can idle past it, and the next turn is a cold write on the largest context yet assembled. [Post 18](../18-long-horizon-ralph/index.md) prices the limiting case: counting only the re-entry call of each iteration, a frozen prefix read about eight minutes apart on the five-minute tier costs 25% more than no caching at all. The one-hour tier pays 2.0× instead of 1.25× on every token written, while each cold rewrite it prevents bills the whole cached prefix at 1.25× instead of 0.1×. In the running example that premium is 0.090 dollars (0.75 × 40,100 tokens), so one prevented rewrite covers it only from iteration 9, whose 27,700-token prefix costs 0.096 dollars more cold than warm.

---

## 5. One run, priced three ways

Set the running example out in full. Twelve iterations; the first request sends 6,000 tokens and each later one 3,100 more, so the twelfth sends 40,100; every iteration emits 600 output tokens. The sizes are illustrative, the rates Claude Sonnet 4.6's from the fourth section. On a rolling breakpoint everything the previous request sent is read from cache and only the 3,100 new tokens are written:

| Iteration | Input tokens sent | Read from cache | Written to cache | Output tokens |
|---|---|---|---|---|
| 1 | 6,000 | 0 | 6,000 | 600 |
| 2 | 9,100 | 6,000 | 3,100 | 600 |
| 6 | 21,500 | 18,400 | 3,100 | 600 |
| 12 | 40,100 | 37,000 | 3,100 | 600 |
| **Run total** | **276,600** | **236,500** | **40,100** | **7,200** |

`snippets/loop_cost.py` prices the same requests three ways:

```text
12 iterations: last request 40,100 tokens; input 276,600, of which 236,500 already sent the turn before; output 7,200
  uncached     $0.938
  static head  $0.793
  rolling      $0.329
40 iterations: last request 126,900 tokens; input 2,658,000, of which 2,531,100 already sent the turn before; output 24,000
  uncached     $8.334
  static head  $7.811
  rolling      $1.595
growth from 12 to 40 iterations: uncached 8.9x, rolling 4.8x, uncached per iteration 2.7x
saved by the rolling breakpoint: 65% at 12 iterations, 81% at 40; by the static head: 15% at 12
input side only at 12 iterations: rolling $0.221, uncached $0.830
```

- **No caching.** 276,600 input tokens at 3 dollars per million is 0.830 dollars and 7,200 output tokens at 15 per million is 0.108: 0.938 dollars.
- **A static head.** A 5,000-token head of tool schemas and system prompt is written once at 1.25× and read eleven times at 0.1×, and the other 216,600 input tokens pay full price: 0.793 dollars, 15% saved. The head is cached; the history, where the tokens are, is not.
- **A rolling breakpoint.** 236,500 tokens read at 0.1× and 40,100 written at 1.25×, with the same output: 0.329 dollars, about a third of the uncached bill, the input side alone falling from 0.830 to 0.221 dollars.

The ratio matters less than how each behaves as the run lengthens. Out to forty iterations, where the request has grown to 126,900 tokens, the uncached bill is 8.9 times its twelve-iteration value for 3.3 times the iterations: the quadratic term arriving on an invoice. The rolling breakpoint's bill is 4.8 times, close to linear, and its advantage widens with length, 65% saved at twelve iterations and 81% at forty. Long autonomous runs are affordable because the growing part of the context is billed at a tenth. A harness with no caching configured pays no fixed premium; it pays the full rate on the quadratic term.

---

## 6. Where the money goes, and the levers that move it

**Context management, priced.** [Post 09](../09-context-management-loop/index.md) gives four corrective moves in increasing order of aggressiveness. With a money column attached they sort differently from the way they are usually taught:

| Rung | Effect on the re-read bill | Effect on the cache | When it pays |
|---|---|---|---|
| **Offload** at the tool boundary | the bytes never enter, so they are never re-read | untouched: nothing already cached changes | whenever an output is large; the only rung that costs the cache nothing |
| **Clear** spent tool results | stops the re-read from here on | a miss from the cleared position onward, so batch the clears | when large results are genuinely spent |
| **Compact** older turns | stops the re-read, and costs a model call | a write premium on the whole surviving history | rarely and deeply |
| **Reset** behind a handoff | the history goes to zero | starts over: a full write on the new window | when the task outgrows one window ([post 18](../18-long-horizon-ralph/index.md)) |

The offload is the worked line: the first section's 12,000-token test log adds 0.324 dollars to an uncached run and 0.074 to a cached one, and offloading it at the tool boundary avoids both while returning a pointer the agent can read on demand.

**Model routing is not free at the run level.** The tier is a per-iteration decision in principle: deciding whether to continue, summarising a tool result or classifying an error are cheap turns, and Claude Haiku 4.5 costs a third of Claude Sonnet 4.6's rates. But a turn sent to a different model leaves the warm cache behind. `snippets/loop_cost.py` lifts iterations 4, 6, 8 and 10 of the running example out of the cached conversation and sends them uncached to Claude Haiku 4.5:

```text
routing iterations 4, 6, 8 and 10 to Claude Haiku 4.5 uncached: 98,400 input tokens, $0.110, against $0.108 left warm on Claude Sonnet 4.6
```

The tier discount is 3× and the cache discount 10×, so lifting a turn out of a warm conversation is close to a wash; here it is a small loss even before counting the work of feeding the cheap turn's output back into the main conversation. Route *roles* instead: a planner, a generator and an evaluator are already separate calls with separate stable prefixes ([post 12](../12-planner-generator-evaluator/index.md)), each able to sit on its own tier and keep its own warm cache.

---

## 7. Cost per run is the wrong number

Every figure so far is cost per *run*, and a run that fails costs full price and delivers nothing. The number a business runs on is spend divided by the work that succeeded. `snippets/run_meter.py` meters an illustrative set of ten runs on a rolling breakpoint, seven of which pass, and the three that fail run to the iteration cap of 12, so they are the most expensive runs in the set:

```text
ten runs, 7 passed: spend $2.567, $0.2567 per run, $0.3667 per successful run; a successful run alone averages $0.2256
```

The difference between the last two numbers is the mistake: a successful run on its own costs about 0.23 dollars, but each success has to carry its share of the failures, and cost per successful run is 0.37 dollars, more than half as much again.

Production adds two corrections to that denominator, from the staged funnel [post 22](../22-evaluating-harnesses/index.md) builds on Faros AI's metrics (Faros AI, "Harness engineering", 22 May 2026): first-pass success rate, defect-escape rate and dollars per merged pull request (PR). The conversion is one division and two corrections, review added and escapes divided out:

```text
cost_per_accepted = cost_per_run / first_pass_success_rate
cost_per_shipped  = (cost_per_accepted + review_cost) / (1 - defect_escape_rate)
```

Two harnesses, worked in `snippets/run_meter.py`, differ only in whether a verification gate runs on every step ([post 11](../11-verification-loops/index.md)). The gate makes each run *more* expensive, because it adds iterations: harness B is taken to need 16 iterations of the running example where A needs 12. Every other input is illustrative, and review is priced at a placeholder loaded rate of 90 dollars an hour, the term that dominates and the first to replace with a real one:

| Illustrative | A: no verification gate | B: gate on every step |
|---|---|---|
| Iterations per run | 12 | 16 |
| First-pass success rate | 48% | 84% |
| Human review per accepted result | 18 minutes | 6 minutes |
| Defect-escape rate | 14% | 4% |

```text
harness                   per run  per accepted   review  per shipped
A, no gate                 $0.329        $0.686   $27.00       $32.19
B, gate on every step      $0.466        $0.554    $9.00        $9.95
B costs 41% more per run and 0.31 times as much per unit shipped
```

B costs 41% more per run and under a third as much per unit shipped, so cost per run alone ranks the two harnesses in the wrong order. The larger finding is the split, drawn in the figure below: 0.55 dollars of tokens against 9.00 dollars of a person's attention per accepted result. Almost every lever of the fourth and sixth sections attacks the small number; the levers that attack the large one are the reliability posts of this series. The same funnel can rank the other way: [post 22](../22-evaluating-harnesses/index.md) works a week in which heavier verification triples the model spend and raises the escape rate, and the cheaper harness wins. The ledger decides, not the direction of the change.

![Computed stacked bars of dollars per unit shipped for two illustrative harnesses: A, no gate, 0.8 dollars of model tokens and 31.4 of review; B, a gate on every step, 0.6 and 9.4. The token segment is a sliver of each bar.](diagrams/04-cost-per-shipped.svg)

*The gate makes a run dearer and a shipped result a third of the price, and the tokens are the thinnest part of either bar.*

The published anchor is a cross-harness comparison with the model held fixed. Sunil Kumar Dash ran eight harnesses on one 25-task set, all on `moonshotai/kimi-k3` through OpenRouter, and estimated cost per successful task from 0.46 dollars to 1.96 at OpenRouter's list prices of 30 July 2026; the cheapest was not the weakest, passing 20 of 25 tasks against 19 for the dearest ("8 Best AI Agent Harnesses in 2026", Composio, 4 August 2026). The design, same model with only the harness changed, is the one [post 04](../04-harness-beats-model/index.md) grades firm, but the set is small, the costs are estimates over a 24-task usage slice, and one vendor ran it, so the fourfold spread is an order of magnitude rather than a ranking: same model, different harnesses, about four times the cost of getting a job done.

---

## 8. Harness-as-a-Service

For most of this series the harness has been built around a large language model (LLM) application programming interface (API), and [post 20](../20-sdk-landscape/index.md) surveyed the software development kits (SDKs) that ship a harness ready-made. Vivek Trivedy named where that leads in September 2025: "the core primitive for working with AI is shifting from the LLM API (chat style endpoints) to the Harness API (customizable runtimes). I call this Harness as a Service (HaaS)" ("The Claude Code SDK and the Birth of HaaS (Harness as a Service)", vtrivedy.com, 23 September 2025). Addy Osmani restated it, crediting Trivedy: "we're moving from building on LLM APIs (which give you a completion) to building on harness APIs (which give you a runtime)" ("Agent Harness Engineering", 19 April 2026).

"Renting a harness" covers two different purchases. **An SDK the team hosts** (the Claude Agent SDK, the OpenAI Agents SDK, LangGraph) is a library that owns the loop, the tool registry, the context policy and the hook lifecycle, and it runs on the team's machines. **A hosted agent runtime** runs the loop on the vendor's side, with the session, the isolation boundary, the tool plumbing and the state inside the service. Databricks makes the platform argument: "Rather than every team building and maintaining its own harness infrastructure", a shared layer for building, deploying, governing and evaluating agents ("What is an AI Agent Harness?", Databricks blog, 17 June 2026). The figure below draws where the vendor's boundary falls in each case and what each bills.

![Three columns. A model API keeps only the model inside the vendor's boundary and bills tokens. An SDK the team hosts runs the vendor's loop, tools, context management and hooks in the team's process and bills tokens plus the team's compute. A hosted runtime holds all of them and the session state inside the boundary and bills tokens plus runtime.](diagrams/02-llm-api-vs-haas.svg)

*Renting the loop moves it inside the vendor's boundary; the token bill keeps running beside the new runtime meter.*

| Tier | Named example | What the harness costs | Model tokens |
|---|---|---|---|
| Model API | any Messages or Completions endpoint | nothing: there is no harness to pay for | billed per token |
| SDK the team hosts | Claude Agent SDK, OpenAI Agents SDK, LangGraph | the team's own compute, plus the engineering to run it | billed per token |
| Hosted runtime, session-metered | Claude Managed Agents | 0.08 dollars per session-hour, accruing only while the session is `running` (Anthropic, "Pricing", consulted October 2026) | billed at standard rates, caching multipliers included |
| Hosted runtime, resource-metered | Amazon Bedrock AgentCore Runtime | 0.1276 dollars per virtual central processing unit (vCPU) hour and 0.0169 per gigabyte (GB) hour at the v2 consumption rates, billed per second, with no processor charge during input and output (I/O) wait (Amazon Web Services (AWS), "Amazon Bedrock AgentCore pricing", consulted October 2026) | not priced on that page; billed by the model service the agent calls |

The last column is the correction worth making explicit: the loop, the isolation, the session state and the tool plumbing cross the boundary, and the token bill does not, so budget ceilings stay the team's concern. Renting turns one meter into two.

`snippets/rent_or_build.py` works both meters against the running example, which took 36 seconds and 0.3293 dollars of tokens on a rolling breakpoint, and against an illustrative eight-hour long-horizon run, at one vCPU and 2 GB with the processor busy only while tools run inside the runtime, a third of the time:

```text
36-second run: session-metered $0.0008, resource-metered $0.0008 (0.24% of the short run's $0.3293 token bill)
eight-hour run: session-metered $0.6400, resource-metered $0.6107
eight hours with the CPU busy throughout: $1.29
```

The runtime meter is a rounding error for short interactive work, a quarter of one per cent, and a line item about twice a whole short run's token bill for anything that runs long.

---

## 9. Build against rent

Three questions settle most of the decision, and a fourth grows at every rung:

| Question | The **rent** case | The **build** case | Why it bites |
|---|---|---|---|
| **Volume** | any volume under the crossover worked below | runs in the millions a month *and* the runtime meter a material share of the bill | the crossover is arithmetic, and it sits far higher than intuition puts it |
| **Control** | the vendor's stop conditions, context policy and hook points fit the task | a bespoke stop condition, a custom verification gate, or a context strategy the vendor does not expose | a rented harness is a fixed loop |
| **Differentiation** | the harness is plumbing beneath a product whose value lies elsewhere | the loop, its tools and its hooks are what customers pay for | renting the moat means renting it from a supplier who also rents it to competitors |
| **Switching cost** | adopting an SDK, where the tie is a dependency | committing to a runtime, where the loop, hook interface, permission model and *trace format* are all the vendor's | the cost of leaving belongs in the sum before committing ([post 20](../20-sdk-landscape/index.md)) |

The figure below sets the three rungs on two axes, how much of the harness is bought and what it costs to leave. [Post 20](../20-sdk-landscape/index.md) sorts the same products on different axes, who owns the loop and whose models it runs; read together they are one ladder: **build**, **adopt an SDK**, **rent a runtime**, each rung buying back more of the work at a higher switching cost.

![Three cards climbing on two axes, more of the harness bought across and a higher cost to leave upward: build, owning all of it; adopt an SDK, buying the loop, tools, context management and hooks; rent a runtime, buying the session, isolation and state too. A note gives the crossover of 1.5 million runs a month.](diagrams/03-build-vs-rent.svg)

*Each rung buys back more of the work and costs more to leave; volume rarely decides which rung is right.*

Volume is the question that sounds decisive and decides least, so the crossover is worth doing rather than asserting. Rented cost scales with runs and owned cost is mostly fixed engineering:

```text
monthly_runs_at_crossover = owned_monthly_cost / (rented_per_run - own_per_run_infra)
```

Owning means owning the code: [post 20](../20-sdk-landscape/index.md) counts the union of this series' two builds at 803 implementation lines, 1,036 with tests, before compaction, retry semantics, a Model Context Protocol (MCP) client or a permission resolution order, each of which a mid-range SDK ships, plus the maintenance and the bugs. Take an illustrative 30,000 dollars a month for the people who would own it, a placeholder for a real number, against the runtime fee of a fifteen-minute session on the session meter:

```text
a fifteen-minute session: $0.02 of runtime; crossover at $30,000 a month: 1,500,000 runs a month
for eight-hour sessions at $0.64 each the crossover falls to 46,875 runs a month
```

Subtracting the compute the team would have paid for anyway raises the crossover further. At a few thousand runs a month a team sits orders of magnitude below it, so **volume rarely decides this**; control, differentiation and switching cost do. The exception is the long-running agent: a session that runs for hours raises the runtime fee per run by an order of magnitude or more and drags the crossover down with it, which is why the two meters of the eighth section are measured separately before anyone decides.

---

## 10. Metering a run that can be billed

Every number in this post comes out of small functions, and the meter belongs in the harness rather than in a spreadsheet. It sums tokens and seconds across a run, prices the cached, written and uncached input separately from the provider's own usage counts, and refuses the call that would cross the ceiling instead of reporting the crossing afterwards. From `snippets/run_meter.py`:

```python
# Per-run cost and latency meter at Claude Sonnet 4.6's rates (Anthropic, "Pricing", consulted October 2026).
IN_PRICE, OUT_PRICE = 3.00 / 1e6, 15.00 / 1e6   # dollars per input and per output token
READ, WRITE = 0.1, {"5m": 1.25, "1h": 2.0}        # multipliers of base input


def meter_run(calls, budget_usd=None, ttl="5m"):
    cost = seconds = 0.0
    for i, u in enumerate(calls):            # u: one call's provider-reported usage
        step = (u["input_tokens"] * IN_PRICE
                + u["cache_creation_input_tokens"] * IN_PRICE * WRITE[ttl]
                + u["cache_read_input_tokens"] * IN_PRICE * READ
                + u["output_tokens"] * OUT_PRICE)
        if budget_usd is not None and cost + step > budget_usd:
            return cost, seconds, f"budget: refused iteration {i + 1}"
        cost, seconds = cost + step, seconds + u["model_seconds"] + u["tool_seconds"]
    return cost, seconds, "completed"
```

The snippet writes the running example as one JavaScript Object Notation (JSON) line per model call, each carrying the `usage` fields the Anthropic Messages API returns, reads the file back as a harness's run log would be read, and meters it:

```text
captured run: 12 calls written as JSON lines and read back
no cache                               $0.9378  36.0s  completed
rolling breakpoint, five-minute tier   $0.3293  36.0s  completed
rolling breakpoint, one-hour tier      $0.4196  36.0s  completed
ceiling $0.25, five-minute tier        $0.2369  27.0s  budget: refused iteration 10
companion CostMeter: $0.2993 for 12 calls (fresh input at 1.0x, no write premium)
companion with budget_usd=0.25: stops after 11 calls at $0.2698 by its own count, $0.2976 at the write price
```

Three details carry the design. The meter reads the three input fields **per call**, as the provider bills them: `input_tokens` counts only the tokens after the last breakpoint, and "total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens" (Anthropic, "Prompt caching"), so a meter that treats `input_tokens` as the whole request under-counts every cached run. The budget test runs *before* the spend, so the ceiling refuses iteration 10 rather than reporting it, the reserve of [post 19](../19-loop-engineering/index.md). And the five-minute line reproduces the rolling-breakpoint figure of the fifth section exactly, while the one-hour line shows what the longer lifetime costs a run that never needed it: 0.4196 dollars against 0.3293.

A tested meter ships with the capstone at [`code/26-coding-agent/src/coding_agent/cost.py`](../../code/26-coding-agent/src/coding_agent/cost.py): a `CostMeter` with `budget_usd` and `over_budget()`, wired into the capstone driver as a stop condition, so the economic control and the loop exit are one object ([post 26](../26-capstone-coding-agent/index.md)). The last two lines above run it on the same calls and show its two simplifications. It charges written tokens at 1.0× rather than the 1.25× write premium, so it reads 0.2993 dollars for a run that costs 0.3293. And its test is `cost() >= budget_usd` at the top of an iteration, so with a 0.25-dollar ceiling it lets iteration 11 start and stops at 0.2698 dollars by its own count, 8% over; at the write price those eleven calls cost 0.2976 dollars, 19% over. Its `add` takes the total input and the cached part, so a caller passing the provider's `input_tokens` field as the total would under-count it as well.

---

## 11. Make it run

The exercise for this post is to run the meter over one captured run, re-derive the arithmetic at current published rates, and compute cost per successful run for a ten-run set. The three snippets run offline from the series root, the second importing the capstone's `CostMeter` unchanged:

```bash
uv run python posts/23-economics-haas/snippets/loop_cost.py
uv run python posts/23-economics-haas/snippets/run_meter.py
uv run python posts/23-economics-haas/snippets/rent_or_build.py
```

Each prints the output quoted above in well under a second. Every rate sits at the top of its file with the page it came from, so re-deriving at a new rate is an edit and a rerun. To try a variation, set `GROWTH` in `loop_cost.py` to 1,000, the size of a turn that offloads its tool output, and watch the uncached and rolling lines move closer together.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A meter fed the wrong input count.** The meter adds the provider's `input_tokens` as the request's input; with caching on, that field holds only the tokens after the last breakpoint, so the dashboard shows a run costing a fraction of its invoice.
- **A ceiling checked after the call.** The run is stopped at its ceiling and the invoice still exceeds it, by the cost of the late, large iteration that crossed the line.
- **A one-line edit that empties the cache.** A timestamp added to the system prompt makes every request a full write on the largest prefix; the bill rises by a multiple while every response looks the same, and only the cache-read count drops.
- **A cache that goes cold between turns.** A test suite or an approval wait outlasts the five-minute lifetime; the next turn writes the whole history again, and a cached run can cost more than an uncached one.
- **A cheap model that costs more.** Routine turns are routed to a cheaper tier, each one lands uncached, and the run's bill does not fall.
- **A ceiling priced at the value of a success.** Runs are allowed to spend what a resolved task is worth, the failures are billed at the same ceiling, and the agent loses money at a healthy success rate.

---

## Common pitfalls

1. **Pricing a run like a single call.** A run pays once per iteration over a growing context, so an estimate from one call's price can be off by an order of magnitude.
2. **Caching the head instead of the history.** In the running example a static head saved 15% against 65% for a breakpoint that moves with the conversation.
3. **Rewriting the history mid-run.** A compaction, a re-sorted tool list or an injected timestamp turns cached reads back into writes on the largest part of the bill.
4. **Ranking harnesses by cost per run.** A harness that spends more per run and succeeds more often can cost a third as much per unit shipped.
5. **Optimising the small number.** Model tokens can be a rounding error beside a person's review time, as in the worked pair of harnesses.
6. **Renting the differentiator, or building the plumbing.** If the harness is the product, renting hands the moat to a supplier; if it is not, owning it delays the product whose value lies elsewhere.

---

## Further reading

- Anthropic, "Prompt caching", Claude Platform documentation (consulted October 2026): the prefix rule, up to four breakpoints, automatic caching, the lifetime tiers and refresh on read, and the three usage fields.
- Anthropic, "Pricing" (consulted October 2026): per-model token rates, the cache multipliers, and session-hour pricing for Claude Managed Agents.
- Amazon Web Services, "Amazon Bedrock AgentCore pricing" (consulted October 2026): a resource-metered hosted runtime, with model inference billed by the model service.
- Vivek Trivedy, "The Claude Code SDK and the Birth of HaaS (Harness as a Service)" (vtrivedy.com, 23 September 2025), and Addy Osmani, "Agent Harness Engineering" (19 April 2026): Harness-as-a-Service, named and restated.
- Sunil Kumar Dash, "8 Best AI Agent Harnesses in 2026: Performance, Cost, and Speed Compared" (Composio, 4 August 2026): cost per successful task across eight harnesses with the model held fixed.
- Databricks, "What is an AI Agent Harness?" (Databricks blog, 17 June 2026): the harness as a shared platform layer.
- Faros AI, "Harness engineering: A guide to building better AI coding agents" (22 May 2026, updated 15 July 2026): the production metrics behind the denominator.
- `ctx-005` (`context-engineering`, "The economics of context: pricing, caching, and latency"): token cost and prompt caching for a single call, the basis of this run-level view.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 24 - Build #1: a minimal agent harness from scratch](../24-build-minimal-harness/index.md):** the loop, tools and ceilings assembled into a runnable harness whose counters this meter reads.
- **[Post 26 - Capstone: a long-running, trusted coding-agent harness](../26-capstone-coding-agent/index.md):** the cost meter wired into a long-horizon driver as a stop condition.
