# Glossary

Harness-specific terms used across the series, alphabetised, one or two lines each. This glossary **extends** the *Context Engineering* glossary rather than duplicating it — shared terms (attention, chunking, context window, context rot, MCP, prompt caching, RAG, sub-agent) are defined there and only re-scoped here where the harness lens differs.

---

**Agent.** A model plus everything around it that lets it *act*, not just respond — the model, the scaffold, and the harness operating together in a loop. Its founding equation, `Agent = Model + Harness`, is Trivedy's (2026), popularised by Osmani.

**Agent loop.** The core cycle a harness runs: call the model, parse its tool calls, execute them, feed the results back, repeat, until a stop condition fires. Also *control loop*.

**Allow-list.** A sandbox policy that permits only named programs and refuses everything else, the inverse of a deny-list. A deny-list stops the dangers you thought of; an allow-list stops the ones you did not. Allow-listing an interpreter allow-lists everything it can run, so `python` on an allow-list is not a boundary. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Approval gate.** A point in the loop where a call classed as sensitive is routed to a human or a stricter policy for a verdict before it executes. A denied call never runs, and the denial is recorded on the run. See [Post 15](posts/15-human-in-the-loop/index.md).

**Approve and remember.** An approval outcome that returns a persisted rule alongside the verdict, so later calls matching that rule stop asking. What lets an approval queue drain itself rather than needing a policy rewrite. See [Post 15](posts/15-human-in-the-loop/index.md).

**Atomic claim.** A task claimed by an operation that cannot half-succeed, such as a rename from `open/` to `claimed/`. An atomic primitive does not by itself buy an atomic claim: the caller must confirm the effect rather than infer it from the absence of an error. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Autonomy spectrum.** The range of oversight settings between fully manual and fully autonomous, framed by Morris (2026) as humans *outside*, *in*, or *on* the loop. The mistake is picking one setting for a whole agent rather than one per class of action. See [Post 15](posts/15-human-in-the-loop/index.md).

**Backstop exit.** A loop exit that exists only so a loop which never reaches its intended stop still terminates, such as the hard iteration cap. Never run a loop without one. See [Post 03](posts/03-the-agent-loop/index.md).

**Batch turn.** A loop turn that waits for the model's complete response before acting. Simpler than a *streaming turn*, and the right default for building and understanding a loop.

**Binding Constraint Thesis.** Zhang et al.'s (2026) formal statement of "harness beats model": across models of comparable frontier capability on long-horizon tasks, the execution harness is often a stronger determinant of the score than the weights. See [Post 04](posts/04-harness-beats-model/index.md).

**Blast radius.** The scope of damage a single agent action can cause if it goes wrong. Sandboxes and permissions exist to bound it.

**Budget exit.** A stop condition expressed in tokens or wall-clock seconds rather than iterations, because a single turn can be cheap or enormous. Checked after a call it can be crossed by one iteration; reserving before spending avoids that.

**Checkpoint.** A commit taken after a verified step and kept as a point the loop can return to, distinct from a version-control commit meant for human review. What makes a risky but reversible step cheap to take. See [Post 08](posts/08-state-filesystem-git/index.md).

**Compaction.** Replacing a span of conversation history with a shorter summary of it, in place, to reclaim window space. Lossy by construction, and it invalidates every prompt-cache breakpoint at or after the rewrite. See [Post 09](posts/09-context-management-loop/index.md).

**Context anxiety.** A failure mode where output quality drops as the context window fills and the model rushes to finish. Countered by active context management: compaction, *tool-output offloading*, and resets.

**Context bridge.** The pair of on-disk artefacts a reset crosses on: a fixed spec saying what the goal is, and a moving *handoff file* saying where the work stands. A fresh window is not starting from nothing. See [Post 18](posts/18-long-horizon-ralph/index.md).

**Context editing.** Provider-side clearing of stale tool results, replaced with placeholders before the model sees them under a configured trigger and keep count. Distinct from compaction, which summarises rather than clears. See [Post 09](posts/09-context-management-loop/index.md).

