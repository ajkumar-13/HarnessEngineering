# 02 · The anatomy of a harness

> **TL;DR.** A harness looks amorphous — "everything around the model" — until you name its parts. Almost every production harness is built from the same eleven components, organised around one core: the **agent loop**. Four components *feed* the model (tools, state, context management, memory), four *govern* it (verification, hooks, permissions, observability), and two operate at larger *scale* (orchestration, long-horizon patterns). This post lays out that map, distinguishes the prebuilt harness you inherit from the custom layer you add, and shows how the rest of the series fills the map in.
>
> **After reading this you will be able to:**
> - Name the eleven components of a harness and say what each is for.
> - Diagnose an agent failure by pointing at the component responsible.
> - Separate the prebuilt harness you get from a tool from the custom layer your team must build.

![The anatomy of a harness: a central agent loop driving the model through reason, act, and observe, flanked by four components that feed the model, four that govern it, and two that operate at larger scale.](diagrams/01-harness-anatomy.svg)
*The map. One loop at the core; four components feed the model, four govern it, and two operate across agents and across context windows. The numbers are the posts that cover each.*

---

## 1. Why a map comes first

"My agent is flaky" is not a diagnosis, and "use a better model" is not usually the fix (Post 01, §5). The value of an anatomy is that it turns a vague complaint into a located one. When you can say *which component* is failing, you know which lever to pull.

The map has a centre and three neighbourhoods. The centre is the **loop** — the thing that makes it an agent rather than a single call. Around it, components divide by what they do to the model: some **feed** it information and capability, some **govern** what it is allowed to do and let you see what it did, and two operate at a larger **scale** than a single running agent. The rest of this post walks the map; the rest of the series is one post per component (Osmani, 2026; ai-boost, 2026).

---

## 2. The core: the agent loop

Everything hangs off the loop, so it comes first. A harness calls the model, reads the actions the model asks for, executes them, feeds the results back, and repeats — the **reason → act → observe** cycle, the pattern named by the ReAct line of work (Yao et al., 2022). Post 03 is entirely about it.

The single most important part of the loop is the least glamorous: **when it stops.** A loop that never stops burns money; a loop that stops too early ships half-done work. Well-built loops carry several layered stop conditions — the goal is verified, a hard iteration cap is hit, a token or time budget is exhausted, or no progress is being made. A recurring theme of this series, stated here once: *most agent bugs are stop-condition bugs, not reasoning bugs.*

---

## 3. Four components that feed the model

These decide what capability and information the model has on each turn. They are where this series overlaps most with context engineering — and where the lens differs, as Post 01 §3 set out.

**Tools & code execution (Post 06).** The agent's hands. The durable lesson of 2025–26 is that a small set of general-purpose tools — above all *bash and code execution* — tends to beat a large zoo of narrow, bespoke tools, because the model can compose general tools into actions you never pre-built (Osmani, 2026). Skills and MCP servers (Post 07) extend this surface at runtime.

**State & filesystem (Post 08).** The model's context window is small and expensive; the filesystem is large and cheap. Writing intermediate results, plans, and artefacts to disk gives the agent a durable memory outside the window, and using **git** for that state adds versioning and rollback — an agent can check out, try, and revert (Osmani, 2026).

**Context management (Post 09).** A long-running loop will fill its window and begin to degrade — *context rot*, in the CE series' terms. The harness fights this actively at runtime with three moves: **compaction** (summarise and offload older turns), **tool-output offloading** (write a 2,000-line log to disk, return a pointer), and full **context resets** with a handoff file for work that outgrows a window (ai-boost, 2026).

**Memory & continual learning (Post 10).** Feeding knowledge *across* sessions, not just within one. A memory file injected at the start of every session, and the discipline of turning each failure into a durable rule — the **ratchet principle** — is what lets a harness get better over time rather than repeating the same mistakes (Osmani, 2026).

---

## 4. Four components that govern the model

These decide what the model is allowed to do, whether its work is real, and what you can see afterwards. This neighbourhood is what separates a demo from something you would run unattended.

**Verification (Post 11).** The antidote to an agent that declares victory without checking. A verification step — running tests, a self-critique, a schema check — surfaces errors immediately, so a small early mistake does not compound into a wasted run. The operating principle: *success is silent, failures are verbose* — passing checks stay quiet; failures get injected back into the loop (Osmani, 2026).

**Hooks & enforcement (Post 13).** Some rules are too important to leave to the model's judgement. A hook is deterministic code that runs at a lifecycle point — before a tool call, after a file edit, before a commit — to enforce a rule unconditionally: run the tests after every edit, block `rm -rf` and force-pushes, require approval before opening a PR (Osmani, 2026). Hooks are the enforcement half of the ratchet.

**Permissions & sandbox (Post 14).** An agent with real tools has a real blast radius. Sandboxing (allow-listed commands, network isolation, ephemeral runtimes) and structured permissions bound what a run can touch, so a mistake — or a prompt injection reaching a tool — is contained (Databricks, 2026).

