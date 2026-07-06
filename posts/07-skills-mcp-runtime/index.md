# 07 · Skills & MCP in the runtime

> **TL;DR.** [Post 06](../06-tools-bash-code/index.md) argued for a *few* general tools. But real agents still need to reach dozens of capabilities — parse PDFs, query a database, file a ticket. The runtime answer is not to load all their schemas at once; it is **progressive disclosure**: keep a large catalog of skills on disk, cheap and dormant, and load a skill's tools into the window only when the task needs them. MCP is the standard that lets those capabilities live in separate servers, so the harness dispatches to them without ever holding their schemas until the call. Skills and MCP are the same idea from two angles: capability on demand.
>
> **After reading this you will be able to:**
> - Explain why loading every tool upfront is a tax on every turn, and how progressive disclosure removes it.
> - Trace an MCP tool call through host → client → server and back, inside one loop turn.
> - Structure a skill registry that discloses tools to the model only when they are relevant.

![Progressive-disclosure timeline: a skill catalog of eight dormant skills on disk, and three turns where the task loads just the one skill it needs — pdf, then sql, then browser — keeping the window small.](diagrams/01-progressive-disclosure.svg)
*The catalog is on disk and costs nothing until used. Each turn loads only the skill the task calls for, so the window never carries schemas it does not need this turn.*

---

## 1. Skills are loadable procedures

A **skill** is a named bundle of capability the agent can pull in when a task calls for it: a set of tools, a snippet of instructions on how to use them, sometimes a reference file. "Parse and query PDFs" is a skill; "operate the ticketing system" is a skill. The defining property is that a skill is *loadable* — it exists in a catalog and is brought into the model's context only when relevant (Anthropic, 2025).

This matters because of the tension [Post 06](../06-tools-bash-code/index.md) left open. A few general tools are ideal, but a serious agent genuinely needs many *specific* capabilities too, and every capability described to the model costs tokens on every call. Twelve skills, each with a couple of tools and a paragraph of guidance, is thousands of tokens the model re-reads every turn even when the current task touches none of them. The window fills with instructions for jobs the agent is not doing.

Skills resolve the tension by separating **having** a capability from **loading** it. The catalog can be arbitrarily large; the window only ever holds what this turn needs.

---

## 2. Progressive disclosure

The mechanism is **progressive disclosure**: load a tool or skill only when the task needs it, not at startup (awesome-harness-engineering, 2026). The hero diagram shows the shape. The catalog sits on disk — eight skills, dormant, zero tokens. On the turn where the task is "read this PDF," the harness loads the `pdf` skill and only then do its tools enter the window. Next turn's different task loads a different skill. At any moment the model sees the base tools plus the one or two skills currently in play.

Contrast the alternative, **eager loading**: put every skill's schema in the system prompt so the model always has everything. It is simpler to build and it is what most first agents do — and it quietly taxes every single turn, filling the window with dormant capability and giving the model fifty things to choose among (the confusion failure from [Post 05](../05-agent-failure-modes/index.md), and the token cost from [Post 06](../06-tools-bash-code/index.md) §1). Progressive disclosure trades a little dispatch machinery for a window that stays small — which, as [Post 09](../09-context-management-loop/index.md) will show, is the difference between an agent that stays sharp over a long session and one that rots.

The engineering question progressive disclosure raises is **discovery**: how does the harness know which skill a turn needs? Three approaches, in rough order of sophistication:

- **Keyword / trigger match.** The skill declares triggers ("pdf", "invoice"); the harness loads it when the task text matches. Crude but cheap and surprisingly effective.
- **A retrieval step.** Embed the task and the skill descriptions; load the top-k most relevant. This is RAG (Context Engineering, Posts 08–09) applied to the tool catalog itself.
- **A meta-tool.** Expose one tool, `load_skill(name)`, and let the *model* decide when to pull a skill in, having seen only the cheap catalog of names. The model discloses to itself.

Most production harnesses combine them: a cheap always-loaded catalog of names, plus the model's own `load_skill` for anything the triggers miss.

---

## 3. A skill registry, in code

Here is the core of a progressive-disclosure registry. The catalog is cheap to advertise (names only); tools enter the window only for skills a turn activates.

```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Skill:
    name: str
    triggers: list[str]                       # signals the task needs this skill
    tools: list                               # the tools it exposes (Post 06)
    setup: Callable[[], None] = lambda: None   # optional lazy initialisation

class SkillRegistry:
    def __init__(self, base_tools, skills):
        self.base_tools = base_tools
        self.skills = skills

    def catalog(self) -> list[str]:
        # cheap: names only, no schemas — safe to keep always in context
        return [s.name for s in self.skills]

    def tools_for(self, task: str) -> list:
        # progressive disclosure: base tools + only the skills this task triggers
        tools = list(self.base_tools)
        for skill in self.skills:
            if any(t in task.lower() for t in skill.triggers):
                skill.setup()                  # load lazily, once needed
                tools += skill.tools
        return tools                           # only these schemas go to the model
```

