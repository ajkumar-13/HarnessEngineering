# Harness Engineering

Standard: 2.2.0 · Plan version: 1.0.0 · Status: draft · Date: 2026-10-03

Harness Engineering is a twenty-six post series on the machine built around a language model so that it can act autonomously and be trusted: the loop that drives the model, the tools it acts through, the state it keeps on disk, the verification that checks its work, the hooks that enforce rules deterministically, the sandboxes and approvals that bound its blast radius, the orchestration and long-horizon patterns that scale it, and the observability and evaluation that let its owner see and improve it. It is the sequel to the Context Engineering series: context engineering decides what one model call sees, harness engineering designs the runtime that makes the calls. The series is framework-agnostic, written in plain Python against provider SDKs, and ships eight offline-testable code companions culminating in three builds. A reader who finishes it can write a verified agent loop with layered exits from a blank file, harden it with hooks, a sandbox, an approval gate, and a sub-agent, run a task across many fresh contexts against a written spec, trace and A/B-evaluate the result, and say with evidence whether a failure is a harness problem or a model problem.

# 1. Purpose and authority

This plan owns the curriculum of the series: which posts exist, in which order, what each one promises, what it requires and recommends, what it covers, which figures and companions carry it, and which primary sources anchor it. Layout, identifiers, the sidecar schema, the body template, the question bank, diagrams, tooling, and workflow are owned by series-standard/STANDARD.md at the version `series.yaml` pins, not by this document. `series.yaml` is the machine form of this lock: its `parts[].posts` lists the reading order, its ids are allocated from `next_post_ordinal` and never reused, and a dropped id goes to `retired`. The validator's plan stage keeps the two in agreement. The pre-lock plan this document replaces is preserved at `audits/plan-pre-lock.md`; where the two disagree, this plan and the shipped posts are canonical.

# 2. Audience, entry, and exit levels

## Reader profiles

- The builder: an engineer shipping an agentic feature who has called a model with tools and watched the result run away, declare victory early, or loop. This reader needs the loop, the stop conditions, verification, and hooks, and is the one every post addresses first.
- The platform engineer: someone building the internal control plane that many agents will run inside, who needs permissions, sandboxes, observability, evaluation, and the economics of a loop at organisation scale (hrn-014, hrn-020 to hrn-023).
- The Context Engineering graduate: a reader who has finished the sibling series and wants the runtime machinery its final part previewed. This reader can skim hrn-001 and hrn-002 and start at hrn-003.

## Entry requirement

The series assumes the reader can call a provider API with a tool definition and read its response, write Python at the level of a small package with tests, and use git from the command line. It assumes the Context Engineering series as background and links to it for everything token-level (prompt caching, context rot, the write/select/compress/isolate strategies, memory content, output evals, token-level prompt injection), but every post is readable without it because each borrowed idea is restated in one paragraph at the point of use. No post assumes the mcp series, but hrn-007 recommends mcp-002 and mcp-011 for the protocol side of the boundary it describes from the host side.

## Exit levels

- After hrn-005 (end of Part I): the reader can name the eleven components of a harness, write the minimal reason-act-observe loop with its four exits, grade the evidence that the harness is a bigger lever than the model, and diagnose six agent failure modes from a trace.
- After hrn-010 (end of Part II): the reader can design and validate a tool schema, load capability on demand without destroying the prompt cache, keep state on disk and under git with a handoff file, choose between offload, clear, compact, and reset, and run a ratchet that turns each failure into a durable rule.
- After hrn-015 (end of Part III): the reader can gate the loop's final-answer exit on ground truth, split planner, generator, and evaluator with a sprint contract, write blocking and reporting hooks, bound a run with an allow-list sandbox and declarative permissions, and place approvals only where a checkpoint cannot undo the action.
- After hrn-020 (end of Part IV): the reader can choose a topology and defend staying single-agent, run a leaderless swarm on a shared repository with file claims and worktrees, drive a task across many fresh contexts with a Ralph loop, compose loops with layered exits and budgets, and settle build-versus-buy against an SDK by measurement.
- After hrn-023: the reader can instrument a run with OpenTelemetry spans, read a trace tree to the failing component, A/B two harness configurations on a fixed task set and tell signal from sampling noise, and price a run per successful task.
- After hrn-026 (advanced): the reader has assembled, hardened, and run the three builds and can extend the capstone along the seams it names.

## Gates

