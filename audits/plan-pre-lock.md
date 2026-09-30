# Harness Engineering — Free Blog Series

A complete, free, practitioner-grade series on **Harness Engineering for LLM Agents** — the discipline of engineering everything around the model (the loop, tools, state, verification, guardrails, orchestration, and observability) that turns a text-completer into a trustworthy autonomous agent.

This document is the **single source of truth** for the series:

- The relationship to the *Context Engineering* series (its prerequisite)
- The repository layout
- The 26-post series outline (with thesis, sections, diagrams, code, and references for each post)
- The diagram system, writing style, and review checklist
- The list of reference assets (glossary, cheatsheet, harness-anatomy poster)

When in doubt, edit this file *first*, then update the posts.

---

## 0. Relationship to the Context Engineering Series

This is the **sibling / sequel** to the *Context Engineering* series. It is a **separate repository** that cross-links to it, not a new part inside it.

**The through-line — three eras of applied LLM engineering:**

| Era | Years | Bottleneck | Discipline | Where |
| --- | ----- | ---------- | ---------- | ----- |
| 1 | 2022–23 | **Phrasing** — how you word the request | Prompt engineering | (pre-history) |
| 2 | 2024–25 | **Information** — what goes in the window | **Context engineering** | *the CE series* |
| 3 | 2026+ | **Autonomy & control** — the machine around the model | **Harness engineering** | *this series* |

**The one-sentence bridge (belongs in Post 01):**

> Context Engineering answered: *given one model call, what tokens go in and where?* Harness Engineering answers the next question: *how do you wrap the model in a loop, tools, verification, and guardrails so it can run autonomously for hours — and be trusted?*

**The clean conceptual seam:** *context engineering is a component **inside** harness engineering.* The harness is everything that is not the model — the runtime that calls the model, handles its tool calls, and decides when to stop. Context engineering designs *what the model sees each step*; harness engineering designs *the machine that drives it*.

**The equation the whole series turns on:** `Agent = Model + Harness`.

**Prerequisite handling.** This series assumes the reader has internalised the CE series (or can). It links back to CE for anything about *token-level* context assembly and goes deep on the *runtime machinery* CE only gestured at. Where a topic appears in both series, the lens is split explicitly:

| Topic | Context Engineering lens (prior series) | Harness Engineering lens (this series) |
| ----- | --------------------------------------- | -------------------------------------- |
| MCP | how a tool's schema costs tokens in the window | how the MCP runtime dispatches calls in the loop |
| Memory | episodic / semantic / procedural *content* | cross-session *state machinery*, the ratchet |
| Sub-agents | isolation as a *context* strategy | orchestration topologies & shared-repo coordination |
| Evals | Ragas / LLM-as-judge on *outputs* | Terminal-Bench / harness A/B on *trajectories* |
| Hooks & workflow | CE Part V ("Modern Agentic Workflow") — a *preview* | the full treatment: hooks as deterministic enforcement |

CE's **Part V (Workflow & Builds)** is, in effect, "harness engineering, lite." This series is that Part V expanded into its own complete treatment.

---

## 1. Goals & Audience

**Goal.** Produce the most complete free resource on harness engineering — the natural next step for anyone who has learned context engineering and now wants to ship agents that run autonomously and reliably.

**Audience.** Three personas, all served by the same posts at different depths:

1. **Builders** — engineers shipping agentic features who need patterns that work in production.
2. **Platform / infra** — people building the internal "agent control plane" for their org.
3. **Students / self-learners** — people who want a structured, free curriculum that continues from context engineering.

**Pedagogical principles** (identical to the CE series, for continuity):
- Every post answers one question.
- Every post has at least one diagram and one runnable code snippet (or a link to one).
- Every non-obvious claim is cited.
- No marketing voice. Neutral, textbook tone.
- Examples come before formalism.
- **Framework-agnostic.** Examples are plain Python and direct provider SDKs first; a framework is shown only when it materially changes the shape of the code. No single framework is the protagonist.

---

## 2. Repository Layout

```
harness-engineering/
├── README.md                          # Series overview + table of contents
├── HARNESS-PLAN.md                    # This file (the master plan)
├── GLOSSARY.md                        # Harness-specific terms; extends the CE glossary
├── CHEATSHEET.md                      # One-page printable: loop + 11 components + failure modes + ratchet
├── REFERENCES.md                      # Master bibliography (papers, blogs, talks)
├── CONTRIBUTING.md                    # Style guide, diagram standards, PR rules
├── LICENSE                            # CC-BY 4.0 for prose, MIT for code
│
├── assets/
│   ├── diagrams/
│   │   ├── src/                       # Editable sources (.excalidraw, .drawio, .svg, .mmd)
│   │   ├── exports/                   # Rendered SVG/PNG used by posts
│   │   └── style/                     # Shared palette/typography tokens (imported from the CE token set)
│   ├── images/
│   └── animations/                    # two animated SVGs: the loop turning, and a context reset
│
├── poster/                            # The single-page A2 sheet, at the repo root
├── posts/
│   ├── 01-from-context-to-harness/
│   │   ├── index.md
│   │   ├── frontmatter.yaml           # slug, date, tags, hero, reading_time
│   │   ├── diagrams/
│   │   └── snippets/
│   ├── 02-anatomy-of-a-harness/
│   │   └── ...
│   ...
│   └── 26-capstone-coding-agent-harness/
│
├── code/                              # Runnable companions; smaller ones have an offline-testable core
│   ├── 03-agent-loop/                 # Post 03 — a ~120-line ReAct loop with stop conditions
│   ├── 06-tools-and-bash/            # Post 06 — bash/code tool + schema validation
│   ├── 11-verification-loop/         # Post 11 — test-driven self-correction
│   ├── 13-hooks/                     # Post 13 — pre/post-tool hooks that gate a run
│   ├── 17-parallel-agents/          # Post 17 — file-based task claiming, no orchestrator
│   ├── 24-minimal-harness/          # Post 24 — Build #1, harness from scratch
│   ├── 25-harness-plus/             # Post 25 — Build #2, + hooks/sandbox/sub-agents
│   └── 26-coding-agent/             # Post 26 — capstone
│
├── templates/
│   ├── post-template.md
│   ├── diagram-style-guide.md
│   ├── code-readme-template.md
│   └── citation-style.md
│
└── tools/
    ├── render-diagrams.ps1
    ├── lint-posts.ps1
    ├── word-count.ps1
    └── build-cheatsheet.ps1
```

