# 05 - Agent failure modes: victory declaration, context anxiety, doom loops

> **TL;DR.** Autonomous agents fail in a small set of recurring, nameable ways, and each one maps to a harness component that can be changed. This post catalogues six: victory declaration, context anxiety, one-shotting, doom loop, silent drift and destructive action; five are performance failures that a re-run or undo recovers, and one is a safety failure that neither undoes. A trace shows which mode a bad run is, and the mode names the fix, which turns "my agent is flaky" into a diagnosis. The six are the runtime counterpart of the five context failure modes of `ctx-006`.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the agent loop and its four exits.
> **Safe to skip?** Skip it if the reader can already name the six modes and the component that fixes each, tell them apart in a trace, and say why victory declaration can only be found by joining a run's stop reason to a check it never made.
>
> **After reading, you will be able to:**
>
> - Recognise each of the six failure modes, victory declaration to destructive action, from a symptom or a trace, and name the component that fixes it.
> - Say what each mode costs and who pays, and work out what a doom loop costs with and without the no-progress exit.
> - Separate the confusable pairs of modes with the one measurement that tells each pair apart.
> - Use the triage table to decide which fix to build first, and say which failures fall outside the six.
> - Run a trace fingerprint over archived runs, count hits per mode, and show that victory declaration appears only as a completed stop joined to a failed check.

![Six cards, one per failure mode, each with its symptom and its fix: verification, context management, a planner split, the no-progress exit, the ratchet, and hooks with permissions for destructive action, the one safety failure.](diagrams/01-failure-modes-grid.svg)

*Six modes, each with an address in the harness: the fix is a named piece of machinery, not a larger model.*

---

## 1. "My agent is flaky" is not a diagnosis

In which recurring, nameable ways do autonomous agents fail, and which harness component fixes each? The sibling series answered the same question one layer down. `ctx-006` resolves a vague complaint about a large language model (LLM) application into one of five named *context* failures: distraction, confusion, conflict, lost-in-the-middle and tool-storm, adapted from Drew Breunig's "How Long Contexts Fail" (22 June 2025; Breunig, 2025). Naming them was the first step to fixing them.

Agents that *run*, looping, calling tools and acting unattended, have their own taxonomy one layer up: not failures of what the model *sees* on one call, but of what the harness *does* across many calls.

**Where these six come from.** Faros AI's guide to harness engineering (22 May 2026) lists *victory declaration bias*, *context anxiety* and *one-shotting overreach* as failure modes "solvable at the harness level", crediting Anthropic's research (Faros AI, 2026). Anthropic's articles describe them: "Effective harnesses for long-running agents" (Justin Young, 26 November 2025) reports an agent that tried to one-shot an application and a later session that declared the job done (Anthropic, 2025), and "Harness design for long-running application development" (Prithvi Rajasekaran, 24 March 2026) names context anxiety (Anthropic, 2026). The doom loop is older than agents: the thrashing any control loop without a progress check reaches, which is why [post 03](../03-the-agent-loop/index.md) counts no-progress detection among its four exits. Silent drift and destructive action are this series' additions, the two failures a harness can make structurally difficult rather than merely less likely.

A second list overlaps without matching. Addy Osmani's "Agent Harness Engineering" (19 April 2026) says today's models "suffer from early stopping, poor decomposition of complex problems, and incoherence as work stretches across multiple context windows", and treats context rot as a problem of its own (Osmani, 2026). Early stopping overlaps victory declaration and context anxiety, poor decomposition is one-shotting, and context rot underlies context anxiety. Cross-window incoherence belongs to multi-session work ([post 18](../18-long-horizon-ralph/index.md)). Two lists that agree on two modes and a mechanism support this taxonomy without proving it complete; section 9 states what falls outside.

One split governs the rest. **Five of the six are performance failures**, which a re-run or undo recovers. **One, destructive action, is a safety failure**, which a re-run cannot undo. Each maps to a component of [post 02](../02-anatomy-of-a-harness/index.md)'s anatomy, and each has a fix that does not wait for a better model.

---

## 2. The six failure modes

Each mode is stated as *symptom, why it happens, the fix*. The numbering is stable, and other posts cite these subsections by number. The grid at the top of the post is the catalogue in one view.

