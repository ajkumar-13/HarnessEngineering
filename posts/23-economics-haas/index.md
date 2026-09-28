# 23 · The economics of a harness & Harness-as-a-Service

> **TL;DR.** A single completion has one price; an agentic run has that price multiplied by the number of loop iterations, and each iteration re-reads a context that grows every step. Harness economics are dominated by two levers: how many times the loop turns, and how cheaply the accumulated history is re-read. Budget ceilings cap the first, and a *rolling* cache breakpoint flattens the second, turning a bill that would grow with the square of the iteration count into one that grows nearly linearly. The number that decides whether an agent ships is not cost per run but cost per *successful* run. This post also covers the shift from large language model (LLM) application programming interfaces (APIs) that return a completion to Harness-as-a-Service (HaaS) products that return a runtime.
>
> **After reading this you will be able to:**
> - Price an agentic run from its iteration count, its growing context and its cache behaviour, three ways over.
> - Use budget ceilings, cache discipline and model routing as economic controls rather than safety rails.
> - Decide when to run your own harness and when to rent a HaaS runtime, from arithmetic rather than instinct.

![Input tokens sent at each of twelve loop iterations. Each bar has a grey lower segment for the part of the context already cached and re-read that turn, which grows every iteration, and a blue upper segment for the fresh tokens written, a flat 3,100 on every bar after the first. Iteration 1 is entirely fresh at 6,000 tokens; iteration 12 sends 40,100, of which 37,000 is re-read. A panel gives the run total of 276,600 input tokens, 236,500 of them cached, 40,100 fresh and 7,200 output, and a second prices it: 12 iterations at $0.94 uncached against $0.33 on a rolling cache, 40 iterations at $8.33 against $1.60.](diagrams/01-loop-cost.svg)
*Cost scales with iterations and with a context that grows each step; caching flattens the re-read of the stable prefix.*

The Context Engineering series priced the single call: how many tokens enter one window, what the output costs, and how caching cuts a repeated prefix (Context Engineering, Post 05). This post is the run-level companion: the unit is one **run** across many loop iterations, and the number that matters is the price of the whole machine turning until it stops. Every dollar figure below is arithmetic on the one price table in §4, so treat them as illustrative and re-derive them before any of them goes near a budget.

---

## 1. The cost of a loop

A single completion is priced once: input tokens in, output tokens out, one invoice line. An agentic run is that invoice multiplied by the number of times the loop turns ([Post 03](../03-the-agent-loop/index.md)). A task resolving in twelve iterations pays for twelve model calls, which is the first fact of harness economics.

The second fact is worse, because the per-iteration cost is not constant. Each turn appends the previous model output and every tool result to the history, so the context grows monotonically. Iteration one might send 6,000 tokens; iteration twelve sends about 40,000, because it re-reads everything accumulated so far, and the run pays for that whole history *again* at every step. Those figures are the series' running example rather than a measurement.

The third fact is the asymmetry between the two token classes. Output costs roughly five times input at every tier, because ingesting a prompt is one parallel pass and generating an answer is one forward pass per token (Context Engineering, Post 05 §3). In a single call that argues for a lower `max_tokens`. In a loop it compounds, because **every output token is paid once at the expensive rate and then re-read as an input token on every later turn**. A 600-token narration emitted at iteration three costs about $0.009 to generate and is re-read on nine later turns: 5,400 input tokens, about $0.016 uncached. The re-reading costs nearly twice the writing.

Tool results obey the same rule and are far larger. A 12,000-token test-suite log returned at iteration three sits in the request for iterations four to twelve: 108,000 input tokens, about $0.32 at the mid-tier rate, which is a third of the entire uncached bill for that run (§5) and still about $0.07 once caching is configured (§6). That is the economic case for tool-output offloading, the cheapest rung of [Post 09](../09-context-management-loop/index.md) §3 and the same move [Post 08](../08-state-filesystem-git/index.md) §3 prices at an 800-fold reduction in what a run carries.

Together the three give the run-level shape. Cost is roughly the iteration count times the *average* context size, and the average grows with the count, so uncached the input bill scales with **the square of the iteration count**: doubling the iterations roughly quadruples the input spend. Compaction is therefore an economic instrument and not only a context-window one, though the trim is not free, since rewriting the message list also rewrites part of the cached prefix (§4, §6). That quadratic term is this section's headline and §4 is what mostly discharges it: left unqualified it is ten times more alarming than a well-built loop actually is.

