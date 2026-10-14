# 02 - The anatomy of a harness

> **TL;DR.** A harness looks amorphous, "everything around the model", until its parts are named. This series names eleven components around one core, the **loop**: four that *feed* the model, four that *govern* it, and two that work at a larger *scale*. Four of the eleven make a system a harness at all; the other seven are standard but optional. The map turns "my agent is flaky" into a located complaint, and separates the prebuilt harness a team inherits from the custom layer it must build.
>
> **Prerequisites:** [Post 01 - From context to harness: the third era](../01-from-context-to-harness/index.md).
> **Safe to skip?** Skip it if the reader can already name the eleven components and the group each belongs to, say which four are constitutive, and tell the mechanism a software development kit (SDK) ships from the policy a team writes on it.
>
> **After reading, you will be able to:**
>
> - List the eleven components of a harness by number and name, in their groups: the loop, four that feed the model, four that govern it, two at larger scale.
> - Say which four components make a system a harness and which seven are standard but optional, and name what a system missing one of the four is.
> - Read the map as a lookup: turn a complaint into the failure mode, the component to change and the post that treats it.
> - Separate the prebuilt harness inherited from an SDK from the custom layer a team adds, as mechanism against policy.
> - Explain why one agent is the default before orchestration, pricing the coordination tax from the cited token multipliers.

![The component map: the loop at the centre with reason, act and observe; tools, state, context management and memory on the left; verification, hooks, permissions and observability on the right; orchestration and long-horizon patterns along the foot of a frame around the whole.](diagrams/01-component-map.svg)

*Eleven components, numbered 01 to 11: the loop at the centre, the components that feed it on one side, the ones that govern it on the other, and the two that work at a larger scale around the whole.*

---

## 1. The question: why does a harness need a map?

"My agent is flaky" is not a diagnosis, and "use a bigger model" is not necessarily the fix: [post 01](../01-from-context-to-harness/index.md) took a first look at the evidence that the harness can be the bigger lever. The value of an anatomy is that it turns a vague complaint into a located one. Once a team can say *which component* is failing, it knows which lever to pull.

The map has a centre and three groups. The centre is the **loop**, the thing that makes a system an agent rather than a single call to a large language model (LLM). Around it, components divide by what they do to the model: some **feed** it information and capability, some **govern** what it may do and record what it did, and two work at a larger **scale** than one running agent. The hero figure draws this layout. The component set overlaps heavily with other published breakdowns (Osmani, 2026; Trivedy, 2026; Databricks, 2026; ai-boost, 2026); the eleven names and the three groups are this series' own, and the next section sets the counts side by side.

Two numbering systems appear on this page, so they are worth separating once. A two-digit number from 01 to 11 is a component, numbered as the hero figure, the [notation guide](../../notation_guide.md) and the [cheatsheet](../../CHEATSHEET.md) number them. "Post NN" is a post of this series. Component 02 is therefore treated in post 06, and nothing has gone wrong.

One seam needs closing before the walk starts, because post 01 drew a different picture. Post 01 nests four rings: model, scaffold, harness, orchestration. That is the *vocabulary*, and it answers "what kind of thing is this?". The eleven components are the *parts list*, and they answer "what is it made of?". The two pictures interlock rather than compete. The scaffold ring is where the system prompt, the tool descriptions and the step-to-step memory are **authored**; the harness ring is the runtime that **executes** them, which is why context management (04) and memory (05) appear here although post 01 files their content under the scaffold. Orchestration (09) is the one component that lives in the ring above the harness, which is why this post calls it part of the scale tier rather than taking it out of the list or renumbering everything after it.

---

## 2. Why eleven, and what other taxonomies count

There is nothing sacred about eleven. Every source splits the same ground differently, so it is worth stating plainly what this map merges and what it promotes.