**Naming rule:** `posts/NN-kebab-case-slug/`. `NN` is a stable two-digit number. The slug never changes after publishing (URL stability). Identical convention to the CE repo.

---

## 3. The Series at a Glance

26 posts in 5 parts + 3 reference assets. Reading order is linear; each part is also a useful standalone unit.

| #   | Part                        | Title (working)                                                              |
| --- | --------------------------- | --------------------------------------------------------------------------- |
| 01  | I — Foundations             | From Context to Harness — the Third Era                                      |
| 02  | I                           | The Anatomy of a Harness                                                     |
| 03  | I                           | The Agent Loop — ReAct, Control Loops, and Stopping                          |
| 04  | I                           | Why the Harness Beats the Model — the Evidence                              |
| 05  | I                           | Agent Failure Modes — Victory Declaration, Context Anxiety, Doom Loops       |
| 06  | II — Core Primitives        | Tools as the Agent's Hands — Bash, Code, and Schemas                         |
| 07  | II                          | Skills & MCP in the Runtime                                                  |
| 08  | II                          | State & the Filesystem — Durable Memory and Git as State                     |
| 09  | II                          | Context Management Inside the Loop — Compaction, Offloading, Resets          |
| 10  | II                          | Continual Learning & the Ratchet — Every Mistake Becomes a Rule             |
| 11  | III — Control & Reliability | Verification Loops — Tests, Self-Critique, Fail-Fast                         |
| 12  | III                         | Planner / Generator / Evaluator — Separating Roles                           |
| 13  | III                         | Hooks & Deterministic Enforcement — Guardrails as Code                       |
| 14  | III                         | Permissions, Sandboxes & Security — the AI Control Plane                     |
| 15  | III                         | Human-in-the-Loop — Approvals, Interventions, Async Feedback                 |
| 16  | IV — Scale & Orchestration  | Multi-Agent Orchestration — Topologies, and When *Not* To                    |
| 17  | IV                          | Parallel Agents on a Shared Repo — Worktrees and Task-Claiming               |
| 18  | IV                          | Long-Horizon & Multi-Context Execution — Ralph Loops and Context Bridging    |
| 19  | IV                          | Loop Engineering — Designing the Loop That Prompts the Agent                 |
| 20  | IV                          | The SDK & Framework Landscape — Agent SDK, LangGraph, and Peers              |
| 21  | V — Production & Builds     | Observability & Trace-Driven Harness Repair                                  |
| 22  | V                           | Evaluating Harnesses — Terminal-Bench, SWE-bench, Harness A/B                |
| 23  | V                           | The Economics of a Harness & Harness-as-a-Service                           |
| 24  | V                           | Build #1 — A Minimal Agent Harness from Scratch                              |
| 25  | V                           | Build #2 — Add Hooks, Sandbox, and Sub-Agents                                |
| 26  | V                           | Capstone — A Long-Running, Trusted Coding-Agent Harness                      |

Reference assets shipped alongside:
- `GLOSSARY.md` — harness-specific terms, alphabetised, one-line definitions; **extends** (does not duplicate) the CE glossary.
- `CHEATSHEET.md` — single page: the agent loop, the 11 harness components, the agent failure modes, the ratchet principle, a "context vs harness vs orchestration" decision tree.
- `poster/one-page-of-harness-engineering.svg` — single A2-printable SVG placing every component on one canvas: loop, tools, state, sandbox, verification, hooks, permissions, orchestration, observability, plus the four exits, the six failure modes, three measured costs, and the order to build them in. Lives at `poster/` in the repository root, matching the sibling series and the `build:poster` script, rather than under `assets/` as earlier drafts of this plan said.

---

## 4. Diagram System

Goal: the series should look like a small, beautifully designed book — and visually match the CE series so the two read as one body of work. **Import the CE design tokens** (`assets/diagrams/style/tokens.json` / `tokens.css`) unchanged.