---

## 2. Latency budget for an autonomous run

Wall-clock time obeys a related multiplication. A run's latency is dominated by its sequential model calls plus its sequential tool calls, because **the loop's decision chain is serial**: the model cannot choose iteration two's action until iteration one's tool result returns. Twelve iterations of a two-second model call and a one-second tool call is thirty-six seconds of sequential work, before any slow tool is counted.

The chain is serial; the work inside a link is not. A model can emit several `tool_use` blocks in one turn, and a harness running them concurrently collapses three one-second waits into one ([Post 06](../06-tools-bash-code/index.md) §9). Across iterations, sub-agent fan-out shortens the wall clock to the slowest worker plus synthesis rather than the sum, and pays for it in tokens: five contexts each carrying a full preamble, priced in [Post 16](../16-multi-agent-orchestration/index.md) §6 and [Post 17](../17-parallel-agents-shared-repo/index.md) §8. Fan-out is a latency purchase paid in tokens, so it fits a budget generous in dollars and tight in minutes.

The growing context stretches latency as well as cost, because a larger input takes longer to prefill, so late iterations are slow twice over. A cache read skips prefill for the cached span, so §4's lever flattens the wait as well as the bill (Context Engineering, Post 05 §5): at iteration twelve the model prefills about 3,100 fresh tokens instead of 40,100. One interactive optimisation does not transfer. Streaming hides decode time by showing tokens as they arrive, but inside a loop it buys nothing, because the harness cannot dispatch a tool until the complete `tool_use` block has arrived. It pays only on the final answer, where a human is reading.

Where the run sits then decides the budget, and the three modes differ by orders of magnitude rather than by degree.

| Mode | Who is waiting | Latency budget | Iterations that fit | What the budget buys |
|---|---|---|---|---|
| **Interactive** | a human at a prompt | seconds to about a minute | roughly 5 to 15 | one attempt, a fast gate, an early escalation |
| **Background** | a queue | minutes to hours | tens to low hundreds | retries, full verification, a sub-agent or two |
| **Long-horizon** | a schedule | hours to days | thousands, across many contexts | resets, handoffs, and the [Post 18](../18-long-horizon-ralph/index.md) loop |

A harness serving two of these needs a ceiling for each; confusing them ships a tool that hangs or a job that quits early. [Post 19](../19-loop-engineering/index.md) §7 makes the same split when allocating a budget across composed loops: a run with a human waiting wants predictable per-task limits, a dispatched background run can afford a shared pool.

---

## 3. Budget ceilings as guardrails

Loop engineering introduced the token ceiling and the wall-clock ceiling as layered exits that stop a run before it burns the whole budget ([Post 19](../19-loop-engineering/index.md) §2). That post framed them as safety rails. Seen from here they are equally an **economic** control, and the reframing changes how you set the number. Be precise about what is counted: a ceiling of 200,000 *cumulative billed input-plus-output tokens across the whole run* is a promise about spend, and a different quantity from the 200,000-token context window a single call may occupy. A wall-clock ceiling is the same promise for latency and for rented compute. Both convert an open-ended liability into a bounded line item.

You do not pick a ceiling by guessing a safe maximum; you derive it from what one run is worth, and the worth of a run is not the worth of a success, because failures are billed too. If a resolved task is worth $2.00 and the harness resolves 55% of what it attempts, the expected value of *starting* a run is $1.10, and that is the ceiling the arithmetic supports. Pricing it at the value of a success funds the failures out of the margin; §7 makes that denominator explicit.