| Source | How it counts | What it names that this map does not | Where that lands here |
|---|---|---|---|
| This series | 11 components around one loop, with orchestration in the scale tier | n/a | n/a |
| Osmani (19 April 2026) | 6 things a harness includes | System prompts and instruction files; bundled infrastructure (filesystem, sandbox, browser) | Prompts and instruction files are authored in the scaffold ([post 01](../01-from-context-to-harness/index.md)); the bundled infrastructure splits across state (03), permissions (08) and tools (02) |
| Databricks (2026) | 8 building blocks | System prompts; guardrails and human-in-the-loop controls as one block | System prompts are authored in the scaffold; human approval is a *policy* on permissions (08), and gets post 15 to itself |
| Trivedy, LangChain (10 March 2026) | 6 capabilities, derived backwards from behaviour | Sandboxes bundled with executing and verifying work; "Battling Context Rot" as a heading | Verification (06) and permissions (08) split what it bundles; context rot is the problem context management (04) exists to solve |
| ai-boost (2026) | 12 "Design Primitives" headings | Planning and task decomposition; debugging and developer experience; human-in-the-loop | Planning is a loop *shape*, treated in posts 12 and 19; debugging is what observability (11) buys; human-in-the-loop is post 15 |

Read across the table and the disagreements are mostly about granularity, not substance. Databricks folds guardrails and human approval into one block where this map keeps hooks (07) and permissions (08) apart, because in practice they fail differently: a hook that never fires is a bug in the team's code, and a permission that is too broad is a bug in its policy. Trivedy's list is shorter because it is derived from *behaviour* rather than architecture; his article states the method as "Behavior we want (or want to fix) → Harness Design to help the model achieve this" (Trivedy, 2026), which yields headings shaped like goals rather than like boxes. The ai-boost catalogue is longer because it is a reading list, and a reading list can afford a heading for developer experience that an architecture diagram cannot.

Two boundaries are drawn on purpose rather than inherited. **Hooks (07)** is a component of its own because deterministic code that runs at a lifecycle point is a different mechanism from an allow-list, even though both constrain the agent; among the sources above only Trivedy and Osmani list it, in near-identical words: "Hooks/Middleware for deterministic execution" (Trivedy, 2026) and "Hooks and middleware for deterministic execution" (Osmani, 2026). **Long-horizon patterns (10)** has a heading only in Trivedy's article, as "Long Horizon Autonomous Execution" (and in Osmani's walk-through, which follows it), and it is kept apart from context management here because resetting to a fresh window against a written specification is a different operation from compacting the window the agent has. A reader who sees those two as merges can merge them; the map still works at nine. What matters is that the parts are named, not that the count is eleven.

---

## 3. The core: the loop

Everything hangs off the loop, so it comes first. A harness calls the model, reads the actions the model asks for, executes them, feeds the results back, and repeats. This is the **reason, act, observe** cycle, the pattern named by the ReAct line of work (Yao et al., 2022). [Post 03](../03-the-agent-loop/index.md) is entirely about it.

The most important part of the loop is the least glamorous: **when it stops.** A loop that never stops burns money; a loop that stops too early ships half-done work. A well-built loop carries four layered exits, numbered the same way throughout this series: (1) final answer, the intended exit, which verification then confirms; (2) iteration cap, a hard ceiling on turns; (3) budget, a ceiling in tokens or wall-clock seconds; (4) no progress, the stall detector that fires when successive turns stop changing anything. Post 03 owns the four exits and argues the claim this series is built on: many agent failures are stopping-condition faults rather than reasoning faults, a claim that rests on named failures, not on a measurement.

---

## 4. What is constitutive, and what is merely standard

Eleven equal-looking boxes leave an obvious question open: how few of them can a system have and still be a harness? A conceptual analysis of the term gives a precise answer. It proposes four conditions that are together necessary and sufficient for a system to count as an agent harness (de Macedo, 8 June 2026): (i) "an agent loop that interleaves reasoning, action, and observation"; (ii) "a tool interface that lets the model perceive and alter the environment"; (iii) "context management that decides what enters and leaves the model's window"; and (iv) "control mechanisms, that is, limits, verification, and deterministic actions". A system is a harness if and only if it has all four at runtime. Each is argued to be necessary on its own terms: "Without an agent loop, the system answers once and stops; it is a generator, not an agent", and without context management "there is no viable loop", because every multi-step task piles results into the window: managing them is "not a luxury reserved for long tasks".

What the same paper rules *out* is as useful as what it rules in. A harness does not require a multi-agent architecture, any learning or fine-tuning, a specific model, or a user interface (UI); in the paper's words, "a harness can be a faceless library". The definition is then turned into an inclusion and exclusion test, applied to six real systems (Claude Code, Codex command-line interface (CLI), Aider, Cline, OpenHands and SWE-agent), and used to separate a harness from an agent framework, an agent SDK, an integrated development environment (IDE) plugin, an evaluation harness and an orchestrator (de Macedo, 2026).