**Observability (Post 21).** You cannot improve what you cannot see. A trace of each run — inputs, outputs, tokens, latency, tool calls, sub-agent spans, and the reason the loop stopped — is what lets you localise the failing component and, increasingly, have an agent read its own traces to propose harness fixes (Osmani, 2026).

---

## 5. Two components that operate at larger scale

The last two are not about one running agent; they are about many agents, or one agent running longer than a single window allows.

**Orchestration (Post 16).** Coordinating several agents as units — one level *above* the harness. The clean boundary from Post 01: a harness drives one model through its loop; an orchestrator manages many agents. It is powerful and over-used; the right default is a single agent with sub-tasks, and multi-agent designs need a real reason (Anthropic, 2024).

**Long-horizon patterns (Post 18).** For work that outgrows one context window — building a whole project across many sessions — the harness resets to a fresh context against a written spec and repeats, carrying state on disk. The simplest form is the **Ralph loop** (Huntley, 2026); the general practice of designing these loops is **loop engineering** (Post 19).

---

## 6. Prebuilt vs custom: which parts you build

Not every component is yours to write. A useful distinction runs through the whole map (Databricks, 2026):

- **The prebuilt harness** is what a tool or SDK gives you out of the box. Claude Code, the Codex harness, and the various agent SDKs already ship a loop, tool dispatch, context management, a permission model, and hooks. You inherit these.
- **The custom harness** is the layer your team adds on top: your organisation's conventions in a memory file, your enforcement hooks, your sandbox policy, your tools, your evals. This is where most of the differentiated engineering — and most of the reliability — actually lives.

The practical consequence is that harness engineering is rarely "build a loop from scratch." It is more often *choosing a prebuilt harness well and then engineering the custom layer that makes it trustworthy for your task.* Posts 24–26 build a harness from scratch anyway — not because you always should, but because doing it once is the fastest way to understand what the prebuilt ones are doing for you.

---

## 7. A mature harness, decoded

It helps to see the map instantiated. Read against a mature production harness such as Claude Code, the eleven components resolve into recognisable layers (as decomposed by Osmani, 2026): an **input layer** (UI, sessions, permission gates), a **knowledge layer** (skills, context compaction, task state, memory), an **integration layer** (the MCP runtime and external servers), an **execution layer** (tool dispatch, the streaming runtime, prompt caching), an **observability layer** (an event bus, background execution), and a **multi-agent layer** (sub-agent coordination, isolation via worktrees).

The point of the exercise is not the specific names. It is that a real, shipping harness is not a monolith with a clever prompt inside — it is exactly the component map above, wired together. Once you can see the seams, you can change one component without disturbing the others, which is the whole reason to have a map.

---

## 8. How the rest of the series fills in the map

Each remaining post takes one component (or one pair) and goes deep:

- **Part II — Core primitives (06–10):** the four *feeds-the-model* components, plus skills/MCP.
- **Part III — Control & reliability (11–15):** the four *governs-the-model* components, plus human-in-the-loop.
- **Part IV — Scale & orchestration (16–20):** the two *scale* components, plus loop engineering and the SDK landscape.
- **Part V — Production & builds (21–26):** observability, evaluation, economics, and three builds that assemble the whole map into a working agent.

Keep the map nearby. Every later post opens by pointing at the component it fills in, so you always know where you are.

---

## Common pitfalls

- **Skipping straight to orchestration.** Multi-agent systems are the last neighbourhood on the map for a reason; a shaky single-agent harness does not improve by being run in parallel.
- **Treating the loop as an afterthought.** The loop and its stop conditions are the core, not plumbing. Most bugs live there (§2).
- **Building every component yourself.** Much of the map is prebuilt; the leverage is in the custom layer, not in re-implementing a loop (§6).
- **Confusing "feeds" with "governs".** Adding more context (a *feed* fix) will not stop an agent that ships unverified work (a *govern* fix). Locate the failure in the right neighbourhood.
- **Wiring the map as a monolith.** If changing one component forces you to touch four others, you have lost the benefit of the anatomy. Keep the seams clean (§7).
- **Adding observability last.** Without a trace you are debugging blind from the first run, not the hundredth (§4).

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (2026) — the component breakdown and the layered decomposition of a mature harness.
- ai-boost, "awesome-harness-engineering" (2026) — the community taxonomy this map is aligned with.
- Databricks, "What is an AI Agent Harness?" (2026) — prebuilt vs custom harness layers.
- O'Reilly Radar, "Agent Harness Engineering" (2026) — the harness as an operating system around the model.
- Anthropic Engineering, "Building Effective Agents" (December 2024) — workflow-vs-agent and the single-agent default.
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022) — the reason→act→observe loop at the core.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: the core of the map — reason→act→observe and the four ways a loop should stop.
- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the first *feeds-the-model* component, and why bash beats a zoo of tools.
- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: the same map, read as a catalogue of what goes wrong and which component fixes it.
