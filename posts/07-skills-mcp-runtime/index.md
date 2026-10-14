# 07 - Skills and MCP in the runtime

> **TL;DR.** A few general tools are the ideal, yet a real agent still needs dozens of specific capabilities, and every schema described to the model is paid for on every turn. **Progressive disclosure** keeps a catalogue of skills dormant on disk and loads a skill's tools only when a task needs them; the **Model Context Protocol (MCP)** moves a capability's code into a separate server process. The trap is the prompt cache: a disclosure scheme that rewrites the tool block invalidates the whole cached prefix, so the operating rule is to **append discovered schemas, never swap them**.
>
> **Prerequisites:** [post 06](../06-tools-bash-code/index.md), the tool call as a contract and the case for a few general tools.
> **Safe to skip?** Skip it if the reader can already say what each level of skill disclosure loads, show why swapping the tool block destroys the prompt cache, and trace an MCP call from the model to a server and back inside one turn.
>
> **After reading, you will be able to:**
>
> - Describe a skill as a loadable procedure and say which of its parts load at each level of disclosure.
> - Work out what an over-stuffed tool list costs per run, and use the published thresholds to decide whether a catalogue needs on-demand loading.
> - Implement progressive disclosure with a skill registry that matches triggers on whole words and initialises each skill once.
> - Show with token counts that appending discovered schemas keeps the cached prefix and swapping them destroys it.
> - Trace an MCP tool call from model to client to server and back inside the act step, validating the result and treating failure as an observation.
> - Choose a general tool, a skill or an MCP server by what each keeps out of the window and the process, and keep results out as well.

![A six-turn run drawn left to right: the tools block and the catalogue never change; the pdf skill's two schemas are appended to the messages on turn 2 and the sql skill's on turn 4, and both stay, while six of the eight skills on disk stay dormant.](diagrams/01-progressive-disclosure.svg)

*Capability arrives when a task asks for it, and it arrives at the end of the conversation, so the front of the request never changes.*

---

## 1. Skills are loadable procedures

How does a harness give an agent dozens of capabilities without loading every schema into the window? The first half of the answer is the **skill**: a named bundle of capability the agent pulls in when a task calls for it, made of tools, instructions on how to use them, and sometimes reference files. "Parse and fill PDF forms" (Portable Document Format) is a skill; "operate the ticketing system" is a skill. Anthropic's announcement defines skills as "folders that include instructions, scripts, and resources that Claude can load when needed" (Anthropic, "Introducing Agent Skills", 16 October 2025). The defining property is that a skill is *loadable*: it sits in a catalogue and enters the model's context only when it is relevant.