### 2.1 Victory declaration

**Symptom.** The agent announces that the task is complete when it is not: tests still red, the feature half-built, the question half-answered.

*Why:* the model is trained to be helpful and to conclude, and it judges its own work generously: "agents reliably skew positive when grading their own work" (Anthropic, 2026), a line Osmani repeats. It is what happens whenever the author of a piece of work is also its only judge.

*Fix:* **verification**: a check against ground truth (tests, a schema, an independent judge) before the loop may exit on a final answer, the first component this series adds to a naive agent ([post 11](../11-verification-loops/index.md)).

### 2.2 Context anxiety

**Symptom.** As the context window fills, the work gets worse: the agent cuts corners, drops steps, or wraps up before the task is done.

*Why:* Anthropic names it: "Some models also exhibit 'context anxiety,' in which they begin wrapping up work prematurely as they approach what they believe is their context limit" (Anthropic, 2026). The article reports this from its own harness work, not from a published measurement: Claude Sonnet 4.5 showed it strongly enough that compaction alone was not sufficient, and Opus 4.5 "largely removed that behavior on its own". Beneath it sits a measured mechanism, context rot: recall and reasoning sag as an input grows long ([post 09](../09-context-management-loop/index.md)). It is the one mode the sources tie to a model generation, so its shape in a trace (section 6) is checked, not assumed.

*Fix:* active **context management**, a ladder from offloading a large output to disk, through clearing tool results already acted on and compacting older turns into a summary, up to a full reset behind a handoff file ([post 09](../09-context-management-loop/index.md)). The cheapest rung that works is the right one.

### 2.3 One-shotting

**Symptom.** The agent attempts the whole task in a single sweep, producing one large, undocumented change that is hard to review and often wrong somewhere.

*Why:* without structure, the model treats a multi-step task as one step. Anthropic's long-running-agent article describes exactly this: the agent "tended to try to do too much at once", in the article's words an attempt "to one-shot the app" (Anthropic, 2025).

*Fix:* a **planner, generator, evaluator split** that forces decomposition and staged review, the verification component applied before any code exists ([post 12](../12-planner-generator-evaluator/index.md)). The harness makes the model plan before it acts, and the plan is written where a later session can read it.

### 2.4 Doom loop

**Symptom.** The agent repeats the same action (re-running a failing command, re-reading a file), busy but making no progress.

*Why:* nothing in a naive loop notices that the state has stopped changing, and given a transcript in which it tried something, the model's most probable continuation is to try it again. It is a missing stop condition, not a weak model.

*Fix:* the loop's **no-progress exit**, exit (4) of [post 03](../03-the-agent-loop/index.md): detect repeated tool calls or unchanged observations across *N* turns and stop. Section 6 shows the eight lines that implement it; section 3 prices a doom loop without them.

### 2.5 Silent drift

**Symptom.** The agent quietly ignores the project's conventions (the wrong test framework, the wrong formatting, a pattern corrected before) and keeps doing so, run after run.

*Why:* the convention was never durably part of what the harness sends, or it was and nothing enforces it; a rule that lives only in a conversation dies with it.

*Fix:* the **ratchet**: put the rule in a memory file the harness injects every session ([post 10](../10-continual-learning-ratchet/index.md)) *and* back it with a **hook** that enforces it deterministically ([post 13](../13-hooks-enforcement/index.md)). A convention held only by the model's goodwill drifts, and a stern line in the system prompt is still goodwill.

### 2.6 Destructive action

**Symptom.** The agent runs something dangerous. Osmani's examples of what a hook should block are the ones worth blocking first: `rm -rf`, `git push --force` and `DROP TABLE` (Osmani, 2026).

*Why:* it has real tools and a real blast radius, and judgement is not a safety mechanism: at a thousand risky commands a quarter, an agent careful 999 times in 1,000 (illustrative rates) still runs one.

*Fix:* a **deny-list hook** that blocks the class of command ([post 13](../13-hooks-enforcement/index.md)) inside a **sandbox** that bounds what any command can reach ([post 14](../14-permissions-sandboxes/index.md)): hooks and permissions. This is the only mode whose fix must run *before* the action, because there is no after.

---

## 3. What each mode costs, and who pays

Symptom and fix are enough to diagnose but not to prioritise. The second axis is cost.

