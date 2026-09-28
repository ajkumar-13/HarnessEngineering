# 07 · Skills & MCP in the runtime

> **TL;DR.** [Post 06](../06-tools-bash-code/index.md) argued for a *few* general tools, yet real agents still need dozens of specific capabilities: parse PDFs, query a database, file a ticket. The runtime answer is not to load all their schemas at once; it is **progressive disclosure**, keeping a large catalogue of skills dormant on disk and loading a skill's tools into the window only when the task needs them. **MCP** (the Model Context Protocol) is the complementary move across a process boundary: a capability lives in a separate server, so its *implementation* runs out-of-process and the same server plugs into any host. Skills and MCP are the same instinct from two angles: capability on demand. The trap is that naive disclosure rewrites the tool block every turn and destroys the prompt cache, so the operating rule is to **append discovered schemas, never swap them**.
>
> **After reading this you will be able to:**
> - Explain why loading every tool upfront is a tax on every turn, and how progressive disclosure removes it.
> - Decide from measured thresholds whether a given catalogue needs on-demand loading at all.
> - Trace an MCP tool call through host → client → server and back, inside one loop turn.
> - Disclose tools without invalidating the prompt cache, by appending schemas instead of swapping them.

![Progressive-disclosure timeline in three tiers: a catalogue of eight dormant skills on disk; three turns where the matched trigger word loads just the one skill the task needs (pdf, then sql, then browser) while 7 of the 8 stay dormant; and the four-step disclosure ladder, from names and descriptions always resident, through the full SKILL.md on relevance and bundled files on reference, to executable scripts that never enter the window at all.](diagrams/01-progressive-disclosure.svg)
*The catalogue is on disk and costs nothing until used. Each turn loads only the skill the task calls for, so the window never carries schemas it does not need this turn.*

---

## 1. Skills are loadable procedures

A **skill** is a named bundle of capability the agent can pull in when a task calls for it: a set of tools, a snippet of instructions on how to use them, sometimes a reference file. "Parse and query PDFs" is a skill; "operate the ticketing system" is a skill. The defining property is that a skill is *loadable*: it exists in a catalogue and is brought into the model's context only when relevant (Anthropic, 2025).

On disk, a skill is a folder, and one file at its root decides when the rest of the folder loads. In the shipped Agent Skills format that file is `SKILL.md`: YAML frontmatter carrying a `name` and a `description`, then a body of instructions (Anthropic, 2025).

```markdown
---
name: pdf-forms
description: Fill, flatten and extract fields from PDF forms. Use when the task
  mentions a PDF, an invoice, a form, or a scanned document.
---

# PDF forms

1. Inspect the form with `scripts/list_fields.py <file.pdf>`.
2. Fill fields from a JSON mapping with `scripts/fill.py <file.pdf> <map.json>`.
3. Always flatten before returning the file to the user.

Field-name conventions for the finance templates are in `REFERENCE.md`.
```

Notice what is absent: there is no `triggers` field. **The description is the trigger.** It is the text a host matches the task against, which means it is written for machine matching rather than for a human browsing a catalogue, and editing it silently changes when the skill fires.

Disclosure is also graded rather than binary. The shipped implementation has three levels (Anthropic, 2025):

- **Level 1, always resident.** The `name` and `description` of every installed skill are preloaded into the system prompt. That is about a line each, so a hundred skills cost less than one verbose tool schema.
- **Level 2, on relevance.** If the model judges the skill relevant to the current task, the full `SKILL.md` is read into context.
- **Level 3, on reference.** Bundled files (a `REFERENCE.md`, a schema, a lookup table) are named from `SKILL.md` and read only if the work actually reaches them.

Executable scripts sit outside the ladder entirely, and this is the level worth pausing on: the agent runs `scripts/fill.py` without either the script or the PDF ever entering the window. A skill's bulkiest material is often something the model never needs to read at all, only to invoke. That is progressive disclosure taken to its limit, and it reframes the hero diagram's binary loaded-or-dormant picture as a simplification of a four-step gradient.

---

