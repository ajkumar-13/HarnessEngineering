# 01 · From context to harness — the third era

> **TL;DR.** Applied large language model (LLM) work has moved through three eras. First the bottleneck was *phrasing* (prompt engineering); then it was *information* (context engineering); by 2026 it is *autonomy and control*: the machine you build around the model so it can run on its own. That machine is the **harness**, and its founding equation is `Agent = Model + Harness`. This post explains what a harness is, why context engineering is a component *inside* it, how the field's vocabulary fits together, and why a growing body of evidence says the harness is a bigger lever than the model.
>
> **After reading this you will be able to:**
> - State, in one sentence, what a harness is and how it differs from a prompt and a context.
> - Place any agent problem in the right layer: model, scaffold, harness, or orchestration.
> - Explain why the same model can succeed or fail on the same task depending on its harness.

![A timeline from 2022 to 2026 across three eras (prompt, context, and harness engineering), each working on a larger surface than the last: a single message, then the whole window, then the whole machine, with the unit of work growing from a message, to a window, to a whole run. Beneath the panels the surface is drawn to scale, and a dated axis records when each name landed, from Anthropic's "Building Effective Agents" in December 2024 through Karpathy in June 2025 to Trivedy on 10 March 2026 and Osmani that April.](diagrams/01-three-eras.svg)
*Three eras, three bottlenecks. The surface the engineer works on grows from a message, to a window, to the entire machine around the model.*

---

## 1. The name changed again

In 2022 the work was **prompt engineering**: you typed one message and reworded it until the answer improved. By 2024 that name no longer fitted the work, because most of what the model read was not the user's sentence but tools, memory, retrieved chunks, and history that an engineer had assembled. The field settled on a new name in mid-2025: **context engineering**, the discipline of assembling that whole window well. Andrej Karpathy popularised the phrase in June 2025, and Anthropic published "Effective context engineering for AI agents" that September (Karpathy, 2025; Anthropic, 2025). The companion *Context Engineering* (CE) series, Post 01, tells that story in full; this series treats it as background.

By 2026 the name has moved again, for the same reason it moved the first time: the surface got bigger. Models stopped being things you call once and started being things that *run*, taking dozens of turns, calling tools, editing files, and working for minutes or hours without a human in the loop. The moment a model runs in a loop, a new and larger surface appears around it: the code that decides what tool to execute, what to do when the tool errors, when to check the work, when to stop, and what the model is never allowed to do. That surface has a name. Everything around the model that is not the model is the **harness**, and engineering it is **harness engineering** (Osmani, 2026; OpenAI, 2026).

The clearest one-line statement of the shift comes from LangChain's Viv Trivedy, who named the discipline in March 2026: "If you're not the model, you're the harness" (Trivedy, 2026). Model providers adopted the same framing within the year. Anthropic's Claude Agent software development kit (SDK) is presented as "the agent harness that powers Claude Code" (Anthropic, 2025–26), and OpenAI titled its own account of the practice "Harness engineering: leveraging Codex in an agent-first world" (OpenAI, 2026).

The three eras are cumulative rather than sequential replacements. Wording still matters; it is now a few lines inside a system prompt. Window assembly still matters; it is now one component of a running machine. What changes at each step is the *unit of work*: a message, then a window, then a whole run.

---

## 2. If you're not the model, you're the harness

The founding equation of the discipline is deliberately blunt (Trivedy, 2026; popularised by Osmani, 2026):

![The equation Agent = Model + Harness as three boxes: Agent equals Model, which supplies reasoning, plus Harness, which holds the loop, tools, state, verification, hooks and sandbox, eleven components in all. Below, three panels give the measured case for the harness term: 52.8% to 66.5% on Terminal-Bench 2.0's 89 tasks with one model held fixed, seven listed changes none of which touched the model, and a production beta of about a million lines across about 1,500 merged pull requests.](diagrams/03-equation.svg)
*`Agent = Model + Harness`. The model is one term in the sum, and often not the one with the most headroom left.*

The **model** supplies reasoning. The **harness** supplies everything that turns reasoning into reliable action: the loop that drives the model, the tools it acts through, the filesystem it keeps state on, the verification that checks its work, the hooks that enforce rules deterministically, the sandbox that bounds the damage it can do, and the observability that lets you see and repair all of it. Post 02 names these components one by one. There are eleven, grouped by what they do to the model: the agent loop sits at the centre, four *feed* it, four *govern* it, and two (orchestration and long-horizon patterns) operate at a larger scale than a single run.

The reason the equation matters is a claim that would have sounded strange in the prompt era and is now widely repeated: "a decent model with a great harness beats a great model with a bad harness" (Osmani, 2026). §5 gives the evidence.

This is not an argument that models don't matter. It is an argument about *where the marginal engineering effort now pays off*. In 2023, the highest-leverage change you could make to an LLM feature was usually a better prompt. In 2026, for anything agentic, the highest-leverage change is usually a better harness.

**Who named it, and when.** The vocabulary is young enough that its provenance is still traceable to individual articles published within about eighteen months of each other, and two of those articles supply the lines this series repeats most.

| When | Who | What they contributed |
|---|---|---|
| December 2024 | Anthropic Engineering, "Building Effective Agents" | The model-plus-loop framing, and the workflow-versus-agent distinction §4 uses. |
| 2025–26 | Anthropic | Shipped the idea as a product: the Claude Agent SDK, "the agent harness that powers Claude Code". |
| 10 March 2026 | Viv Trivedy, LangChain, "The Anatomy of an Agent Harness" | Named the discipline: `Agent = Model + Harness`, "If you're not the model, you're the harness", and the first component list. |
| April 2026 | Addy Osmani, "Agent Harness Engineering" | Popularised the equation, credited Trivedy for it, and added the ratchet principle and the co-training flywheel. |
| 2026 | OpenAI, "Harness engineering: leveraging Codex in an agent-first world" | Made it a provider-level discipline, with a production case study behind it. |
| 2026 | Hugging Face, agent glossary | Pinned the vocabulary §4 uses: model, scaffold, harness, agent, orchestration. |
| 2026 | Faros AI, "Harness Engineering" | The three-era framing this post opens with, and the leaderboard result in §5. |

The phrasing varies between them; the substance does not. Each is pointing at the same shift, which is that the engineering deciding whether an agent works has moved outside the model.

---

## 3. Context engineering is a component inside the harness

Readers arriving from the *Context Engineering* series reasonably ask whether this is context engineering under a new name. It is not, and the relationship is precise.

**Context engineering designs what the model sees on a single call.** Harness engineering designs the *machine that decides what calls to make, in what order, with what tools, and when to stop.* Context engineering is one of the harness's jobs (a large and important one), but it sits alongside the loop, the tools, the verification, and the guardrails. Formally: context engineering is a component *inside* harness engineering (Faros AI, 2026; Hugging Face, 2026).

![Four concentric rings (model, scaffold, harness, orchestration), each band labelled with its share of the seven symptoms in this post's diagnostic table: none on the model, one on the scaffold, five on the harness, one on orchestration. Beside them, four cards give what each layer owns, the complaint that lands there, and the component that answers it, and a panel maps each discipline to the rings it governs: context engineering the inner two, harness engineering the third, gesturing at the fourth.](diagrams/02-nested-rings.svg)
*The layers nest. Context engineering governs the inner rings: what the model sees. Harness engineering governs the machine that drives it. Orchestration governs how several such agents combine.*

The seam is easiest to feel in code. Here is the context-engineering unit of work: one call, one answer, with every decision made about what went into a single object.

```python
# The whole job is this object: which layers, in which order, at what cost.
resp = client.messages.create(
    model=MODEL,
    system=SYSTEM_PROMPT,                    # the scaffold
    tools=TOOL_SCHEMAS,                      # what it is allowed to reach for
    messages=[*memory, *retrieved, {"role": "user", "content": task}],
)
answer = resp.content
```

Here is the harness unit of work: the same call, now inside a machine that decides how many times to make it and when to give up.

```python
messages = [{"role": "user", "content": task}]
for step in range(1, max_iters + 1):              # exit (2): the hard cap
    resp = client.messages.create(model=MODEL, system=SYSTEM_PROMPT,
                                  tools=TOOL_SCHEMAS, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
    if not tool_calls(resp):                      # exit (1): a final answer
        break
    if tokens_used >= token_budget:               # exit (3): the cost ceiling
        break
    if repeating(recent_signatures):              # exit (4): no progress
        break
    messages.append({"role": "user", "content": run_tools(resp)})
```

Everything in the second block that is not the `create` call is harness. The iteration bound, the four exits, the dispatch of whichever tool the model asked for, and the decision to append the result rather than start a fresh conversation are all engineering that lives outside the model and outside the window. Post 03 builds this properly, and the runnable version is [`code/03-agent-loop/`](../../code/03-agent-loop/): a 77-line `loop.py` driven by a scripted offline model, so `python -m pytest -q` runs its seven tests with no application programming interface (API) key. Its four exits are named where the loop can see them, which is the shape every later post refers back to:

```python
class StopReason(str, Enum):
    COMPLETED = "completed"      # (1) the model returned a final answer
    MAX_ITERS = "max_iters"      # (2) hit the hard iteration cap
    BUDGET = "budget"            # (3) ran out of token budget
    NO_PROGRESS = "no_progress"  # (4) the same action repeated with no change
```

A concrete way to feel the same seam in prose: compaction. Deciding *what* to keep when a context window fills (which facts survive a summary) is a context-engineering decision, taught in the CE series. Deciding *that the running loop should pause, summarise, offload the transcript to disk, and resume* is a harness decision, taught here in Post 09. The two meet at the same event and answer different questions.

Most topics the two series share split along that line. The table below is the map between them: where a CE post finishes with the window, the harness post named beside it picks the subject up at the runtime.

| Topic | Context Engineering asks | Harness Engineering asks |
|---|---|---|
| Model Context Protocol (MCP) | What does a tool's schema cost in the window? (CE Post 15) | How does the runtime discover and dispatch the call? (Post 07) |
| Memory | Which content is episodic, semantic, procedural? (CE Post 16) | What machinery carries state across sessions? (Post 10) |
| Sub-agents | Is isolation the right context strategy? (CE Post 13) | Which topology, and who merges the work? (Posts 16, 17) |
| Evaluation | Was this output good? (CE Post 20) | Was this *trajectory* good, and did the harness change help? (Post 22) |
| Hooks | Previewed as part of the agentic workflow (CE Post 26) | Deterministic enforcement at lifecycle points (Post 13) |

Because the two series interlock, this one treats the CE material as background. Where a token-level detail is assumed, it is linked rather than repeated: how attention reads a long window is CE Post 03, what prompt caching is and what it saves is CE Post 05, and how a reranker reorders retrieved chunks is CE Post 09, with the cross-encoder detail in CE Post 11.

---

## 4. The vocabulary, pinned down

The field's terms are used loosely in casual writing; this series uses them precisely (Hugging Face, 2026; Anthropic, 2024):

- **Model.** The neural network. On its own it only *responds*: text in, text out.
- **Scaffold.** The behaviour-defining layer wrapped around the model: the system prompt, the tool descriptions, how the model's output is parsed, and what it remembers from step to step. The scaffold shapes *what the model sees and how its words are interpreted.*
- **Harness.** The execution layer: it calls the model, handles the tool calls the model asks for, decides when to stop, catches errors, and enforces guardrails. The harness is *the runtime that drives the model through repeated cycles.*
- **Workflow.** A system in which the steps are laid out in advance by code: the path is fixed, and the model fills in the blanks at each stop along it (Anthropic, 2024).
- **Agent.** A model plus the scaffold and harness around it, choosing its own path instead of following one laid out for it: the whole thing that can *act*, not just respond.
- **Orchestration.** A layer *above* the harness that coordinates several agents as units. The boundary is clean: a harness drives one model through its loop; an orchestrator manages many agents. Multi-agent systems (Part IV) are an orchestration concern.
- **Context engineering.** The discipline of deciding what the model sees on one call. The prior series.
- **Harness engineering.** The discipline of designing the machine that decides which calls to make. This series.

The workflow-versus-agent line is the one worth pausing on, because it decides whether you need any of this at all. A workflow needs almost no harness: if the steps are known, write them down as code, and the model becomes a component inside a pipeline rather than the thing driving it. An agent needs the full component set, because it is choosing its own path and something has to bound, check, and stop it (Anthropic, 2024). Reach for an agent when the steps genuinely cannot be enumerated in advance. A good number of production "agents" are workflows that would be cheaper, faster, and far more predictable if they admitted it.

Keeping the layers apart is not pedantry. "My agent is flaky" is not a diagnosis, and naming the layer names the fix. Most complaints map onto one layer cleanly:

| What you would actually say | Layer | Component to change | Taught in |
|---|---|---|---|
| "It says it is done, but it isn't." | Harness | Verification | Post 11 |
| "It gets sloppy as the session runs long." | Harness | Context management | Post 09 |
| "It makes the same edit over and over." | Harness | Loop exit (4), no-progress detection | Post 03 |
| "It ignores our conventions every time." | Harness | Memory plus a hook: the ratchet | Post 10 |
| "It retrieved the wrong file." | Scaffold | Context assembly | Context Engineering, Post 09 |
| "It ran a destructive command." | Harness | Deny-list hook plus a sandbox | Posts 13, 14 |
| "My two agents overwrote each other." | Orchestration | Shared-repo coordination | Post 17 |

That table is the compressed form of the series, and a one-page version of it ships in the repository's cheatsheet. Post 05 turns the same material into a catalogue of six named failure modes, which is the form most useful when reading a trace.

**When is it actually a model problem?** An argument that says "check the harness first" is only honest if it also says when to stop checking. Three questions, in order:

1. **Is it a scaffold problem?** If the information the task needs is not in the window at all, or sits where the model will under-attend to it, no loop design rescues it. That is context engineering, and the CE series is the treatment.
2. **Is it a harness problem?** If the information is there, the individual steps look sound when you read them one by one, and the run still fails (it stops too early, repeats itself, declares done without checking, or drifts off the project's conventions) then the fault is in the machine around the model. This is the large middle case, and it is yours to fix today without waiting for anything.
3. **Is it a model problem?** Only when the right information is demonstrably in the window, in a sensible position, the loop verified the work, and the model *still* cannot do the task. Then a stronger model is exactly the right move.

The third case is rarer than it feels from inside a failing run, which is what the evidence in §5 is about.

---

## 5. The evidence: the harness is a real lever

The strongest claim of the field, that the harness can matter more than the model, is not merely rhetorical; it is what practitioners report when they measure. (Post 04 makes this case in full: [Why the harness beats the model](../04-harness-beats-model/index.md).)

**The same model moves up a leaderboard on harness changes alone.** In February 2026 the LangChain team took its coding agent, `deepagents-cli`, from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points that carried it from roughly the top 30 of the leaderboard into the top 5, with the underlying model (`gpt-5.2-codex`) held fixed throughout (Trivedy, LangChain, 2026; reported at one remove in Faros AI, 2026). Terminal-Bench 2.0 is 89 human-verified tasks, each run in its own container against a written oracle solution, scored on whether tests over the final container state pass, and deliberately calibrated so that frontier models score under 50% (Terminal-Bench, Stanford and the Laude Institute, 2025). Across 89 tasks, 52.8% is about 47 resolved and 66.5% is about 59: twelve tasks that the same model, on the same benchmark, could not finish before and could finish after. The score is the load-bearing number here; the rank is the illustration, because rank also moves with how crowded the leaderboard is.

![A leaderboard-rank axis showing one model at about rank 30 in a default harness and about rank 5 in a tuned harness, moving about 25 places with the model unchanged; a box below states Agent = Model + Harness.](../04-harness-beats-model/diagrams/01-harness-gap.svg)
*The same result on a rank axis: one model, two harnesses, about 25 leaderboard places apart. A fixed model cannot move that far on a fixed benchmark unless the harness is the lever.*

**The changes were plumbing around a fixed model.** The write-up lists seven of them and Post 04 tabulates them all; three carry most of the story, and each maps onto a component this post has already introduced. First, a system prompt pushing the agent towards self-verification, backed by a pre-completion checklist that intercepts it before it exits and makes it run a verification pass against the task specification: that is verification, and it is the fix for declaring victory early. Second, tools and context injection that map the working directory and discover the available tooling at start-up, so the agent understands the environment it is standing in: that is context management. Third, middleware hooks that count repeated per-file edits and feed the count back so the agent reconsiders a broken approach: that is no-progress detection, loop exit (4), and the fix for doom loops. No model change, 13.7 points.

**The same effect appears in production, not only on benchmarks.** OpenAI reports an internal team that shipped a production beta of roughly a million lines of code with no line written by hand: every line generated by Codex agents, across about 1,500 merged pull requests over five months, by a team that began with three engineers and grew to seven (OpenAI, 2026). The human work was designing the environment those agents ran in.

**The larger reported multiples are softer.** Secondary write-ups summarising research comparisons put the same-model spread across harnesses at around 6× (MindStudio, 2026). Treat that as reported rather than measured. The direction is unanimous wherever the comparison is run; the exact multiple is not a constant to quote; and the right response to any such figure is to measure your own harness (Post 22).

**Most failures are legible, not mysterious.** The "skill issue" reframe (popularised by HumanLayer, via Osmani, 2026) holds that the majority of agent failures are *configuration* problems, not model-weight problems: a missing convention, an un-enforced rule, a step that was never verified. That is an optimistic claim, because it means most failures are fixable in the harness, by you, today.

**Models and harnesses co-train.** There is a flywheel behind all of this. Useful patterns discovered in harnesses get standardised into products; models are then trained against those patterns and get better at using them; the next harness exploits the improvement (Osmani, 2026). It is why a frontier model can feel noticeably more capable inside its native harness than when dropped into a generic one: the two were shaped together. A shorter version of the same flywheel runs inside a single team, under the name Osmani gives it: the **ratchet principle**, where every mistake becomes a rule, so that a failure seen once is converted into a durable constraint and cannot recur. Post 10 is the mechanism.

The practical takeaway is not "ignore the model." It is: *before you reach for a bigger model, check whether the gap you are seeing is a harness gap.* Very often it is.

---

## 6. What a harness gap costs, in tokens

The leaderboard numbers say the harness moves quality. The arithmetic of a single bad run says it also moves the bill, and it moves it faster than intuition suggests, because a loop re-reads its whole transcript on every turn.

Take a loop whose stable prefix (system prompt plus tool schemas) is 4,000 tokens, where each completed turn appends about 1,200 tokens to the transcript (the assistant message plus the tool result) and the model writes about 400 tokens. Turn *n* therefore reads roughly 4,000 + 1,200(*n* − 1) tokens. Now suppose the agent starts thrashing on turn 3: it makes the same failing edit, reads the same failing test, and tries again.

| Which exit fires | Turn it fires on | Tokens read | Tokens written | Total |
|---|---|---|---|---|
| (2) hard iteration cap of 12, and nothing else | 12 | 127,200 | 4,800 | 132,000 |
| (3) token budget of 40,000 | 6 | 42,000 | 2,400 | 44,400 |
| (4) no-progress detection, window of 3 | 5 | 32,000 | 2,000 | 34,000 |

The cap alone is the expensive option, and not by a small margin: it spends roughly four times what no-progress detection spends, for exactly the same zero progress. The reason is that per-turn cost grows with the transcript, so the cost of a doom loop is quadratic in its length rather than linear. Doubling the iteration cap from 12 to 24 does not double the waste; on these figures it more than triples it, to about 437,000 tokens.

Note also *which* exit is cheapest. The budget ceiling is a blunt instrument: it stops the run once the run has become expensive, which is a statement about size. No-progress detection stops the run once the run has become pointless, which is a statement about shape, and shape is knowable earlier. That ordering is why Post 03 treats the four exits as layered rather than interchangeable, and it is the cheapest available argument for building the fourth one. (Post 23 works the same arithmetic in money, prices one run three ways with prompt caching taken into account, and argues that the number to watch is cost per *successful* run.)

---

## 7. Where the harness ends

A definition that covers everything explains nothing, so it is worth saying what this series holds *outside* the harness.

**The model is outside it.** Weights, post-training, and the choice between two frontier models are real levers, and none of them is harness engineering. Model choice returns in Post 04 as a decision you make *after* ruling out a harness gap, and in Post 20 as a choice the SDK you pick can tie you to.

**Orchestration is above it.** A harness drives one model through one loop. The moment several agents are coordinated as units, with work split between them and results merged, that is orchestration, and Part IV is where it lives. Solving the single-agent harness first is not an arbitrary ordering: a multi-agent system built on an unreliable single-agent harness multiplies the unreliability by the number of agents.

**The environment is a boundary case, and sources genuinely differ.** OpenAI's account counts the repository layout, the continuous integration (CI) configuration, linters and formatters, package-manager setup, and the project instruction file as part of the harness, on the grounds that all of them shape what the agent can reliably do (OpenAI, 2026). This series scopes the harness to the runtime (the loop and the components around it) and treats the repository and its tooling as *inputs* the harness feeds to the model, covered in Posts 08 and 10. Both readings agree on the substance, which is that the work sits outside the model. Where the wider reading matters, it is flagged rather than quietly adopted.

---

## 8. What this series covers

This series is **framework-agnostic**, exactly like its companion. Examples are plain Python and the direct provider and reference agent SDKs; frameworks (LangGraph and peers) appear only when they materially change the shape of a solution, and never as the protagonist. Post 20 surveys the landscape neutrally.

The series goes deep on:

- The **agent loop**: reason→act→observe, and the stop conditions where most bugs actually live (Post 03).
- **Diagnosis and learning**: the evidence behind the harness-beats-model claim, the six named agent failure modes and the component each maps to, and the ratchet that turns every mistake into a durable rule (Posts 04, 05, 10).
- **Tools, code execution, skills, and the Model Context Protocol (MCP)** as the agent's action surface at runtime (Posts 06–07).
- **State and context management inside a running loop**: the filesystem, git, compaction, offloading, and resets (Posts 08–09).
- **Verification and control**: test loops, planner/generator/evaluator splits, hooks as deterministic enforcement, sandboxes, and human-in-the-loop (Posts 11–15).
- **Scale**: multi-agent orchestration, parallel agents on a shared repo, long-horizon and multi-context execution, and loop engineering (Posts 16–19).
- **Production**: observability, harness evaluation, economics, and three build-from-scratch walkthroughs ending in a capstone coding agent (Posts 21–26).

It will *not* be a survey of every SDK or every agent framework. There are surveys; this is a tutorial. By the end of Part I you will have the vocabulary, the component map, and a failure-mode checklist; Parts II–V are depth on each piece.

---

## Common pitfalls

- **Assuming a bigger model will fix an agent that runs badly.** If the loop never verifies its work, a stronger model just declares victory more fluently. Rule out the scaffold and the harness first, in that order (§4, §5).
- **Treating "harness engineering" as a rebrand of "context engineering".** Context is one component inside the harness, not a synonym for it (§3).
- **Confusing the scaffold with the harness.** Editing the system prompt (scaffold) will not fix a missing stop condition (harness). Name the layer, then fix it (§4).
- **Building an agent where a workflow would do.** If the steps are known in advance, code them. An agent is the answer to "the path cannot be enumerated", and it costs you a full harness (§4).
- **Confusing a harness with an orchestrator.** Coordinating many agents is a different, higher problem than driving one model well. Solve the single-agent harness before you go multi-agent (§7).
- **Quoting the reported ~6× model gap as a hard fact.** It reaches you through secondary sources; cite it as reported, and prefer your own measurements (§5, and Post 22).
- **Relying on the iteration cap as the only loop exit.** It is the most expensive way to stop a doom loop, by roughly a factor of four on the arithmetic in §6.

---

## Further reading

- Viv Trivedy, "The Anatomy of an Agent Harness" (LangChain, 10 March 2026): the origin of `Agent = Model + Harness` and of the line §2 is named after, plus the first component list.
- Viv Trivedy, "Improving Deep Agents with harness engineering" (LangChain, 17 February 2026): the primary account of the 52.8% to 66.5% Terminal-Bench 2.0 result, and the seven harness changes behind it.
- Addy Osmani, "Agent Harness Engineering" (April 2026): the equation popularised, the ratchet principle, the co-training flywheel.
- OpenAI, "Harness engineering: leveraging Codex in an agent-first world" (2026): the production case study in §5, and the wider reading of "harness" discussed in §7.
- Anthropic Engineering, "Building Effective Agents" (December 2024): the model-plus-loop framing and the workflow-versus-agent distinction used in §4.
- Anthropic, "Claude Agent SDK" / "Claude Code" documentation (2025–26): "the agent harness that powers Claude Code."
- Faros AI, "Harness Engineering: Making AI Coding Agents Work in 2026": the three-era framing and the leaderboard movement, reported at one remove.
- Hugging Face, "Harness, Scaffold, and the AI Agent Terms Worth Getting Right" (2026): the vocabulary in §4.
- Terminal-Bench 2.0, Stanford University and the Laude Institute (released 7 November 2025; launch write-up by Snorkel AI): 89 containerised, human-verified tasks; the benchmark under §5's headline result.
- MindStudio, "What Is Harness Engineering?" (2026): the reported same-model performance spread.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 02 — The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: the eleven components every harness is built from, and the map the rest of the series fills in.
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: if you would rather start with the machinery: reason→act→observe and the four ways a loop should stop.
- **[Post 04 — Why the harness beats the model](../04-harness-beats-model/index.md)**: the evidence sketched in §5, argued in full.
- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: the six named ways agents fail and the component that fixes each; the diagnostic table in §4, expanded.
- **[The cheatsheet](../../CHEATSHEET.md)** and **[the glossary](../../GLOSSARY.md)**: the one-page version of §4's symptom table, the eleven components, and the which-discipline decision tree, plus every term the series uses. The glossary extends the CE one rather than repeating it.
- **Context Engineering, Post 26, "The modern agentic workflow"**: the preview of this material from the context side. This series is that post expanded into a full treatment.
- **Context Engineering, Post 01, "Why context engineering"**: the prior era, if you are arriving without it.
