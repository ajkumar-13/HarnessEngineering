# 04 · Why the harness beats the model — the evidence

> **TL;DR.** The founding claim of harness engineering is that the machine around the model is a bigger performance lever than the model itself: the same model can succeed or fail on the same task depending only on its harness. This post states that claim carefully, lays out the evidence in order of strength (a same-model, harness-only move of 13.7 points on Terminal-Bench 2.0; a controlled scaffold comparison worth up to 28 points; a peer-reviewed interface-only result that predates the word "harness"), says plainly what that evidence does not show, explains *why* it holds through the model-and-harness co-training flywheel, and turns it into a practical rule: before you reach for a bigger model, check whether the gap you are seeing is a harness gap.
>
> **After reading this you will be able to:**
> - State the "harness beats model" claim precisely, without overclaiming.
> - Grade any harness performance claim you meet, and tell a firm figure from a reported one.
> - Decide, in front of a real underperforming agent, whether to change the harness or the model.

![Two panels over a graded evidence row. A leaderboard-rank axis puts one coding agent at about rank 30 in a default harness and about rank 5 in a tuned harness on Terminal-Bench 2.0, about 25 places apart; beside it, two bars show the same result as a score, 52.8% against 66.5% of the 89 tasks resolved, a gain of 13.7 points with the model held fixed at gpt-5.2-codex. Four cards grade the evidence behind the picture, from that before-and-after through a controlled study worth up to 28 points and a peer-reviewed 12.5% against 3.8%, down to a reported multiple of about 6x whose base is not stated. A box reads Agent = Model + Harness.](diagrams/01-harness-gap.svg)
*The vivid version of one reported result: the same model, two harnesses, about 25 leaderboard places apart. §2 gives the firmer number behind the picture, which is the score, not the rank.*

---

## 1. The claim, stated carefully

Here is the claim in one sentence: **for agentic tasks, the harness explains more of the variance in real-world performance than the choice of model does.** [Post 01](../01-from-context-to-harness/index.md) gave the slogan (*a decent model with a great harness beats a great model with a bad harness*), and this post is the evidence and the reasoning behind it.

The claim now has a formal statement in the literature. Zhang et al. (2026) name it the **Binding Constraint Thesis**: for long-horizon tasks compared across models of comparable frontier capability, the execution harness (the layer governing context construction, tool interaction, orchestration and verification) is often a stronger determinant of performance than the model it wraps, so that "performance variance is governed more by harness configuration than by model choice". Their argument treats the harness as the controller of a closed-loop system and the model as the stochastic policy that controller governs, which is the reason a small harness change can outrun a model substitution rather than merely rival it.

It is worth saying what the claim is *not*, because it is easy to overreach:

- It is **not** "models do not matter." A more capable model raises the ceiling for every harness. The claim is about where the *marginal* engineering effort pays off today, not about which term is larger in the abstract.
- It is **not** "any model with a good harness beats any model." Call the reason the **scaffolding ceiling**: once the harness supplies the right tools, the right context and a sane control flow, what binds is whether the frozen weights can exploit them, and no amount of middleware supplies reasoning capacity the weights lack. The 2026 survey of agent and harness design frames precisely this question, asking whether the bottleneck sits in the foundation model, in the execution harness, or in the coupling between them, and answers that agent quality emerges from the interaction rather than from either term alone (Guo et al., 2026).
- It **is** "for a *given* model on a *given* agentic task, the harness usually moves performance more than a plausible model swap would."

The split between the two terms is easier to see in code than in prose. The entry point of this series' minimal build ([`code/24-minimal-harness/`](../../code/24-minimal-harness/)) takes the model as one argument among nine:

```python
def run(model: Model, registry: ToolRegistry, task: str, *,
        system: Optional[str] = None, verify: Optional[Verifier] = None,
        workspace: Optional[Workspace] = None, max_iters: int = 12,
        token_budget: Optional[int] = None, no_progress_window: int = 3) -> Result:
```

`model` is one parameter and `task` is another. The remaining seven are the harness: the tools the agent may call, the system prompt, the verification gate, the workspace it writes to, and three of the four stop conditions (the fourth, a verified final answer, is the gate). This post argues that on a real task, tuning those seven moves the outcome more than swapping the first.

With that scoped, the evidence, strongest first.

---

## 2. The firm evidence: one model, one benchmark, seven harness changes

