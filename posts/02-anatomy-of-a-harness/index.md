# 02 · The anatomy of a harness

> **TL;DR.** A harness looks amorphous, just "everything around the model," until you name its parts. Almost every production harness is built from the same eleven components, organised around one core: the **agent loop**. Four components *feed* the model (tools, state, context management, memory), four *govern* it (verification, hooks, permissions, observability), and two operate at larger *scale* (orchestration, long-horizon patterns). This post lays out that map, says why eleven and not eight or twelve, turns it into a symptom-to-component lookup, distinguishes the prebuilt harness you inherit from the custom layer you add, and shows how the rest of the series fills the map in.
>
> **After reading this you will be able to:**
> - Name the eleven components of a harness and say what each is for.
> - Diagnose an agent failure by pointing at the component responsible.
> - Separate the prebuilt harness you get from a tool from the custom layer your team must build.

![The anatomy of a harness: a central agent loop driving the model through reason, act, and observe, flanked by four components that feed the model, four that govern it, and two that operate at larger scale.](diagrams/01-harness-anatomy.svg)
*The map. One loop at the core; four components feed the model, four govern it, and two operate across agents and across context windows. Ten numbered badges ring the unnumbered core: the loop is component 01, and the badges run 02 to 11 from there.*

Two numbering systems appear on this page and it is worth separating them once. A two-digit **badge** (01 to 11) is a component of the harness, numbered exactly as the figure above and [the one-page cheatsheet](../../CHEATSHEET.md) number them. **Post NN** is a later post in this series. Component 02 is therefore treated in Post 06, and nothing has gone wrong.

---

## 1. Why a map comes first

"My agent is flaky" is not a diagnosis, and "use a better model" is not usually the fix (Post 01, §5). The value of an anatomy is that it turns a vague complaint into a located one. When you can say *which component* is failing, you know which lever to pull.

The map has a centre and three neighbourhoods. The centre is the **loop**, the thing that makes it an agent rather than a single call. Around it, components divide by what they do to the model: some **feed** it information and capability, some **govern** what it is allowed to do and let you see what it did, and two operate at a larger **scale** than a single running agent. The component set is the one that recurs across published breakdowns (Osmani, 2026; ai-boost, 2026); the grouping into three neighbourhoods is this series' own, and §2 says how the counts compare. The rest of this post walks the map. Most of the remaining posts then take one component and go deep; a handful treat how components combine, and §11 says which is which.

One seam needs closing before the walk starts, because [Post 01](../01-from-context-to-harness/index.md) drew a different picture. Post 01 §4 nests four rings: model, scaffold, harness, orchestration. That is the *vocabulary*, and it answers "what kind of thing is this?". The eleven components are the *parts list*, and they answer "what is it made of?". The two pictures interlock rather than compete. The scaffold ring is where the system prompt, the tool descriptions, and the step-to-step memory are **authored**; the harness ring is the runtime that **executes** them, which is why components 04 and 05 appear here even though Post 01 filed their content under the scaffold. Orchestration (09) is the single component that lives in the ring above the harness, which is why §7 calls it the scale tier rather than promoting it out of the list or renumbering everything below it.

---

## 2. Why eleven, and what other people count

There is nothing sacred about eleven. Every source this post draws on splits the same ground differently, and a reader who has read any of them will notice, so it is worth stating plainly what this map merges and what it promotes.

| Source | How it counts | What it names that this map does not | Where that lands here |
|---|---|---|---|
| This series | 11 components around one loop, with orchestration as the scale tier | n/a | n/a |
| Databricks (2026) | 8 foundational components | System prompts; guardrails and human-in-the-loop as one component | System prompts are authored in the scaffold (Post 01 §4); human-in-the-loop is a *policy* on component 08, and gets Post 15 to itself |
| Trivedy, LangChain (2026) | 6 capabilities, derived backwards from behaviour | Sandboxes bundled with execute-and-verify; "battling context rot" as a heading | 06 and 08 split what it bundles; context rot is the problem component 04 exists to solve |
| ai-boost (2026) | 12 "Design Primitives" headings | Planning and task decomposition; debugging and developer experience; human-in-the-loop | Planning is a loop *shape*, treated in Posts 12 and 19; debugging is what component 11 buys you; human-in-the-loop is Post 15 |

