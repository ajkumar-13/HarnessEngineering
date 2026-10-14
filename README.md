# Harness Engineering

A free, framework-agnostic series of 26 posts on the machine built around a large language model (LLM) so that it can act autonomously and be trusted: the loop that drives the model, the tools it acts through, the state it keeps on disk, the verification that checks its work, the hooks that enforce rules deterministically, the permissions, sandboxes and approvals that bound what it can do, the orchestration and long-horizon patterns that scale it, and the observability and evaluation that let its owner see and improve it. The series is built on one equation, `Agent = Model + Harness`: the harness is everything that is not the model. It is the sequel to the `context-engineering` series: context engineering decides what one model call sees, and harness engineering designs the runtime that makes the calls.

The examples are plain Python against the official provider SDKs. A framework or agent SDK appears in one post (post 20), and only to compare shapes; no framework is the subject of the series.

## What a reader builds

- A vocabulary that holds across the series: the eleven components of a harness (loop, tools, state, context management, memory, verification, hooks, permissions, orchestration, long-horizon patterns, observability), the four exits of the loop, the six agent failure modes, and the three grades of evidence for the claim that the harness matters more than the model.
- A reason-act-observe loop with layered exits, a validated tool schema, state kept on disk and under git with a handoff file, and a ratchet that turns each failure into a durable rule.
- A verification gate on the loop's final answer, blocking and reporting hooks, an allow-list sandbox, declarative permissions, and an approval gate placed where a checkpoint cannot undo the action.
- Three builds in Part V: a minimal agent harness, the same harness hardened with hooks, a sandbox, an approval gate and a sub-agent, and a long-running coding-agent harness that runs a written spec across many fresh contexts, traces each run and compares two configurations.

## The posts

### Part I - Foundations

After this part a reader can name the eleven components of a harness, write the minimal reason-act-observe loop with its four exits, grade the evidence that the harness is a bigger lever than the model, and diagnose six agent failure modes from a trace.

1. [01 - From context to harness: the third era](posts/01-from-context-to-harness/index.md)
2. [02 - The anatomy of a harness](posts/02-anatomy-of-a-harness/index.md)
3. [03 - The agent loop: ReAct, control loops, and stopping](posts/03-the-agent-loop/index.md)
4. [04 - Why the harness beats the model: the evidence](posts/04-harness-beats-model/index.md)
5. [05 - Agent failure modes: victory declaration, context anxiety, doom loops](posts/05-agent-failure-modes/index.md)

### Part II - Core primitives

After this part a reader can design and validate a tool schema, load capability on demand without destroying the prompt cache, keep state on disk and under git with a handoff file, choose between offloading, clearing, compacting and resetting the context, and run a ratchet that turns each failure into a durable rule.