Each turn, the harness calls `tools_for(task)` and sends the model just those schemas. The `pdf` skill's tools never reach the window on a turn about databases. That is the whole idea; everything else is refinement (better discovery, caching loaded skills across turns, letting the model call `load_skill` itself).

---

## 4. MCP is progressive disclosure across a process boundary

Skills keep capability off the window until needed. The **Model Context Protocol (MCP)** does the same thing across a *process* boundary: it lets a capability live in a separate server that the harness talks to over a standard protocol, so the tool's implementation — and much of its footprint — is never in your process at all until you call it.

The Context Engineering series covered MCP end-to-end (Post 15); the runtime recap is the triangle: **host, client, server** (MCP spec, 2025).

- **Host** — your harness. It runs the loop and decides when to call a tool.
- **Client** — a connector inside the host, one per server, that speaks the MCP wire protocol (JSON-RPC over a transport).
- **Server** — a separate process or remote service that *owns* the tool: it advertises what it offers and executes calls.

The decisive property for harness engineering is the boundary. Because the server is separate, its tools do not touch your window until the model calls one, and the **same server works with any host** — swap the model or the harness and the `create_ticket` server is unchanged. MCP decouples model choice from tool choice.

---

## 5. Dispatching an MCP call inside the loop

Inside a single turn, an MCP tool call is just the ACT step of [Post 03](../03-the-agent-loop/index.md) with two extra hops — through the client and over the transport.

![MCP dispatch across host, client, and server: the model emits a tool call, the host routes it to the matching client, the client calls the server over stdio or HTTP, the server runs the tool, and the result returns the same path to become the next observation.](diagrams/02-mcp-dispatch.svg)
*Six steps, one turn. The tool runs in another process; only its result — not its schema or its code — enters your window.*

Two runtime concerns the harness owns, not the protocol:

- **Validation still applies.** The tool result comes back over the wire as data; validate it before feeding it to the model, exactly as [Post 06](../06-tools-bash-code/index.md) §4 validated the call going out. A misbehaving server is an untrusted input.
- **Failure is an observation, not a crash.** A server that times out, disconnects, or errors must surface as "error: ticketing server unavailable" — a corrigible observation — never as an exception that kills the loop. The dispatch discipline is identical to a local tool; only the failure modes are richer.

And the security note that MCP makes unavoidable: a tool result is text that re-enters the context window, so a compromised or hostile MCP server is an **indirect prompt-injection** vector. Treat server output as untrusted; this is the subject of [Post 14](../14-permissions-sandboxes/index.md).

---

## 6. Curate the catalog, not just the window

Progressive disclosure removes the *per-turn* token tax, but it does not remove the need for judgement about *what belongs in the catalog at all*. A catalog of two hundred skills is still a discovery problem — the harness (or the model) has to find the right one — and every skill is still code to maintain and secure. The curation discipline of [Post 06](../06-tools-bash-code/index.md) §6 applies one level up: **the fewest skills that cover the space**, each earning its place.

The rule of thumb: reach for a *skill* when a capability is cohesive, reusable, and occasionally needed (PDF handling); reach for a *general tool* like bash when the capability is better *composed* than packaged; and reach for an *MCP server* when the capability belongs to a system you do not own or want to run in-process (the company ticketing system). All three are the same instinct — capability on demand — at three different distances from your loop.

---

## Common pitfalls

- **Loading every tool upfront.** Eager loading taxes every turn and gives the model too much to choose among. Disclose progressively (§2).
- **Advertising full schemas in the catalog.** The always-loaded catalog should be *names and one-line descriptions*, not schemas — otherwise you have paid the tax you were avoiding (§3).
- **Trusting MCP server output.** A tool result is untrusted text re-entering the window; validate it and treat a hostile server as an injection vector (§5).
- **Letting a server failure crash the loop.** A timeout or disconnect is an observation the model can react to, not an exception (§5).
- **A catalog with no discovery.** Two hundred skills the harness cannot search is as useless as none. Progressive disclosure needs a way to *find* the right skill (§2).
- **Reaching for MCP when a local tool would do.** MCP earns its complexity when a capability belongs to another system; for your own logic, a local tool is simpler (§6).

---

## Further reading

- Anthropic, "Model Context Protocol" specification and launch (2024–25) — host / client / server, transports, resources vs tools vs prompts.
- Anthropic, "Agent Skills" launch (2025) — skills as loadable, progressively-disclosed capability.
- awesome-harness-engineering (2026) — the "Skills & MCP" and progressive-disclosure sections.
- Context Engineering, Post 15 — Tools and MCP end-to-end, and the token cost of tool and skill definitions.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 08 — State & the filesystem](../08-state-filesystem-git/index.md)**: where a loaded skill writes its intermediate work — durable state via the filesystem and git.
- **[Post 09 — Context management inside the loop](../09-context-management-loop/index.md)**: keeping the window small over a long session, of which progressive disclosure is the first move.
- **[Post 14 — Permissions, sandboxes & security](../14-permissions-sandboxes/index.md)**: treating MCP server output as untrusted — the indirect-injection surface.