**Context engineering.** The sibling discipline: deciding what the model sees on a single call. Harness engineering decides what happens *around* the call, and treats context management as one component inside it.

**Context reset.** Discarding the working context entirely and restarting from a durable artefact such as a spec or handoff file. The move that makes long-horizon work possible, and the engine of the *Ralph loop*.

**Control plane.** The org-level layer that governs many agents at once — permissions, budgets, audit, policy. The enterprise framing of harness engineering.

**Coordination tax.** The overhead a multi-agent design pays and a single agent never does: per-agent fixed tokens, latency set by the slowest worker plus synthesis, and partial failure. Price it before paying it. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Custom harness.** A harness you build and own, chosen when the work needs a loop, tool set, or guardrail a *prebuilt harness* does not expose. See [Post 02](posts/02-anatomy-of-a-harness/index.md).

**Decider.** The half of an *approval gate* that returns the verdict: a human, a model classifier, or a stub in a test. Separating it from the policy, which decides which calls are gated at all, is what makes a gate testable. See [Post 15](posts/15-human-in-the-loop/index.md).

**Deny-list.** A refusal policy naming forbidden commands or patterns, used to block a known-dangerous class such as `rm -rf` or a force-push. Cheap and useful, but it only stops what you anticipated.

**Destructive action.** A failure mode where an agent runs a dangerous command (`rm -rf`, a force-push, `DROP TABLE`). Bounded by a deny-list *hook* and a *sandbox*, not by trusting the model's judgement.

**Doom loop.** A failure mode where an agent repeats the same ineffective action without progress. Detected by *no-progress detection*; broken by a loop exit.

**Eager loading.** Putting every tool schema, skill and instruction into the window at startup regardless of the task. The default that *progressive disclosure* replaces.

**Effective context.** The share of a nominal context window a model actually uses well. Consistently shorter than the advertised figure, which is why calling the window small is a statement about the work rather than about the specification.

**Elicitation gap.** The literature's term for the *harness gap*: the distance between what a model can do and what its scaffold lets it do. Plot it across harness versions rather than reading it once. See [Post 04](posts/04-harness-beats-model/index.md).

**Exactly-once.** The property that a unit of work is performed one time and no more, even under concurrency or retry. Distinct from at-least-once delivery, which permits duplicates and therefore requires idempotent side effects.

**Fail-fast.** Surfacing an error at the step that caused it rather than letting it compound through later steps. The reason a verification loop runs per step rather than at the end.

**Guard exit.** A stop taken on the iteration cap, the budget or no-progress detection: the run did not finish and something caught it. It has to return a resumable position as well as a result, which the intended exit does not. See [Post 19](posts/19-loop-engineering/index.md).

**Handoff artefact.** A structured file (spec, plan, state summary) that carries context from one agent, iteration, or session to the next — the mechanism that lets work survive a context reset.

**Handoff contract.** The fields a *handoff file* must carry for a reset to be safe: a spec pointer, what is done, what is next, decisions and their reasons, open questions, and the paths that matter. Its completeness test is to seed a fresh window with the handoff alone and check that it can name the next concrete action. See [Post 18](posts/18-long-horizon-ralph/index.md).

**Handoff file.** The concrete artefact a *handoff artefact* is written to: a file on disk carrying the spec, the plan and the state a fresh context needs to continue. Rewritten each iteration, never appended to. See [Post 08](posts/08-state-filesystem-git/index.md).

**Harness.** Everything that is not the model that drives a single agent: the loop, tools, state, context management, memory, verification, hooks, permissions, and observability. *Orchestration* and long-horizon patterns appear on the same anatomy map but operate at a larger scale. The runtime that drives the model.

**Harness engineering.** The discipline of designing that harness — deciding when the agent stops, how errors are handled, and what guardrails keep it on track — so it succeeds on real tasks.

