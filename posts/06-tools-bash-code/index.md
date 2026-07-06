# 06 · Tools as the agent's hands — bash, code, and schemas

> **TL;DR.** Tools are the ACT step of the loop — the surface through which a model changes the world. The durable lesson of 2025–26 is counter-intuitive: instead of building a bespoke tool for every action, give the model a *few general-purpose tools* — above all bash and code execution — and let it compose them. Reliability then comes from two disciplines: schemas good enough that the model knows when *not* to call, and validating every call against its schema before executing it. A tool is a contract written in tokens.
>
> **After reading this you will be able to:**
> - Design a tool schema that teaches the model when to call it — and when not to.
> - Argue for a small set of general tools over a zoo of narrow ones, on both reliability and safety grounds.
> - Validate a tool call against its schema so a bad call becomes a correctable error, not a crash.

![Tool dispatch flow: the model emits a tool call, the harness validates the input against the tool's schema, and either executes it or returns an error observation without running anything.](diagrams/01-tool-dispatch.svg)
*Dispatch is validate-then-execute. The schema is the contract; a call that violates it is refused and handed back for the model to fix.*

---

## 1. Tools are the ACT step of the loop

[Post 03](../03-the-agent-loop/index.md) drew the loop as reason → act → observe. This post is the **act** stage in depth. A tool is whatever the harness lets the model invoke to affect the world: run a shell command, call an API, read or write a file. Everything else in the loop — the reasoning, the stopping — is bookkeeping around this one capability. Take tools away and you have a chatbot; add them and you have an agent.

Two properties make tools the delicate part of the harness. First, they are the model's only *causal* connection to reality, so their design decides both what the agent *can* do and what it can do *by mistake* — the blast radius from [Post 05](../05-agent-failure-modes/index.md)'s destructive-action failure. Second, every tool a model *might* call is described to it on *every* call, before the user's request even appears. A tool definition is not free; it is tokens the model reads each turn (a cost the Context Engineering series works out in full, Post 15). Tool design is therefore always two things at once: a usability decision and a budget decision.

---

## 2. The general-purpose-tool argument

The instinct when building an agent is to enumerate: it will need to read files, so add `read_file`; write files, so add `write_file`; list directories, search, move, copy, delete… Fifty tools later you have a combinatorial mess. The better instinct, now widely adopted, is the opposite: **give the model a handful of general-purpose tools and let it compose them** (Osmani, 2026).

![Two panels: a zoo of ~50 narrow tools on the left with a large overlapping schema, versus a few general tools — bash, python, read_file, write_file — on the right with a tiny schema that composes anything.](diagrams/02-universal-vs-zoo.svg)
*The model already knows how to use `bash`. It half-knows your fifty bespoke wrappers. One general surface is also one surface to sandbox.*

The single most powerful tool is **bash** (or equivalently, code execution). Anything the fifty narrow file tools could do, a shell command does — and countless things they could not, because the model can *compose*: pipe, loop, chain, write a throwaway script. Four advantages fall out:

- **A tiny schema.** `bash` takes one string. Fifty tools take fifty schemas the model reads every call.
- **Nothing to choose between.** With fifty overlapping tools the model must *pick*, and picking wrong is a failure mode of its own. With `bash` there is one obvious surface.
- **Patterns the model was trained on.** Models have seen enormous amounts of shell and Python. They have seen far less of *your* `move_file_v2` wrapper. The general tool is the one the model is best at.
- **One surface to secure.** Sandboxing one general tool is tractable ([Post 14](../14-permissions-sandboxes/index.md)); sandboxing fifty narrow ones, each with its own edge cases, is not.

This does not mean *only* bash. A few high-value structured tools earn their place — a retrieval tool, a tool that returns strongly-typed data your code consumes downstream. The rule is not "one tool"; it is **"the fewest general tools that cover the space,"** and to reach for a bespoke tool only when a general one genuinely cannot express the action.

---

## 3. Schema design: teach the model when *not* to call

A tool's schema and description are the entire interface the model has to it. Good ones do more than describe parameters — they teach *judgement*. The goal, in a phrase, is a tool that is **easy to use well and hard to use badly.**

- **Name for the action, not the implementation.** `run_tests` beats `pytest_invoke`; the model reasons about intent, not your stack.
- **Write the description for the caller, not the maintainer.** Say what the tool is *for*, what it returns, and — most valuable — *when not to call it*. "Use for arithmetic on numbers you already have; do **not** use to look up facts" prevents a whole class of misuse before it happens.
- **Constrain the input.** A tight schema (`enum` instead of free string, `required` fields, `additionalProperties: false`) is documentation the model cannot ignore and a validator you get for free (§4).
- **Return errors as information.** A tool's output — including its errors — is an *observation* the model reads next turn. "error: file not found: /tmp/x" is a correctable signal; a raised exception that crashes the loop is not.

Every one of these is also a token decision. A description precise enough to prevent misuse costs tokens on every call; an over-explained tool crowds the window. Aim for the *shortest* description that still teaches when not to call — a pilot's checklist, not a manual.

---

## 4. Validation is the tool contract

Because the model generates tool calls as text, it can generate calls that violate the schema — a missing field, a wrong type, a hallucinated parameter. The harness must not pass these straight through to execution. Dispatch is therefore two steps, always in this order: **validate the input against the schema, then execute only if it passes** (the hero diagram).

The payoff is the difference between a *correctable error* and a *crash*. When validation fails, the harness returns an error observation — "invalid input: missing required 'command'" — and the model, seeing it next turn, fixes the call. The loop self-corrects. Without validation, a malformed call reaches your execution code and throws, taking down the turn or, worse, executing something half-formed. This is the same principle as structured output and constrained decoding on the *generation* side (Context Engineering, Post 21), applied on the *dispatch* side.

The [code companion](../../code/06-tools-and-bash/) implements exactly this: a small JSON-Schema validator, a `ToolRegistry` that validates before it dispatches, and a `bash` tool with a deny-list — and its whole test suite runs offline.

---

## 5. Parallel tool calls

Modern models can request *several* tool calls in a single turn — read three files at once, run two independent checks. A harness that executes them one after another leaves latency on the table. Two rules keep parallel calls safe:

- **Parallelise only independent calls.** Reading three files is independent; "create a file then read it" is not. When calls depend on each other, the model should sequence them across turns, not batch them.
- **Return results in a stable, labelled order.** Each result must be tied back to the call that produced it (by an id), or the model cannot tell which observation answers which action.

Parallel execution is a latency optimisation, not a correctness one. As with streaming ([Post 03](../03-the-agent-loop/index.md) §6), get the serial version correct first, then parallelise the calls you have proven are independent.

---

## 6. Curate: the fewest tools that cover the space

Pulling §§2–5 together into one operating rule: **treat the tool list as a budget to be spent deliberately, not a pantry to be stocked.** Every tool added is schema tokens on every call, one more thing for the model to choose among, and one more surface to secure. The bias should be toward *removal*: ten focused tools beat fifty overlapping ones (Osmani, 2026), and the same curation discipline that keeps a memory file to a checklist ([Post 10](../10-continual-learning-ratchet/index.md)) keeps a tool list sharp.

When you *do* have many capabilities to expose — dozens of MCP servers, say — the answer is not to load all their schemas at once. It is **progressive disclosure**: load a tool only when the task needs it, the subject of [Post 07](../07-skills-mcp-runtime/index.md).

---

## Common pitfalls

- **A bespoke tool for every action.** Fifty narrow tools cost more, confuse the model, and multiply the attack surface. Prefer a few general ones (§2).
- **Passing tool calls straight to execution.** Without schema validation, a malformed call crashes the turn instead of being handed back for the model to fix (§4).
- **Letting a tool raise.** A tool's errors are observations. Return "error: …" as a string; never let an exception escape into the loop (§3, §4).
- **Descriptions written for the maintainer.** The model needs to know what the tool is *for* and *when not to call it* — not how it is implemented (§3).
- **Forgetting the token cost.** Every tool schema is read on every call. An over-stuffed tool list quietly taxes every turn (§1, §6).
- **Parallelising dependent calls.** Batch only independent actions; sequence anything with a data dependency (§5).
- **Exposing `bash` without a sandbox.** A general tool is powerful precisely because it can do anything — which is why it needs the deny-list and sandbox of Posts 13–14.

---

## Further reading

- Anthropic, "Tool use" documentation (2024–26) — tool schemas, `tool_use` / `tool_result`, parallel tool calls.
- OpenAI, "Structured outputs" / function calling docs — schemas as contracts on the generation side.
- Addy Osmani, "Agent Harness Engineering" (2026) — bash-as-a-universal-tool and tool curation ("ten focused tools").
- awesome-harness-engineering (2026) — the "Tool Design" section.
- Context Engineering, Post 15 — the token-cost framing of tool definitions.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 07 — Skills & MCP in the runtime](../07-skills-mcp-runtime/index.md)**: how to expose *many* capabilities without paying for all their schemas at once — progressive disclosure.
- **[Post 14 — Permissions, sandboxes & security](../14-permissions-sandboxes/index.md)**: making the one general tool safe — the deny-list and sandbox that bound `bash`.
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: revisit the ACT step this post expanded.
