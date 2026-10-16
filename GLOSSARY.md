# Glossary

The terms used across Harness Engineering, alphabetised, one entry each. The series is the sequel to the `context-engineering` series, and the terms the two share (agent loop, context rot, context window, MCP, prompt cache, RAG, sub-agent, tool) are defined here as this series uses them, from the side of the runtime rather than of a single call. The fixed vocabulary (the eleven components, the four exits, the six failure modes, the evidence grades) is set out in the [notation guide](notation_guide.md).

---

**Agent.** A model plus everything around it that lets it act, not just respond: the model, the scaffold, and the harness operating together in a loop. Its founding equation, `Agent = Model + Harness`, is Trivedy's (2026), popularised by Osmani. See [Post 01](posts/01-from-context-to-harness/index.md).

**`Agent = Model + Harness`.** The equation the series is built on: everything in an agent that is not the model is the harness. Stated by Trivedy (2026) with the line "If you're not the model, you're the harness", and written in code font throughout the series. See [Post 01](posts/01-from-context-to-harness/index.md).

**Agent loop.** The core cycle a harness runs: call the model, parse its tool calls, execute them, feed the results back, and repeat until a stop condition fires. Also *control loop*; the first of the *eleven components*, named simply "loop" in the component list. See [Post 03](posts/03-the-agent-loop/index.md).

**Allow-list.** A sandbox policy that permits only named programs and refuses everything else, the inverse of a deny-list. A deny-list stops the dangers its author thought of; an allow-list also stops the ones nobody thought of. Allow-listing an interpreter allow-lists everything it can run, so `python` on an allow-list is not a boundary. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Approval gate.** A point in the loop where a call classed as sensitive is routed to a human or a stricter policy for a verdict before it executes. A denied call never runs, and the denial is recorded on the run. See [Post 15](posts/15-human-in-the-loop/index.md).

**Approve and remember.** An approval outcome that returns a persisted rule alongside the verdict, so later calls matching that rule stop asking. It is what lets an approval queue drain itself rather than needing a policy rewrite. See [Post 15](posts/15-human-in-the-loop/index.md).

**Atomic claim.** A task claimed by an operation that exactly one caller can succeed at, such as creating a per-task token with `O_CREAT | O_EXCL`. An atomic primitive does not by itself buy an exclusive claim: a rename moves a file atomically, but whether a second rename of the same file fails depends on the platform, and checking afterwards does not close the race. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Autonomy spectrum.** The range of oversight settings between fully manual and fully autonomous, framed by Morris (2026) as humans *outside*, *in*, or *on* the loop. The mistake is picking one setting for a whole agent rather than one per class of action. See [Post 15](posts/15-human-in-the-loop/index.md).

**Backstop exit.** A loop exit that exists only so that a loop which never reaches its intended stop still terminates, such as the *iteration cap*. No loop should run without one. See [Post 03](posts/03-the-agent-loop/index.md).

**Batch turn.** A loop turn that waits for the model's complete response before acting. Simpler than a *streaming turn*, and the right default for building and understanding a loop. See [Post 03](posts/03-the-agent-loop/index.md).

**Binding Constraint Thesis.** Zhang et al.'s (2026) formal statement of "harness beats model": across models of comparable frontier capability on long-horizon tasks, the execution harness is often a stronger determinant of the score than the weights. See [Post 04](posts/04-harness-beats-model/index.md).

**Blast radius.** The scope of damage a single agent action can cause if it goes wrong. Sandboxes and *permissions* exist to bound it. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Budget exit.** The third of the four *loop exits*: a stop condition expressed in tokens or wall-clock seconds rather than iterations, because a single turn can be cheap or enormous. Checked after a call, it can be crossed by one iteration; reserving before spending avoids that. See [Post 03](posts/03-the-agent-loop/index.md) and [Post 19](posts/19-loop-engineering/index.md).

**Checkpoint.** A commit taken after a verified step and kept as a point the loop can return to, distinct from a version-control commit meant for human review. It is what makes a risky but reversible step cheap to take. See [Post 08](posts/08-state-filesystem-git/index.md).

**Compaction.** Replacing a span of conversation history with a shorter summary of it, in place, to reclaim window space. Lossy by construction, and it invalidates every prompt-cache breakpoint at or after the rewrite. See [Post 09](posts/09-context-management-loop/index.md).

**Context anxiety.** One of the six *failure modes*, named by Anthropic (Rajasekaran, 2026): as the context window fills, output quality drops and the model cuts corners or races to finish. Countered by active *context management*: compaction, *tool-output offloading*, and resets. See [Post 05](posts/05-agent-failure-modes/index.md).