On disk a skill is a folder, and one file at its root decides when the rest of the folder loads. In the Agent Skills format that file is `SKILL.md`: YAML (YAML Ain't Markup Language) frontmatter carrying a `name` and a `description`, then a body of instructions (Zhang, Lazuka and Murag, "Equipping agents for the real world with Agent Skills", Anthropic Engineering, 16 October 2025).

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

What is absent matters: there is no `triggers` field. **The description is the trigger.** It is the text the task is matched against, so it is written for matching rather than for a human browsing a catalogue, and editing it silently changes when the skill fires.

Disclosure is graded rather than binary. The engineering article names three levels and leaves room for more:

- **Level 1, always resident.** "At startup, the agent pre-loads the `name` and `description` of every installed skill into its system prompt." That is about a line each. In this post's snippet a catalogue line costs 13 tokens and a tersely written tool schema 79 on average, so a hundred installed skills cost about what seventeen such schemas cost.
- **Level 2, on relevance.** "If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full `SKILL.md` into context."
- **Level 3 and beyond, on reference.** Bundled files (a `REFERENCE.md`, a schema, a lookup table) are named from `SKILL.md`, and the article calls them "the third level (and beyond) of detail, which Claude can choose to navigate and discover only as needed".

Executable scripts sit outside the ladder: "Claude can run this script without loading either the script or the PDF into context." A skill's bulkiest material is often something the model only invokes and never reads, which is progressive disclosure taken to its limit.

---

## 2. The cost of an over-stuffed tool list

[Post 06](../06-tools-bash-code/index.md) left a tension open: a few general tools are ideal, but a serious agent needs many specific capabilities, and every capability described to the model costs tokens on every call. Anthropic's tool search documentation (consulted October 2026) puts a number on it: "A typical multiserver setup (GitHub, Slack, Sentry, Grafana, and Splunk) can consume ~55k tokens in definitions", and tool search "typically reduces this by over 85 percent", loading only the three to five tools a given request needs. Both are the vendor's own figures, reported rather than independently measured.

The arithmetic is simple: every definition is re-read on every turn of the run. The first two rows below use illustrative catalogue sizes; the third is the cited five-server figure.

| Catalogue | Definition tokens | Re-read over a 20-turn run | Uncached input cost | Selection risk |
|---|---|---|---|---|
| 5 focused tools (illustrative) | 1,500 | 30,000 | $0.09 | comfortable |
| 12 skills of about 24 tools (illustrative) | 8,000 | 160,000 | $0.48 | approaching the cliff |
| 5 MCP servers (cited) | 55,000 | 1,100,000 | $3.30 | well past it |

Costs are definition tokens times 20 turns at 3 dollars per million input tokens, the Claude Sonnet 4.6 input rate on Anthropic's pricing page (consulted October 2026; re-derive it against the current page), with no caching, which is the pessimistic case: $55{,}000 \times 20 = 1{,}100{,}000$ tokens, or $3.30. Section 6 is about the fact that a *stable* catalogue caches and a *changing* one does not.

Accuracy is the other half of the bill: the same documentation says the model's ability to pick the right tool degrades past 30 to 50 available tools. Below that threshold a flat list is fine and this post's machinery is unnecessary; above it the model guesses more often, and the guessing shows up as wrong-tool calls or as a doom loop ([post 05](../05-agent-failure-modes/index.md)) when a plausible wrong tool half-works. Gan and Sun's RAG-MCP paper (6 May 2025), on retrieval-augmented generation (RAG), measured the same effect from the other side, firm on this series' scale (one model, one benchmark, only the tool prompt changed): retrieving tools instead of listing them all "more than triples tool selection accuracy (43.13% vs 13.62% baseline)" on its benchmark tasks.

---

## 3. Progressive disclosure

The mechanism is **progressive disclosure**: load a tool or skill only when the task needs it, not at startup, which the Agent Skills article calls "the core design principle that makes Agent Skills flexible and scalable". The hero shows the shape on the six-turn run that this post's snippets use. The catalogue sits on disk: eight skills, dormant, one line each. On the turn whose task names an invoice PDF, the harness loads the `pdf` skill and only then do its tools enter the window; two turns later a task about the orders database loads `sql`. At any moment the model sees the base tools plus the skills the run has needed so far.

The alternative is **eager loading**: put every skill's schema in the request so the model always has everything. It is simpler to build, and past the thresholds of section 2 it taxes every turn and degrades the model's choice. Progressive disclosure trades that tax for dispatch machinery and, if built carelessly, the prompt cache (section 6). Done properly it is what [post 09](../09-context-management-loop/index.md) classes as a *preventative* context move, alongside offloading at the tool boundary and distinct from the corrective ones (clear, compact, reset): it keeps schemas out of the window before any bloat forms.

The engineering question it raises is **discovery**: how does the harness know which skill a turn needs? Three approaches, in rough order of sophistication:

- **Keyword or trigger match.** The skill declares trigger words ("pdf", "invoice"), or, in the shipped format, its description carries them; the harness loads it when the task text matches. Crude and cheap.
- **A retrieval step.** Embed the task and the skill descriptions and load the top few: the select pipeline of RAG (`ctx-009` and `ctx-011`) applied to the tool catalogue. Embed the *description*, not just the name, which collides with every similarly named tool, and rerank the candidates, because first-pass vector scores are noisy over text this short.
- **A meta-tool.** Expose one tool, `load_skill(name)`, and let the *model* decide when to pull a skill in, having seen only the cheap catalogue. The model discloses to itself.

A harness can combine them: a cheap always-loaded catalogue, plus the model's own `load_skill` for anything the triggers miss. A custom retrieval step is a supported shape rather than a workaround: the tool search documentation lets a team implement its own search logic "(for example, using embeddings or semantic search)" by returning `tool_reference` blocks from a tool of its own, so its own search still uses the vendor's disclosure path.

---

## 4. When disclosure is worth building

Progressive disclosure is machinery, and machinery that is not needed is a liability. The thresholds the tool search documentation publishes make the decision close to mechanical:

| Signal | Threshold in the documentation | What it means |
|---|---|---|
| Catalogue size | 10 or more tools | Start deferring; below ten, a flat list is simpler |
| Definition budget | more than 10k tokens of definitions | The tax is a visible line on the bill |
| Selection accuracy | dropping as the toolset grows | At or past the 30 to 50 tool cliff of section 2 |
| Aggregation | several MCP servers, 200 or more tools | Assume deferral from the first day |
| Growth | a library that grows over time | Build the machinery before the cliff, not after |

The inverse rule matters as much. The same page calls standard tool calling the better fit below ten tools, when every tool is used in every request, or when the definitions are small, under 100 tokens in total. At that size the dispatch machinery and the cache risk of section 6 cost more than the schemas they remove, and building disclosure for nine tools is a mistake in the other direction.

One corollary applies at every size, and the documentation states it as a tip: keep the three to five most-used tools always loaded. The common path should never pay a discovery round trip to find `read_file`.

---

## 5. A skill registry, in code

The core of a progressive-disclosure registry fits on one screen. The catalogue is cheap to advertise (one line per skill); tools enter the request only for skills a task activates. This is the top of `snippets/skill_registry.py`:

```python
import re
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Skill:
    name: str
    description: str                           # the catalogue line, always resident
    triggers: list[str]                        # words that signal the task needs this skill
    tools: list = field(default_factory=list)  # the tool schemas it exposes (post 06)
    setup: Callable[[], None] = lambda: None   # optional lazy initialisation

class SkillRegistry:
    def __init__(self, base_tools, skills):
        self.base_tools = base_tools
        self.skills = skills
        self.loaded: set[str] = set()

    def catalogue(self) -> list[str]:
        # cheap: one line per skill, never a schema
        return [f"{s.name}: {s.description}" for s in self.skills]

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

A harness built this way calls `tools_for(task)` each turn and sends just those schemas, so the `pdf` tools never reach the window on a turn about databases. The snippet's catalogue holds eight skills (pdf, sql, browser, email, git, image, calendar, translate) and three base tools, and its run is six tasks; it prints what each turn would send:

```text
turn  task                                         swap: tools_for() sends          append: disclose() adds
   1  List the files in the reports folder.        base + -                         -
   2  Extract the totals from invoice-march.pdf.   base + pdf_extract, pdf_fill     pdf_extract, pdf_fill
   3  Write the totals to totals.txt.              base + -                         -
   4  Query the orders database for March.         base + sql_query, sql_schema     sql_query, sql_schema
   5  Compare the two sets of totals.              base + -                         -
   6  Write a short summary to summary.txt.        base + -                         -
loaded after the run: pdf, sql; still dormant: 6 of 8

'Check that the digital signature is legitimate.': substring match fires git: True; word match fires git: False
```

Two details in the listing are the ones a first implementation gets wrong. Trigger matching is on whole words, because the obvious `any(t in task for t in triggers)` fires on any containing string: the last line shows a `git` trigger firing on "digital" and "legitimate". And `setup()` is guarded by `self.loaded`, because an unguarded call runs on every turn whose text happens to match, not once.

The third mistake is visible only in the output: the middle column changes on four of the six turns. It is the subject of the next section.

---

## 6. Append, never swap

`tools_for` returns a *different list* on every turn where the skill set changes, and the tool block sits at the very front of the cached prefix. Anthropic's "Tool use with prompt caching" documentation (consulted October 2026) states the rule: "The cache follows a prefix hierarchy" of tools, then system, then messages, and "a change at one level invalidates that level and everything after it"; modifying tool definitions invalidates the entire cache, tools, system and messages together.

That collides with the rest of the series. [Post 03](../03-the-agent-loop/index.md) shows the re-sent prefix, rendered as tools then system prompt then messages, as exactly what prompt caching exploits, and `ctx-005` gives the economics of a cached stable prefix. A naive disclosure registry rewrites that prefix on purpose every time a skill triggers.

The fix is one line of design: **append, never swap.** Keep the base tools in the cached prefix, mark everything else deferred, and let a newly discovered schema arrive *appended to the conversation* rather than swapped into the tool block. The vendor implementation has this property: when the model finds a deferred tool, its definition "is appended inline as a `tool_reference` block in the conversation history", and "The prefix is untouched, so prompt caching is preserved." In the registry that is the difference between returning a new tool list and returning something to append, the method that follows `tools_for` in the same file:

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

`snippets/prefix_cache.py` puts token counts on the difference. It renders the six-turn run three ways (eager, with all 13 skill schemas in the tool block; swap, with `tools_for`; append, with `disclose`), as tools then system then messages, and counts tokens with `tiktoken`'s `o200k_base` encoding as a stand-in for the provider's tokenizer, so every count is illustrative. A request reuses the cache only when the previous request is an exact prefix of it; otherwise it reuses nothing, as the documentation says. Reused tokens are billed at 0.1 times the base input rate and the rest written at 1.25 times, the five-minute cache multipliers on Anthropic's pricing page (consulted October 2026). It prints:

```text
skill schemas: 13, 79 tokens each on average; catalogue lines: 8, 13 tokens each

turn   eager: sent  reused    swap: sent  reused    append: sent  reused
   1        1,427       0            405       0            405       0
   2        1,454   1,427            662       0            667     405
   3        1,480   1,454            458       0            693     667
   4        1,504   1,480            621       0            861     693
   5        1,528   1,504            506       0            885     861
   6        1,553   1,528            531     506            910     885

eager   sent  8,946  reused  7,393 (83%)  billed as  2,681 token-equivalents
swap    sent  3,183  reused    506 (16%)  billed as  3,397 token-equivalents
append  sent  4,421  reused  3,511 (79%)  billed as  1,489 token-equivalents
swap / append billed: 2.28 times
```

Swapping sends the fewest tokens of the three and costs the most: on turns 2 to 5 the tool block changed, so the cache was rebuilt from nothing four times, and the run is billed 2.28 times what appending costs. The chart below draws the reused column of each strategy.

![A line chart of tokens reused from the cache on each of six turns. Eager loading reuses about 1,400 to 1,500 from turn 2 on, billed 2,681; append rises from 405 to 885, billed 1,489; swap reuses nothing on turns 1 to 5 and 506 on turn 6, billed 3,397.](diagrams/02-append-vs-swap.svg)

*Every change to the tool block resets the cache to nothing; appended schemas leave everything before them reusable.*

Appending sends a little more each turn, because the disclosed schemas stay in the history, and reuses nearly all of it. Eager loading caches perfectly too, but it carries all 13 schemas from the first turn; on this short run that costs more than appending, and the gap widens as the catalogue grows. The run is small: Claude Sonnet 4.6 caches nothing under 1,024 tokens (prompt caching page, consulted October 2026), so each request here stands for a prefix padded past that minimum; the comparison, not the size, is the point.

A consequence is easy to mistake for a bug: once disclosed, a skill stays disclosed for the rest of the run. That is correct. Un-disclosing it would mean editing the prefix, which is a swap under another name, and one extra schema in the window costs far less than a cache miss.

---

## 7. Skill registries and distribution

Skills are *distributable*. A skill is a self-contained folder, so a registry can version and share skills across projects as a package manager shares libraries, and the format is portable: Anthropic says skills can be used across Claude apps, Claude Code and its application programming interface (API) (Anthropic, 16 October 2025), and it has since published Agent Skills as an open standard.

Distribution is also where three problems start.

- **Naming.** A flat catalogue assembled from several sources collides: two `search` tools and three `create_ticket` variants confuse trigger matching and the model alike. The tool search documentation's advice is consistent namespacing, a prefix "by service or resource" (`github_`, `slack_`), so one search matches a coherent group and the name carries its provenance.
- **Trust.** An installed skill's scripts run inside the agent's own environment. A skill is a software supply-chain dependency with none of the isolation of a separate server process, so packaging is a security decision as well as an ergonomic one, and it is a concrete reason a team may prefer an MCP server to a skill for the same function.
- **Versioning.** Because the description is the matching surface (section 1), editing it changes *when the skill fires*, not just how it reads. Descriptions are interface, and an edit to one is a breaking change even when the code beneath is untouched.

None of this argues against distribution; it argues for reviewing an installed skill as any other dependency is reviewed ([post 14](../14-permissions-sandboxes/index.md)).

---

## 8. MCP: a tool behind a process boundary

Skills keep a capability's schema out of the window until needed. MCP does something different for its *code*: the tool lives in a separate server that the harness talks to over a standard protocol, so its implementation and dependencies never run in the harness's process.

`ctx-015` covers MCP from the token side, and the `mcp` series covers the protocol itself: `mcp-002` the architecture and `mcp-011` the host's tool loop. The runtime recap is the triangle of the specification (modelcontextprotocol.io, revision 2026-07-28):

- **Host:** the harness, a large language model (LLM) application, in the specification's words one of the "LLM applications that initiate connections"; it runs the loop and decides when to call a tool.
- **Client:** a connector inside the host, one per server, that speaks the protocol: JSON-RPC 2.0 (JavaScript Object Notation remote procedure call) messages over a transport (stdio or Streamable HTTP, the Hypertext Transfer Protocol, `mcp-004`).
- **Server:** a separate process or remote service that *owns* the tool: it advertises what it offers and executes calls.

The decisive property is the boundary: because the server runs elsewhere, the **same server works with any host**. Swap the model or the harness and the `create_ticket` server is unchanged; MCP decouples model choice from tool choice.

One clarification, because it is easy to overstate. MCP does **not** by itself keep a server's tool *schemas* out of the window. "Most MCP clients load all tool definitions upfront directly into context", as Anthropic's "Code execution with MCP" (Adam Jones and Conor Kelly, 4 November 2025) puts it: the client calls the server's `tools/list` and advertises every returned schema to the model, exactly like a local tool. Keeping those schemas out is progressive disclosure applied to the MCP catalogue, not a free property of the protocol. What the process boundary buys is that the tool's *implementation* stays out of the process, not that its *interface* stays out of the context.

The remedy has two shipped shapes. The first is deferred loading plus a search step over the catalogue: section 3's meta-tool, productised, with section 6's append property built in. The second is stranger: stop presenting a server as a tool list at all, and present it as **code on a filesystem**, one directory per server and one file per tool, so the model reads a tool's definition only when it opens the file. The same article reports one workflow falling "from 150,000 tokens to 2,000 tokens", "a time and cost saving of 98.7%", on that change, a reported figure for one workflow, with the reasoning stated plainly: "Models are great at navigating filesystems." It is the filesystem-as-context argument of [post 08](../08-state-filesystem-git/index.md), arriving from the opposite direction.

---

## 9. Dispatching an MCP call inside the loop

Inside a single turn, an MCP tool call is the act step of [post 03](../03-the-agent-loop/index.md) with two extra hops: through the client, and over the transport to the server. The figure below draws the six steps.

![One loop turn in six steps across a process boundary: the model passes a tool call to the MCP client, which sends a JSON-RPC tools/call request to the server process, where create_ticket runs; the result returns, passes a validation gate and becomes the next observation, and a timeout or a wrong shape becomes an error observation.](diagrams/03-mcp-dispatch.svg)

*The tool's code runs in another process; only its result crosses back, and the harness checks it before the model sees it.*

The current revision describes the base protocol as "Stateless, self-contained requests" with "Per-request capability negotiation", so a dispatch holds no long-lived session: the host lists a server's tools, caches the catalogue, and re-lists when the list may have changed. The dispatch in `snippets/mcp_dispatch.py` is a request and a check on what comes back; its stub client prints the frame a real client would write and returns a canned result in the specification's shape:

```python
def validate(result: dict) -> dict:
    if not isinstance(result, dict) or not isinstance(result.get("content"), list):
        return {"error": "malformed tool result"}
    if result.get("isError"):
        return {"error": "tool reported an error", "content": result["content"]}
    return result

def call_mcp_tool(client, name: str, arguments: dict) -> dict:
    try:
        result = client.request("tools/call", {"name": name, "arguments": arguments})
    except (TimeoutError, ConnectionError) as exc:
        return {"error": f"{name} unavailable: {exc}"}   # a corrigible observation, not a crash
    return validate(result)   # server output is untrusted input
```

Running `uv run python posts/07-skills-mcp-runtime/snippets/mcp_dispatch.py` from the series root prints the frame, the observation, a server that times out, and a result of the wrong shape:

```text
client sends:   {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "create_ticket", "arguments": {"title": "Disk full on web-03"}, "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {}}}}
observation:    {"resultType": "complete", "content": [{"type": "text", "text": "TICKET-4417 created"}], "isError": false}
server down:    {"error": "create_ticket unavailable: no response in 30 s"}
bad result:     {"error": "malformed tool result"}
```

Two runtime concerns belong to the harness, not the protocol:

- **Validation still applies.** The result comes back over the wire as data; it is checked before it reaches the model, as [post 06](../06-tools-bash-code/index.md) validates the call going out. A misbehaving server is an untrusted input, and a tool that reports `isError` is an error observation, not a success.
- **Failure is an observation, not a crash.** A server that times out, disconnects or errors surfaces as "create_ticket unavailable", which the model can react to, never as an exception that kills the loop.

And the security note that MCP makes unavoidable. A tool result is text that re-enters the context window, so a compromised or hostile server is an **indirect prompt-injection** vector. The attack is not hypothetical: Invariant Labs (26 May 2025) showed an issue filed in a *public* repository that could "hijack a user's agent" and "coerce it into leaking data from private repositories", against an agent using the official GitHub MCP server and asked only to look at open issues. Invariant places the flaw in the agent system, not in the server's code. The untrusted text is not only the result. A server's tool *descriptions* arrive over the same `tools/list` and land in the window before any call is made, the tool poisoning Invariant Labs described on 1 April 2025. Both halves are the subject of [post 14](../14-permissions-sandboxes/index.md).

---

## 10. Keeping results out of the window, not just schemas

The dispatch figure draws the default: every result crosses back into the window as an observation. Three sequential calls mean three turns, and the two intermediate results are read once and then carried in the transcript for the rest of the run. The alternative is to let the model write a short script that calls the tools, and run it. Anthropic's "Programmatic tool calling" documentation (consulted October 2026) states the property: "Tool results from programmatic calls are not added to Claude's context"; only the final output of the code is. Token cost then scales with the size of the *answer* rather than the *data*: fetching two thousand rows to compute one total costs one number instead of two thousand rows (an illustrative case).

The effect follows the shape of the workload, which makes it a decision rather than a default. The same page reports Anthropic's internal evaluations: on a 75-tool project-management agent benchmark, programmatic calling "reduced billed input tokens by roughly 38%" with no change in task accuracy, while on τ²-bench, whose turns make one or two sequential calls, it "left scores unchanged and cost roughly 8% more". Both are reported figures. The technique pays when a turn fans out across many calls or large intermediate results, and charges a small premium when it does not.

One restriction matters here: the page lists tools from Anthropic's MCP connector among those that cannot be called this way, a further argument for the filesystem presentation of section 8. The same instinct applied to one oversized output is the offloading of [post 09](../09-context-management-loop/index.md), which writes the output to disk and returns a pointer.

---

## 11. Curate the catalogue, not just the window

Progressive disclosure removes the *per-turn* tax, not the judgement about *what belongs in the catalogue*. Two hundred skills are still a discovery problem and still code to maintain and secure. The curation discipline of [post 06](../06-tools-bash-code/index.md) applies one level up: **the fewest skills that cover the space**, each earning its place.

The rule of thumb: reach for a *skill* when a capability is cohesive, reusable and occasionally needed (PDF handling); for a *general tool* such as bash when the capability is better *composed* than packaged; and for an *MCP server* when the capability belongs to a system the team does not own or does not want in its process (the company ticketing system). All three are capability on demand, at three distances from the loop.

| Mechanism | Keeps out of window | Keeps out of process | Prompt cache | Characteristic failure |
|---|---|---|---|---|
| General tool | nothing | nothing | sits in the stable cached prefix | a wrong composition the model must debug |
| Skill | its schemas, until loaded | nothing: it runs in the agent's own environment | breaks the prefix if swapped, survives if appended (section 6) | never triggers, or triggers on everything |
| MCP server | nothing by itself | its code and dependencies | the same append-or-swap rule, plus a catalogue that can change | timeout, disconnect, or a hostile description (section 9) |

Read down the window column and only the skill removes anything; read down the process column and only the MCP server does. A team that adopts MCP expecting a smaller context has confused the two columns, and a team that packages a skill expecting isolation has confused them the other way. The one column where the three behave the *same* is the cache column, which is why section 6 is a rule about disclosure in general rather than about skills in particular.

---

## 12. Make it run

The three snippets run offline from the series root in the root environment (`tiktoken` for the counts, the standard library otherwise):

```bash
uv run python posts/07-skills-mcp-runtime/snippets/skill_registry.py
uv run python posts/07-skills-mcp-runtime/snippets/prefix_cache.py
uv run python posts/07-skills-mcp-runtime/snippets/mcp_dispatch.py
```

The first prints section 5's turn table, the second section 6's token counts, the third section 9's frame and observations. `prefix_cache.py` imports `SKILLS` and `TASKS` from `skill_registry.py`, so a changed catalogue or run changes both tables.

---

## 13. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **Substring triggers.** A document task about a "legitimate digital signature" loads the `git` skill; the window carries schemas nobody asked for, and the model calls `git_log` on a PDF task.
- **A tool list rebuilt every turn.** The usage figures show cache reads near zero on every turn a skill changes, and the bill rises although fewer tokens are sent.
- **Un-disclosing a skill to save room.** Removing a schema after its task is done is a swap under another name, with the same cache miss on the next turn.
- **Expecting MCP to shrink the context.** After a few servers are connected, the first call's input tokens jump by the size of every `tools/list` schema.
- **A server failure raised as an exception.** A timeout ends the run with a traceback instead of reaching the model as "unavailable", where it could have tried another path.
- **A description edited as prose.** A skill that loaded yesterday never loads today, because its description no longer contains the words tasks use.

---

## Common pitfalls

1. **Loading every tool upfront.** Past ten tools or 10k tokens of definitions, eager loading taxes every turn and, further out, degrades selection; disclose progressively (sections 3 and 4).
2. **Swapping the tools block when skills change.** Any change to the tool definitions invalidates tools, system and messages together; append discovered schemas instead (section 6).
3. **Advertising full schemas in the catalogue.** The always-loaded catalogue is names and one-line descriptions; schemas in it pay the tax disclosure was meant to avoid (section 1).
4. **Assuming MCP keeps schemas out of the window.** A connected server's schemas are advertised like local tools; keeping them out is still progressive disclosure's job (section 8).
5. **Trusting an MCP server's output or its descriptions.** Both are untrusted text re-entering the window, and the descriptions arrive first, before any call (section 9).

---

## Further reading

- Anthropic, "Introducing Agent Skills" (16 October 2025): skills as folders of instructions, scripts and resources, loaded when needed, across Claude apps, Claude Code and the API.
- Barry Zhang, Keith Lazuka and Mahesh Murag, "Equipping agents for the real world with Agent Skills" (Anthropic Engineering, 16 October 2025): the levels of disclosure, and scripts that run without entering the window.
- Anthropic, "Tool search tool" documentation (consulted October 2026): the 55k-token setup, the 30 to 50 tool cliff, and the thresholds.
- Anthropic, "Tool use with prompt caching" documentation (consulted October 2026): the prefix hierarchy, and why deferred loading preserves the cache.
- Anthropic, "Programmatic tool calling" documentation (consulted October 2026): intermediate results kept out of the window, and the two benchmarks behind section 10.
- Adam Jones and Conor Kelly, "Code execution with MCP" (Anthropic Engineering, 4 November 2025): clients that load every definition upfront, and the filesystem presentation.
- Model Context Protocol specification (modelcontextprotocol.io, revision 2026-07-28): host, client, server, JSON-RPC 2.0, and stateless requests.
- Invariant Labs, "GitHub MCP Exploited" (26 May 2025): the worked indirect-injection incident of section 9.
- Gan and Sun, "RAG-MCP" (6 May 2025): retrieval against a full tool list, measured.
- ai-boost, "awesome-harness-engineering" (2026): the Skills and MCP heading among its design primitives.
- `ctx-015`: tools and MCP from the token side; `ctx-029`: an MCP server built end to end, the server side of the boundary this post views from the host.
- `mcp-002` and `mcp-011`: the protocol's architecture, and the host's tool loop and permissions.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 08 - State and the filesystem: durable memory and git as state](../08-state-filesystem-git/index.md):** where a loaded skill writes its intermediate work, durable state on disk and under git.
- **[Post 11 - Verification loops: tests, self-critique, fail-fast](../11-verification-loops/index.md):** the first post of Part III, which checks the work the extended tool surface makes possible.