Two ways the instrument fails silently are worth carrying over from Post 19. The first is **enforcement in arrears**. A ceiling tested after the call overshoots by one iteration, and §1's growth curve means the iteration crossing the line is a late and expensive one: uncached, the running example's twelfth iteration costs about $0.129 against the first iteration's $0.027, so the overshoot is nearly five times what an early iteration would have cost. The fix is to reserve for the estimated next call and stop before it ([Post 19](../19-loop-engineering/index.md) §4). Caching shrinks the error sharply, because with a rolling breakpoint the per-iteration cost is nearly flat: about $0.0315 at the first iteration and $0.0317 at the twelfth. The second is **spend with nothing to show for it**. A run killed at the ceiling with no durable checkpoint forfeits the entire amount ([Post 19](../19-loop-engineering/index.md) §8; [Post 08](../08-state-filesystem-git/index.md)), which makes checkpointing an economic requirement rather than a convenience: a resumable guard exit turns a hard stop into a pause you can price a second tranche against.

A cheaper instrument sits beside the ceiling: a ceiling caps what a run *can spend*, and a per-step verification gate caps what it can *waste*. [Post 11](../11-verification-loops/index.md) §5 prices the same run with an error entering at iteration two and finds that losing 83% of the steps costs 95% of the spend.

---

## 4. Prompt caching across loop iterations

The single biggest lever on run cost is prompt caching, and it works differently in a loop than in a single call. The mechanism is a **prefix match**: the provider stores the processed state for a contiguous prefix measured from the first byte, so any change at position *N* invalidates everything from *N* onward (Anthropic, "Prompt caching", 2025–26). Prices at the series' reference mid tier of $3 per million input tokens and $15 per million output tokens (Anthropic, "Pricing", 2026):

| Token class | Multiplier on base input | Mid-tier price per million | When you pay it |
|---|---|---|---|
| Fresh input | 1.0× | $3.00 | no cache configured, or a miss |
| Cache write, 5-minute time-to-live (TTL) | 1.25× | $3.75 | the first request that stores a span |
| Cache write, 1-hour TTL | 2.0× | $6.00 | the same, on the long-lived tier |
| Cache read (hit) | 0.1× | $0.30 | every later request that reuses the span |
| Output | n/a | $15.00 | once, at generation, then re-read as input |

A single call has nothing to reuse *within itself*; caching pays there only across repeated calls sharing a prefix (Context Engineering, Post 05 §6). In a loop the reuse is structural, because the prefix is re-read every iteration whether or not any traffic repeats.

### The prefix is not the head; it is everything that already happened

The usual mental model treats the cacheable region as a small static head of system prompt and tool schemas. That is the single-call model, and in a loop it leaves most of the money on the table, because **a loop only ever appends**: nothing before the newest turn changes, so the entire prior conversation is a stable prefix for the next request.

Providers expose that directly. A request may define up to four cache breakpoints, so spans changing at different frequencies cache separately, and the agent pattern is to keep the last one on the final block of the most recently completed turn and advance it every iteration. Automatic caching does the advancing for you: "the cache point moves forward automatically as conversations grow. Each new request caches everything up to the last cacheable block, and previous content is read from cache" (Anthropic, "Prompt caching", 2025–26). Spend the four deliberately, because each layer changes on its own clock:

```text
  request layout, front (most stable) → back (most volatile)
  ┌────────────────────────────────────────────────┐
  │ TOOLS      schemas, change on deploy      ◀ bp1 │
  │ SYSTEM     prompt + durable rules         ◀ bp2 │
  │ CONTEXT    spec, memory file, exemplars   ◀ bp3 │
  ├─── everything above is written once per run ────┤
  │ HISTORY    turns 1 … n-1, frozen               │
  │ TURN n-1   last completed turn            ◀ bp4 │  ← this one moves
  ├─────────── advanced every iteration ────────────┤
  │ TURN n     the observation just returned        │
  └────────────────────────────────────────────────┘
```

This is what makes §1's quadratic term survivable: the accumulated history is still re-read every turn, but at 0.1× rather than 1.0×, so the term growing with the square of the iteration count grows against a rate ten times smaller.

### What breaks it

**A rewrite of the tail.** Compaction, a re-sorted tool list, an injected timestamp, a memory file edited mid-run: each changes bytes already cached, so everything after the change is recomputed. This is the most expensive invisible mistake a loop makes, and the multiplier is the reason: it turns the largest line on the bill from a 0.1× read into a 1.25× write, a more than twelvefold jump on the same tokens. Nothing in the response says so; only the provider-reported `cache_read_input_tokens` count does, which is why it belongs on the `model.call` span beside the ordinary input and output counts ([Post 21](../21-observability-traces/index.md) §2). [Post 09](../09-context-management-loop/index.md) §7 works the exact bill for a compaction, which is more forgiving than the usual telling: tools and system render before messages, so what you lose is the history's cache from the rewrite onward plus the write premium on the new prefix. Hence **compact rarely and deeply**, since a shallow compaction pays nearly the full premium for almost no read saving.