**Context bridge.** The pair of on-disk artefacts a reset crosses on: a fixed spec saying what the goal is, and a moving *handoff file* saying where the work stands. A fresh window that has both is not starting from nothing. See [Post 18](posts/18-long-horizon-ralph/index.md).

**Context editing.** Provider-side clearing of stale tool results, replaced with placeholders before the model sees them, under a configured trigger and keep count. Distinct from compaction, which summarises rather than clears. See [Post 09](posts/09-context-management-loop/index.md).

**Context engineering.** The sibling discipline, and the subject of the `context-engineering` series: deciding what the model sees on a single call. Harness engineering decides what happens around the call, and treats context management as one component inside it. See [Post 01](posts/01-from-context-to-harness/index.md).

**Context management.** The fourth of the *eleven components*, one of the four that feed the loop: keeping a long-running loop's window useful as it fills, by a ladder of moves tried cheapest first (offload a large output to disk, clear results already acted on, compact older turns into a summary, reset behind a handoff file). One of the four components a system must have to count as a harness at all. See [Post 09](posts/09-context-management-loop/index.md).

**Context reset.** Discarding the working context entirely and restarting from a durable artefact such as a spec or handoff file. The move that makes long-horizon work possible, and the engine of the *Ralph loop*. See [Post 09](posts/09-context-management-loop/index.md) and [Post 18](posts/18-long-horizon-ralph/index.md).

**Context rot.** The degradation of a model's output as its context window fills with stale, redundant or distracting material, so that a long-running loop gets worse the longer it runs. The token-level account is the `context-engineering` series' (`ctx-006`); this series treats it as the problem *context management* exists to fight. See [Post 09](posts/09-context-management-loop/index.md).

**Context window.** The bounded span of tokens a model reads on one call: the system prompt, the tool descriptions, the conversation so far and the latest observation. Small and expensive beside the filesystem, which is why a harness keeps durable *state* on disk and treats the window as a scratchpad. See [Post 08](posts/08-state-filesystem-git/index.md) and [Post 09](posts/09-context-management-loop/index.md).

**Control plane.** The organisation-level layer that governs many agents at once: permissions, budgets, audit, policy. The enterprise framing of harness engineering. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Coordination tax.** The overhead a multi-agent design pays and a single agent never does: per-agent fixed tokens, latency set by the slowest worker plus the lead's own calls, and partial failure. It should be priced before it is paid. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Custom harness.** The layer a team adds on top of a *prebuilt harness*: its tools, its memory file, its enforcement hooks, its sandbox policy and its evaluations; the policy that runs on the mechanism a vendor ships. See [Post 02](posts/02-anatomy-of-a-harness/index.md).

**Decider.** The half of an *approval gate* that returns the verdict: a human, a model classifier, or a stub in a test. Separating it from the policy, which decides which calls are gated at all, is what makes a gate testable. See [Post 15](posts/15-human-in-the-loop/index.md).

**Deny-list.** A refusal policy naming forbidden commands or patterns, used to block a known-dangerous class such as `rm -rf` or a force-push. Cheap and useful, but it only stops what its author anticipated. See [Post 13](posts/13-hooks-enforcement/index.md).

**Destructive action.** One of the six *failure modes*, and the safety failure among them: the agent runs something dangerous (`rm -rf`, `git push --force`, `DROP TABLE`). Bounded by a deny-list *hook* and a *sandbox*, not by trusting the model's judgement. See [Post 05](posts/05-agent-failure-modes/index.md).

**Doom loop.** One of the six *failure modes*: the agent repeats the same ineffective action (re-running a failing command, re-reading the same file) and makes no progress while looking busy. Detected by *no-progress detection*; broken by a loop exit. See [Post 05](posts/05-agent-failure-modes/index.md).

**Eager loading.** Putting every tool schema, skill and instruction into the window at startup regardless of the task. The default that *progressive disclosure* replaces. See [Post 07](posts/07-skills-mcp-runtime/index.md).

**Effective context.** The share of a nominal context window a model actually uses well. Consistently shorter than the advertised figure, which is why calling the window small is a statement about the work rather than about the specification. See [Post 08](posts/08-state-filesystem-git/index.md).

**Elicitation gap.** The literature's term for the *harness gap*: the distance between what a model can do and what its scaffold lets it do (Starace, 2026). Best plotted across harness versions rather than read once. See [Post 04](posts/04-harness-beats-model/index.md).