| Mode | What it consumes | Who pays | Recovered by a re-run? |
| ---- | ---------------- | -------- | ---------------------- |
| Victory declaration | A run, plus a review cycle spent on work never done | The reviewer, then the user who trusted it | Yes, though trust returns slowly |
| Context anxiety | The tail of a long run, its worst and dearest turns | The budget, then the re-run | Yes |
| One-shotting | Review capacity: one change nobody can bisect | The reviewer | Yes |
| Doom loop | The remaining token and wall-clock budget | The budget | Yes |
| Silent drift | A little of every run, compounding across the repository | The whole team, quietly | Only by undoing each instance |
| Destructive action | Whatever the command reached | Whoever owned the data | **No** |

Every cost but the last can be reclaimed, by a re-run or by undoing the drift, which is why destructive action alone needs a gate in front of it.

**A worked example: what a doom loop costs.** A doom loop is the cheapest failure to detect and among the dearest to leave running, because its cost grows with the square of its length. Take a loop whose transcript grows by 4,000 tokens a turn (one model response plus one tool result; an illustrative size, not a measurement) and is re-read on every call. Turn $k$ then reads $4{,}000k$ input tokens, and a run of $n$ turns reads $2{,}000\,n(n+1)$ in all. `snippets/doom_loop_cost.py` drives the companion loop of post 03, [`code/03-agent-loop/`](../../code/03-agent-loop/), with a scripted model that reads a file, runs the tests, makes an edit, and from turn 4 runs the same failing tests on every turn. Running `uv run python posts/05-agent-failure-modes/snippets/doom_loop_cost.py` from the series root prints:

```text
exits enabled                           stop reason  turn  input tokens
no-progress window of 3, cap of 12      no_progress     6        84,000
cap of 12 only (the default)              max_iters    12       312,000
cap of 40 only                            max_iters    40     3,280,000
cap of 12 / no progress: 3.71 times
cap of 40 / no progress: 39.05 times
```

With the no-progress exit at its default window of three, the run stops on turn 6 after 84,000 input tokens. With only the companion's default cap of 12, the same worthless run reads 312,000, 3.71 times as much; with a cap of 40, 3,280,000, 39 times as much. The ratio holds at any per-token price and grows with the cap. That is why exit (4) is worth building before leaning on exit (2): the cap stops the run only once the expensive part has been paid for ([post 23](../23-economics-haas/index.md) works the economics in full).

---

## 4. Where they strike: failures cluster in the loop

Mapped onto the reason, act, observe loop of [post 03](../03-the-agent-loop/index.md), the six cluster at specific stages, which is why each has a specific fix. The figure below marks where each mode shows and where its fix sits.

![The agent loop of reason, act and observe with red failure tags where each mode shows, and purple gates where each fix installs: verification on the exit, the no-progress check and the deny-list hook before act, context management between turns, the memory file at session start.](diagrams/02-where-failures-strike.svg)

*The stage that shows a symptom is not always the stage that carries its fix.*

- **At reason**, where the model decides, live the *judgement* failures: victory declaration and one-shotting.
- **At act**, where a tool runs, lives the *blast-radius* failure: destructive action.
- **At observe, as the loop turns again**, live the *iteration* failures: doom loop and context anxiety.
- **Across turns** lives the *consistency* failure: silent drift.

**The address of a failure is not always the address of its fix.** Victory declaration is a decision made at reason, but its fix sits on the loop's **exit**, the only point at which a candidate answer exists to be checked. Context anxiety is a property of the accumulated window, so its fix runs between turns. Silent drift is fixed at session start, where the memory file is injected, and before each tool call, where the hook fires. The working rule: **instrument at the stage where the symptom shows; install the fix at the stage that controls it.** The trace names the mode; [post 02](../02-anatomy-of-a-harness/index.md)'s map names the component.

---

## 5. A harness that fixed three of them

The clearest public example of this taxonomy at work is Anthropic's account of a harness built so that a coding agent could construct a large application across many context windows (Anthropic, 2025). Its premise: even "a frontier coding model like Opus 4.5" falls short given only a high-level prompt.