## 2. The cost of an over-stuffed tool list

The tension [Post 06](../06-tools-bash-code/index.md) left open is that a few general tools are ideal, but a serious agent genuinely needs many *specific* capabilities too, and every capability described to the model costs tokens on every call. That cost is now measured rather than asserted. A typical multi-server setup (GitHub, Slack, Sentry, Grafana and Splunk) consumes roughly **55,000 tokens of tool definitions before the agent does any work at all**, and deferring the definitions a request does not need typically removes more than 85 per cent of that, leaving the three to five tools the request actually uses (Anthropic, 2025–26).

The arithmetic reproduces for smaller catalogues. A tool schema with a description, parameter docs and an example runs to roughly 300 to 600 tokens, and every one of them is re-read on every turn of the run.

| Catalogue | Definition tokens | Re-read over a 20-turn run | Uncached input cost | Selection risk |
|---|---|---|---|---|
| 5 focused tools | ~1,500 | 30,000 | $0.09 | comfortable |
| 12 skills (~24 tools) | ~8,000 | 160,000 | $0.48 | approaching the cliff |
| 5 MCP servers | ~55,000 | 1,100,000 | $3.30 | well past it |

Costs use the series' reference input price of $3 per million tokens ([Post 23](../23-economics-haas/index.md) §4) and assume no caching, which is the pessimistic case; §6 is about the fact that a *stable* catalogue caches and a *changing* one does not.

Tokens are only half the bill. The second cost is accuracy: a model's ability to pick the right tool degrades once it has more than roughly **30 to 50 available tools** (Anthropic, 2025–26). That threshold is worth far more than a vague warning about "too many tools", because it says where the cliff is. Below it, a flat list is fine and the dispatch machinery in this post is unnecessary. Above it, the model is guessing more often, and the guessing shows up as the measured collapse in tool-selection accuracy of [Post 06](../06-tools-bash-code/index.md) §10, or as a doom loop ([Post 05](../05-agent-failure-modes/index.md) §2.4) when a plausible wrong tool half-works.

---

## 3. Progressive disclosure

The mechanism is **progressive disclosure**: load a tool or skill only when the task needs it, not at startup (ai-boost, 2026). The hero diagram shows the shape. The catalogue sits on disk: eight skills, dormant, zero tokens. On the turn where the task is "read this PDF," the harness loads the `pdf` skill and only then do its tools enter the window. Next turn's different task loads a different skill. At any moment the model sees the base tools plus the one or two skills currently in play.

Contrast the alternative, **eager loading**: put every skill's schema in the system prompt so the model always has everything. It is simpler to build and it is what most first agents do, and past the thresholds in §2 it quietly taxes every single turn while degrading the choice the model has to make. Progressive disclosure trades that tax for some dispatch machinery and, if built carelessly, for the prompt cache as well (§6). Done properly it is what [Post 09](../09-context-management-loop/index.md) §8 classes as a *preventative* context move, alongside offloading at the tool boundary and as distinct from the three corrective ones (clear, compact, reset): it keeps schemas out of the window before any bloat forms, so there is less to compact later.

The engineering question progressive disclosure raises is **discovery**: how does the harness know which skill a turn needs? Three approaches, in rough order of sophistication:

- **Keyword / trigger match.** The skill declares triggers ("pdf", "invoice"), or, in the shipped format, its description carries them; the harness loads it when the task text matches. Crude but cheap and surprisingly effective.
- **A retrieval step.** Embed the task and the skill descriptions; load the top-k most relevant. This is the same Select pipeline that powers retrieval-augmented generation (RAG) (Context Engineering, Posts 09 and 11), applied to the tool catalogue itself. Two details decide whether it works: embed the *description*, not just the name, because a bare name collides with every other similarly-named tool; and rerank the candidates rather than trusting first-pass vector scores, which are noisy over text this short.
- **A meta-tool.** Expose one tool, `load_skill(name)`, and let the *model* decide when to pull a skill in, having seen only the cheap catalogue of names. The model discloses to itself.