**Eleven components.** The parts of a harness as post 02 maps them, named the same way everywhere in the series: the *loop* at the centre; four that feed it (*tools*, *state*, *context management*, *memory*); four that govern it (*verification*, *hooks*, *permissions*, *observability*); and two that work at a larger scale (*orchestration*, *long-horizon patterns*). Numbered 01 to 11 in the order loop, tools, state, context management, memory, verification, hooks, permissions, orchestration, long-horizon patterns, observability. See [Post 02](posts/02-anatomy-of-a-harness/index.md).

**Evidence grades.** The three strengths at which the series ranks a claim that the harness matters more than the model: *firm* (the same model on the same benchmark, before and after a harness change), *controlled* (a comparison of scaffolds with the model and the tasks held fixed), and *reported* (a multiple quoted at one remove, whose base cannot be checked). A reported multiple is never promoted to a measured one. See [Post 04](posts/04-harness-beats-model/index.md).

**Exactly-once.** The property that a unit of work is performed one time and no more, even under concurrency or retry. Distinct from at-least-once delivery, which permits duplicates and therefore requires idempotent side effects. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Fail-fast.** Surfacing an error at the step that caused it rather than letting it compound through later steps. The reason a verification loop runs per step rather than at the end. See [Post 11](posts/11-verification-loops/index.md).

**Failure modes.** The six named ways an agent run goes wrong, each tied to the component that fixes it: *victory declaration*, *context anxiety*, *one-shotting*, *doom loop*, *silent drift*, and *destructive action*. See [Post 05](posts/05-agent-failure-modes/index.md).

**Final-answer exit.** The first of the four *loop exits*, and the intended one: the model finishes, signalled by a terminal stop reason from the provider rather than by the mere absence of a tool call. Whether the work is actually done is a separate question, answered by a *verification gate*. See [Post 03](posts/03-the-agent-loop/index.md).

**Guard exit.** A stop taken on the iteration cap, the budget or no-progress detection: the run did not finish and something caught it. It has to return a resumable position as well as a result, which the intended exit does not. See [Post 19](posts/19-loop-engineering/index.md).

**Handoff artefact.** A structured file (spec, plan, state summary) that carries context from one agent, iteration, or session to the next: the mechanism that lets work survive a context reset. See [Post 08](posts/08-state-filesystem-git/index.md).

**Handoff contract.** The fields a *handoff file* must carry for a reset to be safe: post 08's four (spec, done, next, and the state: branch, last checkpoint and the paths that matter) plus the two a long-horizon loop adds, decisions with their reasons and open questions. Its completeness test is to seed a fresh window with the handoff alone and check that it can name the next concrete action. See [Post 18](posts/18-long-horizon-ralph/index.md).

**Handoff file.** The concrete artefact a *handoff artefact* is written to: a file on disk carrying the spec, what is done, what is next and a checkable state, which is what a fresh context needs to continue. Rewritten each iteration, never appended to. See [Post 08](posts/08-state-filesystem-git/index.md).

**Harness.** Everything that is not the model: the runtime that drives a single agent through the loop, tools, state, context management, memory, verification, hooks, permissions, and observability. *Orchestration* and *long-horizon patterns* appear on the same component map but operate at a larger scale. In the nesting the series uses, the model sits inside the scaffold, the scaffold inside the harness, and the harness inside orchestration. See [Post 01](posts/01-from-context-to-harness/index.md) and [Post 02](posts/02-anatomy-of-a-harness/index.md).

**Harness engineering.** The discipline of designing that harness (deciding when the agent stops, how errors are handled, and what guardrails keep it on track) so that it succeeds on real tasks. See [Post 01](posts/01-from-context-to-harness/index.md).

**Harness gap.** The distance between what a model can already do and what its harness lets it do. It is closed before a bigger model is bought: the model problem is whatever remains afterwards, not what was visible at the start. Also *elicitation gap*. See [Post 04](posts/04-harness-beats-model/index.md).

**Harness-as-a-Service (HaaS).** A shift from LLM APIs that return completions to APIs that return a runtime, with the loop, tools, context management, and hooks built in. Also *harness API*. Named by Trivedy (2025) and popularised by Osmani (2026). See [Post 23](posts/23-economics-haas/index.md).

**Hook.** A deterministic script run at a lifecycle point (session start, pre-tool, post-edit, pre-commit) to enforce a rule the model cannot be trusted to follow on its own. *Hooks* are the seventh of the *eleven components*, one of the four that govern the loop, and the enforcement tooth of the *ratchet*. See [Post 13](posts/13-hooks-enforcement/index.md).

**Hook lifecycle.** The set of points at which hooks fire, plus the blocking asymmetry across them: only a hook that runs before an action can prevent it, and one that runs after can only report, with the report re-entering the loop as an observation. See [Post 13](posts/13-hooks-enforcement/index.md).

