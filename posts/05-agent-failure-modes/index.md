# 05 · Agent failure modes — victory declaration, context anxiety, doom loops

> **TL;DR.** Autonomous agents do not fail randomly; they fail in a small set of recurring, nameable ways, each mapping to a harness component you can change. This post catalogues six: victory declaration, context anxiety, one-shotting, doom loops, silent drift, and destructive action. Five are performance failures and one is a safety failure, and all six are fixed by building something rather than by buying a bigger model. Naming the mode turns "my agent is flaky" into a diagnosis, and the diagnosis names the fix. It is the runtime analogue of the Context Engineering series' five *context* failure modes.
>
> **After reading this you will be able to:**
> - Name the six recurring agent failure modes and recognise each from its symptom.
> - Map any observed failure to the harness component, or pair, that fixes it.
> - Read a trace to tell which mode you are looking at, and where in the loop it struck.
> - Separate the confusable pairs, and recognise the failures this taxonomy excludes.

![A grid of six cards, one per failure mode: victory declaration, context anxiety, one-shotting, doom loop, silent drift, and destructive action, each with its symptom and the harness component that fixes it.](diagrams/01-failure-modes-grid.svg)
*Six modes, and for each the component, sometimes the pair, that fixes it. The value of the taxonomy is that the fix is never "use a bigger model"; it is always a specific piece of machinery.*

---

## 1. "My agent is flaky" is not a diagnosis

The Context Engineering series argued that a vague complaint about a large language model (LLM) application almost always resolves into one of five named *context* failures: distraction, confusion, conflict, lost-in-the-middle, and tool-storm (Context Engineering, Post 06, adapting Breunig, 2025). Naming them was the first step to fixing them.

Agents that *run*, which is to say loop, call tools and act unattended, have their own taxonomy one layer up. These are not failures of what the model *sees* on a single call; they are failures of what the harness *does* across many calls. Like their context-layer cousins, they are a short and finite list.

**Where these six come from.** Three are named in the wild: Faros AI's survey of coding-agent harnesses lists *victory declaration bias*, *context anxiety* and *one-shotting overreach*, crediting all three to Anthropic's research on long-running agents (Faros AI, 2026; Anthropic, 2025). The doom loop is older than the agent era, being the thrashing case any control loop without a progress check eventually reaches, which is why [Post 03](../03-the-agent-loop/index.md) numbers no-progress detection among its four exits. Silent drift and destructive action are this series' own additions, included because they are the two failures a harness can make structurally difficult rather than merely less likely.

A second, independently assembled list overlaps without matching: Osmani names *early stopping*, *poor decomposition*, *incoherence as work stretches across multiple context windows*, and *context rot* (Osmani, 2026). Early stopping is victory declaration renamed, poor decomposition is one-shotting, and context rot is the mechanism behind context anxiety. Cross-window incoherence is real and deliberately absent, being a property of multi-session work rather than of any one run ([Post 18](../18-long-horizon-ralph/index.md)). Two lists built from different evidence converging on four of the same failures is the strongest support this taxonomy has; it is not proof of completeness, and §9 states what falls outside.

One split governs the rest. **Five of the six are performance failures**, where the agent works badly and a re-run recovers it. **One, destructive action, is a safety failure**, where a re-run cannot undo what happened. All six map to a component from the anatomy of [Post 02](../02-anatomy-of-a-harness/index.md) rather than to a model upgrade.

---

## 2. The six failure modes

Each mode is stated as *symptom · why it happens · the fix*. The numbering is stable, and other posts cite these subsections by number.

### 2.1 Victory declaration

**Symptom.** The agent announces the task is complete when it is not: tests still red, the feature half-built, the question half-answered.

*Why:* the model is trained to be helpful and to conclude, and agents reliably skew positive when grading their own work (Osmani, 2026). This is not a reasoning defect a stronger model removes; it is what happens whenever the author of a piece of work is also its only judge.

*Fix:* a **verification loop** that checks the work against ground truth (tests, a schema, an independent judge) before the loop may exit on a "final answer". This is the component this series would add first to a naive agent, for the cost reasons in §3, and it is [Post 11](../11-verification-loops/index.md).

### 2.2 Context anxiety

**Symptom.** As the context window fills, output quality drops: the agent cuts corners, drops steps, or races to finish.