**The clock.** The default TTL is five minutes, measured from the *start* of the request that writes or reads the entry, so generation time counts against it, and a read refreshes it for free (Anthropic, "Prompt caching", 2025–26). A loop whose tool call is a full test suite or a human approval gate can idle past the TTL, and the next turn is a cold write on the largest context yet assembled. [Post 18](../18-long-horizon-ralph/index.md) §4 prices the limiting case: iterating eight minutes apart on the default tier costs about 25% *more* for a frozen prefix than no caching at all. The one-hour tier costs 2.0× on the write against 1.25×, so it pays whenever the alternative is more than one extra cold write per run.

---

## 5. One run, priced three ways

Set the running example out in full. Twelve iterations; the first request sends 6,000 tokens; each turn appends about 600 tokens of output and 2,500 of tool result, so the request grows by 3,100 tokens a turn and the twelfth sends 40,100. Total input is 276,600 tokens and total output 7,200, priced at the §4 mid-tier rates. The figures are illustrative.

| Iteration | Input tokens sent | Of which already cached | Fresh tokens written | Output tokens |
|---|---|---|---|---|
| 1 | 6,000 | 0 | 6,000 | 600 |
| 2 | 9,100 | 6,000 | 3,100 | 600 |
| 6 | 21,500 | 18,400 | 3,100 | 600 |
| 12 | 40,100 | 37,000 | 3,100 | 600 |
| **Run total** | **276,600** | **236,500** | **40,100** | **7,200** |

Three ways of paying for it:

- **No caching.** 276,600 input at $3 per million is $0.830; 7,200 output at $15 per million is $0.108. **$0.938.**
- **A static head.** Freeze a 5,000-token head of tool schemas and system prompt: one write at 1.25×, eleven reads at 0.1×, and the other 216,600 input tokens at full price. **$0.793**, a saving of 15%. The head is cached; the history, which is where the tokens actually are, is not.
- **A rolling breakpoint.** The whole prior conversation is cached each turn: 236,500 tokens read at 0.1×, 40,100 written at 1.25×, the same output. **$0.329**, about a third of the uncached bill, with the input side alone falling from $0.830 to $0.221.

The gap between the second and third rows is the whole of §4: a static head saves a seventh, the rolling breakpoint nearly two thirds, because only the second applies to the term that actually grows. What matters more than the ratio is how each behaves as the run lengthens. Run the same model out to forty iterations, where the request has grown to 126,900 tokens:

| Run length | Uncached | Rolling breakpoint | Uncached, per iteration |
|---|---|---|---|
| 12 iterations | $0.94 | $0.33 | $0.078 |
| 40 iterations | $8.33 | $1.60 | $0.208 |
| **Growth factor** | **8.9×** | **4.8×** | **2.7×** |

Tripling the iteration count multiplies the uncached bill by nearly nine, which is §1's quadratic term arriving on an invoice. With a rolling breakpoint the same tripling costs 4.8×, close to linear, and the cache's advantage *widens* with run length: 65% saved at twelve iterations, 81% at forty. Long autonomous runs are affordable specifically because the growing part of the context is billed at a tenth. A harness with no caching configured has not made a run 15% dearer; it has changed the exponent.

---

## 6. Where the money goes, and the levers that move it

**Context management, priced.** [Post 09](../09-context-management-loop/index.md) gives four corrective moves in increasing order of aggressiveness. With a money column attached they sort differently from the way they are usually taught.

| Rung | Effect on the re-read bill | Effect on the cache | When it pays |
|---|---|---|---|
| **Offload** at the tool boundary | the bytes never enter, so are never re-read | untouched: nothing already cached changes | almost always; the only free rung |
| **Clear** spent tool results | stops the re-read from here on | breaks the prefix from the cleared position, so batch the clears | when large results are genuinely spent |
| **Compact** older turns | stops the re-read, and costs a model call | write premium on the whole surviving prefix | rarely and deeply |
| **Reset** behind a handoff | history goes to zero | starts over: a full write on the new window | when the task outgrows one window ([Post 18](../18-long-horizon-ralph/index.md)) |