**Hosted agent runtime.** A vendor service that runs the whole loop on its own machines and meters it by session time. The far end of the build-versus-rent axis, and the point at which lock-in has to be priced rather than assumed. See [Post 23](posts/23-economics-haas/index.md).

**Human-in-the-loop (HITL).** A harness pattern where a human approves, interrupts, or steers the agent at defined points on the *autonomy spectrum*. See [Post 15](posts/15-human-in-the-loop/index.md).

**Idempotency key.** A stable identifier attached to a side-effecting action so that a replay of that action is recognised and not performed twice. What makes a retry safe. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Indirect prompt injection.** An attack in which instructions reach the model through content it reads (a web page, an issue, a file) rather than from the user. The reason tool output is untrusted data, not instructions. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Information-loss budget.** The fidelity a team is willing to spend to reclaim window space, decided in advance and written into the summarisation prompt, and used to choose between offloading, clearing, compacting and resetting. See [Post 09](posts/09-context-management-loop/index.md).

**Initialiser agent.** An agent that runs once to build the environment a long-running task needs (setup script, feature list, progress file and an initial git commit), leaving a coding agent to make incremental progress in every later session. See [Post 26](posts/26-capstone-coding-agent/index.md).

**Iteration cap.** The second of the four *loop exits*: a hard integer ceiling on turns, so that a loop which never reaches a final answer still terminates. A *backstop exit*, set well above the iteration count real tasks need; it bounds turns, not cost. See [Post 03](posts/03-the-agent-loop/index.md).

**Jail.** A working-directory boundary a sandboxed command may not escape. A correct jail check compares resolved paths, not string prefixes: `/worksecrets` is not inside `/work` despite sharing its characters. See [Post 25](posts/25-build-harness-plus/index.md).

**Layered exits.** The full set of stop conditions a production loop carries at once (final answer, iteration cap, budget, no progress), checked in an order, rather than reliance on any single one. See [Post 19](posts/19-loop-engineering/index.md).

**Lease.** A time-bounded claim on a task, so that work held by a crashed agent returns to the pool instead of being stranded. What lets a leaderless task board recover. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Least privilege.** Granting a task the narrowest scope, the shortest credential lifetime and the clearest per-run attribution it can work with, rather than whatever is convenient to configure. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Lethal trifecta.** Willison's (2025) name for the combination that makes an agent exploitable: access to private data, exposure to untrusted content, and the ability to communicate externally. Removing any one leg closes the exfiltration path. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Long-horizon patterns.** The tenth of the *eleven components*, one of the two that work at a larger scale: the patterns for work that outgrows one context window, in which the harness resets to a fresh context against a written spec and repeats, carrying state on disk and crossing each reset on a *context bridge*. The simplest is the *Ralph loop*. See [Post 18](posts/18-long-horizon-ralph/index.md).

**Loop.** The first of the *eleven components*, at the centre of the map: the *agent loop*, reason, act, observe, repeated until one of the four *loop exits* fires. Every other component either feeds it, governs it, or works around it at a larger scale. See [Post 03](posts/03-the-agent-loop/index.md).

**Loop engineering.** The discipline of designing the loop that drives an agent, especially its *layered exits*, instead of hand-writing each prompt. The line that carried the reframe is Peter Steinberger's: "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents" (quoted in Osmani, 2026). See [Post 19](posts/19-loop-engineering/index.md).

**Loop exits.** The four stop conditions every real loop carries, numbered the same way throughout the series: (1) the *final-answer exit*, the intended one; (2) the *iteration cap*; (3) the *budget exit*; (4) *no-progress detection*. The last three are guards. See [Post 03](posts/03-the-agent-loop/index.md).

**MCP (Model Context Protocol).** An open protocol by which a host application's client connects to servers that expose tools, resources and prompts. This series looks at it from the host's side, as one way capability enters the loop at runtime; the protocol itself is the subject of the `mcp` series (`mcp-002`, `mcp-011`). See [Post 07](posts/07-skills-mcp-runtime/index.md).

**Memory.** The fifth of the *eleven components*, one of the four that feed the loop: knowledge carried across sessions rather than within one, chiefly a *memory file* read in at the start of every session and the *ratchet* that writes new rules into it. What lets a harness get better over time rather than repeat the same mistakes. See [Post 10](posts/10-continual-learning-ratchet/index.md).