**Toolchain.**
- **Custom SVG** (hand-edited) for canonical hero diagrams and precise charts (e.g. the harness-vs-model performance-gap chart, the loop timeline).
- **Excalidraw** for hand-feel conceptual diagrams.
- **Mermaid** for sequence and state diagrams (the agent loop, tool-call sequences, planner/evaluator handoffs) that benefit from being source-controllable text.
- **draw.io** only when neither fits.
- **Animated SVG** for the two moments that are about *time* rather than shape: the loop turning, and a context reset with a handoff file. Both are built (`assets/animations/`), both are drawn with the same roughjs generator and tokens as the post figures, and both animate opacity only, inside `prefers-reduced-motion: no-preference`, over a still frame that is already the complete diagram. No Lottie: a self-contained SVG needs no runtime and degrades to the still everywhere CSS animation is unavailable.

**Style tokens** (shared with CE): 1 primary, 1 accent, 3 neutrals, 1 alert; colour-blind safe. Stroke 1.5 px primary / 1 px secondary. Inter for labels, JetBrains Mono for code. Max 960 px display width, 2× retina export. Every diagram ships dark- and light-mode variants, a caption, an `alt` description, and its editable source.

**Canonical "hero" diagrams (drawn once, reused):**
1. The Agent Loop (Reason → Act → Observe → Stop?) — used in 03, 05, 11, 19.
2. The Harness Anatomy (the 11 components) — used in 02, 06, 13, 21.
3. Model + Harness equation / performance-gap chart — used in 01, 04.
4. Three-Eras timeline (prompt → context → harness) — used in 01.
5. Planner / Generator / Evaluator triangle — used in 12, 18.
6. Hook lifecycle (pre-tool, post-edit, pre-commit, session-start) — used in 13, 10.
7. Sandbox / permission boundary — used in 14, 25.
8. Multi-agent topologies gallery (single, orchestrator-worker, shared-repo swarm) — used in 16, 17.
9. Ralph loop / context-reset-with-handoff — used in 18, 09.
10. Harness Anatomy poster — the recurring "you are here" mini-map.

---

## 5. Per-Post Specs

Each spec is the brief a writer (human or agent) needs to draft the post. Format:

> **Thesis** — one sentence the post must prove.
> **Sections** — H2 outline.
> **Diagrams** — what to draw.
> **Code** — what to ship in `code/NN-…/` if any.
> **References** — must-cite sources.

> **Note (Parts I–II, as shipped):** where a post's shipped diagram or code differs from the brief below, the shipped version is canonical and the brief records the original intent. Posts 03/05/09/10 ship diagrams that differ from the drafted type but cover the same content.

### Part I — Foundations

#### 01. From Context to Harness — the Third Era
- **Thesis.** Applied LLM work has moved through three eras — prompt, context, harness — and in 2026 the harness (everything that is not the model) is the dominant lever; context engineering is now one component inside it.
- **Sections.** The three eras and their shifting bottlenecks (phrasing → information → autonomy) · "If you're not the model, you're the harness" · The equation `Agent = Model + Harness` · How this series relates to the Context Engineering series (context ⊂ harness) · The precise vocabulary: model, scaffold, harness, context engineering, harness engineering, orchestration · What this series will and won't cover.
- **Diagrams.** (a) Three-eras timeline. (b) Nested rings: model ⊂ scaffold ⊂ harness ⊂ orchestration. (c) The `Agent = Model + Harness` equation as a hero.
- **Code.** None.
- **References.** Anthropic "Building Effective Agents"; Anthropic Claude Agent SDK docs; OpenAI "Harness engineering" (Codex); Faros "Harness Engineering"; Hugging Face agent glossary; the Context Engineering series (Post 01).