Laid over this map, the four conditions land on components **01** (loop), **02** (tools), **04** (context management) and **06** (verification). The fourth condition is the loosest fit, and the mapping is this series' choice: the paper's "limits" are the loop's exits, its "deterministic actions" overlap hooks (07), and the series files the condition under verification, its fullest form, although the paper's test is met by any one of the three: "a cap on tool calls or a deterministic check passes". Four of the eleven are constitutive; the other seven are standard in production and optional in principle. That is a sharper claim than "most production harnesses have these parts", because it is falsifiable: a system missing any of the four is something else, a generator, a wrapper or a pipeline. [Post 20](../20-sdk-landscape/index.md) takes up the two nearest neighbours, the agent framework and the agent SDK, and sorts them by how much of the loop they own. The test also explains a common shape of demo: a loop, tools and a verifier, and no context management. It looks complete, works on short runs, and degrades on long ones, because the missing part is the one long runs need.

---

## 5. Four components that feed the model

These decide what capability and information the model has on each turn. They are where this series overlaps most with context engineering, and where the lens differs, as [post 01](../01-from-context-to-harness/index.md) set out: the sibling series designs one call, this one the runtime around the calls.

**02, tools (post 06).** The agent's hands; also called tools and code execution. By 2026 the common practice is a small set of general-purpose tools, above all bash and code execution, in preference to a large set of narrow, bespoke ones, because the model can compose general tools into actions nobody pre-built. Osmani puts it as "bash plus code execution has become the default general-purpose strategy for autonomous problem solving" (Osmani, 2026; Trivedy, 2026). Skills and Model Context Protocol (MCP) servers extend this surface at runtime ([post 07](../07-skills-mcp-runtime/index.md)).

**03, state (post 08).** The model's context window is small and expensive; the filesystem is large and cheap. Writing intermediate results, plans and artefacts to disk gives the agent a durable record outside the window, and keeping that state under **git** adds versioning and rollback: an agent can check out, try, and revert (Osmani, 2026).

**04, context management (post 09).** A long-running loop fills its window and begins to degrade. The token-level account of that degradation, *context rot*, is the sibling series' (`ctx-006`, which catalogues the context failure modes this group inherits). The harness fights it actively at runtime, and [post 09](../09-context-management-loop/index.md) sets the corrective moves out as a ladder of rising aggressiveness: **offload** a big tool output to disk and hand back a pointer (write a 2,000-line log to a file, say, and return its path), **clear** tool results that have already been acted on, **compact** the older turns into a summary, and **reset** the window entirely behind a handoff file. Osmani describes three of them as compaction, tool-call offloading and full context resets, crediting the last to Anthropic (Osmani, 2026). The lower rungs lose less, so they are tried first.

**05, memory (post 10).** Feeding knowledge *across* sessions, not just within one; also called memory and continual learning. A memory file injected at the start of every session, and the discipline of turning each failure into a durable rule, **the ratchet**, are what let a harness get better over time rather than repeat the same mistakes (Osmani, 2026).

---

## 6. Four components that govern the model

These decide what the model may do, whether its work is real, and what can be seen afterwards. This group is what separates a demo from something a team would run unattended.

**06, verification (post 11).** The answer to an agent that declares victory without checking. A verification step (running the tests, a self-critique, a schema check) surfaces an error at the step that caused it, so a small early mistake does not compound into a wasted run. The operating principle is HumanLayer's, as Osmani reports it: "success is silent, failures are verbose". Passing checks stay quiet, and failures are fed back into the loop (Osmani, 2026).

**07, hooks (post 13).** Some rules are too important to leave to the model's judgement. A hook is deterministic code that runs at a lifecycle point (before a tool call, after a file edit, before a commit) to enforce a rule unconditionally. Osmani's examples: run the type check, the linter and the tests after every edit; block `rm -rf`, `git push --force` and `DROP TABLE`; require approval before opening a pull request (PR) or pushing to `main` (Osmani, 2026). Hooks are the enforcement half of the ratchet.

**08, permissions (post 14).** An agent with real tools has a real blast radius. A sandbox, an isolated workspace where an agent acts "without affecting anything outside the environment" (Databricks, 2026), and declarative permission rules bound what a run can touch, so a mistake, or a prompt injection that reaches a tool, is contained. Which actions a human must approve is a policy on this component, and [post 15](../15-human-in-the-loop/index.md) treats it.