**Memory file.** The durable, human-editable file (`CLAUDE.md`, `AGENTS.md`) where ratcheted rules live and which is read into context at session start. Rules are volatile and get retired on inspection; the spec is not. See [Post 10](posts/10-continual-learning-ratchet/index.md).

**Middleware.** A deterministic wrapper around the loop that intercepts whole turns (pre-completion checks, loop detection, context injection), where a *hook* fires at one named lifecycle point. The framework-side spelling of the same instinct. See [Post 04](posts/04-harness-beats-model/index.md).

**Model.** The trained weights behind a provider's API, which a harness treats as fixed: it takes a window and returns text and tool calls, and keeps no state between calls. The innermost ring of the nesting model, scaffold, harness, orchestration. See [Post 01](posts/01-from-context-to-harness/index.md).

**No-progress detection.** The fourth of the four *loop exits*: a stop condition that halts a loop when successive iterations stop changing anything, guarding against thrashing and the *doom loop*. Its naive form, repeated tool calls over the last few turns, can kill an agent that is legitimately polling or retrying. See [Post 03](posts/03-the-agent-loop/index.md).

**Objective ground truth.** A verdict that does not depend on the model's opinion: a compiler, a test suite, a schema. The strongest rung of the *verifier ladder*, and the only kind that can gate a loop exit outright. See [Post 11](posts/11-verification-loops/index.md).

**Observability.** The eleventh of the *eleven components*, one of the four that govern the loop: a *trace* of each run (inputs, outputs, tokens, latency, tool calls, sub-agent spans, and the reason the loop stopped) from which the failing component can be found and repaired. Taught last for convenience, and the component most regretted when deferred. See [Post 21](posts/21-observability-traces/index.md).

**Offloading.** Writing a large tool result to disk and returning a pointer, so that the bytes never enter the prefix. The cheapest rung of context management, and the only one that costs no cache. See [Post 09](posts/09-context-management-loop/index.md).

**One verifiable increment.** The sizing rule for a long-horizon iteration: the smallest change that leaves the repository in a state the tests can answer yes or no about. At once the commit boundary, the gate boundary and the review boundary. See [Post 18](posts/18-long-horizon-ralph/index.md).

**One writer always.** The 2026 revision of the single-agent steelman: extra agents may contribute intelligence, but only one of them writes. It permits *orchestrator-worker* while still refusing the uncoordinated swarm. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**One-shotting.** One of the six *failure modes*: the agent attempts a whole multi-step task in a single sweep, producing one large change that is hard to review and often wrong somewhere. Countered by a *planner, generator, evaluator* split that forces decomposition. See [Post 05](posts/05-agent-failure-modes/index.md).

**Orchestration.** The ninth of the *eleven components*, one of the two that work at a larger scale: coordinating several agents as units, one level up from a single-agent harness. A harness drives one model; an orchestrator manages many agents. Powerful and over-used: the default is one agent with sub-tasks. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Orchestrator-worker.** A topology in which one agent decomposes a task and delegates units to workers it coordinates. Contrast the leaderless *shared-repo swarm*, where the repository is the coordinator. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Outcome eval.** Scoring whether the task actually resolved (tests passing, a pull request merged) rather than grading one completion. The third lens beside output evaluation and *trajectory eval*. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Outcome tag.** The attribute on a tool span recording which layer decided the call: `blocked` by a hook, `refused` by a sandbox, `denied` by an approval gate, or `ok`. One tag for several is how a silent gate hides. See [Post 21](posts/21-observability-traces/index.md).

**Override token.** A named, single-use, reason-carrying grant that lets one blocked call through and appends to an override log. The sanctioned escape hatch that stops a hook set being switched off wholesale, because a guardrail with no exception path gets removed rather than respected. See [Post 13](posts/13-hooks-enforcement/index.md).

**Partial-failure policy.** The decision, taken before a fan-out rather than after it, about what the lead does with results and a hole: fail the run, retry then degrade with a marker, or escalate. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**`pass@1`, `pass@k`, `pass^k`.** Benchmark scores over repeated attempts: resolved on a single try, resolved by *at least one* of $k$ tries, and resolved by *all* $k$. A one-shot deployment is described by the first or the third; quoting the second flatters it by however much luck contributed. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Permissions.** The eighth of the *eleven components*, one of the four that govern the loop: the declarative rules, the sandbox and the approvals that bound what a run can touch, so that a mistake, or a prompt injection reaching a tool, is contained. Which actions a human must approve is a policy on this component. See [Post 14](posts/14-permissions-sandboxes/index.md) and [Post 15](posts/15-human-in-the-loop/index.md).