**Harness gap.** The distance between what a model can already do and what its harness lets it do. Close it before buying a bigger model: the model problem is whatever remains afterwards, not what was visible at the start. Also *elicitation gap*.

**Harness-as-a-Service (HaaS).** A shift from LLM APIs that return completions to APIs that return a *runtime* with the loop, tools, context management, and hooks built in. Also *harness API* (Osmani, 2026).

**Hook.** A deterministic script run at a lifecycle point (pre-tool, post-edit, pre-commit, session-start) to enforce a rule the model cannot be trusted to follow on its own.

**Hook lifecycle.** The set of points at which hooks fire, plus the blocking asymmetry across them: only a hook that runs before an action can prevent it, and one that runs after can only report, with the report re-entering the loop as an observation. See [Post 13](posts/13-hooks-enforcement/index.md).

**Hosted agent runtime.** A vendor service that runs the whole loop on its own machines and meters it by session time. The far end of the build-versus-rent axis, and the point at which lock-in has to be priced rather than assumed. See [Post 23](posts/23-economics-haas/index.md).

**Human-in-the-loop (HITL).** A harness pattern where a human approves, interrupts, or steers the agent at defined points on the autonomy spectrum.

**Idempotency key.** A stable identifier attached to a side-effecting action so a replay of that action is recognised and not performed twice. What makes a retry safe.

**Indirect prompt injection.** An attack in which instructions reach the model through content it reads (a web page, an issue, a file) rather than from the user. The reason tool output is untrusted data, not instructions. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Information-loss budget.** The fidelity you are willing to spend to reclaim window space, decided in advance and written into the summarisation prompt, and used to choose between offloading, clearing, compacting and resetting.

**Initialiser agent.** An agent that runs once to build the environment a long-running task needs — setup script, repository, progress file — leaving a coding agent to make incremental progress in every later session. See [Post 26](posts/26-capstone-coding-agent/index.md).

**Jail.** A working-directory boundary a sandboxed command may not escape. A correct jail check compares resolved paths, not string prefixes: `/worksecrets` is not inside `/work` despite sharing its characters.

**Layered exits.** The full set of stop conditions a production loop carries at once (final answer, iteration cap, budget, no-progress) rather than relying on any single one. See [Post 19](posts/19-loop-engineering/index.md).

**Lease.** A time-bounded claim on a task, so work held by a crashed agent returns to the pool instead of being stranded. What lets a leaderless task board recover.

**Least privilege.** Granting a task the narrowest scope, the shortest credential lifetime and the clearest per-run attribution it can work with, rather than whatever is convenient to configure. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Lethal trifecta.** Willison's (2025) name for the combination that makes an agent exploitable: access to private data, exposure to untrusted content, and the ability to communicate externally. Remove any one leg and the exfiltration path closes. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Loop engineering.** The sub-discipline of designing the loop that drives an agent — especially its *layered exits* — instead of hand-writing each prompt. The line that carried the reframe is Steinberger's: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents" (quoted in Osmani, 2026), who files the discipline one floor above the harness. See [Post 19](posts/19-loop-engineering/index.md).

**Memory file.** The durable, human-editable file (`CLAUDE.md`, `AGENTS.md`) where ratcheted rules live and which is read into context at session start. Rules are volatile and get retired on inspection; the spec is not. See [Post 10](posts/10-continual-learning-ratchet/index.md).

**Middleware.** A deterministic wrapper around the loop that intercepts whole turns — pre-completion checks, loop detection, context injection — where a *hook* fires at one named lifecycle point. The framework-side spelling of the same instinct.

**No-progress detection.** A stop condition that halts a loop when successive iterations stop changing anything, guarding against thrashing.

**Objective ground truth.** A verdict that does not depend on the model's opinion: a compiler, a test suite, a schema. The strongest rung of the *verifier ladder*, and the only kind that can gate a loop exit outright.

**Offloading.** Writing a large tool result to disk and returning a pointer, so the bytes never enter the prefix. The cheapest rung of context management, and the only one that costs no cache.