**11, observability (post 21).** A team cannot improve what it cannot see. A trace of each run (inputs, outputs, tokens, latency, tool calls, sub-agent spans, and the reason the loop stopped) is what lets an engineer localise the failing component. Osmani reports a next step as an open problem named by Trivedy: agents that analyse their own traces to find and fix harness-level failures (Osmani, 2026). The component is numbered last and lands in Part V, nineteen posts after this one, because tracing is easiest to teach once there is a full harness to trace. That is a teaching order, not a build order: observability is the component a team regrets deferring.

---

## 7. Two components that operate at larger scale

The last two are not about one running agent; they are about many agents, or one agent running longer than a single window allows.

**09, orchestration (post 16).** Coordinating several agents as units. The clean boundary from post 01 is that a harness drives one model through its loop, while an orchestrator coordinates many agents one level up. It is powerful and easy to overuse, and the default this series takes from Anthropic's "Building effective agents" is "finding the simplest solution possible, and only increasing complexity when needed" (Anthropic, 2024): one agent first.

That default is often argued qualitatively, which makes it easy to wave away. It prices out. Anthropic's account of the multi-agent research system it built (13 June 2025) gives both halves of the trade in numbers: "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats" (Anthropic, 2025). Applied to an illustrative task whose chat form costs 40,000 tokens, `uv run python posts/02-anatomy-of-a-harness/snippets/coordination_tax.py` prints:

```text
shape                          multiplier    tokens  above chat
one chat turn                          1x    40,000           0
single agent in a loop                 4x   160,000     120,000
orchestrator with sub-agents          15x   600,000     560,000
coordination tax, orchestrator over single agent: 440,000 tokens, 11 chats
```

![Three dashed illustrative bars on one token axis: one chat turn at 40,000 tokens, a single agent in a loop at 160,000 and an orchestrator with sub-agents at 600,000, with the 440,000-token gap between the last two marked as the coordination tax.](diagrams/02-coordination-tax.svg)

*The multipliers are Anthropic's; the 40,000-token task is illustrative. The gap between the single agent and the orchestrator is paid before the answer is any better.*

The coordination tax is the gap between the last two rows, which the chart above draws to scale: 440,000 tokens, eleven chats' worth of spend ($15 \times 40{,}000 - 4 \times 40{,}000 = 440{,}000$). The honest other half of the same report is why the pattern survives at all. Token usage "by itself explains 80% of the variance" in performance on the BrowseComp evaluation, and the multi-agent system "outperformed single-agent Claude Opus 4 by 90.2%" on Anthropic's internal research evaluation (Anthropic, 2025). Spending more tokens is a large part of what buys the improvement, which is why the advice is *only with a real reason* rather than *never*. The report names the reason: multi-agent systems "excel especially for breadth-first queries", work whose independent paths will not fit in one window. Anything narrower is one agent with sub-tasks.

**10, long-horizon patterns (post 18).** For work that outgrows one context window, such as building a whole project across many sessions, the harness resets to a fresh context against a written specification and repeats, carrying state on disk. The simplest form is the **Ralph loop** (Huntley, 2025); the practice of designing such loops is loop engineering ([post 19](../19-loop-engineering/index.md)).

---

## 8. Reading the map as a diagnostic

A map is worth carrying only if it shortens a search. The way to use this one is to translate the sentence a colleague actually says into a group, and then into a component. The table below does that for the six failure modes catalogued in [post 05](../05-agent-failure-modes/index.md), plus the complaint that arrives when there is no trace.

| What the team hears | Failure mode (post 05) | Group | Component to change | Treated in |
|---|---|---|---|---|
| "It said it was done, and it wasn't." | victory declaration | governs | 06 verification, on exit (1) | [post 11](../11-verification-loops/index.md) |
| "It gets rushed and sloppy near the end of a long run." | context anxiety | feeds | 04 context management: compact or reset | [post 09](../09-context-management-loop/index.md) |
| "It tried the whole thing in one go and made a mess." | one-shotting | governs | 06 verification: a planner, generator, evaluator split | [post 12](../12-planner-generator-evaluator/index.md) |
| "It has been going in circles for twenty minutes." | doom loop | core | 01 loop: the no-progress exit (4) | [post 03](../03-the-agent-loop/index.md) |
| "It keeps ignoring a convention the team agreed last week." | silent drift | feeds, then governs | 05 memory file, enforced by a 07 hook | [post 10](../10-continual-learning-ratchet/index.md) |
| "It ran a force-push nobody asked for." | destructive action | governs | 07 deny-list hook, plus an 08 sandbox | [post 14](../14-permissions-sandboxes/index.md) |
| "It failed, and nobody can say where." | none | governs | 11 observability | [post 21](../21-observability-traces/index.md) |