*Why:* a reported behaviour on top of a measured mechanism. As available space shrinks, models are observed to rush and to cut corners to avoid running out of room (Faros AI, 2026, reporting Anthropic, 2025). The decay underneath it is measured: recall and reasoning sag as an input grows long, which is context rot ([Post 09](../09-context-management-loop/index.md) §1). The *rushing* is not, so treat this mode as a shape to look for in your own traces (§6) rather than a settled phenomenon.

*Fix:* active **context management**, a ladder from offloading a large output to disk, through clearing tool results already acted on and compacting older turns into a summary, up to a full reset behind a handoff file ([Post 09](../09-context-management-loop/index.md)). Reach for the cheapest rung that works.

### 2.3 One-shotting

**Symptom.** The agent attempts the whole task in a single sweep, producing one large, undocumented change that is hard to review and usually wrong somewhere.

*Why:* without structure, the model treats a multi-step task as one step. Anthropic's long-running-agent study describes exactly this: the agent "tended to try to do too much at once, essentially to attempt to one-shot the app" (Anthropic, 2025).

*Fix:* a **planner / generator / evaluator split** that forces decomposition and staged review ([Post 12](../12-planner-generator-evaluator/index.md)). The harness makes the model plan before it acts, and the plan is written where a later session can read it.

### 2.4 Doom loop

**Symptom.** The agent repeats the same action (re-running a failing command, re-reading the same file) making no progress while looking busy.

*Why:* nothing in a naive loop notices that the state has stopped changing. The model sees a transcript in which it has tried something, and the most probable continuation is to try it again.

*Fix:* the **no-progress stop condition** from [Post 03](../03-the-agent-loop/index.md): detect repeated tool calls or unchanged observations across *N* turns and break. This is exit ④, and §6 shows the eight lines that implement it. Without it a doom loop burns the whole budget, and §3 works out how much that is.

### 2.5 Silent drift

**Symptom.** The agent quietly ignores your project's conventions (wrong test framework, wrong formatting, a pattern you have corrected before) and keeps doing so, run after run.

*Why:* the convention was never durably part of what the harness sends, or it was and nothing enforces it. A rule that lives only in a conversation dies with that conversation.

*Fix:* the **ratchet**. Put the rule in a memory file the harness injects every session ([Post 10](../10-continual-learning-ratchet/index.md)) *and* back it with a **hook** that enforces it deterministically ([Post 13](../13-hooks-enforcement/index.md)). A convention held only by the model's goodwill will drift.

### 2.6 Destructive action

**Symptom.** The agent runs something dangerous. Osmani's canonical examples are the ones worth blocking first: `rm -rf`, `git push --force`, and `DROP TABLE` (Osmani, 2026).

*Why:* it has real tools and a real blast radius, and judgement alone is not a safety mechanism. An agent careful 999 times in 1,000 is still an agent that drops a production table this quarter.

*Fix:* a **deny-list hook** that blocks the class of command ([Post 13](../13-hooks-enforcement/index.md)) inside a **sandbox** that bounds what any command can reach ([Post 14](../14-permissions-sandboxes/index.md)). This is the only mode whose fix must run *before* the action, because there is no after.

---

## 3. What each mode costs, and who pays

Symptom and fix are enough to diagnose, but not to prioritise, and a real agent usually has more than one of these at once. The second axis is cost.

| Mode | What it consumes | Who pays | Recovered by a re-run? |
| ---- | ---------------- | -------- | ---------------------- |
| Victory declaration | A run, plus a review cycle spent on work never done | The reviewer, then the user who trusted it | Yes, though trust returns slower than tokens |
| Context anxiety | The tail of a long run, its worst and dearest turns | The budget, twice | Yes |
| One-shotting | Review capacity: one change nobody can bisect | The reviewer | Yes |
| Doom loop | The entire remaining token and wall-clock budget | The budget | Yes |
| Silent drift | A little of every run, compounding across the repository | The whole team, quietly | Only by undoing each instance |
| Destructive action | Whatever the command reached | Whoever owned the data | **No** |

Every cost here except the last is a re-run away from being reclaimed, which is why destructive action alone is fixed by a gate in front of the action rather than a check behind it.

**A worked example: what a doom loop costs.** A doom loop is the cheapest failure to detect and among the dearest to leave running, because its cost grows quadratically. Take a loop whose transcript grows by roughly 4,000 tokens a turn (one model response plus one tool result) and which re-reads the whole transcript on every call. Input at turn *k* is then about 4,000*k* tokens, so a run of *n* turns costs about 2,000·*n*·(*n*+1) input tokens.