The offload is the worked line: §1's 12,000-token test log adds about $0.32 to an uncached run and about $0.07 to a cached one, and offloading it at the tool boundary avoids both while returning a pointer the agent can re-read on demand.

**Model routing, and why it is not free at the run level.** The tier is a per-*iteration* decision: deciding whether to continue, summarising a tool result and classifying an error are cheap turns, and the cheap tier costs about a third of the mid tier, at $1 and $5 per million against $3 and $15 (Anthropic, "Pricing", 2026). But routing a turn to a different model means a different cache, and that usually swallows the saving. Take four of the twelve iterations out of the cached conversation and run them uncached on the cheap tier: 98,400 input tokens at $1 per million plus 2,400 output at $5 per million is **$0.110**, against **$0.108** for leaving them where they were. The tier discount is about 3× and the cache discount 10×, so lifting a turn out of a warm conversation is close to a wash and can be a loss. Route *roles* instead: a planner, a generator and an evaluator are already separate calls with separate stable prefixes ([Post 12](../12-planner-generator-evaluator/index.md)), each able to sit on its own tier and keep its own warm cache.

---

## 7. Cost per run is the wrong number

Every figure so far is cost per *run*, and a run that fails costs full price and delivers nothing. The business number is total spend divided by the work that actually shipped, which is the staged funnel [Post 22](../22-evaluating-harnesses/index.md) §10 builds: first-pass success rate, defect-escape rate, dollars per merged pull request (PR) (Faros AI, 2026). That supplies the denominator every earlier number was missing, and the conversion is one division and two corrections:

```
cost_per_accepted  = cost_per_run / first_pass_success_rate
cost_per_shipped   = (cost_per_accepted + review_cost) / (1 - defect_escape_rate)
```

Worked on two harnesses that differ only in whether a verification gate runs on every step ([Post 11](../11-verification-loops/index.md)). The gate makes each run *more* expensive, because it adds iterations. Review time is priced at a placeholder $90 an hour; substitute your own loaded rate, because it is the term that dominates.

| | A: no verification gate | B: gate on every step |
|---|---|---|
| Model cost per run | $0.33 | $0.52 |
| First-pass success rate | 48% | 84% |
| Model cost per accepted result | $0.69 | $0.62 |
| Human review per accepted result | 18 min, so $27.00 | 6 min, so $9.00 |
| Defect-escape rate | 14% | 4% |
| **Cost per unit of work shipped** | **$32.20** | **$10.02** |

B costs 58% more per run and about a third as much per unit shipped, so cost per run alone can rank two harnesses in the wrong order. The second finding is larger: the model bill is a rounding error beside review time, $0.62 of tokens against $9.00 of a person's attention. Almost every lever in §4 and §6 attacks the small number, and the levers that attack the large one are the reliability chapters of this series, which is why an economics post spends most of its links pointing at them.

The empirical anchor is a cross-harness comparison with the model held fixed. Across eight harnesses on a 25-task set, all running `moonshotai/kimi-k3` through the same provider, estimated cost per successful task ranged from $0.46 to $1.96, and the cheapest was not the weakest: the $0.46 harness passed 20 of 25 tasks against the $1.96 one's 19 (Kumar Dash, 2026). Those figures are one vendor's blog on a small task set at a single day's list prices, so treat them as an order of magnitude. The shape is [Post 04](../04-harness-beats-model/index.md)'s thesis as a ledger entry: same model, different harnesses, a fourfold difference in the cost of getting a job done.

---

## 8. Harness-as-a-Service

For most of this series the harness has been something you build, assembled around a model API. As Osmani puts it, the field is moving from building on LLM APIs, which give you a completion, to building on harness APIs, which give you a *runtime* (Osmani, 2026). The software development kit (SDK) survey previewed this as the field's natural commercial endpoint ([Post 20](../20-sdk-landscape/index.md) §9).