Read across the table and the disagreements are mostly about granularity, not about substance. Databricks folds guardrails and human approval into one component where this map keeps enforcement (07) and permissions (08) apart, because in practice they fail differently: a hook that never fires is a bug in your code, and a permission that is too broad is a bug in your policy. Trivedy's list is shorter because it is derived from *behaviour* rather than from architecture: the method runs from the behaviour you want (or want to fix) to the harness design that produces it (Trivedy, 2026), which yields headings shaped like symptoms rather than like boxes. The awesome-harness-engineering catalogue is longer because it is a reading list, and a reading list can afford a heading for developer experience that an architecture diagram cannot.

One component in this map is a heading nowhere else, and that is deliberate. **Hooks and enforcement (07)** is separated from permissions because deterministic code that runs at a lifecycle point is a different mechanism from an allow-list, even though both constrain the agent. A second boundary is drawn on purpose rather than inherited: **long-horizon patterns (10)** is a heading only in Trivedy's list, as *long-horizon autonomous execution*, and it is kept out of context management here because resetting to a fresh window against a written specification is a different operation from compacting the window you have. If those two look like merges to you, merge them; the map still works at nine. What matters is that the parts are named, not that the count is eleven.

---

## 3. The core: the agent loop

Everything hangs off the loop, so it comes first. A harness calls the model, reads the actions the model asks for, executes them, feeds the results back, and repeats. This is the **reason → act → observe** cycle, the pattern named by the ReAct line of work (Yao et al., 2022). Post 03 is entirely about it.

The single most important part of the loop is the least glamorous: **when it stops.** A loop that never stops burns money; a loop that stops too early ships half-done work. Well-built loops carry four layered stop conditions, numbered the same way throughout this series: (1) the model returns a final answer and it is verified, (2) a hard iteration cap is hit, (3) a token or wall-clock budget is exhausted, (4) no progress is detected. A recurring theme of this series, stated here once: *most agent bugs are stop-condition bugs, not reasoning bugs.*

---

## 4. What is constitutive, and what is merely standard

Eleven equal-looking boxes leave an obvious question unanswered: how few of them can a system have and still be a harness? The most precise available answer comes from a conceptual analysis of the term itself, which proposes four **necessary and sufficient** conditions for a system to count as an agent harness (de Macedo, 2026): (i) an agent loop that interleaves reasoning, action and observation; (ii) a tool interface that lets the model perceive and alter its environment; (iii) context management that decides what enters and leaves the context window; and (iv) a control mechanism that verifies and corrects execution. Each is argued to be necessary on its own terms: without the loop it is a single-pass generator rather than an agent, and without context management long tasks become brittle as useful information dilutes.

What the same paper rules *out* is as useful as what it rules in. A harness does not require a multi-agent architecture, any learning or fine-tuning, a particular model, or a user interface (UI). The definition is then operationalised as an inclusion and exclusion test, applied to six real systems (Claude Code, Codex CLI, Aider, Cline, OpenHands and SWE-agent), and used to separate a harness from an agent framework, an agent software development kit (SDK), an integrated development environment (IDE) plugin, an evaluation harness, and an orchestrator (de Macedo, 2026).

Laid over this map, the four conditions land on components **01** (the loop), **02** (tools), **04** (context management) and **06** (verification). Four of the eleven are constitutive; the other seven are standard in production and optional in principle. That is a sharper claim than "almost every production harness has these parts", because it is falsifiable: a system missing any of the four is something else. Post 20 takes up the two nearest of those neighbours, the agent framework and the agent SDK, and sorts them by how much of the loop they own. It also explains a pattern you will meet repeatedly, that a demo built in an afternoon usually has 01, 02 and 06 and is missing 04, which is exactly why it works for ten turns and falls apart at fifty.

