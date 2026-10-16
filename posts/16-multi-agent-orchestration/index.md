# 16 - Multi-agent orchestration: topologies, and when not to

> **TL;DR.** Orchestration coordinates *agents as units*, one level above the harness that drives a single agent, and it comes in four shapes: single agent, orchestrator-worker, pipeline and swarm. It is powerful and over-used, because splitting a task whose pieces need each other's context trades one coherent agent for several that make incompatible decisions. Fanning out reads is cheap and fanning out writes is not, and every fan-out pays a coordination tax in repeated prefixes, a wall-clock set by the slowest worker, and a policy for the worker that fails. Add orchestration only when the work is genuinely parallel, the pieces are independent, and the gain covers that tax.
>
> **Prerequisites:** [post 08](../08-state-filesystem-git/index.md), state on disk and the filesystem as the bus between steps.
> **Safe to skip?** Skip it if the reader can already say who writes the control flow in each multi-agent topology, price a fan-out against one agent in tokens and seconds, and choose what a lead does with a failed worker before dispatching any.
>
> **After reading, you will be able to:**
>
> - Separate a harness from an orchestrator, and name the four topologies and who writes the control flow in each.
> - Steelman the single-agent default, and tell a cheap read fan-out from a write fan-out whose agents must agree.
> - Price the coordination tax of a fan-out in tokens, cached and uncached, and in wall-clock set by the slowest worker.
> - Coordinate agents through shared files, and choose a partial-failure policy before the fan-out rather than after a failure.
> - Apply the decision framework: default to one agent, justify every extra one, and treat isolation as the exception.

![Four panels, each naming who writes the control flow: a single agent running its own sub-tasks, the model; a lead dispatching four workers and merging, the engineer and the lead; a pipeline of draft, edit and fact-check, the engineer; four peers around a shared repository, nobody centrally.](diagrams/01-topologies-gallery.svg)

*Same model, four shapes. The right default is the first one.*

---

## 1. Harness versus orchestrator

When does coordinating agents as units pay for its coordination tax, and when should one agent with sub-tasks stay single? [Post 01](../01-from-context-to-harness/index.md) drew the boundary this part crosses. A **harness** drives *one* model through its loop: tools, state, verification, guardrails. An **orchestrator** coordinates *many* agents as units, one level up: component 09, orchestration, of [post 02](../02-anatomy-of-a-harness/index.md).

Everything in Parts I to III was harness engineering within **one task owned by one loop**, even where that loop makes a second model call for an independent opinion. [Post 12](../12-planner-generator-evaluator/index.md) looks like an exception and is not: its evaluator is a separate agent with its own context, but planner, generator and evaluator all serve one owning loop and one definition of done. Extra model calls in service of one task are still a harness; agents that own their own tasks are orchestration.

The distinction says where a problem lives. "The agent does not verify its work" is a harness problem, fixed inside one agent ([post 11](../11-verification-loops/index.md)). "Three agents overwrite each other's edits" is an orchestration problem, fixed in how the agents are coordinated ([post 17](../17-parallel-agents-shared-repo/index.md)). Confusing the two sends a team tuning prompts when it needed a task queue, or building a swarm when one agent was underfed.

The sibling series reached this territory from the token side: `ctx-013` treats sub-agents as an *isolation* strategy, a child with its own clean window that returns only a structured result, and delegates only under a contract test (the input fully specified, the output structured and finite, the work self-contained). This post is the runtime companion: the unit is an agent, not a window.

---

## 2. Four topologies, and who writes the control flow

This series groups multi-agent designs into four shapes, the four panels of the figure at the top in order:

- **Single agent.** One harness that decomposes a task into sub-tasks it runs itself. This is not orchestration, and it is the default. Sub-agents spawned *within* one harness are still this shape as long as one loop owns the task.
- **Orchestrator-worker.** A lead agent decomposes the task, dispatches independent pieces to workers, then synthesises their results. Good when a task fans out into parallel, self-contained pieces.
- **Pipeline.** Agents in sequence, each transforming the work and passing it on (draft, then edit, then fact-check). Good when the stages are distinct and ordered.
- **Swarm.** Many peer agents on a shared substrate, coordinating through files with no central lead. This is how a codebase gets worked in parallel ([post 17](../17-parallel-agents-shared-repo/index.md)), and it is the contested shape: Walden Yan of Cognition, which now deploys multi-agent systems, calls "the unstructured-swarm approach, arbitrary networks of agents negotiating with each other" "mostly a distraction" (Yan, "Multi-Agents: What's Actually Working", Cognition, 22 April 2026). The gallery shows shapes that exist, not shapes equally endorsed.

