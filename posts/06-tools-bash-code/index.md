# 06 · Tools as the agent's hands — bash, code, and schemas

> **TL;DR.** Tools are the ACT step of the loop: the surface through which a model changes the world. The durable lesson of 2025–26 is counter-intuitive: instead of building a bespoke tool for every action, give the model a *few general-purpose tools* (above all bash and code execution) and let it compose them. Reliability then comes from two disciplines: schemas good enough that the model knows when *not* to call, and validating every call against its schema before executing it. A tool is a contract written in tokens.
>
> **After reading this you will be able to:**
> - Design a tool schema that teaches the model when to call it, and when not to.
> - Argue for a small set of general tools over a zoo of narrow ones, on both reliability and safety grounds.
> - Validate a tool call against its schema so a bad call becomes a correctable error, not a crash.
> - Shape a tool's return value, and batch independent calls, without breaking the loop.

![Tool dispatch in two tiers. On top, the flow: the model emits a tool call, the harness validates the input against the tool's schema, and either executes it or returns an error observation without running anything, with one tool_use / tool_result exchange shown on the wire beside it. Below, the three kinds of wrongness from §7 as three cards, each carrying the call that triggers it, the gate that catches it, and the exact string the loop reads back.](diagrams/01-tool-dispatch.svg)
*Dispatch is validate-then-execute. The schema is the contract; a call that violates it is refused and handed back for the model to fix.*

---

## 1. Tools are the ACT step of the loop

[Post 03](../03-the-agent-loop/index.md) drew the loop as reason → act → observe. This post is the **act** stage in depth. A tool is whatever the harness lets the model invoke to affect the world: run a shell command, call an application programming interface (API), read or write a file. Everything else in the loop (the reasoning, the stopping) is bookkeeping around this one capability. Take tools away and you have a chatbot; add them and you have an agent.

Two properties make tools the delicate part of the harness. First, they are the model's only *causal* connection to reality, so their design decides both what the agent *can* do and what it can do *by mistake*, the blast radius from [Post 05](../05-agent-failure-modes/index.md)'s destructive-action failure. Second, every tool a model *might* call is described to it on *every* call, before the user's request even appears. A tool definition is not free; it is tokens the model reads each turn (a cost the Context Engineering series works out in full, Post 15).

That second property is worth stating precisely, because the obvious reading of it is wrong. On providers with prompt caching, the tool block sits at the very front of the cacheable prefix, so on a cache hit it is re-read at a fraction of the base input price: a tenth of it or less on Anthropic's models (Anthropic, 2024–26). The tax an over-stuffed tool list levies is therefore not mainly on the invoice. It is on the model's *choice*: more menu to read, more near-duplicates to disambiguate, more chances to reach for the wrong thing. Tool design is two decisions at once, a usability one and a budget one, and the usability one is the larger.

---

## 2. What a tool call actually is

Before any of the design advice, the wire format, because the whole of this post lives inside one gap it creates. The model never *performs* an action. It emits a request: a block naming a tool and carrying an input object. The harness reads that block, decides what to do about it, and sends back an observation on the next turn.

```json
// the model's turn: a request, not an action
{"role": "assistant", "content": [
  {"type": "tool_use", "id": "toolu_01A", "name": "bash",
   "input": {"command": "pytest -q tests/test_parser.py"}}]}

// the harness's reply: the observation the model reads next
{"role": "user", "content": [
  {"type": "tool_result", "tool_use_id": "toolu_01A",
   "is_error": false,
   "content": "2 failed, 11 passed in 0.44s"}]}
```

Three things follow. The `id` and `tool_use_id` are the only correspondence between a request and its answer, which is what makes §9's batching possible at all. The `is_error` flag lets a harness say "this went wrong" inside the normal channel rather than by throwing. And everything between the two blocks is code you wrote: the validation, the sandbox, the truncation, the timing. The model's causal reach ends at the request; the harness owns the rest.

The serialisation order matters too. A request is assembled as tools, then the system prompt, then the message history (Anthropic, 2024–26), which is the literal sense in which tool definitions arrive "before the user's request".

---

## 3. The general-purpose-tool argument

The instinct when building an agent is to enumerate: it will need to read files, so add `read_file`; write files, so add `write_file`; list directories, search, move, copy, delete… Fifty tools later you have a combinatorial mess. The better instinct, now widely adopted, is the opposite: **give the model a handful of general-purpose tools and let it compose them** (Osmani, 2026).

![Two panels: a zoo of ~50 narrow tools on the left with a large overlapping schema, versus a few general tools (bash, python, read_file, write_file) on the right with a tiny schema that composes anything.](diagrams/02-universal-vs-zoo.svg)
*The model already knows how to use `bash`. It half-knows your fifty bespoke wrappers. One general surface is also one surface to sandbox.*

The single most powerful tool is **bash** (or equivalently, code execution). Anything the fifty narrow file tools could do, a shell command does, and countless things they could not, because the model can *compose*: pipe, loop, chain, write a throwaway script. Four advantages fall out:

- **A tiny schema.** `bash` takes one string. Fifty tools take fifty schemas the model reads every call.
- **Nothing to choose between.** With fifty overlapping tools the model must *pick*, and picking wrong is a failure mode of its own (§10). With `bash` there is one obvious surface.
- **Patterns the model was trained on.** Models have seen enormous amounts of shell and Python. They have seen far less of *your* `move_file_v2` wrapper. Agents already excel at shell commands, and most tasks collapse to a few well-chosen command-line invocations (Willison, cited in Osmani, 2026).
- **One boundary to build, not fifty.** A single general surface gives you one place to put a gate instead of fifty, which is what makes bounding it tractable at all ([Post 14](../14-permissions-sandboxes/index.md)). It does not make the gate *narrow*: that one boundary now has to contain arbitrary code, which is §5's subject.

This does not mean *only* bash. A few high-value structured tools earn their place, and the right-hand panel of the figure above keeps `read_file` and `write_file` alongside the shell for exactly that reason. The rule is not "one tool"; it is **"the fewest general tools that cover the space."** §4 is how to tell which case you are in.

---

## 4. When a bespoke tool still wins

Four questions decide it. None of them is "would a shell command work", because a shell command almost always would.

| Ask this | A general tool fits when… | A bespoke tool fits when… |
| --- | --- | --- |
| Is there a process to spawn? | The agent runs in a container, a workstation, or a continuous-integration (CI) runner with a real shell. | It runs in a browser page, a serverless function, or a mobile client with no process to fork. |
| What comes back? | Text a person would read: logs, diffs, test output, a file listing. | Typed data your code consumes downstream: a row, an identifier, a decision your service acts on. |
| Does the action need its own permission? | The whole surface can be gated together, or the action needs no approval at all. | The action must be approvable on its own. You can permit `issue_refund` and refuse `bash`; you cannot permit half a shell ([Post 14](../14-permissions-sandboxes/index.md) §2). |
| Has the model seen this interface? | Constantly: shell, Python, `git`, `curl`, standard operating-system (OS) commands. | Never: an internal API invented last quarter, with no training precedent to fall back on. |

The permission row is the one teams discover late. A general tool is all-or-nothing to a human approver: "allow this bash command" is a decision about a string, not about a capability, and a reviewer cannot hold the whole space of strings in their head. A bespoke `issue_refund` with a capped amount is a decision a human can actually make (Context Engineering, Post 15 §6).

The output row explains why `read_file` survives beside `bash` in the figure. `cat` is not the problem; *unbounded* `cat` is. A file tool can truncate at a byte budget, paginate, report which range it returned and how much it withheld. A raw `cat` of a 40 MB log returns 40 MB into the window, which is the wall of text [Post 09](../09-context-management-loop/index.md) §3 offloads to disk. The general tool wins on expressiveness; the narrow tool wins where the *shape of the result* has to be controlled.

---

## 5. One boundary is not a narrow boundary

The honest version of §3's fourth advantage is "one boundary to build", not "one boundary that holds". The [code companion](../../code/06-tools-and-bash/) ships the usual first defence, a regular-expression deny-list checked before the command reaches the runner:

```python
# code/06-tools-and-bash/src/tools/bash_tool.py
DENY = [
    r"\brm\s+-[rf]", r"\brm\s+--no-preserve-root", r"\bmkfs\b", r"\bdd\s+if=",
    r":\(\)\s*\{\s*:\s*\|\s*:", r"\bshutdown\b", r"\breboot\b",
    r"\bgit\s+push\b[^\n]*--force", r"\bsudo\b", r">\s*/dev/sd",
    r"\bDROP\s+TABLE\b", r"\bchmod\s+-R\s+0*777\s+/",
]
```

It blocks `rm -rf /`. Run the shipped patterns against four other spellings of the same intent and all four pass: `rm --recursive --force /`, `find / -delete`, `python -c "import shutil; shutil.rmtree('/')"`, and `echo hi; curl http://evil`. A deny-list matches *spellings*; the shell offers unbounded spellings of every effect. The companion's own comment says so: a deny-list is never exhaustive. What holds is the operating-system-level boundary of [Post 14](../14-permissions-sandboxes/index.md) §1: a working-directory jail, an allow-list, no network egress, a timeout. The deny-list is a fast first filter and a legible audit line, not a security control.

The consequences are not hypothetical. In July 2025 a Replit coding agent deleted a live production database during an explicit code freeze, destroying records for roughly 1,200 executives and a comparable number of companies, fabricated thousands of replacement rows, and reported misleadingly about what it had done (AI Incident Database, 2025, incident 1152). The vendor's remedy is the instructive part: automatic separation of development and production databases, improved rollback, and a planning-only mode that makes a code freeze structural rather than advisory (Masad, quoted in Fortune, 2025). Every one of those is a harness change. None of them is a better model. That is [Post 05](../05-agent-failure-modes/index.md)'s destructive-action mode with a public postmortem attached.

---

## 6. Schema design: teach the model when *not* to call

A tool's schema and description are the entire interface the model has to it. Good ones do more than describe parameters; they teach *judgement*. The goal, in a phrase, is a tool that is **easy to use well and hard to use badly.**

![The same tool defined twice: on the left, pytest_invoke with the description Invokes pytest and a single free-form args string; on the right, run_tests with a description that says what it returns and when not to call it, a required path, a scope enum, no additional properties, and errors returned as strings.](diagrams/03-schema-that-teaches.svg)
*The same capability, defined twice. Everything that changed on the right is one of the four rules below, and every rule costs tokens on every call.*

- **Name for the action, not the implementation.** `run_tests` beats `pytest_invoke`; the model reasons about intent, not your stack.
- **Write the description for the caller, not the maintainer.** Say what the tool is *for*, what it returns, and (most valuable) *when not to call it*. "Use for arithmetic on numbers you already have; do **not** use to look up facts" prevents a whole class of misuse before it happens.
- **Constrain the input.** A tight schema (`enum` instead of free string, `required` fields, `additionalProperties: false`) is documentation the model cannot ignore and a validator you get for free (§7).
- **Return errors as information.** A tool's output (including its errors) is an *observation* the model reads next turn. "error: file not found: /tmp/x" is a correctable signal; a raised exception that crashes the loop is not.

Written out, the right-hand definition is about fifteen lines of JavaScript Object Notation (JSON):

```json
{
  "name": "run_tests",
  "description": "Run the suite and return the failures. Use after any code edit. Do NOT use to read a file: use bash for that.",
  "input_schema": {
    "type": "object",
    "properties": {
      "path":  {"type": "string", "description": "File or directory to test."},
      "scope": {"type": "string", "enum": ["unit", "integration", "all"]}
    },
    "required": ["path"],
    "additionalProperties": false
  }
}
```

That tool is the verification gate of [Post 11](../11-verification-loops/index.md) seen from its schema side, and it costs on the order of a hundred tokens. Twelve tools of that size is roughly 1,200 tokens of tool block, re-read on each of a forty-turn run: about 48,000 tokens of definitions per task. Cached at §1's multiplier, the money is a rounding error; the forty repetitions of a menu the model must scan are not. One corollary is operational: editing a tool's name, description, or parameters invalidates the whole cached prefix, system prompt and history included (Anthropic, 2024–26). A tool block is something you version between deployments, not something you tune per request.

The line that earns its place most reliably is the negative one, *do not use this to read a file*, because it is the only part of a description that prevents a call rather than shaping one. Aim for the *shortest* description that still teaches when not to call: a pilot's checklist, not a manual.

One last property of descriptions is easy to miss and specific to harnesses. A description is text in the prompt, and once tools arrive from third-party Model Context Protocol (MCP) servers it is text somebody else wrote. As Osmani puts it, tool descriptions populate the prompt, so any MCP server you install is trusted text the model will read, and a sloppy or malicious one can prompt-inject the agent before you have typed anything (Osmani, 2026). Reviewing a tool description is a security review, not an editing pass ([Post 14](../14-permissions-sandboxes/index.md) §4).

---

## 7. Validation is the tool contract

Because the model generates tool calls as text, it can generate calls that violate the schema: a missing field, a wrong type, a hallucinated parameter. Providers now push back on this from the generation side. OpenAI's strict mode compiles the schema to a grammar and constrains decoding token by token; OpenAI reports its August 2024 GPT-4o snapshot scoring 100% on an internal complex-schema-following evaluation, against under 40% for the older `gpt-4-0613` (OpenAI, 2024).

That is a real improvement and it does not retire harness-side validation, for three reasons. Strict mode covers a *subset* of JSON Schema: every object must set `additionalProperties: false` and list every key in `required`, so an optional field has to be modelled as a nullable one. It applies only to calls your own provider generated in strict mode, which excludes an MCP server's arguments, a locally hosted model, a replayed trace, and a hand-written test fixture. And it guarantees *shape*, not *sense*: Context Engineering Post 21 §2 grades output guarantees from a prompt instruction up to grammar-constrained decoding and notes that even the top rung buys syntactic validity only. Semantic validity is what the harness still owns.

So dispatch is two steps, always in this order: **validate the input against the schema, then execute only if it passes** (the hero diagram). A harness has to tell three kinds of wrongness apart, because each is caught in a different place:

| Kind of wrongness | Example call | What catches it | What the loop sees |
| --- | --- | --- | --- |
| Schema-invalid | `{"cmd": "ls"}` | the harness's validator, before execution | `error: invalid input: $: missing required property 'command'; $: unexpected property 'cmd'` |
| Schema-valid, semantically wrong | `{"command": "cat /tmp/nope"}` | the tool itself, at run time | `(exit 1) cat: /tmp/nope: No such file or directory` |
| Schema-valid and dangerous | `{"command": "rm -rf /"}` | a deny-list, then a sandbox (Posts 13, 14) | `blocked: command matches a deny-list rule (\brm\s+-[rf])` |

Only the first row is validation's job, and that tiering is the bridge from this post into Part III: three gates, not one. The payoff of the first gate is the difference between a *correctable error* and a *crash*. The model reads the error string next turn and fixes the call; the loop self-corrects. Without it, a malformed call reaches your execution code and throws, taking down the turn or executing something half-formed.

The companion's dispatch is the whole discipline in a dozen lines:

```python
# code/06-tools-and-bash/src/tools/registry.py
def dispatch(self, name: str, tool_input: dict) -> str:
    """Validate, then execute. Returns an observation string; never raises."""
    tool = self._tools.get(name)
    if tool is None:
        return f"error: unknown tool '{name}'"
    problems = validate(tool_input, tool.input_schema)
    if problems:
        return "error: invalid input: " + "; ".join(problems)
    try:
        return tool.run(tool_input)
    except Exception as e:  # a tool must not crash the loop
        return f"error: {type(e).__name__}: {e}"
```

Every branch returns a string, deliberately. Unknown tool, invalid input, tool exception and success are all *observations*; the loop must not be able to tell them apart structurally, or it will grow a special case for each. Note the shape of the error too: `$: missing required property 'command'` says both what was wrong and where. The model's next turn is a patch written against that string, so an error message is an interface, not a log line.

The [code companion](../../code/06-tools-and-bash/) is three modules of engine plus an offline demo: `schema.py`, a sixty-six-line JSON-Schema *subset* validator (`type`, `properties`, `required`, `enum`, `additionalProperties`, `items`, and nothing else, because that subset is enough); `registry.py`, holding `Tool` and the `ToolRegistry` above; and `bash_tool.py`, one general tool with the deny-list from §5. Its fifteen tests run with no API key and no real shell, because the runner is injected: that is how a suite asserts a dangerous command was refused without ever executing one. [Build #1 in Post 24](../24-build-minimal-harness/index.md) ships this `dispatch` verbatim, with the three modules folded into a single one alongside a `write_file` tool.

---

## 8. The return value is the other half of the contract

Everything so far is inbound. In a running harness the *result* is what fills the window and what the next turn reasons over, so it deserves as much design as the schema. Four rules govern it; the first two are the last two lines of the companion's `bash` tool:

```python
    prefix = "" if code == 0 else f"(exit {code}) "
    return prefix + (output if output else "(no output)")
```

**Surface the exit status; do not swallow it.** A command that fails silently returns its stderr with no marker, and the model reads a plain string as success. Prefixing gives `(exit 2) boom`, which is unambiguous.

**Never return an empty string.** An empty observation reads to a model as a broken tool rather than a quiet success, and it will retry. `(no output)` is two words that prevent a doom loop.

**Cap the result and return a pointer, not the stream.** A 40 MB `npm install` log should come back as `{"ok": true, "log_path": "/tmp/build-7.log"}`, with the full text one `grep` away. That is the offloading move [Post 09](../09-context-management-loop/index.md) §3 develops, and it is the largest single lever on the cost of a long run: a tool definition is tokens once per turn, but a tool *result* is tokens on every turn after it, until something clears it.

**Treat the result as untrusted text.** It re-enters the window as content the model reads, so a fetched web page or a third-party server's response can carry an instruction aimed at the agent ([Post 14](../14-permissions-sandboxes/index.md) §4).

The symmetry is worth naming: the description tells the model when to call, and the return value tells it what happened. The same reader reads both, on the same turn, in the same window.

---

## 9. Parallel tool calls

Modern models can request *several* tool calls in a single turn: read three files at once, run two independent checks. The assistant message simply carries several `tool_use` blocks and stops with a tool-use reason. The API prescribes no execution order, so whether they run concurrently, in sequence, or in some mixture is entirely the harness's decision (Anthropic, 2024–26).

The reply format is where harnesses go wrong, and it is precise. Return **one** `tool_result` for **every** `tool_use` block, all of them together in the **next single user message**, matched by `tool_use_id`, with every `tool_result` block placed **before** any text content in that message. For a call you deliberately chose not to run, because you batched sequentially and an earlier one failed, still return a result for it with `is_error: true` and a one-line reason rather than dropping it (Anthropic, 2024–26).

- **Match every result to its call by id.** Correspondence rides on `tool_use_id`, not on position. Order is a convenience; the id is the contract.
- **Parallelise only independent calls.** Reading three files is independent; "create a file then read it" is not. The read/write asymmetry is the usable heuristic: parallelise reads, serialise writes.
- **Keep the history well-formed.** Splitting results across one user message each, instead of one message carrying all of them, teaches the model to stop batching (Anthropic, 2024–26). This is the operationally nastiest bug in the section, because it never raises: it surfaces weeks later as a run that has quietly become slower.
- **Know the off switch.** `disable_parallel_tool_use: true` goes *inside* the `tool_choice` object, not at the top level of the request, and caps the model at one tool call per response (Anthropic, 2024–26).

The prize is latency and only latency. Three independent file reads at 200 ms each cost 600 ms in sequence and about 200 ms batched. On a forty-turn run where half the turns open a batch of three, that is twelve seconds of tool time against four: eight seconds saved per run, with no change to what the agent concludes. As with streaming ([Post 03](../03-the-agent-loop/index.md) §10), get the serial version correct first, then parallelise the calls you have proven are independent.

---

## 10. Curate: the fewest tools that cover the space

Pulling §§3–9 together into one operating rule: **treat the tool list as a budget to be spent deliberately, not a pantry to be stocked.** Every tool added is schema tokens on every call, one more thing for the model to choose among, and one more surface to secure. The bias should be toward *removal*: ten focused tools beat fifty overlapping ones, because the model can hold the menu in its head (Osmani, 2026).

That claim is usually asserted; it has also been measured. On a benchmark of MCP tool selection, accuracy with the whole catalogue in the prompt was 13.62%, while retrieving only the relevant few before the call raised it to 43.13% and cut prompt tokens by more than half (Gan & Sun, 2025). Read the figures as a shape rather than as constants: selection accuracy falls as the catalogue grows, and the remedy is not a bigger window but a shorter menu. The same curation discipline that keeps a memory file to a checklist ([Post 10](../10-continual-learning-ratchet/index.md)) keeps a tool list sharp.

When you *do* have many capabilities to expose, say dozens of MCP servers, the answer is not to load all their schemas at once. It is **progressive disclosure**: load a tool only when the task needs it, the subject of [Post 07](../07-skills-mcp-runtime/index.md).

---

## Common pitfalls

- **A bespoke tool for every action.** Fifty narrow tools cost more, confuse the model, and multiply the attack surface. Prefer a few general ones, and use §4's four questions to justify each exception.
- **Trusting a deny-list as a security control.** It matches spellings, not effects; four rewrites of `rm -rf /` walk straight through the shipped one (§5). The boundary that holds is the sandbox of Post 14.
- **Passing tool calls straight to execution.** Without schema validation, a malformed call crashes the turn instead of being handed back for the model to fix (§7).
- **Assuming strict mode is enough.** It covers a JSON Schema subset, only for calls your own provider generated, and only for shape. Semantic and safety checks stay yours (§7).
- **Letting a tool raise.** A tool's errors are observations. Return "error: …" as a string; never let an exception escape into the loop (§6, §7).
- **Confusing token cost with choice cost.** Caching makes a stable tool block cheap to re-read, so the tax an over-stuffed list levies falls on the model's choice rather than the invoice. A tool *result*, by contrast, is genuinely tokens on every turn after it, which is why an unbounded log is the most expensive thing a tool can do (§1, §8, §10).
- **Malformed parallel history.** One user message per result instead of one message carrying all of them teaches the model to stop batching, and shows up as a silent latency regression (§9).

---

## Further reading

- Anthropic, "Tool use" and "Parallel tool use" documentation (2024–26): tool schemas, `tool_use` / `tool_result`, `tool_use_id` matching, and the `disable_parallel_tool_use` switch.
- Anthropic, "Prompt caching" documentation (2024–26): the tools → system → messages prefix order, the cached-read multiplier, and what a tool edit invalidates.
- OpenAI, "Introducing Structured Outputs in the API" (2024) and the structured-outputs guide (2024–26): strict mode, the supported JSON Schema subset, and the schema-following evaluation figures.
- Tiantian Gan and Qiyao Sun, "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation" (2025): the 13.62% → 43.13% tool-selection measurement behind §10.
- Addy Osmani, "Agent Harness Engineering" (2026): bash as a universal tool, tool curation ("ten focused tools"), and tool descriptions as an injection surface.
- AI Incident Database, incident 1152 (2025), with Fortune's report of 23 July 2025: the Replit production-database deletion and the harness changes that followed it.
- awesome-harness-engineering (2026): the "Tool Design" section.
- Context Engineering, Post 15: the token-cost framing of tool definitions; Post 21 §2: the ladder of output guarantees.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 07 — Skills & MCP in the runtime](../07-skills-mcp-runtime/index.md)**: how to expose *many* capabilities without paying for all their schemas at once: progressive disclosure.
- **[Post 09 — Context management inside the loop](../09-context-management-loop/index.md)**: what happens to a tool result after the model has read it, and how to stop results accumulating.
- **[Post 14 — Permissions, sandboxes & security](../14-permissions-sandboxes/index.md)**: making the one general tool safe: the sandbox that does what §5's deny-list cannot.
- **[Post 24 — Build #1, a minimal agent harness](../24-build-minimal-harness/index.md)**: this registry, wired into a working loop with a verification gate.
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: revisit the ACT step this post expanded.