**Planner, generator, evaluator.** A pattern that splits planning, doing, and grading across separate agents, because a standalone evaluator can be tuned to be sceptical far more easily than a model grading its own work. Rajasekaran (Anthropic, 2026) designed it after the generator and discriminator of a generative adversarial network; Osmani (2026) calls it "GANs for prose". See [Post 12](posts/12-planner-generator-evaluator/index.md).

**Prebuilt harness.** A vendor's or framework's ready-made runtime that ships the loop, tools and guardrails. Faster to adopt, and its abstractions are its opinions. See [Post 02](posts/02-anatomy-of-a-harness/index.md) and [Post 20](posts/20-sdk-landscape/index.md).

**Production funnel.** The staged measurement that converts evals into money: first-pass success rate, then defect-escape rate, then dollars per merged pull request. It supplies the denominator a token figure alone is missing. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Progressive disclosure.** Loading a tool, skill, or piece of context only when the current task needs it, rather than at startup. See [Post 07](posts/07-skills-mcp-runtime/index.md).

**Prompt cache.** Provider-side reuse of the key and value tensors for a byte-identical prompt prefix, billed at a steep discount. Prefix-keyed, so editing anything near the front invalidates everything after it, which is why stable content goes first. The token-level account is `ctx-005`. See [Post 07](posts/07-skills-mcp-runtime/index.md) and [Post 09](posts/09-context-management-loop/index.md).

**Quarantine.** A task-board state for work that has failed repeatedly, so that a poisoned task stops being reclaimed by each fresh agent in turn. The state a *lease* needs behind it if reclaim is not to become a loop of its own. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**RAG (retrieval-augmented generation).** Retrieving passages from a corpus and placing them in the window before the model answers. A topic of the `context-engineering` series; in this series retrieval is one more tool the loop can call, and the series does not re-teach it.

**Ralph loop.** The simplest long-horizon pattern (named by Huntley, 2025): feed the same prompt against a written spec, let the agent do one task and commit, reset to a fresh context, and repeat until done. See [Post 18](posts/18-long-horizon-ralph/index.md).

**Ratchet.** The principle "every mistake becomes a rule": each failure is converted into durable constraints (a *memory file* line so the model reads it, a *hook* so it is enforced, a reviewer check so it is caught) so that it has to defeat all three to recur. Also *ratchet principle*. See [Post 10](posts/10-continual-learning-ratchet/index.md).

**Re-entry tax.** The fixed cost every fresh context pays before it does useful work (read the spec, read the handoff, orient in the repository), split into a frozen half a prompt cache serves and a volatile half it cannot. See [Post 18](posts/18-long-horizon-ralph/index.md).

**ReAct.** Reason, act, observe: the interleaving of reasoning steps and tool actions that most agent loops implement, named by the ReAct line of work (Yao et al., 2023). See [Post 03](posts/03-the-agent-loop/index.md).

**Refused.** A tool outcome distinct from blocked, denied and ok: the call reached the tool and the sandbox stopped it from inside. Without its own outcome a sandbox refusal is indistinguishable in a trace from a command that ran. See [Post 21](posts/21-observability-traces/index.md).

**Resolved-rate.** The share of benchmark tasks a harness actually completed, reported as a mean over several seeds with its spread, because agent runs are stochastic. It means little without the cost per resolved task beside it. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Rollback.** Discarding the tracked changes since a *checkpoint* and the untracked debris inside the paths the step could touch; ignored files and untracked files elsewhere are kept. What makes a reversible action cheap enough to take without asking first. See [Post 08](posts/08-state-filesystem-git/index.md).

**Rubber-stamp rate.** The proportion of approval requests answered without engagement, and the number that separates an approval gate from approval theatre. Measurable only if approvals are recorded, not just denials. See [Post 15](posts/15-human-in-the-loop/index.md).

**Run.** One complete execution of a harness from task to stop condition, and the unit observability is organised around. Most agent failure modes are visible only as shapes across a run, not as facts about a single turn. See [Post 21](posts/21-observability-traces/index.md).

**Sandbox.** An isolated execution environment (an allow-list, a path boundary, network isolation, a resource limit, an ephemeral runtime) that bounds what an agent's tools can touch. Part of the *permissions* component. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Scaffold.** The behaviour-defining layer around the model: system prompt, tool descriptions, how responses are parsed, what is remembered across steps. Distinct from the *harness*, which is the execution mechanism around it. See [Post 01](posts/01-from-context-to-harness/index.md).

**Scaffolding ceiling.** The limit on how far a harness can carry a given model: once the tools, the context and the control flow are right, what binds is whether the frozen weights can exploit them. Why "harness beats model" is a scoped claim rather than an absolute one. See [Post 04](posts/04-harness-beats-model/index.md).

