<div align="center">

# Harness Engineering

**A free, framework-agnostic series on engineering everything around the model — the loop, tools, state, verification, and guardrails — that turns an LLM into a trustworthy autonomous agent.**

The loop · tools · state · verification · hooks · sandboxes · orchestration · observability.

[![License: CC BY 4.0](https://img.shields.io/badge/Prose-CC--BY--4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE)
[![Posts](https://img.shields.io/badge/posts-26-orange.svg)](#-the-series)
[![Status](https://img.shields.io/badge/status-in%20progress-yellow.svg)](HARNESS-PLAN.md)

[Read the cheatsheet](CHEATSHEET.md) · [Glossary](GLOSSARY.md) · [References](REFERENCES.md) · [Plan](HARNESS-PLAN.md) · [Contribute](CONTRIBUTING.md)

</div>

---

## Why this exists

Most agents fail not because the model is weak but because the **machine around the model** is wrong: the loop never stops for the right reason, a tool is described badly, there is no verification step, or a destructive command has nothing to block it. The field now has a name for engineering that machine: **harness engineering**. Its founding equation is `Agent = Model + Harness`, and a growing body of evidence says the harness is a *bigger* performance lever than the model itself.[^1][^2]

This series is the sequel to the [**Context Engineering**](#-companion-series) series. Context engineering answered: *given one model call, what tokens go in and where?* Harness engineering answers the next question: *how do you wrap the model in a loop, tools, verification, and guardrails so it can run autonomously for hours — and be trusted?* Context engineering is a component **inside** harness engineering.

> No marketing voice. Neutral, textbook tone. Examples first, formalism second. Framework-agnostic.

---

## Quick start

**If you have one hour, read these three:**

1. [01 · From context to harness](posts/01-from-context-to-harness/index.md)
2. [02 · The anatomy of a harness](posts/02-anatomy-of-a-harness/index.md)
3. [03 · The agent loop](posts/03-the-agent-loop/index.md)

**If you have ten minutes, read the [one-page cheatsheet](CHEATSHEET.md).**

**If you have ten seconds:**

> `Agent = Model + Harness`. The harness is everything that is not the model: a **loop** that drives it, **tools** it acts through, **state** it keeps on disk, **verification** that checks its work, **hooks** that enforce rules deterministically, and **observability** that lets you see and fix all of it. The same model swings enormously on harness design alone.

---

## 📚 The series

Twenty-six posts in five parts. Reading order is linear; each part is also a useful standalone unit. The series assumes the *Context Engineering* series as background but is readable on its own.

### Part I — Foundations

| #  | Title | Folder |
|----|-------|--------|
| 01 | [From context to harness — the third era](posts/01-from-context-to-harness/index.md) | `01-from-context-to-harness` |
| 02 | [The anatomy of a harness](posts/02-anatomy-of-a-harness/index.md) | `02-anatomy-of-a-harness` |
| 03 | [The agent loop — ReAct, control loops, and stopping](posts/03-the-agent-loop/index.md) | `03-the-agent-loop` |
| 04 | [Why the harness beats the model](posts/04-harness-beats-model/index.md) | `04-harness-beats-model` |
| 05 | [Agent failure modes](posts/05-agent-failure-modes/index.md) | `05-agent-failure-modes` |

### Part II — Core primitives

| #  | Title | Folder |
|----|-------|--------|
| 06 | [Tools as the agent's hands](posts/06-tools-bash-code/index.md) | `06-tools-bash-code` |
| 07 | [Skills & MCP in the runtime](posts/07-skills-mcp-runtime/index.md) | `07-skills-mcp-runtime` |
| 08 | [State & the filesystem](posts/08-state-filesystem-git/index.md) | `08-state-filesystem-git` |
| 09 | [Context management inside the loop](posts/09-context-management-loop/index.md) | `09-context-management-loop` |
| 10 | [Continual learning & the ratchet](posts/10-continual-learning-ratchet/index.md) | `10-continual-learning-ratchet` |

### Part III — Control & reliability

| #  | Title | Folder |
|----|-------|--------|
| 11 | [Verification loops](posts/11-verification-loops/index.md) | `11-verification-loops` |
| 12 | [Planner / generator / evaluator](posts/12-planner-generator-evaluator/index.md) | `12-planner-generator-evaluator` |
| 13 | [Hooks & deterministic enforcement](posts/13-hooks-enforcement/index.md) | `13-hooks-enforcement` |
| 14 | [Permissions, sandboxes & security](posts/14-permissions-sandboxes/index.md) | `14-permissions-sandboxes` |
| 15 | [Human-in-the-loop](posts/15-human-in-the-loop/index.md) | `15-human-in-the-loop` |

### Part IV — Scale & orchestration

| #  | Title | Folder |
|----|-------|--------|
| 16 | [Multi-agent orchestration](posts/16-multi-agent-orchestration/index.md) | `16-multi-agent-orchestration` |
| 17 | [Parallel agents on a shared repo](posts/17-parallel-agents-shared-repo/index.md) | `17-parallel-agents-shared-repo` |
| 18 | [Long-horizon & multi-context execution](posts/18-long-horizon-ralph/index.md) | `18-long-horizon-ralph` |
| 19 | [Loop engineering](posts/19-loop-engineering/index.md) | `19-loop-engineering` |
| 20 | [The SDK & framework landscape](posts/20-sdk-landscape/index.md) | `20-sdk-landscape` |

### Part V — Production & builds

| #  | Title | Folder |
|----|-------|--------|
| 21 | [Observability & trace-driven repair](posts/21-observability-traces/index.md) | `21-observability-traces` |
| 22 | [Evaluating harnesses](posts/22-evaluating-harnesses/index.md) | `22-evaluating-harnesses` |
| 23 | [The economics of a harness & HaaS](posts/23-economics-haas/index.md) | `23-economics-haas` |
| 24 | [Build #1 — a minimal agent harness](posts/24-build-minimal-harness/index.md) | `24-build-minimal-harness` |
| 25 | [Build #2 — hooks, sandbox, sub-agents](posts/25-build-harness-plus/index.md) | `25-build-harness-plus` |
| 26 | [Capstone — a long-running coding-agent harness](posts/26-capstone-coding-agent/index.md) | `26-capstone-coding-agent` |

---

## 🧭 Companion series

This series is the sibling of **Context Engineering** — the two are designed to read as one body of work. Where a token-level detail is assumed here (how attention reads a window, what prompt caching is, how RAG assembles a layer), it is taught there and linked, not repeated. Topics shared by both series are covered from different lenses:

| Topic | Context Engineering lens | Harness Engineering lens (here) |
|-------|--------------------------|---------------------------------|
| MCP | how a tool's schema costs tokens | how the MCP runtime dispatches calls in the loop |
| Memory | episodic / semantic / procedural content | cross-session state machinery, the ratchet |
| Sub-agents | isolation as a context strategy | orchestration topologies, shared-repo swarms |
| Evals | judging outputs | judging trajectories and outcomes |

---

## 🧰 Reference assets

| Asset | What it is |
|-------|-----------|
| [`CHEATSHEET.md`](CHEATSHEET.md) | Single printable page: the loop, the eleven components, agent failure modes, the ratchet, a decision tree. |
| [`GLOSSARY.md`](GLOSSARY.md) | Every harness term, alphabetised, one-line definitions; extends the CE glossary. |
| [`REFERENCES.md`](REFERENCES.md) | Master bibliography for every citation in the series. |
| [`HARNESS-PLAN.md`](HARNESS-PLAN.md) | The master plan — thesis, sections, diagrams, and code per post. |

---

## 📜 License

Dual-licensed: **prose and diagrams** under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); **code** under [MIT](LICENSE).

[^1]: Faros AI, "Harness Engineering: Making AI Coding Agents Work in 2026." https://www.faros.ai/blog/harness-engineering
[^2]: Osmani, A., "Agent Harness Engineering." https://addyosmani.com/blog/agent-harness-engineering/