---

## 5. Four components that feed the model

These decide what capability and information the model has on each turn. They are where this series overlaps most with context engineering, and where the lens differs, as Post 01 §3 set out.

**02 · Tools and code execution (Post 06).** The agent's hands. By 2026 the settled practice is a small set of general-purpose tools, above all *bash and code execution*, in preference to a large zoo of narrow, bespoke tools, because the model can compose general tools into actions you never pre-built (Osmani, 2026; Trivedy, 2026). Skills and Model Context Protocol (MCP) servers (Post 07) extend this surface at runtime.

**03 · State and filesystem (Post 08).** The model's context window is small and expensive; the filesystem is large and cheap. Writing intermediate results, plans, and artefacts to disk gives the agent a durable memory outside the window, and using **git** for that state adds versioning and rollback: an agent can check out, try, and revert (Osmani, 2026).

**04 · Context management (Post 09).** A long-running loop will fill its window and begin to degrade. This is *context rot*, in the Context Engineering (CE) series' terms, and CE Post 06 catalogues the token-level failure modes this neighbourhood inherits. The harness fights it actively at runtime, and Post 09 sets the corrective moves out as a ladder of rising aggressiveness: **offload** a big tool output to disk and hand back a pointer (write a 2,000-line log to a file, return its path), **clear** tool results that have already been acted on, **compact** the older turns into a summary, and **reset** the window entirely behind a handoff file (ai-boost, 2026). Lower rungs lose less, so they are tried first.

**05 · Memory and continual learning (Post 10).** Feeding knowledge *across* sessions, not just within one. A memory file injected at the start of every session, and the discipline of turning each failure into a durable rule (the **ratchet principle**), is what lets a harness get better over time rather than repeating the same mistakes (Osmani, 2026).

---

## 6. Four components that govern the model

These decide what the model is allowed to do, whether its work is real, and what you can see afterwards. This neighbourhood is what separates a demo from something you would run unattended.

**06 · Verification (Post 11).** The antidote to an agent that declares victory without checking. A verification step (running tests, a self-critique, a schema check) surfaces errors immediately, so a small early mistake does not compound into a wasted run. The operating principle is *success is silent, failures are verbose*: passing checks stay quiet, and failures get injected back into the loop (Osmani, 2026).

**07 · Hooks and enforcement (Post 13).** Some rules are too important to leave to the model's judgement. A hook is deterministic code that runs at a lifecycle point (before a tool call, after a file edit, before a commit) to enforce a rule unconditionally: run the tests after every edit, block `rm -rf` and force-pushes, require approval before opening a pull request (PR) (Osmani, 2026). Hooks are the enforcement half of the ratchet.

**08 · Permissions and sandbox (Post 14).** An agent with real tools has a real blast radius. Sandboxing (allow-listed commands, network isolation, ephemeral runtimes) and structured permissions bound what a run can touch, so a mistake, or a prompt injection reaching a tool, is contained (Databricks, 2026). Which actions a human must approve is a policy on this component, and Post 15 treats it.

**11 · Observability (Post 21).** You cannot improve what you cannot see. A trace of each run (inputs, outputs, tokens, latency, tool calls, sub-agent spans, and the reason the loop stopped) is what lets you localise the failing component and, increasingly, have an agent read its own traces to propose harness fixes (Osmani, 2026). It lands nineteen posts away, in Part V, because tracing is easiest to teach once there is a full harness to trace. That is a teaching order, not a build order: as the pitfalls below say, observability is the component you regret deferring.

---

## 7. Two components that operate at larger scale

The last two are not about one running agent; they are about many agents, or one agent running longer than a single window allows.

**09 · Orchestration (Post 16).** Coordinating several agents as units: the scale tier of the map. The clean boundary from Post 01 is that a harness drives one model through its loop, while an orchestrator coordinates many agents one level up. It is powerful and over-used, and the right default is a single agent with sub-tasks (Anthropic, 2024).