6. [06 - Tools as the agent's hands: bash, code, and schemas](posts/06-tools-bash-code/index.md)
7. [07 - Skills and MCP in the runtime](posts/07-skills-mcp-runtime/index.md)
8. [08 - State and the filesystem: durable memory and git as state](posts/08-state-filesystem-git/index.md)
9. [09 - Context management inside the loop: compaction, offloading, resets](posts/09-context-management-loop/index.md)
10. [10 - Continual learning and the ratchet: every mistake becomes a rule](posts/10-continual-learning-ratchet/index.md)

### Part III - Control and reliability

After this part a reader can gate the loop's final-answer exit on ground truth, split planner, generator and evaluator with a sprint contract, write blocking and reporting hooks, bound a run with an allow-list sandbox and declarative permissions, and place approvals only where a checkpoint cannot undo the action.

11. [11 - Verification loops: tests, self-critique, fail-fast](posts/11-verification-loops/index.md)
12. [12 - Planner, generator, evaluator: separating the roles](posts/12-planner-generator-evaluator/index.md)
13. [13 - Hooks and deterministic enforcement: guardrails as code](posts/13-hooks-enforcement/index.md)
14. [14 - Permissions, sandboxes, and security: the AI control plane](posts/14-permissions-sandboxes/index.md)
15. [15 - Human-in-the-loop: approvals, interventions, async feedback](posts/15-human-in-the-loop/index.md)

### Part IV - Scale and orchestration

After this part a reader can choose a multi-agent topology and defend staying single-agent, run a leaderless swarm on a shared repository with file claims and worktrees, drive a task across many fresh contexts with a Ralph loop, compose loops with layered exits and budgets, and settle build-versus-buy against an SDK by measurement.

16. [16 - Multi-agent orchestration: topologies, and when not to](posts/16-multi-agent-orchestration/index.md)
17. [17 - Parallel agents on a shared repo: worktrees and task-claiming](posts/17-parallel-agents-shared-repo/index.md)
18. [18 - Long-horizon and multi-context execution: Ralph loops and context bridging](posts/18-long-horizon-ralph/index.md)
19. [19 - Loop engineering: designing the loop that prompts the agent](posts/19-loop-engineering/index.md)
20. [20 - The SDK and framework landscape: Agent SDK, LangGraph, and peers](posts/20-sdk-landscape/index.md)

### Part V - Production and builds

After this part a reader can instrument a run with OpenTelemetry spans, read a trace tree to the failing component, compare two harness configurations on a fixed task set and tell signal from sampling noise, price a run per successful task, and has assembled, hardened and run the three builds.

21. [21 - Observability and trace-driven repair: seeing what the harness did](posts/21-observability-traces/index.md)
22. [22 - Evaluating harnesses: Terminal-Bench, SWE-bench, harness A/B](posts/22-evaluating-harnesses/index.md)
23. [23 - The economics of a harness and Harness-as-a-Service](posts/23-economics-haas/index.md)
24. [24 - Build #1: a minimal agent harness from scratch](posts/24-build-minimal-harness/index.md)
25. [25 - Build #2: add hooks, sandbox, and sub-agents](posts/25-build-harness-plus/index.md)
26. [26 - Capstone: a long-running, trusted coding-agent harness](posts/26-capstone-coding-agent/index.md)

## Where to start

The posts are written to be read in order, and each one names the earlier posts it depends on. A reader with an hour reads [post 01](posts/01-from-context-to-harness/index.md), [post 02](posts/02-anatomy-of-a-harness/index.md) and [post 03](posts/03-the-agent-loop/index.md): why the discipline exists, the eleven components, and the loop with its exits. A reader who has finished the `context-engineering` series can skim posts 01 and 02 and start at post 03. A reader building the internal platform that many agents run inside will find permissions, sandboxes, observability, evaluation and cost in posts 14 and 20 to 23. A reader with ten minutes reads the [cheatsheet](CHEATSHEET.md).

## Before starting

The series assumes the reader can call a provider API with a tool definition and read its response, write Python at the level of a small package with tests, and use git from the command line. It takes the `context-engineering` series as background for everything at the level of tokens (prompt caching, context rot, memory content, output evaluation, prompt injection at the token level), but every post is readable without it: each borrowed idea is restated in one paragraph where it is used. Post 07 looks at the Model Context Protocol (MCP) from the host's side; the protocol itself is the subject of the `mcp` series, which no post requires.

## How a post is organised

Each post opens with a short summary, its prerequisites, and what the reader will be able to do afterwards, then works through numbered sections from the question to the answer, and closes with what can go wrong, the common pitfalls, further reading, and what to read next. Mechanism comes before name: a pattern is shown as a loop, a file, a gate or a hook in code before the field's name for it is given, and every named failure mode is tied to the component that fixes it. Every post uses the vocabulary fixed in the [notation guide](notation_guide.md). The figures read correctly in light and dark mode. Where a post has review questions, the series website shows them, with hints and explanations, beside the post.

## What is measured, and what is cited

Every cost, token count, test count, line count and benchmark figure in a post is labelled in the sentence that uses it: produced by a snippet or companion test the post names, cited to a dated source whose full entry is in [REFERENCES.md](REFERENCES.md), or marked illustrative. Claims that the harness is a bigger lever than the model are graded by the strength of their evidence (firm: the same model on the same benchmark; controlled: a comparison of scaffolds; reported: a multiple at one remove), and a reported multiple is never presented as a measured one. Cost arithmetic names the model tier and the published rate it uses, as of the date the post gives, and the posts tell the reader to re-derive it against current rates. Nearly every source is a 2025 or 2026 blog post, vendor document or preprint, and benchmark scores and prices move; each one is dated where it is quoted.

## The code

Eight companions live under [code/](code/), each a self-contained Python project with its own README, `pyproject.toml`, `src/` and tests. Each runs offline against a scripted mock model: its test suite needs no API key and no network.

| Directory | What it is | Post |
|---|---|---|
| [code/03-agent-loop/](code/03-agent-loop/) | a reason-act-observe loop with the four exits | [03](posts/03-the-agent-loop/index.md) |
| [code/06-tools-and-bash/](code/06-tools-and-bash/) | schema validation, a validate-then-dispatch registry, and one `bash` tool with a deny-list | [06](posts/06-tools-bash-code/index.md) |
| [code/11-verification-loop/](code/11-verification-loop/) | a test-driven self-correction loop: generate, verify, retry | [11](posts/11-verification-loops/index.md) |
| [code/13-hooks/](code/13-hooks/) | a pre-tool deny-list and post-edit checks that gate a run | [13](posts/13-hooks-enforcement/index.md) |
| [code/17-parallel-agents/](code/17-parallel-agents/) | a file-based task board with atomic claiming for a leaderless swarm | [17](posts/17-parallel-agents-shared-repo/index.md) |
| [code/24-minimal-harness/](code/24-minimal-harness/) | Build #1: loop, tools, a verification gate and layered exits | [24](posts/24-build-minimal-harness/index.md) |
| [code/25-harness-plus/](code/25-harness-plus/) | Build #2: Build #1 with hooks, a sandbox, an approval gate, a sub-agent and tracing | [25](posts/25-build-harness-plus/index.md) |
| [code/26-coding-agent/](code/26-coding-agent/) | the capstone: a spec run across many fresh contexts with an evaluator and a ratchet | [26](posts/26-capstone-coding-agent/index.md) |

Each installs and tests from its own directory, either with [uv](https://docs.astral.sh/uv/):

```bash
cd code/03-agent-loop
uv run --extra dev pytest -q
uv run python -m agent_loop
```

or with pip, as each companion's README shows (`python -m pip install -e ".[dev]"`, then `pytest -q`). The eight suites hold 80 tests between them (7, 15, 9, 9, 9, 10, 13 and 8 in the order of the table), and all 80 pass offline. Each README gives its offline demo and, for the companions that have one, the adapter that drives it with a real model and the API key that run needs. The scripts under a post's `snippets/` run from the series root with `uv run python posts/NN-slug/snippets/<name>.py`.

## Reference pages

- [Cheatsheet](CHEATSHEET.md): one printable page with the loop and its four exits, the eleven components, the six failure modes and their fixes, the ratchet, and which discipline a problem belongs to.
- [Glossary](GLOSSARY.md): every term the series uses, one entry each.
- [Notation guide](notation_guide.md): the fixed vocabulary, the evidence grades, the claim labels, the spelling, and the figure colours.
- [References](REFERENCES.md): every paper, vendor page, and piece of documentation the posts cite, grouped by post.

## The poster and the animations

[poster/one-page-of-harness-engineering.svg](poster/one-page-of-harness-engineering.svg) puts the whole series on one sheet, drawn by hand: the equation the series is built on, the eleven components around the loop, how the loop stops, how it fails, the verifier ladder, what survives a context reset, a panel of costs from the posts, and the order to build a harness in. It reads in light and dark mode and prints at A2.

Two figures are animated, because a loop is a thing that happens over time: [the loop turning](posts/03-the-agent-loop/diagrams/06-the-loop-turning.svg) (reason, act, observe, and the stop check after every turn), in post 03, and [a context reset](posts/09-context-management-loop/diagrams/05-context-reset.svg) (a window filling to its limit, clearing on one frame, and the handoff file that survives it), in post 09. Only opacity is animated, and only when the reader's system allows motion; with motion off, each is a complete still.

## Corrections and feedback

This repository is the published source of the series and is maintained by its author. It does not take pull requests or issues. Vendor documentation, benchmark scores and prices move quickly, so a dead link or a stale figure is a real bug: corrections and suggestions go through the series website.

## License

Prose, questions, and figures are licensed under CC BY 4.0. Code is licensed under MIT. See [LICENSE](LICENSE).
