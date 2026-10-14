# 04 - Why the harness beats the model: the evidence

> **TL;DR.** The founding claim of harness engineering is that, for a given model on a given agentic task, the harness often moves performance more than a plausible model swap would. This post grades the evidence as firm, controlled or reported (a same-model gain of 13.7 points on Terminal-Bench 2.0, a controlled scaffold comparison worth up to 28 points, a peer-reviewed interface-only ablation), says what it does not show, explains how models are coupled to the harnesses they were trained in, and turns it into a three-run test and an order of moves: rule out a harness gap before paying for a bigger model.
>
> **Prerequisites:** [post 01](../01-from-context-to-harness/index.md).
> **Safe to skip?** Skip it if the reader can already grade a harness result as firm, controlled or reported, say why a leaderboard rank is weaker evidence than a score, and run a test that separates a harness problem from a model problem.
>
> **After reading, you will be able to:**
>
> - State the claim that the harness beats the model with its scope, and say what it does not claim.
> - Grade a harness performance claim as firm, controlled or reported, and say what each published result does not show.
> - Explain how co-training couples a model to its harness, and why the best harness for a task need not be the one the model was trained in.
> - Run the three-run test that tells a harness problem from a model problem, and read its verdict.
> - Order the moves for an underperforming agent, and show why a harness fix bought once beats a model upgrade paid on every run.

![A dot plot of five cited results, each one model under a weaker and a stronger harness: Terminal-Bench 2.0, 52.8% to 66.5%, firm; two models on a tau-squared-bench subset, 33% to 53% and 43% to 53%, firm; SWE-bench Lite, 11.0% to 18.0%, controlled; GAIA Level 2, 56% to 84%, controlled. A sixth row, the reported sixfold spread, has no marks: it names no model, benchmark or base.](diagrams/01-graded-evidence.svg)

*Every graded result holds the model fixed and moves the score; the reported multiple cannot even be plotted.*

---

## 1. The question: how strong is the evidence?

The claim in one sentence: **for a given model on a given agentic task, the harness often moves performance more than a plausible model swap would.** [Post 01](../01-from-context-to-harness/index.md) gave the slogan, Addy Osmani's "A decent model with a great harness beats a great model with a bad harness" (Osmani, 2026), and took a first look at the evidence. This post asks how strong that evidence is and what it does not show.

The claim has a formal statement in the literature. Zhang et al. ("Stop Comparing LLM Agents Without Disclosing the Harness", 7 May 2026) call it the **Binding Constraint Thesis**: for long-horizon tasks across models of comparable frontier capability, "performance variance is governed more by harness configuration than by model choice" (Zhang et al., 2026). They treat the harness as the controller of a closed-loop system and the large language model (LLM) as the stochastic policy it governs, which is why a small harness change can shift performance by more than substituting one model for another.

The claim is easy to overreach, so its limits come first:

- It is **not** "models do not matter." A more capable model raises the ceiling for every harness; the claim is about where the marginal engineering effort pays off today.
- It is **not** "any model with a good harness beats any model." Call the limit the **scaffolding ceiling**: once the harness supplies the right tools, context and control flow, what binds is whether the frozen weights can use them. Guo et al.'s survey of agent and harness design (14 June 2026) asks whether the bottleneck sits in the model, the harness or the coupling between them, and argues that agent quality emerges from their interaction with the task and the evaluation, not from the model or the harness alone (Guo et al., 2026).
- It **is** a claim about one model and one task: hold those fixed, and the harness is the larger lever.

The split between the two terms of `Agent = Model + Harness` is visible in code. `uv run python posts/04-harness-beats-model/snippets/harness_knobs.py` reads the signature of `run()`, the entry point of this series' minimal build in [`code/24-minimal-harness/`](../../code/24-minimal-harness/), and sorts its parameters:

```text
run() takes 9 parameters
the model:   model
the task:    task
the harness: registry, system, verify, workspace, max_iters, token_budget, no_progress_window (7)
```

The other seven are the harness: the tools (`registry`), the system prompt, the verification gate, the workspace, and exits (2) to (4) of [post 03](../03-the-agent-loop/index.md), the iteration cap, the budget and the no-progress window; exit (1), a final answer, is what the verification gate checks. The claim is that on a real task, tuning those seven moves the outcome more than swapping `model`.