- With no-progress detection at a window of three, an agent that begins repeating at turn 4 is stopped at turn 6: roughly **84,000** input tokens.
- Without it, the same useless run continues to a 40-iteration cap: roughly **3.28 million**.

That is a factor of **39** on identical, worthless work, and the ratio holds at any per-token price. It is also why exit ④ is worth building before you lean on exit ②: the iteration cap does stop the run, but only once the expensive part has been paid for ([Post 23](../23-economics-haas/index.md) works the per-run economics through in full).

---

## 4. Where they strike: failures cluster in the loop

These six are not scattered randomly through an agent's behaviour. Mapped onto the reason → act → observe loop from [Post 03](../03-the-agent-loop/index.md), they cluster at specific stages, which is exactly why each has a specific fix.

![The agent loop on the left, each stage carrying the thing you watch there; on the right, the six failure modes grouped by the loop stage where they strike: reason, act, observe, and across turns; below both, a table pairing where each mode's symptom shows with where its fix installs.](diagrams/02-where-failures-strike.svg)
*Failures have addresses. One-shotting and victory declaration are decisions made at REASON; destructive action happens at ACT; doom loops and context anxiety show up as the loop turns; silent drift spans every turn.*

- **At REASON**, where the model decides, live the *judgement* failures: victory declaration and one-shotting.
- **At ACT**, where a tool runs, lives the *blast-radius* failure: destructive action.
- **At OBSERVE / loop-back** live the *iteration* failures: doom loop and context anxiety.
- **Across turns** lives the *consistency* failure: silent drift.

**The address of a failure is not always the address of its fix.** Victory declaration is a *decision* made at REASON, but the component that fixes it sits on the loop's **exit**, the only point at which a candidate answer exists to be checked. Context anxiety belongs to no single stage, being a property of the accumulated window, so its fix runs between turns. Silent drift has no address in the loop at all, and is fixed at session start where the memory file is injected and at pre-tool where the hook fires. The working rule is therefore: **instrument at the stage where the symptom shows; install the fix at the stage that controls it.** The trace (§6) names the mode; the anatomy map of [Post 02](../02-anatomy-of-a-harness/index.md) names the component.

---

## 5. A harness that fixed three of them

The clearest public example of this taxonomy in action is Anthropic's write-up of a harness built so a coding agent could construct a large application across many context windows (Anthropic, 2025). The model was capable, and the early attempts still failed in three of the six ways catalogued above.

The report names them almost in this post's vocabulary. The agent "tended to try to do too much at once, essentially to attempt to one-shot the app" (§2.3). That over-reach "led to the model running out of context in the middle of its implementation, leaving the next session to start with a feature half-implemented and undocumented" (§2.2). And a later session, seeing that some progress had been made, "would often declare the job done" while work remained (§2.1).

None of the fixes was a different model. An **initialiser agent** runs once and writes the scaffolding: a setup script, a git repository with an initial commit, a progress file, and a requirements file in JSON (JavaScript Object Notation) listing every feature the application must have, each marked *failing* to begin with. For the study's clone of a chat application that meant over 200 discrete features, at the granularity of "a user can open a new chat, type in a query, press enter, and see an AI response". A **coding agent** then runs session after session under three standing rules: one feature at a time; verify it end to end through browser automation, driven by a Puppeteer server over the Model Context Protocol (MCP), before marking it passing; and commit with a descriptive message and update the progress file before the session ends.

Each rule closes a named mode with a named component:

- The feature list with per-feature pass/fail is a **verification loop** ([Post 11](../11-verification-loops/index.md)). "Done" becomes a count of passing checks rather than a claim, which is what makes victory declaration *detectable*: with over 200 independently checkable features, an agent reporting done at 120 is contradicted by a file in the repository, not by a reviewer three days later.
- "One feature at a time" is the **planner split** ([Post 12](../12-planner-generator-evaluator/index.md)) at its smallest useful size, with the decomposition written down before any code exists, so one-shotting has nowhere to go.
- The progress file and per-feature commits are **durable state** ([Post 08](../08-state-filesystem-git/index.md)) plus the handoff that makes a context reset survivable ([Post 18](../18-long-horizon-ralph/index.md)), turning a filling window from a quality cliff into a scheduled stop.

One detail is worth taking wholesale: the feature list is JSON rather than Markdown, because a model is less likely to quietly rewrite a structured file than a prose one (Anthropic, 2025). That is the ratchet instinct of §2.5 applied to an artefact instead of a rule.

---

## 6. Detecting them from a trace

Diagnosis needs evidence, so most of this list is only actionable once you have observability ([Post 21](../21-observability-traces/index.md)). Each mode leaves a characteristic signature in a run's trace:

![Six small trace sketches: turn boxes ending in a green exit followed by a failing check; a quality line sloping down against turn number; a bar chart with one enormous first turn; four identical call chips with a bar under the last three; a run axis with the same finding recurring; and a deny-listed command beside a BLOCKED stamp. Below them, a four-step ladder giving the order to run the tests in, cheapest evidence first.](diagrams/03-trace-signatures.svg)
*Reading a trace is pattern-matching against these six sketches: the shape carries the diagnosis, and the wording of any one log line does not.*

- **Victory declaration:** the loop exited on a "final answer" (stop ①), but a downstream check later failed. Signal: *completed runs with failing outcomes.*
- **Context anxiety:** quality falls as a function of turn number or tokens used, not task difficulty. Signal: *late-run answers are worse than early-run ones.*
- **One-shotting:** a single enormous tool call or diff with no intermediate steps. Signal: *one turn does almost everything.*
- **Doom loop:** the same tool-call signature repeats. Signal: *identical `(tool, args)` across consecutive turns*, exactly what stop ④ watches for.
- **Silent drift:** the same reviewer or lint finding recurs across many runs. Signal: *a rule you "fixed" keeps reappearing.*
- **Destructive action:** a tool call matching a dangerous pattern. Signal: *a command on the deny-list was attempted.*

Those are the cheap signals, readable from an ordinary run log with no tracing stack. Four of the six are shapes *over turns* rather than facts about a single turn, which is why a per-call log is not enough. Read as *span geometry* they become recognisable waterfall shapes, and one sharpens: the strongest tell for victory declaration is a run that exits with no verification span at all, an absence rather than a failure ([Post 21](../21-observability-traces/index.md) §4).

**What "identical" means in practice.** The doom-loop bullet hides the only detail that matters: how a harness decides two turns are the same. The companion loop, [`code/03-agent-loop/`](../../code/03-agent-loop/), settles it in eight lines of `loop.py`.

```python
def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps(
        [[tu.name, tu.input] for tu in tool_uses], sort_keys=True)

# ...once per turn, inside the loop body:
recent.append(_signature(resp.tool_uses))
window = recent[-no_progress_window:]
if len(window) == no_progress_window and len(set(window)) == 1:
    return Result(None, StopReason.NO_PROGRESS, step, tokens_used, messages)
```

The default window is three, so three consecutive turns of byte-identical tool calls end the run. Two things follow. The same fingerprint over an *archived* transcript is a doom-loop query rather than an exit, which is how the mode is found in finished runs. And because the loop's `Result` carries a stop reason of `COMPLETED`, `MAX_ITERS`, `BUDGET` or `NO_PROGRESS`, "completed runs with failing outcomes" becomes a join rather than a phrase.

```python
# The same fingerprint, run over an archive rather than a live loop.
def doom_loop_turns(transcript, window=3):
    sigs = [_signature(turn["tool_uses"]) for turn in transcript]
    return [i for i in range(window - 1, len(sigs))
            if len(set(sigs[i - window + 1:i + 1])) == 1]

# Victory declaration is a join, not a pattern: runs the harness called
# COMPLETED whose downstream check disagreed.
victory = [r for r in runs
           if r.stop_reason is StopReason.COMPLETED and not r.checked_ok]
```

**Not every repetition is a doom loop.** A naive match over-fires on exactly the runs you least want to kill: an agent polling a build, retrying a flaky call, or re-submitting after a correction. This series found it while building [`code/24-minimal-harness/`](../../code/24-minimal-harness/), where a gate rejection sends a failure report back into the loop, the agent fixes the bug and re-submits, and a plain detector reads that as repetition. The run was being killed for making progress. The fix in `harness.py` is one line, and its comment is the lesson:

```python
    messages.append({"role": "user",
                     "content": f"verification failed: {verdict.report}"})
    recent.clear()  # a real correction is progress; reset the detector
```

Two mitigations generalise: use a *window* rather than a single repeat, and reset the detector whenever genuinely new information enters the loop. One limitation is worth stating rather than hiding: the shipped detector compares *tool calls*, not observations, so an agent re-running the same command against changing state is invisible to it. The "unchanged observations" half of §2.4's definition is design intent, not implemented code.

---

## 7. Differential diagnosis: the confusable pairs

Six signatures are enough when the trace is clean. In front of a genuinely bad run they are not, because several modes wear each other's clothes. The question is rarely "what does a doom loop look like" but "which of these two is it", and each pair is separated by a single measurement.

| These two look alike | The measurement that separates them | How to read the answer |
| -------------------- | ----------------------------------- | ---------------------- |
| Context anxiety vs one-shotting | Work done per turn against turn index, and quality against task difficulty | Anxiety tracks turn index and window fill; one-shotting is a bar chart with an enormous first bar and near-empty ones after |
| Victory declaration vs silent drift | Is the fault visible inside one run, or only across many? | Victory declaration is caught within a run by a check the run never made; drift is the same finding recurring across runs |
| Doom loop vs slow but real progress | Successive tool-call signatures, not turn counts | An agent doing new work changes its signature every turn, which is why the detector compares fingerprints rather than counting iterations |
| Destructive action vs one that was stopped | The recorded outcome on the tool span | `blocked` (hook), `denied` (approval) and `refused` (sandbox) are successes; `ok` on a deny-listed command is the incident ([Post 14](../14-permissions-sandboxes/index.md) §5) |
| Silent drift vs a convention never written down | Read the assembled prompt for that run | If the rule is not in the window this is not drift, it is a missing memory file ([Post 10](../10-continual-learning-ratchet/index.md)) |

The fourth row is the reason gate outcomes must be distinguishable at all. A sandbox that refuses a command inside the tool and returns an ordinary string leaves the trace unable to tell a refusal from a command that ran, which is precisely the defect this series found and fixed in its own second build ([Post 25](../25-build-harness-plus/index.md) §10). A guardrail you cannot see fire is a guardrail you cannot audit.

Walk the tests in cost order, as the sibling series' diagnostic checklist does (Context Engineering, Post 06): the stop reason first because it is free, signatures next because they are one pass over the transcript, then quality against turn index because it needs a metric, and only then an LLM judge over sampled runs. The first test that earns a yes is almost always the right diagnosis.

---

## 8. The triage table, and what to build first

Collapsed to a lookup, the fastest path from symptom to fix:

| You observe… | Failure mode | Change these components |
| ------------ | ------------ | ----------------------- |
| "Done!" but it isn't | Victory declaration | Verification loop ([Post 11](../11-verification-loops/index.md)) |
| Quality drops late in a long run | Context anxiety | Context management ([Post 09](../09-context-management-loop/index.md)) |
| One giant undocumented change | One-shotting | Planner / evaluator ([Post 12](../12-planner-generator-evaluator/index.md)) |
| Same action, no change | Doom loop | No-progress stop ([Post 03](../03-the-agent-loop/index.md)) |
| Ignores your conventions | Silent drift | Memory file + hook ([Posts 10](../10-continual-learning-ratchet/index.md) · [13](../13-hooks-enforcement/index.md)) |
| Dangerous command | Destructive action | Deny-list hook + sandbox ([Posts 13](../13-hooks-enforcement/index.md) · [14](../14-permissions-sandboxes/index.md)) |

A lookup answers "which component", not "which first", and a real agent usually needs three or four of these. The order this series' own builds follow falls out of §3's cost column:

1. **The loop's exits and the verification gate.** Build #1 ([Post 24](../24-build-minimal-harness/index.md)) ships the loop, a schema-validated tool registry, a verification gate and all four stop conditions. Victory declaration and doom loop close first: they are the cheapest fixes, and the gate is a precondition for trusting any later measurement, since an unverified run cannot tell you whether your next change helped.
2. **The blast-radius layers.** Build #2 ([Post 25](../25-build-harness-plus/index.md)) adds hooks, a sandbox, a human approval gate and a sub-agent, closing destructive action at the moment the agent is handed tools that reach something real.
3. **Context management and the ratchet.** [Post 09](../09-context-management-loop/index.md) and [Post 10](../10-continual-learning-ratchet/index.md) earn their place once runs are long enough for the window to matter and repeated enough for conventions to drift.

One dependency appears nowhere in the table: everything in §6 and §7 needs a trace first ([Post 21](../21-observability-traces/index.md)). Without one you are not diagnosing, you are guessing with extra steps.

---

## 9. What is not on this list

A taxonomy that claims to cover everything is unfalsifiable. Three classes of failure sit deliberately outside these six, and a reader whose bug is one of them should stop hunting for a mode.

- **Context-layer failures.** The model reading one assembled window badly: distraction, confusion, conflict, lost-in-the-middle, tool-storm. These are failures of *what the model sees on a single call*, fixed at token level rather than at runtime (Context Engineering, Post 06). An agent can be free of all six runtime modes and still be handed a bad window every turn.
- **Systems failures.** A rate limit, a truncated response, malformed JSON from a tool, a transport error. These are ordinary engineering bugs, appearing in a trace as spans that never returned ([Post 21](../21-observability-traces/index.md)). Treating a transient transport error as a stop condition is itself a mistake: it deserves a bounded retry ([Post 19](../19-loop-engineering/index.md)).
- **Adversarial failures.** Indirect prompt injection through a tool result, or tool poisoning through a server description the agent was never meant to trust. These are attacks rather than gaps ([Post 14](../14-permissions-sandboxes/index.md)). A hook that stops your agent making a mistake is not a hook that stops an attacker steering it.

One genuine runtime mode is folded rather than counted: **incoherence across context windows**, where multi-session work drifts because each session rebuilds its own understanding of the task (Osmani, 2026). It belongs to long-horizon execution ([Post 18](../18-long-horizon-ralph/index.md)) rather than to a single run.

---

## 10. Naming is the first fix

The reason this taxonomy matters is not that it is complete; it is that it is *actionable*. "My agent is flaky" invites you to reach for the one lever that almost never helps: a bigger model. Naming the mode redirects you to the lever that does. The failure has an address, the address has a fix, and §8 tells you which fix to build first.

The rest of the series builds those fixes. When you reach [Post 11](../11-verification-loops/index.md) (verification) or [Post 13](../13-hooks-enforcement/index.md) (hooks), you will already know exactly which failure you are buying insurance against.

---

## Common pitfalls

- **Reaching for a bigger model first.** None of the six is fixed by model choice: five are harness gaps and the sixth is a safety boundary (§1, and Post 04). Diagnose before you upgrade.
- **Trusting the model's own "done".** Stopping on a final answer means the model *believes* it is finished, not that it *is* (§2.1).
- **Treating a doom loop as a reasoning problem.** It is a missing stop condition, not a dumb model. Add exit ④ (§2.4; Post 03).
- **Shipping a stall detector that kills healthy runs.** A bare "same call twice" rule fires on polling, on retries, and on an agent correcting itself after a gate rejection. Use a window, and reset it when real feedback arrives (§6).
- **Fixing silent drift with a stern system prompt.** A convention held only by the model's goodwill drifts. Enforce it with a hook (§2.5).
- **Relying on the model to avoid destructive commands.** Judgement is not a safety control. Block the class of command deterministically, and make the refusal visible in the trace (§2.6, §7).
- **Debugging without a trace.** Most of these modes are invisible until you can see the run (§6).
- **Assuming one fix per agent.** A real agent needs three or four of these components, and the order matters as much as the set (§8).

---

## Further reading

- Anthropic, "Effective harnesses for long-running agents" (Anthropic Engineering, November 2025): the primary study behind three of the six modes, and the initialiser-plus-coding-agent harness that fixed them.
- Faros AI, "Harness Engineering" (2026): victory declaration, context anxiety and one-shotting as named production failure modes, credited to Anthropic's research.
- Addy Osmani, "Agent Harness Engineering" (2026): early stopping, poor decomposition and incoherence across context windows; the positive skew of self-grading; the ratchet and hooks.
- Kief Morris, "Humans and Agents in Software Engineering Loops" (martinfowler.com, 2026): the humans outside / in / on the loop spectrum, and the case that the human's job is building the harness rather than inspecting each output.
- Drew Breunig, "How Long Contexts Fail" (2025): the context-layer failure taxonomy this runtime one parallels, and the essay the sibling series adapts.
- Context Engineering, Post 06: the five *context* failure modes this taxonomy sits above, and the ordered diagnostic walk §7 borrows its cost ordering from.
- Yao et al., "ReAct" (2022): the reason → act → observe loop whose stages give each failure the address it is diagnosed by in §4.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 21 — Observability & trace-driven repair](../21-observability-traces/index.md)**: the traces §6 depends on, and the waterfall shapes each of these modes deforms a run into.
- **[Post 11 — Verification loops](../11-verification-loops/index.md)**: the fix for victory declaration, the first failure most naive agents hit.
- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the ACT stage in depth, the surface where destructive action is prevented or permitted.
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: revisit the loop and its stop conditions, the home of doom loops and context anxiety.