![Two boxes side by side. On the left, an LLM API: you send a prompt and receive a completion, while the loop, tools, context management, and hooks all sit outside the service as your responsibility. On the right, a Harness API or HaaS: you send a task and receive an agent run, with the loop, tools, context management, and hooks all living inside the service boundary. Below them, renting shown as four tiers rather than two, from a model API with no harness to pay for, through an SDK you host, to session-metered and resource-metered hosted runtimes, with model tokens billed to you in the first three and separately in the last. A panel prices the same 36-second run that cost $0.329 in tokens on both meters: $0.0008 of runtime, against $0.64 for an eight-hour session and $0.87 metered by resource.](diagrams/02-llm-api-vs-haas.svg)
*An LLM API returns a completion and leaves the loop to you; a harness API returns a runtime with the loop, tools, context, and hooks inside the boundary.*

"Renting a harness" covers two quite different purchases, and §9 turns on telling them apart. **A harness SDK you host** (the Claude Agent SDK, the OpenAI Agents SDK, LangGraph) is a library owning the loop, the tool registry, the context policy and the hook lifecycle, and it runs on your machines; Osmani's own exemplars sit here. **A hosted agent runtime** (Claude Managed Agents, AWS Bedrock AgentCore, Google Vertex AI Agent Engine, Microsoft Foundry Agent Service) runs the loop on the vendor's side, with the session, the isolation boundary, the tool plumbing and the state inside the service. Databricks makes the same argument from the platform side: the harness is a product with prebuilt layers you assemble rather than a thing every team writes ([Post 02](../02-anatomy-of-a-harness/index.md); Databricks, 2026). The vendors agree that the harness is the product and disagree entirely on the unit of sale.

| Tier | Named example | What you pay for the harness | Model tokens |
|---|---|---|---|
| Model API | any Messages or Completions endpoint | nothing; there is no harness to pay for | billed to you per token |
| SDK you host | Claude Agent SDK, OpenAI Agents SDK, LangGraph | your own compute, plus the engineering to run it | billed to you per token |
| Hosted runtime, session-metered | Claude Managed Agents | $0.08 per session-hour, metered only while the session is `running` (Anthropic, "Pricing", 2026) | billed to you at standard rates, caching multipliers included |
| Hosted runtime, resource-metered | AWS Bedrock AgentCore Runtime | $0.0895 per vCPU-hour and $0.00945 per GB-hour, with Gateway at $0.005 per 1,000 API invocations (AWS, 2026) | billed separately through the underlying model service |

The last column is the correction worth making explicitly. Budget ceilings do **not** become the vendor's concern: the loop, the isolation, the session state and the tool plumbing cross the boundary, and the token bill does not. Renting turns one meter you understand into two that do not compose.

Work both against §5's run, which took 36 seconds and cost $0.329 in tokens. On a session-metered runtime the runtime charge is 36 seconds at $0.08 an hour, or **$0.0008**: a quarter of one per cent of the run. A long-horizon run of the [Post 18](../18-long-horizon-ralph/index.md) kind holding a session open for eight hours costs **$0.64** on the session meter, or **$0.87** on a resource meter at one vCPU and 2 GB, comparable to the whole token bill of the short run. The runtime meter is a rounding error for short interactive work and a first-class line item for anything that idles or runs long, and the two answer to different halves of this post: the token meter to §4 and §6, the runtime meter to §2.

---

## 9. Build-versus-rent economics

Three questions settle most of it and the third usually decides the rest, with a fourth that grows at every rung.

![Three cards side by side, one per question. Volume: rent at a few thousand runs a month where renting saves months of engineering, build at millions where the aggregate margin exceeds the cost of a team owning the harness. Control: rent when the vendor loop, context strategy and hooks already cover the task, build when you need a bespoke stop condition, a custom verification gate, or a context strategy nobody exposes. Differentiation, marked as the deciding question: rent when the harness is undifferentiated plumbing under a product whose value lies elsewhere, build when it is your product, because renting it means renting your moat from a supplier who also rents it to your competitors.](diagrams/03-build-vs-rent.svg)
*Two questions price the decision; the third one makes it. Volume and control are arithmetic you can run, and both usually say rent. Differentiation is the one that overrides them.*

