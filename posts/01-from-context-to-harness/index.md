# 01 - From context to harness: the third era

> **TL;DR.** Applied large language model (LLM) work has moved through three eras: first the bottleneck was phrasing (prompt engineering), then information (context engineering), and by 2026 it is autonomy and control. The machine built around the model so that it can run on its own is the **harness**, and the line that names it is `Agent = Model + Harness`. This post pins down the vocabulary (model, scaffold, harness, orchestration), shows why context engineering is one component inside the harness, takes a first look at the evidence that the harness is a bigger lever than the model, and says where the harness ends.
>
> **Prerequisites:** none. This is the first post of the series.
> **Safe to skip?** Skip it if the reader can already state `Agent = Model + Harness`, tell a scaffold from a harness and a harness from an orchestrator, and say why context engineering sits inside the harness rather than beside it.
>
> **After reading, you will be able to:**
>
> - State `Agent = Model + Harness`, and place prompt, context and harness engineering on one timeline with the bottleneck of each era.
> - Explain why context engineering is one component inside the harness, using the seam between one model call and the loop that makes it.
> - Use model, scaffold, harness and orchestration precisely, and assign a product, a component or a failure to the right one.
> - Explain why the same model can succeed or fail on one task depending on its harness, in results and in tokens.
> - Say where the harness ends: what belongs to the model, what belongs to orchestration, and where the sources disagree.

![A timeline from 2022 to 2026 with three eras under the axis: prompt engineering in 2022 to 2023, bottleneck phrasing, unit a message; context engineering in 2024 to 2025, information, a window; harness engineering in 2026, autonomy and control, a run. Above it, flags for December 2024, June 2025 and 10 March 2026.](diagrams/01-three-eras.svg)

*Each era kept the work of the one before and widened the surface the engineer works on: a message, then a window, then a whole run.*

---

## 1. The question: why did the name change again?

In 2022 the work was **prompt engineering**: a user typed one message, and the engineer reworded it until the answer improved. By 2024 that name no longer fitted the work, because most of what the model read on a call was not the user's sentence but tools, memory, retrieved chunks and history that an engineer had assembled. The field settled on a new name in mid-2025: **context engineering**, the discipline of assembling that whole window well. Andrej Karpathy popularised the phrase in a post on X in June 2025, and Anthropic Engineering published "Effective context engineering for AI agents" in September 2025 (Karpathy, 2025; Anthropic, 2025). The sibling series, `context-engineering`, tells that story in full from `ctx-001`; this series treats it as background.

By 2026 the name moved again, for the same reason: the surface grew. Models stopped being called once and started to *run*: dozens of turns, tool calls and file edits, minutes or hours of work with no person in the loop. Once a model runs in a loop, a larger surface appears around it: the code that decides which tool to execute, what to do when the tool fails, when to check the work, when to stop, and what the model may never do. Everything around the model that is not the model is the **harness**, and designing it is **harness engineering**.

Faros AI's guide to harness engineering (published 22 May 2026) gives the three eras their dates and their bottlenecks: prompt engineering in 2022 to 2023, when the bottleneck was phrasing; context engineering in 2024 to 2025, when it was information; harness engineering in 2026, when it is autonomy and control (Faros AI, 2026). The figure at the top draws the three on one axis, with three dated articles that shaped the vocabulary.

The eras are cumulative, not replacements. Wording still matters; it is now a few lines inside a system prompt. Window assembly still matters; it is now one component of a running machine. What changes at each step is the *unit of work*: a message, then a window, then a whole run.

---

## 2. If you're not the model, you're the harness

The founding line of the discipline is deliberately blunt. Viv Trivedy's "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026) opens with the equation `Agent = Model + Harness` and the sentence "If you're not the model, you're the harness." A harness, in the same article, is "every piece of code, configuration, and execution logic that isn't the model itself" (Trivedy, 2026).

The **model** supplies the reasoning. The **harness** supplies everything that turns reasoning into reliable action: the loop that drives the model, the tools it acts through, the state it keeps on disk, the verification that checks its work, the hooks that enforce rules in code, the permissions and the sandbox that bound what it can touch, and the observability that lets an engineer see and repair all of it. [Post 02](../02-anatomy-of-a-harness/index.md) names the components one by one. There are eleven: the loop at the centre; four that feed the model (tools, state, context management, memory); four that govern it (verification, hooks, permissions, observability); and two that work at a larger scale than one run (orchestration, long-horizon patterns).

