# 12 · Planner / generator / evaluator — separating the roles

> **TL;DR.** [Post 11](../11-verification-loops/index.md) showed that a model grading its own work skews positive. The structural fix is to make the grader a *different agent* from the maker: a **planner** decomposes the task and sets a contract, a **generator** builds to it, and an independent **evaluator** grades the result against that contract. Agreeing the definition of done *before* the work (a **sprint contract**) is what stops the generator from declaring victory by lowering the bar. The split costs a large multiple of a single agent's tokens and wall-clock time, so it earns its place when correctness needs judgement rather than a test.
>
> **After reading this you will be able to:**
> - Separate the author of a piece of work from its grader, so the check is genuinely independent.
> - Write a sprint contract that fixes "done" before generation starts, and route each criterion to the cheapest verifier that can settle it.
> - Design against the evaluator's own biases, give it tools of its own, and notice that nothing in the pattern checks the planner.
> - Price three roles against one agent, and decide when a single agent plus a test suite is enough.

![The brief that goes in, a one to four sentence prompt expanded to 16 features across 10 sprints, feeds a planner that writes the criteria. The planner hands a plan to the generator and the contract to the evaluator, and each role is listed with what it reads, what it writes and what it never sees. The generator's work crosses to the evaluator, which returns PASS or NEEDS_WORK; a failure report goes back to the generator, capped at three revisions, and a pass leads to done. A measured cost table compares a single agent at 20 minutes and $9 against the full harness at 6 hours and $200.](diagrams/01-pge-triangle.svg)
*Three roles, one loop. The evaluator holds the contract but not the generator's reasoning, so it does not skew positive.*

---

## 1. Why self-evaluation is biased

The verification loop of [Post 11](../11-verification-loops/index.md) leaned on objective ground truth: a test either passes or it does not. But much of what an agent produces has no unit test. Is this design sound? Is this summary faithful? Is this refactor an improvement? When the check itself needs judgement, the obvious move is to ask the model, and the obvious mistake is to ask *the same model that produced the work.*

A model grading its own output skews positive. Anthropic's harness team put it plainly: asked to evaluate work they have produced, agents "tend to respond by confidently praising the work" even when a human reader would call the quality obviously mediocre (Anthropic, 2026; Osmani, 2026). The cause is structural rather than a prompting failure. The model is trained to be helpful and to conclude, it has just argued itself into the answer, and it carries the reasoning that made the answer look right. Asking it "is this correct?" invites the same optimism that produced the work. Self-critique is a useful first pass ([Post 11](../11-verification-loops/index.md) §3), never an independent one.

That conclusion is recent, and the shift behind it is instructive. The long-running-agent harness Anthropic published in November 2025 ran two roles, an initialiser and a coding agent, and its standing instruction to the coding agent was "self-verify all features" (Anthropic, 2025). The design that replaced it four months later moved verification out of the maker entirely and gave it to a role of its own (Anthropic, 2026).

Independence is structural, not a matter of prompting. It comes from making the grader **a separate agent**: a different model call, with its own context, that never saw the generator's chain of thought and has no stake in the work being finished. That agent can only judge what is in front of it against the criteria it was given.

The framing that stuck is **"GANs for prose"** (Osmani, 2026): as in a generative adversarial network (GAN), a generator that produces and an evaluator that critiques, held in tension. The analogy is worth one qualification, because where it breaks is the subject of §3. A GAN's discriminator is *trained* against the generator and improves in lockstep with it, and what it decides is whether a sample is real or generated. Here the evaluator is fixed for the whole run, and it grades against written criteria rather than against a learned sense of what real work looks like. Nothing teaches this grader a standard, so the standard has to be written down.

---

## 2. The three roles

The published version of the pattern builds a whole application from a paragraph. Anthropic's planner "took a simple 1-4 sentence prompt and expanded it into a full product spec"; the generator then worked in sprints, "picking up one feature at a time from the spec"; the evaluator drove the running application through a browser and scored what it found (Anthropic, 2026). Three roles, three contexts, one artefact passed between them.

Generalised, the roles divide as follows.

- **Planner.** Decomposes the task into steps and, crucially, writes the **acceptance criteria**: what would make this done. Planning first is also the fix for one-shotting ([Post 05](../05-agent-failure-modes/index.md)): the harness forces a plan before any code.
- **Generator.** Does the work, guided by the plan. It is the only role that writes the artefact, and it works to satisfy the criteria rather than its own sense of "good enough."
- **Evaluator.** Grades the finished work against the criteria, independently. It receives the contract and the work, and returns a verdict with a report.

What each role is denied matters as much as what it is given.

| Role | Reads | Writes | Never sees |
| --- | --- | --- | --- |
| Planner | The task as stated, and the repository it lands in | The plan and the numbered acceptance criteria | The work, which does not exist yet |
| Generator | The plan, the contract, and the last verdict | The artefact, and nothing else | Why the evaluator ruled as it did, beyond the report |
| Evaluator | The contract and the finished work | A verdict and a report | The generator's plan of attack and chain of thought |

The boundary between generator and evaluator is the one that carries the whole pattern. If they share a context, "grade your work" is just self-critique with extra steps. Kept apart, the evaluator becomes the verification gate of Post 11, now able to judge the things a test cannot. These are three roles inside one task, which is a different problem from coordinating several agents as independent units ([Post 16](../16-multi-agent-orchestration/index.md)): here there is one artefact, and the roles exist to keep its author away from its grade.

---

## 3. Sprint contracts: agree "done" before the work

The split only works if the criteria are fixed *before* generation starts. A **sprint contract** is that agreement: a definition of done settled before any code is written, so the generator builds to a target it cannot move (Osmani, 2026; Anthropic, 2026).

![A contract frozen before the work, listing six numbered criteria with the cheapest verifier that settles each and whether it is objective or judged: five are settled by a unit test, type checker, test runner or script, and only the sixth, whether the error a user sees is understandable, is left to the evaluator. Below it three numbered phases: negotiate the criteria, generate to the contract, and judge the work against the same contract, with PASS shipping the sprint and NEEDS_WORK naming the criterion.](diagrams/02-sprint-contract.svg)
*The bar is set before the work. In the stricter variant drawn here the planner drafts and the evaluator agrees, so the generator is not a party to its own standard.*

Both published designs put the negotiation between the **generator and the evaluator**: "before each sprint, the generator and evaluator negotiated a sprint contract" (Anthropic, 2026), and Osmani describes the same two parties. The figure above draws a stricter variant, in which the planner drafts and the evaluator agrees and the generator is not in the room at all. Both are defensible, and the trade is worth stating plainly. Excluding the generator removes any incentive to soften a criterion before it is written down. Including it buys one thing back: the chance to flag a criterion that is impossible or unmeasurable *as written*, before a sprint is spent discovering that.

What the two versions guarantee is identical, and weaker than it first sounds. The contract exists before any code does, and a second role has to agree to it, so nothing can be relaxed retroactively.

Negotiation is a short exchange over a draft rather than a debate. One role writes candidate criteria; the second reads them and pushes back on the three kinds that cause trouble later: the unmeasurable ("the code should be clean"), the impossible as written ("under 100 ms on the free tier"), and the ones that quietly assume work nobody scheduled. What comes out is a numbered list. A contract for one small feature might read:

1. `parse()` accepts an empty list and returns `[]`.
2. `parse()` raises `ValueError` on a malformed row, naming the row number.
3. Every public function carries a type annotation.
4. The new behaviour is covered by tests, and the suite passes.
5. The changelog gains one line describing the change.
6. The error a user sees is understandable without reading the source.

Written down, the list sorts itself into two kinds, and that sorting is what turns the choice in §10 from a coin toss into a calculation.

| # | Criterion | Settled by | Kind |
| --- | --- | --- | --- |
| 1 | Empty list returns `[]` | A unit test | Objective |
| 2 | Malformed row raises `ValueError` naming the row | A unit test | Objective |
| 3 | Public functions annotated | A type checker | Objective |
| 4 | Suite passes | The test runner | Objective |
| 5 | Changelog line present | A five-line script | Objective |
| 6 | Error message is understandable | The evaluator | Judged |

Five of the six criteria are settled by code that costs nothing per run and cannot hallucinate a pass. Route each criterion to the cheapest verifier that can settle it, which is the verifier ladder of [Post 11](../11-verification-loops/index.md) §2 applied per criterion rather than per task, and the evaluator only grades the residue:

```python
def grade(contract, work, evaluator):
    """Settle every criterion the cheapest way it can be settled."""
    failures = []
    for c in contract.criteria:
        if c.check is not None:              # objective: a test, a typecheck, a script
            ok, detail = c.check(work)
        else:                                # judged: the only ones worth a model call
            ok, detail = evaluator(c, work)
        if not ok:
            failures.append("criterion %d unmet: %s" % (c.number, detail))
    return Verdict(accepted=not failures, report="\n".join(failures))
```

`grade` is what sits behind the `evaluator` callable in the loop of §4: the role is still a separate agent, but it is only asked about the criteria that need an opinion.

Real contracts run far longer than six lines: sprint 3 of Anthropic's game-maker run carried "27 criteria covering the level editor" alone (Anthropic, 2026). At that size the routing stops being a nicety. It is the difference between a judged grade on twenty-seven items and a judged grade on three.

A verdict of "done" now means "meets the pre-agreed contract", which is a claim you can *check*, because the criteria are written down and the failures are named against them. Whether it is a claim worth trusting depends on the contract being complete, and nothing in the pattern guarantees that (§8).

---

## 4. Handoffs between the roles

Each role passes the next a structured artefact, exactly the handoff files of [Post 08](../08-state-filesystem-git/index.md): the planner hands over a plan and contract, the generator hands over the work, the evaluator hands back a verdict. The loop is the verification loop of Post 11 with the roles made explicit.

```python
from dataclasses import dataclass


@dataclass
class Verdict:
    """The evaluator's answer: the sibling of Post 11's VerifyResult, renamed
    because a judged verdict is an opinion where `ok` is a fact."""

    accepted: bool
    report: str = ""


@dataclass
class Sprint:
    """The outcome of a sprint: the last work, and whether it was accepted."""

    work: object
    attempts: int
    accepted: bool
    report: str = ""


def run_sprint(planner, generator, evaluator, task, *, max_revisions=3):
    """Plan once, then generate and independently evaluate until the contract is met."""
    contract = planner(task)                        # decompose + acceptance criteria, up front
    feedback, work = None, None
    for attempt in range(1, max_revisions + 2):
        work = generator(task, contract, feedback)  # build to the contract, not to "good enough"
        verdict = evaluator(work, contract)         # SEPARATE agent: grades work vs the contract
        if verdict.accepted:
            return Sprint(work, attempt, accepted=True)
        feedback = verdict.report                   # verbose critique, handed back to the generator
    return Sprint(work, max_revisions + 1, accepted=False, report=feedback)
```

Two design choices carry the independence. First, `evaluator` is a *different* callable with its own context, given `work` and `contract` but deliberately **not** the generator's reasoning; letting the evaluator see the maker's justification is how it gets talked into a pass. Second, `max_revisions` caps the loop, because an evaluator that never accepts and a generator that never satisfies it will otherwise thrash. That cap is the no-progress stop, exit ④ of [Post 03](../03-the-agent-loop/index.md), applied across roles rather than within one.

The third choice is what happens when the cap is reached, and a real deployment has to make it. There are three answers. Fail the run loudly, which is right when nothing downstream can use partial work. Return the best attempt marked unaccepted, so the caller decides. Or escalate to a human with the last verdict attached. The version above returns rather than raises, matching the companion of Post 11 on disk, where `code/11-verification-loop/src/verification_loop/loop.py` returns a `Solution` carrying `verified=False` and the failure report: the caller is better placed than the loop to judge whether unverified work is worth having. Under supervision the answer is usually the third, because "an evaluator was unsure" is one of the named escalation triggers of [Post 15](../15-human-in-the-loop/index.md) §9. An exhausted sprint is a handoff, not only an exception.

---

## 5. How big is a chunk

`run_sprint` as written plans once and grades the finished `work`. That is fail-at-the-end with extra roles, and [Post 11](../11-verification-loops/index.md) §1 already made the argument against it: a wrong turn in feature two is cheapest to find before feature three is built on top of it.

Neither published harness works that way. The planner's spec is a numbered list of features, sixteen of them spread across ten sprints in the game-maker run; the generator takes one feature at a time; and the evaluator is invoked per feature or per sprint rather than over the completed application (Anthropic, 2026). Granularity is therefore a design choice with a cost on both sides. Evaluating more often buys earlier detection and pays for it in evaluate calls; evaluating less often saves those calls and pays for it in rework on everything built on top of the mistake.

The rule that resolves it is the one that sizes a Ralph-loop iteration in [Post 18](../18-long-horizon-ralph/index.md) §3: make the chunk one verifiable increment. Read that way, the contract of §3 is not one document but a list of per-chunk contracts, each small enough that all its criteria can be checked at once.

The handoff between chunks is a file. In Anthropic's reference implementation the evaluator returns `PASS` or `NEEDS_WORK` with specific findings, and on `NEEDS_WORK` those findings are written to disk and become the next builder session's opening prompt (Anthropic, 2026). That is the handoff artefact of [Post 08](../08-state-filesystem-git/index.md) in its most literal form: the verdict outlives the context that produced it, which is what lets the loop survive a reset.

---

## 6. The evaluator is not an oracle

Independence removes one bias. It does not make the grader correct, and treating the evaluator's verdict as ground truth quietly reintroduces the problem the split was meant to solve, one level up where it is harder to see. A large language model (LLM) used as a judge is fallible in ways that are by now documented and measured.

Three of the four hazards below were identified in the paper that named the LLM-as-judge method (Zheng et al., 2023). The fourth is an operational hazard the same discipline guards against rather than a measured bias (Context Engineering, Post 20).

- **Self-preference.** A separate context is not a separate model. A judge favours output from its own model family (Zheng et al., 2023), so the pairing that looks most independent structurally can be the least independent in practice. Using a *different* model as the evaluator costs no extra calls and removes a real correlation. It is not free, though: a second provider means a second integration, a second rate limit, and no shared prompt cache with the generator ([Post 23](../23-economics-haas/index.md) §4).
- **Length bias.** Longer work scores higher whether or not the extra length carries anything (Zheng et al., 2023). A generator that learns this will pad, and the revision loop of §4 is precisely a mechanism for learning it.
- **Position bias.** When a judge compares two options, the order affects the winner (Zheng et al., 2023). If your evaluator ever ranks alternatives, randomise the order and check that the verdict survives the swap.
- **Rubric drift.** Across many evaluations the standard wanders, so the same work is accepted in one run and rejected in another. The sprint contract is the main defence, precisely because it is written down and fixed; a rubric held only in the evaluator's prompt drifts by paraphrase.

The cheap sanity check for all four: occasionally feed the evaluator work you already know is bad, and confirm it says so. An evaluator that has quietly become a rubber stamp looks exactly like a generator that has become excellent, and only testing the grader tells them apart. Those known-bad cases are a fixture set rather than a habit, which means they belong in the eval harness of [Post 22](../22-evaluating-harnesses/index.md) §4, versioned alongside everything else the harness is measured on. It is the same move that post’s §5 makes on a benchmark’s graders: a run that did nothing must fail, and a known-good solution must pass.

### A verdict the generator can act on

The other half of evaluator quality is what it *returns*. `verdict.accepted` drives the loop, but `verdict.report` drives the next attempt, and a report that says "does not meet the bar" sends the generator on a random walk through the solution space at full price per lap.

A useful verdict names the criterion that failed, points at where, and stops short of writing the fix. "Criterion 3 unmet: no test covers the empty-list case in `parse()`" is actionable, and it is exactly what the numbered contract of §3 makes possible. "Improve the tests" is not. Leaving the *how* to the generator matters too: an evaluator that dictates the patch has stopped grading and started generating, at which point nobody is checking the work.

This is the "success is silent, failures are verbose" rule of [Post 11](../11-verification-loops/index.md) §4 applied to judgement rather than to tests.

---

## 7. An evaluator that gathers its own evidence

A grader that only reads the artefact is judging the generator's *account* of the work. A grader with tools of its own judges the work.

The distinction is not academic. Anthropic gave its evaluator a browser-automation server over the Model Context Protocol (MCP), which let it "click through the running application the way a user would": exercising the interface, the endpoints behind it, and the state left in the database, then scoring the sprint against the bugs it found as well as against the contract (Anthropic, 2026). Tools as the action surface are [Post 06](../06-tools-bash-code/index.md); dispatching a server's tools inside the loop is [Post 07](../07-skills-mcp-runtime/index.md). Nothing in either says those are the generator's exclusive property.

Generalised, the move is to prefer first-hand evidence over reported evidence at every criterion: run the suite yourself rather than reading the claim that it passes, open the file rather than trusting the diff summary, query the table rather than accepting "the row is written."

The payoff is precise. Three of the four hazards in §6 operate on *presentation*, since length, order and idiom are all properties of how work is shown to a judge. Evidence the evaluator gathered itself was not presented to it by anyone, so those levers stop working. A screenshot the evaluator took cannot be padded.

The cost is equally precise. A tool-using evaluator is a second agent loop rather than a second model call, so it carries its own iterations, its own tool latency and its own growing context, and it should be priced as a run rather than as a call (§9).

### Enforce the boundary at the tool layer

The rule against an evaluator that writes the fix (§6) is, as stated there, an instruction. Instructions are exactly what a model talks itself around, which is the whole argument of [Post 13](../13-hooks-enforcement/index.md). Enforce it where it cannot be argued with instead. Anthropic's reference implementation runs the evaluator as a separate subagent with no Write or Edit tools, reviewing the diff and the screenshots "from a context window that never saw the build" (Anthropic, 2026). That is the permission boundary of [Post 14](../14-permissions-sandboxes/index.md) applied to a role rather than to an action, and it converts two of this post's central claims from aspirations into properties: the evaluator cannot start generating, and it genuinely never saw the reasoning.

---

## 8. Nobody is checking the planner

There is a hole in the architecture, and it is worth naming plainly because the three-role diagram hides it: the contract is graded against nothing.

![The chain task, planner, contract, generator, evaluator, with a solid green bracket linking contract to evaluator marked checked, and a dashed red bracket linking task to contract marked not checked.](diagrams/03-the-unchecked-edge.svg)
*The same pipeline as the hero figure, drawn to show the edge it leaves out, with two panels below it: the hole in the pattern, and where to put the missing check.*

The evaluator checks the work against the contract. Nothing checks the contract against the task. A planner that writes incomplete criteria produces a sprint where the generator satisfies every stated requirement, the evaluator accepts, and the result is wrong in a way the whole apparatus was structurally unable to notice. Worse, the confident "accepted" verdict is now evidence *for* the wrong result.

The pattern does offer a partial defence, and it deserves naming before it is dismissed. Renegotiating the contract before every sprint rather than writing it once gives a missing requirement ten chances to be caught instead of one, and involving the grader in drafting means at least one role that will not do the work has read the criteria (Anthropic, 2026). It is only partial. A planner and an evaluator that share a blind spot about the task will renegotiate the same incomplete contract ten times over, and nothing in the loop ever compares any version of it against the original request.

Which is why the honest advice is to keep the contract where a person will see it:

- **A human reads the contract, not the work.** Reviewing acceptance criteria takes a fraction of the time reviewing output does, and it is the highest-leverage minute in the sprint: the only point at which a missing requirement is still cheap to add. This is the approval gate of [Post 15](../15-human-in-the-loop/index.md) spent on the criteria rather than on every action, which is what keeps it rare enough to be read properly.
- **Criteria come from the task, quoted where possible.** A contract that paraphrases the request has already lost information; one that quotes it can be checked against it. The figure's second panel carries the rest of the checklist, including a contract that always passes first time (usually a sign the criteria are too easy) and the grader sanity check of §6.

The lesson generalises beyond this pattern: every check in a harness pushes the trust problem somewhere else, and it is worth knowing where you pushed it. Here it lands on the contract.

---

## 9. The cost of the extra roles

Three roles are not free, and the arithmetic is worse than the three-role picture suggests. A sprint runs one planning call, then a generate call *and* an evaluate call per attempt. The loop of §4, at its default cap of three revisions, therefore admits nine model calls where a single agent would make one. That is the floor, and it assumes every role answers in a single call.

On real work the multiple is larger. Anthropic ran one brief, a 2D retro game maker with a level editor, a sprite editor, entity behaviours and a playable test mode, under both designs and published the result (Anthropic, 2026).

| Run | Wall clock | Cost |
| --- | --- | --- |
| Single agent, one pass, on the brief above | 20 minutes | $9 |
| Full planner / generator / evaluator harness, same brief | 6 hours | $200 |
| A later, simplified harness on a different brief (a digital audio workstation) | 3 hours 50 minutes | $124.70 |

Over twenty times the price and roughly eighteen times the wall clock, for a quality difference the team reported as immediately apparent. That ratio, rather than the nine-call floor, is the number to plan against.

Three structural drivers account for the gap, and all three are in [Post 23](../23-economics-haas/index.md):

- **The evaluate call is input-heavy, and its input grows.** It re-reads the whole artefact on every attempt, and the artefact is larger every time (Post 23 §1). The late revisions are the expensive ones.
- **Prompt caching works within a role, not across them.** Three roles mean three different stable prefixes, so the discount that flattens a single agent's re-reads is fragmented three ways. Caching is the single biggest lever on run cost (Post 23 §4), and splitting the roles spends part of it.
- **The roles are serial.** The generator cannot start until the plan exists, and the evaluator cannot start until the work does, so latency adds rather than overlaps (Post 23 §2). That is how twenty minutes becomes six hours.

The pattern pays when the check needs judgement *and* the stakes are real: a design decision, a piece of prose, a refactor whose correctness no single test captures, on work expensive enough that a confidently wrong result costs more than the extra calls. It is the dearer cousin of the verification loop. Use objective checks wherever they reach, because they are cheap and never hallucinate a pass, and escalate to an independent evaluator only where judgement is unavoidable.

---

## 10. When a single agent is enough

The split is over-applied as often as it is under-applied. §3 already turned the choice from a binary into a matter of proportion: what decides it is how much of the contract can be settled by code.

| How much of the contract is code-checkable | What grades it | What it costs | What it fails to catch |
| --- | --- | --- | --- |
| All of it | A type checker and a test suite inside the verification loop of [Post 11](../11-verification-loops/index.md) | One agent, one call per attempt | Anything the tests do not assert: a correct program nobody wanted |
| Most of it | Tests for the objective criteria, an evaluator for the judged residue only | One agent, plus one small judged call per attempt | Judged criteria the contract never thought to write down |
| Little of it, low stakes | The generator's own self-critique, as a first pass (Post 11 §3) | A second call in the same context | The positive skew, which survives intact |
| Little of it, high stakes or expensive to be wrong | The full three roles, with a tool-using evaluator (§7) | Roughly twenty times a single agent (§9) | An incomplete contract, which nothing in the pattern checks (§8) |

Read the table down its last column rather than its first. Every row leaves something uncaught, so the choice is not which option is best but which residual risk is affordable here. A test suite that misses the point is cheap and confident; three roles grading an incomplete contract are expensive and confident.

The question to ask before adding roles is simply: *can this check be written as code?* If it can, write the check. If it cannot, make the checker a separate agent and give it a contract.

---

## Common pitfalls

- **Grading inside the maker's context.** "Now review your work" in one context is self-critique with extra steps, and handing the evaluator the generator's chain of thought is the same mistake in slower motion: the maker's justification is exactly what talks a grader into a pass (§1, §2).
- **No contract agreed up front.** Without a definition of done fixed before generation, the generator moves the goalposts and victory declaration returns (§3).
- **Sending every criterion to the evaluator.** Most criteria in a real contract are settled by a test, a type checker or a five-line script, at a fraction of the price and with no risk of a hallucinated pass (§3).
- **A verdict with no actionable report, or an evaluator that never accepts.** "Does not meet the bar" sends the generator on a random walk at full price per lap, and an uncapped generate-and-evaluate loop is a doom loop spread across roles (§4, §6).
- **An evaluator that writes the fix.** Once it dictates the patch it has stopped grading and nobody is checking the work. Enforce the boundary with tools rather than with instructions (§6, §7).
- **Nobody reviewing the contract.** The evaluator checks the work against the criteria; nothing checks the criteria against the task (§8).
- **Trusting the evaluator as ground truth.** An LLM judge is fallible; use it where objective checks cannot reach, not as an oracle (§6; Post 11 §2).

---

## Further reading

- Anthropic, "Harness design for long-running application development" (2026): the planner/generator/evaluator harness this post generalises, the sprint contract negotiated before each sprint, a tool-using evaluator, and the published cost comparison.
- Anthropic, "cwc-long-running-agents" reference implementation (2026): the evaluator subagent with no write tools, and the findings file that becomes the next builder session's opening prompt.
- Anthropic, "Effective harnesses for long-running agents" (2025): the earlier two-role design whose coding agent self-verified, useful as the picture this pattern replaced.
- Addy Osmani, "Agent Harness Engineering" (2026): the planner/generator/evaluator split, "GANs for prose," and sprint contracts.
- Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023): the paper that named the method and measured position, verbosity and self-enhancement bias in model judges.
- Context Engineering, Post 20 (2026): the four LLM-judge failure modes and their mitigations, applied to single outputs rather than to a role split.
- awesome-harness-engineering (2026): the Planning & Task Decomposition section.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 13 — Hooks & deterministic enforcement](../13-hooks-enforcement/index.md)**: when a rule is too important for even an evaluator, enforce it with code that cannot be argued with.
- **[Post 15 — Human-in-the-loop](../15-human-in-the-loop/index.md)**: who reads the contract, and where an exhausted sprint escalates to.
- **[Post 18 — Long-horizon & multi-context execution](../18-long-horizon-ralph/index.md)**: the same three roles run per iteration, against a spec that outlives any single context.
- **[Post 11 — Verification loops](../11-verification-loops/index.md)**: the objective-check version, and when it is all you need.