That default is usually argued qualitatively, which makes it easy to wave away. It prices out. Anthropic's report on the multi-agent research system it built gives both halves of the trade in numbers: agents use roughly **four times** the tokens of a chat interaction, and multi-agent systems roughly **fifteen times** (Anthropic, 2025). Work that through on a task whose chat form costs 40,000 tokens.

| Shape | Multiplier | Tokens for a 40k-token task | Cost above the chat |
|---|---|---|---|
| One chat turn | 1x | 40,000 | n/a |
| Single agent in a loop | ~4x | ~160,000 | ~120,000 |
| Orchestrator with sub-agents | ~15x | ~600,000 | ~560,000 |

The coordination tax is the gap between the last two rows: about 440,000 tokens, eleven chats' worth of spend, charged before the answer is any better. The honest other half of the same report is why the pattern survives at all. Token usage alone explained about 80% of the performance variance on their BrowseComp evaluation, and the multi-agent configuration outperformed single-agent Claude Opus 4 by 90.2% on their internal research evaluation (Anthropic, 2025). Spending more tokens is a large part of what buys the improvement, which is exactly why the advice is "needs a real reason" rather than "never". A real reason looks like breadth-first work whose independent paths will not fit in one window. Anything narrower is one agent with sub-tasks.

**10 · Long-horizon patterns (Post 18).** For work that outgrows one context window, such as building a whole project across many sessions, the harness resets to a fresh context against a written specification and repeats, carrying state on disk. The simplest form is the **Ralph loop** (Huntley, 2025); the general practice of designing these loops is **loop engineering** (Post 19).

---

## 8. Reading the map as a diagnostic

A map is only worth carrying if it shortens a search. The way to use this one is to translate the sentence a colleague actually says into a neighbourhood, and then into a component. The table below does that for the six failure modes catalogued in [Post 05](../05-agent-failure-modes/index.md), plus the complaint that arrives when there is no trace.

| What you actually hear | Neighbourhood | Component to change | Treated in |
|---|---|---|---|
| "It said it was done, and it wasn't." | Governs | 06 Verification | [Post 11](../11-verification-loops/index.md) |
| "It gets rushed and sloppy near the end of a long run." | Feeds | 04 Context management: compact or reset | [Post 09](../09-context-management-loop/index.md) |
| "It has been going in circles for twenty minutes." | Core | 01 The loop's no-progress exit, stop condition (4) | [Post 03](../03-the-agent-loop/index.md) |
| "It tried the whole thing in one shot and made a mess." | Core | 01 Loop shape: split the planner from the generator | [Post 12](../12-planner-generator-evaluator/index.md) |
| "It keeps ignoring a convention the team agreed last week." | Feeds, then governs | 05 Memory file, enforced by 07 a hook | [Post 10](../10-continual-learning-ratchet/index.md) |
| "It rewrote a file nobody asked it to touch." | Governs | 07 Deny-list hook, plus 08 a sandbox | [Post 14](../14-permissions-sandboxes/index.md) |
| "It failed, and nobody can say where." | Governs | 11 Observability | [Post 21](../21-observability-traces/index.md) |

Three of those rows are worth reading twice, because they are the ones people get wrong. "It gets sloppy near the end" is routinely treated as a model problem and is almost always a window problem. "It keeps ignoring a convention" spans two neighbourhoods on purpose: writing the rule into a memory file is a *feed* fix and it decays, so the durable version pairs it with an enforcement hook. And "it failed and nobody can say where" is not a symptom of the failing component at all; it is a symptom of the missing one.

For anything the table does not cover, a three-way heuristic does most of the work. If the fix you are reaching for is *more information*, you are in the feeds neighbourhood. If it is *a rule the model cannot skip*, you are in governs. If it is *another agent*, stop and re-read §7 before you spend fifteen times the tokens. This is the same derivation Trivedy (2026) runs in the other direction, from wanted behaviour to harness design; a diagnostic table is that method read backwards from the behaviour you got.

---

## 9. Prebuilt vs custom: which parts you build

Not every component is yours to write. A distinction this series uses throughout runs across the whole map:

- **The prebuilt harness** is what a tool or SDK gives you out of the box. Claude Code, the Codex harness, and the various agent SDKs already ship a loop, tool dispatch, context management, a permission model, and hooks. You inherit these.
- **The custom harness** is the layer your team adds on top: your organisation's conventions in a memory file, your enforcement hooks, your sandbox policy, your tools, your evals. This is where most of the reliability lives, and it is the part no vendor can ship for you.

![Two columns split by a dashed seam: the prebuilt side lists the agent loop, tool dispatch, context management, a hook system, a permission model and a trace format; the custom side lists your memory file, your tools, your evals, your enforcement hooks and your sandbox policy, with arrows pairing the three components that appear on both sides. Below them, three panels carry the questions that settle ownership: does the mechanism differ between tasks inside your organisation, in which case inherit it; would getting it wrong fail silently, in which case own it and test it; and could a competitor copy it from your public documentation, in which case it is prebuilt in all but name.](diagrams/03-prebuilt-vs-custom.svg)
*Tools, hooks, and permissions appear on both sides. The harness ships the machinery; you supply the policy it runs. The evals row is the exception: it carries a post number rather than a component badge, because evaluation (Post 22) is custom-only and has no prebuilt counterpart to pair with.*

Notice that three components appear in both lists. That is not sloppy bookkeeping, it is the shape of the split: an SDK gives you a *hook system*, and you write the *hooks*; it gives you a *permission model*, and you write the *policy*; it gives you *tool dispatch*, and you write the *tools*. The mechanism is inherited and the policy is yours, which is why hearing that a team uses an SDK answers far less about a system than it sounds like it does.

Three questions settle ownership for any component on the map:

1. **Does the mechanism differ between tasks inside your organisation?** If not, inherit it. Nobody's reason-act-observe loop is special enough to justify writing one.
2. **Would getting it wrong fail silently?** If yes, own the policy and test it. A permission set that is too broad emits no error message; neither does a hook that never fires.
3. **Could a competitor copy it from your public documentation?** If yes, it is prebuilt in all but name. If not, it is custom by definition: your conventions, your evals, your enforcement rules.

The smallest instantiation of this map in the series is [`../../code/24-minimal-harness/`](../../code/24-minimal-harness/), the companion to Post 24. It builds three components from scratch and inherits nothing; four engine modules carry them, alongside a demo and one test file:

```
code/24-minimal-harness/src/minimal_harness/
├── harness.py    # 01  the loop, and its four layered exits
├── tools.py      # 02  schema-validated registry, deny-listed bash
├── verify.py     # 06  the verification gate
└── models.py     #     the provider seam; ScriptedModel keeps it offline
```

The loop's exits are the whole point, and they are worth seeing as code rather than as prose. This is `harness.py`, lightly elided:

```python
class StopReason(str, Enum):
    COMPLETED = "completed"      # (1) a final answer that PASSED the gate
    MAX_ITERS = "max_iters"      # (2) hit the hard iteration cap
    BUDGET = "budget"            # (3) ran out of token budget
    NO_PROGRESS = "no_progress"  # (4) the same action repeated with no change

# ... inside run(), when the model proposes a final answer the GATE decides:
if resp.is_final():
    candidate = Candidate(resp.text, workspace)
    verdict = verify(candidate) if verify else VerifyResult(True)
    if verdict.ok:
        # stop (1): the only exit that returns verified work
        return Result(resp.text, StopReason.COMPLETED, True, step,
                      tokens_used, "", messages)
    messages.append({"role": "user",
                     "content": f"verification failed: {verdict.report}"})
```

Hold that against §4 and something instructive falls out: Build #1 satisfies three of the four constitutive conditions and skips the third. There is no compaction anywhere in `harness.py`, which is precisely why its default `max_iters` is 12 rather than 200. The governing components arrive separately, in [`../../code/25-harness-plus/`](../../code/25-harness-plus/), as five small modules: `hooks.py` (07), `sandbox.py` (08), `approval.py` (Post 15's policy on 08), `observe.py` (11), and one that belongs to the scale tier, `subagent.py` (09). Both companions run offline against a scripted model, so neither needs a network or an application programming interface (API) key.