Three of those rows are worth reading twice, because they are the easiest to get wrong. "It gets sloppy near the end" is easily treated as a model problem when it is often a window problem: the same model that was careful early in the run is reading a crowded window late in it. "It keeps ignoring a convention" spans two groups on purpose: writing the rule into a memory file is a *feed* fix and it can be ignored, so the durable version pairs it with an enforcement hook. And "it failed and nobody can say where" is not a symptom of the failing component at all; it is a symptom of the missing one.

For anything the table does not cover, a three-way heuristic does most of the work. If the fix being reached for is *more information*, the problem is in the feeds group. If it is *a rule the model cannot skip*, it is in governs. If it is *another agent*, the coordination tax of the previous section applies before anyone spends fifteen times the tokens. This is Trivedy's derivation run in the other direction: his method goes from wanted behaviour to harness design (Trivedy, 2026), and a diagnostic table is that method read backwards from the behaviour the team got.

---

## 9. Prebuilt against custom: which parts a team builds

Not every component is a team's to write. A distinction this series uses throughout runs across the whole map:

- **The prebuilt harness** is what a tool or SDK provides out of the box. Claude Code, the Codex harness and the agent SDKs ship a loop, tool dispatch, context management, a hook system, a permission model and some form of trace. A team inherits these.
- **The custom harness** is the layer the team adds on top: its conventions in a memory file, its own tools, its evaluations, its enforcement hooks, its sandbox policy. This series argues that most of the reliability lives here, because it is the part no vendor can ship for a particular codebase.

![Two columns split by a dashed seam: the mechanism an SDK ships (loop, tool dispatch, context management, hook system, permission model, trace format) and the policy a team writes (its tools, hooks, sandbox policy, memory file and evaluations), with arrows pairing tool dispatch, the hook system and the permission model with their custom counterparts.](diagrams/03-prebuilt-custom-seam.svg)

*Tools, hooks and permissions appear on both sides: the harness ships the machinery, and the team supplies the policy it runs.*

The figure shows three components on both sides of the seam. That is not sloppy bookkeeping; it is the shape of the split. An SDK gives a team a *hook system*, and the team writes the *hooks*; it gives a *permission model*, and the team writes the *policy*; it gives *tool dispatch*, and the team writes the *tools*. The mechanism is inherited and the policy is the team's, which is why hearing that a team uses an SDK says much less about its system than it seems to. Evaluations sit on the custom side alone: they are not one of the eleven components but the discipline that checks them ([post 22](../22-evaluating-harnesses/index.md)), and no vendor can ship a team's task set.

Three questions settle ownership for any component on the map:

1. **Does the mechanism differ between tasks inside the organisation?** If not, inherit it. Few teams have a reason-act-observe loop special enough to justify writing their own.
2. **Would getting it wrong fail silently?** If yes, own the policy and test it. A permission set that is too broad emits no error message; neither does a hook that never fires.
3. **Could a competitor copy it from the team's public documentation?** If yes, it is prebuilt in all but name. If not, it is custom by definition: the team's conventions, its evaluations, its enforcement rules.

The smallest instantiation of this map in the series is [`code/24-minimal-harness/`](../../code/24-minimal-harness/), the companion to post 24. It builds three components from scratch and inherits nothing; four engine modules carry them, alongside a demo and one test file:

```text
code/24-minimal-harness/src/minimal_harness/
├── harness.py    # 01  the loop, and its four layered exits
├── tools.py      # 02  schema-validated registry, deny-listed bash
├── verify.py     # 06  the verification gate
└── models.py     #     the provider seam; ScriptedModel keeps it offline
```