The cleanest public data point is a before-and-after with the weights pinned. In February 2026 the LangChain team reported improving their coding agent, `deepagents-cli`, from **52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points, with the model held fixed at gpt-5.2-codex** (Trivedy, LangChain, 2026). Only the harness changed. In leaderboard terms that took the agent from just outside the top thirty into the top five, which is what the hero diagram draws, and what secondary write-ups picked up (Faros AI, 2026).

The benchmark matters to the reading. Terminal-Bench 2.0 is 89 hard, human-verified tasks in containers, spanning software engineering, machine learning, security, data processing, scientific computing and system administration, executed under the Harbor runner that spins up a sandbox per task and scores the result. It is not a quiz. Each task either resolves or does not.

Run the deduction on the **score**, not the rank. A fixed set of 89 containerised tasks, a fixed set of weights, and 13.7 more points of resolved-rate: that is 13.7 points of capability that were always inside the model and were not being elicited. Nothing about the model changed, so nothing about the model can explain the change. The rank move is the vivid consequence, and it is the weaker number, because rank conflates the improvement with the density of the field around it. On a sparse leaderboard the same 13.7 points might move two places; on a crowded one, two points might move twenty. Quote the score; illustrate with the rank.

What makes this result useful rather than merely encouraging is that the primary source lists what was changed, and every item is a component this series has a post about. The mapping below is this series' vocabulary applied to their list, not a claim LangChain makes:

| Harness change (Trivedy, LangChain, 2026) | Surface | Component in this series | Failure mode it closes |
| --- | --- | --- | --- |
| A plan / build / verify / fix phase structure in the system prompt | System prompt | Verification loop ([Post 11](../11-verification-loops/index.md)) | Victory declaration |
| **PreCompletionChecklistMiddleware**: intercepts the agent before it exits and forces a re-check against the task specification | Middleware | Verification gate ([Post 11](../11-verification-loops/index.md)) | Victory declaration |
| **LocalContextMiddleware**: maps the working directory and its neighbours at startup, and runs commands to discover the tooling actually installed | Tools and context | Context management ([Post 09](../09-context-management-loop/index.md)) | Silent drift |
| Prompting for testable code: exact paths, named edge cases, output a grader can check programmatically | System prompt | Tool and output contracts ([Post 06](../06-tools-bash-code/index.md)) | One-shotting |
| Injected time-budget warnings so the agent knows how much run it has left | Middleware | Stop conditions ([Posts 03](../03-the-agent-loop/index.md), [19](../19-loop-engineering/index.md)) | Context anxiety |
| **LoopDetectionMiddleware**: counts edits per file through tool-call hooks and prompts a rethink after N | Middleware | No-progress detection ([Post 19](../19-loop-engineering/index.md)) | Doom loop |
| An "xhigh-high-xhigh" reasoning sandwich: more reasoning compute on planning and verification than on the implementation in between | Run configuration | Run economics ([Post 23](../23-economics-haas/index.md)) | One-shotting |

Read the middle column and the right-hand column together. The levers that moved a real leaderboard by 13.7 points are the eleven components of [Post 02](../02-anatomy-of-a-harness/index.md) and the six failure modes of [Post 05](../05-agent-failure-modes/index.md), under other names. That is the strongest single argument this series can make for its own contents.

Two honest caveats. The source does not publish a per-change delta, so the table attributes *kind*, not magnitude: it does not tell you that loop detection was worth four points and the checklist three. And this is one team's iterative campaign against one benchmark, which §5 returns to.

---

## 3. The controlled evidence: hold the model, vary the scaffold

A single team's before-and-after is a strong existence proof and a weak generalisation. Two other results carry the generalisation.

The first is a controlled comparison. Starace (2026) ran a pre-registered study of three scaffolds (ReAct, a planner-actor-rater multi-agent design, and planner-then-executor) against five models from three providers on the GAIA assistant benchmark, holding tasks and run conditions fixed and taking three attempts per question. The finding: "Scaffold choice alone moves measured accuracy by as much as 28 percentage points within a single model." The paper's conclusion is the sharper half, and it is worth reading twice: "single-scaffold capability numbers are scaffold-conditional estimates and ... the elicitation gap is not guaranteed to shrink as models improve."

Two things follow. First, that study names the phenomenon better than this series did. **Elicitation gap** is the literature's term for what Post 01 called the harness gap: the distance between what a model can do and what its scaffold lets it do. Use whichever word your audience knows; they are the same quantity. Second, the elicitation gap is the standing answer to "why not simply wait for the next model." Waiting is only a strategy if the gap closes on its own, and the controlled evidence says it is not guaranteed to.