The article reports two failure patterns. First, the agent "tended to try to do too much at once", one-shotting (section 2.3), and this often "led to the model running out of context in the middle of its implementation, leaving the next session to start with a feature half-implemented and undocumented": the full window that context management exists for (section 2.2), though the article reports the exhaustion rather than the rushing. Second, "a later agent instance would look around, see that progress had been made, and declare the job done": victory declaration (section 2.1). It also reports features marked complete without an end-to-end test.

None of the fixes was a different model. An **initialiser agent** runs once and writes the scaffolding: an `init.sh` script, a progress file, an initial git commit, and a feature list in JSON (JavaScript Object Notation), each feature marked *failing* to begin with; for the article's clone of claude.ai, over 200 features, such as "a user can open a new chat, type in a query, press enter, and see an AI response". A **coding agent** then runs session after session under three rules: one feature at a time; test it end to end with browser automation, through a Puppeteer server over the Model Context Protocol (MCP), before marking it passing; and commit with descriptive messages and summarise progress in the progress file.

Each rule closes a named mode with a named component:

- The feature list with a pass or fail per feature is **verification** ([post 11](../11-verification-loops/index.md)). "Done" becomes a count of passing checks rather than a claim: an agent that reports done with, say, 120 of over 200 features passing is contradicted by a file in the repository.
- "One feature at a time" is the **planner split** ([post 12](../12-planner-generator-evaluator/index.md)) at its smallest, with the decomposition written before any code exists, so one-shotting has nowhere to go.
- The progress file and the commits are **state** ([post 08](../08-state-filesystem-git/index.md)), the handoff that makes a fresh context survivable ([post 18](../18-long-horizon-ralph/index.md)), turning a full window from a quality cliff into a scheduled stop.

The feature list is JSON rather than Markdown because "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files" (Anthropic, 2025): the ratchet's instinct applied to an artefact.

---

## 6. Detecting them from a trace

Diagnosis needs evidence, so most of this list is only actionable once there is observability ([post 21](../21-observability-traces/index.md)). Each mode leaves a characteristic signature in a run's trace:

- **Victory declaration:** the loop exited on a final answer, exit (1), but a downstream check failed. Signal: *completed runs with failing outcomes.*
- **Context anxiety:** quality falls as a function of turn number or tokens used, not of task difficulty. Signal: *late-run answers are worse than early-run ones.*
- **One-shotting:** a single enormous tool call or diff with no intermediate steps. Signal: *one turn does almost everything.*
- **Doom loop:** the same tool-call signature repeats. Signal: *identical `(tool, args)` across consecutive turns*, exactly what exit (4) watches for.
- **Silent drift:** the same reviewer or lint finding recurs across many runs. Signal: *a rule that was "fixed" keeps reappearing.*
- **Destructive action:** a tool call matching a dangerous pattern. Signal: *a command on the deny-list was attempted.*

These are cheap signals, readable from an ordinary run log. Four of the six are shapes *over turns* or runs rather than facts about one turn, which is why a per-call log is not enough. Read as span geometry, one sharpens: the strongest tell for victory declaration is a run that exits with no verification span at all ([post 21](../21-observability-traces/index.md)).

**What "identical" means in practice.** The doom-loop signal hides the one detail that matters: how a harness decides that two turns are the same. The companion loop settles it in eight lines of `loop.py`: four that fingerprint a turn,

```python
def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps(
        [[tu.name, tu.input] for tu in tool_uses], sort_keys=True)
```

and four inside the loop body, once per turn:

```python
        recent.append(_signature(resp.tool_uses))
        window = recent[-no_progress_window:]
        if len(window) == no_progress_window and len(set(window)) == 1:
            return Result(None, StopReason.NO_PROGRESS, step, tokens_used, messages)
```

The default window is three, so three consecutive turns of byte-identical tool calls end the run. Two things follow. The same fingerprint over an *archived* transcript is a doom-loop query rather than an exit, which finds the mode in finished runs. And because the loop's `Result` carries a stop reason of `COMPLETED`, `MAX_ITERS`, `BUDGET` or `NO_PROGRESS`, "completed runs with failing outcomes" becomes a join. `snippets/trace_fingerprint.py` does both over seven scripted runs of the companion loop, with the companion's own `_signature`:

```python
# The same fingerprint, run over an archive rather than a live loop.
def doom_loop_turns(transcript, window=3):
    sigs = [_signature(turn["tool_uses"]) for turn in transcript]
    return [i for i in range(window - 1, len(sigs))
            if len(set(sigs[i - window + 1:i + 1])) == 1]
```

```python
# Victory declaration is a join, not a pattern: runs the harness called
# COMPLETED whose downstream check disagreed.
victory = [r for r in runs
           if r["stop_reason"] is StopReason.COMPLETED and not r["checked_ok"]]
```

Running `uv run python posts/05-agent-failure-modes/snippets/trace_fingerprint.py` from the series root prints:

```text
run     stop reason  check
run-01  completed    passed
run-02  completed    failed
run-03  max_iters    failed
run-04  no_progress  failed
run-05  no_progress  failed
run-06  completed    passed
run-07  completed    failed

completed, by stop reason alone: run-01, run-02, run-06, run-07
victory declaration: 2  run-02, run-07
context anxiety:     0  needs a quality score per turn; this archive has none
one-shotting:        1  run-07
doom loop:           2  run-03, run-04
silent drift:        3  run-01, run-03, run-07
destructive action:  1  run-06
identical calls, changing results (a poll, not a doom loop): run-05
```

The figure below draws five of those runs turn by turn. Four runs stopped as `completed`, and nothing in their stop reasons separates the two that passed from the two that failed; only the join with the check does. Run-07 is both one-shotting and victory declaration: one run can show two modes. Run-03 never hit exit (4), because its configuration had no window, yet the archive query finds its doom loop. Run-06 passed its check and is still the incident, because `rm -rf build/` ran. Context anxiety finds nothing: that signal needs a quality metric per turn, not a fingerprint.

![Five archived runs drawn turn by turn: a run that declares done and fails its check, a 412-line edit declared done, a run stopped on three identical test calls, a build poll stopped although its results changed, and a run that ran rm -rf build/ and passed its check.](diagrams/03-trace-signatures.svg)

*The shape of a run carries the diagnosis; the wording of any one log line does not.*

**Not every repetition is a doom loop.** A naive match over-fires on exactly the runs least worth killing: a poll, a retry of a flaky call, a re-submission after a correction. Run-05 is the poll: three identical `build_status` calls whose results changed from `queued` to `running`, stopped as `no_progress` all the same. This series met the re-submission case while building [`code/24-minimal-harness/`](../../code/24-minimal-harness/): a gate rejection sends a failure report back into the loop, the agent fixes the bug and re-submits, and a plain detector reads that as repetition, killing the run for making progress. The fix in `harness.py` is one line, and its comment is the lesson:

```python
            messages.append({"role": "user",
                             "content": f"verification failed: {verdict.report}"})
            recent.clear()  # a real correction is progress; reset the detector
```

Two mitigations generalise: use a *window* rather than a single repeat, and reset the detector whenever genuinely new information enters the loop. One limitation is worth stating: the shipped detector compares *tool calls*, not observations, so it cannot tell a poll whose result changes from a retry whose result does not. The "unchanged observations" half of section 2.4's definition is design intent in the companion; the archive query adds it after the fact, which is how it separates run-05 from run-04.

---

## 7. Differential diagnosis: the confusable pairs

Six signatures are enough when the trace is clean. In front of a genuinely bad run several modes wear each other's clothes, and the question becomes "which of these two is it". Each pair is separated by a single measurement.

| These two look alike | The measurement that separates them | How to read the answer |
| -------------------- | ----------------------------------- | ---------------------- |
| Context anxiety and one-shotting | Work done per turn against turn index, and quality against task difficulty | Anxiety tracks turn index and window fill; one-shotting is one enormous first turn and near-empty ones after |
| Victory declaration and silent drift | Is the fault visible inside one run, or only across many? | Victory declaration is caught within a run by a check the run never made; drift is the same finding recurring across runs |
| Doom loop and slow but real progress | Successive tool-call signatures and their results, not turn counts | An agent doing new work changes its signature or its result every turn, which is why the detector compares fingerprints rather than counting iterations |
| Destructive action and one that was stopped | The recorded outcome on the tool span | `blocked` (hook), `denied` (approval) and `refused` (sandbox) are successes; `ok` on a deny-listed command is the incident ([post 14](../14-permissions-sandboxes/index.md)) |
| Silent drift and a convention never written down | Read the assembled prompt for that run | If the rule is not in the window this is not drift, it is a missing memory file ([post 10](../10-continual-learning-ratchet/index.md)) |