| Question | You are in the **rent** case if | You are in the **build** case if | Why it bites |
|---|---|---|---|
| **Volume** | almost always; see the crossover below | monthly runs are in the millions *and* the runtime meter is a material share of the bill | the crossover is arithmetic, and it sits far higher than most teams guess |
| **Control** | the vendor's stop conditions, context policy and hook points fit the task | you need a bespoke stop condition, a custom verification gate, or a context strategy the vendor does not expose | a rented harness is a fixed loop, and the ceiling of rent is a hard one |
| **Differentiation** | the harness is plumbing beneath a product whose value lies elsewhere | the loop, its tools and its hooks are what customers pay for | renting your moat means renting it from a supplier who also rents it to competitors |
| **Switching cost** | you are adopting an SDK, where the tie is a dependency | you are committing to a runtime, where the loop, hook API, permission model and *trace format* are all the vendor's | exit cost belongs in the sum before you commit ([Post 20](../20-sdk-landscape/index.md) §8) |

The figure sets the three out side by side because they are not weighted equally: volume and control are cost questions, and the crossover below shows how rarely volume decides anything, whereas differentiation is a question about what your product *is*. Read with [Post 20](../20-sdk-landscape/index.md) §6, the two rules are one ladder: **build**, **buy an SDK**, **rent a runtime**, each rung buying back more work at a higher switching cost. Do the crossover rather than asserting it: rented margin scales with runs and owned cost is mostly fixed engineering, so

```
monthly_runs_at_crossover = owned_monthly_cost / (rented_per_run - your_own_per_run_infra)
```

Substitute the §8 figures. A fifteen-minute session on a session-metered runtime costs $0.02. Owning the harness instead means owning the code Post 20 prices at roughly 1,250 lines to reach a mid-range SDK's feature set, and past 2,000 once compaction, retry semantics, a Model Context Protocol (MCP) client and a permission resolution order are added, plus its maintenance and its bugs. Take a fully loaded $30,000 a month for the people who would own it, a placeholder to replace with your own number. The crossover is $30,000 / $0.02, or **1.5 million runs a month**, higher still once you subtract the compute you would have paid for anyway.

That is not where the volume argument usually lands. Most teams sit three orders of magnitude below the crossover, so **volume almost never decides this**; control, differentiation and switching cost do. The exception is the resource-metered tier, where a long-running or memory-hungry agent pushes the per-run figure an order of magnitude higher and drags the crossover down with it, which is why §8's two meters must be measured separately first.

---

## 10. Metering a run you can actually bill

Every number in this post came out of one small function, and it belongs in the harness rather than in a spreadsheet. It sums tokens and seconds across a run, prices the cached and fresh portions separately at the §4 multipliers, and refuses the call that would breach the ceiling rather than reporting the breach afterwards.

```python
# Per-run cost and latency meter, at the mid-tier reference rates of §4
# (Anthropic, "Pricing", 2026). Re-derive against current rates before use.
IN_PRICE    = 3.00 / 1_000_000   # $ per input token
OUT_PRICE   = 15.00 / 1_000_000  # $ per output token
CACHE_READ  = 0.10               # a cache hit costs 0.1x base input
CACHE_WRITE = 1.25               # a 5-minute cache write costs 1.25x (1h is 2.0x)

def meter_run(steps, budget_usd=None):
    cost = seconds = 0.0
    for i, s in enumerate(steps):
        cached  = s["cached_tokens"]              # provider-reported, per call
        written = s["input_tokens"] - cached      # new bytes, cached for next turn
        step = (cached * IN_PRICE * CACHE_READ
                + written * IN_PRICE * CACHE_WRITE
                + s["output_tokens"] * OUT_PRICE)
        if budget_usd is not None and cost + step > budget_usd:
            return cost, seconds, "budget-exhausted before iteration %d" % (i + 1)
        cost, seconds = cost + step, seconds + s["model_seconds"] + s["tool_seconds"]
    return cost, seconds, "completed"

run = [{"input_tokens": 6000 + 3100 * i,
        "cached_tokens": 0 if i == 0 else 6000 + 3100 * (i - 1),
        "output_tokens": 600, "model_seconds": 2.0, "tool_seconds": 1.0}
       for i in range(12)]

for budget in (None, 0.25):
    print("$%.4f  %.1fs  %s" % meter_run(run, budget))
```