The axis that decides the design is **who writes the control flow**. Erik Schluntz and Barry Zhang draw the line between a *workflow* and an *agent*, where an LLM is a large language model: workflows are "systems where LLMs and tools are orchestrated through predefined code paths", while agents are "systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks" (Anthropic, "Building effective agents", 19 December 2024). A model inside a fixed code path is cheap to bound, trace and reproduce; one that chooses its own next step buys flexibility with unpredictability.

On that axis, with orchestrator-worker split by who plans, the shapes show their consequences; the third column is the article's name for the nearest pattern, in its spelling.

| Shape | Who writes the control flow | Anthropic's name for it | What it costs to debug |
|---|---|---|---|
| Single agent | The model, inside one owning loop | Agent | One trace, one context: the easiest case in the table. |
| Pipeline | The engineer, fixed at design time | Prompt chaining | One trace per stage; a bad output localises to a stage. |
| Orchestrator-worker, fixed split | The engineer (a known split) | Parallelization (sectioning) | N worker traces plus a merge, where their disagreements surface. |
| Orchestrator-worker, lead splits | The engineer writes dispatch and merge; the lead model chooses the split | Orchestrator-workers | The split changes between runs, so runs do not reproduce. |
| Swarm | Nobody centrally; the repository | (no counterpart) | Per-agent traces, interleaved, with no global ordering. |

The row that matters is the fourth. The article still files orchestrator-workers among its workflows, because the code that dispatches and merges is fixed; the difference from parallelization is that "subtasks aren't pre-defined, but determined by the orchestrator based on the specific input". That alone costs reproducibility: two runs of one task can split it differently. A lead that also decides, round after round, whether to re-plan and dispatch again has taken over the control flow itself, which is the article's definition of an agent, and that crossing, rather than the agent count, is where a run stops being repeatable. `ctx-013` reaches three overlapping shapes from the context side (sequential, fan-out and fan-in, supervisor) and draws the same line: only the supervisor hands the next step to the model.

The topologies are tools, not a ladder: the question in each case is who needs to choose the next step at run time.

---

## 3. The steelman for staying single

Yan's 2025 essay for Cognition, "Don't Build Multi-Agents" (12 June 2025), argued that most people should not try to build multi-agent systems, so the honest default is to argue *against* them. A single agent has real advantages that fragmentation throws away:

- **Coherent context.** One agent holds the whole task in one window. Split into agents, each worker sees only its slice, spread across handoffs that lose information.
- **Simpler failure.** One loop has one place to look when it breaks; a swarm adds stale views, lost messages, merge conflicts and a synthesis that trusted a bad result.
- **No coordination tax.** Every agent boundary is a place to serialise, hand off and reconcile, pure cost unless parallelism buys it back.

The steelman is simple: *a single agent with sub-tasks keeps the context whole and the system legible, and most tasks fit.* Reaching past it needs a named thing that multi-agent buys.

### Why fragmentation breaks things, precisely

The essay's worked example names the mechanism. A task, "build a Flappy Bird clone", is split into "build a moving game background with green pipes and hit boxes" and "build a bird that you can move up and down". The first subagent misreads its subtask and builds a background that looks like Super Mario Bros.; the second builds a bird that "doesn't look like a game asset and it moves nothing like the one in Flappy Bird", and the final agent is left "with the undesirable task of combining these two miscommunications" (Yan, 2025). Giving each subagent the original task fixes the misreading but not the deeper problem: the two can still return a bird and a background "with completely different visual styles", because neither could see what the other was doing.

Every action carries **implicit decisions** that were never written down: an art style, a naming convention, a unit. So the failure looks like poor quality rather than an error: two agents made reasonable, incompatible choices, and the incompatibility surfaced only when the pieces met. The essay states the principle flatly: "Actions carry implicit decisions, and conflicting decisions carry bad results."