In practice, harnesses often combine them: a cheap always-loaded catalogue of names, plus the model's own `load_skill` for anything the triggers miss. A custom retrieval step is a first-class shape rather than a workaround; provider tool-search interfaces accept a client-side search that hands back references to matching tools, so a team can run its own embedding search and still use the vendor's disclosure path (Anthropic, 2025–26).

---

## 4. When disclosure is worth building

Progressive disclosure is machinery, and machinery that is not needed is a liability. The published thresholds make the decision mechanical rather than a matter of taste (Anthropic, 2025–26).

| Signal | Threshold | What it means |
|---|---|---|
| Catalogue size | 10 or more tools | Start deferring; below ten, a flat list is simpler and cheaper |
| Definition budget | more than ~10k tokens of schemas | The tax is now a visible line on the bill |
| Selection accuracy | dropping as the toolset grows | You are at or past the 30–50-tool cliff (§2) |
| Aggregation | several MCP servers at once | Hundreds of tools arrive together; assume deferral from day one |
| Growth | catalogue expands over time | Build the machinery before the cliff, not after |

The inverse rule matters just as much: stay with plain eager loading when the catalogue is under ten tools, when nearly every tool is used on nearly every request, or when each definition is under a hundred tokens on its own. At that size, the dispatch machinery and the cache damage of §6 both cost more than the schemas they remove.

One corollary applies at every size: **keep the three to five most-used tools permanently loaded**. The common path should never pay a discovery round trip to find `read_file`.

---

## 5. A skill registry, in code

Here is the core of a progressive-disclosure registry. The catalogue is cheap to advertise (names only); tools enter the window only for skills a turn activates.

```python
import re
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Skill:
    name: str
    triggers: list[str]                        # words that signal the task needs this skill
    tools: list = field(default_factory=list)  # the tools it exposes (Post 06)
    setup: Callable[[], None] = lambda: None   # optional lazy initialisation

class SkillRegistry:
    def __init__(self, base_tools, skills):
        self.base_tools = base_tools
        self.skills = skills
        self.loaded: set[str] = set()

    def catalogue(self) -> list[str]:
        # cheap: names only; a real catalogue adds a one-line description each
        return [s.name for s in self.skills]

    def matches(self, skill: Skill, task: str) -> bool:
        # word boundaries, not substrings: a "git" trigger must not fire on "legitimate"
        words = set(re.findall(r"[a-z0-9_]+", task.lower()))
        return any(t in words for t in skill.triggers)

    def tools_for(self, task: str) -> list:
        # progressive disclosure: base tools + only the skills this task triggers
        tools = list(self.base_tools)
        for skill in self.skills:
            if self.matches(skill, task):
                if skill.name not in self.loaded:
                    skill.setup()              # runs once, on first activation
                    self.loaded.add(skill.name)
                tools += skill.tools
        return tools                           # only these schemas go to the model
```

Each turn, the harness calls `tools_for(task)` and sends the model just those schemas. The `pdf` skill's tools never reach the window on a turn about databases.

Two details in that listing are the ones a first implementation gets wrong. Trigger matching is on whole words, because the obvious `any(t in task for t in triggers)` fires on any containing string: a `pdf` trigger matches "pdfx" and a `git` trigger matches "legitimate" and "digital". And `setup()` is guarded by `self.loaded`, because an unguarded call runs on every turn whose text happens to match, not once.

The third thing it gets wrong is not visible in the listing at all, and it is the subject of the next section.

---

## 6. Append, never swap

`tools_for` returns a *different list* on any turn where the skill set changes, and the tool block sits at the very front of the cached prefix. Providers render a request as a prefix hierarchy, `tools` then `system` then `messages`, and a change at one level invalidates that level and everything after it. Modifying tool definitions therefore invalidates the **entire** cache: tools, system and messages together (Anthropic, 2025–26).

That collides with the rest of the series. [Post 03](../03-the-agent-loop/index.md) §5 names the re-sent prefix, rendered as tools then system prompt then messages, as exactly what prompt caching is designed to exploit, and [Post 23](../23-economics-haas/index.md) §4 calls rewriting the prefix mid-run the most expensive invisible mistake a loop makes. A naive disclosure registry commits that mistake on purpose, every time a new skill triggers.

