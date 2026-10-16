# 20 - The SDK and framework landscape: Agent SDK, LangGraph, and peers

> **TL;DR.** An agent software development kit (SDK) is a **prebuilt harness**: it ships the loop, tools, context management, hooks and permissions that Parts I to III built by hand, and the team still supplies the custom layer. Four shapes cover the field, a batteries-included SDK, a code-first framework, a graph framework and an open harness engine, sorted by two axes: how much of the loop the product owns, and whether it is tied to one provider's models. What each shape takes away is a set of defaults, from its stop conditions to its permission resolution order, worth reading before adoption. The choice between two harnesses is settled by a paired A/B on the team's own tasks, and twenty tasks rarely settle it.
>
> **Prerequisites:** [post 02](../02-anatomy-of-a-harness/index.md), the eleven components and the seam between a prebuilt harness and the custom layer.
> **Safe to skip?** Skip it if the reader can already say what each shape of agent SDK ships and takes away, find an SDK's documented permission resolution order, and size a harness A/B before trusting its verdict.
>
> **After reading, you will be able to:**
>
> - List what an agent SDK ships as a prebuilt harness in the eleven-component vocabulary, and sort any option into four shapes along two axes.
> - Read a batteries-included SDK against a graph framework by the shape of the code, and name what each one takes away.
> - Audit an SDK's defaults before adopting it, starting from its stop conditions and its documented permission resolution order.
> - Pick the shape for a situation from an observable signal, price the build, and settle the choice with a paired A/B rather than an argument.
> - Keep the portable half of a harness portable, and place Harness-as-a-Service and agent-to-agent protocols beside the Model Context Protocol.