The mitigation is to make the implicit decisions explicit *before* the fan-out (the shared spec of [post 18](../18-long-horizon-ralph/index.md), the memory file of [post 10](../10-continual-learning-ratchet/index.md)), which works exactly to the degree that somebody anticipated what needed deciding. That limit is why the single agent stays the default: one agent holding the whole task never has to anticipate, because it decides once and remembers.

### What the steelman looks like ten months on

Yan revisited the argument in April 2026, ten months later and after Cognition had shipped multi-agent systems, and narrowed it rather than retracting it. The revised position is that "multi-agent systems work best today when writes stay single-threaded and the additional agents contribute intelligence rather than actions": "A clean-context reviewer catches bugs the coder can't see", a stronger model consulted as a "smart friend" catches what a weaker primary misses, and a manager coordinates scope across child agents. The shape that ships, in his phrase, is "map-reduce-and-manage: a manager splits work, children execute, the manager synthesizes and reports back" (Yan, 2026).

The revised default is not "one agent always" but **one writer always**, which permits the orchestrator-worker topology while still refusing the swarm, and it lands on the line the next section draws from the other direction.

---

## 4. Read fan-out is cheap; write fan-out is not

There is a sharp asymmetry hiding inside "are the subtasks independent?".

**Agents that only read are nearly free to parallelise.** Fifty agents summarising fifty documents make no decisions that have to agree; the worst case is a bad summary, and there is nothing to reconcile.

**Agents that write have to agree.** Every write to a shared codebase is a decision the others may contradict, and the coordination machinery (task claiming, worktrees, merges) exists to manage that ([post 17](../17-parallel-agents-shared-repo/index.md)).

`snippets/fan_out.py` runs both kinds with a lead and four scripted workers. In the read task each worker counts the error codes in one of four service logs, and the lead's merge equals the single agent's answer with nothing to reconcile. In the write task each worker adds one feature's settings to one shared settings file, and each makes the implicit decisions its feature needs without seeing the others: two shared keys come back written twice with different values (a timeout of `"30s"` against `10`, two date formats), and the session lifetime comes back as two different keys, `http.session_ttl_s = 3600` and `cache.session_minutes = 30`, which a key-level merge accepts without complaint. The figure below draws the two runs.