The fourth row is why gate outcomes must be distinguishable at all. A sandbox that refuses a command inside the tool and returns an ordinary string leaves the trace unable to tell a refusal from a command that ran, the defect this series found and fixed in its own second build ([post 25](../25-build-harness-plus/index.md)).

Walk the tests in cost order, much as `ctx-006`'s checklist orders questions by the evidence needed: the stop reason first, because it is free; signatures next, one pass over the transcript; then quality against turn index, which needs a metric; and only then an LLM judge over sampled runs. The first test that earns a yes is the first place to look.

---

## 8. The triage table, and what to build first

Collapsed to a lookup, the fastest path from symptom to fix:

| Observed | Failure mode | Component to change |
| -------- | ------------ | ------------------- |
| "Done!", but it isn't | Victory declaration | Verification ([post 11](../11-verification-loops/index.md)) |
| Quality drops late in a long run | Context anxiety | Context management ([post 09](../09-context-management-loop/index.md)) |
| One giant undocumented change | One-shotting | Verification as a planner, generator, evaluator split ([post 12](../12-planner-generator-evaluator/index.md)) |
| Same action, no change | Doom loop | The loop's no-progress exit ([post 03](../03-the-agent-loop/index.md)) |
| Ignores the project's conventions | Silent drift | Memory and hooks, the ratchet (posts [10](../10-continual-learning-ratchet/index.md) and [13](../13-hooks-enforcement/index.md)) |
| Dangerous command | Destructive action | Hooks and permissions: a deny-list hook and a sandbox (posts [13](../13-hooks-enforcement/index.md) and [14](../14-permissions-sandboxes/index.md)) |

A lookup answers "which component", not "which first", and a real agent often needs three or four of these. The order this series' builds follow falls out of section 3's cost column:

1. **The loop's exits and the verification gate.** Build #1 ([post 24](../24-build-minimal-harness/index.md)) ships the loop, a schema-validated tool registry, a verification gate and all four exits. Victory declaration and doom loop close first: they are the cheapest fixes, and an unverified run cannot say whether any later change helped.
2. **The blast-radius layers.** Build #2 ([post 25](../25-build-harness-plus/index.md)) adds hooks, a sandbox, a human approval gate and a sub-agent, closing destructive action beyond Build #1's deny list, for tools that reach something real.
3. **Context management and the ratchet.** [Post 09](../09-context-management-loop/index.md) and [post 10](../10-continual-learning-ratchet/index.md) earn their place once runs are long enough for the window to matter and repeated enough for conventions to drift.

Everything in sections 6 and 7 needs a trace first ([post 21](../21-observability-traces/index.md)); without one, diagnosis is guessing.

---

## 9. What is not on this list

A taxonomy that claims to cover everything is unfalsifiable. Three classes of failure sit deliberately outside these six.

- **Context-layer failures.** The model reading one assembled window badly: distraction, confusion, conflict, lost-in-the-middle, tool-storm. These are failures of *what the model sees on a single call*, fixed at token level (`ctx-006`). An agent free of all six runtime modes can still be handed a bad window every turn.
- **Systems failures.** A rate limit, a truncated response, malformed JSON from a tool, a transport error: ordinary engineering bugs, appearing in a trace as spans that never returned ([post 21](../21-observability-traces/index.md)). A transient transport error deserves a bounded retry ([post 19](../19-loop-engineering/index.md)), not a stop condition; a run ended by a rate limit as if the agent had failed is the symptom of getting this wrong.
- **Adversarial failures.** Indirect prompt injection through a tool result, or tool poisoning through a server description the agent was never meant to trust: attacks rather than gaps ([post 14](../14-permissions-sandboxes/index.md)). A hook that stops a mistake is not a hook that stops an attacker steering the agent.

One genuine runtime mode is folded rather than counted: **incoherence across context windows** (Osmani, 2026), where each session rebuilds its own understanding of the task. It belongs to long-horizon execution ([post 18](../18-long-horizon-ralph/index.md)), not to one run.

---

## 10. Naming is the first fix

