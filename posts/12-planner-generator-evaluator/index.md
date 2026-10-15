# 12 - Planner, generator, evaluator: separating the roles

> **TL;DR.** A model grading its own work skews positive, so the grader has to be a different agent from the maker: a **planner** drafts the criteria, a **generator** builds to them, and an independent **evaluator** grades the result against them. Agreeing done before the work (a **sprint contract**), and settling with code every criterion that code can settle, stops the generator passing by lowering the bar. The split costs many times a single agent, so it earns its place where correctness needs judgement rather than a test.
>
> **Prerequisites:** [post 11](../11-verification-loops/index.md), the verification loop, the verifier ladder and why self-critique is a weak gate.
> **Safe to skip?** Skip it if the reader can already keep an evaluator independent of the maker, freeze a contract before the first attempt with each criterion routed to the cheapest verifier, and say what nothing in the pattern checks.
>
> **After reading, you will be able to:**
>
> - Separate the author of a piece of work from its grader, and say what each of the three roles reads, writes and never sees.
> - Write a sprint contract that fixes done before generation starts, and route each criterion to the cheapest verifier that can settle it.
> - Design against the evaluator's own biases, give it tools to gather its own evidence, and enforce its read-only boundary in its tool registry.
> - Explain why nothing in the pattern checks the planner, and put the missing check on the contract.
> - Price three roles against one agent, and decide when a single agent with a test suite is enough.