Put numbers on it, using the series' reference rates: input at $3 per million tokens, cached prefix at a tenth of that. Take a twenty-turn run whose prefix averages 25,000 tokens, of which 8,000 is the skill catalogue (§2's middle row). Eager loading caches perfectly: one full-price read of 25,000 plus nineteen discounted reads of 2,500, about 72,500 token-equivalents. Progressive disclosure that *swaps* the block on four of those turns pays full price on each of those four, adding 4 × 22,500 = 90,000 token-equivalents, for a run total near 162,500. And the saving it bought was modest to begin with: keeping 8,000 tokens out saves their full price once and their discounted price on the other nineteen turns, 8,000 + 19 × 800, about 23,200. The mechanism has spent 90,000 to save 23,200, a four-fold loss, and none of it appears anywhere except the invoice.

The fix is one line of design: **append, never swap.** Keep the base tools in the cached prefix, mark everything else deferred, and let a newly discovered schema arrive *appended to the conversation* rather than swapped into the prefix. The vendor implementation states the property directly: deferred tools are excluded from the system-prompt prefix, and when the model discovers one, its definition is appended inline as a reference block, so "the prefix is untouched" and prompt caching is preserved (Anthropic, 2025–26).

In the registry, that is the difference between returning a new tool list and returning something to append:

```python
    def disclose(self, task: str) -> list:
        """Schemas for newly triggered skills, to APPEND to the conversation.

        The tools block itself never changes, so the cached prefix survives and
        every already-disclosed skill stays available for the rest of the run.
        """
        new = []
        for skill in self.skills:
            if self.matches(skill, task) and skill.name not in self.loaded:
                skill.setup()
                self.loaded.add(skill.name)
                new += skill.tools
        return new
```

A consequence falls out that is easy to mistake for a bug: once disclosed, a skill stays disclosed for the rest of the run. That is correct. Un-disclosing it would mean editing the prefix, which is a swap under another name, and the window cost of one extra schema is far below the cost of a cache miss.

---

## 7. Skill registries and distribution

Skills are *distributable*. Because a skill is a self-contained folder (its tools, its instructions, its triggers), a registry can version and share skills across projects the way a package manager shares libraries, and the shipped format is deliberately portable: the same folder works in a desktop client, a terminal agent, or a direct application programming interface (API) integration. That is how skill ecosystems grow beyond one team's repository.

It is also where three specific problems start.