![Computed from the snippet. Left, four read workers whose merge equals the single agent's answer, 0 conflicts. Right, four write workers on one settings file: two keys written twice with different values, and a session lifetime of 3,600 seconds against 30 minutes under different keys, which merges cleanly.](diagrams/02-read-vs-write-fan-out.svg)

*Reads never have to agree; writes do, and the costly disagreement is the one that merges cleanly.*

So the practical rule is: fan out on reads freely, and treat every write fan-out as a design problem that needs an answer for how conflicts are *prevented* rather than detected. A merge conflict is the cheap case, because a tool raises it and a human sees it. The expensive case is two writes that merge cleanly and disagree in meaning: an hour against half an hour for one session, both green, neither flagged.

The asymmetry also explains why the same question gets opposite answers in research and in coding. Research is read-heavy, so it fans out well; coding is write-heavy, and Anthropic's assessment of its own research system is that "most coding tasks involve fewer truly parallelizable tasks than research" (Hadfield et al., "How we built our multi-agent research system", Anthropic, 13 June 2025). Yan's single-threaded writes are the same boundary, named from the other side.

---

## 5. When multi-agent genuinely pays

Real cases share a signature: **independent parallel work whose gains exceed the fragmentation cost.**

The best-known published evidence on that side of the argument is Anthropic's research system: "a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval" (Hadfield et al., 2025). It is graded reported here, because the eval is internal, and it comes with the article's own caveats. On the BrowseComp evaluation, "token usage by itself explains 80% of the variance", so a substantial part of what fan-out buys is spending more, and the stated boundary condition is that "multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance". Breadth-first research is such a task; most work is not, so the result is an existence proof, not a default.

Four cases clear the bar:

- **Fan-out over independent items.** Reviewing fifty files, summarising a hundred documents: the pieces do not need each other's context, so fragmentation costs little.
- **Genuinely separate expertise or context.** A task that splits cleanly into sub-problems with little shared state: research one topic per agent, then combine.
- **Throughput at scale.** Many changes to one codebase in parallel, where a swarm on a shared repository is argued to move more work per hour than one agent could. This is the hardest of the four and the most disputed: it is a write fan-out, so it works only with the coordination machinery of [post 17](../17-parallel-agents-shared-repo/index.md), which also examines the largest published run, and Yan calls unstructured swarms "mostly a distraction".
- **Isolation.** Not a throughput argument at all. A second agent is sometimes bought for its *boundary*: untrusted input or a destructive tool runs inside a sandbox and a permission set of its own, so a bad outcome is contained ([post 14](../14-permissions-sandboxes/index.md)), often behind a deterministic gate that decides what reaches it at all ([post 13](../13-hooks-enforcement/index.md)). Containment is the whole purchase, so the tax is worth paying at zero throughput gain, and this case skips the gates of the decision framework below. The boundary is real only if it is handed down: an approval gate is an argument to one run, so a spawned agent has one only if its parent passes it, while shipped systems can also let a permissive parent's mode be inherited ([post 15](../15-human-in-the-loop/index.md)).

The criteria, calibrated against recognisable work:

| Task | Shape | Why |
|---|---|---|
| Summarise 100 documents | Fan-out over items | Read-only; the summaries never have to agree with each other. |
| Draft, edit and fact-check one report | Pipeline | Stages are ordered and distinct, and one artefact runs through all of them. |
| Refactor one module | Single agent | The decisions are interdependent; splitting them is the Flappy Bird failure. |
| Fix 50 unrelated bugs in one repository | Swarm with worktrees | A write fan-out that pays only with real claiming and isolation machinery (post 17). |
| Design a feature with a user | Single agent | The value is the evolving reasoning; there is no finite output contract. |
| Run untrusted code | Isolation | A boundary rather than a topology, bought for blast radius (post 14). |
| Review one pull request for security, performance and style | **Borderline** | Three read-only passes, each with a clean contract, so it fans out cheaply. But one reviewer holding all three lenses catches interactions that three specialists each miss. Fan out when the passes are long, stay single when they are short. |

---

## 6. What the coordination tax actually costs

Three costs decide whether a topology pays, and `snippets/fan_out.py` puts numbers on the first two for both tasks above.

**Tokens multiply with agents as well as with work.** An orchestrator with four workers makes six calls (a plan, four workers, a merge), and each carries the shared prefix of system prompt and tool schemas before it does anything useful. Anthropic's averages point the same way: "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats" (Hadfield et al., 2025). Those are averages over different workloads, not a controlled comparison: an order of magnitude, not a coefficient.

The snippet counts every prompt each role sees with `tiktoken`'s o200k_base, a stand-in for Claude's tokenizer, and prices it at the Claude Sonnet 4.6 rates of 3 and 15 dollars per million input and output tokens (Anthropic, "Pricing", consulted October 2026). Its stand-in prompts are small and its latencies are chosen, so every number below is illustrative; "billed as" is the input in input-rate tokens once caching is counted:

```text
shared prefix (system prompt and 8 tool schemas): 1,198 tokens
log slices: api 1,492, auth 1,490, billing 1,493, search 5,965 tokens
conventions document: 1,541 tokens

read fan-out: count the error codes in four service logs
design                       calls   input  billed as  output   dollars  seconds
single agent                     1  11,659     11,659      60    0.0359      120
lead + 4 workers, uncached       6  18,065     18,065     351    0.0595      100
lead + 4 workers, cached         6  18,065     12,974     351    0.0442      100
merged result equals the single agent's: True; conflicts to reconcile: 0

write fan-out: four features added to one settings file
design                       calls   input  billed as  output   dollars  seconds
single agent                     1   2,760      2,760      61    0.0092      120
lead + 4 workers, uncached       7  17,045     17,045     561    0.0595      115
lead + 4 workers, cached         7  17,045     10,875     561    0.0410      115
keys written twice with different values: 2 (shared.timeout, shared.date_format)
concepts encoded twice with different meanings, merged cleanly: 1 (session-lifetime)
```

![Computed and illustrative, for the read fan-out. Left, input billed as input-rate tokens: single agent 11,659; lead and four workers 18,065 uncached, 7,188 of it the prefix six times, and 12,974 cached. Right, seconds: 120 for one agent doing 10, 10, 10 and 90 in turn; 100 for 5 of planning, the 90-second worker and 5 of merging.](diagrams/03-the-coordination-tax.svg)

*The bill, itemised: the prefix is paid per call, and the wall-clock is the slowest worker plus the lead's own calls.*

Uncached, the read fan-out costs 1.7 times the single agent in dollars, because the prefix is paid six times instead of once, as the figure above itemises. **Caching changes that picture without removing the tax.** Where every role starts with byte-identical system prompt and tool schemas, that prefix is cacheable: the lead's first call writes it at 1.25 times the input rate and each later call reads it at 0.1 times (`ctx-005` works the same mechanism for one agent; Anthropic, "Prompt caching", consulted October 2026). Two conditions there decide whether the discount exists at all. The prefix must reach the model's minimum cacheable length, 1,024 tokens for Sonnet 4.6, which the snippet asserts; and "a cache entry only becomes available after the first response begins", so workers dispatched at the same instant as the call that writes the prefix all miss. The snippet's workers start after the lead's plan returns, and the read fan-out drops to 1.2 times. [Post 23](../23-economics-haas/index.md) applies the same mechanism to the iterations of a single run.

The write fan-out shows the arithmetic lost before it starts. Each writer must read the 1,541-token conventions document to stay consistent, and the lead reads it again to reconcile the two conflicts, so the fan-out costs 6.5 times the single agent uncached and 4.5 times cached. Fan-out saves only when the workers' material together is meaningfully smaller than what one agent would have read, which happens when each worker genuinely needed less than the whole. Both tasks here are one-shot: each piece of material is read once. `ctx-013` works the other case, where each piece is a loop of tool calls: one agent then re-reads every earlier tool result on every later call, and fan-out can cost less than staying single, because a worker re-reads only its own.

**Latency is the slowest worker, plus the lead's own calls.** Parallelism gives the maximum, not the average. The snippet sleeps a chosen latency per call and measures the run with `time.perf_counter`: four pieces of 10, 10, 10 and 90 seconds take a single agent 120 seconds in sequence, and take the fan-out 5 seconds of planning, 90 seconds waiting for the slow log, and 5 seconds of merging, 100 seconds. Four workers bought a 1.2 times speed-up, not 4 times, and the write fan-out's 15-second reconciliation call leaves it at 115.

**Partial failure needs a policy.** When one worker fails, the lead has the other results and a hole, a question a single agent never faces; a system that never decided it answers "synthesise anyway" by default, and the section on the partial-failure policy below gives three better answers.

None of these makes orchestration wrong; they are the bill the throughput has to cover.

---

## 7. Shared files as the inter-agent bus

When agents do need to coordinate, the mechanism is rarely a message broker. It is the **filesystem** ([post 08](../08-state-filesystem-git/index.md)). A task queue is a directory of task files; a result is a file a worker writes; the shared spec is a file everyone reads. The repository is the bus.

So the state primitives of Part II carry straight into orchestration, and no central server is required, which is what makes a leaderless swarm possible ([post 17](../17-parallel-agents-shared-repo/index.md)). The claiming half ships with this series at [`code/17-parallel-agents/`](../../code/17-parallel-agents/): `TaskBoard.claim()` takes a task by creating a claim token with `os.open(token, O_CREAT | O_EXCL | O_WRONLY)`, which only one caller can do, and only then renames `open/<task>` to `claimed/<task>.<agent>`; the loser of a race moves on to the next task. Its nine tests run offline from inside that directory with `uv run --extra dev pytest -q`.

The orchestrator-worker half is a few lines with no framework, and the two things worth encoding in it are two of the costs above. `snippets/partial_failure.py` carries it:

```python
def orchestrate(lead, worker, task, max_workers=4):
    """Fan out independent subtasks, keep the failures visible, then synthesise."""
    subtasks = lead.plan(task)                       # decompose into independent pieces
    results, failures = [], []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        pending = {pool.submit(worker.run, st): st for st in subtasks}
        for future in as_completed(pending):         # the block ends when the slowest one does
            subtask = pending[future]
            try:
                results.append({"subtask": subtask, "result": future.result()})
            except Exception as exc:                 # a failed worker is data, not a crash
                failures.append({"subtask": subtask, "error": repr(exc)})
    return lead.synthesise(task, results, failures)  # the hole is an argument, not a silence
```

The loop over `as_completed` does not finish until the slowest future does, so the run costs the maximum and not the mean. A per-worker timeout belongs inside `worker.run`, where it raises like any other failure. The `failures` list is the partial-failure policy made syntactic: a `synthesise(task, results)` signature lets a lead average over a hole without noticing; `synthesise(task, results, failures)` forces it to have an opinion.

In production each worker writes its result to a file and the lead reads the directory, so the run survives a crash ([post 08](../08-state-filesystem-git/index.md)). The design then sits in what `plan` splits and what `synthesise` trusts: pieces that are not independent produce workers that need context they lack, and a wrong result quietly poisons the combined answer unless `synthesise` catches it.

The lead sees *summaries*, not the work, the position in which a confident wrong answer is indistinguishable from a correct one. Two things help. Workers return **what they checked**, not only what they concluded (the `checked` field of every result in `fan_out.py`), so the lead has something to weigh. And the lead gets a verification step of its own ([post 11](../11-verification-loops/index.md)) rather than treating combination as formatting; an orchestrator that only concatenates is a single point of unverified trust on top of every worker.

---

## 8. Choose the partial-failure policy before the fan-out

When a worker fails, three answers are worth having, and which fits is a property of the work, not of the failure.

- **Fail the run.** The subtasks are jointly necessary, so a missing slice makes the answer wrong rather than thinner: a migration applied to nine of ten shards is broken, not ninety per cent done.
- **Retry, then degrade with a marker.** The work is a read fan-out, where a missing piece narrows the answer without falsifying it. Retry once, since many worker failures are transient (a timeout, a rate limit), then synthesise with an explicit gap naming what is missing, and have the lead's own verification check that the gap survived into the final text ([post 11](../11-verification-loops/index.md)). A degraded answer that says what it is missing is useful; one that does not is a confident lie.
- **Escalate.** The failed slice is irreversible or high-value, so the decision belongs to a human rather than to a default. This is an escalation trigger in the sense of [post 15](../15-human-in-the-loop/index.md): the run pauses, the hole is described, and someone chooses.

Made explicit, the policy is a parameter of the fan-out rather than an accident of whichever code path happened to exist. In `partial_failure.py` the lead's `synthesise` calls it:

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

The snippet runs one fan-out of four documents once per policy, with the worker on doc-2 rate-limited on its first attempt and the one on doc-4 failing every time, and once with no policy at all:

```text
4 subtasks; doc-2 fails once (rate limit), doc-4 fails every time (unreadable)
no policy           2 of 4 kept; note: None
                    answer: doc-1: uptime 99.95%; doc-3: no incidents
                    nothing in the answer says that 2 of the 4 documents are missing
fail                raised RuntimeError: 2 of 4 subtasks failed
retry_then_degrade  3 of 4 kept; note: MISSING: doc-4
                    answer: doc-1: uptime 99.95%; doc-2: two incidents; doc-3: no incidents
                    worker attempts: doc-1 1, doc-2 2, doc-3 1, doc-4 2
escalate            2 of 4 kept; note: ESCALATED: doc-2, doc-4 failed; paused for a human
                    answer: doc-1: uptime 99.95%; doc-3: no incidents
                    worker attempts: doc-1 1, doc-2 1, doc-3 1, doc-4 1
```

In the run with no policy half the evidence is gone and the answer reads exactly like a complete one; the retry recovers the transient failure and marks the permanent one. The rule that ties the three together is procedural: **the policy is chosen before the fan-out, not after the failure.** A system that decides at failure time will decide "synthesise anyway", because that is the branch the code already has.

---

## 9. A decision framework

The steelman and the exceptions go into an order, which the figure below draws.

![Three gates in order: independent and parallel subtasks, acceptable fragmentation, a gain that covers the tax. A no at any gate falls through to one agent; yes at all three leads to orchestration with two conditions, one writer and a failure policy chosen first. Isolation enters from above, past the gates.](diagrams/04-orchestration-decision.svg)

*Default to a single agent; each gate must say yes before a second agent earns its cost.*

Start with a single agent. Add orchestration only when three things are all true: the subtasks are genuinely independent, the context fragmentation is acceptable, and the gain covers the coordination cost. A "no" to any one of them sends the design back to one agent with sub-tasks.

The bar is high because the tax is paid on every run and the benefit only on the runs whose work turned out to be parallel. Two follow-on rules make the framework harder to fool. Keep writes single-threaded unless the machinery of [post 17](../17-parallel-agents-shared-repo/index.md) is in place (Yan, 2026), and settle the partial-failure policy in the same design session that chooses the topology. Isolation is the one exception that skips the gates entirely, because what it buys is containment rather than throughput.

---

## 10. Make it run

The exercise is to run an orchestrator-worker example on a read and a write fan-out and record tokens and wall-clock against one agent. Both snippets run offline from the series root; `fan_out.py` needs `tiktoken`, which the series environment provides, and `partial_failure.py` needs only the standard library:

```bash
uv run python posts/16-multi-agent-orchestration/snippets/fan_out.py
uv run python posts/16-multi-agent-orchestration/snippets/partial_failure.py
```

They print the outputs quoted above; `fan_out.py` takes about five seconds, because it sleeps each simulated latency at 1/100 scale and asserts that the measured wall-clock agrees with the model within 15 per cent. Two variations are worth running. Set the four entries of `WORKER_S` equal and watch the speed-up rise, still short of four because of the lead's own calls; then drop `CONVENTIONS` from the write workers' prompts and watch the write fan-out's cost fall while its conflicts stay exactly where they were.

---

## 11. What can go wrong?

- **Dispatching every worker at once and counting on the cache.** The lead's first call and the workers start in the same instant; each misses and pays a fresh cache write, so the prefix costs more than with no caching at all.
- **A write fan-out with a key-level merge as its only check.** The merge reports no conflicts, and in production one service expires sessions after an hour while another expires them after thirty minutes.
- **Splitting by agent count rather than by work.** Four workers are given one long slice and three short ones; the run takes as long as the long slice, and the speed-up is a fraction of the one the design promised.
- **A lead that drops the failures argument.** `synthesise(task, results)` ignores the hole; the report summarises two of four documents and nobody reading it can tell.

---

## Common pitfalls

1. **Reaching for multi-agent by default.** Splitting a task whose pieces needed each other's context trades one coherent agent for several that make incompatible decisions.
2. **Confusing sub-agents with orchestration.** One harness spawning helpers, or calling a second model as an independent grader, is still a single agent; orchestration coordinates agents that own their own tasks.
3. **Fanning out writes without a conflict story.** Parallel readers are nearly free; parallel writers must agree on conventions and files, and agents that cannot see each other's work cannot agree on anything.
4. **Pricing fan-out by agent count.** Latency is the slowest worker plus the lead's calls, and the prefix is paid once per call unless caching is ordered to save it.
5. **No policy for a failed worker.** Deciding at failure time means deciding "synthesise anyway", which ships an answer built on partial evidence with nothing marking what is missing.
6. **Debugging a swarm without traces.** Many agents multiply the failure surface, and a lead that chooses the split does not reproduce between runs, so per-agent traces are not optional ([post 21](../21-observability-traces/index.md)).

---

## Further reading

- Erik Schluntz and Barry Zhang, "Building effective agents" (Anthropic, 19 December 2024): the workflow-against-agent distinction and the composition patterns the topology table maps the four shapes onto.
- Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox and Daniel Ford, "How we built our multi-agent research system" (Anthropic, 13 June 2025): the 90.2% internal research-eval result, the 4× and 15× token averages, and the article's own caveats on both.
- Walden Yan, "Don't Build Multi-Agents" (Cognition, 12 June 2025): the steelman for staying single-agent, and the Flappy Bird walkthrough.
- Walden Yan, "Multi-Agents: What's Actually Working" (Cognition, 22 April 2026): the revision ten months on, single-threaded writes, and map-reduce-and-manage.
- Anthropic, "Prompt caching" and "Pricing" (Claude documentation, consulted October 2026): the cache write and read multipliers, the minimum cacheable length, and the rule for concurrent requests.
- ai-boost, awesome-harness-engineering (GitHub, consulted October 2026): the Task Runners & Orchestration reading list.
- `ctx-013`, "Isolate strategies": sub-agents as a context-isolation strategy, the clean-contract test, and the loop case where fan-out costs less than one agent.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 17 - Parallel agents on a shared repo: worktrees and task-claiming](../17-parallel-agents-shared-repo/index.md):** the swarm topology in depth, with worktrees and file-based task claiming that makes write fan-out safe.
- **[Post 20 - The SDK and framework landscape: Agent SDK, LangGraph, and peers](../20-sdk-landscape/index.md):** how the shipped SDKs and frameworks package sub-agents, handoffs and graphs, and which topology each makes easy.