![Three role cards: the planner, which never sees the work; the generator, which writes only the artefact; and the evaluator, inside a registry with read_file only, which never sees the generator's reasoning. A contract of six criteria sits between them; NEEDS_WORK goes back to the generator and PASS leads to done.](diagrams/01-three-roles.svg)

*Three roles, one artefact between them. The grader holds the contract and the work, never the reasoning that produced the work, and its tools cannot write.*

---

## 1. Why self-evaluation is biased

Why does an independent evaluator beat a self-grading agent, and what does the split cost? The verification loop of [post 11](../11-verification-loops/index.md) leaned on objective ground truth: a test either passes or it does not. But much of what an agent produces has no unit test. Is this design sound? Is this summary faithful? Is this refactor an improvement? When the check itself needs judgement, the obvious move is to ask a model, and the obvious mistake is to ask *the same model that produced the work.*

A model grading its own output skews positive. Prithvi Rajasekaran of Anthropic's Labs team puts it plainly: asked to evaluate work they have produced, agents "tend to respond by confidently praising the work", even when a human can see the work is mediocre (Rajasekaran, "Harness design for long-running application development", Anthropic, 24 March 2026). Osmani repeats the finding as "agents reliably skew positive when grading their own work" ("Agent Harness Engineering", 19 April 2026). The cause is structural rather than a prompting failure. The model is trained to be helpful and to conclude, it has just argued itself into the answer, and it carries the reasoning that made the answer look right. Self-critique is a useful first pass ([post 11](../11-verification-loops/index.md)), never an independent one.

That conclusion is recent. The long-running harness Anthropic published in November 2025 ran an initialiser agent and a coding agent, and its table of fixes answers "Claude marks features as done prematurely" with an instruction to the coding agent: "Self-verify all features" (Justin Young, "Effective harnesses for long-running agents", Anthropic, 26 November 2025). The design that replaced it four months later kept the generator's own end-of-sprint check but moved the grade to a role of its own, on the finding that "tuning a standalone evaluator to be skeptical turns out to be far more tractable" than making a generator critical of its own work (Rajasekaran, 2026).

Independence comes from making the grader **a separate agent**: a different model call, with its own context, that never saw the generator's chain of thought and has no stake in the work being finished.

Rajasekaran's design took its inspiration from generative adversarial networks (GANs), a generator and a discriminator held in tension; Osmani's phrase for the result is "GANs for prose". The analogy breaks in one place that matters. A GAN's discriminator is *trained* against the generator and improves with it; this evaluator is fixed for the whole run and grades against written criteria. Nothing teaches it a standard, so the standard has to be written down, which is the subject of the section on sprint contracts.

---

## 2. The three roles

The published version of the pattern builds a whole application from a paragraph. Rajasekaran's planner "took a simple 1-4 sentence prompt and expanded it into a full product spec", sixteen features spread across ten sprints in the game-maker run; the generator worked in sprints, picking up one feature at a time from the spec; and the evaluator used the Playwright MCP (Model Context Protocol) server to click through the running application and grade what it found (Rajasekaran, 2026). Three roles, three contexts, one artefact passed between them.

Generalised, the **planner** decomposes the task and drafts the **acceptance criteria**, what would make it done; planning first is also the fix for one-shotting ([post 05](../05-agent-failure-modes/index.md)). The **generator** is the only role that writes the artefact, and it works to the criteria rather than its own sense of "good enough". The **evaluator** grades the finished work against the criteria and returns `PASS`, or `NEEDS_WORK` with the failures named. What each role is denied matters as much as what it is given, and the figure at the top draws the three side by side.

| Role | Reads | Writes | Never sees |
| --- | --- | --- | --- |
| Planner | The task as stated, and the repository it lands in | The plan and the numbered acceptance criteria | The work, which does not exist yet |
| Generator | The plan, the contract, and the last report | The artefact, and nothing else | The evaluator's reasoning, beyond the report |
| Evaluator | The contract and the finished work | PASS or NEEDS_WORK, and a report | The generator's plan of attack and chain of thought |

The boundary between generator and evaluator carries the whole pattern. If they share a context, "grade the work" is self-critique with extra steps; kept apart, the evaluator becomes the verification gate of post 11, able to judge what a test cannot. These are three roles inside one task, a different problem from coordinating agents that own tasks of their own ([post 16](../16-multi-agent-orchestration/index.md)): here there is one artefact, and the roles keep its author away from its grade.

---

## 3. Sprint contracts: agree "done" before the work

The split only works if the criteria are fixed *before* generation starts. A **sprint contract** is that agreement: a definition of done settled before any code is written, so the generator builds to a target it cannot move.

In Rajasekaran's harness the two parties are the generator and the evaluator: "Before each sprint, the generator and evaluator negotiated a sprint contract." The generator proposed what it would build and how success would be verified, the evaluator reviewed the proposal, and the two iterated until they agreed (Rajasekaran, 2026); Osmani describes the same two parties. A stricter variant has the planner draft and the evaluator agree, so the generator is not in the room at all. Excluding the generator removes any incentive to soften a criterion before it is written down; including it buys back the chance to flag a criterion that is impossible *as written* before a sprint is spent discovering that. Either way the guarantee is the same, and weaker than it sounds: the contract exists before any code does, and a second role has agreed to it, so nothing can be relaxed retroactively.

Negotiation is a short exchange over a draft, in which the second role pushes back on the three kinds of criterion that cause trouble later: the unmeasurable ("the code is clean"), the impossible as written ("under 100 ms on the free tier"), and the ones that quietly assume work nobody scheduled. `uv run python posts/12-planner-generator-evaluator/snippets/three_roles.py` runs the stricter variant for one small feature, a `parse()` for a two-column export, with deterministic stand-ins where a real harness calls a model in each role. Its planner drafts seven criteria and its evaluator refuses one:

```text
evaluator refuses draft criterion 7, 'the code is clean': names nothing observable
contract frozen before attempt 1: 6 criteria, digest 07c1ff17
  1  unit test        parse([]) returns []
  2  unit test        a malformed row raises ValueError naming the row number
  3  schema check     every row matches {"name": str, "amount": int}
  4  annotation check every public function is annotated
  5  script           CHANGELOG.md gains exactly one line
  6  evaluator        the error a user sees is understandable without the source
```

The digest is a hash of the agreed text, printed again with every verdict, so a contract that moved between attempts would show it. Written down, the list sorts itself into two kinds, and that sorting is what turns the choice between one agent and three into a calculation. Five of the six criteria are settled by code that costs no model call and cannot hallucinate a pass: two unit tests, a schema check, an annotation check standing in for a type checker, and a short script. Only the sixth is judged. Route each criterion to the cheapest verifier that can settle it, which is the verifier ladder of [post 11](../11-verification-loops/index.md) applied per criterion rather than per task, and the evaluator only grades the residue:

```python
def grade(contract, work, evaluator):
    """Settle every criterion the cheapest way it can be settled."""
    failures = []
    for c in contract.criteria:
        if c.check is not None:              # objective: a test, a schema, a script
            ok, detail = c.check(work)
        else:                                # judged: the only ones worth a model call
            ok, detail = evaluator(c, work)
        if not ok:
            failures.append(f"criterion {c.number} unmet: {detail}")
    return Verdict(accepted=not failures, report="\n".join(failures))
```

`grade` is what sits behind the `evaluator` callable in the loop of the next section: the role is still a separate agent, but it is only asked about the criteria that need an opinion.

![Six contract criteria, each with its verifier, against three attempts, after a draft of seven with criterion 7 refused and the contract frozen as digest 07c1ff17. Attempt 1 leaves criteria 2, 3 and 6 unmet, attempt 2 only criterion 6, and attempt 3 passes all six; the digest never changes.](diagrams/02-sprint-contract.svg)

*The bar is set before the work and never moves; the objective criteria fail for free, and the judge is asked only about the one that needs an opinion.*

Real contracts run far longer than six lines: "Sprint 3 alone had 27 criteria covering the level editor" (Rajasekaran, 2026). At that size the routing is the difference between a judged grade on twenty-seven items and one on a few. A verdict of "done" now means "meets the pre-agreed contract", a claim that can be *checked*, because the failures are named against written criteria. Whether it is worth trusting depends on the contract being complete, and nothing in the pattern guarantees that, as the section on the planner shows.

---

## 4. Handoffs between the roles

Each role passes the next a structured artefact, as with the handoff files of [post 08](../08-state-filesystem-git/index.md): the planner hands over a plan and contract, the generator hands over the work, the evaluator hands back a verdict. The loop is the verification loop of post 11 with the roles made explicit, and it is the snippet's own:

```python
@dataclass
class Verdict:
    """The evaluator's answer: the sibling of post 11's VerifyResult, renamed
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
        feedback = verdict.report                   # the named failures, handed back to the generator
    return Sprint(work, max_revisions + 1, accepted=False, report=feedback)
```

In the snippet's run the generator replays three scripted versions of `parse.py`, one per attempt, and the verdicts come back as the figure above draws them:

```text
attempt 1  NEEDS_WORK  digest 07c1ff17  unmet: 2, 3, 6
    criterion 2 unmet: the error for row 2 reads 'not enough values to unpack (expected 2, got 1)'
    criterion 3 unmet: parse returned [{'name': 'bolt', 'amount': '3'}, {'name': 'nut', 'amount': '12'}]
    criterion 6 unmet: the message does not say which row is wrong
attempt 2  NEEDS_WORK  digest 07c1ff17  unmet: 6
    criterion 6 unmet: the message names the row but not what is wrong with it
    evaluator write_file refused: write_file is not in the evaluator's registry
attempt 3  PASS        digest 07c1ff17
sprint accepted: True after 3 attempts; files written: generator 4, evaluator 0
```

Attempt 2 is the one the split exists for: every objective check passes, so a loop that only ran tests would have accepted an error that reads `row 2` and nothing more. The judged criterion catches it, with the rule a model would be asked to apply: name the row, what was expected and what was found.

Two design choices carry the independence. First, `evaluator` is a *different* callable with its own context, given `work` and `contract` but deliberately **not** the generator's reasoning; letting the evaluator see the maker's justification is how it gets talked into a pass. Second, `max_revisions` caps the loop, because an evaluator that never accepts and a generator that never satisfies it will otherwise thrash. That cap is exit (2), the iteration cap of [post 03](../03-the-agent-loop/index.md), applied across roles rather than within one. A real exit (4), no progress, is cheap to add on top: when two verdicts in a row name the same failures, the remaining attempts buy nothing.

The third choice is what happens when the cap is reached. Fail the run loudly, when nothing downstream can use partial work; return the last attempt marked unaccepted, so the caller decides; or escalate to a human with the last verdict attached. The version above returns, matching the companion of post 11, whose `solve` returns a `Solution` carrying `verified=False` and the failure report. Under supervision the answer is often the third, since "an evaluator was unsure" is one of the escalation triggers of [post 15](../15-human-in-the-loop/index.md). An exhausted sprint is a handoff, not only an exception.

---

## 5. How big is a chunk

`run_sprint` as written plans once and grades the finished `work`. Over a whole application that is fail-at-the-end with extra roles, and [post 11](../11-verification-loops/index.md) already made the argument against it: a wrong turn in feature two is cheapest to find before feature three is built on top of it.

The published harnesses chose differently. Rajasekaran's first harness graded each sprint against its contract; Anthropic's reference implementation, `cwc-long-running-agents`, invokes its evaluator after each feature. Rajasekaran's later, simpler harness dropped the sprints and moved the evaluator "to a single pass at the end of the run rather than grading per sprint"; on the newer model (Claude Opus 4.6) "the model's raw capability increased, so the boundary moved outward", and the evaluator "is worth the cost when the task sits beyond what the current model does reliably solo" (Rajasekaran, 2026). Granularity is therefore a design choice with a cost on both sides, and the model moves it. Evaluating more often buys earlier detection and pays for it in evaluate calls; evaluating less often saves those calls and pays for it in rework on everything built on top of the mistake.

The rule that resolves it is the one that sizes a Ralph-loop iteration in [post 18](../18-long-horizon-ralph/index.md): make the chunk one verifiable increment. Read that way, a sprint contract is not one document but a list of per-chunk contracts, each small enough that all its criteria can be checked at once.

The handoff between chunks is a file. In the reference implementation a separate evaluator returns `PASS` or `NEEDS_WORK` with specific findings, and on `NEEDS_WORK` the findings are written to `NEXT_FINDINGS.md` and become the next builder session's starting prompt (Anthropic, `cwc-long-running-agents`, GitHub, 2026). That is the handoff artefact of [post 08](../08-state-filesystem-git/index.md) in its most literal form: the verdict outlives the context that produced it.

---

## 6. The evaluator is not an oracle

Independence removes one bias. It does not make the grader correct, and treating its verdict as ground truth reintroduces the problem one level up, where it is harder to see. A large language model (LLM) used as a judge is fallible in documented ways.

The paper that named the LLM-as-a-judge method examined its limitations as "position, verbosity, and self-enhancement biases, as well as limited reasoning ability" (Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", NeurIPS 2023). The four hazards below take the first three and add an operational one, as `ctx-020` does for single outputs.

- **Self-preference.** A separate context is not a separate model. Zheng et al. call it self-enhancement bias: GPT-4 favoured its own answers with a 10% higher win rate and Claude-v1 with a 25% higher one, though the authors judged their data too limited to establish the bias. Panickssery, Bowman and Feng (2024) measured it directly, as the case where an LLM evaluator "scores its own outputs higher than others' while human annotators consider them of equal quality". A *different* model as the evaluator costs no extra calls and removes that correlation, at the price of a second integration, a second rate limit, and no prompt cache shared with the generator ([post 23](../23-economics-haas/index.md)).
- **Length bias.** The paper's verbosity bias: a judge favours longer, verbose responses, even when they are no clearer. A generator that learns this will pad, and the revision loop of `run_sprint` is a mechanism for learning it.
- **Position bias.** When a judge compares two options, the order affects the winner (Zheng et al., 2023). If an evaluator ever ranks alternatives, randomise the order and check that the verdict survives the swap.
- **Rubric drift.** Across many evaluations the standard wanders, so the same work is accepted in one run and rejected in another. The paper does not measure it. The sprint contract is the main defence, precisely because it is written down and fixed; a rubric held only in the evaluator's prompt drifts by paraphrase.

The cheap sanity check for all four: occasionally feed the evaluator work already known to be bad, and confirm it says so. An evaluator that has quietly become a rubber stamp looks exactly like a generator that has become excellent, and only testing the grader tells them apart. Those known-bad cases are a fixture set, which belongs in the internal eval harness of [post 22](../22-evaluating-harnesses/index.md), versioned alongside everything else the harness is measured on.

### A verdict the generator can act on

The other half of evaluator quality is what it *returns*. `verdict.accepted` drives the loop, but `verdict.report` drives the next attempt, and "does not meet the bar" sends the generator on a random walk at full price per lap.

A useful verdict names the criterion that failed, points at where, and stops short of writing the fix. "Criterion 2 unmet: the error for row 2 reads 'not enough values to unpack (expected 2, got 1)'" is actionable, and it is exactly what the numbered contract makes possible. "Improve the error handling" is not. Leaving the *how* to the generator matters too: an evaluator that dictates the patch has stopped grading and started generating, at which point nobody is checking the work. This is the "success is silent, failures are verbose" rule of [post 11](../11-verification-loops/index.md) applied to judgement rather than to tests.

---

## 7. An evaluator that gathers its own evidence

A grader that only reads the artefact is judging the generator's *account* of the work. A grader with tools of its own judges the work.

The distinction is not academic. Rajasekaran's evaluator used the Playwright MCP server "to click through the running application the way a user would", testing user-interface features, application programming interface (API) endpoints and database states, then graded each sprint "against both the bugs it had found and a set of criteria", each with a hard threshold that failed the sprint if any one fell below it (Rajasekaran, 2026). Tools as the action surface are [post 06](../06-tools-bash-code/index.md); dispatching a server's tools inside the loop is [post 07](../07-skills-mcp-runtime/index.md). Nothing in either says those are the generator's exclusive property.

Generalised, the move is to prefer first-hand evidence at every criterion: run the suite rather than read the claim that it passes, query the table rather than accept "the row is written". The snippet's checks work this way: they load the generated `parse.py` itself and read the changelog itself.

The payoff is that three of the four hazards above operate on *presentation*: length, order and the model's own idiom are properties of how work is shown to a judge, and evidence the evaluator gathered itself was shown to it by nobody. A screenshot the evaluator took cannot be padded. The cost is that a tool-using evaluator is a second agent loop rather than a second model call, with its own iterations, tool latency and growing context, so it is priced as a run rather than as a call.

### Enforce the boundary at the tool layer

The rule against an evaluator that writes the fix is, so far, an instruction, and instructions are what a model talks itself around, the argument of [post 13](../13-hooks-enforcement/index.md). Anthropic's reference implementation runs the evaluator as a separate subagent "with no Write/Edit tools that reviews the diff and the screenshots from a context window that never saw the build" (Anthropic, `cwc-long-running-agents`, 2026). The snippet does the same with two registries over one repository: the generator's holds `read_file` and `write_file`, the evaluator's holds `read_file` only. When its stand-in, on attempt 2, reaches for the fix itself, the call never runs: `write_file is not in the evaluator's registry`, and the run ends with the evaluator having written nothing. That is the permission boundary of [post 14](../14-permissions-sandboxes/index.md) applied to a role rather than to an action, and, with the separate context, it converts two of this post's central claims from aspirations into properties: the evaluator cannot start generating, and it genuinely never saw the reasoning.

---

## 8. Nobody is checking the planner

The three-role picture hides a hole: the contract is graded against nothing.

![A chain of cards from the task through the planner, the contract and the generator to the evaluator. A purple bracket marks the work checked against the contract; a red bracket marks the contract not checked against the task. A human card below reads the contract.](diagrams/03-the-unchecked-edge.svg)

*The same pipeline as the hero, drawn to show the edge it leaves out, and where the missing check belongs.*

The evaluator checks the work against the contract; nothing checks the contract against the task, as the figure above draws. A planner that writes incomplete criteria produces a sprint where the generator satisfies every stated requirement, the evaluator accepts, and the result is wrong in a way the whole apparatus was structurally unable to notice. Worse, the confident "accepted" verdict is now evidence *for* the wrong result. The snippet's contract has the same hole: nothing in it says what `parse()` should do with a negative amount, so no attempt is ever checked for it.

The pattern does offer a partial defence. Negotiating a contract before each sprint reviews each chunk's criteria just before it is built, not once at the start, and involving the grader in drafting means one role that will not do the work has read the criteria. But a planner and an evaluator that share a blind spot about the task will agree to the same incomplete criteria sprint after sprint, and nothing in the loop compares any version of it against the original request.

Which is why the honest advice is to keep the contract where a person will see it:

- **A human reads the contract, not the work.** Criteria are far shorter than output, and reading them is the one point at which a missing requirement is still cheap to add. This is the approval gate of [post 15](../15-human-in-the-loop/index.md) spent on the criteria rather than on every action, which keeps it rare enough to be read properly.
- **Criteria come from the task, quoted where possible.** A contract that paraphrases the request has already lost information; one that quotes it can be checked against it.
- **A contract that always passes first time is suspect.** It can mean the criteria are too easy rather than that the generator is excellent, and it is the cue for the known-bad sanity check above.

The lesson generalises beyond this pattern: every check in a harness pushes the trust problem somewhere else, and it is worth knowing where it was pushed. Here it lands on the contract.

---

## 9. The cost of the extra roles

A sprint runs one planning call, then a generate call *and* an evaluate call per attempt. The loop of `run_sprint`, at its default cap of three revisions, allows four attempts and so up to $1 + 4 + 4 = 9$ model calls where a single agent answering in one call makes one, even before any role needs more than one call. The snippet's run made eight: one planning call, one evaluator call to agree the contract, and three generate and three judge calls. It counts the tokens of its stand-in prompts with `tiktoken` and prices them at the Claude Sonnet 4.6 rates of 3 and 15 dollars per million input and output tokens (Anthropic's pricing page, consulted October 2026); the prompts are toys, so the counts are illustrative:

```text
             calls   input  output   dollars
planner          1      35      72   0.00119
generator        3     554     222   0.00499
evaluator        4     378      53   0.00193
three roles      8     967     347   0.00811
one agent        1      42     109   0.00176
multiple: 4.6 times one agent's dollars (illustrative)
```

By hand: $967 \times 3 + 347 \times 15 = 8{,}106$ millionths of a dollar for the three roles, against $42 \times 3 + 109 \times 15 = 1{,}761$ for one call that writes the same final file, a ratio of about 4.6. Even on a toy, the generator's input dominates, because each attempt re-reads the contract, the last report and the file it is revising.

On real work the multiple is larger. Rajasekaran ran one brief, "Create a 2D retro game maker" with a level editor, a sprite editor, entity behaviours and a playable test mode, through a single agent and through the full harness, both on Claude Opus 4.5, and published the result (Rajasekaran, 2026):

| Run | Wall clock | Cost, US dollars |
| --- | --- | --- |
| Single agent, on the brief above | 20 minutes | 9 |
| Full planner, generator, evaluator harness, same brief | 6 hours | 200 |
| A later, simplified harness on a different brief (a digital audio workstation) | 3 hours 50 minutes | 124.70 |

That is $200 / 9 \approx 22$ times the price and $360 / 20 = 18$ times the wall clock, six hours being 360 minutes. One result per design, on one brief, so it is a cost observation rather than a benchmark, graded reported: the quality side is Rajasekaran's judgement by inspection, that "the difference in output quality was immediately apparent", and that in the solo run "the actual game was broken". That ratio, rather than the nine-call ceiling or the snippet's toy multiple, is the number to plan against.

Three structural drivers account for the gap, and all three are in [post 23](../23-economics-haas/index.md):

- **The evaluate call is input-heavy, and its input grows.** It re-reads the whole artefact on every attempt, and the artefact is larger every time.
- **Prompt caching works within a role, not across them.** Three roles mean three stable prefixes, so the discount that flattens a single agent's re-reads is fragmented three ways; post 23 names caching the single biggest lever on run cost.
- **The roles are serial.** The generator cannot start until the plan exists, nor the evaluator until the work does, so latency adds rather than overlaps.

The pattern pays when the check needs judgement *and* a confidently wrong result costs more than the extra calls: a design decision, a piece of prose, a refactor whose correctness no single test captures.

---

## 10. When a single agent is enough

The sprint contract turned the choice from a binary into a matter of proportion: what decides it is how much of the contract code can settle.

| How much of the contract is code-checkable | What grades it | What it costs | What it fails to catch |
| --- | --- | --- | --- |
| All of it | A type checker and a test suite inside the verification loop of [post 11](../11-verification-loops/index.md) | One agent, one call per attempt | Anything the tests do not assert: a correct program nobody wanted |
| Most of it | Tests for the objective criteria, an evaluator for the judged residue only | One agent, plus one small judged call per attempt | Judged criteria the contract never thought to write down |
| Little of it, low stakes | The generator's own self-critique, as a first pass | A second call in the same context | The positive skew, which survives intact |
| Little of it, high stakes or expensive to be wrong | The full three roles, with a tool-using evaluator | Many times a single agent: about 22 times in the one published comparison | An incomplete contract, which nothing in the pattern checks |

Read the table down its last column. Every row leaves something uncaught, so the choice is which residual risk is affordable here. A test suite that misses the point is cheap and confident; three roles grading an incomplete contract are expensive and confident.

The question to ask before adding roles is simply: *can this check be written as code?* If it can, write the check. If it cannot, make the checker a separate agent and give it a contract.

---

## 11. Make it run

The snippet runs from the series root with the standard library and `tiktoken`, and calls no model; apart from `tiktoken` fetching its encoding file once and caching it, it touches neither the network nor the disk:

```bash
uv run python posts/12-planner-generator-evaluator/snippets/three_roles.py
```

It prints the contract, the three verdicts and the cost table quoted above, which together are this post's exercise: a contract for one small feature, the loop run with an evaluator that has no write tools, the verdicts recorded, and the cost multiple against a single agent. To try a variation, add `"write_file"` to the evaluator's registry in `main()` and watch the sprint line report a write by the evaluator; or give criterion 6 a `check` that only looks for `row 2`, and watch attempt 2 pass with an error message no user could act on.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **The evaluator forked from the generator's conversation.** A subagent started with the maker's history is not a separate context; the first attempt passes suspiciously often, and the defects surface in review.
- **A contract edited after the first attempt.** The digest changes between verdicts and the pass rate climbs, while the defects users report stay where they were.
- **Every criterion sent to the judge.** The cost per sprint grows with the length of the contract, and a judged "the suite passes" comes back `PASS` while continuous integration is red.
- **A report that names no criterion.** Each attempt changes code unrelated to the failure, the same criterion stays unmet until the cap, and the sprint ends unaccepted at full price.
- **The cap treated as success.** The caller uses `Sprint.work` without reading `Sprint.accepted`, and unaccepted work ships as though it had passed.

---

## Common pitfalls

1. **Grading inside the maker's context.** "Now review the work" in one context is self-critique with extra steps, and handing the evaluator the generator's chain of thought is the same mistake in slower motion.
2. **No contract agreed up front.** Without a definition of done fixed before generation, the generator moves the goalposts and victory declaration returns.
3. **An evaluator that writes the fix.** Once it dictates the patch it has stopped grading and nobody is checking the work; take the write tools out of its registry rather than asking it not to.
4. **Nobody reviewing the contract.** The evaluator checks the work against the criteria; nothing checks the criteria against the task.
5. **Trusting the evaluator as ground truth.** An LLM judge is fallible; use it where objective checks cannot reach, test it with known-bad work, and never treat it as an oracle.

---

## Further reading

- Prithvi Rajasekaran, "Harness design for long-running application development" (Anthropic, 24 March 2026): the three-role harness, sprint contracts, a tool-using evaluator and the cost comparison.
- Anthropic, `cwc-long-running-agents` reference implementation (GitHub, 2026): the evaluator subagent with no write tools, and the findings file.
- Justin Young, "Effective harnesses for long-running agents" (Anthropic, 26 November 2025): the earlier two-agent design whose coding agent self-verified.
- Addy Osmani, "Agent Harness Engineering" (19 April 2026): the planner, generator and evaluator split, "GANs for prose", and sprint contracts.
- Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023): the paper that named the method and examined position, verbosity and self-enhancement bias in model judges.
- Panickssery, A., Bowman, S. R., and Feng, S., "LLM Evaluators Recognize and Favor Their Own Generations" (2024): self-preference measured directly.
- `ctx-020`: the four LLM-judge failure modes and their mitigations, applied to single outputs rather than to a role split.
- ai-boost, awesome-harness-engineering (GitHub, 2026): the Planning & Task Decomposition primitive.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 13 - Hooks and deterministic enforcement: guardrails as code](../13-hooks-enforcement/index.md):** when a rule is too important for even an evaluator, enforce it with code that cannot be argued with.
- **[Post 16 - Multi-agent orchestration: topologies, and when not to](../16-multi-agent-orchestration/index.md):** agents that own their own tasks, the pattern three roles inside one task are often confused with.