The second result predates the vocabulary entirely. SWE-agent (Yang et al., 2024) held GPT-4 Turbo fixed and changed only the interface the model acted through, building what the authors called an agent-computer interface: a small set of well-shaped commands for viewing, editing and running code, with guardrails on their output. It resolved 12.5% of the full SWE-bench test set against 3.8% for the previous best non-interactive retrieval-augmented system. That is more than three times the resolved-rate, from interface design alone, in a peer-reviewed paper published two years before anyone in this literature wrote the word "harness". The idea is older than its name.

---

## 4. The softer evidence: reported multiples, treated as reported

Beyond controlled work you will meet stronger-sounding figures: that the *same* model varies **several-fold** across harnesses. The most-quoted is a same-model spread of up to sixfold, which circulates through secondary write-ups (MindStudio, 2026). Follow that citation chain and it attributes the figure to Stanford and Tsinghua scaffold research without linking the underlying comparison, so a reader cannot check the model, the benchmark, or the baseline the multiple is a multiple *of*.

This series does not invent numbers, and reported numbers are labelled as reported. So the multiple is *reported*: the honest use of it is "large, and consistently in the same direction," not "exactly six times."

That contrast is more useful than the discount alone, because it generalises into a checklist. Five questions grade any harness performance claim, including the ones in this post:

| Question to ask of the claim | LangChain, +13.7 pts | Starace, up to 28 pts | The reported ~6× |
| --- | --- | --- | --- |
| Is the model named and held fixed? | Yes: gpt-5.2-codex | Yes: five models, each held fixed | Not stated |
| Is the benchmark and its version named? | Yes: Terminal-Bench 2.0 | Yes: GAIA validation, Levels 1 and 2 | Not stated |
| Is the harness specification published? | Yes: the changes are listed | Yes: three named scaffolds, pre-registered | No |
| Controlled comparison, or a snapshot? | Iterative before-and-after, one team | Controlled, three attempts per question | Unknown |
| Score delta, or rank delta? | Score: +13.7 points | Score: percentage points | A multiple, base unstated |

A claim that answers the first three questions is usable. A claim that answers none of them is a direction, not a number. Note that the checklist is not kind to the figure this post finds most quotable, which is the point of running it.

The reason to mention the reported multiples at all is that the *direction* is consistent. The two 2026 papers that survey this evidence across sources report the same sign (Zhang et al., 2026; Guo et al., 2026), and no source this series found reports that swapping harnesses barely moves a fixed model. When independent sources agree on a large effect in the same direction, the effect is probably real even when the precise multiple is not. The correct response to any of these figures is still to **measure your own harness** ([Post 22](../22-evaluating-harnesses/index.md)); the token-side companion to that trajectory-level measurement is output evaluation (Context Engineering, Post 20).

---

## 5. What the evidence does not show

A post whose selling point is honesty about numbers owes its own numbers the same scepticism. Four limits, each traceable.

**Rank is not score.** The hero diagram charts a leaderboard move because that is the form the result circulated in, and it is the weaker of the two available numbers for the reason §2 gave. Where the two disagree in any write-up you read, follow the score.

**A benchmark-tuned harness can overfit its benchmark.** Seven changes iterated against Terminal-Bench 2.0 are seven opportunities to fit that task distribution. Nothing in the result promises the same 13.7 points on your codebase, which is exactly why [Post 22](../22-evaluating-harnesses/index.md) puts a held-out split and production metrics above any leaderboard.

**Harness gains are model-specific and do not transfer for free.** The same team's follow-up found that one harness cannot be optimal for every model, because providers differ in prompting conventions and in the tool implementations they expect. Building per-model profiles moved their tau2-bench results from 33% to 53% for one model and from 43% to 53% for another (Trivedy and Daugherty, 2026). A harness copied from another team's model is not the harness they measured.

**Benchmarks move under the results built on them.** Terminal-Bench 2.1 revised 28 of the 2.0 tasks, correcting dependencies that had drifted, resource budgets too tight for valid solutions, and instructions that did not match their tests. Scores across versions are not directly comparable, and this post's own headline figure is attached to a version that has since been superseded.

The disciplined conclusion is the one Zhang et al. (2026) draw: "Until harness specifications are disclosed, leaderboard comparisons for long-horizon agents should be treated as incomplete and potentially misleading." That standard applies to the numbers above as much as to anyone else's.