The evidence comes in three grades, used for every performance claim in this series ([notation guide](../../notation_guide.md)):

- **Firm:** the same model on the same benchmark, before and after a harness change.
- **Controlled:** a comparison of scaffolds with the model and the tasks held fixed, set up as a study.
- **Reported:** a claim quoted at one remove, whose model, benchmark or base cannot be checked.

A reported multiple is never promoted to a measured one. The figure at the top plots every graded result of this post on one axis, and the sections below take them strongest first.

---

## 2. The firm evidence: one model, one benchmark, seven harness changes

The cleanest public result is a before-and-after with the weights pinned. In "Improving Deep Agents with harness engineering" (LangChain blog, 17 February 2026), Viv Trivedy reports that LangChain took its coding agent, `deepagents-cli`, from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points, keeping the model fixed at `gpt-5.2-codex` and changing only the harness (Trivedy, 2026). In leaderboard terms the agent went "from Top 30 to Top 5", the baseline having been "just outside the Top 30 of the leaderboard" at the time. This is the firm grade: one model, one benchmark, a harness change in between.

Terminal-Bench 2.0, released by Stanford University and the Laude Institute on 7 November 2025, has 89 human-verified tasks, each run in its own container with tests that check the final state; the LangChain runs used the Harbor runner, which starts a sandbox per task, drives the agent loop and scores the result (Terminal-Bench, 2025; Trivedy, 2026). On 89 tasks the gain is $0.137 \times 89 = 12.2$ tasks' worth of resolve rate, about 47 tasks rising to about 59 (this series' arithmetic).

The deduction runs on the **score**, not the rank. Fixed tasks, fixed weights, and 13.7 more points of resolve rate: that capability was in the model all along and was not being drawn out. The rank is the weaker number, because it also moves with how crowded the leaderboard is: the same 13.7 points could move two places on a sparse leaderboard and twenty on a crowded one (illustrative numbers).