![A matrix of six components, loop, state, context management, hooks, permissions and orchestration, against the Claude Agent SDK, the OpenAI Agents SDK, LangGraph and the Codex harness, each cell built in, partial or the team's to build, as documented in October 2026.](diagrams/01-sdk-feature-matrix.svg)

*What each shape ships, as its documentation stated it on one date: a sketch of the field, not a spec sheet.*

---

## 1. What an agent SDK provides

What does an agent SDK give a team, what does it take away, and how is build-versus-buy settled by measurement rather than by argument? An agent SDK is the **prebuilt harness** of [post 02](../02-anatomy-of-a-harness/index.md). It ships the components Parts I to III built: the agent loop, tool dispatch, context management, hooks and a permission model, and most also ship orchestration as sub-agents ([post 16](../16-multi-agent-orchestration/index.md)) and some of the observability of [post 21](../21-observability-traces/index.md). A team that adopts one inherits them.

What the team still supplies is the **custom layer**: its tools, its rules in a memory file, its enforcement hooks, its evaluations, and the task. One vendor draws the split on its own architecture diagram: "Your application owns product context, business rules, and tools; Codex app-server provides the agent loop and sandboxed execution" (OpenAI, "Codex as a platform: build on the open agent harness", 19 August 2026). That is post 02's seam, drawn by a provider. An SDK removes the *plumbing* of harness engineering and leaves the part specific to the problem: "just use an SDK" and "harness engineering is dead" are different claims, and only the first can be true.

### The case that makes the point

OpenAI's account of its own agent-first project is the clearest published example (Ryan Lopopolo, "Harness engineering: leveraging Codex in an agent-first world", OpenAI, 11 February 2026). The first commit landed in late August 2025; five months later the repository held "on the order of a million lines of code" for an internal beta, with "roughly 1,500 pull requests" merged by three engineers, later seven, at "an average throughput of 3.5 PRs per engineer per day", and every line written by Codex. These are the vendor's figures for its own project with nothing held fixed: they show what a team can do inside a prebuilt harness, not that one harness beats another ([post 01](../01-from-context-to-harness/index.md)).

The team did not write a harness; it drove Codex, and what it engineered was the custom layer. The instructive detail is a failure: "one big `AGENTS.md`" did not work, because "a giant instruction file crowds out the task, the code, and the relevant docs". What replaced it was "a short `AGENTS.md` (roughly 100 lines)" serving as a map into a structured `docs/` directory, checked by the team's own linters and continuous integration (CI) jobs. That is progressive disclosure applied to the memory file ([post 10](../10-continual-learning-ratchet/index.md)), and no SDK shipped it.

---

## 2. Four shapes, and the two axes that sort the rest

Four shapes cover most of the field:

- **A batteries-included agent SDK.** The Claude Agent SDK "gives you the same tools, agent loop, and context management that power Claude Code", and its capabilities table lists built-in tools, hooks, subagents, the Model Context Protocol (MCP), permissions and sessions (Anthropic, "Agent SDK overview", consulted October 2026). The team supplies tools, options and a goal; the loop is inside.
- **A provider's code-first framework.** The OpenAI Agents SDK is "a very small set of primitives" composed in ordinary Python: agents, handoffs and agents as tools, and guardrails, plus sessions and built-in tracing (OpenAI, Agents SDK documentation, consulted October 2026). It runs its own loop but is nearer to a library than to an application.
- **A graph framework.** LangGraph is "a low-level orchestration framework and runtime" that "does not abstract prompts or architecture" (LangChain, LangGraph documentation, consulted October 2026): the agent is an explicit graph of nodes and edges over a persistence layer, and the team draws the loop. LangChain's own documentation puts planning, sub-agents and context management in a separate product on top, which it calls an agent harness.
- **An open harness engine to embed.** The Codex harness behind OpenAI's Codex app, command-line interface (CLI) and editor extension is the `openai/codex` repository, Apache-2.0 and public since April 2025. "Codex as a platform" offers it as `codex exec` for bounded jobs, the Codex SDK for programmatic control, and app-server for persistent threads, streamed events and approval requests, and says "The open-source layer is the harness and integration surface; model access and managed services remain separate."

A harness of one's own is the fifth option, priced in the section on choosing a shape, because it is a decision about cost rather than a product on a shelf.

The field is wider: Google's Agent Development Kit, Microsoft's Agent Framework, "the successor to Semantic Kernel and AutoGen" (Dmytro Struk and Shawn Henry, Microsoft, 19 February 2026), Pydantic AI, smolagents, CrewAI. A review would date within a quarter, so two axes are more useful than a list: **how much of the loop the product owns**, and **whether it is tied to one provider's models**. The figure below places the options on both; the Reference Implementations section of awesome-harness-engineering (ai-boost, GitHub, consulted October 2026) is the living list this paragraph is not.

![Four cells on two axes. Columns: the team draws the loop, or the product ships it. Rows: one provider's models by default, above, and any provider's models, below. Product's loop, one provider: the Claude Agent SDK and the Codex harness. Product's loop, any provider: the OpenAI Agents SDK. Team's loop, any provider: LangGraph and a harness of one's own. Team's loop, one provider: a loop over one client SDK, as this series' builds are.](diagrams/02-build-vs-buy.svg)

*Two questions place any product before its documentation is read: who owns the loop, and whose models it runs.*

The sibling series read several of these hosts from the token side, pricing a memory file, a skill and a tool schema inside the window (`ctx-026`); this post asks what they ship as runtime machinery.

---

## 3. What each one actually ships

Naming products teaches nothing; naming their primitives and the box on the map each fills teaches the map. The table is a translation dictionary, not a scorecard, from the documentation named above, consulted October 2026.

| Shape (example) | Its own vocabulary | Where it lands on the map |
|---|---|---|
| **Batteries-included SDK** (Claude Agent SDK) | hooks on lifecycle events (`PreToolUse`, `PostToolUse`, `PreCompact` and more); permission modes (`default`, `acceptEdits`, `plan`, `dontAsk`, `auto`, `bypassPermissions`); MCP servers; subagents; sessions to resume or fork; automatic compaction | hooks ([post 13](../13-hooks-enforcement/index.md)); permissions ([post 14](../14-permissions-sandboxes/index.md)); tools and MCP ([post 07](../07-skills-mcp-runtime/index.md)); orchestration; context management ([post 09](../09-context-management-loop/index.md)) |
| **Code-first framework** (OpenAI Agents SDK) | agents; handoffs; guardrails, input guardrails by default in parallel with the agent and tool guardrails around each function-tool call; `needs_approval` per tool; sessions; built-in tracing | orchestration; hooks; permissions ([post 15](../15-human-in-the-loop/index.md)); state ([post 08](../08-state-filesystem-git/index.md)); observability ([post 21](../21-observability-traces/index.md)) |
| **Graph framework** (LangGraph) | a typed state graph of nodes and edges; checkpointers that save a snapshot "at each super-step"; `interrupt()` and resume; time travel across checkpoints | the loop, drawn by the team ([post 03](../03-the-agent-loop/index.md)); durable state; permissions, as approval gates; replay |
| **Open harness engine** (Codex) | `codex exec`; app-server threads that start, resume and fork, with compaction and approval requests; the Codex SDK; hooks; sandbox and approval policy | the loop; context management; permissions: sandboxes ([post 14](../14-permissions-sandboxes/index.md)) and approvals |

The instructive column is the one the table cannot show: what each shape does *not* give.

- A batteries-included SDK does not give explicit control flow. A branch its loop does not make has to go through its hooks and options, or nowhere; that is the price of a free loop.
- A code-first framework gives places to put checks but no verifier ([post 11](../11-verification-loops/index.md)), and its stop condition is a turn cap that raises `MaxTurnsExceeded` unless an error handler is passed (OpenAI, "Running agents", consulted October 2026).
- A graph framework gives no compaction policy, no permission model and no sandbox: it gives the machinery to express a loop, and `interrupt()` as an approval primitive.
- An open engine does not include model access or the vendor's hosted services. The engine can be forked; the tokens cannot.

The hero matrix is illustrative and dated: a mark records what the named page documented in October 2026, and "partial" means this section qualifies it. The OpenAI Agents SDK's context management is partial because compaction is an opt-in session wrapper, `OpenAIResponsesCompactionSession`, and its permissions because approval is set per tool, by a flag or a per-call callable, with no rule language or modes (OpenAI, "Sessions" and "Human-in-the-loop", consulted October 2026). LangGraph's orchestration is partial because the team draws any multi-agent topology itself, and its permissions because `interrupt()` pauses the graph for a human, the mechanism of [post 15](../15-human-in-the-loop/index.md), with no rules around it. Its state cell is where a graph framework is strongest: a run interrupted at any node resumes there, but only on a durable checkpointer, because with `InMemorySaver` "When the process restarts, all checkpoints are lost" (LangChain, "Persistence", consulted October 2026).

---

## 4. The shape of the code

The difference between shapes shows in about a dozen lines. The block below is not run: it is the two vendors' documented shapes, the Claude Agent SDK's `query` with `ClaudeAgentOptions` (Anthropic, "How the agent loop works") and LangGraph's `StateGraph` with a checkpointer (LangChain, "Graph API" and "Persistence"), consulted October 2026, with the team's own functions left as names:

```python
# A: a batteries-included SDK owns the loop; the team supplies tools, options and a goal.
options = ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"], max_turns=30,
                             hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[deny_list])]})
async for message in query(prompt="add a test for the parser and make it pass", options=options):
    ...

# B: a graph framework: the team draws the loop as nodes and edges.
graph = StateGraph(State)
graph.add_node("reason", call_model)
graph.add_node("act", run_tools)
graph.add_edge(START, "reason")
graph.add_edge("act", "reason")
graph.add_conditional_edges("reason", lambda s: "act" if s["tool_calls"] else END)
app = graph.compile(checkpointer=saver)
result = app.invoke({"task": "add a test for the parser and make it pass"},
                    config={"configurable": {"thread_id": "run-1"}})
```

The SDK hides the loop and streams back messages; the graph framework hands over the loop to wire, in eight statements that block A never writes. The two that carry the argument are the last two of block B: the checkpointer passed at compile time and the thread identifier passed at invoke time make the run resumable, inspectable and forkable. That is what the extra lines buy, and a team that does not need it pays for nothing.

`snippets/two_shapes.py` runs the comparison without either vendor's package. Shape A is the loop of [post 24](../24-build-minimal-harness/index.md)'s companion, which owns the control flow; shape B is a small standard-library graph with explicit edges, a dictionary for a checkpointer and an interrupt before the node that acts. One scripted model, one shared tool function:

```text
task: Which version does config.txt pin? Answer with the version only.
shape A, a loop that owns the control flow: completed; 2 model calls, 296 input and 52 output tokens
shape B, a graph wired by hand: stopped before act with 2 checkpoints saved
  a fresh graph sharing only the checkpointer resumed it to END; 2 model calls, 296 input and 52 output tokens, 4 checkpoints
transcript of both: tool_use read_file {"path": "config.txt"} -> tool_result "name = parser\nversion = 2.4.1\n" -> answer 2.4.1
same transcript, same tokens: True
```

Same requests, same tokens (counted with tiktoken, so illustrative). What differs is who wrote the loop and what survives a stop: shape B was halted before its tool call, and a second graph that shared only the checkpointer finished the run. Neither shape is better in the abstract. A plain reason-act-observe loop drawn as a graph is a state machine with two states, a diagram of a `while` loop rather than an improvement on one, until the run needs to stop and come back.

---

## 5. What an SDK takes away

"Know what it takes away" is useless advice without a list. Seven things are worth checking before adopting an SDK, because each is a decision this series made deliberately and the SDK has already made:

- **The stop conditions.** [Post 19](../19-loop-engineering/index.md) reserves the budget *before* the call that would breach it. Which exits does the SDK implement, is the ceiling enforced or advisory, and does a guard exit leave a resumable position? The Claude Agent SDK is a worked answer: `max_turns` counts tool-use turns only, it and `max_budget_usd` default to no limit, and spend is compared with the cap after each response arrives, so "Spend can therefore pass the cap by up to the cost of that one response" (Anthropic, "How the agent loop works", consulted October 2026). A guard exit returns `error_max_turns` or `error_max_budget_usd` with a session identifier to resume from.
- **The context-management policy.** When does it compact, what does it drop, and can anyone see what was dropped? An SDK that summarises the middle of a run has made a [post 09](../09-context-management-loop/index.md) decision, and a summary that discarded the wrong thing looks exactly like a model that forgot.
- **Error and retry semantics.** Does a failing tool return an observation, as [post 06](../06-tools-bash-code/index.md) requires, or raise into the process? Do the SDK's own retries count against the budget?
- **The permission granularity.** Per tool, or per call with arguments? [Post 15](../15-human-in-the-loop/index.md) starts at tool granularity and narrows to arguments where the coarse version fires on things nobody needs to see; in its illustrative session, narrowing one policy took a gate from 34 requests per run to 3.
- **The hook lifecycle.** Which events can a hook observe, and which can *stop* a call? By [post 13](../13-hooks-enforcement/index.md)'s test, a hook that can only comment after the fact is a report, not a gate; only the points in front of an action can block it.
- **The trace format.** Is a gate's refusal distinguishable from a success ([post 14](../14-permissions-sandboxes/index.md))? [Post 21](../21-observability-traces/index.md) lists what a usable span carries: the stop reason, tokens per model call, and sub-agent work nested.
- **The upgrade cadence.** A fast-moving SDK changes underneath its users, a maintenance cost that belongs inside the build-versus-buy sum.

### One question, worked

Take the permission question against a real SDK. The Claude Agent SDK evaluates a tool call in six steps: hooks, deny rules, ask rules, the permission mode, allow rules, and only then the `canUseTool` callback (Anthropic, "Configure permissions", Claude Agent SDK documentation, consulted October 2026). The answer to "per tool, or per call with arguments?" is therefore *both*, and the part worth learning is the precedence.

Two consequences fall out of the order. A deny rule sitting *ahead* of the mode is what makes an aggressive mode survivable: "If a deny rule matches, the tool is blocked, even in `bypassPermissions` mode." And the callback sitting *last* is the argument-level granularity of [post 15](../15-human-in-the-loop/index.md), which anything approved by an earlier step never reaches. The page states it as a warning, "Auto-approved tools never reach `canUseTool`", so checks placed only in the callback are "silently bypassed for that tool", a defect that produces no error message.

The transferable lesson is the artefact to look for: for every SDK under evaluation, find the documented **resolution order**. An SDK that publishes none has still made the decision, somewhere nobody outside can read.

---

## 6. Which shape a team is in

The default is an SDK, and a harness of one's own is a choice to be earned.

Questions such as "is unusual control flow needed?" are answered by preference, so the table replaces each with a signal that can be observed:

| The signal observable today | The shape it points at | What it costs |
|---|---|---|
| One model in production, no concrete plan to switch | that model's own SDK, as the reference fit to measure against | portability, and a rewrite if the plan changes |
| Branch logic the SDK's loop keeps fighting, or runs that must survive a process restart | a graph framework | the batteries: compaction, permissions and sandboxing become the team's |
| The vendor's loop and sandbox wanted inside the team's own product surface | an open harness engine, embedded | the integration work; model access is still rented |
| Nobody can name the SDK feature that would be given up | a batteries-included SDK, not a build | nothing; this is the cheap answer |
| A requirement no shipped harness expresses, stated in one sentence | a harness of one's own | everything in the sum below, plus its maintenance |

The last two rows are the useful ones: "nobody can name what would be given up" is a testable statement about the team rather than a claim about the tools, and it is often the true one. The first row carries a caveat. A model's own SDK carries the conventions the model was trained against, which makes it the natural first harness to try, but [post 04](../04-harness-beats-model/index.md) found the best harness for a task is not necessarily the one the model was post-trained with: the vendor's SDK is a baseline to measure against, not a guaranteed best. Fit the harness to the model, then measure.

### Price the build before choosing it

This series builds two harnesses from scratch, so the last row's cost can be counted rather than estimated. `snippets/build_cost.py` reads the two companions:

```text
Build #1 (code/24-minimal-harness): 520 implementation lines, 138 test lines, 10 tests
Build #2 (code/25-harness-plus): 728 implementation lines, 233 test lines, 13 tests
union: Build #2's 728 implementation lines plus Build #1's 75-line verifier = 803
```

Build #1 ([post 24](../24-build-minimal-harness/index.md)) buys a loop, a schema-validated tool registry, a verification gate and four layered exits; Build #2 ([post 25](../25-build-harness-plus/index.md)) adds hooks, a sandbox, an approval gate, a sub-agent and tracing. They do not simply add, because each carries its own loop and registry and Build #2 ships no verifier, so the union is Build #2 plus Build #1's verifier: 803 implementation lines as `wc -l` counts them, before a single test. That total still has no compaction policy, no retry semantics, no MCP client and no permission resolution order, each of which a mid-range SDK ships and this series did not price.

Maintenance is not the worst of it. Build #2 shipped with two defects its passing tests could not see: its sandbox checked the first token of a command and then ran the raw string through a shell, so `echo hi; curl http://evil.example` passed, and its tracer tagged every sandbox refusal `ok`, because the sandbox refuses *inside* the tool and returns an ordinary string. [Post 25](../25-build-harness-plus/index.md) dissects both. The cost of rolling one's own includes the bugs that an SDK's other users have already found.

Build from scratch to *understand* what the SDKs do, which is what posts 24 to 26 are for, not to ship what they build.

---

## 7. Settle it by measuring, not by arguing

The comparison of the third section is a sketch, and sketches lose to evidence. The premise of this series is that the harness is a variable that moves outcomes ([post 04](../04-harness-beats-model/index.md)), which makes *the choice between two harnesses an empirical question*.

The method is the harness A/B of [post 22](../22-evaluating-harnesses/index.md): hold the model and the task set fixed, swap the harness, and compare **resolved-rate** and **cost per resolved task**, plus wall-clock and human interventions per run. Agent runs are draws from a stochastic process, so each task runs several times and the arms are compared task by task.

### A worked comparison

`snippets/harness_ab.py` runs that experiment in miniature, with one stand-in model held fixed. Harness A is shape A, post 24's loop, which accepts the model's first final answer; harness B is the hand-wired graph with one more node, a cheap check that the answer appears in the file the agent read, and one retry when it does not. The stand-in errs on each answer with a per-task probability; four in ten of its errors are made-up values that B's check catches, the rest values misread from the wrong line, which it does not. Because the stand-in is defined, B's true advantage is known, which a real A/B never knows. Twenty tasks, five seeds each, every number computed and illustrative:

```text
20 tasks x 5 seeds = 100 runs per arm; the model is held fixed
arm  resolved   rate  tokens/run  cost/run   cost/resolved  seconds/run
  A   66/100   66.0%         366  $0.00172  $0.00260         4.1
  B   67/100   67.0%         419  $0.00192  $0.00286         4.5
per task, resolved of 5 (A/B): 5/5 5/5 5/5 5/4 5/5 5/3 4/4 4/4 3/3 3/4 4/5 3/3 3/5 2/1 3/3 3/3 3/2 0/2 1/0 0/1
B-only wins 5, A-only wins 5, ties 10; sign test p = 1.00
measured lift +1.0 points; naive standard error 6.7 points (runs as independent), paired by task 4.5 points
95% interval on the paired lift: -8.3 to +10.3 points
true lift, from the stand-in's definition: +6.2 points
verdict: not callable; detecting the true lift four times in five would take about 83 tasks
```

Costs are tiktoken counts at the Claude Sonnet 4.6 rates of 3 and 15 dollars per million input and output tokens (Anthropic pricing page, consulted October 2026), and seconds are simulated at 2.0 per model call and 0.1 per tool call; real prompts are far larger, and the ratios are the point. Read it in four steps:

- **Resolved-rate:** 66% against 67%. B is better by construction, by 6.2 points, and twenty tasks measured one.
- **Cost per resolved task:** B's check and retry cost about 10% more per resolved task (0.00286 dollars against 0.00260), to be justified against a lift nobody can yet see.
- **Is the gap real?** The paired interval runs from −8.3 to +10.3 points, and the sign test on the ten discordant tasks agrees: no call either way. The naive 6.7-point standard error treats runs that share a task as independent; pairing by task is what post 22 prescribes.
- **The per-task diff:** B won five tasks and lost five, and every one of A's wins is noise, because the stand-in makes B at least as good on every task. A regression seen at five seeds is re-run before it is believed.

The figure below draws the run. The arithmetic belongs before a migration, not after: at this spread about 83 tasks would detect the true lift four times in five, the sizing problem post 22 takes up.

![Two panels computed by the post's A/B snippet. Left, twenty tasks as rows, each a dot at B's resolved count minus A's, out of five seeds: ten on zero, five to the right and five to the left. Right, the measured lift of 1.0 point with its 95 percent interval from minus 8.3 to plus 10.3 points, crossing zero, the true lift of 6.2 points, and a table: A resolved 66 of 100 runs and B 67.](diagrams/03-harness-ab.svg)

*A real 6.2-point improvement, measured on twenty tasks as one point, with an interval wide enough to hold either verdict.*

Two cautions travel with any such comparison. An A/B across two vendors' SDKs measures model and harness as a pair, because each vendor's SDK is shaped for its own models. And migration cost is set less by the loop than by how deeply the custom layer reached into the SDK's types, which is decided at design time.

---

## 8. Portability and lock-in

Every SDK ties its users to its abstractions: its loop, its hook interface and its permission model are its own, and migrating off them is real work. The cheapest way to see how much is to look at what survives a move untouched.

A tool is a function plus a schema, both the team's; only the adapter belongs to the harness. In `snippets/two_shapes.py` one tool reaches both shapes:

```python
# The portable half: a plain function and the schema that describes it.
def read_file(args: dict) -> str:
    return (WORKDIR / args["path"]).read_text(encoding="utf-8")


READ_FILE = {
    "name": "read_file",
    "description": "Read a UTF-8 text file and return its contents.",
    "input_schema": {"type": "object",
                     "properties": {"path": {"type": "string"}},
                     "required": ["path"], "additionalProperties": False},
}

# Adapter A: a harness that takes a tool list and runs the loop itself.
registry = ToolRegistry([Tool(READ_FILE["name"], READ_FILE["description"],
                              READ_FILE["input_schema"], read_file)])


# Adapter B: a graph framework, where the same function becomes one node.
def act(state: dict) -> dict:
    call = state["pending"]
    return {**state, "pending": None,
            "messages": state["messages"] + [tool_result(call, read_file(call.input))]}
```

`Tool` and `ToolRegistry` are the real types of [`code/24-minimal-harness/`](../../code/24-minimal-harness/), and every provider SDK has an equivalent pair. The function and the schema did not move; the switching cost for this tool is the few lines under each adapter comment. **The length of the adapter is the switching cost**, a quantity to design down rather than a risk to worry about.

Two things reduce lock-in, and both follow from that observation:

- **Plain tools and MCP.** A tool defined as a function ports at the cost of its adapter. A capability behind an MCP server ports at no cost to the server, because the protocol puts a boundary between host and server ([post 07](../07-skills-mcp-runtime/index.md); `mcp-002`): any host that speaks MCP calls it unchanged, and the Claude Agent SDK, the OpenAI Agents SDK and Codex all document MCP support.
- **A separable custom layer.** The memory file, the evaluations and the task definitions are the team's; the more they live outside the SDK's types, the cheaper a switch. A hook written as a plain predicate over a tool name and its arguments ports; the same logic written against the SDK's hook input object does not.

An open engine prices lock-in differently: a permissive licence makes forking available where migrating was the only option. That changes the shape of the risk without removing it, because model access is not in the release; the dependency moves from the engine to the tokens.

The trade is the usual one. A vendor's SDK buys the reference fit for that vendor's models at the cost of portability; a graph framework buys explicit control at the cost of the batteries; an open engine buys the right to fork at the cost of integration work; a harness of one's own buys total control at the price counted above. There is no free option, only a priced one.

---

## 9. Harness-as-a-Service, and the layer beside MCP

The landscape is trending a step further. Vivek Trivedy named it in September 2025: "the core primitive for working with AI is shifting from the LLM API (chat style endpoints) to the Harness API (customizable runtimes). I call this Harness as a Service (HaaS)" ("The Claude Code SDK and the Birth of HaaS (Harness as a Service)", vtrivedy.com, 23 September 2025). Addy Osmani's "Agent Harness Engineering" (April 2026) restated it, crediting Trivedy, as a move from large language model (LLM) application programming interfaces (APIs) "which give you a completion" to harness APIs "which give you a runtime", and counts the Claude Agent SDK, the Codex SDK and the OpenAI Agents SDK as pointing that way.

The far end of the trend is a runtime the vendor hosts: a task goes in and an agent run comes back. Anthropic's documentation already lists one beside its SDK, Managed Agents, "A hosted agent harness that runs the agent loop, with sessions in an Anthropic-managed cloud sandbox or a self-hosted sandbox" (Anthropic, "Agent SDK overview", consulted October 2026). A rented runtime has no line count and no maintenance but a per-run price, so whether to build, adopt or rent becomes partly an economics question, which is [post 23](../23-economics-haas/index.md).

A second shift runs *beside* MCP rather than above it. The Agent2Agent (A2A) protocol standardises "how independent, often opaque, AI agents communicate and collaborate with each other as peers" (A2A Project, "Agent2Agent (A2A) Protocol Specification", version 1.0.0, consulted October 2026). An agent publishes an agent card, "a structured description of what it can do and how to reach it" (Agentic AI Foundation, "A2A joins AAIF's open agentic stack", 17 August 2026), and other agents read it to discover capabilities and delegate tasks without sharing their internals. MCP connects one agent *down* to its tools and data; A2A connects agents *sideways* to each other, and the specification's own example has an A2A server agent using MCP for the tools behind its task. It is governed, not a rumour: Google launched it in April 2025, the Linux Foundation launched it as a project on 23 June 2025, version 1.0 shipped in March 2026, and it became a hosted project of the Agentic AI Foundation on 17 August 2026. Systems that cross an organisational boundary are beyond this series' scope, but this is the layer to watch.

---

## 10. Make it run

The plan's exercise for this post is to implement one tiny task against a batteries-included shape and a graph shape with one shared tool function, then A/B the two on a fixed task set. No vendor SDK or framework is installed for it: the three snippets run offline from the series root with the standard library and `tiktoken`, and the first two import the loop of `code/24-minimal-harness/` unchanged:

```bash
uv run python posts/20-sdk-landscape/snippets/two_shapes.py
uv run python posts/20-sdk-landscape/snippets/harness_ab.py
uv run python posts/20-sdk-landscape/snippets/build_cost.py
```

Each prints the output quoted above in about a second; the real A/B runner is [post 22](../22-evaluating-harnesses/index.md)'s. To try a variation, set `SEEDS` in `harness_ab.py` to 20 and watch the interval narrow on the same twenty tasks.

---

## 11. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A permission check written only in the callback.** The team puts its argument checks in `canUseTool` and adds a bare allow rule for `Bash`; every `Bash` call that reaches the allow step is approved there, and the checks never run.
- **A budget treated as a hard ceiling.** `max_budget_usd` is set to the exact limit; the response that crosses it still completes, and the bill overshoots by one call, plus whatever running sub-agents spend before they stop.
- **An in-memory checkpointer in production.** The graph resumes perfectly in testing; the first process restart loses every run in flight, because the checkpoints lived in memory.
- **A verdict from twenty tasks.** The A/B shows a two-point gap and the team migrates; a rerun with new seeds shows the opposite sign, and nobody can say which harness is better.
- **Tools written against the SDK's types.** Every tool takes the SDK's context object, so a migration rewrites each tool, not a few adapter lines.

---

## Common pitfalls

1. **Rolling a harness of one's own by default.** Build from scratch to learn, not as a production reflex; the union of this series' two builds is 803 lines before compaction, retries or an MCP client.
2. **Thinking an SDK removes harness engineering.** It removes the plumbing; the custom layer is still designed, as OpenAI's own team found with its memory file.
3. **Adopting without auditing the defaults.** The SDK has already chosen the stop conditions, compaction, retries, hook lifecycle and permission resolution order; each is documented somewhere, or decided where nobody can read it.
4. **Choosing an SDK from a feature matrix.** Hold the model and the task set fixed, A/B the harnesses with several seeds per task, and pair the comparison by task.
5. **Deep lock-in, unpriced.** The switching cost is the length of the adapters and the depth the custom layer reached into the SDK's types; both are design-time choices.
6. **A graph framework for a simple loop.** Explicit graphs earn their extra lines through durable state and resumability; a plain reason-act-observe loop drawn as a graph is a two-state machine.

---

## Further reading

- Anthropic, Claude Agent SDK documentation: "Agent SDK overview", "How the agent loop works", "Configure permissions" and the hooks guide (consulted October 2026).
- OpenAI, Agents SDK documentation (consulted October 2026).
- LangChain, LangGraph documentation: overview, "Persistence" and "Interrupts" (consulted October 2026).
- OpenAI, "Codex as a platform: build on the open agent harness" (19 August 2026), with the Apache-2.0 `openai/codex` repository.
- Ryan Lopopolo, "Harness engineering: leveraging Codex in an agent-first world" (OpenAI, 11 February 2026). The agent-first internal project and the `AGENTS.md` table of contents.
- Vivek Trivedy, "The Claude Code SDK and the Birth of HaaS (Harness as a Service)" (vtrivedy.com, 23 September 2025), and Addy Osmani, "Agent Harness Engineering" (April 2026). Harness-as-a-Service, named and popularised.
- A2A Project, "Agent2Agent (A2A) Protocol Specification", version 1.0.0 (consulted October 2026).
- ai-boost, awesome-harness-engineering (GitHub, consulted October 2026). The Reference Implementations section.
- `ctx-026` (`context-engineering`): the same hosts read from the token side.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 21 - Observability and trace-driven repair: seeing what the harness did](../21-observability-traces/index.md):** Part V opens with seeing what a harness, prebuilt or not, actually did on each step.
- **[Post 22 - Evaluating harnesses: Terminal-Bench, SWE-bench, harness A/B](../22-evaluating-harnesses/index.md):** the A/B of this post at full size, with the graders, seeds and sizing that let it reach a verdict.