**Seam.** An injected dependency at which an expensive thing (the model, the clock, the shell) can be replaced by a double, so that the harness can be tested without a network. It has to exist from the first commit, because a harness that constructs its own model cannot be driven by a fake one. See [Post 24](posts/24-build-minimal-harness/index.md).

**Semantic conflict.** A merge git accepts and the mainline rejects: two disjoint hunks, both branches green, and a broken state that existed in neither. Only a gate on the merged result can catch it. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Shared-repo swarm.** Many agents working one repository with no central orchestrator, claiming tasks through the filesystem and isolating edits in *worktrees*. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Silent drift.** One of the six *failure modes*: the agent quietly ignores the project's conventions (the wrong test framework, the wrong formatting, a pattern corrected before) and keeps doing so, run after run. Fixed by the *ratchet*: the rule in a memory file, backed by a *hook* that enforces it. See [Post 05](posts/05-agent-failure-modes/index.md).

**Skill.** A named, loadable bundle of capability (a set of tools, usage instructions, and sometimes a reference file) that the harness brings into context only when a task needs it. The unit of *progressive disclosure*. See [Post 07](posts/07-skills-mcp-runtime/index.md).

**Span.** One timed, attributed unit inside a *trace*: a model call, a tool call, a hook, carrying its inputs, outcome and cost. See [Post 21](posts/21-observability-traces/index.md).

**Sprint contract.** A definition of done negotiated between a generator and an evaluator before work begins, so that completion is judged against agreed criteria. See [Post 12](posts/12-planner-generator-evaluator/index.md).

**Stall signal.** The thing a *no-progress detection* actually compares: a tool-call signature, an observable effect on disk, or a verifier score. A detector tuned to one shape of stall will not catch another. See [Post 19](posts/19-loop-engineering/index.md).

**State.** Component 03, one of the *eleven components* and of the four that feed the loop: what the agent keeps on disk rather than in the window (intermediate results, plans, a handoff file), with git adding versioning and rollback. The window is small and expensive; the filesystem is large and cheap. See [Post 08](posts/08-state-filesystem-git/index.md).

**Steering.** Injecting a human message into a running agent so that it lands as the next observation rather than restarting the run. Between turns any loop the harness drives can take one; interrupting mid-turn needs a streaming connection. See [Post 15](posts/15-human-in-the-loop/index.md).

**Stop condition.** Any rule that ends a loop; the four a production loop carries are the *loop exits* (final answer, iteration cap, budget, no progress). This series argues that many agent failures are stop-condition faults rather than reasoning faults; the claim rests on which failures have been named, not on a measurement. See [Post 03](posts/03-the-agent-loop/index.md).

**Stop gate.** A blocking hook on the loop's termination event that refuses the final-answer exit while a deterministic check is still failing: the verification loop promoted from a request into an exit the model cannot open. It needs an iteration cap beside it, or a gate that never passes is an infinite loop. See [Post 13](posts/13-hooks-enforcement/index.md).

**Stop reason.** The attribute on a run span recording why the loop exited, with the canonical values `completed`, `max_iters`, `budget`, `no_progress` and `error`. Their distribution across runs is the cheapest health metric a harness has. See [Post 21](posts/21-observability-traces/index.md).

**Streaming turn.** A loop turn that begins executing a tool call as soon as its arguments are fully formed, before the model finishes its response. It buys the tail of a response and costs parsing complexity; the loop's logic is identical either way. See [Post 03](posts/03-the-agent-loop/index.md).

**Structured feedback.** A verifier's report returned as data the model can act on rather than a bare pass or fail. The difference between a correction loop that converges and one that guesses. See [Post 11](posts/11-verification-loops/index.md).

**Sub-agent.** An agent the harness dispatches with its own fresh context to do one bounded piece of work and return a result, so that the work's intermediate tokens never enter the parent's window. Distinct from *orchestration* of peers: the parent keeps control and the sub-agent is one of its actions. See [Post 16](posts/16-multi-agent-orchestration/index.md) and [Post 25](posts/25-build-harness-plus/index.md).

**Task board.** A directory of files representing open, claimed and done work, where an exclusive file create is the concurrency control. No lock server, no database, no coordinator. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).

**Token-equivalent.** A costing unit that multiplies a token by its price relative to base input, so that cache writes, cache reads and uncached input can be compared in one column. What turns a compaction decision into arithmetic. See [Post 09](posts/09-context-management-loop/index.md).