- **Naming.** A flat catalogue assembled from several sources collides. Two `search` tools and three `create_ticket` variants confuse trigger matching and the model equally. Namespace by owner or service (`github_`, `slack_`) so one search matches a whole coherent group and the name itself carries provenance (Anthropic, 2025–26).
- **Trust.** An installed skill runs *in your process*. It is a software supply-chain dependency with none of the isolation an MCP server has (§11's figure marks exactly this: the skill column keeps nothing out of your process). Packaging is therefore a security decision as well as an ergonomic one, and it is the concrete reason a team may prefer an MCP server to a skill for identical functionality.
- **Versioning.** Because the description is the matching surface (§1), editing a description changes *when the skill fires*, not just how it reads. Descriptions are API surface, and edits to them are breaking changes even when the code beneath is untouched.

None of this argues against distribution. It argues for treating a skill's boundaries and description with the care given to a public API, and for reviewing an installed skill the way any other dependency is reviewed ([Post 14](../14-permissions-sandboxes/index.md)).

---

## 8. MCP: a tool behind a process boundary

Skills keep a capability's schema off the window until needed. MCP does the same for a capability's *code*, one step further out: it lets a tool live in a separate server that the harness talks to over a standard protocol, so the tool's implementation, and much of its footprint, never runs in your process at all.

The Context Engineering series covered MCP end-to-end (Post 15); the runtime recap is the triangle: **host, client, server** (modelcontextprotocol.io, latest).

- **Host:** your harness. It runs the loop and decides when to call a tool.
- **Client:** a connector inside the host, one per server, that speaks the MCP wire protocol (JSON-RPC over a transport).
- **Server:** a separate process or remote service that *owns* the tool: it advertises what it offers and executes calls.

The decisive property for harness engineering is the boundary. Because the server runs elsewhere, its tool *code* never executes in your process, and the **same server works with any host**: swap the model or the harness and the `create_ticket` server is unchanged. MCP decouples model choice from tool choice.

One clarification, because it is easy to overstate. MCP does **not** by itself keep a server's tool *schemas* out of your window. Most clients call the server's `tools/list` and advertise every returned schema to the model, exactly like a local tool (Anthropic, 2025). Keeping many such schemas out of the window is progressive disclosure (§3) applied to the MCP catalogue, not a free property of the protocol. What the process boundary buys you is that the tool's *implementation and dependencies* stay out of your process, not that its *interface* stays out of your context.

The remedy has two shipped shapes, and it is worth naming both rather than leaving the reader with a diagnosis. The first is deferred loading plus a search step over the catalogue: §3's meta-tool, productised, with the append-not-swap property of §6 built in. The second is stranger and more effective: stop presenting a server as a tool list at all, and present it as **code on a filesystem**, one directory per server and one file per tool, so the model reads a tool's definition only when it opens the file. Anthropic reports a workflow falling from 150,000 tokens to 2,000 on that change alone, a saving of 98.7 per cent, with the reasoning stated plainly: models are good at navigating filesystems, so presenting tools as files lets them read definitions on demand rather than all upfront (Anthropic, 2025). That is the same filesystem-as-context-extension argument [Post 08](../08-state-filesystem-git/index.md) makes, arriving from the opposite direction.

---

## 9. Dispatching an MCP call inside the loop

Inside a single turn, an MCP tool call is just the ACT step of [Post 03](../03-the-agent-loop/index.md) with two extra hops: through the client and over the transport.

![MCP dispatch across host, client, and server: the model emits a tool call, the host routes it to the matching client, the client calls the server over stdio or HTTP, the server runs the tool, and the result returns the same path to become the next observation. The host panel also records the catalogue that crosses at connect time, and a closing row gives the three runtime concerns the harness still owns: validating the result, treating failure as an observation, and the schema that arrives before any call.](diagrams/02-mcp-dispatch.svg)
*Six steps, one turn. The tool's code runs in another process; by default, only its result crosses back into your window.*

Reduced to its core, a dispatch is a request over a client that has already listed the server's tools and cached the result. The current specification revision is stateless, with self-contained requests and per-request capability negotiation (modelcontextprotocol.io, latest), so there is no long-lived session to hold. The host lists the server's tools once, caches the catalogue, and re-lists only when it has reason to believe the list has changed.

```python
# One MCP tool call, dispatched inside the ACT step of the loop (Post 03).
class StubClient:
    """Stands in for a real JSON-RPC client so this snippet runs on its own."""
    def request(self, method: str, params: dict) -> dict:
        return {"content": [{"type": "text", "text": "TICKET-4417 created"}]}

def validate(result: dict) -> dict:
    if not isinstance(result, dict) or "content" not in result:
        return {"error": "malformed tool result"}
    return result

def call_mcp_tool(client, name: str, arguments: dict) -> dict:
    try:
        result = client.request("tools/call", {"name": name, "arguments": arguments})
    except (TimeoutError, ConnectionError) as exc:
        return {"error": f"{name} unavailable: {exc}"}   # a corrigible observation, not a crash
    return validate(result)   # server output is untrusted input (Post 06 §7)

print(call_mcp_tool(StubClient(), "create_ticket", {"title": "Disk full on web-03"}))
```

The two runtime concerns the harness owns, not the protocol, are already visible in those lines:

- **Validation still applies.** The tool result comes back over the wire as data; validate it before feeding it to the model, exactly as [Post 06](../06-tools-bash-code/index.md) §7 validated the call going out. A misbehaving server is an untrusted input.
- **Failure is an observation, not a crash.** A server that times out, disconnects, or errors must surface as "error: ticketing server unavailable", a corrigible observation, never as an exception that kills the loop. The dispatch discipline is identical to a local tool; only the failure modes are richer.

And the security note that MCP makes unavoidable. A tool result is text that re-enters the context window, so a compromised or hostile server is an **indirect prompt-injection** vector. The attack is not hypothetical: in May 2025, researchers demonstrated it end to end against the official GitHub MCP server, where a malicious issue filed in a *public* repository hijacked an agent asked only to look at open issues and coerced it into leaking the contents of the user's *private* repositories (Invariant Labs, 2025). Note also that the untrusted text is not only the result. A server's tool *descriptions* are attacker-controlled text that arrives over the same `tools/list` this section depends on, and they land in the window before any call is made. Both halves are the subject of [Post 14](../14-permissions-sandboxes/index.md) §4.

---

## 10. Keeping results out of the window, not just schemas

The dispatch figure in §9 draws the default: every result crosses back into the window as an observation. That is one design, not the only one, and the alternative belongs in a post about keeping windows small.

Standard dispatch makes every tool call a round trip through the model. Three sequential calls mean three turns, and the two intermediate results are read once, never needed again, and carried in the transcript for the rest of the run. The alternative is to let the model write a short script that calls the tools, and run it. Results from those calls are not added to the model's context; only the final output of the code is (Anthropic, 2026). Token cost then scales with the size of the *answer* rather than the size of the *data*: fetching two thousand rows to compute one total costs one number instead of two thousand rows.

The measured effect follows the shape of the workload rather than being uniform, which is what makes it a decision rather than a default. On a seventy-five-tool project-management benchmark, calling programmatically cut billed input tokens by roughly **38 per cent with no change in task accuracy**; on a benchmark whose turns make only one or two sequential calls it left scores unchanged and cost about **8 per cent more** (Anthropic, 2026). The technique pays when a turn fans out across many calls or across large intermediate results, and charges a small premium when it does not.

One restriction matters here specifically: tools reached through an MCP connector currently cannot be called from code this way, which is a further argument for the filesystem presentation of §8. The same instinct applied to a single oversized output is [Post 09](../09-context-management-loop/index.md) §3's offloading, which writes the output to disk and returns a pointer.

That completes the arc. §3 keeps schemas out of the window, §8 keeps code out of the process, and this keeps results out of the window: three faces of capability on demand.

---

## 11. Curate the catalogue, not just the window

Progressive disclosure removes the *per-turn* token tax, but it does not remove the need for judgement about *what belongs in the catalogue at all*. A catalogue of two hundred skills is still a discovery problem (the harness, or the model, has to find the right one), and every skill is still code to maintain and secure. The curation discipline of [Post 06](../06-tools-bash-code/index.md) §10 applies one level up: **the fewest skills that cover the space**, each earning its place.

The rule of thumb: reach for a *skill* when a capability is cohesive, reusable, and occasionally needed (PDF handling); reach for a *general tool* like bash when the capability is better *composed* than packaged; and reach for an *MCP server* when the capability belongs to a system you do not own or want to run in-process (the company ticketing system). All three are the same instinct, capability on demand, at three different distances from your loop.

![Three cards ordered by distance from the loop: a general tool, always in the window; a skill, on disk and loaded on demand; and an MCP server, in another process. Each card gives when to reach for it, what it keeps out of your window, what it keeps out of your process, and an example.](diagrams/03-three-distances.svg)
*Two rows decide the choice: what each mechanism keeps out of your window, and what it keeps out of your process. They are not the same row.*

Setting the three side by side makes the §8 clarification impossible to miss. Read across the *window* row and only the skill removes anything; read across the *process* row and only the MCP server does. A team that adopts MCP expecting a smaller context has confused the two rows, and a team that packages a skill expecting isolation has confused them the other way. Two further attributes matter at runtime and are not in the figure:

| Mechanism | Keeps out of window | Keeps out of process | Prompt cache | Characteristic failure |
|---|---|---|---|---|
| General tool | nothing | nothing | sits in the stable cached prefix | a wrong composition the model must debug |
| Skill | its schemas, until loaded | nothing: it still runs in yours | breaks the prefix if swapped, survives if appended (§6) | never triggers, or triggers on everything |
| MCP server | nothing by itself | its code and dependencies | same append-or-swap rule, plus a catalogue that can change under you | timeout, disconnect, or a hostile schema (§9) |

Read as a decision matrix, the table says something the prose does not. The only column where the three mechanisms behave the *same* is the cache column, which is why §6 is a rule about disclosure in general rather than about skills in particular.

---

## Common pitfalls

- **Loading every tool upfront.** Past ten tools or 10k tokens of definitions, eager loading taxes every turn and degrades selection. Disclose progressively (§3, §4).
- **Building disclosure machinery for nine tools.** Below the thresholds, the dispatch code and the cache risk cost more than the schemas they remove (§4).
- **Swapping the tools block every turn.** Recomputing the tool list invalidates tools, system and messages together; append discovered schemas instead (§6).
- **Advertising full schemas in the catalogue.** The always-loaded catalogue should be *names and one-line descriptions*, not schemas; otherwise you have paid the tax you were avoiding (§5).
- **Editing a skill description as if it were prose.** The description is the matching surface, so an edit changes when the skill fires: treat it as a versioned interface (§7).
- **Assuming MCP shrinks your window for free.** A connected server's schemas are advertised to the model just like local tools; keeping them out is still progressive disclosure's job (§8).
- **Trusting an MCP server's output, or its schema.** Both are untrusted text re-entering the window, and the schema arrives first, before any call (§9).
- **Letting a server failure crash the loop.** A timeout or disconnect is an observation the model can react to, not an exception (§9).

---

## Further reading

- Anthropic, "Introducing Agent Skills" (2025): skills as portable folders of instructions, scripts and resources, loaded when needed.
- Anthropic Engineering, "Equipping agents for the real world with Agent Skills" (2025): the three disclosure levels of §1, and scripts that run without entering the window.
- Anthropic, "Tool search tool" documentation (2025–26): the 55k-token measurement, the 30–50-tool selection cliff, and the thresholds tabulated in §4.
- Anthropic, "Tool use with prompt caching" documentation (2025–26): the tools → system → messages prefix hierarchy, what invalidates each level, and why deferred loading preserves the cache.
- Anthropic, "Programmatic tool calling" documentation (2026): letting the model call tools from code so intermediate results never enter the window, and the two benchmarks behind §10's numbers.
- Anthropic Engineering, "Code execution with MCP" (2025): why most clients load every definition upfront, and the filesystem presentation that took one workflow from 150,000 tokens to 2,000.
- modelcontextprotocol.io, "Specification" (latest): host, client, server, the JSON-RPC transports, and the stateless request model of the current revision.
- Invariant Labs, "GitHub MCP vulnerability" (2025): the worked indirect-injection incident behind §9.
- ai-boost, "awesome-harness-engineering" (2026): the Skills & MCP and progressive-disclosure sections.
- Context Engineering, Post 15: tools and MCP end-to-end, and the token cost of tool and skill definitions.
- Context Engineering, "Build #2 — MCP server from scratch": building a server end to end (three tools, a resource, a prompt, a permission boundary), the server side of the boundary this post views from the host side.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 08 — State & the filesystem](../08-state-filesystem-git/index.md)**: where a loaded skill writes its intermediate work, durable state via the filesystem and git.
- **[Post 09 — Context management inside the loop](../09-context-management-loop/index.md)**: keeping the window small over a long session, of which progressive disclosure is the preventative first move.
- **[Post 14 — Permissions, sandboxes & security](../14-permissions-sandboxes/index.md)**: treating MCP server output *and* its schemas as untrusted, the indirect-injection surface.
- **[Post 23 — The economics of a harness & HaaS](../23-economics-haas/index.md)**: prompt caching as the dominant cost lever, and why §6's rule is an economic one.
- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the few-general-tools argument this post extends to on-demand skills and MCP.