The practical consequence is that harness engineering is rarely "build a loop from scratch". It is more often *choosing a prebuilt harness well and then engineering the custom layer that makes it trustworthy for your task.* Posts 24 to 26 build one from scratch anyway, not because you always should, but because doing it once is the fastest way to understand what the prebuilt ones are doing for you.

---

## 10. A mature harness, decoded

It helps to see the map instantiated in something large. The clearest public picture of a mature harness is Fareed Khan's breakdown of Claude Code's architecture, which Osmani reports and explicitly labels an *estimate* rather than published architecture (Osmani, 2026). Read with that caveat firmly attached, the same component map resolves into seven recognisable layers: an **input layer** (the UI, sessions, permission gates), a **knowledge layer** (skills, context compaction, task state, memory), an **integration layer** (the MCP runtime and external servers), an **execution layer** (tool dispatch, the streaming runtime, prompt caching), an **output layer** (streaming and formatting the result back to the surface it came from), an **observability layer** (an event bus, background execution), and a **multi-agent layer** (sub-agent coordination, isolation via worktrees).

![A mature harness in six stacked bands, each naming what it holds and which numbered components of the map it covers: input (UI, sessions, permission gates; component 08), knowledge (skills, compaction, task state, memory; components 02 to 05), integration (the MCP runtime and external servers; component 02), execution (tool dispatch, streaming runtime, prompt caching; components 01 and 02), observability (an event bus, background execution; component 11), and multi-agent (sub-agent coordination, worktree isolation; component 09), closed by three notes: on the seventh layer folded into execution, on the three components that get no band at all, and on the estimate the whole breakdown rests on.](diagrams/02-layered-harness.svg)
*The same harness, regrouped as the layers of a shipping system, from an estimated breakdown rather than published architecture. Read top-down: input at the surface, the multi-agent layer at the base. The figure draws six bands, folding output into execution, because at this resolution the two share one path.*

The point of the exercise is not the specific names, and it is certainly not that this is how Claude Code is really built. It is that a real, shipping harness is not a monolith with a clever prompt inside; it is the component map above, wired together, whichever way an outside observer chooses to band it. Once you can see the seams, you can change one component without disturbing the others, which is the whole reason to have a map.

---

## 11. How the rest of the series fills in the map

The index below is the key between the badges on the figure, the numbering on the cheatsheet, and the running order of the series.

| # | Component | Neighbourhood | Treated in | Part |
|---|---|---|---|---|
| 01 | Agent loop | Core | [Post 03](../03-the-agent-loop/index.md) | I |
| 02 | Tools and code execution | Feeds | [Post 06](../06-tools-bash-code/index.md) | II |
| 03 | State and filesystem | Feeds | [Post 08](../08-state-filesystem-git/index.md) | II |
| 04 | Context management | Feeds | [Post 09](../09-context-management-loop/index.md) | II |
| 05 | Memory and continual learning | Feeds | [Post 10](../10-continual-learning-ratchet/index.md) | II |
| 06 | Verification | Governs | [Post 11](../11-verification-loops/index.md) | III |
| 07 | Hooks and enforcement | Governs | [Post 13](../13-hooks-enforcement/index.md) | III |
| 08 | Permissions and sandbox | Governs | [Post 14](../14-permissions-sandboxes/index.md) | III |
| 09 | Orchestration | Scale | [Post 16](../16-multi-agent-orchestration/index.md) | IV |
| 10 | Long-horizon patterns | Scale | [Post 18](../18-long-horizon-ralph/index.md) | IV |
| 11 | Observability | Governs | [Post 21](../21-observability-traces/index.md) | V |