**One verifiable increment.** The sizing rule for a long-horizon iteration: the smallest change that leaves the repository in a state the tests can answer yes or no about. Simultaneously the commit boundary, the gate boundary and the review boundary. See [Post 18](posts/18-long-horizon-ralph/index.md).

**One writer always.** The 2026 revision of the single-agent steelman: extra agents may contribute intelligence, but only one of them writes. It permits *orchestrator-worker* while still refusing the uncoordinated swarm. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**One-shotting.** A failure mode where an agent attempts a whole multi-step task in a single sweep, producing one large change that is hard to review. Countered by a *planner / generator / evaluator* split that forces decomposition.

**Orchestration.** A layer that coordinates multiple agents as units, one level up from a single-agent harness. A harness drives one model; an orchestrator manages many agents.

**Orchestrator-worker.** A topology in which one agent decomposes a task and delegates units to workers it coordinates. Contrast the leaderless *shared-repo swarm*, where the repository is the coordinator. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Outcome eval.** Scoring whether the task actually resolved — tests passing, a pull request merged — rather than grading one completion. The third lens beside output evaluation and *trajectory eval*. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Outcome tag.** The attribute on a tool span recording which layer decided the call: `blocked` by a hook, `refused` by a sandbox, `denied` by an approval gate, or `ok`. One tag for several is how a silent gate hides. See [Post 21](posts/21-observability-traces/index.md).

**Override token.** A named, single-use, reason-carrying grant that lets one blocked call through and appends to an override log. The sanctioned escape hatch that stops a hook set being switched off wholesale, because a guardrail with no exception path gets removed rather than respected. See [Post 13](posts/13-hooks-enforcement/index.md).

**Partial-failure policy.** The decision, taken before a fan-out rather than after it, about what the lead does with results and a hole: fail the run, retry then degrade with a marker, or escalate. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**`pass@1` / `pass@k` / `pass^k`.** Benchmark scores over repeated attempts: resolved on a single try, resolved by *at least one* of k tries, and resolved by *all* k. A one-shot deployment is described by the first or the third; quoting the second flatters it by however much luck contributed. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Planner / generator / evaluator.** A pattern that splits planning, doing, and grading across separate agents, because an independent evaluator does not skew positive the way self-grading does. Sometimes "GANs for prose."

**Prebuilt harness.** A vendor's or framework's ready-made runtime that ships the loop, tools and guardrails for you. Faster to adopt, and its abstractions are its opinions. See [Post 20](posts/20-sdk-landscape/index.md).

**Production funnel.** The staged measurement that converts evals into money: first-pass success rate, then defect-escape rate, then dollars per merged pull request. It supplies the denominator a token figure alone is missing. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Progressive disclosure.** Loading a tool, skill, or piece of context only when the current task needs it, rather than at startup.

**Prompt cache.** Provider-side reuse of the key and value tensors for a byte-identical prompt prefix, billed at a steep discount. Prefix-keyed, so editing anything near the front invalidates everything after it, which is why stable layers go first.

**Quarantine.** A task-board state for work that has failed repeatedly, so a poisoned task stops being reclaimed by each fresh agent in turn. The state a *lease* needs behind it if reclaim is not to become a loop of its own. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Ralph loop.** The simplest long-horizon pattern (named by Geoffrey Huntley): feed the same prompt against a written spec, let the agent do one task and commit, reset to a fresh context, repeat until done.

**Ratchet principle.** "Every mistake becomes a rule." Each failure is converted into a durable constraint — a memory-file line, a hook, a reviewer check — so it cannot recur.

**Re-entry tax.** The fixed cost every fresh context pays before it does useful work — read the spec, read the handoff, orient in the repository — split into a frozen half a prompt cache serves and a volatile half it cannot. See [Post 18](posts/18-long-horizon-ralph/index.md).

**ReAct.** Reason → Act → Observe: the interleaving of reasoning steps and tool actions that most agent loops implement.