#### 02. The Anatomy of a Harness
- **Thesis.** Every production harness is the same eleven components; naming them turns "my agent is flaky" into a diagnosable, buildable system.
- **Sections.** The component map (loop · tools/code · state/filesystem · context management · memory/continual learning · verification · hooks/enforcement · permissions/sandbox · orchestration · long-horizon patterns · observability) · Prebuilt vs custom harness layers · A guided tour of one mature harness (Claude Code's layered architecture, decoded) · How the rest of the series maps onto this map.
- **Diagrams.** Hero — the Harness Anatomy (all 11 components with data flow). A layered view of a real harness (input / knowledge / integration / execution / output / observability / multi-agent).
- **Code.** None (map only).
- **References.** Addy Osmani "Agent Harness Engineering"; awesome-harness-engineering taxonomy; Databricks "What is an AI Agent Harness?"; O'Reilly Radar "Agent Harness Engineering".

#### 03. The Agent Loop — ReAct, Control Loops, and Stopping
- **Thesis.** At its core a harness is a loop — Reason → Act → Observe — and most agent bugs are stopping-condition bugs, not reasoning bugs.
- **Sections.** The ReAct pattern in plain English · The minimal control loop (call model → parse tool calls → execute → feed results → repeat) · Stopping conditions (goal met, max-iterations, token/time budget, no-progress detection) · Streaming vs batch turns · State carried across iterations · Where the loop lives relative to the provider API.
- **Diagrams.** Hero — the Agent Loop with the four exit conditions annotated. A Mermaid sequence diagram of one loop iteration.
- **Code.** `code/03-agent-loop/` — a ~120-line ReAct loop over a provider SDK with explicit, layered stop conditions; offline-testable core (mock model).
- **References.** Yao et al. "ReAct" (2022); Anthropic "Building Effective Agents"; awesome-harness-engineering (Agent Loop section).

#### 04. Why the Harness Beats the Model — the Evidence
- **Thesis.** The gap between what a model can do and what you see it doing is largely a harness gap; the same model swings enormously on harness design alone.
- **Sections.** The claim, stated carefully · Terminal-Bench 2.0 case studies (same model, harness-only improvements moving agents up the leaderboard) · The reported ~6× same-model performance spread · The "skill issue" reframe — failures as configuration, not weights · The model–harness co-training flywheel (why models feel different inside their native harness) · How to reason about model choice once you accept this.
- **Diagrams.** (a) Same-model, different-harness performance-gap bar chart (with citations). (b) The co-training flywheel.
- **Code.** None (a small reproducible mini-benchmark is deferred to Post 22).
- **References.** Faros "Harness Engineering" (LangChain #30→#5); MindStudio harness posts (6× gap, Stripe throughput); HumanLayer "skill issue" framing; Addy Osmani (co-training flywheel).

#### 05. Agent Failure Modes — Victory Declaration, Context Anxiety, Doom Loops
- **Thesis.** Autonomous agents fail in a small set of recurring, nameable ways; each maps to a specific harness fix. (The runtime analogue of the CE series' "five context failure modes.")
- **Sections.** Victory declaration (marking done without verifying) · Context anxiety (rushing as the window fills) · One-shotting / overreach · Doom loops and thrashing · Silent drift from conventions · Detection signals for each · The failure-mode → harness-component fix table.
- **Diagrams.** A five/six-panel "symptom → cause → harness fix" gallery. Decision tree: symptom → likely failure mode → component to change.
- **Code.** Small reproducible notebooks, one per failure mode (synthetic tasks).
- **References.** Faros (victory declaration, context anxiety, one-shotting); Drew Breunig / Chroma "context rot" (bridge back to CE Post 06); Martin Fowler "Humans and Agents in Software Engineering Loops".

### Part II — Core Primitives

#### 06. Tools as the Agent's Hands — Bash, Code, and Schemas
- **Thesis.** Rather than pre-building a tool for every action, give the agent a small set of general-purpose tools — bash and code execution — and let it compose; schema quality decides reliability.
- **Sections.** Tools as the action surface of the loop · The general-purpose-tool argument (bash/code beats fifty bespoke tools) · Tool schema design (naming, descriptions, when *not* to call) · Structured output and validation as a tool contract · Parallel tool calls · Ten focused tools vs fifty overlapping ones.
- **Diagrams.** Tool-dispatch inside the loop. Bash-as-universal-tool vs bespoke-tool-zoo, side by side.
- **Code.** `code/06-tools-and-bash/` — a bash/code execution tool with schema validation and safe parsing; offline-testable.
- **References.** Anthropic tool-use docs; OpenAI structured outputs; awesome-harness-engineering (Tool Design); Addy Osmani (tool curation). Bridge to CE Post 15 for token-cost framing.

#### 07. Skills & MCP in the Runtime
- **Thesis.** Skills and MCP are how a harness loads capability on demand; the runtime concern is discovery, dispatch, and progressive disclosure — not just the schema.
- **Sections.** Skills as loadable procedures · Progressive disclosure (load a tool/skill only when the task needs it) · MCP as the runtime integration layer (host/client/server, recap from CE) · Dispatching an MCP call inside the loop · Skill registries and distribution · The cost of an over-stuffed tool list.
- **Diagrams.** Progressive-disclosure timeline (tools appearing as tasks demand them). MCP dispatch sequence inside one loop iteration.
- **Code.** A minimal skill-registry + loader; a tiny MCP client call wired into the loop.
- **References.** MCP spec; Anthropic skills launch; awesome-harness-engineering (Skills & MCP). Bridge to CE Post 15.

#### 08. State & the Filesystem — Durable Memory and Git as State
- **Thesis.** The filesystem is the harness's cheap, durable extension of the context window, and git turns agent state into something versioned and reversible.
- **Sections.** Why agents need state outside the window · The filesystem as scratchpad and inter-step bus · Git as versioned state (checkpoints, rollback on error) · Handoff artefacts between sessions/agents · When to use a flat file vs a store · Anti-patterns (state that should have been in the prompt, and vice-versa).
- **Diagrams.** Filesystem-and-git as durable state around the loop. A handoff-file lifecycle.
- **Code.** A checkpoint/rollback helper backed by git; a handoff-file writer/reader.
- **References.** Addy Osmani (filesystem & git); Manus blog (append-only history, from CE); awesome-harness-engineering (Memory & State). Bridge to CE Post 08 (WRITE).

#### 09. Context Management Inside the Loop — Compaction, Offloading, Resets
- **Thesis.** A long-running harness must actively manage its own context or it rots; the three runtime moves are compaction, tool-output offloading, and full resets with a handoff.
- **Sections.** Context rot inside a live agent (recap from CE, applied to a running loop) · Compaction (summarise-and-offload older context) · Tool-call offloading (2,000-line log → file → read on demand) · Progressive disclosure (again, as a context move) · Full context resets with a structured handoff file · Choosing between them.
- **Diagrams.** Context-window timeline with a compaction event and an offload event. Reset-with-handoff sequence.
- **Code.** A rolling-summary compactor and a tool-output offloader (write large outputs to disk, return a pointer).
- **References.** awesome-harness-engineering (Context Delivery & Compaction); Addy Osmani (context management); Anthropic long-running-agent harness write-up. Explicit bridge to CE Posts 03, 12.

#### 10. Continual Learning & the Ratchet — Every Mistake Becomes a Rule
- **Thesis.** A good harness gets better over time because each failure is converted into a durable constraint; memory files and the "ratchet principle" are how learning survives a fresh context.
- **Sections.** Statelessness vs continual learning · Memory files injected every session (`AGENTS.md`/`CLAUDE.md`) · Keep it to a pilot's checklist, not a style guide (earn each line) · The ratchet: mistake → rule + hook + reviewer check · Cross-session knowledge consolidation · When memory becomes clutter.
- **Diagrams.** Hook lifecycle feeding memory. The ratchet: a failure turning into three durable constraints.
- **Code.** A tiny "learn-from-failure" helper that appends a rule to a memory file and registers a matching check.
- **References.** Addy Osmani (the ratchet principle, `AGENTS.md`); awesome-harness-engineering (Memory & State). Bridge to CE Post 16.

### Part III — Control & Reliability

#### 11. Verification Loops — Tests, Self-Critique, Fail-Fast
- **Thesis.** Verification is what makes autonomy safe: check each step so small errors surface immediately instead of compounding into a wasted run.
- **Sections.** Why verify per-step (fail-fast beats fail-at-the-end) · Test suites as the agent's ground truth · Self-critique and its limits (agents skew positive grading their own work) · Feeding errors back into the loop ("success is silent, failures are verbose") · Wasted-compute economics of unverified runs.
- **Diagrams.** The loop with a verification gate. Compounding-error vs fail-fast, side by side.
- **Code.** `code/11-verification-loop/` — a test-driven self-correction loop: run tests, inject failures, retry to green; offline-testable.
- **References.** Faros (verification loops as fail-fast); Addy Osmani (self-verification, silent success); awesome-harness-engineering (Verification & CI). Bridge to CE Post 20.

#### 12. Planner / Generator / Evaluator — Separating Roles
- **Thesis.** Splitting planning, generation, and evaluation across separate agents beats a single self-grading agent, because an independent evaluator doesn't skew positive.
- **Sections.** Why self-evaluation is biased · The planner/generator/evaluator split ("GANs for prose") · Sprint contracts — negotiating "done" before coding · Handoffs between roles · Cost of the extra roles vs the reliability won · When a single agent is enough.
- **Diagrams.** Planner/Generator/Evaluator triangle with handoff artefacts. A sprint-contract sequence.
- **Code.** A three-role loop where an independent evaluator gates the generator against a pre-agreed contract.
- **References.** Addy Osmani (planner/generator/evaluator, sprint contracts); Anthropic long-running-agent harness (planner/generator/evaluator roles, verification gates); awesome-harness-engineering (Planning & Task Decomposition).

#### 13. Hooks & Deterministic Enforcement — Guardrails as Code
- **Thesis.** Some rules are too important to leave to the model; hooks run deterministic code at lifecycle points to make certain failures structurally impossible.
- **Sections.** The limits of asking the model nicely · Hook lifecycle points (pre-tool, post-edit, pre-commit, session-start) · What to enforce deterministically (typecheck/lint/tests on edit; block `rm -rf`, force-push, `DROP TABLE`; require approval before PRs; auto-format) · Hooks as the enforcement half of the ratchet · Keeping hooks fast and quiet.
- **Diagrams.** Hero — hook lifecycle around the loop. A blocked-destructive-command flow.
- **Code.** `code/13-hooks/` — a pre-tool / post-edit hook system that gates a run (deny-list + post-edit test runner); offline-testable.
- **References.** Addy Osmani (hooks, "make failures structurally impossible"); Claude Code hooks docs; awesome-harness-engineering (Permissions, Verification).

#### 14. Permissions, Sandboxes & Security — the AI Control Plane
- **Thesis.** An autonomous agent with real tools is an attack surface and a blast radius; sandboxing and structured permissions are the control plane that bounds both.
- **Sections.** Isolated execution (allow-listed commands, network isolation, ephemeral runtimes) · Permission systems beyond prompts (structured authorization, role-based access) · Blast-radius thinking (what can this run destroy?) · Prompt injection reaching a tool-using agent (recap + runtime defences) · The "AI control plane" framing for orgs · A threat-model template for a harness.
- **Diagrams.** Sandbox / permission boundary (hero). Indirect-injection-into-a-tool sequence with defence layers.
- **Code.** A sandbox wrapper (allow-list + timeout + working-dir jail) around the bash tool.
- **References.** Databricks (harness security); awesome-harness-engineering (Security, Sandbox & Permissions); Simon Willison prompt-injection corpus; OWASP LLM Top 10. Bridge to CE Post 23.

#### 15. Human-in-the-Loop — Approvals, Interventions, Async Feedback
- **Thesis.** Full autonomy is rarely the goal; the harness decides *where* a human must approve, *when* to pause, and *how* feedback re-enters the loop.
- **Sections.** The autonomy spectrum (suggest → approve → act) · Approval gates for irreversible actions · Interruption and steering mid-run · Asynchronous / streaming feedback · Escalation triggers · Designing for reviewer trust and fatigue.
- **Diagrams.** The autonomy spectrum. An approval-gate sequence with an async human reply.
- **Code.** An approval-gate primitive (pause on a flagged tool call, resume on decision).
- **References.** Martin Fowler "Humans and Agents in Software Engineering Loops"; awesome-harness-engineering (Human-in-the-Loop); Faros (reviewer fatigue metrics).

### Part IV — Scale & Orchestration

#### 16. Multi-Agent Orchestration — Topologies, and When *Not* To
- **Thesis.** Orchestration coordinates *agents as units*, one level above the harness; it's powerful and over-used, and the right default is a single agent with sub-tasks.
- **Sections.** Harness vs orchestrator (within-agent vs across-agents) · Topologies (single, orchestrator-worker, pipeline, swarm) · The steelman for staying single-agent · When multi-agent genuinely pays · Shared files as the inter-agent bus · A decision framework.
- **Diagrams.** Multi-agent topologies gallery (hero). Decision tree: do you need orchestration?
- **Code.** A minimal orchestrator-worker example (no framework).
- **References.** Anthropic "Building Effective Agents"; Cognition "Don't Build Multi-Agents"; awesome-harness-engineering (Orchestration). Bridge to CE Post 13.

#### 17. Parallel Agents on a Shared Repo — Worktrees and Task-Claiming
- **Thesis.** Many agents can work a single codebase in parallel without a central orchestrator if they claim tasks via files and isolate their edits in worktrees.
- **Sections.** The shared-repo pattern (Anthropic's 16 parallel Claude instances, no central orchestrator) · Task-claiming via files · Git worktrees for edit isolation · Merge/conflict handling · Throughput vs coordination cost · Failure isolation across the swarm.
- **Diagrams.** Shared-repo swarm claiming tasks via files. Worktree isolation per agent.
- **Code.** `code/17-parallel-agents/` — file-based task claiming + per-worktree isolation over a toy repo; offline-testable.
- **References.** Anthropic long-running / multi-instance harness write-up; awesome-harness-engineering (Task Runners & Orchestration); MindStudio (Stripe-scale throughput).

#### 18. Long-Horizon & Multi-Context Execution — Ralph Loops and Context Bridging
- **Thesis.** Tasks bigger than one context window are handled by resetting to a fresh context against a written spec and repeating — the Ralph loop — with state living on disk.
- **Sections.** Work that outgrows one window · The Ralph loop (same prompt, fresh context, one task, commit, repeat) · Context bridging across sessions (handoff files, spec-as-source-of-truth) · Multi-context software builds · Convergence criteria and stopping · Where this overlaps planner/evaluator (Post 12).
- **Diagrams.** Hero — Ralph loop resetting context to a handoff/spec. Multi-context build timeline.
- **Code.** A Ralph-style driver: spec file + fresh-context runner + commit-per-iteration + success check.
- **References.** Geoffrey Huntley (Ralph technique); Anthropic long-running-agent harness (multi-context builds, handoff artefacts); awesome-harness-engineering (Agent Loop, state persistence).

#### 19. Loop Engineering — Designing the Loop That Prompts the Agent
- **Thesis.** The 2026 shift is from prompting the agent to designing the loop that prompts it for you — with layered exits so it stops for the right reason.
- **Sections.** "Stop prompting, design the loop" · Layered exits (verifier confirms goal · hard max-iterations · token/time budget · no-progress detection) · Loop engineering vs a bare while-loop · Composing loops (inner verify loop inside an outer task loop) · Guardrails against runaway spend.
- **Diagrams.** The loop with all four layered exits. Nested inner/outer loops.
- **Code.** A budget-and-progress-aware loop controller wrapping the Post 03 loop.
- **References.** Addy Osmani (loop engineering, June 2026); Cobus Greyling / tosea.ai (loop engineering); Peter Steinberger & Boris Cherny (as cited by Osmani).

#### 20. The SDK & Framework Landscape — Agent SDK, LangGraph, and Peers
- **Thesis.** You rarely build a harness fully from scratch in production; knowing what the major SDKs give you (and take away) is the practical skill.
- **Sections.** What an agent SDK provides (loop, tools, context management, hooks, permissions) · Claude Agent SDK · OpenAI Agents SDK / Codex harness · LangGraph and graph-based control · When to use an SDK vs roll your own · Portability and lock-in · Harness-as-a-Service (preview of Post 23).
- **Diagrams.** Feature-matrix of major harness SDKs. Build-vs-buy decision tree.
- **Code.** The same tiny task, implemented against two SDKs, for comparison.
- **References.** Anthropic Claude Agent SDK docs; OpenAI "Harness engineering" (Codex); LangGraph docs; awesome-harness-engineering (Reference Implementations).

### Part V — Production & Builds

#### 21. Observability & Trace-Driven Harness Repair
- **Thesis.** You cannot improve a harness you cannot see; per-run traces are what let you find the failing component and ratchet a fix.
- **Sections.** What to log (inputs, outputs, tokens, latency, tool calls, sub-agent spans, stop reasons) · Trace trees for one agent run · Replays and regression detection · Reading a trace to localise a harness-level failure · Agents that analyse their own traces to propose harness fixes · A minimal OTel-based DIY stack.
- **Diagrams.** A trace tree for one agent run. Trace → localised-component → ratchet fix.
- **Code.** An OTel-instrumented wrapper around the loop emitting spans per iteration/tool call.
- **References.** OpenTelemetry GenAI semconv; Langfuse / Phoenix docs; Addy Osmani (agents analysing traces). Bridge to CE Post 22.

#### 22. Evaluating Harnesses — Terminal-Bench, SWE-bench, Harness A/B
- **Thesis.** Harness quality is measured on *trajectories and outcomes*, not single outputs; you A/B whole harnesses on real task benchmarks.
- **Sections.** Output evals (CE) vs trajectory/outcome evals (here) · Agentic benchmarks (Terminal-Bench, SWE-bench and kin) · Building an internal eval harness for your agent · A/B-testing harness changes on a fixed task set · Production metrics (dollars/merged-PR, first-pass success, defect-escape rate) · Guarding against benchmark overfit.
- **Diagrams.** Output-eval vs trajectory-eval comparison. A harness A/B pipeline.
- **Code.** A small harness A/B runner: one task set, two harness configs, scored side by side (offline-testable core).
- **References.** Terminal-Bench; SWE-bench; Faros staged metrics (dollars/PR, first-pass rate, defect escape); awesome-harness-engineering (Evals & Verification). Bridge to CE Post 20.

#### 23. The Economics of a Harness & Harness-as-a-Service
- **Thesis.** Loops multiply token cost and latency; the economics of a harness — and the shift to Harness-as-a-Service — decide whether an agent ships.
- **Sections.** Cost of a loop (N iterations × context) · Latency budget for an autonomous run · Budget ceilings as guardrails · Prompt caching across loop iterations (recap from CE) · HaaS — from LLM APIs (return completions) to harness APIs (return runtimes) · Build-vs-rent economics.
- **Diagrams.** Cost/latency of a multi-iteration run. LLM-API vs harness-API (HaaS) contrast.
- **Code.** A per-run cost/latency meter that sums across loop iterations and tool calls.
- **References.** Addy Osmani (HaaS); Databricks (harness platform); Anthropic/OpenAI prompt-caching docs. Bridge to CE Post 05.

#### 24. Build #1 — A Minimal Agent Harness from Scratch
- **Thesis.** A real, useful harness is ~500 lines once you've internalised Parts I–III: loop + tools + verification + stop conditions.
- **Sections.** Spec · The loop (from Post 03) · Bash/code tool (from Post 06) · A verification gate (from Post 11) · Layered stop conditions (from Post 19) · Running it on a real task · What we deliberately left out.
- **Diagrams.** End-to-end architecture of the minimal harness. Sequence of one full task run.
- **Code.** `code/24-minimal-harness/` — full repo with tests and a one-command demo; offline-runnable core.
- **References.** Posts 03, 06, 11, 19.

#### 25. Build #2 — Add Hooks, Sandbox, and Sub-Agents
- **Thesis.** Hardening the minimal harness into something you'd trust means adding deterministic enforcement, isolation, and a sub-agent — each a small, bounded addition.
- **Sections.** Adding hooks (Post 13) · Adding a sandbox and permissions (Post 14) · Adding one sub-agent (Post 16) · Adding a human approval gate (Post 15) · Observability wiring (Post 21) · Before/after reliability on a task set.
- **Diagrams.** The Build #1 harness with the four new components layered on. Blast-radius before/after.
- **Code.** `code/25-harness-plus/` — extends Build #1 with hooks, sandbox, sub-agent, approval gate.
- **References.** Posts 13, 14, 15, 16, 21.

#### 26. Capstone — A Long-Running, Trusted Coding-Agent Harness
- **Thesis.** Putting the whole series together: a coding agent that runs across multiple contexts, verifies itself, enforces guardrails, is observable, and is A/B-evaluated — end to end.
- **Sections.** Product spec · The long-horizon driver (Ralph/loop engineering, Posts 18–19) · Planner/generator/evaluator (Post 12) · Hooks + sandbox + permissions (Posts 13–14) · Memory & the ratchet (Post 10) · Observability + harness A/B (Posts 21–22) · Cost guardrails (Post 23) · Deployment · What to ship next.
- **Diagrams.** Full harness architecture. Data-flow across a multi-context run. Eval/observability loop.
- **Code.** `code/26-coding-agent/` — production-shaped repo tying the series together.
- **References.** Posts 10, 12, 13, 14, 18, 19, 21, 22, 23; Anthropic long-running-agent harness; OpenAI "Harness engineering".

---

## 6. Reference Assets

### `GLOSSARY.md`
Harness-specific terms, alphabetised, one or two lines each; **extends** the CE glossary rather than duplicating it (cross-link shared terms). Examples: *agent loop, blast radius, control plane, doom loop, handoff artefact, HaaS, harness, hook, loop engineering, no-progress detection, orchestrator, planner/generator/evaluator, progressive disclosure, Ralph loop, ratchet principle, ReAct, sandbox, scaffold, sprint contract, stop condition, task-claiming, tool-call offloading, trajectory eval, verification loop, victory declaration, worktree*.

### `CHEATSHEET.md`
Single page, printable:
- The agent loop (Reason → Act → Observe → Stop?) with the four exit conditions.
- The 11 harness components.
- The agent failure-mode taxonomy with its fixes.
- The ratchet principle.
- A "context engineering vs harness engineering vs orchestration" decision tree.

### `poster/one-page-of-harness-engineering.svg`
A single A2-printable SVG placing every component on one canvas — model, loop, tools/code, filesystem/git, sandbox, verification, hooks, permissions, memory, orchestration, observability — together with the four exits, the six failure modes, three measured costs and the order to build them in, because a poster is read standing up and out of order. Visually consistent with the CE one-pager, and at the same 1200 by 1700. **Built**; see `poster/README.md`.

---

## 7. Style Guide (short version)

Identical to the CE series, for continuity:
- Voice: **neutral, textbook**. Second-person "you" is fine when it addresses the reader directly; avoid "I" and "we" (outside an explicit code-along) and any marketing tone.
- Sentences: short. Paragraphs: 2–4 sentences.
- Define every acronym on first use, in every post (don't assume linear reading).
- Inline citations as parenthetical `(Author, Year)`; full bibliography in `REFERENCES.md`.
- Code: runnable, with `pyproject.toml`. Official provider SDKs and the reference agent SDKs; **framework-agnostic** — plain Python first, a framework only when it changes the shape of the code.
- Every post starts with: a 2–4-sentence TL;DR, an estimated reading time (in the `frontmatter.yaml` sidecar), and the 3–5 things the reader will be able to do after. Keep prose under ~10 em-dashes per post.
- Every post ends with: a "Common pitfalls" block, a "Further reading" block, and a "What to read next" pointer. Cross-link to the Context Engineering series wherever a token-level detail is assumed.

---

## 8. Build & Review Workflow

1. **Spec lock.** A post is written only after its spec in §5 is reviewed and pinned.
2. **Diagram-first.** Diagrams are drafted before prose; prose adapts to the diagram.
3. **Draft → review → diagram polish → code → eval pass.** Five-step gate per post.
4. **Lint.** `tools/lint-posts.ps1` enforces frontmatter, alt-text, dead links.
5. **Cross-link.** Every post links forward to at least one upcoming post, back to at least one prior post, and — where relevant — across to the Context Engineering series.
6. **License.** Prose CC-BY 4.0, code MIT.

---

## 9. Decisions

1. **Separate sibling repo.** This series lives in its own repo (`harness-engineering`) and cross-links to the Context Engineering repo; it does not extend the CE repo. Rationale: CE is already a coherent 30-post unit; a standalone repo keeps URLs stable and lets this series stand alone.
2. **Prerequisite, not dependency.** The series assumes CE as background but is readable on its own; token-level details are linked out to CE rather than re-taught.
3. **Length.** 26 posts in 5 parts, mirroring the CE shape (Foundations → Primitives → Control → Scale → Builds).
4. **Overlap policy.** Topics shared with CE (MCP, memory, sub-agents, evals, security, observability) are covered from the *runtime/harness* lens; each such post opens with a one-line pointer to its CE counterpart.
5. **Design system.** Import the CE design tokens unchanged so the two series read as one body of work.
6. **Publishing order.** Strict numerical for the canonical path; ship a Part at a time once its posts and diagrams are polished.
7. **Framework-agnostic.** No single SDK is the protagonist; Post 20 surveys the landscape neutrally.
8. **Translation.** English only for v1.

---

## 10. State of the Build

Section 10 was originally a pre-writing to-do list. All of it is done; this is what the
repository actually looks like, and what is still outstanding.

**Shipped.** All 26 posts (Parts I–V), each with `index.md`, `frontmatter.yaml` and three
figures. Eight runnable code companions under `code/`, all offline, 80 passing tests
between them. `GLOSSARY.md` (71 terms), `CHEATSHEET.md`, `REFERENCES.md` with a section
per post, `templates/` (post, diagram-style, code-readme, citation-style), and
`tools/audit.py`, which gates structure, frontmatter, links and the SVG contract.

**Deviations from §2 worth knowing.** There is no `posts/NN-slug/snippets/` directory;
code lives inline in the post or in `code/`. `assets/` holds the diagram generator rather
than the `src`/`exports`/`style` split §2 sketches. The design tokens are imported from the
Context Engineering series unchanged, `--ce-*` prefix included — that is deliberate, not
drift.

**Done since this section was written.** The poster exists, at `poster/` rather than under
`assets/`. The hand-drawn pass covers all 26 posts, and the hand-drawn render is now the
*published* figure for all 78 rather than an opt-in alternate. Frontmatter carries the
sibling's full field set.

**Outstanding.**

Both items previously listed here are closed.

1. **The canonical heroes were checked, and only one pair actually disagreed.** The rule in §4
   is "drawn once, reused", and no post reuses another post's SVG file. That turned out to be
   the right call rather than a lapse: the loop appears in 03, 05, 11 and 19, but 03 draws it
   in full while the others compress it to a card reading *reason, act, observe* and cite Post
   03 by number, which is reuse of the vocabulary where reuse of the file would waste the
   canvas. The same holds for the anatomy (02, and the three posts that name components by
   number), the topologies (16 marks its swarm panel "Post 17"), and the three build-versus
   decisions, which are about components (02), frameworks (20) and runtimes (23) and do not
   overlap. **The one real conflict was Post 20's `03-harness-ab` against Post 22's
   `02-harness-ab-pipeline`.** Post 20's figure promised that twenty tasks settle the choice
   "in an afternoon"; Post 22's works a *larger* task set through to p = 0.39 and declines to
   call it. Post 20's own §6 agrees with Post 22 and the figure had dropped the caveat. It now
   carries §6's worked numbers and the arithmetic that undercuts them.
2. **`assets/animations/` is built**: two animated SVGs, a README, and a `build:animations`
   script. See §4.

`AUDIT-2026-09-04.md` is the current work list and supersedes this section wherever the two
disagree. `tools/PROGRESS.md` is the resume point.