Note what the table does *not* say. The four *governs* components do not all sit in Part III: verification, hooks and permissions do, and observability lands in Part V. Five further posts treat how components **combine** rather than any single one: [Post 07](../07-skills-mcp-runtime/index.md) (skills and MCP extend the tool surface at runtime), [Post 12](../12-planner-generator-evaluator/index.md) (splitting the loop's roles), [Post 15](../15-human-in-the-loop/index.md) (human approval as a policy on 08), [Post 17](../17-parallel-agents-shared-repo/index.md) (many agents on one repository, coordinating through the repository itself rather than through a lead), and [Post 19](../19-loop-engineering/index.md) (designing the loop that drives everything else). Four more treat the discipline around the map rather than its parts: [Post 04](../04-harness-beats-model/index.md) (the evidence), [Post 05](../05-agent-failure-modes/index.md) (the failure catalogue), [Post 22](../22-evaluating-harnesses/index.md) (evaluation) and [Post 23](../23-economics-haas/index.md) (economics), while [Post 20](../20-sdk-landscape/index.md) reads §9's split as a purchasing decision. Posts 24 to 26 assemble the whole map into working code.

Keep the map nearby. [The one-page cheatsheet](../../CHEATSHEET.md) carries the eleven components, the loop's four exits, and the failure-mode-to-fix table on a single printable page, and every later post opens by pointing at the component it fills in, so you always know where you are.

---

## Common pitfalls

- **Skipping straight to orchestration.** Multi-agent systems are the last neighbourhood on the map for a reason; a shaky single-agent harness does not improve by being run in parallel, and it costs roughly fifteen times the tokens to find that out (§7).
- **Treating the loop as an afterthought.** The loop and its four stop conditions are the core, not plumbing. Most bugs live there (§3).
- **Building every component yourself.** Much of the map is prebuilt; the leverage is in the custom layer, not in re-implementing a loop (§9).
- **Confusing "feeds" with "governs".** Adding more context (a *feed* fix) will not stop an agent that ships unverified work (a *govern* fix). Locate the failure in the right neighbourhood (§8).
- **Shipping without component 04.** A demo with a loop, tools and a verifier looks complete and is missing a constitutive part; it will work for ten turns and fail at fifty (§4).
- **Wiring the map as a monolith.** If changing one component forces you to touch four others, you have lost the benefit of the anatomy. Keep the seams clean (§10).
- **Adding observability last.** Its post is late in the series for teaching reasons only. Without a trace you are debugging blind from the first run, not the hundredth (§6).

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (personal blog, April 2026; reposted on O'Reilly Radar, 15 May 2026, with the author's permission): the component breakdown, and the layered decomposition of a mature harness that he reports from Fareed Khan's estimate. The two are one article, not two sources.
- Viv Trivedy, "The Anatomy of an Agent Harness," LangChain blog (10 March 2026): six harness capabilities derived backwards from wanted behaviour, and the origin of `Agent = Model + Harness`.
- Sanderson Oliveira de Macedo, "What makes a harness a harness: necessary and sufficient conditions for an agent harness" (arXiv:2606.10106, 2026): the constitutive definition, the inclusion and exclusion test, and the boundaries against frameworks, SDKs and orchestrators.
- Databricks, "What is an AI Agent Harness?" (2026): the same ground split into eight foundational components, with the sharpest treatment of sandboxing and isolated execution.
- ai-boost, "awesome-harness-engineering" (2026): the community reading list this map is checked against; it splits the field into twelve Design Primitives headings, and §2 says where the two differ.
- Anthropic Engineering, "Building Effective Agents" (December 2024): the simplest-system-that-works default, and the workflow-versus-agent distinction.
- Anthropic Engineering, "How we built our multi-agent research system" (June 2025): the 4x and 15x token multipliers, and the eval results that make the trade concrete.
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022): the reason→act→observe loop at the core of the map.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: the core of the map, and the four ways a loop should stop.
- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the first *feeds-the-model* component, and why a few general tools beat a zoo of narrow ones.
- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: §8's table expanded into six named modes, each with its detection signals and its harness fix.
- **[Post 01 — From context to harness](../01-from-context-to-harness/index.md)**: the four-ring vocabulary this parts list sits inside, if you arrived here first.