**Refused.** A tool outcome distinct from blocked, denied and ok: the call reached the tool and the sandbox stopped it from inside. Without its own outcome a sandbox refusal is indistinguishable in a trace from a command that ran.

**Resolved-rate.** The share of benchmark tasks a harness actually completed, reported as a mean over several seeds with its spread, because agent runs are stochastic. It means little without the cost per resolved task beside it. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Rollback.** Discarding everything since a *checkpoint*, tracked changes and untracked debris alike. What makes a reversible action cheap enough to take without asking first. See [Post 08](posts/08-state-filesystem-git/index.md).

**Rubber-stamp rate.** The proportion of approval requests answered without engagement, and the number that separates an approval gate from approval theatre. Measurable only if approvals are recorded, not just denials. See [Post 15](posts/15-human-in-the-loop/index.md).

**Run.** One complete execution of a harness from task to stop condition, and the unit observability is organised around. Most agent failure modes are visible only as shapes across a run, not as facts about a single turn.

**Sandbox.** An isolated execution environment (allow-listed commands, network isolation, ephemeral runtime) that bounds what an agent's tools can touch.

**Scaffold.** The behaviour-defining layer around the model: system prompt, tool descriptions, how responses are parsed, what is remembered across steps. Distinct from the *harness*, which is the execution mechanism.

**Scaffolding ceiling.** The limit on how far a harness can carry a given model: once the tools, the context and the control flow are right, what binds is whether the frozen weights can exploit them. Why "harness beats model" is a scoped claim rather than an absolute one. See [Post 04](posts/04-harness-beats-model/index.md).

**Seam.** An injected dependency at which an expensive thing — the model, the clock, the shell — can be replaced by a double, so the harness can be tested without a network. It has to exist from the first commit, because a harness that constructs its own model cannot be driven by a fake one. See [Post 24](posts/24-build-minimal-harness/index.md).

**Semantic conflict.** A merge git accepts and the mainline rejects: two disjoint hunks, both branches green, and a broken state that existed in neither. Only a gate on the merged result can catch it. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Shared-repo swarm.** Many agents working one repository with no central orchestrator, claiming tasks through the filesystem and isolating edits in *worktrees*. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Silent drift.** A failure mode where an agent quietly ignores project conventions, run after run. Fixed by the *ratchet*: the rule in a memory file, backed by a *hook* that enforces it.

**Skill.** A named, loadable bundle of capability — a set of tools, usage instructions, and sometimes a reference file — that the harness brings into context only when a task needs it. The unit of *progressive disclosure*.

**Span.** One timed, attributed unit inside a *trace*: a model call, a tool call, a hook, carrying its inputs, outcome and cost. See [Post 21](posts/21-observability-traces/index.md).

**Sprint contract.** A "definition of done" negotiated between a generator and an evaluator before work begins, so completion is judged against agreed criteria.

**Stall signal.** The thing a *no-progress detection* actually compares: a tool-call signature, an observable effect on disk, or a verifier score. A detector tuned to one shape of stall will not catch another. See [Post 19](posts/19-loop-engineering/index.md).

**Steering.** Injecting a human message into a running agent so it lands as the next observation rather than restarting the run. A property of the loop's input mode, not a feature added above the loop. See [Post 15](posts/15-human-in-the-loop/index.md).

**Stop condition.** Any rule that ends a loop: goal verified, max iterations, token/time budget exhausted, or no progress. Most agent bugs are stop-condition bugs.

**Stop gate.** A blocking hook on the loop's termination event that refuses the final-answer exit while a deterministic check is still failing — the verification loop promoted from a request into an exit the model cannot open. Pair it with an iteration cap, or a gate that never passes is an infinite loop. See [Post 13](posts/13-hooks-enforcement/index.md).

**Stop reason.** The attribute on a run span recording why the loop exited, with the canonical values `completed`, `max_iters`, `budget`, `no_progress` and `error`. Their distribution across runs is the cheapest health metric a harness has. See [Post 21](posts/21-observability-traces/index.md).