---

## 6. The "skill issue" reframe: failures are configuration, not weights

There is a complementary, more qualitative line of evidence: when practitioners *audit* their agent failures, most turn out to be fixable in the harness. The framing that stuck is the **"skill issue" reframe** (popularised by HumanLayer, via Osmani, 2026): the majority of agent failures are *configuration* problems, not model-weight problems.

[Post 05](../05-agent-failure-modes/index.md) is the catalogue that makes this concrete. All six of its failure modes are harness problems rather than model ones: five (victory declaration, context anxiety, one-shotting, doom loops, silent drift) are fixed by a harness component, and the sixth (destructive action) is bounded by a guardrail. None is fixed by a better model. Only when the right information is demonstrably in the window, in a sensible place, the loop has verified the work, and the model *still* cannot do the task, do you have a genuine model problem (the test [Post 01](../01-from-context-to-harness/index.md) §4 states, and Context Engineering, Post 01 §5 before it).

Notice that this reframe and the table in §2 are the same observation from two directions. The failure catalogue predicts which components will pay; the LangChain campaign is a case of someone paying them and reporting the total. This reframe is also optimistic, which is why it is worth internalising: most of the gap between what your agent does and what the model can do is *yours to close*, today, without waiting for the next model.

---

## 7. Why it holds: the co-training flywheel

The evidence says the harness is a large lever. The *mechanism* that keeps it large is a feedback loop between harnesses and model training.

![A four-step cycle: harnesses discover a useful pattern, it is standardised into a product or software development kit, the next model trains against it, the model gets better at using it, and harnesses exploit the improvement, repeating each model generation. A side panel gives what follows for a model in its native harness. Below, three cards carry the published measurements of the loop: discovered scaffolds worth +8.1 points on FeatureBench, 85.2% of that performance retained in the weights after distillation at 27.7% passed with no scaffold at all, and per-model harness profiles moving tau2-bench from 33% to 53%.](diagrams/02-cotraining-flywheel.svg)
*Useful harness patterns become training signal for the next model, which is why a model feels sharper inside the harness it was shaped with.*

The loop runs like this (Osmani, 2026):

1. A harness discovers a useful pattern: bash-as-a-universal-tool, plan files, hooks, a particular tool-calling shape.
2. The pattern gets standardised into a product or software development kit (SDK): Claude Code, the Codex harness, the agent SDKs.
3. The next generation of models is trained against traces full of that pattern.
4. Those models get *better at using* the pattern, and the next harness exploits the improvement.

That is a blogger's framing of the loop, and it deserves more than a blogger's evidence. Two anchors carry it.

**The loop has been run deliberately, and measured.** Ding et al. (2026) implement it as an explicit training procedure they call scaffold-mediated post-training: procedural scaffolds are organised into a graph that co-evolves with model parameters through discovery, distillation and recompilation. On the FeatureBench task set, automatically discovered scaffolds lift the passed rate by 8.1 percentage points, and after distilling those scaffolds into the weights the model keeps a 27.7% passed rate **with no external scaffold at all**, a retention of 85.2% of the scaffolded performance. That last figure is step 4 of the flywheel measured directly: the pattern survives in the weights once the harness that taught it is taken away.

**The consequence is measurable too, and it is narrower than "use the vendor's own tool."** What the tuning evidence shows is that a harness performs best on the model it was tuned *for*, with gains of ten to twenty points on a tool-use benchmark from per-model profiles alone (Trivedy and Daugherty, 2026). Vendor SDKs are the common case of that, because they were tuned against their own model, but the operative property is fit, not branding. A carefully tuned in-house harness on a model you profiled beats a native SDK you never measured.

Two practical consequences follow:

- **A model feels different inside the harness it was shaped with.** The same weights dropped into a generic harness are not the same experience. This is why "just use the best model" quietly underrates the harness: the best model was co-trained with a harness you may not be running.
- **Harness patterns have a shelf life and a compounding value.** A pattern you invent today may become a native model capability in a generation (Ding et al.'s 85.2% retention is that happening on purpose), and the patterns you adopt from the model's native harness are the ones it is *best* at.

---

## 8. Telling a harness problem from a model problem, in three runs

§6 gave the test for a genuine model problem: the right information is in the window, in the right place, the loop has verified the work, and the model still fails. A test is only useful if you can run it. Three runs establish it, each holding something different fixed. Take the failing trace ([Post 21](../21-observability-traces/index.md)) and replay it three ways:

| Run | What it holds fixed | What a pass means | What to do next |
| --- | --- | --- | --- |
| **A.** Replay the trace with the missing information hand-placed at the top of the window | Model, harness, task | It was a context-placement problem | Fix retrieval, ordering or compaction ([Post 09](../09-context-management-loop/index.md); Context Engineering, Post 01 §5) |
| **B.** Run the same task under the model's own SDK harness, unmodified | Model, task | It was a harness-fit problem | Adopt or port the pattern that fixed it ([Post 20](../20-sdk-landscape/index.md); §7) |
| **C.** Run the same task with the next model up, harness unchanged | Harness, task | A genuine model gap, *given this harness* | Upgrade, then re-measure ([Post 22](../22-evaluating-harnesses/index.md)) |

Only if A and B fail and C passes do you have a model problem. Even then, read the verdict precisely: the model problem is what *remains* after the harness gap is closed, not what you saw at the start. Run C before runs A and B and you will attribute the harness gap to the model, buy a bigger model, and never learn that a stop condition would have done it.

None of this is trustworthy on one task. A harness A/B needs a fixed task set, graded objectively, with the model argument identical on both sides ([Post 22](../22-evaluating-harnesses/index.md)):

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

The paired counts matter as much as the delta: a config two points ahead on the mean may have fixed five tasks and broken three, and only the row-by-row tally shows it. Point `run_a` and `run_b` at two configurations of [`code/24-minimal-harness/`](../../code/24-minimal-harness/), which takes every harness knob as a keyword argument.

Treat that function as the skeleton rather than the instrument. The version that survives contact with reality repeats every task across several seeds, puts the discordant counts through a significance test, and takes its graders and its held-out split from [Post 22](../22-evaluating-harnesses/index.md). That post also works out how little a small set buys you: a 6.7-point lift over sixty tasks can still be indistinguishable from a coin flip. §5's caution about single results applies to your own measurements as much as to other people's.

---

## 9. So how should you choose a model?

Accepting the claim does not mean ignoring model choice; it means *ordering* your moves correctly. A practical procedure when an agent underperforms:

1. **Diagnose first ([Post 05](../05-agent-failure-modes/index.md)).** Name the failure mode. If it is one of the six harness-fixable modes, a bigger model is the wrong tool.
2. **Exhaust the cheap harness fixes.** A verification loop, a stop condition, or a hook: these are hours of work, not a re-architecture, and they are where the leaderboard move came from (§2).
3. **Use the harness your model was tuned for.** Given the flywheel (§7), a model performs best in a harness fitted to it, and the vendor's own SDK is usually the nearest available fit.
4. **Upgrade the model only when the gap is a genuine model problem.** Establish that with the three runs in §8, not by intuition. Then a stronger model is exactly right.
5. **Re-measure after every change ([Post 22](../22-evaluating-harnesses/index.md)).** Every figure in this post, yours included, is a measurement, not a law.

![A ladder of five numbered steps with the cost of each: diagnose first, free and minutes; exhaust the cheap harness fixes, hours; use the model's native harness, one migration; only now upgrade the model, more per token forever; re-measure after every change, an afternoon per change. A dashed red arrow skips from step one straight to step four, labelled as the common and most expensive move.](diagrams/03-choose-model-order.svg)
*The rungs are cheap until step 4, and step 4 is the only one you keep paying for per token.*

Reading the ladder with the costs attached explains why the order is not arbitrary. Steps 1 to 3 are one-off costs paid in engineer-hours; step 4 is a *recurring* cost paid per token, on every run, for as long as the system lives.

The asymmetry is worth working out rather than asserting. Take the run model from [Post 23](../23-economics-haas/index.md): a task that resolves in twelve iterations re-reads its whole history every turn, with the context growing from about 6,000 tokens at iteration one to about 40,000 at iteration twelve. The input bill for one run is roughly iterations times average context, so about 12 × 23,000 = 276,000 input tokens. Growth alone has almost quadrupled it against the 72,000 tokens a non-growing context would have cost.

Now write the run's current price as C. A model upgrade that triples the input price makes each run cost about 3C, because that run is overwhelmingly input tokens, so the upgrade adds 2C on every run, forever. Set that against the stop condition you did not write: one engineer-day, paid once. If an engineer-day is worth about 1,000 runs at the current price, the upgrade has cost more than the fix would have after 500 runs, and at 200 runs a day that break-even arrives inside three days. Substitute your own numbers; the shape does not change, because one side of the comparison is a constant and the other is a rate.

That is the real argument for the order, and it is not that model upgrades are expensive in absolute terms. It is that you buy a harness fix once and rent a model upgrade indefinitely, so the cheap rungs are worth spending first even when the upgrade would also have worked. The upgrade is still available afterwards, and by then you will know whether you still need it.

---

## Common pitfalls

- **Overclaiming the thesis.** "Harness beats model" is scoped to a *given* model on *agentic* tasks. It is not "models are irrelevant", and the scaffolding ceiling is why (§1).
- **Charting the vivid number when a firmer one exists.** A rank move is memorable and field-dependent; the score delta behind it is the number that carries the argument. Check whether the primary source published scores before you draw ranks (§2, §5).
- **Quoting reported multiples as measured facts.** The "~6×" figure is reported by a secondary source that does not link its own primary; run the five-question checklist before repeating any figure, including these (§4).
- **Upgrading the model before diagnosing.** All six failure modes are harness problems, not model ones; a bigger model spends more to hide them (§6, §9).
- **Declaring a model problem without the three runs.** "The model still cannot do it" is a conclusion that requires evidence from a replay and a native-harness run, not a hunch (§8).
- **Copying another team's harness and expecting their numbers.** Harness gains are model-specific; profiles tuned for one provider moved a tool-use benchmark by ten to twenty points, which is also the size of the loss when the fit is wrong (§5, §7).
- **Treating any of these figures as stable.** Leaderboards, models and benchmarks all move; Terminal-Bench 2.1 revised 28 of the tasks this post's headline number was measured on. The *mechanism* is durable; the numbers are snapshots (§5).

---

## Further reading

- Trivedy, V. (LangChain), "Improving Deep Agents with harness engineering" (17 February 2026): the primary source for the same-model, harness-only move from 52.8% to 66.5% on Terminal-Bench 2.0, with the seven changes listed.
- Zhang, Y., Wang, J., Ge, Y., Xu, W., Hamm, J., and Reddy, C. K., "Stop Comparing LLM Agents Without Disclosing the Harness" (2026): the Binding Constraint Thesis, a variance-decomposition protocol, and the disclosure standard §5 closes on.
- Starace, J., "Scaffold Effects on GAIA: A Controlled Comparison" (2026): three scaffolds, five models, tasks held fixed, and up to 28 percentage points of within-model movement; the source of the term *elicitation gap*.
- Yang, J., Jimenez, C., et al., "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" (2024): the peer-reviewed, interface-only result (12.5% against 3.8%, GPT-4 Turbo fixed) that predates the vocabulary.
- Guo, J., et al., "From Question Answering to Task Completion: A Survey on Agent System and Harness Design" (2026): the model-versus-harness-versus-coupling question, and the six runtime responsibilities a harness decomposes into.
- Ding, F., et al., "Scaffold-Mediated Post-Training: Co-Evolving Model Parameters and Procedural Scaffold Graphs" (2026): the co-training flywheel executed as a training procedure, with the 85.2% retention figure after the scaffold is removed.
- Trivedy, V., and Daugherty, M. (LangChain), "Tuning Deep Agents to Work Well with Different Models" (29 April 2026): why one harness cannot be optimal for every model, with per-model tuning worth ten to twenty points.
- Faros AI, "Harness Engineering: Making AI Coding Agents Work in 2026": the secondary summary through which the leaderboard move circulated.
- MindStudio, "What Is Harness Engineering?" (2026): the reported several-fold same-model spread, and a worked example of a citation chain that stops short of its primary.
- Osmani, A., "Agent Harness Engineering" (2026): the co-training flywheel framing and the "skill issue" reframe, the latter via HumanLayer.
- Context Engineering, Post 01 §5: the original model-problem-versus-context-problem test that §6 and §8 extend to harnesses.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: the catalogue behind the "skill issue" reframe, the six harness-fixable failures one by one.
- **[Post 02 — The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: the eleven levers this post says matter more than the model, and the map §2's table lands on.
- **[Post 20 — The SDK & framework landscape](../20-sdk-landscape/index.md)**: where §9's "use the harness your model was tuned for" turns into a choice between real SDKs.
- **[Post 22 — Evaluating harnesses](../22-evaluating-harnesses/index.md)**: how to measure the claim on your own system instead of trusting a reported figure.