**Tool.** A single action the model can invoke through the loop (run bash, edit a file, call an API), described to it by a schema. *Tools* are the second of the *eleven components*, one of the four that feed the loop; a small set of general-purpose tools, above all bash and code execution, tends to beat a large set of narrow ones. See [Post 06](posts/06-tools-bash-code/index.md).

**Tool poisoning.** An injection planted in a tool's description rather than in its output, read by the model and usually invisible to the user (Invariant Labs, 2025; OWASP MCP03, 2025). Invariant Labs also names the "rug pull", where a server changes a description after the tool was approved. See [Post 14](posts/14-permissions-sandboxes/index.md).

**Tool-call signature.** Tool name plus normalised arguments: the fingerprint whose repetition across consecutive turns is the classic *doom loop*. Comparing signatures alone cannot tell a poll whose result changes from a retry whose result does not; the companion's detector compares signatures only, and comparing the results as well separates the two. See [Post 05](posts/05-agent-failure-modes/index.md).

**Tool-output offloading.** Writing a large tool output (a 2,000-line log) to disk and returning a pointer, so that the window carries a short pointer (path, size, head and tail) rather than the whole output on every later call. The pointer has to be actionable: a path the agent can genuinely read back. See [Post 09](posts/09-context-management-loop/index.md).

**Tool-using evaluator.** A grader with its own tools and its own loop, which gathers first-hand evidence (running the suite, driving the application, querying the database) instead of judging the generator's account of the work. A verifier, not a judge. See [Post 12](posts/12-planner-generator-evaluator/index.md).

**Topology.** The shape of a multi-agent arrangement: single, orchestrator-worker, pipeline, or swarm. A decision about who writes and who reconciles, not about how many models are involved. See [Post 16](posts/16-multi-agent-orchestration/index.md).

**Trace.** The recorded sequence of *spans* for one run, and the primary debugging surface for a harness. Four of the six agent failure modes have signatures that exist only in the sequence. See [Post 21](posts/21-observability-traces/index.md).

**Trajectory eval.** Evaluating an agent on the path it took (steps, tool calls, outcome), not just a single final output. The eval lens harness engineering needs. See [Post 22](posts/22-evaluating-harnesses/index.md).

**Transient failure.** An error caused by the environment rather than the model: a rate limit, an overload, a timeout, a dropped connection. It calls for a retry with bounded backoff, counted apart from the iteration cap, not a stop condition, and its spend is charged to the same budget as everything else. A 429 from a spend cap is not transient: it is a budget stop. See [Post 19](posts/19-loop-engineering/index.md).

**Validate-then-execute.** The two-step dispatch discipline: check the arguments against the schema, then run only if they pass. The schema is the contract, and a call that violates it is refused and handed back for the model to fix. See [Post 06](posts/06-tools-bash-code/index.md).

**Verification.** The sixth of the *eleven components*, one of the four that govern the loop: checking the agent's work against something other than its own word (tests, a schema, a compiler, an independent evaluator) so that errors surface at the step that caused them. Its principle, HumanLayer's as Osmani (2026) reports it, is "success is silent, failures are verbose". One of the four components a system must have to count as a harness. See [Post 11](posts/11-verification-loops/index.md).

**Verification gate.** The check on the loop's exit that a candidate answer must pass before the run counts as done, which turns *victory declaration* from a judgement call into a fact about the repository. See [Post 11](posts/11-verification-loops/index.md).

**Verification loop.** A per-step check against ground truth (tests, a schema, a compiler) that surfaces errors immediately so they do not compound, feeding each failure back into the loop as the next observation. See [Post 11](posts/11-verification-loops/index.md).

**Verifier ladder.** The checks available to a verification loop, from cheapest to dearest: schema validation, a compiler or type checker, a test suite, an independent judge, and the model's own self-critique. The line that matters falls between the test suite and the judge: above it a failure is a fact, below it a verdict is an opinion. See [Post 11](posts/11-verification-loops/index.md).

**Victory declaration.** One of the six *failure modes*, and the first: the agent announces the task complete when it is not (tests still red, the feature half-built). The canonical reason to add a *verification gate*. See [Post 05](posts/05-agent-failure-modes/index.md).

**Workflow.** A system whose steps are laid out in advance by code: the path is fixed and the model fills in the blanks at each stop along it (Anthropic, 2024). The contrast that gives *agent* its meaning, and the right answer more often than it is chosen. See [Post 01](posts/01-from-context-to-harness/index.md).

**Worktree.** A separate working copy of a git repository that lets a parallel agent make edits in isolation, avoiding conflicts with other agents on the same repository. See [Post 17](posts/17-parallel-agents-shared-repo/index.md).
