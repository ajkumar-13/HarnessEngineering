# 16 · Multi-agent orchestration — topologies, and when not to

> **TL;DR.** Orchestration coordinates *agents as units*, one level above the harness that drives a single agent. It comes in a few shapes (single, orchestrator-worker, pipeline, swarm), and it is powerful and badly over-used. The failure mode is reaching for many agents when one agent with sub-tasks would keep the context coherent and the system debuggable. Add orchestration only when the work is genuinely parallel, the subtasks are independent, and the throughput is worth the coordination cost.
>
> **After reading this you will be able to:**
> - Distinguish a harness (drives one agent) from an orchestrator (coordinates many).
> - Name the four common topologies, and say who writes the control flow in each.
> - Apply a decision framework that defaults to a single agent and justifies every extra one.
> - Price the coordination tax before paying it: per-agent tokens, slowest-worker latency, partial failure.

![Four topology panels: a single agent fanning out to sub-tasks, an orchestrator-worker with a lead and four workers, a pipeline of draft, edit and fact-check in sequence, and a swarm of peers around a shared repo. Each panel carries Anthropic's own name for the shape, what it costs to debug, and a task that actually fits it. Beneath them, the axis the design turns on: workflow, where predefined code paths keep the run cheap to bound and reproduce, against agent, where the model directs its own process and the run stops reproducing. A strip orders the five shapes along that axis, and a closing line records that Cognition calls the unstructured swarm mostly a distraction.](diagrams/01-topologies-gallery.svg)
*Same model, four shapes. The right default is the top-left one.*

---

## 1. Harness versus orchestrator

[Post 01](../01-from-context-to-harness/index.md) drew the boundary, and it is worth restating precisely as this part crosses it. A **harness** drives *one* model through its loop: tools, state, verification, guardrails. An **orchestrator** coordinates *many* agents as units, one level up.

Everything in Parts I to III was harness engineering within **one task owned by one loop**, even where that loop makes a second model call to get an independent opinion. [Post 12](../12-planner-generator-evaluator/index.md) is the case that looks like an exception and is not. Its evaluator really is a separate agent with its own context, bought precisely so the grade does not come from the maker, but planner, generator and evaluator all serve one owning loop and one definition of done. Extra model calls in service of one task are still a harness. Agents that own their own tasks are orchestration.

The distinction is not pedantry, because it tells you where a problem lives. "My agent does not verify its work" is a harness problem, fixed inside one agent ([Post 11](../11-verification-loops/index.md)). "My three agents overwrite each other's edits" is an orchestration problem, fixed in how the agents are coordinated ([Post 17](../17-parallel-agents-shared-repo/index.md)). Confusing the two sends you tuning prompts when you needed a task queue, or building a swarm when one agent was underfed.

The sibling series reached this territory from the token side. Context Engineering treats sub-agents as an *isolation* strategy: a child runs in its own clean window, its noisy intermediate work never enters the parent's context, and only a structured result comes back (Context Engineering, Post 13). The test it applies before delegating anything is a contract test: the input must be fully specified, the output structured and finite, the work genuinely self-contained. This post is the runtime companion. The unit here is not a window but an agent, and the questions are how many agents there are, who decides the split, what the coordination costs, and what happens when one of them fails.

---

## 2. Four topologies, and who writes the control flow

Almost every multi-agent design is one of four shapes, which are the four panels of the hero figure in order (Anthropic, 2024; awesome-harness-engineering, 2026):

- **Single agent.** One harness that decomposes a task into sub-tasks it runs itself. This is not orchestration, and it is the default. Sub-agents spawned *within* one harness (a research helper, a reviewer) are still this shape as long as one loop owns the task.
- **Orchestrator-worker.** A lead agent decomposes the task and dispatches independent pieces to workers, then synthesises their results. Good when a task fans out into parallel, self-contained pieces.
- **Pipeline.** Agents in sequence, each transforming the work and passing it on (draft, then edit, then fact-check). Good when the stages are distinct and ordered.
- **Swarm.** Many peer agents on a shared substrate, coordinating through files with no central lead. This is how a codebase gets worked in parallel ([Post 17](../17-parallel-agents-shared-repo/index.md)), and it is the contested shape: Cognition, having since deployed multi-agent systems in production, calls the unstructured-swarm approach "mostly a distraction" (Cognition, 2026). Read the gallery as four shapes that exist, not four shapes equally endorsed.

Naming the shapes is only half the work. The axis that actually decides the design is **who writes the control flow**. Anthropic draws the line between a *workflow* and an *agent*: in a workflow, large language model (LLM) calls and tools are "orchestrated through predefined code paths"; in an agent, "LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks" (Anthropic, 2024). A model inside a fixed code path is cheap to bound, trace and reproduce; one that chooses its own next step buys flexibility and pays for it in unpredictability.

Map the four shapes onto that axis, splitting orchestrator-worker by who does the planning, and the operational consequences fall out.

| Shape | Who writes the control flow | Anthropic's name for it | What it costs to debug |
|---|---|---|---|
| Single agent | The model, inside one owning loop | Agent | One trace, one context: the easiest case in the table. |
| Pipeline | The engineer, fixed at design time | Prompt chaining | One trace per stage; a bad output localises to a stage. |
| Orchestrator-worker, fixed plan | The engineer (a known split) | Parallelisation (sectioning) | N worker traces plus a merge; most bugs live in the merge. |
| Orchestrator-worker, re-planning lead | The lead model, at run time | Orchestrator-workers | The plan changes between rounds, so runs do not reproduce. |
| Swarm | Nobody centrally; the repository | (no counterpart) | Per-agent traces, interleaved, with no global ordering. |

The row that matters is the fourth. A lead that re-plans between rounds has crossed from workflow to agent, and that crossing, rather than the agent count, is where reproducibility is lost. Context Engineering reaches three overlapping shapes from the context side (sequential, fan-out and fan-in, supervisor), which is a useful cross-check rather than a contradiction (Context Engineering, Post 13).

The topologies are tools, not a ladder. Most systems that reach for a swarm needed a single agent with a bigger context, and most that build an orchestrator needed a pipeline.

---

## 3. The steelman for staying single

Multi-agent architectures are the most over-applied pattern in the field, so the honest default is to argue *against* them (Cognition, 2025). A single agent has real advantages that fragmentation throws away:

- **Coherent context.** One agent holds the whole task in one window. The moment you split into agents, each worker sees only its slice, and the context that made the task make sense is fragmented across handoffs that lose information.
- **Simpler failure.** One loop has one place to look when it breaks. A swarm multiplies the failure surface: a worker with a stale view, a lost message, a merge conflict, a synthesis that trusted a bad result.
- **No coordination tax.** Every agent boundary is a place to serialise, hand off, and reconcile. That overhead is pure cost unless parallelism buys it back.

The steelman is simple: *a single agent with sub-tasks keeps the context whole and the system legible, and most tasks fit.* Reach past it only when you can name the specific thing multi-agent buys.

### Why fragmentation breaks things, precisely

"Fragmented context" is vague enough to sound survivable, so it is worth naming the mechanism, and the source's own worked example is the one to hold on to. Take "build a Flappy Bird clone" and split it into "build a moving game background with green pipes and hit boxes" and "build a bird that you can move up and down". The first subagent returns a background that looks like Super Mario Bros. The second returns a bird that, in Cognition's words, "doesn't look like a game asset and it moves nothing like the one in Flappy Bird". Neither subagent broke its brief. The final agent is left "with the undesirable task of combining these two miscommunications" (Cognition, 2025).

Every action an agent takes carries **implicit decisions** that were never written down: an art style, a component library, a naming convention, an error-handling style. This is why the failure looks like poor quality rather than an error. Nothing crashed. Two agents made reasonable, incompatible choices, and the incompatibility only surfaced when the pieces met. Cognition's principle states it flatly: "Actions carry implicit decisions, and conflicting decisions carry bad results."

The mitigation is to make the implicit decisions explicit *before* the fan-out (the shared spec of [Post 18](../18-long-horizon-ralph/index.md), the memory file of [Post 10](../10-continual-learning-ratchet/index.md)), which works exactly to the degree that you anticipated what needed deciding. That is a real limit, and it is the honest reason the single agent stays the default: one agent holding the whole task never has to anticipate, because it decides once and remembers.

### What the steelman looks like a year on

Cognition revisited the argument in April 2026, after shipping multi-agent systems of their own, and did not retract it so much as narrow it. Their revised position is that multi-agent systems "work best today when writes stay single-threaded" and when "the additional agents contribute intelligence rather than actions": a reviewer reading with a clean context, a stronger model asked for a second opinion, a researcher fetching what the writer needs. The shape that ships, in their phrase, is "map-reduce-and-manage: a manager splits work, children execute, the manager synthesizes and reports back" (Cognition, 2026).

Two things follow. The revised default is not "one agent always" but **one writer always**, which is a far more usable rule and one that permits the orchestrator-worker topology while still refusing the swarm. And it was reached from production experience rather than first principles, which matters because it lands on the same line the next section draws from the other direction.

---

## 4. Read fan-out is cheap; write fan-out is not

There is a sharp asymmetry hiding inside "are the subtasks independent?", and it is the most useful line to draw before designing anything.

**Agents that only read are nearly free to parallelise.** Fifty agents summarising fifty documents make no decisions that have to agree with each other. Their outputs are independent by construction, the worst case is a bad summary, and there is nothing to reconcile.

**Agents that write have to agree.** Two agents editing one codebase share conventions, interfaces, and file contents. Every write is a decision the others may contradict, and the coordination machinery (task claiming, worktrees, merges) exists entirely to manage that ([Post 17](../17-parallel-agents-shared-repo/index.md)).

So the practical rule is: fan out on reads freely, and treat every write fan-out as a design problem that needs an answer for how conflicts are *prevented* rather than detected. Detection is what a merge conflict is, and a merge conflict is the cheap case, because a tool raises it and a human sees it. The expensive case is two writes that merge cleanly and disagree in meaning: two authentication helpers with different session semantics, both green, both merged, neither flagged.

The asymmetry also explains why the same question gets opposite answers in research and in coding. Research is read-heavy, so it fans out well. Coding is write-heavy, and Anthropic's own assessment of its research system is that "most coding tasks involve fewer truly parallelizable tasks than research" (Anthropic, 2025). Cognition's single-threaded-writes rule (§3) is the same boundary, named from the other side.

---

## 5. When multi-agent genuinely pays

There are real cases, and they share a signature: **independent parallel work whose gains exceed the fragmentation cost.**

The strongest published evidence on the other side of the argument is Anthropic's research system, where a lead running Claude Opus 4 with Claude Sonnet 4 subagents "outperformed single-agent Claude Opus 4 by 90.2%" on their internal research eval (Anthropic, 2025). That is a large margin and it deserves to be taken at face value. It also deserves the same paper's caveats. On the BrowseComp evaluation, "token usage by itself explains 80% of the variance", so a substantial part of what fan-out buys is simply spending more, and the stated boundary condition is that "multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance". Breadth-first research at that price is such a task. Most work is not, which is why the result is an existence proof rather than a default.

Four cases clear the bar:

- **Fan-out over independent items.** Reviewing fifty files, summarising a hundred documents, running the same task across many targets. The pieces do not need each other's context, so fragmentation costs little and parallelism wins.
- **Genuinely separate expertise or context.** A task that splits cleanly into sub-problems with little shared state (research one topic per agent, then combine).
- **Throughput at scale.** Many changes to one codebase in parallel, where a swarm on a shared repository moves more work per hour than one agent could (MindStudio, 2026). This is the hardest of the four and the most disputed: it is a write fan-out, so it works only with the coordination machinery of [Post 17](../17-parallel-agents-shared-repo/index.md), Anthropic judges coding less parallelisable than research (Anthropic, 2025), and Cognition (2026) puts unstructured swarms outside what they would deploy. Treat throughput as the case that has to be earned with machinery rather than assumed from agent count.
- **Isolation.** Not a throughput argument at all. A second agent is sometimes bought for its *boundary*: untrusted input or a destructive tool runs inside a sandbox and a permission set of its own, so a bad outcome is contained ([Post 14](../14-permissions-sandboxes/index.md)), often behind a deterministic gate that decides what reaches it at all ([Post 13](../13-hooks-enforcement/index.md)). This is the one case where the coordination tax of §6 is worth paying at zero throughput gain, because containment is the entire purchase, and it is also the one case that does not go through the gates in §9. The boundary is only real if it is handed down: an approval gate is an argument to one run rather than a property of the system, so a spawned agent has one only if its parent passes it, and shipped systems fail the other way, letting a permissive parent's mode be inherited silently ([Post 15](../15-human-in-the-loop/index.md)).

Criteria this abstract get answered optimistically under pressure, so calibrate them against work you recognise.

| Task | Shape | Why |
|---|---|---|
| Summarise 100 documents | Fan-out over items | Read-only; the summaries never have to agree with each other. |
| Draft, edit and fact-check one report | Pipeline | Stages are ordered and distinct, and one artefact runs through all of them. |
| Refactor one module | Single agent | The decisions are interdependent; splitting them is the Flappy Bird failure. |
| Fix 50 unrelated bugs in one repository | Swarm with worktrees | A write fan-out that pays only with real claiming and isolation machinery (Post 17). |
| Design a feature with a user | Single agent | The value is the evolving reasoning; there is no finite output contract. |
| Run untrusted code | Isolation | A boundary rather than a topology, bought for blast radius (Post 14). |
| Review one pull request for security, performance and style | **Borderline** | Three read-only passes, each with a clean contract, so it fans out cheaply. But one reviewer holding all three lenses catches interactions that three specialists each miss. Fan out when the passes are long, stay single when they are short. |

---

## 6. What the coordination tax actually costs

"Coordination cost" gets asserted a lot and quantified rarely. Three costs are worth being concrete about, because they decide whether a topology pays.

![Three panels: token bars showing one agent against a lead and four workers with five times the fixed overhead and identical work; a latency chart of four ten-second workers, one ninety-second worker, and a synthesis pass; and five worker chips, one failed, feeding a lead holding four results and a hole.](diagrams/03-the-coordination-tax.svg)
*The bill, itemised. Each panel is a cost a single agent never pays.*

**Tokens multiply with agents, not with work.** An orchestrator with four workers is five contexts, each carrying its own system prompt, tool schemas, and task framing before it does anything useful. The fixed overhead per agent is paid whether the worker's slice was large or trivial. The published multipliers are the numbers to hold on to: agents "use about 4x more tokens than chat interactions, and multi-agent systems use about 15x more tokens than chats" (Anthropic, 2025). Dividing one by the other puts a multi-agent run near four times a single agent, though those are averages over different workloads rather than a controlled comparison, so treat it as an order of magnitude and not a coefficient.

Work it through. Suppose the system prompt plus tool schemas comes to 6,000 tokens, each worker's slice of task-specific material is 2,000 tokens, and each worker emits 1,000 tokens. A single agent doing all four slices reads 6,000 + (4 x 2,000) = 14,000 input tokens. An orchestrator with four workers reads five preambles instead of one, plus the same 8,000 tokens of slices, plus a synthesis pass over 4,000 tokens of worker output: 42,000 input tokens for identical work.

Caching changes that picture without removing the tax. Where the workers share a byte-identical system prompt and tool schemas, that prefix is cacheable: the first call pays a write premium of about 1.25 times base input price and every later read costs about a tenth of it (Context Engineering, Post 05). [Post 23](../23-economics-haas/index.md) §4 applies the same mechanism to the iterations of a *single* run; the multi-agent multiplier is what this section adds on top of that, and caching is what partially offsets it.

| Design | Preamble, billed as input-equivalent | Slices | Synthesis | Total |
|---|---|---|---|---|
| Single agent | 6,000 | 8,000 | none | **14,000** |
| Lead + 4 workers, uncached | 5 x 6,000 = 30,000 | 8,000 | 4,000 | **42,000** |
| Lead + 4 workers, shared prefix cached | (6,000 x 1.25) + (4 x 6,000 x 0.1) = 9,900 | 8,000 | 4,000 | **21,900** |

The numbers are illustrative rather than a benchmark; the shape is what transfers. Uncached, the fan-out costs three times the single agent. Cached, it costs about 1.6 times, and what survives the discount is the per-worker task framing plus each worker's own observations. The break-even is the one the sibling series states at the token level (Context Engineering, Post 13), restated here at the agent level:

```
single_cost ~ (preamble + all slices) * in_price
            + (one output) * out_price

multi_cost  ~ (preamble_write + N * preamble_read) * in_price
            + sum(worker slices) * in_price
            + sum(worker outputs) * out_price
            + (synthesis input + synthesis output) * price
```

Fan-out saves only when the sum of the workers' slices is meaningfully smaller than the single combined prompt would have been, which happens when each worker genuinely needed less than the whole. A design where every worker reloads a near-complete view of the world has already lost the arithmetic.

**Latency is the slowest worker, plus synthesis.** Parallelism does not give you the average; it gives you the maximum, and then adds the lead's synthesis pass on top. Four workers at ten seconds and one at ninety run in ninety seconds, plus roughly five seconds of synthesis: ninety-five seconds against the one hundred and thirty a single agent would have spent doing the same five pieces in sequence. Five agents bought a 1.4x speed-up, not a 5x one. Fan-out over uneven work wins far less than the agent count suggests.

**Partial failure needs a policy, and usually does not have one.** When one of five workers fails, the lead has four results and a hole. Does it synthesise anyway, retry the one, or abandon the task? A single agent never faces this question, and multi-agent systems that never decided it tend to answer "synthesise anyway" by default: a confident answer built on four-fifths of the evidence, with nothing in the output marking what is missing. §8 gives that question three answers.

None of these makes orchestration wrong. They are the bill that the throughput has to cover, and the point of naming them is that the bill is usually larger than the design assumed.

---

## 7. Shared files as the inter-agent bus

When agents do need to coordinate, the mechanism is rarely a message broker. It is the **filesystem** ([Post 08](../08-state-filesystem-git/index.md)). A task queue is a directory of task files; a result is a file a worker writes; the shared spec is a file everyone reads. The repository is the bus.

This is why the state primitives of Part II carry straight into orchestration. A worker claims a task by renaming its file, does the work, and writes a result; the lead reads the results and synthesises. No central server is required, which is exactly what makes a leaderless swarm possible ([Post 17](../17-parallel-agents-shared-repo/index.md)). The runnable version of the claiming half ships with this series at [`code/17-parallel-agents/`](../../code/17-parallel-agents/), where `TaskBoard.claim()` is an atomic `os.rename` from `open/` to `claimed/<task>.<agent>` and the loser of a race moves on to the next task; its nine tests run offline with `python -m pytest -q`.

The orchestrator-worker half is a few lines with no framework, and the two things worth encoding in it are the two costs from §6:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def orchestrate(lead, worker, task, max_workers=4, timeout=120):
    """Fan out independent subtasks, keep the failures visible, then synthesise."""
    subtasks = lead.plan(task)                       # decompose into independent pieces
    results, failures = [], []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        pending = {pool.submit(worker.run, st): st for st in subtasks}
        for future in as_completed(pending):         # completes when the slowest one does
            subtask = pending[future]
            try:
                results.append({"subtask": subtask, "result": future.result(timeout)})
            except Exception as exc:                 # a failed worker is data, not a crash
                failures.append({"subtask": subtask, "error": repr(exc)})
    return lead.synthesise(task, results, failures)  # the hole is an argument, not a silence
```

The executor is where the latency claim becomes visible: the `with` block does not exit until the slowest future does, so the run costs the maximum and not the mean. The `failures` list is the partial-failure policy made syntactic. A `synthesise(task, results)` signature lets a lead average over a hole without ever noticing; `synthesise(task, results, failures)` forces it to have an opinion.

In production the results do not stay in memory. Each worker writes its result to a file, the lead reads the directory, and the run survives a crash because the state is on disk rather than in a process ([Post 08](../08-state-filesystem-git/index.md)). The whole design then sits in what `plan` splits and what `synthesise` trusts. If the pieces are not independent, `plan` produces workers that need context they do not have; if a worker returns something wrong, `synthesise` must catch it, because a bad result quietly poisons the combined answer.

Synthesis is the step that gets underestimated. The lead sees *summaries*, not the work: it has each worker's conclusion and none of the evidence that produced it, which is precisely the position in which a confident wrong answer is indistinguishable from a correct one. Two things help. Have workers return **what they checked**, not only what they concluded, so the lead has something to weigh. And give the lead a verification step of its own ([Post 11](../11-verification-loops/index.md)) rather than treating combination as a formatting exercise; an orchestrator that only concatenates is a single point of unverified trust sitting on top of every worker.

---

## 8. Choose the partial-failure policy before the fan-out

§6 asked the question and left it open: when one of five workers fails, does the lead synthesise anyway, retry, or abandon? Three answers are worth having, and which one fits is a property of the work rather than of the failure.

- **Fail the run.** The subtasks are jointly necessary, so a missing slice makes the answer wrong rather than merely thinner. A migration applied to nine of ten shards is not ninety per cent migrated; it is broken. Fail loudly and let the caller decide.
- **Retry, then degrade with a marker.** The work is a read fan-out, where a missing piece narrows the answer without falsifying it. Retry once, since most worker failures are timeouts and rate limits, then synthesise with an explicit gap in the output naming what is missing, and have the lead's own verification check that the gap survived into the final text ([Post 11](../11-verification-loops/index.md)). A degraded answer that says what it is missing is useful. One that does not is a confident lie.
- **Escalate.** The failed slice is irreversible or high-value, so the decision belongs to a human rather than to a default. This is the escalation trigger of [Post 15](../15-human-in-the-loop/index.md): the run pauses, the hole is described, and someone chooses.

Made explicit, the policy is a parameter of the fan-out rather than an accident of the code path that happened to exist:

```python
def apply_policy(policy, results, failures, retry, gap_note, escalate):
    """Decide what the lead does with a partial result set. Chosen at design time."""
    if not failures:
        return results, None
    if policy == "fail":
        raise RuntimeError(f"{len(failures)} of {len(results) + len(failures)} subtasks failed")
    if policy == "retry_then_degrade":
        recovered, still_failed = retry(failures)
        return results + recovered, gap_note(still_failed)
    if policy == "escalate":
        return results, escalate(failures)
    raise ValueError(f"unknown partial-failure policy {policy!r}")
```

The rule that ties the three together is procedural: **the policy is chosen before the fan-out, not after the failure.** A system that decides at failure time will decide "synthesise anyway", because that is the branch the code already has.

---

## 9. A decision framework

Put the steelman and the exceptions into an order you can follow under pressure.

![On the left, three gates from a task to run: are the subtasks independently parallel, is the fragmentation acceptable, and is the throughput worth the tax. A no at any gate keeps the work on a single agent; a yes to all three leads to orchestration. On the right, what that yes costs, priced. A token table shows the same work at 14,000 input tokens for a single agent, 42,000 for a lead and four workers uncached, and 21,900 with a shared prefix cached. A latency chart shows four workers at ten seconds and one at ninety finishing in ninety-five seconds with synthesis, against one hundred and thirty in sequence: a 1.4x speed-up, not 5x. A third panel gives the published evidence both ways.](diagrams/02-orchestration-decision.svg)
*Default to a single agent. Add orchestration only when parallel, independent work outweighs the coordination cost.*

Start with a single agent. Add orchestration only when three things are all true: the subtasks are genuinely independent, the context fragmentation is acceptable, and the throughput justifies the coordination cost. A "no" to any one of them sends you back to one agent with sub-tasks.

The bar is deliberately high because of when the two sides of the ledger are paid. The coordination tax of §6 is paid on every run, whether or not the work turned out to be parallel; the benefit is paid only on the runs where it was. Two follow-on rules make the framework harder to fool. Keep writes single-threaded unless you have the machinery of [Post 17](../17-parallel-agents-shared-repo/index.md) (Cognition, 2026), and settle the partial-failure policy of §8 in the same design session that chooses the topology. Isolation (§5) is the one exception that skips the gates entirely, because what it buys is containment rather than throughput.

---

## Common pitfalls

- **Reaching for multi-agent by default.** The single agent is the default, and splitting a task whose pieces needed each other's context trades one coherent agent for several confused ones (§3).
- **Confusing sub-agents with orchestration.** One harness spawning helpers, or calling a second model as an independent grader, is still a single agent; orchestration is coordinating agents that own their own tasks (§1, §2).
- **Fanning out writes without a conflict story.** Parallel readers are nearly free; parallel writers must agree on conventions and files, and agents that cannot see each other's work through a shared bus cannot agree on anything (§4, §7; Post 17).
- **Trusting a worker's output blindly.** A bad result poisons the synthesis, and the lead sees conclusions rather than evidence. Verify what you combine (§7; Post 11).
- **Pricing fan-out by agent count.** Latency is the slowest worker plus synthesis, and tokens scale with agents rather than with work (§6).
- **No policy for a failed worker.** Deciding at failure time means deciding "synthesise anyway", which ships a confident answer built on partial evidence with nothing marking what is missing (§8).
- **Debugging a swarm without traces.** Many agents multiply the failure surface, and a re-planning lead does not reproduce between runs, so per-agent traces are not optional ([Post 21](../21-observability-traces/index.md)).

---

## Further reading

- Anthropic Engineering, "Building Effective Agents" (December 2024): the workflow-versus-agent distinction and the composition patterns §2 maps the four topologies onto.
- Anthropic Engineering, "How we built our multi-agent research system" (June 2025): the 90.2% research-eval result, the 15x token multiplier, and the author's own caveats on both.
- Cognition, "Don't Build Multi-Agents" (2025): the steelman for staying single-agent, and the Flappy Bird walkthrough §3 uses.
- Yan, W., "Multi-Agents: What's Actually Working" (2026): the April 2026 revision, single-threaded writes, and map-reduce-and-manage.
- awesome-harness-engineering (2026): the Task Runners & Orchestration primitive and its topology taxonomy.
- MindStudio, "What Is Harness Engineering?" (2026): enterprise-scale parallel throughput, and the claim §5 qualifies.
- Context Engineering, Post 13: sub-agents as a context-isolation strategy, with the clean-contract test and the token-level cost arithmetic.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 17 — Parallel agents on a shared repo](../17-parallel-agents-shared-repo/index.md)**: the swarm topology in depth, with worktrees and file-based task claiming.
- **[Post 12 — Planner / generator / evaluator](../12-planner-generator-evaluator/index.md)**: roles within one task, the pattern orchestration is often confused with.
- **[Post 02 — The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: orchestration as the scale tier of the component map.