The write-up lists what was changed. It turns three knobs, the system prompt, the tools and the middleware (LangChain's term for hooks around model and tool calls), and sets how much reasoning the model spends at each stage. The article does not number its changes; this series counts seven, and the mapping onto components and failure modes is this series' reading, not LangChain's:

| Change, as the write-up describes it (Trivedy, 2026) | Component | Failure mode it targets |
| --- | --- | --- |
| System-prompt guidance for a build-verify loop: planning and discovery, build, verify, fix | verification | victory declaration |
| `PreCompletionChecklistMiddleware`: "intercepts the agent before it exits and reminds it to run a verification pass against the Task spec" | verification | victory declaration |
| `LocalContextMiddleware`: maps the working directory and its parent and child directories at start-up, and runs bash commands to find tools such as Python installations | context management | none of the six: an agent that does not know its environment |
| Prompting for testable code: file paths in the task specification followed exactly, edge cases tested, work measured against programmatic tests | context management | none of the six: work a grader cannot check |
| Injected time-budget warnings that nudge the agent to finish and shift to verification | loop (the budget, made visible to the model) | none of the six: a run that times out |
| `LoopDetectionMiddleware`: tracks per-file edit counts through tool-call hooks and suggests reconsidering the approach after N edits to the same file | hooks | doom loop |
| An "xhigh-high-xhigh" reasoning sandwich: more reasoning on planning and verification than on the build between them | none of the eleven: a model setting the harness chooses | none of the six |

The figure below places each change on one run: every change sits around the model call, and none touches the weights.

![One Terminal-Bench run left to right in three phases, plan and discover, build, verify and fix, around one unchanged model, gpt-5.2-codex. The system prompt spans the run; the reasoning setting reads xhigh, high, xhigh. Local context acts at the start, loop detection on repeated edits, time-budget warnings along the run, and the pre-completion checklist as a gate at the exit.](diagrams/02-changes-around-the-model.svg)

*Seven changes, all in the system prompt, the middleware or the run settings; the model is the one thing that stayed the same.*

Two caveats belong with the result. The source publishes no per-change delta, so the table attributes kind, not size. Its one isolated comparison is about the reasoning setting: `xhigh` throughout scored 53.9%, "due to agent timeouts", against 63.6% at `high` (Trivedy, 2026). And this is one team's iterative campaign against one benchmark, a limit taken up below.

The same team ran a second firm experiment. "Tuning Deep Agents to Work Well with Different Models" (LangChain blog, 29 April 2026) starts from "A single harness can't be optimal for every model" and builds per-model profiles: overrides for the system prompt, the tools and their names, the middleware, the sub-agents and the skills. On a curated subset of harder τ²-bench tasks, a profile moved GPT-5.3-Codex from 33% to 53% and Claude Opus 4.7 from 43% to 53%, each against the default harness with the same model (Trivedy and Daugherty, 2026). That is firm, with one qualification: the team that tuned the harness chose the subset.

---

## 3. The controlled evidence: hold the model, vary the scaffold

A single team's before-and-after is a strong existence proof and a weak generalisation. Two studies built as comparisons carry the generalisation.

The first is Jason Starace's "Scaffold Effects on GAIA: A Controlled Comparison" (7 June 2026), a pre-registered study of three scaffolds (ReAct; planner-actor-rater, a multi-agent design; and planner-then-executor) across five models from three providers (Claude Opus 4.7, Claude Sonnet 4.6, Claude Haiku 4.5, Gemini 3.1 Pro Preview and GPT-5.5) on the validation questions of GAIA, a benchmark of questions for general assistants, at Levels 1 and 2, with tasks and conditions held fixed and three attempts per question. The finding: "Scaffold choice alone moves measured accuracy by as much as 28 percentage points within a single model." The cell is Claude Opus 4.7 at Level 2, where planner-actor-rater scored 84% and ReAct 56%, on the paper's robust slice, which drops the attempts hit by a provider software bug (Starace, 2026). This is the controlled grade.

Its conclusion is the sharper half: "single-scaffold capability numbers are scaffold-conditional estimates and that the elicitation gap is not guaranteed to shrink as models improve" (Starace, 2026). The **elicitation gap**, a term the paper takes from earlier work at METR on agent time horizons, is the distance between what a model can do and what its scaffold lets it do: what [post 01](../01-from-context-to-harness/index.md) calls a harness gap. Starace pre-registered the prediction that more capable models would be less sensitive to the scaffold, and the data rejected it in direction: the most capable Anthropic model gained the most from structured scaffolds at the harder level. Waiting for the next model is a strategy only if the gap closes on its own, and the controlled evidence says it is not guaranteed to.

The second result predates the vocabulary. SWE-agent (Yang et al., first posted May 2024; NeurIPS 2024) changed only the interface a model acts through: an agent-computer interface (ACI) of a few well-shaped commands for viewing, searching and editing files, with guardrails and concise feedback after every action. With GPT-4 Turbo it resolved 12.47% of the full SWE-bench test set, 286 of 2,294 tasks, against a previous best of 3.8% from a non-interactive, retrieval-augmented system (Yang et al., 2024); that 3.8% belongs to a different model, Claude 3 Opus, in a different setting, so it is not a harness-only comparison. The harness-only comparison is the paper's ablation on SWE-bench Lite, 300 tasks: with GPT-4 Turbo held fixed, the ACI resolved 18.0% against 11.0% for an agent given only the default Linux shell, which the authors report as a 64% relative increase. That is controlled, peer-reviewed, and about twenty-one months older than the February 2026 articles that named harness engineering.

---

## 4. The softer evidence: reported multiples, treated as reported

Beyond the studies, stronger-sounding figures circulate: that the same model varies several-fold across harnesses. MindStudio's "What Is Harness Engineering?" (8 May 2026) says that "the same underlying model can produce performance gaps of up to 6x depending on how the agent wrapper" is designed, and attributes the figure to Stanford and Tsinghua research without linking it (MindStudio, 2026). The article names no model, no benchmark and no baseline for the figure, so a reader cannot check what the multiple is a multiple of. It is reported: the honest use of it is "large, and in the same direction as the firm results", never "six times".

The contrast generalises into a checklist. Five questions grade any harness performance claim, including the ones in this post:

| Question to ask of the claim | LangChain, +13.7 points | Starace, up to 28 points | The reported 6x |
| --- | --- | --- | --- |
| Is the model named and held fixed? | Yes: `gpt-5.2-codex` | Yes: five models, each held fixed | Not stated |
| Is the benchmark and its version named? | Yes: Terminal-Bench 2.0 | Yes: GAIA validation, Levels 1 and 2 | Not stated |
| Is the harness specification published? | The changes are listed | Three named scaffolds, pre-registered | No |
| Controlled comparison, or a snapshot? | Iterative before-and-after, one team | Controlled, three attempts per question | Unknown |
| Score delta, or rank delta? | Score: +13.7 points | Score: percentage points | A multiple, base unstated |

A claim that answers the first three questions is usable; a claim that answers none of them is a direction, not a number. The reported figures are still worth mentioning, because their direction agrees with every firm and controlled result above, as both 2026 papers find (Zhang et al., 2026; Guo et al., 2026). The response to any of them is the same: **measure one's own harness** ([post 22](../22-evaluating-harnesses/index.md)); the output-level counterpart of that trajectory-level measurement is `ctx-020`.

---

## 5. What the evidence does not show

A post arguing for honesty about numbers owes its own numbers the same scepticism. Five limits:

**Rank is not score.** The headline result circulated as a leaderboard move ("Top 30 to Top 5"), and secondary write-ups turn it into exact places (Faros AI, 2026). Where a write-up's rank and score disagree, follow the score.

**A harness tuned on a benchmark can overfit it.** Seven changes iterated against Terminal-Bench 2.0 are seven chances to fit that task distribution, and the LangChain write-up says so itself: "Changes that overfit to a task are bad for generalization and can lead to regressions in other Tasks" (Trivedy, 2026). Nothing promises 13.7 points on another codebase, which is why [post 22](../22-evaluating-harnesses/index.md) puts a held-out split and production metrics above any leaderboard.

**Harness gains are model-specific.** Per-model profiles exist because providers differ in prompting conventions and in the tool implementations they expect, and a profile moved its model by ten to twenty points (Trivedy and Daugherty, 2026). A harness copied from a team that runs another model is not the harness they measured.

**Benchmarks move under the results built on them.** Terminal-Bench 2.1 (6 May 2026) was released "to fix issues in 28 of the 89 tasks in Terminal-Bench 2.0", in external dependencies, resource budgets and misspecified tasks, and its release notes report that most representative agent-model pairs score higher on 2.1 (Terminal-Bench, 2026). A 2.0 score and a 2.1 score are not the same measurement, and this post's headline figure belongs to a version that has since been revised.

**The effect is not universal.** Starace's review of related work cites a large controlled study on safety benchmarks in which scaffold effects were small once the evaluation format was held constant (Starace, 2026). The claim is about agentic tasks where the harness decides what the model can reach and when it stops; on a task where the harness has little to decide, it has little to add.

The disciplined conclusion is the one Zhang et al. draw: "Until harness specifications are disclosed, leaderboard comparisons for long-horizon agents should be treated as incomplete and potentially misleading" (Zhang et al., 2026). That standard applies to the numbers above as much as to anyone else's.

---

## 6. The "skill issue" reframe: failures are configuration, not weights

A complementary, qualitative line of evidence comes from practitioners who audit their own agent failures. HumanLayer's "Skill Issue: Harness Engineering for Coding Agents" (12 March 2026) puts it bluntly: "over the course of dozens of projects and hundreds of agent sessions, we kept arriving at the same conclusion: it's not a model problem. It's a configuration problem." (HumanLayer, 2026). Osmani's article spread the framing as the **"skill issue" reframe**: most agent failures come down to configuration rather than model weights (Osmani, 2026). It is the experience of one team, with no counts behind "most", so it is reported.

[Post 05](../05-agent-failure-modes/index.md) is the catalogue that makes the reframe concrete. Its six failure modes are harness problems: victory declaration, context anxiety, one-shotting, doom loop and silent drift are each fixed by a harness component, and destructive action is bounded by hooks and permissions. A newer model can reduce one of them: in "Harness design for long-running application development" (Anthropic Engineering, 24 March 2026), Prithvi Rajasekaran reports that Sonnet 4.5 showed context anxiety and that "Opus 4.5 largely removed that behavior on its own" (Anthropic, 2026). The harness fix still comes first, because it works on the model in hand. A genuine model problem is what is left when the right information is demonstrably in the window, in a sensible place, the loop has verified the work, and the model still cannot do the task: the test post 01 gives, and `ctx-001` gave for the window before it.

The reframe and the table of LangChain's changes are one observation from two directions: the failure catalogue predicts which components will pay, and the LangChain campaign is a team paying for them and reporting the total. It is also the optimistic reading: most of the gap between what an agent does and what its model can do is closable by whoever owns the harness, without waiting for the next model.

---

## 7. Why it holds: models are trained inside harnesses

The evidence says the harness is a large lever. The mechanism that keeps it large is a feedback loop between harnesses and model training, which Trivedy describes in "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026) and Osmani popularised. Trivedy's account: "Today's agent products like Claude Code and Codex are post-trained with models and harnesses in the loop." The loop itself: "Useful primitives are discovered, added to the harness, and then used when training the next generation of models. As this cycle repeats, models become more capable within the harness they were trained in." (Trivedy, 2026).

![A cycle of four steps: a useful primitive is discovered in a harness, added to the harness, used to train the next model, and the model becomes more capable inside that harness. Beside it, two cards: discovered skills added 8.1 points on FeatureBench and the distilled model still passed 27.7% with no scaffold, 85.2% retained; and the side effect, overfitting, with Opus 4.6 scoring far lower in Claude Code than in other harnesses.](diagrams/03-co-training-loop.svg)

*The loop that makes a model good at its own harness also makes it awkward in others, so fit to the task, not the brand, is what to optimise.*

The figure above draws the loop and the two things measured about it. The first is that the loop can be run on purpose. Ding et al. ("Scaffold-Mediated Post-Training", 2026) organise procedural scaffolds into a graph that co-evolves with the model's parameters through discovery, distillation and recompilation. On FeatureBench, automatically discovered skills improve the passed rate by 8.1 percentage points, and after distillation the model still passes 27.7% "without any external scaffold", a retention of 85.2%, defined as the post-distillation passed rate over the rate with the skills (Ding et al., 2026). The last step of the loop, a pattern surviving in the weights once the harness that taught it is gone, is measured directly, in one preprint.

The second is the side effect, and it cuts against the obvious conclusion. Training with a harness in the loop "creates this overfitting", Trivedy writes, citing the `apply_patch` tool of the Codex prompting guide: change the tool's logic and a model trained on it does worse. And then: "But this doesn't mean that the best harness for your task is the one a model was post-trained with." On the Terminal-Bench 2.0 leaderboard, "Opus 4.6 in Claude Code scores far below Opus 4.6 in other harnesses" (Trivedy, 2026). Osmani draws the same line: the best harness "isn't necessarily the one the model was trained inside; it's the one designed for your task" (Osmani, 2026).

Two practical consequences follow:

- **Fit, not branding, is the operative property.** A harness performs best on the model and the task it was tuned for. A model's own software development kit (SDK) is a useful reference fit, because it carries the conventions the model was trained against, but it is a baseline to measure against, not a guaranteed best.
- **Harness patterns have a shelf life.** A pattern adopted today may become native model behaviour in a generation, which is what Ding et al.'s 85.2% retention does on purpose. The LangChain write-up says as much of its loop detection: "As models improve, these guardrails will likely be unnecessary, but today helps agents execute correctly and autonomously" (Trivedy, 2026).

---

## 8. Telling a harness problem from a model problem, in three runs

The test for a genuine model problem (the right information in the window, in the right place, the loop has verified the work, and the model still fails) is only useful if it can be run. Three runs establish it, each holding something different fixed. Take the failing trace ([post 21](../21-observability-traces/index.md)) and replay it three ways:

| Run | What it holds fixed | What a pass means | What to do next |
| --- | --- | --- | --- |
| **A.** Replay the trace with the missing information placed by hand at the top of the window | Model, harness, task | It was a context-placement problem | Fix retrieval, ordering or compaction ([post 09](../09-context-management-loop/index.md); `ctx-001`) |
| **B.** Run the same task under a harness fitted to the model: its own SDK harness, or a per-model profile | Model, task | It was a harness-fit problem | Port the pattern that fixed it ([post 20](../20-sdk-landscape/index.md)) |
| **C.** Run the same task with the next model up, harness unchanged | Harness, task | A genuine model gap, given this harness | Upgrade, then re-measure ([post 22](../22-evaluating-harnesses/index.md)) |

Only if A and B fail and C passes is there a model problem. Even then the verdict is precise: the model problem is what remains after the harness gap is closed, not what was seen at the start. Running C before A and B attributes the harness gap to the model: the team buys a bigger model and never learns that a stop condition would have done it.

None of this is trustworthy on one task. A harness A/B needs a fixed task set, graded objectively, with the model identical on both sides ([post 22](../22-evaluating-harnesses/index.md)). `snippets/harness_ab.py` holds the tally:

```python
def harness_ab(tasks, run_a, run_b):
    """Paired A/B of two harness configs. run_x(task) -> True if resolved."""
    wins_a = wins_b = ties = 0
    resolved_a = resolved_b = 0
    for task in tasks:                      # fixed, versioned set
        a, b = run_a(task), run_b(task)     # same model inside both
        resolved_a += a
        resolved_b += b
        if a and not b:   wins_a += 1
        elif b and not a: wins_b += 1
        else:             ties += 1
    n = len(tasks)
    return {"resolved_a": resolved_a / n, "resolved_b": resolved_b / n,
            "delta": (resolved_b - resolved_a) / n,
            "wins_a": wins_a, "wins_b": wins_b, "ties": ties}
```

The paired counts matter as much as the delta. The snippet runs it on 100 illustrative tasks where configuration B fixes five of A's failures and breaks three of A's successes, and `uv run python posts/04-harness-beats-model/snippets/harness_ab.py` prints:

```text
resolved: A 50%, B 52%, delta +2%
paired:   B fixed 5, B broke 3, unchanged 92
```

The mean says two points better; the tally says eight tasks changed, three of them for the worse. To run it for real, point `run_a` and `run_b` at two configurations of [`code/24-minimal-harness/`](../../code/24-minimal-harness/), which takes every harness parameter as a keyword argument.

That function is the skeleton, not the instrument. The real version repeats every task across seeds, puts the discordant counts through a significance test, and takes its graders and held-out split from [post 22](../22-evaluating-harnesses/index.md), which also shows how little a small set buys: on its illustrative 60-task example, a 6.7-point lift from 12 discordant pairs is consistent with a coin flip.

---

## 9. How to choose a model once the claim is accepted

Accepting the claim does not mean ignoring model choice; it means ordering the moves. When an agent underperforms:

1. **Diagnose first ([post 05](../05-agent-failure-modes/index.md)).** Name the failure mode. If it is one of the six, its harness fix comes before any bigger model.
2. **Exhaust the cheap harness fixes.** A verification gate, a stop condition, a hook: hours of work, not a re-architecture, and the kind of change behind the 13.7 points.
3. **Fit the harness to the model.** Start from what the model was trained against (its provider's prompting guide, its tool conventions, its own SDK as a reference run) and tune for the task, as the per-model profiles did.
4. **Upgrade the model only when the gap is a genuine model problem.** Establish it with the three runs, not by intuition; then a stronger model is exactly right.
5. **Re-measure after every change ([post 22](../22-evaluating-harnesses/index.md)).** Every figure in this post, and every figure a team produces, is a measurement, not a law.

The order is not arbitrary, because the costs have different shapes. Steps 1 to 3 are paid once, in engineer-hours; step 4 is paid per token, on every run, for as long as the system lives. Take [post 23](../23-economics-haas/index.md)'s illustrative running example: twelve iterations, the first request 6,000 tokens, each turn appending 3,100 more, so every turn re-reads the history before it. Write the price of one run today as $C$. A model upgrade that triples the price per token makes each run cost $3C$, an extra $2C$ on every run. Set that against the stop condition nobody wrote: one engineer-day, paid once, taken here to be worth 1,000 runs at today's price. All of these sizes are illustrative, and `uv run python posts/04-harness-beats-model/snippets/upgrade_cost.py` works them through:

```text
one run reads 276,600 input tokens; a context that never grew would read 72,000
growth multiplies the input by 3.84
upgrade: 3C a run, 2C extra on every run
fix: 1,000C once; break-even after 500 runs, 2.5 days at 200 runs a day
```

![A line chart of extra spend, in units of one run's price today, against runs, illustrative. The harness fix is a flat dashed line at 1,000; the model upgrade a dashed line rising by 2 a run to 2,000 at 1,000 runs. They cross at 500 runs, two and a half days at 200 runs a day.](diagrams/04-buy-once-rent-forever.svg)

*One side of the comparison is a constant and the other is a rate, so the rate always wins in the end; only the crossing point depends on the numbers.*

The figure above draws it: the fix is a flat line, the upgrade a rising one, and they cross after $1{,}000 / 2 = 500$ runs. Real numbers move the crossing, not the shape. The argument is not that upgrades are expensive in absolute terms; it is that a harness fix is bought once and a model upgrade is rented indefinitely, so the cheap rungs come first even when the upgrade would also have worked. The upgrade is still available afterwards, and by then the team knows whether it is needed.

---

## 10. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **The rank in the slide deck.** "Top 30 to Top 5" goes into a design review as "25 places", and nobody can say what 25 places is worth on another leaderboard: the number that carried the argument was the 13.7-point score.
- **A reported multiple as a target.** A team promises "six times better" from a new harness, and cannot say six times what, on which benchmark, against which baseline.
- **Another team's harness, another team's model.** The harness is copied from a write-up and run on a different model; the score barely moves, and the conclusion drawn is that harness work does not pay.
- **The upgrade before the diagnosis.** The agent declares victory without running the tests; the team moves to a stronger model, and gets the same unfinished task, declared done more fluently, at three times the price per run.
- **Run C alone.** The bigger model passes the failing task, and the team records a model problem, without having tried the replay with the information placed by hand or a harness fitted to the model.
- **An A/B read from the mean.** A configuration two points ahead on one pass over a small set ships, and the next run puts it two points behind: the paired counts were a handful of tasks either way.

---

## Common pitfalls

1. **Overclaiming the thesis.** "Harness beats model" is scoped to a given model on agentic tasks; the scaffolding ceiling is why it is not "models are irrelevant".
2. **Quoting the vivid number when a firmer one exists.** A rank moves with the crowd around it; the score delta on a fixed task set is the number that carries the argument.
3. **Promoting a reported figure.** A multiple with no model, benchmark or base stays reported, however often it is repeated; run the five questions before repeating it.
4. **Assuming the native harness is the best harness.** Co-training couples a model to its harness, but the best harness is the one fitted to the task; measure the native one, do not assume it.
5. **Treating any of these figures as stable.** Leaderboards, models and benchmarks move: Terminal-Bench 2.1 revised 28 of the 89 tasks the headline result was measured on. The mechanism is durable; the numbers are snapshots.

---

## Further reading

- Viv Trivedy, "Improving Deep Agents with harness engineering" (LangChain blog, 17 February 2026). The firm result and the changes behind it.
- Viv Trivedy and M. Daugherty, "Tuning Deep Agents to Work Well with Different Models" (LangChain blog, 29 April 2026). Per-model profiles.
- Viv Trivedy, "The Anatomy of an Agent Harness" (LangChain blog, 10 March 2026). The co-training loop and its overfitting.
- Y. Zhang et al., "Stop Comparing LLM Agents Without Disclosing the Harness" (arXiv, 7 May 2026). The Binding Constraint Thesis.
- J. Starace, "Scaffold Effects on GAIA: A Controlled Comparison" (arXiv, 7 June 2026). Up to 28 points within one model.
- J. Yang, C. E. Jimenez, et al., "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" (NeurIPS 2024). The interface-only ablation.
- J. Guo et al., "From Question Answering to Task Completion: A Survey on Agent System and Harness Design" (arXiv, 14 June 2026).
- F. Ding et al., "Scaffold-Mediated Post-Training: Co-Evolving Model Parameters and Procedural Scaffold Graphs" (arXiv, 2026). The loop run as a training procedure.
- HumanLayer, "Skill Issue: Harness Engineering for Coding Agents" (12 March 2026), and Addy Osmani, "Agent Harness Engineering" (19 April 2026). The "skill issue" reframe.
- MindStudio, "What Is Harness Engineering?" (8 May 2026). The reported sixfold spread.
- Terminal-Bench 2.0 (Stanford University and the Laude Institute, 7 November 2025) and Terminal-Bench 2.1 (6 May 2026).

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 05 - Agent failure modes: victory declaration, context anxiety, doom loops](../05-agent-failure-modes/index.md):** the six harness failures behind the "skill issue" reframe, one by one, with the component that fixes each.
- **[Post 22 - Evaluating harnesses: Terminal-Bench, SWE-bench, harness A/B](../22-evaluating-harnesses/index.md):** how to measure the claim on a team's own system instead of trusting anyone's figure, this post's included.