`series.yaml` declares no formal gates (`gates: []`). The de facto gates are the three builds: no reader should move past hrn-024 without the ten-test minimal harness passing offline, past hrn-025 without the fourteen-call adversarial table reproduced (nine calls reaching execution in Build #1, one in Build #2), or past hrn-026 without the eight-test capstone suite green and the A/B demo run.

# 3. Pedagogical rules

- One question per post. Each post answers the central question in its spec and nothing else; shared ground is cross-linked by post number, never re-taught.
- Mechanism before name. Every pattern is shown as a loop, a file, a gate, or a hook in code before the field's name for it is given, and every named failure mode is tied to the component that fixes it.
- Framework-agnostic. Code is plain Python over the official provider SDKs; an SDK or graph framework appears only in hrn-020, and only to compare shapes. No framework is the protagonist.
- Offline-testable companions. Every companion under `code/` has a mocked model, a `pytest` suite, and a one-command demo, so every claim about a harness can be checked without credentials; live runs are an opt-in `live.py`.
- Evidence graded, not asserted. Claims about harness-versus-model performance are ranked by strength (same model and benchmark, controlled scaffold comparison, reported multiples) and what the evidence does not show is stated.
- Every number comes from a run or a cited source. Costs, token counts, test counts, and line counts quoted in prose are produced by the committed companion or cited to the document that reports them, and the model-and-rate assumptions behind cost arithmetic are stated.
- Build order follows the component map. Parts II and III each add one component to the loop of hrn-003; the builds of Part V assemble them in the same order (loop, tools, verification, exits, then hooks, sandbox, approval, sub-agent, tracing, then long-horizon, roles, ratchet, cost).
- Context Engineering is cited, not repeated. Where a token-level detail is assumed, the post states it in one paragraph and points to the sibling post; the lens is always the runtime.
- Common pitfalls, Further reading, What to read next. Every post ends with the three blocks, and every forward reference is to a post by number within the series.

# 4. Curriculum lock

26 posts in 5 parts. Post numbers are permanent; a post inserted later takes the next ordinal from `series.yaml` and the directories after it renumber (STANDARD.md Section 2.2).

| Part | Title | Posts | Ids |
|---|---|---|---|
| I | Part I - Foundations | 01-05 | hrn-001 to hrn-005 |
| II | Part II - Core primitives | 06-10 | hrn-006 to hrn-010 |
| III | Part III - Control and reliability | 11-15 | hrn-011 to hrn-015 |
| IV | Part IV - Scale and orchestration | 16-20 | hrn-016 to hrn-020 |
| V | Part V - Production and builds | 21-26 | hrn-021 to hrn-026 |

Retired ids: none.

# 5. Per-post specifications

One specification per shipped post, in `series.yaml` order. The sidecars of this series carry no `level`, `prerequisites`, or `recommended` keys, so the level and the dependency graph below are the record of those facts until the migration commit adds them (Section 9). Titles are the sidecar titles with the number prefix removed, verbatim.

## Part I - Foundations

### hrn-001 - From context to harness — the third era

- **Meta:** Part I; beginner; core; proof none; code none.
- **Central question:** What is a harness, and why did the bottleneck of applied LLM work move from phrasing to information to autonomy and control?
- **Promise:** The reader can state `Agent = Model + Harness`, place prompt, context, and harness engineering on one timeline, explain why context engineering is a component inside the harness, use the vocabulary (model, scaffold, harness, orchestration) precisely, and say where the harness ends.
- **Coverage:** the three eras and their bottlenecks, "if you're not the model, you're the harness", the nested rings model to scaffold to harness to orchestration, the vocabulary pinned down, a first look at the evidence, what a harness gap costs in tokens, what the series covers and leaves out
- **Dependencies:** requires none; supports hrn-002, hrn-004.
- **Visuals:** hero `01-three-eras.svg` (2022 to 2026 across three eras, each working on a larger surface); `02-nested-rings.svg`; `03-equation.svg`.
- **Lab/gate:** Write the one-sentence bridge from the Context Engineering series in the reader's own words and classify five named products as model, scaffold, harness, or orchestration.
- **Anchors:** Trivedy 2026 (The Anatomy of an Agent Harness; the origin of the equation), Osmani 2026 (Agent Harness Engineering), OpenAI 2026 (Harness engineering with Codex), Anthropic 2024 (Building Effective Agents), Faros AI 2026, Hugging Face 2026 (harness and scaffold terms).

### hrn-002 - The anatomy of a harness

- **Meta:** Part I; beginner; core; proof none; code none.
- **Central question:** What are the parts of a production harness, and how does naming them turn "my agent is flaky" into a diagnosis?
- **Promise:** The reader can list the eleven components around the loop (four that feed the model, four that govern it, two at larger scale), say which are constitutive and which merely standard, read the map as a symptom-to-component lookup, and separate the prebuilt harness inherited from an SDK from the custom layer added on top.
- **Coverage:** why a map comes first, why eleven and what other taxonomies count, the loop as the core, constitutive against standard components, the feeding four, the governing four, the two at scale, the map as a diagnostic, prebuilt against custom, one mature harness decoded, how the series fills the map in
- **Dependencies:** requires hrn-001; supports hrn-003, hrn-020.
- **Visuals:** hero `01-harness-anatomy.svg` (eleven components with data flow around the loop); `02-layered-harness.svg`; `03-prebuilt-vs-custom.svg`.
- **Lab/gate:** Take one agent the reader has run, map a flaky behaviour it showed to a component on the map, and name which half (prebuilt or custom) owns the fix.
- **Anchors:** Osmani 2026, Trivedy 2026, de Macedo 2026 (necessary and sufficient conditions for a harness), Databricks 2026 (What is an AI Agent Harness), awesome-harness-engineering 2026.

### hrn-003 - The agent loop — ReAct, control loops, and stopping

- **Meta:** Part I; intermediate; core; proof none; code included.
- **Central question:** What does the minimal reason-act-observe loop look like on the wire, and why are most agent bugs stopping-condition bugs?
- **Promise:** The reader can write the minimal control loop over a provider API, pair `tool_use` and `tool_result` blocks correctly, act on every `stop_reason`, carry state between turns, implement the four layered exits (goal verified, iteration cap, token and time budget, no-progress detection) without false positives, and choose between streaming and batch turns.
- **Coverage:** a harness is a loop, the minimal control loop, one turn on the wire, how the API signals an exit, the stateless model and the remembering loop, what the loop carries, stopping as the hard part, sizing the cap and the budget, no-progress detection, streaming against batch, the ReAct origin
- **Dependencies:** requires hrn-002; supports hrn-004, hrn-005, hrn-006, hrn-008, hrn-011, hrn-019, hrn-021, hrn-023, hrn-024.
- **Visuals:** hero `01-agent-loop.svg` (reason, act, observe with the four exits annotated); `02-stateless-model.svg`; `03-batch-vs-streaming.svg`.
- **Lab/gate:** Run `code/03-agent-loop/` offline (`pytest -q`, seven tests) and make the mock model trigger each of the four exits in turn, reading the stop reason each time.
- **Anchors:** Yao et al. 2023 (ReAct), Anthropic 2024 (Building Effective Agents), Anthropic Messages API documentation (stop reasons, tool use), Faros AI 2026, awesome-harness-engineering 2026 (Agent Loop).

### hrn-004 - Why the harness beats the model — the evidence

- **Meta:** Part I; beginner; core; proof idea; code none.
- **Central question:** How strong is the evidence that the same model swings widely on harness design alone, and what does that evidence not show?
- **Promise:** The reader can state the founding claim carefully, rank the evidence by strength (a same-model harness-only move of 13.7 points on Terminal-Bench 2.0, a controlled scaffold comparison worth up to 28 points, a peer-reviewed interface-only result), name what the evidence does not show, explain the model-and-harness co-training flywheel, and run a three-run test that tells a harness problem from a model problem.
- **Coverage:** the claim stated carefully, the firm evidence (one model, one benchmark, seven harness changes), the controlled evidence, the softer evidence treated as reported, what the evidence does not show, the "skill issue" reframe, the co-training flywheel, telling a harness problem from a model problem in three runs, how to choose a model once the claim is accepted
- **Dependencies:** requires hrn-001; recommends hrn-003; supports hrn-022.
- **Visuals:** hero `01-harness-gap.svg` (same model, different harness, with citations); `02-cotraining-flywheel.svg`; `03-choose-model-order.svg`.
- **Lab/gate:** For one task the reader's agent fails, run the three-run diagnostic (same harness and model, bigger model, changed harness) and record which run moved the outcome.
- **Anchors:** Trivedy 2026 (Improving Deep Agents with harness engineering), Zhang et al. 2026 (Stop Comparing LLM Agents Without Disclosing the Harness), Starace 2026 (Scaffold Effects on GAIA), Yang et al. 2024 (SWE-agent), Guo et al. 2026 (survey on agent system and harness design), Terminal-Bench 2.0.

### hrn-005 - Agent failure modes — victory declaration, context anxiety, doom loops

- **Meta:** Part I; intermediate; core; proof none; code included.
- **Central question:** In which recurring, nameable ways do autonomous agents fail, and which harness component fixes each?
- **Promise:** The reader can recognise victory declaration, context anxiety, one-shotting, doom loops, silent drift, and destructive action from a trace, say what each costs and who pays, separate the confusable pairs, and use the triage table to decide what to build first.
- **Coverage:** "flaky" is not a diagnosis, the six modes, cost and who pays, where failures cluster in the loop, a harness that fixed three of them, detecting each mode from a trace with a per-turn fingerprint, differential diagnosis of the confusable pairs, the triage table, what is not on the list, naming as the first fix
- **Dependencies:** requires hrn-003; supports hrn-021.
- **Visuals:** hero `01-failure-modes-grid.svg` (six panels of symptom, cause, and harness fix); `02-where-failures-strike.svg`; `03-trace-signatures.svg`.
- **Lab/gate:** Run the trace-fingerprint snippet over an archive of the reader's own runs and count the hits per mode; confirm that victory declaration shows up only as a join between a COMPLETED stop and a failed downstream check.
- **Anchors:** Anthropic 2025 (Effective harnesses for long-running agents), Faros AI 2026, Osmani 2026, Morris 2026 (Humans and Agents in Software Engineering Loops, martinfowler.com), Breunig 2025 (How Long Contexts Fail).

## Part II - Core primitives

### hrn-006 - Tools as the agent's hands — bash, code, and schemas

- **Meta:** Part II; intermediate; core; proof none; code included.
- **Central question:** Why do a few general-purpose tools beat a zoo of bespoke ones, and what makes a tool call reliable?
- **Promise:** The reader can explain a tool call as a contract written in tokens, argue for bash and code execution as the universal tools and name when a bespoke tool still wins, design a schema that teaches the model when not to call, validate every call against its schema before executing, shape the return value, handle parallel tool calls, and curate the fewest tools that cover the space.
- **Coverage:** tools as the ACT step, what a tool call is on the wire, the general-purpose-tool argument, when a bespoke tool wins, one boundary is not a narrow boundary, schema design, validation as the contract, the return value as the other half, parallel tool calls, curating the tool set
- **Dependencies:** requires hrn-003; supports hrn-007, hrn-008, hrn-011, hrn-014, hrn-024.
- **Visuals:** hero `01-tool-dispatch.svg` (dispatch inside the loop); `02-universal-vs-zoo.svg`; `03-schema-that-teaches.svg`.
- **Lab/gate:** Run `code/06-tools-and-bash/` (fifteen tests) and add one deny-listed command and one schema violation to the registry tests, watching each be rejected before execution.
- **Anchors:** Anthropic tool-use and parallel tool-use documentation, Anthropic prompt caching documentation, OpenAI 2024 (Structured Outputs), Gan and Sun 2025 (RAG-MCP), Osmani 2026.

### hrn-007 - Skills & MCP in the runtime

- **Meta:** Part II; intermediate; core; proof none; code included.
- **Central question:** How does a harness give an agent dozens of capabilities without loading every schema into the window?
- **Promise:** The reader can describe skills as loadable procedures, measure the cost of an over-stuffed tool list, implement progressive disclosure through a skill registry, append discovered schemas rather than swap them so the prompt cache survives, dispatch an MCP call inside the ACT step, and keep results as well as schemas out of the window.
- **Coverage:** skills as loadable procedures, the cost of an over-stuffed tool list, progressive disclosure, when disclosure is worth building, a skill registry in code, append never swap, skill registries and distribution, MCP as a tool behind a process boundary, dispatching an MCP call inside the loop, keeping results out of the window, curating the catalogue
- **Dependencies:** requires hrn-006; recommends mcp-002, mcp-011; supports none.
- **Visuals:** hero `01-progressive-disclosure.svg` (tools appearing as tasks demand them); `02-mcp-dispatch.svg`; `03-three-distances.svg`.
- **Lab/gate:** Build the skill registry from the post, load two skills on demand, and show with token counts that the cached prefix is preserved when schemas are appended and destroyed when they are swapped.
- **Anchors:** Anthropic 2025 (Introducing Agent Skills; Equipping agents for the real world with Agent Skills), Anthropic tool search and programmatic tool calling documentation, Anthropic 2025 (Code execution with MCP), modelcontextprotocol.io specification, Invariant Labs 2025 (GitHub MCP vulnerability).

### hrn-008 - State & the filesystem — durable memory and git as state

- **Meta:** Part II; intermediate; core; proof none; code included.
- **Central question:** Where should an agent's state live when the window is volatile, expensive, and small relative to the work?
- **Promise:** The reader can use the filesystem as scratchpad and inter-step bus, quantify what moving state to disk saves, checkpoint after each verified step and roll back under git, write and read a structured handoff file that survives a context reset, confirm that a write landed, and choose between a flat file, a database, and an index.
- **Coverage:** the window is not where state lives, the filesystem as scratchpad and bus, what moving state to disk is worth, git as reversible state, what shipping harnesses checkpoint, handoff files, writing is not the same as having written, flat file against database against index, where state belongs
- **Dependencies:** requires hrn-003; recommends hrn-006; supports hrn-009, hrn-010, hrn-016, hrn-017, hrn-018.
- **Visuals:** hero `01-filesystem-durable-state.svg` (filesystem and git around the loop); `02-handoff-lifecycle.svg`; `03-where-state-belongs.svg`.
- **Lab/gate:** Write the handoff file from the post for a task in progress, kill the session, start a fresh one that reads only the handoff, and confirm it resumes at the right step and rolls back one bad commit.
- **Anchors:** Osmani 2026, Manus 2025 (Context Engineering for AI Agents), Anthropic 2025 (Effective context engineering for AI agents), Aider git integration documentation, Anthropic checkpointing documentation.

### hrn-009 - Context management inside the loop — compaction, offloading, resets

- **Meta:** Part II; intermediate; core; proof none; code included.
- **Central question:** How does a long-running harness keep its own window from rotting while the loop runs?
- **Promise:** The reader can tell context rot from a healthy long run, apply the ladder offload (lossless), clear (nearly lossless), compact (lossy), and reset (total), price each rung against the prompt cache, keep bytes out of the stable prefix, and choose the cheapest rung that works.
- **Coverage:** context rot while the loop runs, reading the window, offload, clear, compact, reset behind a handoff, what each move costs the prompt cache, prevention by keeping bytes out of the prefix, choosing between them
- **Dependencies:** requires hrn-008; supports hrn-010, hrn-018, hrn-023.
- **Visuals:** hero `01-window-timeline.svg` (a window filling, with a compaction and an offload event); `02-three-moves.svg`; `03-escalation-ladder.svg`.
- **Lab/gate:** Run the offloader and the rolling compactor from the post on a captured transcript and record tokens before and after each rung together with the cache hit rate on the next turn.
- **Anchors:** Hong, Troynikov and Huber 2025 (Context Rot), Anthropic context editing and compaction documentation, Anthropic 2025 (Managing context on the Claude Developer Platform), Anthropic 2025 (Effective harnesses for long-running agents).

### hrn-010 - Continual learning & the ratchet — every mistake becomes a rule

- **Meta:** Part II; intermediate; core; proof none; code included.
- **Central question:** How does a harness get better over time when the model cannot learn between sessions?
- **Promise:** The reader can keep a memory file that is read every session and earns each line, run the ratchet that turns one failure into a memory line, a hook, and a reviewer check, decide which teeth a failure earns, promote an observation to a rule, prune clutter, and watch a rule after it lands.
- **Coverage:** stateless model and learning harness, the memory file, earn each line, one failure three constraints, which teeth a failure earns, promotion from observation to rule, a ratchet only climbs if the steps are real, why reliability only climbs, when memory becomes clutter, watching a rule after it lands
- **Dependencies:** requires hrn-008; recommends hrn-009; supports hrn-013, hrn-026.
- **Visuals:** hero `01-ratchet-mechanism.svg` (a failure becoming three durable constraints); `02-ratchet-over-time.svg`; `03-life-of-a-rule.svg`.
- **Lab/gate:** Take one real failure from the reader's agent, write its memory line, its hook, and its check, then run the `Ratchet` from `code/26-coding-agent/` and show the fix landing only after the rule exists.
- **Anchors:** Osmani 2026 (the ratchet principle), Agentic AI Foundation 2026 (AGENTS.md), Anthropic prompt caching documentation and price list, awesome-harness-engineering 2026 (Memory and State).

## Part III - Control and reliability

### hrn-011 - Verification loops — tests, self-critique, fail-fast

- **Meta:** Part III; intermediate; core; proof idea; code included.
- **Central question:** What makes autonomy safe enough to run unattended, and why is the model's own judgement not it?
- **Promise:** The reader can gate the loop's final-answer exit on ground truth, explain why per-step verification beats verifying at the end, say why self-critique skews positive, hand a failing check back so that success is silent and failure is verbose, price an unverified run, handle flaky and gameable verifiers, and decide which tasks admit a verifier at all.
- **Coverage:** fail-fast against fail-at-the-end, tests as ground truth, self-critique and its limits, feeding failures back, the economics of an unverified run, flaky and slow verifiers, the verifier can be gamed, which tasks admit a verifier, where the gate belongs
- **Dependencies:** requires hrn-003; recommends hrn-006; supports hrn-012, hrn-013, hrn-015, hrn-016, hrn-019, hrn-022, hrn-024.
- **Visuals:** hero `01-verification-gate.svg` (the loop with a gate on the final-answer exit); `02-compounding-vs-failfast.svg`; `03-verifier-ladder.svg`.
- **Lab/gate:** Run `code/11-verification-loop/` (nine tests), inject a failing test, and watch the loop retry to green; then remove the gate and measure the wasted iterations on the same task.
- **Anchors:** Faros AI 2026, Osmani 2026, Huang et al. 2024 (LLMs cannot self-correct reasoning yet), Kamoi et al. 2024, Madaan et al. 2023 (Self-Refine), Shinn et al. 2023 (Reflexion), Panickssery, Bowman and Feng 2024, Sharma et al. 2023 (sycophancy).

### hrn-012 - Planner / generator / evaluator — separating the roles

- **Meta:** Part III; intermediate; core; proof none; code included.
- **Central question:** Why does an independent evaluator beat a self-grading agent, and what does the split cost?
- **Promise:** The reader can separate the author of a piece of work from its grader, write a sprint contract that fixes "done" before generation starts and routes each criterion to the cheapest verifier, design against the evaluator's own biases and give it tools, notice that nothing checks the planner, and price three roles against one agent.
- **Coverage:** why self-evaluation is biased, the three roles, sprint contracts, handoffs between roles, how big a chunk is, the evaluator is not an oracle, an evaluator that gathers its own evidence, nobody is checking the planner, the cost of the extra roles, when a single agent is enough
- **Dependencies:** requires hrn-011; supports hrn-016, hrn-018, hrn-026.
- **Visuals:** hero `01-pge-triangle.svg` (three roles, what each reads, writes, and never sees, with the measured cost table); `02-sprint-contract.svg`; `03-the-unchecked-edge.svg`.
- **Lab/gate:** Write a sprint contract for one small feature, run the three-role loop from the post with an evaluator that has no write tools, and record the PASS or NEEDS_WORK verdicts and the cost multiple against a single agent.
- **Anchors:** Anthropic 2026 (Harness design for long-running application development; cwc-long-running-agents), Anthropic 2025 (Effective harnesses for long-running agents), Osmani 2026, Zheng et al. 2023 (Judging LLM-as-a-Judge).

### hrn-013 - Hooks & deterministic enforcement — guardrails as code

- **Meta:** Part III; intermediate; core; proof none; code included.
- **Central question:** Which rules are too important to leave to the model, and how does a hook enforce them every time?
- **Promise:** The reader can name the four lifecycle points (session start, pre-tool, post-edit, pre-commit) and say which two can block, write a gate and a report hook with the exit-code contract, choose what to enforce deterministically, see hooks as the enforcement half of the ratchet, keep them fast and quiet, and test the guard including its escape hatch.
- **Coverage:** the limits of asking nicely, the four lifecycle points and which can stop you, the shape of a hook, what to enforce deterministically, hooks as the enforcement half of the ratchet, keeping hooks fast and quiet, the escape hatch and testing the guard
- **Dependencies:** requires hrn-011; recommends hrn-010; supports hrn-014, hrn-015, hrn-020, hrn-021, hrn-025.
- **Visuals:** hero `01-hook-lifecycle.svg` (four points around the loop); `02-blocked-command.svg`; `03-gates-and-reports.svg`.
- **Lab/gate:** Run `code/13-hooks/` (nine tests), add a deny rule for one destructive command and a post-edit test runner, and show the command blocked before execution while the test failure is only reported.
- **Anchors:** Osmani 2026, Anthropic Claude Code hooks documentation, NIOSH 2024 (Hierarchy of Controls), Git githooks and git-push documentation, awesome-harness-engineering 2026.

### hrn-014 - Permissions, sandboxes & security — the AI control plane

- **Meta:** Part III; intermediate; core; proof none; code included.
- **Central question:** How does a harness bound the attack surface and the blast radius of an agent with real tools?
- **Promise:** The reader can wrap the bash tool in an allow-list sandbox with a timeout and a working-directory jail that is actually enforced at execution, declare permissions instead of prompting for them, reason about blast radius, defend a tool-using agent against indirect prompt injection in layers, make every gate observable, and fill in a threat-model template for a harness.
- **Coverage:** isolated execution, permissions beyond prompts, blast-radius thinking, prompt injection reaching a tool-using agent, a gate you cannot see fire, the AI control plane, a threat-model template
- **Dependencies:** requires hrn-013; recommends hrn-006, mcp-019, sec-018, sec-022; supports hrn-025.
- **Visuals:** hero `01-sandbox-boundary.svg` (what a run can and cannot touch); `02-injection-defence.svg`; `03-which-gate-fired.svg`.
- **Lab/gate:** Run the sandbox wrapper against the post's escape attempts (sibling-directory paths, an allow-listed interpreter, a relative path) and confirm which are blocked, which are allowed, and that each decision is logged.
- **Anchors:** Databricks 2026, Willison 2025 (The lethal trifecta), OWASP 2025 (Top 10 for LLM Applications; MCP Top 10), Invariant Labs 2025 (GitHub MCP exploited; tool poisoning), Beurer-Kellner et al. 2025, Debenedetti et al. 2025 (CaMeL), Anthropic and OpenAI sandbox documentation, GTFOBins.

### hrn-015 - Human-in-the-loop — approvals, interventions, async feedback

- **Meta:** Part III; intermediate; core; proof none; code included.
- **Central question:** Where on the autonomy spectrum does each action belong, and how does a human enter the loop without becoming its bottleneck?
- **Promise:** The reader can place actions on the autonomy spectrum, reserve approval for what a checkpoint cannot undo, separate the policy from the decider, handle yes, no, and the answers in between, interrupt and steer a run in flight, make feedback asynchronous, define what happens when nobody answers, write escalation triggers, and design against reviewer fatigue.
- **Coverage:** the autonomy spectrum, what earns a gate, the policy and the decider, the answers in between, a decider that is not a person, interruption and steering, asynchronous feedback and what the reviewer sees, when nobody answers, escalation triggers, reviewer trust and fatigue
- **Dependencies:** requires hrn-013; recommends hrn-011; supports hrn-025.
- **Visuals:** hero `01-autonomy-spectrum.svg`; `02-approval-gate.svg` (a gate with an asynchronous reply); `03-anatomy-of-a-gate.svg`.
- **Lab/gate:** Run the approval primitive from `code/25-harness-plus/` on a flagged call, answer it asynchronously, and let one call time out to confirm the when-nobody-answers policy fires.
- **Anchors:** Morris 2026 (Humans and Agents in Software Engineering Loops), Feng, McDonald and Zhang 2025 (Levels of Autonomy for AI Agents), Anthropic 2026 (auto mode in Claude Code; How we built Claude Code auto mode), Anthropic Claude Agent SDK permissions documentation, Faros AI 2026.

## Part IV - Scale and orchestration

### hrn-016 - Multi-agent orchestration — topologies, and when not to

- **Meta:** Part IV; intermediate; core; proof none; code included.
- **Central question:** When does coordinating agents as units pay for its coordination tax, and when should one agent with sub-tasks stay single?
- **Promise:** The reader can separate harness from orchestrator, name the four topologies and who writes the control flow in each, steelman the single-agent default, distinguish cheap read fan-out from expensive write fan-out, price the coordination tax, use shared files as the inter-agent bus, choose a partial-failure policy before fanning out, and apply the decision framework.
- **Coverage:** harness against orchestrator, four topologies, the steelman for staying single, read fan-out against write fan-out, when multi-agent pays, what the coordination tax costs, shared files as the bus, the partial-failure policy, a decision framework
- **Dependencies:** requires hrn-008; recommends hrn-011, hrn-012; supports hrn-017, hrn-020, hrn-025.
- **Visuals:** hero `01-topologies-gallery.svg` (single, orchestrator-worker, pipeline, swarm); `02-orchestration-decision.svg`; `03-the-coordination-tax.svg`.
- **Lab/gate:** Run the minimal orchestrator-worker example on a read fan-out task and a write fan-out task and record tokens and wall-clock against the single-agent run of each.
- **Anchors:** Anthropic 2024 (Building Effective Agents), Anthropic 2025 (How we built our multi-agent research system), Cognition 2025 (Don't Build Multi-Agents), Yan 2026 (Multi-Agents: What's Actually Working), awesome-harness-engineering 2026.

### hrn-017 - Parallel agents on a shared repo — worktrees and task-claiming

- **Meta:** Part IV; advanced; core; proof none; code included.
- **Central question:** How do many agents work one codebase in parallel with no central orchestrator and no double-claimed task?
- **Promise:** The reader can implement task-claiming by exclusive file creation and confirm the claim took, add leases, reclaim, and quarantine, isolate each agent's edits in a git worktree, choose the isolation boundary, handle merges and conflicts, trade throughput against coordination cost, and design for at-least-once execution.
- **Coverage:** the shared-repo pattern, task-claiming via files, the same primitive at two layers, leases, reclaim and quarantine, worktrees for edit isolation, choosing the isolation boundary, merge and conflict handling, throughput against coordination cost, at-least-once not exactly-once, failure isolation across the swarm
- **Dependencies:** requires hrn-016; recommends hrn-008; supports none.
- **Visuals:** hero `01-shared-repo-swarm.svg` (agents claiming tasks through the repository); `02-worktree-isolation.svg`; `03-at-least-once.svg`.
- **Lab/gate:** Run `code/17-parallel-agents/` (nine tests, including the barrier-synchronised threaded claim test) and reproduce zero double claims over eight threads and four hundred tasks.
- **Anchors:** Carlini 2026 (Building a C compiler with a team of parallel Claudes), Anthropic 2025 (Effective harnesses for long-running agents), Gray and Cheriton 1989 (Leases), Kleppmann 2016 (How to do distributed locking), Bernstein c. 1995 (maildir).

### hrn-018 - Long-horizon & multi-context execution — Ralph loops and context bridging

- **Meta:** Part IV; advanced; core; proof none; code included.
- **Central question:** How does a harness finish a task that is bigger than any single context window?
- **Promise:** The reader can run a Ralph loop (fresh context, written spec, one task, commit, repeat), size one task against the re-entry tax, keep the reset cheap with a frozen prefix, bridge contexts with the spec and a handoff, decide who may write to the spec, design a multi-context build, enforce convergence and stopping with guards, and plan the review of fifty commits.
- **Coverage:** work that outgrows one window, the Ralph loop, sizing one task and the re-entry tax, the frozen prefix and the cache clock, the spec and the handoff, who may write to the spec, a reference design for a multi-context build, convergence, stopping and the guards, who reviews fifty commits, the overlap with planner and evaluator
- **Dependencies:** requires hrn-009; recommends hrn-008, hrn-012; supports hrn-019, hrn-023, hrn-026.
- **Visuals:** hero `01-ralph-loop.svg` (reset to a fresh context against the spec); `02-multi-context-timeline.svg`; `03-inside-one-iteration.svg`.
- **Lab/gate:** Run the Ralph-style driver from the post on a three-task spec with a mock model, confirm one commit per iteration, and make the acceptance gate rather than the agent's report decide convergence.
- **Anchors:** Huntley 2025 (Ralph Wiggum as a software engineer), Anthropic 2025 (Effective harnesses for long-running agents), Osmani 2026 (Long-running Agents), Kwa et al. 2025 (METR, long software tasks), Anthropic prompt caching documentation.

### hrn-019 - Loop engineering — designing the loop that prompts the agent

- **Meta:** Part IV; intermediate; core; proof none; code included.
- **Central question:** What does a well-engineered loop carry that a bare `while not done` does not?
- **Promise:** The reader can implement the four layered exits over the loop of hrn-003, reserve budget before spending it, choose what to compare for no-progress detection, treat a failed call as a retry rather than an exit, compose an inner verify loop inside an outer task loop, hand off cleanly after a guard exit, and put a hard ceiling on runaway spend.
- **Coverage:** stop prompting and design the loop, layered exits, loop engineering against a bare while-loop, reserve before you spend, what you compare decides what you detect, a failed call is not an exit, composing loops, a guard exit is a handoff, guardrails against runaway spend
- **Dependencies:** requires hrn-003; recommends hrn-011, hrn-018; supports hrn-024.
- **Visuals:** hero `01-layered-exits.svg` (the loop with all four exits); `02-nested-loops.svg`; `03-after-a-guard-exit.svg`.
- **Lab/gate:** Wrap the hrn-003 loop in the budget-and-progress controller from the post and show a guard exit writing a handoff that a second run resumes from.
- **Anchors:** Osmani 2026 (Loop engineering), tosea.ai 2026, Greyling 2026, Anthropic 2024 (Building Effective Agents), TechCrunch 2026 (Uber caps employee AI spending).

### hrn-020 - The SDK & framework landscape — Agent SDK, LangGraph, and peers

- **Meta:** Part IV; intermediate; core; proof none; code included.
- **Central question:** What does an agent SDK give you and take away, and how do you settle build-versus-buy by measurement?
- **Promise:** The reader can list what an SDK ships as a prebuilt harness, sort the options into four shapes along two axes, read the shape of the code in a batteries-included SDK against a graph framework, name what each takes away, pick the shape for a given situation, measure rather than argue the decision, keep the portable half portable, and place Harness-as-a-Service beside MCP.
- **Coverage:** what an SDK provides, four shapes and two axes, what each ships, the shape of the code, what an SDK takes away, which shape you are in, settle it by measuring, portability and lock-in, Harness-as-a-Service and the layer beside MCP
- **Dependencies:** requires hrn-002; recommends hrn-013, hrn-016; supports none.
- **Visuals:** hero `01-sdk-feature-matrix.svg`; `02-build-vs-buy.svg`; `03-harness-ab.svg` (the small A/B that does not settle the choice in an afternoon).
- **Lab/gate:** Implement the same tiny task against a batteries-included SDK and a graph framework with one shared tool function, and run the hrn-022 A/B runner over both on a fixed task set.
- **Anchors:** Anthropic Claude Agent SDK documentation (including permissions), OpenAI 2026 (Harness engineering with Codex; Codex as a platform), OpenAI Agents SDK documentation, LangGraph documentation, awesome-harness-engineering 2026.

## Part V - Production and builds

### hrn-021 - Observability & trace-driven repair — seeing what the harness did

- **Meta:** Part V; intermediate; core; proof none; code included.
- **Central question:** How do you find which component failed, on which step, and why, in a run of dozens of model and tool calls?
- **Promise:** The reader can define the span a harness must emit, record the stop reason and every gate outcome, read the geometry of a trace tree, localise a failure to a component, carry trace context across processes, replay a run against a diverging harness, decide sampling and retention, let an agent read its own traces, and stand up a minimal OpenTelemetry stack.
- **Coverage:** why a harness is opaque by default, the span, the stop reason and the gate outcomes, the trace tree for one run, reading a trace to localise a failure, trace context across processes, replays and regression detection, sampling, retention and access, agents that read their own traces, a do-it-yourself stack
- **Dependencies:** requires hrn-003; recommends hrn-005, hrn-013; supports hrn-022, hrn-025, hrn-026.
- **Visuals:** hero `01-trace-tree.svg` (nested spans for one run); `02-trace-to-ratchet.svg`; `03-trace-shapes.svg`.
- **Lab/gate:** Instrument the hrn-003 loop with the OpenTelemetry wrapper from the post, run it to each of the four exits, and read each stop reason and gate outcome back out of the exported spans.
- **Anchors:** OpenTelemetry 2025 (Semantic conventions for generative AI systems), OpenTelemetry 2026 (Inside the LLM call), W3C 2021 (Trace Context), Langfuse documentation, Arize Phoenix documentation, Osmani 2026.

### hrn-022 - Evaluating harnesses — Terminal-Bench, SWE-bench, harness A/B

- **Meta:** Part V; advanced; core; proof idea; code included.
- **Central question:** How is harness quality measured on whole trajectories and outcomes, and how do you tell a real improvement from sampling noise?
- **Promise:** The reader can contrast output evals with trajectory and outcome evals, describe Terminal-Bench, SWE-bench and their successors and the grading contract behind each, choose between `pass@1`, `pass@k`, and `pass^k`, build an internal eval harness and validate its grader first, size the task set and schedule runs, A/B a harness change with the model held fixed and compute paired differences with error bars, read the trajectory as well as the outcome, run the staged production funnel, and guard against benchmark overfit.
- **Coverage:** output against trajectory and outcome evals, the agentic benchmarks, the pass family, an internal eval harness, validating the grader, sizing and scheduling, A/B-testing a harness change, knowing when a difference is real, reading the trajectory, the production funnel, benchmark overfit
- **Dependencies:** requires hrn-011; recommends hrn-004, hrn-021; supports hrn-026.
- **Visuals:** hero `01-output-vs-trajectory.svg`; `02-harness-ab-pipeline.svg` (a larger task set worked to $p = 0.39$ and not called); `03-production-funnel.svg`.
- **Lab/gate:** Run the A/B runner from the post over two harness configurations on one fixed task set with several seeds, compute the paired difference and its interval, and state whether the result is callable.
- **Anchors:** Jimenez et al. 2024 (SWE-bench), OpenAI 2024 (SWE-bench Verified) and 2026 (why it no longer measures frontier capability), Deng et al. 2025 (SWE-Bench Pro), Yu et al. 2025 (UTBoost), Yao et al. 2024 (tau-bench), Miller 2024 (Adding Error Bars to Evals), Terminal-Bench documentation, Yang et al. 2024 (SWE-agent), Faros AI 2026, Strathern 1997.

### hrn-023 - The economics of a harness & Harness-as-a-Service

- **Meta:** Part V; intermediate; core; proof idea; code included.
- **Central question:** What decides whether an agent ships, cost per run or cost per successful run, and which two levers move it?
- **Promise:** The reader can write the cost of a loop as iterations times a growing context, set a latency budget, use budget ceilings as guardrails, place a rolling cache breakpoint so the bill grows nearly linearly rather than quadratically, price one run three ways, find where the money goes, compute cost per successful run, compare LLM APIs with Harness-as-a-Service products, reason about build-versus-rent, and meter a run that can be billed.
- **Coverage:** the cost of a loop, the latency budget, budget ceilings as guardrails, prompt caching across iterations, one run priced three ways, where the money goes and the levers, cost per run is the wrong number, Harness-as-a-Service, build-versus-rent, metering a run
- **Dependencies:** requires hrn-003; recommends hrn-009, hrn-018; supports hrn-026.
- **Visuals:** hero `01-loop-cost.svg` (quadratic against nearly linear with a rolling breakpoint); `02-llm-api-vs-haas.svg`; `03-build-vs-rent.svg`.
- **Lab/gate:** Run the per-run cost and latency meter from the post over one captured run, re-derive the arithmetic at current published rates, and compute cost per successful run for a ten-run set.
- **Anchors:** Osmani 2026, Anthropic prompt caching and pricing documentation, AWS 2026 (Bedrock AgentCore pricing), Kumar Dash 2026 (Composio, cost per successful task), Databricks 2026, Faros AI 2026.

### hrn-024 - Build #1 — a minimal agent harness from scratch

- **Meta:** Part V; intermediate; core; proof none; code required.
- **Central question:** What is the smallest real harness, and what does assembling it from the four primitives teach?
- **Promise:** The reader can assemble a loop, a schema-validated tool registry, a verification gate, and layered stop conditions into about five hundred lines, run it on a real task offline and live, read what the ten-test suite pins down and what it cannot see, and name what was left out and why.
- **Coverage:** the spec, the layout, the loop, the bash and file tools, the verification gate, layered stop conditions, running it on a real task, what the tests pin down, making it live, what was left out, the lesson the build teaches
- **Dependencies:** requires hrn-003, hrn-006, hrn-011, hrn-019; supports hrn-025.
- **Visuals:** hero `01-minimal-architecture.svg` (loop, registry, gate, exits); `02-task-run-sequence.svg`; `03-the-four-seams.svg`.
- **Lab/gate:** Run `code/24-minimal-harness/` (`pytest -q`, ten tests, no API key), then set a small token budget and confirm the budget check fires before the final-answer branch, so the overrun is at most one iteration.
- **Anchors:** hrn-003, hrn-006, hrn-011, hrn-019; Anthropic 2024 (Building Effective Agents), Trivedy 2026, Osmani 2026, Databricks 2026.

### hrn-025 - Build #2 — add hooks, sandbox, and sub-agents

- **Meta:** Part V; advanced; core; proof none; code required.
- **Central question:** What does hardening the minimal harness into something you would trust add, and what does each layer stop?
- **Promise:** The reader can add deterministic hooks, an allow-list sandbox with an enforced jail, a human approval gate, and one sub-agent to Build #1, wrap them in tracing, score the result against fourteen adversarial calls, read the thirteen tests and what they did not catch, and name what Build #2 still leaves out.
- **Coverage:** the spec, the layout, hooks, the sandbox, approval, one sub-agent, observability wiring, before and after on a scored task set, the tests, what the tests did not catch, what Build #2 leaves out, taking it live, what the build teaches
- **Dependencies:** requires hrn-024, hrn-013, hrn-014, hrn-015, hrn-016; recommends hrn-021; supports hrn-026.
- **Visuals:** hero `01-layered-harness.svg` (Build #1 with four layers added); `02-blast-radius.svg`; `03-what-tests-miss.svg`.
- **Lab/gate:** Run `code/25-harness-plus/` (thirteen tests) and reproduce the adversarial table: nine of fourteen calls reach execution under Build #1 and one under Build #2, and identify the one that gets through.
- **Anchors:** hrn-013, hrn-014, hrn-015, hrn-016, hrn-021; Anthropic Claude Code hooks documentation, Willison 2023 to 2026 (prompt injection), OWASP 2025, GTFOBins, Cognition 2025.

### hrn-026 - Capstone — a long-running, trusted coding-agent harness

- **Meta:** Part V; advanced; core; proof none; code required.
- **Central question:** How do the components of the series assemble into one coding agent that runs across many contexts, verifies itself, learns, meters its cost, and records everything?
- **Promise:** The reader can run the capstone's long-horizon driver with planner, generator, and evaluator roles, the ratchet, cost guardrails, and tracing from a spec to completion, read the eight-test suite, name every seam the architecture leaves open and where it wires in, describe the deployment shape, and decide what to ship next.
- **Coverage:** the product spec, the layout, the long-horizon driver, planner, generator and evaluator, the guards and the seam where they belong, memory and the ratchet, observability and harness A/B, cost guardrails, the tests, the deployment shape, what to ship next, what the build teaches and what it cannot do
- **Dependencies:** requires hrn-025, hrn-010, hrn-012, hrn-018; recommends hrn-021, hrn-022, hrn-023; supports none.
- **Visuals:** hero `01-capstone-architecture.svg` (the whole series in one machine); `02-multi-context-run.svg`; `03-eval-observability-loop.svg`.
- **Lab/gate:** Run `code/26-coding-agent/` (eight tests, 429 lines across seven modules, no credentials), run the two-task spec demo to completion across fresh contexts, and run the A/B demo with the model held fixed.
- **Anchors:** Anthropic 2025 (Effective harnesses for long-running agents), OpenAI 2026 (Harness engineering with Codex), Trivedy 2026 (both articles), Huntley 2025, Anthropic prompt caching documentation; hrn-010, hrn-012, hrn-018, hrn-019, hrn-021 to hrn-025.

# 6. Series-specific contracts

## Notation and claim standards

- No mathematics beyond cost arithmetic; the only symbols are token counts, rates, and probabilities in `$...$`. The sidecars carry no `math` key and `vocab.math` is unused.
- Component names are fixed by hrn-002 and used identically everywhere: loop, tools, state, context management, memory, verification, hooks, permissions, orchestration, long-horizon patterns, observability. Failure modes are the six of hrn-005; the four exits are those of hrn-003.
- Performance claims are graded as in hrn-004 (firm, controlled, reported) and a reported multiple is never promoted to a measured one. Quotations are verbatim and attributed to the person who wrote them (the 2026-09-04 audit corrected three attributions; `REFERENCES.md` is the record).
- Inline citations are parenthetical author and year; `REFERENCES.md` holds the full entry for every citation in every post.

## Code companions

- There is no shared library (`library: null`). Eight standalone companions live under `code/` (`03-agent-loop`, `06-tools-and-bash`, `11-verification-loop`, `13-hooks`, `17-parallel-agents`, `24-minimal-harness`, `25-harness-plus`, `26-coding-agent`), each with `README.md`, `pyproject.toml`, `src/`, and `tests/`.
- Every companion runs offline against a mock model; the full suite (eighty tests) passes with no API key and no network. A live run is an explicit `live.py` and is never required by a post.
- Every security invariant a post states about its companion has a test that exercises it the way an attacker would (threads for the claim protocol, path escapes for the jail, interpreter commands for the allow-list), after the 2026-09-04 audit found three companions whose suites were structurally unable to see the bug the post warned about.
- Line and test counts quoted in a post are those of the committed companion at the time of writing and are updated when the companion changes.

## Compute and cost

- `vocab.compute` is unused; no post needs more than a laptop. Cost arithmetic in hrn-010, hrn-018, hrn-023, and hrn-026 names the model tier and published rate it uses and tells the reader to re-derive against current rates.

## Diagrams and animations

- Three figures per post, drawn with the shared roughjs generator under `assets/diagrams/excalidraw-generator/` and the Context Engineering design tokens unchanged (`--ce-*` prefix included; deliberate). Each figure ships light and dark variants, a caption, and alt text that describes the mechanism.
- Hero vocabulary is reused across posts by citation rather than by file: the loop is drawn in full in hrn-003 and compressed to a card elsewhere; the anatomy likewise from hrn-002.
- Two animated SVGs under `assets/animations/` (the loop turning; a reset with handoff) animate opacity only under `prefers-reduced-motion: no-preference` over a still that is the complete diagram.

## Series-specific checks

- `tools/audit.py` gates structure, sidecar fields, relative links, the em-dash cap, and the SVG contract (both variants, alt text, caption) and must stay green; the family validator is added beside it at migration (Section 10).

# 7. Sibling handoffs and deliberate omissions

## Assumed from context-engineering (not yet locked; prose only)

- The sibling series is the stated background of every post. Token-level ground is cited by post number and not re-taught: prompt caching and the stable prefix and the economics of a single call (its Post 05), context rot and the context failure modes (Post 06), write, select, compress, and isolate (Posts 07 to 13), the system prompt as software (Post 14), tools and MCP from the token side (Post 15), memory content (Post 16), output evals (Post 20), observability of a single call (Post 22), prompt injection at the token level (Post 23), and its Part V agentic workflow and builds (Posts 26 to 30), of which this series is the full treatment.
- When context-engineering locks, hrn-001, hrn-003, hrn-005, hrn-009, hrn-010, hrn-011, hrn-014, hrn-021, hrn-022, and hrn-023 gain `recommends` entries for the posts above; until then the handoff lives here.

## Assumed from mcp (locked)

- The protocol itself: architecture (mcp-002), the wire protocol and transports (mcp-003, mcp-004), server construction (mcp-005 to mcp-009), the host's tool loop and permissions (mcp-011), security the protocol does not stop (mcp-019), and authorization (mcp-020). hrn-007 views the boundary from the host side only and recommends mcp-002 and mcp-011; hrn-014 recommends mcp-019 for the protocol-side threat model.

## Shared with ai-security (sec ids locked in parallel)

- Prompt injection against tool-using agents, confused deputies, sandboxing as capability-based design, and multi-agent and MCP server trust are owned by ai-security (sec-018, sec-021, sec-022, sec-023). hrn-014 and hrn-025 implement the runtime controls (deny-list hook, allow-list sandbox, approval gate, defence in depth) and recommend sec-018 and sec-022 for the attacker's view and the measured evaluation of defences.

## Left to siblings

- evaluation-engineering: eval design, grader validation, and statistics in general; hrn-022 covers only trajectory and outcome evals of harnesses and the A/B of a harness change.
- learn-dspy and other framework-specific series: programming models that compile prompts; hrn-020 names the shape only.
- transformer, reasoning: what the model does inside a call, including reasoning-model behaviour; this series treats the model as fixed.

## Deliberate omissions

- Failure and recovery mechanics (retries with backoff and jitter, rate limits, circuit breakers, dead-letter queues, durable execution): considered as a new post in the 2026-09-04 audit and folded into hrn-017, hrn-018, and hrn-019 instead; no new id.
- Model routing, escalation, and fallback as harness parameters: left to context-engineering (its Posts 04 and 05).
- Running a harness as a service (triggers, workers, sessions, tenancy): one tier above the declared boundary; hrn-017 is the queue-and-worker post and hrn-023 names Harness-as-a-Service without building one.
- A production MCP server: built in context-engineering's Build #2 and in the mcp series; hrn-007 only dispatches a call.

# 8. Projects

None. `series.yaml` lists no projects and `next_project_ordinal` is 1. The three builds (hrn-024 to hrn-026) are posts with companions, not projects: they ship no deployed service, no users, and no evaluation record under `projects/`. A candidate first project is the capstone's coding agent taken live against a real repository with the seams hrn-026 names closed; it would take id hrn-p01 with `after_post: hrn-026` and `uses` hrn-010, hrn-012, hrn-013, hrn-014, hrn-018, hrn-019, hrn-021, hrn-022, hrn-023. It is not committed by this plan.

# 9. Risks and decisions

## Risk register

- Source volatility. Nearly every anchor is a 2025 or 2026 blog post, vendor document, or preprint, and several numbers (Terminal-Bench scores, catch rates, prices) will move. Mitigation: every figure is dated and attributed in the post and in `REFERENCES.md`; the plan anchors name the document, not the number.
- Vendor documentation drift. hrn-009, hrn-013, hrn-015, and hrn-020 describe specific provider features (context editing parameters, hook events, permission resolution order). Mitigation: each is cited to the dated documentation and the post states the mechanism, not just the parameter name.
- Companion rot. Eight companions pin provider SDKs; a breaking SDK release breaks `live.py` while the offline suites stay green. Mitigation: the offline core is the contract; live scripts are opt-in.
- The sidecar lacks level and prerequisites. Until the migration commit adds them, this plan is the only record of the dependency graph, and the validator cannot cross-check it against the posts. Mitigation: Section 5 and `series.yaml` carry the graph; the migration adds the keys verbatim from this plan.
- Two sibling locks pending. context-engineering is unlocked and ai-security's ids are being locked in parallel; if a sec id cited here changes, the recommends in hrn-014 must follow. Mitigation: only ids the ai-security plan names by number are cited.

## Decisions locked

- Twenty-six posts in five parts, mirroring the sibling's shape; no new posts. The 2026-09-04 audit proposed six and rejected all six on duplication, scope, or substance; the one with substance (failure and recovery) was folded into hrn-017 to hrn-019.
- Framework-agnostic: no SDK is the protagonist; hrn-020 is the one survey.
- Separate repository and separate id space from context-engineering; the sibling is a prerequisite, not a dependency.
- Part titles are normalised to hyphen and sentence case in both the sidecars and `series.yaml`: `Part I - Foundations`, `Part II - Core primitives`, `Part III - Control and reliability`, `Part IV - Scale and orchestration`, `Part V - Production and builds` (the sidecars had an em-dash separator, title case, and an ampersand in three of the five). "&" became "and" in part titles only.
- `status: complete` in `series.yaml`, following the README badge and the audit's executed status; the registry's `shipped` is the same state.
- Levels: hrn-001, hrn-002, and hrn-004 beginner; hrn-017, hrn-018, hrn-022, hrn-025, and hrn-026 advanced; all others intermediate. `levels_used` is `[beginner, intermediate, advanced]`.
- `requires` is the one-or-few-post chain a reader must have read for the post's code to make sense; `recommends` carries the rest of the dense in-post cross-link graph (every post links to between four and twenty-three others). The three builds require every post whose component they assemble.
- Cross-series ids appear only for mcp (locked) and ai-security (sec-NNN equal to its plan's post number); context-engineering is prose until it locks.
- The old `HARNESS-PLAN.md` is preserved verbatim at `audits/plan-pre-lock.md` and `AUDIT-2026-09-04.md` moves to `audits/`; README links to both are updated at the migration commit, not by this lock.

## Recorded divergences

- Titles. All twenty-six sidecar titles carry an em-dash subtitle, an ampersand, or a slash and are kept verbatim in Section 5 (twenty-two of them have the form "Title, em-dash, subtitle"; hrn-007, hrn-008, hrn-010, hrn-013, hrn-014, hrn-018, hrn-020, hrn-021, and hrn-023 contain an ampersand; hrn-012 a slash; hrn-024 and hrn-025 a number sign). The house style asks for no em-dashes; retitling to a colon form is work for each post's migration commit, and is recorded here once.
- Sidecar schema. The sidecars are in the Context Engineering house form (`description`, `last_modified`, `keywords`, `category`, `series`, `hero_alt`, `toc`, `draft`, `canonical_url`, `next`, `prev`) and lack the standard's `summary`, `updated`, `status`, `level`, `prerequisites`, `code`, and `outcomes`. The migration commit maps `description` to `summary` and `last_modified` to `updated`, and adds `level`, `prerequisites`, `recommended`, `code`, and `outcomes` from Section 5 and from each post's "After reading this you will be able to" block.
- Body template. Posts carry a TL;DR, an outcomes block, numbered sections, Common pitfalls, Further reading, and What to read next, but no prerequisites line and no question bank; `questions.json` is absent in every post directory and is migration work.
- README. The part headings in README.md still use the em-dash separator and the ampersand, and the status badge links to `HARNESS-PLAN.md`; both change at migration.
- hrn-005: the pre-lock plan's brief named five failure modes and "small reproducible notebooks"; the post ships six modes (destructive action added as the safety failure) and a trace-fingerprint snippet instead of notebooks.
- hrn-007: the pre-lock brief promised "a tiny MCP client call wired into the loop"; the post ships the dispatch as an inline snippet and no companion under `code/`.
- hrn-020: the pre-lock brief named "Agent SDK, LangGraph, and peers" and the post adds the open harness engines (the Apache-2.0 Codex engine) as a fourth shape; `03-harness-ab.svg` was redrawn after the audit to carry the caveat that twenty tasks do not settle the choice.
- hrn-024 and hrn-025: the audit found the token budget unenforceable in Build #1 and the jail unenforced in Build #2; both companions and both posts were corrected on 2026-09-05, and the specs above describe the corrected behaviour.
- hrn-017: the audit found the claim protocol double-claiming under threads; the companion now confirms the rename landed and ships a barrier-synchronised test, and the post teaches the lesson.

# 10. Roadmap

All 26 posts are drafted and shipped, with eight companions and eighty passing tests. Next, in order:

1. Lock commit: `Lock the curriculum`, tag `lock-1.0.0`. This adds `series.yaml`, this `plan.md`, the normalised `part:` strings and `id:` keys in the sidecars, and `audits/plan-pre-lock.md` and `audits/AUDIT-2026-09-04.md`.
2. Migration commit per post (STANDARD.md Section 13): map the sidecars to the standard schema, add `level`, `prerequisites`, `recommended`, `code`, and `outcomes` from Section 5, add the prerequisites line to each body, retitle to the colon form without em-dashes, and update the README part headings and plan links.
3. Question banks: write `questions.json` for every post to the family floor, aligned to each post's outcomes block.
4. Add the family validator beside `tools/audit.py` and keep both green; retire whatever `audit.py` checks that the validator now covers.
5. When context-engineering locks, add its ids to the `recommends` of the posts named in Section 7 and bump the plan version.
6. Decide whether to commit the candidate project hrn-p01 (Section 8).