Addy Osmani's "Agent Harness Engineering" (19 April 2026) made the equation widely known, credits Trivedy with it, and states the claim behind it: "A decent model with a great harness beats a great model with a bad harness" (Osmani, 2026). Section 5 takes a first look at the evidence for that claim.

This is not an argument that models do not matter; it is about where the marginal engineering effort now pays off. In the prompt era that was usually a better prompt; for anything agentic in 2026, this series argues, it is usually a better harness.

**Who said what, and when.** The vocabulary is young enough to trace to individual articles, all published within about eighteen months.

| When | Who | What they contributed |
|---|---|---|
| 19 December 2024 | Anthropic Engineering, "Building effective agents" | Agents as "LLMs using tools based on environmental feedback in a loop", the workflow-versus-agent distinction of section 4, and stopping conditions "such as a maximum number of iterations". |
| June 2025 | Andrej Karpathy, on X | Popularised "context engineering", the era before this one. |
| 11 February 2026 | Ryan Lopopolo, OpenAI, "Harness engineering: leveraging Codex in an agent-first world" | The term used by a model provider, with a production case study behind it. |
| 17 February 2026 | Viv Trivedy, LangChain, "Improving Deep Agents with harness engineering" | The same-model, harness-only result of section 5. |
| 10 March 2026 | Viv Trivedy, LangChain, "The Anatomy of an Agent Harness" | `Agent = Model + Harness`, "If you're not the model, you're the harness", and a component list derived from the behaviour an agent needs. |
| 19 April 2026 | Addy Osmani, "Agent Harness Engineering" | Popularised the equation, credited Trivedy with it, and named the ratchet: every mistake becomes a rule. |
| 22 May 2026 | Faros AI, guide to harness engineering | The three-era framing, with a date range and a bottleneck for each era. |
| 25 May 2026 | Hugging Face, "Harness, Scaffold, and the AI Agent Terms Worth Getting Right" | The vocabulary of section 4: model, scaffold, harness, orchestration. |

Model providers adopted the framing as well. Anthropic's Agent SDK documentation (consulted October 2026) says the software development kit (SDK) gives "the same tools, agent loop, and context management that power Claude Code", and OpenAI put the word in the title of its own account (Anthropic, Claude Agent SDK documentation; OpenAI, 2026). Osmani credits Trivedy with coining the term; it was already in print in February 2026, in OpenAI's account of 11 February and LangChain's write-up of 17 February. The phrasing varies; the substance does not: the engineering that decides whether an agent works has moved outside the model.

---

## 3. Context engineering is a component inside the harness

A reader arriving from the sibling series may reasonably ask whether this is context engineering under a new name. It is not, and the relationship is precise.

**Context engineering designs what the model sees on a single call.** Harness engineering designs the *machine that decides which calls to make, in what order, with what tools, and when to stop.* Assembling the window is one of the harness's jobs, a large one, which post 02 names context management; it sits beside the loop, the tools, verification and the rest. LangChain's write-up of 17 February puts the relationship in one line: "Part of harness engineering is building a good delivery mechanism for context engineering" (Trivedy, 2026). Context engineering is a component *inside* harness engineering.

The seam is easiest to see in code. `snippets/harness_loop.py` runs both units of work offline, against a scripted model that answers in the shape a provider application programming interface (API) does, so it needs no key and no network. The context-engineering unit of work is one request object and one answer:

```python
def one_call(model, task, memory=(), retrieved=()):
    # The whole job is this object: which layers, in which order, at what cost.
    request = {
        "system": SYSTEM,          # scaffold: the system prompt
        "tools": TOOLS,            # scaffold: what the model may reach for
        "messages": [*memory, *retrieved, {"role": "user", "content": task}],
    }
    return model.create(**request)
```

The harness unit of work is the same call inside a machine that decides how many times to make it and when to give up:

```python
def run_loop(model, task, max_iters=12, token_budget=None, window=None):
    messages = [{"role": "user", "content": task}]
    read = written = 0
    recent = []
    for turn in range(1, max_iters + 1):                     # exit (2): the iteration cap
        resp = model.create(system=SYSTEM, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp["content"]})
        read += resp["usage"]["input"]
        written += resp["usage"]["output"]
        if resp["stop_reason"] == "end_turn":                # exit (1): a final answer
            return {"exit": "completed", "turn": turn, "read": read, "written": written}
        if token_budget and read + written >= token_budget:  # exit (3): the budget
            return {"exit": "budget", "turn": turn, "read": read, "written": written}
        recent = (recent + [resp["tool_calls"]])[-(window or 1):]
        if window and len(recent) == window and recent.count(recent[0]) == window:
            return {"exit": "no_progress", "turn": turn, "read": read, "written": written}  # (4)
        messages.append({"role": "user", "content": run_tools(resp["tool_calls"])})
    return {"exit": "max_iters", "turn": max_iters, "read": read, "written": written}
```

Everything in the second block that is not the `create` call is harness: the four exits, (1) final answer, (2) iteration cap, (3) budget and (4) no progress, spelled `completed`, `max_iters`, `budget` and `no_progress` in code; the dispatch of whichever tool the model asked for; and the decision to append the result rather than start a fresh conversation. All of it lives outside the model and outside the window. The scripted model reads a file, runs the tests, and then asks for the same failing edit on every turn. Running `uv run python posts/01-from-context-to-harness/snippets/harness_loop.py` from the series root prints:

```text
one call: one request, one answer: 'Done.'
loop, model answers on turn 4: completed on turn 4, 24,800 tokens
loop, doom loop, cap only: max_iters on turn 12, 132,000 tokens
loop, doom loop, no-progress window of 3: no_progress on turn 5, 34,000 tokens
```

The same stuck model costs 132,000 tokens when only the cap can stop it and 34,000 when the loop notices that nothing is changing; section 6 explains the gap. [Post 03](../03-the-agent-loop/index.md) owns the four exits and builds the loop properly, and its companion [`code/03-agent-loop/`](../../code/03-agent-loop/) is a 77-line `loop.py` whose seven tests run with no API key.

Compaction shows the same seam in prose. Deciding *what* to keep when a window fills (which facts survive a summary) is a context-engineering decision, taught in `ctx-012`. Deciding *that the running loop should pause, summarise, offload the transcript to disk and resume* is a harness decision, taught here in post 09. The two meet at the same event and answer different questions.

Most topics the two series share split along that line. Where a post of the sibling series finishes with the window, the post of this series named beside it picks the subject up at the runtime.

| Topic | Context engineering asks | Harness engineering asks |
|---|---|---|
| Model Context Protocol (MCP) | What does a tool's schema cost in the window? (`ctx-015`) | How does the runtime discover and dispatch the call? (post 07) |
| Memory | Which content is episodic, semantic, procedural? (`ctx-016`) | What machinery carries memory across sessions? (post 10) |
| Sub-agents | Is isolation the right context strategy? (`ctx-013`) | Which topology, and who merges the work? (posts 16, 17) |
| Evaluation | Was this output good? (`ctx-020`) | Was this *trajectory* good, and did the harness change help? (post 22) |
| Hooks | Previewed as part of the agentic workflow (`ctx-026`) | Deterministic enforcement at lifecycle points (post 13) |

Token-level detail is linked rather than repeated: attention over a long window is `ctx-003`, prompt caching `ctx-005`, and reranking `ctx-009` and `ctx-011`.

---

## 4. The vocabulary, pinned down

The field's terms are used loosely in casual writing; this series uses them precisely, as the Hugging Face glossary and Anthropic's "Building effective agents" draw them (Hugging Face, 2026; Anthropic, 2024), and as the [notation guide](../../notation_guide.md) fixes them for every post:

- **Model.** The neural network. On its own it only *responds*: text in, text out.
- **Scaffold.** The behaviour-defining layer wrapped around the model: the system prompt, the tool descriptions, how the model's output is parsed, and what it remembers from step to step. The scaffold shapes *what the model sees and how its words are interpreted.*
- **Harness.** The execution layer: it calls the model, executes the tool calls the model asks for, decides when to stop, catches errors and enforces guardrails. The harness is *the runtime that drives the model through repeated cycles.* Osmani's list of examples is the familiar one: "Claude Code, Cursor, Codex, Aider, Cline: these are all harnesses" (Osmani, 2026).
- **Workflow.** A system in which the steps are laid out in advance by code: the path is fixed, and the model fills in the blanks at each stop along it.
- **Agent.** A model plus the scaffold and harness around it, choosing its own path instead of following one laid out for it: the whole thing that can *act*, not just respond.
- **Orchestration.** A layer *above* the harness that coordinates several agents as units. A harness drives one model through its loop; an orchestrator manages many agents. Multi-agent systems (Part IV) are an orchestration concern, which is why post 02 counts orchestration as the one component that lives in the ring above the harness.
- **Context engineering.** The discipline of deciding what the model sees on one call. The sibling series.
- **Harness engineering.** The discipline of designing the machine that decides which calls to make. This series.

The four layers nest, and the figure below draws them as rings: each one wraps the one inside it and depends on it.

![Four concentric rings: model at the centre, then scaffold, harness and orchestration. A table beside them gives what each ring holds and who engineers it: the scaffold belongs to context engineering, the harness to harness engineering, orchestration to Part IV.](diagrams/02-nested-rings.svg)

*Context engineering works on the scaffold ring; harness engineering on the runtime around it; orchestration on how several such agents combine.*

The workflow-versus-agent line is worth pausing on, because it decides whether most of this series is needed at all. A workflow needs almost no harness: the known steps are written as code, and the model is a component inside a pipeline rather than the thing driving it. An agent needs the full component set, because it chooses its own path and something has to bound it, check it and stop it. Anthropic's article puts it as "predictability and consistency for well-defined tasks" against "flexibility and model-driven decision-making" (Anthropic, 2024). An agent is the answer when the steps cannot be enumerated in advance; when they can, a workflow is cheaper, faster and more predictable, whatever it is called.

Keeping the layers apart is not pedantry. "My agent is flaky" is not a diagnosis, and naming the layer names the fix. Most complaints map onto one layer cleanly, and [post 05](../05-agent-failure-modes/index.md) names the failure modes behind the harness rows:

| What the team says | Failure mode (post 05) | Layer | Component to change | Taught in |
|---|---|---|---|---|
| "It says it is done, but it isn't." | victory declaration | harness | verification | post 11 |
| "It gets sloppy as the session runs long." | context anxiety | harness | context management | post 09 |
| "It makes the same edit over and over." | doom loop | harness | loop: the no-progress exit | post 03 |
| "It ignores our conventions every time." | silent drift | harness | memory and hooks: the ratchet | post 10 |
| "It retrieved the wrong file." | none | scaffold | context assembly | `ctx-009` |
| "It ran a destructive command." | destructive action | harness | hooks and permissions | posts 13, 14 |
| "My two agents overwrote each other." | none | orchestration | shared-repository coordination | post 17 |

The table is the compressed form of the series, and the [cheatsheet](../../CHEATSHEET.md) carries its failure-mode form on one page.

**When is it actually a model problem?** An argument that says "check the harness first" is only honest if it also says when to stop checking. Three questions, in order:

1. **Is it a scaffold problem?** If the information the task needs is not in the window at all, or sits where the model will under-attend to it, no loop design rescues it. That is context engineering, and the sibling series is the treatment.
2. **Is it a harness problem?** If the information is there, the individual steps look sound when read one by one, and the run still fails (it stops too early, repeats itself, declares done without checking, or drifts off the project's conventions), the fault is in the machine around the model. This is the large middle case, and it can be fixed today without waiting for a new model.
3. **Is it a model problem?** Only when the right information is demonstrably in the window, in a sensible position, the loop has verified the work, and the model *still* cannot do the task. Then a stronger model is exactly the right move.

This series holds that the third case is rarer than it feels from inside a failing run; section 5 is the first look at why.

---

## 5. A first look at the evidence

The strongest claim of the field is that the harness can matter more than the model. Post 04 grades the evidence for it as **firm** (the same model on the same benchmark, before and after a harness change), **controlled** (a comparison of scaffolds with the model and the tasks held fixed) or **reported** (a claim quoted at one remove, whose model, benchmark or base cannot be checked), and a reported multiple is never promoted to a measured one. This section previews the evidence with those grades.

**The same model moved up a leaderboard on harness changes alone (firm).** In "Improving Deep Agents with harness engineering" (17 February 2026), Trivedy reports that LangChain took its coding agent, `deepagents-cli`, from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points, with the model held fixed at `gpt-5.2-codex`: in leaderboard terms, from just outside the top 30 into the top 5 (Trivedy, 2026). Terminal-Bench 2.0, released on 7 November 2025 by Stanford University and the Laude Institute (launch write-up by Snorkel AI), has 89 human-verified tasks, each run in its own container, and was calibrated to keep frontier models under about a 50% resolve rate (Terminal-Bench, 2025). On 89 tasks, a 52.8% resolve rate is the equivalent of about 47 tasks and 66.5% of about 59, roughly twelve more (this series' arithmetic: 0.528 × 89 = 47.0 and 0.665 × 89 = 59.2; a rate averaged over repeated trials need not be a whole number of tasks). The score is the number that carries the argument; the rank is an illustration, because a rank also moves with how crowded the leaderboard is.

![Two hollow cited marks on a Terminal-Bench 2.0 resolve-rate axis for one model, gpt-5.2-codex: the default harness at 52.8%, about 47 of 89 tasks, and the tuned harness at 66.5%, about 59, a firm gain of 13.7 points.](diagrams/03-same-model-gain.svg)

*Only the harness changed between the two marks; the model, the benchmark and the 89 tasks did not.*

**The changes were plumbing around a fixed model.** The write-up turns three knobs, the system prompt, the tools and the middleware (LangChain's term for hooks around model and tool calls), and sets how much reasoning the model spends at each stage; post 04 tabulates all seven changes. Three carry most of the story, and each maps onto a component named in section 2. First, a system prompt that pushes the agent to test its own work, backed by a `PreCompletionChecklistMiddleware` that intercepts the agent before it exits and reminds it to run a verification pass against the task specification: verification, the fix for declaring victory early. Second, a `LocalContextMiddleware` that maps the working directory and finds the installed tools at start-up, so the agent knows the environment it is standing in: context management. Third, a `LoopDetectionMiddleware` that counts edits to each file and, after a set number, adds a note telling the agent to reconsider its approach: no-progress detection, the fix for doom loops. No model change, 13.7 points.

**What the work looks like in production.** OpenAI's "Harness engineering" account describes an internal beta built over five months with no manually written code: on the order of a million lines, roughly 1,500 pull requests opened and merged, by a team that began with three engineers and has grown to seven (OpenAI, 2026; InfoQ, 2026, reports the five months and the million lines). The human work was designing the environment the agents ran in. It is a provider's account of its own project, with no model held fixed and no comparison, so it shows what harness work looks like rather than how large the lever is, and it carries no grade on that scale.

**The larger multiples are softer (reported).** MindStudio's "What Is Harness Engineering?" (8 May 2026) reports that the same model can differ by up to six times in performance across harness designs, and attributes the figure to Stanford and Tsinghua research without linking the comparison (MindStudio, 2026). A reader cannot check the model, the benchmark or the base of that multiple, so it is reported: the direction agrees with the firm result, and the multiple is not a constant to quote. The right response to any such figure is to measure one's own harness ([post 22](../22-evaluating-harnesses/index.md)).

**Most failures are configuration (reported).** HumanLayer's "skill issue" framing, as Osmani reports it, holds that most agent failures come down to configuration rather than model weights (Osmani, 2026). If it holds, most failures are fixable in the harness.

**Models and harnesses are trained together.** Osmani describes a loop he credits to Trivedy: a useful pattern found in a harness is standardised into the product, used when the next models are trained, and the next model gets better at it, which is why a model can feel more capable inside its native harness (Osmani, 2026). A shorter version runs inside one team, under Osmani's name for it: the **ratchet**, in which every mistake becomes a rule (post 10).

The practical rule is not "ignore the model". It is to check whether a gap is a harness gap before reaching for a bigger model.

---

## 6. What a harness gap costs, in tokens

The harness moves quality; the arithmetic of one bad run shows it also moves the bill, faster than intuition suggests, because a loop re-reads its whole transcript on every turn.

Take a loop whose stable prefix (the system prompt plus the tool schemas) is 4,000 tokens, where each completed turn appends about 1,200 tokens to the transcript (the assistant message plus the tool result) and the model writes about 400 tokens: illustrative sizes, not measurements. Turn $n$ therefore reads $4{,}000 + 1{,}200(n - 1)$ tokens. This is the scripted model of section 3: from turn 3 on it makes the same failing edit and tries again. `snippets/exit_cost.py` runs the loop of section 3 against it with one exit enabled at a time, and `uv run python posts/01-from-context-to-harness/snippets/exit_cost.py` prints:

```text
exit enabled                                 fires  turn      read  written     total
iteration cap of 12, nothing else        max_iters    12   127,200    4,800   132,000
token budget of 40,000                      budget     6    42,000    2,400    44,400
no progress, window of 3               no_progress     5    32,000    2,000    34,000
iteration cap of 24, nothing else        max_iters    24   427,200    9,600   436,800
cap of 12 / no progress: 3.88 times
cap of 24 / cap of 12:   3.31 times
```

The cap alone is the expensive option, and not by a small margin: it spends 3.88 times what no-progress detection spends, for exactly the same zero progress. The reason is that the cost of each turn grows with the transcript, so the cost of a doom loop is quadratic in its length rather than linear. Doubling the iteration cap from 12 to 24 does not double the waste; on these sizes it multiplies it by 3.31, to 436,800 tokens. The chart below plots the running total turn by turn.

![A dashed illustrative curve of cumulative tokens against turn for the scripted doom loop, rising from 4,400 on turn 1 to 132,000 on turn 12, with marks where each exit stops it: no progress on turn 5 at 34,000, the budget on turn 6 at 44,400, the cap on turn 12.](diagrams/04-exit-cost.svg)

*The curve bends upward because every turn re-reads all the turns before it; the earlier an exit fires, the less of the curve the run pays for.*

Note also *which* exit is cheapest. The budget stops a run once it has become expensive, a statement about size. No-progress detection stops it once it has become pointless, a statement about shape, and shape is knowable earlier. That is why post 03 treats the four exits as layered rather than interchangeable. [Post 23](../23-economics-haas/index.md) works the same arithmetic in money, with prompt caching, and argues that the number to watch is cost per *successful* run.

---

## 7. Where the harness ends

A definition that covers everything explains nothing, so this series also says what it holds *outside* the harness.

**The model is outside it.** Weights, post-training and the choice between two frontier models are real levers, and none of them is harness engineering. Model choice returns in post 04 as a decision made *after* ruling out a harness gap, and in post 20 as a choice that an SDK can tie a team to.

**Orchestration is above it.** A harness drives one model through one loop. Once several agents are coordinated as units, with work split between them and results merged, that is orchestration, and Part IV is where it lives. Solving the single-agent harness first is not an arbitrary ordering: a multi-agent system built on an unreliable single-agent harness carries that unreliability into every agent it runs.

**The environment is a boundary case, and the sources genuinely differ.** Trivedy's definition is wide: every piece of code, configuration and execution logic that is not the model. OpenAI's account puts much of its engineering into the repository itself (its structure, the continuous integration (CI) configuration, formatting rules, custom linters and the `AGENTS.md` file that tells the agents how to work) and calls it scaffolding. This series scopes the harness to the runtime, the loop and the components around it, and treats the repository and its tooling as *inputs* the harness feeds to the model (posts 08 and 10). Both readings agree that the work sits outside the model; where the wider reading matters, a post flags it.

---

## 8. What this series covers

This series is **framework-agnostic**, like its sibling. Examples are plain Python over the official provider SDKs; a framework (LangGraph and its peers) appears only in post 20, to compare shapes, and is never the protagonist. The 26 posts fall into five parts:

- **Part I, Foundations (posts 01 to 05):** this post, the eleven components, the agent loop and its four exits, the evidence, and the six failure modes (victory declaration, context anxiety, one-shotting, doom loop, silent drift, destructive action).
- **Part II, Core primitives (posts 06 to 10):** tools, skills and MCP, state on disk and in git, context management inside the loop, and the ratchet.
- **Part III, Control and reliability (posts 11 to 15):** verification, the planner, generator and evaluator split, hooks, permissions and sandboxes, and the human in the loop.
- **Part IV, Scale and orchestration (posts 16 to 20):** multi-agent topologies, parallel agents on a shared repository, long-horizon execution, loop engineering, and the SDK landscape.
- **Part V, Production and builds (posts 21 to 26):** observability, evaluation, economics, and three builds: a minimal harness (post 24), the same harness with hooks, a sandbox, an approval gate and a sub-agent (post 25), and a long-running coding-agent capstone (post 26).

By the end of Part I a reader can name the eleven components, write the minimal reason-act-observe loop with its four exits, grade the evidence that the harness is a bigger lever than the model, and diagnose the six failure modes from a trace. Parts II to V go deep on each piece. It is a tutorial, not a survey of every SDK or framework.

---

## 9. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A bigger model for a harness gap.** The loop never verifies its work, so the team upgrades the model. The symptom is the same unfinished task, declared done more fluently, at a higher price per call.
- **Editing the scaffold for a harness fault.** The team adds "stop when the work is done" to the system prompt of an agent that repeats the same edit. The doom loop continues, because nothing in the loop checks whether anything changed.
- **The cap as the only exit.** Every stuck run costs the full cap; section 6 puts it at 3.88 times what no-progress detection spends on the same run.
- **An agent where a workflow would do.** The steps are known, but the team builds a loop that chooses them, and gets runs that are slower, costlier and less predictable than a fixed pipeline.
- **A reported multiple quoted as a measurement.** "Harnesses make models six times better" lands in a design review, and nobody can say six times what, on which benchmark.
- **Going multi-agent before the single harness is reliable.** Two agents that each lack a no-progress exit overwrite each other's files, and the failures multiply.

---

## Common pitfalls

1. **Treating "harness engineering" as a rebrand of "context engineering".** Context management is one component inside the harness, not a synonym for it.
2. **Confusing the scaffold with the harness.** Editing the system prompt (scaffold) will not fix a missing stop condition (harness); name the layer, then fix it.
3. **Confusing a harness with an orchestrator.** Coordinating many agents is a different, higher problem than driving one model well, and it comes after the single-agent harness works.
4. **Reading the leaderboard rank instead of the score.** The rank moves with how crowded the leaderboard is; the 13.7-point score delta on a fixed 89-task benchmark is the number that carries the argument.
5. **Forgetting that each era kept the one before.** The prompt and the window still matter inside a harness; harness engineering adds a runtime around them rather than replacing them.

---

## Further reading

- Viv Trivedy, "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026). The origin of `Agent = Model + Harness`, of the line section 2 is named after, and of the definition of a harness quoted there.
- Viv Trivedy, "Improving Deep Agents with harness engineering" (LangChain blog, 17 February 2026). The primary account of the 52.8% to 66.5% Terminal-Bench 2.0 result and the harness changes behind it.
- Addy Osmani, "Agent Harness Engineering" (19 April 2026). The equation popularised, the ratchet, the model and harness training loop, and the "skill issue" framing reported from HumanLayer.
- Ryan Lopopolo, OpenAI, "Harness engineering: leveraging Codex in an agent-first world" (11 February 2026), with InfoQ's report of 21 February 2026. The production account of section 5 and the wider reading of section 7.
- Anthropic Engineering, "Building effective agents" (19 December 2024). Agents as tools in a loop with stopping conditions, and the workflow-versus-agent distinction of section 4.
- Anthropic, Claude Agent SDK documentation (consulted October 2026). The SDK as the tools, agent loop and context management of Claude Code, as a library.
- Faros AI, guide to harness engineering (22 May 2026). The three eras with their dates and bottlenecks.
- Sergio Paniego and Aritra Roy Gosthipaty, "Harness, Scaffold, and the AI Agent Terms Worth Getting Right" (Hugging Face blog, 25 May 2026). The vocabulary of section 4.
- Terminal-Bench 2.0, Stanford University and the Laude Institute (released 7 November 2025; launch write-up by Snorkel AI). The 89-task benchmark under section 5's result.
- MindStudio, "What Is Harness Engineering?" (8 May 2026). The reported same-model spread of up to six times.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 02 - The anatomy of a harness](../02-anatomy-of-a-harness/index.md):** the eleven components every harness is built from, and the map the rest of the series fills in.
- **[Post 04 - Why the harness beats the model: the evidence](../04-harness-beats-model/index.md):** the evidence of section 5, ranked firm, controlled and reported and argued in full.