In `harness.py` the loop's exits are an enumeration, `StopReason`, whose four values are spelled `completed`, `max_iters`, `budget` and `no_progress`, and `completed` is returned only when the final answer has passed the verification gate. Hold that against the constitutive test and something instructive falls out: Build #1 meets three of the four conditions and skips the third. There is no compaction anywhere in `harness.py`; its default cap of 12 iterations is what keeps the transcript short enough not to need managing. The governing components arrive separately, in [`code/25-harness-plus/`](../../code/25-harness-plus/), as five small modules: `hooks.py` (07), `sandbox.py` (08), `approval.py` (post 15's policy on 08), `observe.py` (11), and one that belongs to the scale tier, `subagent.py` (09). Both companions run offline against a scripted model, so neither needs a network or an application programming interface (API) key.

The practical consequence is that harness engineering is rarely "build a loop from scratch". It is more often *choosing a prebuilt harness well and then engineering the custom layer that makes it trustworthy for the task.* Posts 24 to 26 build one anyway, because doing it once shows what the prebuilt ones do.

---

## 10. A mature harness, decoded

It helps to see the map instantiated in something large. Osmani's "Agent Harness Engineering" (19 April 2026) calls Fareed Khan's breakdown of Claude Code's architecture "the clearest public picture I've seen of a mature harness", and labels it an *estimated* breakdown rather than published architecture (Osmani, 2026). Read with that caveat firmly attached, the estimate names seven layers around a central agent loop, and each lands on components of the map:

| Layer, in the estimate | What the estimate puts there | Components of the map |
|---|---|---|
| Input | the user interface, a session manager, a permission gate | 08 permissions |
| Knowledge | a skill registry, a context compressor, a task graph, a memory store | 02 tools, 03 state, 04 context management, 05 memory |
| Integration | the MCP runtime and external servers | 02 tools, extended at runtime |
| Execution | tool dispatch, a streaming runtime, a prompt cache | 01 loop, 02 tools |
| Output | verified task results | 06 verification, implied by "verified" |
| Observability | an event bus and a background executor | 11 observability |
| Multi-agent | sub-agent spawning, teammate mailboxes, a finite-state machine (FSM) protocol, an autonomous board, a worktree isolator | 09 orchestration |

Two components get no layer of their own: hooks (07), which Osmani places behind the permission gate, and long-horizon patterns (10). That is not evidence that Claude Code lacks them; it is a reminder that banding is one outside observer's reading, and a layer diagram groups by where code runs, not by what job it does.

The point is not that this is how Claude Code is really built. It is that a shipping harness is not a monolith with a clever prompt inside; it is the component map, wired together, however an observer bands it. Once the seams are visible, one component can change without disturbing the others, which is the whole reason to have a map.

---

## 11. How the rest of the series fills in the map

The index below is the key between the numbers on the hero figure, the numbering in the notation guide and the cheatsheet, and the running order of the series.

| # | Component | Group | Treated in | Part |
|---|---|---|---|---|
| 01 | Loop | core | [post 03](../03-the-agent-loop/index.md) | I |
| 02 | Tools | feeds | [post 06](../06-tools-bash-code/index.md) | II |
| 03 | State | feeds | [post 08](../08-state-filesystem-git/index.md) | II |
| 04 | Context management | feeds | [post 09](../09-context-management-loop/index.md) | II |
| 05 | Memory | feeds | [post 10](../10-continual-learning-ratchet/index.md) | II |
| 06 | Verification | governs | [post 11](../11-verification-loops/index.md) | III |
| 07 | Hooks | governs | [post 13](../13-hooks-enforcement/index.md) | III |
| 08 | Permissions | governs | [post 14](../14-permissions-sandboxes/index.md) | III |
| 09 | Orchestration | scale | [post 16](../16-multi-agent-orchestration/index.md) | IV |
| 10 | Long-horizon patterns | scale | [post 18](../18-long-horizon-ralph/index.md) | IV |
| 11 | Observability | governs | [post 21](../21-observability-traces/index.md) | V |