```text
$0.3293  36.0s  completed
$0.2369  27.0s  budget-exhausted before iteration 10
```

Three details are worth naming. `cached_tokens` is read **per call** rather than fixed once for the run, which is the only way a rolling breakpoint can be expressed; a scalar prefix size hard-codes the static-head model §4 exists to correct. The budget test runs *before* the spend, so the ceiling is a ceiling and not a notification ([Post 19](../19-loop-engineering/index.md) §4). And the first line reproduces §5's rolling-breakpoint figure exactly, which is the point of having the meter at all.

A tested version ships with the capstone at [`code/26-coding-agent/src/coding_agent/cost.py`](../../code/26-coding-agent/src/coding_agent/cost.py): a `CostMeter` carrying the same cached, fresh and output splits, with `budget_usd` and `over_budget()` wired into the capstone driver as a stop condition, so the economic control and the loop exit are one object. It simplifies in two places worth knowing before you copy it, and [Post 26](../26-capstone-coding-agent/index.md) §8 prices both: fresh input is charged at 1.0× rather than at the write premium above, and the test is `spent >= ceiling` at the top of an attempt, so the run still overshoots by one call.

---

## Common pitfalls

- **Pricing a run like a single call.** A completion has one price; a run pays that price once per iteration over a growing context, so a naive estimate can be off by an order of magnitude (§1).
- **Treating all tokens as one price.** Output costs about five times input and is then re-read as input on every later turn, so verbosity is charged twice over (§1).
- **Caching the head instead of the history.** A static prefix of tools and system prompt saved 15% of the running example against 65% for a breakpoint that advances with the conversation (§4, §5).
- **Rewriting the tail mid-run.** Compaction, a re-sorted tool list or an injected timestamp turns cached reads back into writes on the largest part of the bill, and only the cache-read token count shows it (§4).
- **Setting ceilings by intuition, or from the value of a success.** Derive the ceiling from value times success rate and enforce it before the call, and give interactive and background runs separate numbers (§2, §3).
- **Optimising the small number.** Model tokens are often a rounding error beside human review time, so a harness that raises per-run cost and raises first-pass success can be decisively cheaper per unit shipped (§7).
- **Renting your differentiator, or building undifferentiated plumbing.** If the harness is your product, renting hands your moat to a supplier who also rents it to competitors; if it is not, owning the plumbing delays a product whose value lies elsewhere (§8, §9).

---

## Further reading

- Osmani, A., "Agent Harness Engineering" (2026): the shift from LLM APIs that give you a completion to harness APIs that give you a runtime.
- Anthropic, "Prompt caching" documentation (2025–26): the prefix-match rule, the four-breakpoint budget, automatic advancing breakpoints, the TTL tiers and refresh-on-read.
- Anthropic, "Pricing" documentation (2026): per-tier token rates, the cache-write and cache-read multipliers, and session-hour pricing for a hosted agent runtime.
- AWS, "Amazon Bedrock AgentCore pricing" (2026): a resource-metered agent runtime, with model tokens billed separately from it.
- Kumar Dash, S., "8 Best AI Agent Harnesses in 2026" (Composio, 2026): cost per successful task across eight harnesses with the model held fixed.
- Databricks, "What is an AI Agent Harness?" (2026): the harness as a platform product with prebuilt layers rather than a per-team rewrite.
- Faros AI, "Harness Engineering" (2026): the staged production funnel supplying this post's denominator.
- Context Engineering, Post 05: token cost, the input/output asymmetry and prompt caching at the single-call level.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 24 — Build #1: a minimal agent harness](../24-build-minimal-harness/index.md)**: loop, tools and ceilings assembled into a runnable harness whose cost you can now meter.
- **[Post 26 — Capstone](../26-capstone-coding-agent/index.md)**: the cost meter of §10 wired into a real driver as a stop condition.
- **[Post 22 — Evaluating harnesses](../22-evaluating-harnesses/index.md)**: where the success rate in §7's denominator comes from, and how to measure it without fooling yourself.
- **[Post 09 — Context management inside the loop](../09-context-management-loop/index.md)**: the four rungs of §6, with the cache arithmetic for compaction worked in full.