The taxonomy matters not because it is complete but because it is *actionable*. "My agent is flaky" invites the one lever that rarely helps first, a bigger model; naming the mode redirects attention to the lever that does. The failure has an address, the address has a fix, and the triage table says which fix to build first.

Kief Morris's "Humans and Agents in Software Engineering Loops" (martinfowler.com, 4 March 2026) draws the same line for the people around the agent. A human *in* the loop fixes each bad artefact; "The 'on the loop' way is to change the harness that produced the artefact so it produces the results we want" (Morris, 2026). A named failure mode makes that change specific, and the rest of the series builds the changes, from [post 11](../11-verification-loops/index.md) (verification) to [post 13](../13-hooks-enforcement/index.md) (hooks) and beyond.

---

## 11. Make it run

Both snippets run offline from the series root and import the companion loop of post 03 unchanged:

```bash
uv run python posts/05-agent-failure-modes/snippets/doom_loop_cost.py
uv run python posts/05-agent-failure-modes/snippets/trace_fingerprint.py
```

The first prints section 3's cost table, the second section 6's archive and hits per mode. To run the fingerprint over real runs, replace the scripted `runs` list with records that carry a transcript, a stop reason, the check's verdict and the reviewer's findings. The no-progress exit itself is tested by the companion's seven tests, run from inside `code/03-agent-loop/`:

```bash
uv run --extra dev pytest -q
```

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **Counting success by stop reason.** A dashboard reports every `completed` run as a success; the rate looks high while users report unfinished work, because victory declaration lives only in the join with the check.
- **A no-progress window that kills healthy runs.** A bare "same call twice" rule, or a window blind to results, ends a build poll or a post-rejection correction as `no_progress`. Good runs stop early on the doom-loop exit.
- **A refusal recorded as an ordinary result.** The sandbox blocks `rm -rf`, but the tool returns a plain string, so the trace shows `ok` and nobody can say whether the command ran.
- **Fixing the symptom's address instead of the fix's.** A team adds "check your work" to the prompt to stop victory declaration; the agent still exits on its own word, because the check belongs on the exit.

---

## Common pitfalls

1. **Reaching for a bigger model first.** Each of the six has a harness fix that does not wait for a better model; only context anxiety is reported to shrink with a newer one (section 2.2, and post 04).
2. **Trusting the model's own "done".** A final answer means the model *believes* it is finished, not that it *is* (section 2.1).
3. **Fixing silent drift with a stern system prompt.** A convention held by goodwill drifts; enforce it with a hook (section 2.5).
4. **Relying on the model to avoid destructive commands.** Block the class of command deterministically, and make the refusal visible in the trace (sections 2.6 and 7).
5. **Debugging without a trace.** Most of these modes are invisible until the run can be seen (section 6).

---

## Further reading

- Anthropic Engineering, Justin Young, "Effective harnesses for long-running agents" (26 November 2025): one-shotting and declaring the job done, and the harness that fixed them.
- Anthropic Engineering, Prithvi Rajasekaran, "Harness design for long-running application development" (24 March 2026): context anxiety named, and self-grading's positive skew.
- Faros AI, "Harness engineering: A guide to building better AI coding agents" (22 May 2026): three of the modes named, credited to Anthropic's research.
- Addy Osmani, "Agent Harness Engineering" (19 April 2026): early stopping, poor decomposition, incoherence across windows, context rot, and hooks against destructive commands.
- Kief Morris, "Humans and Agents in Software Engineering Loops" (martinfowler.com, 4 March 2026): humans outside, in and on the loop.
- Drew Breunig, "How Long Contexts Fail" (22 June 2025): the context-layer taxonomy `ctx-006` adapts.
- `ctx-006`: the five *context* failure modes this taxonomy sits above, and the diagnostic walk section 7 adapts.
- Yao et al., "ReAct" (2022): the reason, act, observe loop that gives each failure its address.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 06 - Tools as the agent's hands: bash, code, and schemas](../06-tools-bash-code/index.md):** the act stage in depth, the surface where destructive action is prevented or permitted.
- **[Post 21 - Observability and trace-driven repair: seeing what the harness did](../21-observability-traces/index.md):** the traces section 6 depends on, and the span shapes these modes leave in a run.