Note what the table does *not* say. The four *governs* components do not all sit in Part III: verification, hooks and permissions do, and observability lands in Part V. Five further posts treat how components **combine** rather than any single one: [post 07](../07-skills-mcp-runtime/index.md) (skills and MCP extend the tool surface at runtime), [post 12](../12-planner-generator-evaluator/index.md) (splitting the loop's roles), [post 15](../15-human-in-the-loop/index.md) (human approval as a policy on 08), [post 17](../17-parallel-agents-shared-repo/index.md) (many agents on one repository, coordinating through the repository itself rather than through a lead), and [post 19](../19-loop-engineering/index.md) (designing the loop that drives everything else). Five more treat the discipline around the map rather than its parts: [post 04](../04-harness-beats-model/index.md) (the evidence), [post 05](../05-agent-failure-modes/index.md) (the failure catalogue), [post 20](../20-sdk-landscape/index.md) (the prebuilt and custom split read as a purchasing decision), [post 22](../22-evaluating-harnesses/index.md) (evaluation) and [post 23](../23-economics-haas/index.md) (economics). Posts 24 to 26 assemble the whole map into working code.

The [cheatsheet](../../CHEATSHEET.md) carries the eleven components, the loop's four exits and the failure-mode-to-fix table on one printable page, and every later post opens by pointing at the component it fills in.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A feed fix for a govern failure.** The agent ships unverified work, so the team adds more context about the task. The symptom is the same false "done", now with a longer prompt and a higher bill per call.
- **A memory line taken for enforcement.** A convention is written into the memory file and nothing checks it. It holds for a few sessions, then a long run drifts off it again: silent drift, with the rule still sitting in the file.
- **The SDK counted as the whole harness.** A team adopts an agent SDK and keeps its default permission policy, because "the permissions are handled". The first destructive command runs without an error, because the permission model allowed it; the mechanism was inherited and the policy was never written.
- **A demo without context management.** A loop, tools and a verifier pass every short demonstration. On the first long task the output gets rushed and sloppy as the window fills, and the team blames the model.
- **Orchestration for a narrow task.** A lead agent and three sub-agents are set on work one agent could do. The token bill lands at about fifteen times the chat form rather than four, and the answer is no better.
- **The decoded layers read as architecture.** The seven-layer estimate is quoted in a design review as how Claude Code is built. It is one outside observer's reading, and nothing in it was published by the vendor.

---

## Common pitfalls

1. **Skipping straight to orchestration.** A shaky single-agent harness does not improve by being run in parallel; it costs about fifteen times the chat-form tokens to find that out.
2. **Treating the loop as plumbing.** The loop and its four exits are the core, and stopping is where the hard bugs live.
3. **Rebuilding what is prebuilt.** Most of the mechanism is inherited from an SDK; the leverage is in the custom layer, not in rewriting a loop.
4. **Wiring the map as a monolith.** If changing one component forces changes in four others, the benefit of the anatomy is lost; keep the seams clean.
5. **Adding observability last.** Its post comes late for teaching reasons only; without a trace, debugging is blind from the first run, not the hundredth.

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (personal blog, 19 April 2026; reposted on O'Reilly Radar, 15 May 2026, with the author's permission). The six things a harness includes, the ratchet, the hook examples, and the estimated layered breakdown of Claude Code that he reports from Fareed Khan. The two postings are one article, not two sources.
- Viv Trivedy, "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026). Six harness capabilities derived backwards from wanted behaviour, and the origin of `Agent = Model + Harness`.
- Sanderson Oliveira de Macedo, "What makes a harness a harness: necessary and sufficient conditions for an agent harness" (arXiv:2606.10106, 8 June 2026). The constitutive definition, the inclusion and exclusion test, and the boundaries against frameworks, SDKs and orchestrators.
- Databricks, "What is an AI Agent Harness?" (Databricks blog, 2026). The same ground split into eight building blocks, with sandboxes and guardrails each treated at length.
- ai-boost, "awesome-harness-engineering" (GitHub, 2026). The community reading list this map is checked against; it splits the field into twelve Design Primitives headings.
- Anthropic Engineering, "Building effective agents" (19 December 2024). The simplest-system-that-works default, and the workflow-versus-agent distinction.
- Anthropic Engineering, "How we built our multi-agent research system" (13 June 2025). The 4× and 15× token multipliers, and the evaluation results that make the trade concrete.
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (arXiv, 2022; ICLR 2023). The reason, act, observe loop at the core of the map.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 03 - The agent loop: ReAct, control loops, and stopping](../03-the-agent-loop/index.md):** the core of the map, and the four exits a loop stops on.
- **[Post 20 - The SDK and framework landscape: Agent SDK, LangGraph, and peers](../20-sdk-landscape/index.md):** the prebuilt and custom split as a purchasing decision, with each product shape read in the eleven-component vocabulary.