**Streaming turn.** A loop turn that begins executing a tool call as soon as its arguments are fully formed, before the model finishes speaking. Buys the tail of a response and costs parsing complexity; the loop's logic is identical either way.

**Structured feedback.** A verifier's report returned as data the model can act on rather than a bare pass or fail. The difference between a correction loop that converges and one that guesses.

**Task board.** A directory of files representing open, claimed and done work, where the filesystem's own atomicity is the concurrency control. No lock server, no database, no coordinator.

**Token-equivalent.** A costing unit that multiplies a token by its price relative to base input, so cache writes, cache reads and uncached input can be compared in one column. What turns a compaction decision into arithmetic. See [Post 09](posts/09-context-management-loop/index.md).

**Tool.** A single action the model can invoke through the loop (run bash, edit a file, call an API), described to it by a schema. A small set of general-purpose tools tends to beat a large set of narrow ones.

**Tool poisoning.** An injection planted in a tool's *description* rather than in its output, read by the model and usually invisible to the user (OWASP, 2025). It includes the "rug pull", where a server changes a description after the tool was approved. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Tool-call signature.** Tool name plus normalised arguments: the fingerprint whose repetition across consecutive turns is the classic *doom loop*. Comparing signatures alone misses an agent wandering in circles, so fold the observed effect in beside it. See [Post 05](posts/05-agent-failure-modes/index.md).

**Tool-output offloading.** Writing a large tool output (a 2,000-line log) to disk and returning a pointer, so it costs one line in the window rather than a re-send every turn. The pointer has to be actionable: a path the agent can genuinely read back.

**Tool-using evaluator.** A grader with its own tools and its own loop, which gathers first-hand evidence — running the suite, driving the application, querying the database — instead of judging the generator's account of the work. A verifier, not a judge. See [Post 12](posts/12-planner-generator-evaluator/index.md).

**Topology.** The shape of a multi-agent arrangement: single, orchestrator-worker, pipeline, or swarm. A decision about who writes and who reconciles, not about how many models are involved. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Trace.** The recorded sequence of *spans* for one run, and the primary debugging surface for a harness. Four of the six agent failure modes have signatures that exist only in the sequence.

**Trajectory eval.** Evaluating an agent on the *path* it took (steps, tool calls, outcome), not just a single final output. The eval lens harness engineering needs.

**Transient failure.** An error caused by the environment rather than the model: a rate limit, a timeout, a dropped connection. It calls for a retry with bounded backoff, not a stop condition, and its retries are charged to the same budget as everything else.

**Validate-then-execute.** The two-step dispatch discipline: check the arguments against the schema, then run only if they pass. The schema is the contract, and a call that violates it is refused and handed back for the model to fix. See [Post 06](posts/06-tools-bash-code/index.md).

**Verification gate.** The check on the loop's exit that a candidate answer must pass before the run counts as done, which turns *victory declaration* from a judgement call into a fact about the repository. See [Post 11](posts/11-verification-loops/index.md).

**Verification loop.** A per-step check (tests, self-critique) that surfaces errors immediately so they do not compound. "Success is silent; failures are verbose."

**Verifier ladder.** The ordered set of checks available to a verification loop, from compiler and tests through schema validation to an independent judge and finally self-critique. Strength and cost do not track each other monotonically. See [Post 11](posts/11-verification-loops/index.md).

**Victory declaration.** A failure mode where an agent marks a task complete without verifying it. The canonical reason to add a verification loop.

**Workflow.** A system whose steps are laid out in advance by code: the path is fixed and the model fills in the blanks at each stop along it (Anthropic, 2024). The contrast that gives *agent* its meaning, and the right answer more often than it is chosen. See [Post 01](posts/01-from-context-to-harness/index.md).

**Worktree.** A separate working copy of a git repository that lets a parallel agent make edits in isolation, avoiding conflicts with other agents on the same repo.
