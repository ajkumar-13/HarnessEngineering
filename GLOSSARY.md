# Glossary

Harness-specific terms used across the series, alphabetised, one or two lines each. This glossary **extends** the *Context Engineering* glossary rather than duplicating it — shared terms (attention, chunking, context window, context rot, MCP, prompt caching, RAG, sub-agent) are defined there and only re-scoped here where the harness lens differs.

---

**Agent.** A model plus everything around it that lets it *act*, not just respond — the model, the scaffold, and the harness operating together in a loop.

**Agent loop.** The core cycle a harness runs: call the model, parse its tool calls, execute them, feed the results back, repeat, until a stop condition fires. Also *control loop*.

**Blast radius.** The scope of damage a single agent action can cause if it goes wrong. Sandboxes and permissions exist to bound it.

**Control plane.** The org-level layer that governs many agents at once — permissions, budgets, audit, policy. The enterprise framing of harness engineering.

**Doom loop.** A failure mode where an agent repeats the same ineffective action without progress. Detected by *no-progress detection*; broken by a loop exit.

**Handoff artefact.** A structured file (spec, plan, state summary) that carries context from one agent, iteration, or session to the next — the mechanism that lets work survive a context reset.

**Harness.** Everything that is not the model: the loop, tools, state, sandbox, verification, hooks, permissions, orchestration, and observability. The runtime that drives the model.

**Harness engineering.** The discipline of designing that harness — deciding when the agent stops, how errors are handled, and what guardrails keep it on track — so it succeeds on real tasks.

**Harness-as-a-Service (HaaS).** A shift from LLM APIs that return completions to APIs that return a *runtime* with the loop, tools, context management, and hooks built in.

**Hook.** A deterministic script run at a lifecycle point (pre-tool, post-edit, pre-commit, session-start) to enforce a rule the model cannot be trusted to follow on its own.

**Human-in-the-loop (HITL).** A harness pattern where a human approves, interrupts, or steers the agent at defined points on the autonomy spectrum.

**Loop engineering.** The sub-discipline of designing the loop that drives an agent — especially its *layered exits* — instead of hand-writing each prompt. "Stop prompting; design the loop that prompts it for you."

**No-progress detection.** A stop condition that halts a loop when successive iterations stop changing anything, guarding against thrashing.

**Orchestration.** A layer *above* the harness that coordinates multiple agents as units. A harness drives one model; an orchestrator manages many agents.

**Planner / generator / evaluator.** A pattern that splits planning, doing, and grading across separate agents, because an independent evaluator does not skew positive the way self-grading does. Sometimes "GANs for prose."

**Progressive disclosure.** Loading a tool, skill, or piece of context only when the current task needs it, rather than at startup.

**Ralph loop.** The simplest long-horizon pattern (named by Geoffrey Huntley): feed the same prompt against a written spec, let the agent do one task and commit, reset to a fresh context, repeat until done.

**Ratchet principle.** "Every mistake becomes a rule." Each failure is converted into a durable constraint — a memory-file line, a hook, a reviewer check — so it cannot recur.

**ReAct.** Reason → Act → Observe: the interleaving of reasoning steps and tool actions that most agent loops implement.

**Sandbox.** An isolated execution environment (allow-listed commands, network isolation, ephemeral runtime) that bounds what an agent's tools can touch.

**Scaffold.** The behaviour-defining layer around the model: system prompt, tool descriptions, how responses are parsed, what is remembered across steps. Distinct from the *harness*, which is the execution mechanism.

**Sprint contract.** A "definition of done" negotiated between a generator and an evaluator before work begins, so completion is judged against agreed criteria.

**Stop condition.** Any rule that ends a loop: goal verified, max iterations, token/time budget exhausted, or no progress. Most agent bugs are stop-condition bugs.

**Tool-call offloading.** Writing a large tool output (e.g. a 2,000-line log) to disk and returning a pointer, so it does not consume the context window until the agent reads it.

**Trajectory eval.** Evaluating an agent on the *path* it took (steps, tool calls, outcome), not just a single final output. The eval lens harness engineering needs.

**Verification loop.** A per-step check (tests, self-critique) that surfaces errors immediately so they do not compound. "Success is silent; failures are verbose."

**Victory declaration.** A failure mode where an agent marks a task complete without verifying it. The canonical reason to add a verification loop.

**Worktree.** A separate working copy of a git repository that lets a parallel agent make edits in isolation, avoiding conflicts with other agents on the same repo.
