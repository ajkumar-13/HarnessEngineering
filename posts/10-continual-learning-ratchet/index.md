# 10 - Continual learning and the ratchet: every mistake becomes a rule

> **TL;DR.** The model does not learn between sessions, but the harness can, by writing what it learns to a memory file the next session reads. The **ratchet** turns every failure into durable constraints, a memory-file line, a hook that enforces it and a reviewer check that catches it, so the same class of mistake does not recur. Nothing inside the loop reverses a rule, so a wrong rule is as permanent as a right one: rules are reviewed before they land and pruned on purpose.
>
> **Prerequisites:** [post 08](../08-state-filesystem-git/index.md), state on disk and the handoff file.
> **Safe to skip?** Skip it if the reader can already keep a memory file to a checklist, decide which of the ratchet's three teeth a failure earns, and say why a rule needs a reviewed root cause and a provenance note before it becomes permanent.
>
> **After reading, you will be able to:**
>
> - Keep a memory file that the harness reads at every session start, write each line so it can be enforced, and price what carrying it costs.
> - Turn one failure into the ratchet's three teeth, a memory-file line, a hook and a reviewer check, and decide which of them the failure earns.
> - Promote an observation to a rule only when it passes the three tests, with a reviewed root cause and a provenance note.
> - Prune a memory file of obsolete, contradictory and redundant rules, and read a rule's hook firing rate after it lands.
> - Run the companion's `Ratchet` and show the fix landing only after the rule exists, within one run and across sessions.

![One failure, a merged pull request with a commented-out test, fans out into three cards: a memory-file line in AGENTS.md read at session start, a pre-commit hook that greps the diff for skip markers on every commit, and a reviewer sub-agent that flags commented-out tests as a blocker.](diagrams/01-ratchet-mechanism.svg)

*One failure, three independent constraints: the model reads the rule, a hook blocks the mistake, a reviewer catches what slips through.*

---

## 1. Stateless model, learning harness

How does a harness get better over time when the model cannot learn between sessions? The model is stateless ([post 03](../03-the-agent-loop/index.md)): it keeps nothing between calls, let alone between sessions, and its weights do not change while it works. An agent that "learns from experience" is therefore not learning in the model; it is learning in the *harness*, which writes down what it discovered and reads it again next time.

[Post 08](../08-state-filesystem-git/index.md) gave the mechanism (files on disk) and [post 09](../09-context-management-loop/index.md) the discipline of keeping the window small. This post uses both for one purpose: **carrying knowledge across tasks and sessions**, component 05, memory, of [post 02](../02-anatomy-of-a-harness/index.md)'s map. Post 08's handoff file carries state *within* one long job; the memory file carries lessons *across* many. `ctx-016` sorts memory into episodic, semantic and procedural kinds, and sends rules that people write and change by review to the system prompt or `AGENTS.md` rather than to a memory store. That file is the subject here.

---

## 2. The memory file: read every session

The concrete artefact is a **memory file**: `AGENTS.md`, `CLAUDE.md`, or whatever file a harness injects at the start of each session. Osmani calls it "the single highest-leverage configuration point, because it lands in the system prompt every turn" (Addy Osmani, "Agent Harness Engineering", 19 April 2026). `AGENTS.md` is the vendor-neutral form of the convention. Its specification page calls it "a README for agents", says it "is now stewarded by the Agentic AI Foundation under the Linux Foundation", reports it "used by over 60k open-source projects", and lists Codex, Jules, Cursor, Aider, VS Code, Devin and GitHub Copilot's coding agent among the tools that read it (Agentic AI Foundation, agents.md, consulted 14 October 2026). `CLAUDE.md` is the counterpart for Claude Code; how these files compose with a system prompt is `ctx-014`'s subject.

The harness reads the file at session start and places it ahead of the first user turn, so it is part of the prompt prefix before the conversation begins: *effectively part of the system prompt* rather than a document the model might consult, in the most cache-sensitive position in the window. It holds the project's conventions and hard-won lessons: the package manager, the test command, the mistakes not to repeat. It is the core of the *custom* harness, the policy a team adds on top of the mechanism a vendor ships.

### What a line actually costs

Every line is paid for on every task, so it is worth pricing. Take a 40-line memory file at about 20 tokens a line (both illustrative): $40 \times 20 = 800$ tokens. At Claude Opus 5's base input rate of 5 dollars per million tokens, with a cache read at 0.1 times that (0.50 dollars) and a five-minute cache write at 1.25 times (6.25 dollars), as Anthropic's "Pricing" page lists them on 14 October 2026 (the rates move, so re-derive them against the current page), one model call costs $800 \times 5 / 10^6 = 0.004$ dollars uncached, 0.005 dollars to write the cache and 0.0004 dollars to read it, as `snippets/line_cost.py` prints. At an illustrative 100 calls a day, a year is 36,500 calls, and carrying the file costs between $36{,}500 \times 0.0004 = 14.60$ dollars (every call a cache read) and $36{,}500 \times 0.004 = 146$ dollars (every call uncached), depending on how often the prefix is warm.

So the fortieth line is not expensive in money. The budget actually being spent is **attention**: "Every line is competing for attention, and more rules make each rule matter less" (Osmani, 2026). A line the model skims dilutes the lines it should have followed and teaches it that this file holds material it can safely ignore. That is why the rule is "earn each line", not "keep it under N tokens".

---

## 3. Earn each line: a checklist, not a manual

The common way a memory file fails is by growing into a style guide nobody follows. Osmani's corrective is a hard discipline in five words, "Pilot's checklist, not style guide", followed by "Earn each line" and "Rules should trace to a specific past failure or a hard external constraint" (Osmani, 2026). Concretely:

- **Every line traces to a specific failure or a hard constraint.** "Use `uv`, not `pip`" earns its place because an agent once used `pip` and broke the lockfile. A line that traces to nothing is a line the model learns to ignore.
- **Keep it short**: tens of lines, not hundreds. Osmani reports that HumanLayer keeps its file under 60 lines (Osmani, 2026; reported). A file that will not fit on a page is a manual, and a model reads a manual the way people do: not carefully.
- **Prefer rules with teeth.** "Never skip tests" is stronger when a hook enforces it; a rule that lives only in the file drifts (the *silent drift* failure mode of [post 05](../05-agent-failure-modes/index.md)).

### What a followable rule looks like

"Earn each line" governs *whether* a line exists, not how to write one, and badly written rules are ignored as reliably as unearned ones. `ctx-014` gives six rules for writing rules, and three do most of the work in a memory file:

- **Say what to do, not only what to avoid.** "Don't use pip" leaves the agent to guess the alternative, and it will guess something. "Use `uv add`; the lockfile is authoritative" is a rule with a destination.
- **One concept per line.** A line that bundles the package manager, the test command and the commit convention gets partially followed, and nobody can tell which third landed.
- **Be specific enough to check.** "Write good tests" cannot be enforced, reviewed or violated in any detectable way. "Every new module needs a test file before the change is proposed for review" can be all three.

The test for a line is whether a hook could be written for it. If nothing could deterministically catch a violation, the line is advice rather than a rule, and advice belongs in a skill or document the model loads only when the task calls for it ([post 07](../07-skills-mcp-runtime/index.md)), not in the file it reads on every task.

### The same file, before and after

Here is one project's memory file in two states (the issue numbers and dates are illustrative). First, the style-guide shape:

```markdown
# Project rules
- Write clean, idiomatic code.
- Prefer good test coverage.
- Use uv, not pip, and run the typechecker before committing, and keep commits atomic.
- Don't break the build.
```

And the ratcheted shape:

```markdown
# Project rules
- Use `uv add` to add a dependency; the lockfile is authoritative. [#412, 2026-05-02]
- Every new module ships with a test file. [#377, 2026-05-19]
- Run `mypy src/` before committing; a failing typecheck blocks the commit. [#431, 2026-06-01]
- Never comment out tests; delete them or fix them. [#455, 2026-06-08]
```

Every line moves for a reason. "Write clean, idiomatic code" and "Prefer good test coverage" cannot be checked, so they are advice, and they go. The third line bundles three concepts; it splits into two rules with destinations, and the commit-atomicity clause, which nobody could trace to a failure, does not survive. "Don't break the build" says only what to avoid. The last line is Osmani's own: it opens with "never" but names the destination. Each surviving line carries the issue and date that motivated it, which pruning will need, and each is something a pre-commit hook could detect.

---

## 4. The ratchet: one failure, three constraints

This practice turns a memory file from documentation into a *learning mechanism*. When the agent fails, the instance is fixed and then **the failure is converted into durable constraints so that it cannot recur.** Osmani's section heading names it, "The ratchet: every mistake becomes a rule", and his worked example is a pull request (PR) with a commented-out test, merged by accident: "The next version of my `AGENTS.md` says 'never comment out tests; delete them or fix them.' The next version of my pre-commit hook greps for `.skip(` and `xit(` in the diff. The next version of my reviewer subagent flags commented-out tests as a blocker" (Osmani, 2026). Generalised, that example is three teeth, and this series treats the triple as the unit, as the figure at the top of the post draws it:

1. **A memory-file line**: the model reads it every session and *usually* complies.
2. **A hook**: deterministic enforcement that blocks the mistake even when the model forgets ([post 13](../13-hooks-enforcement/index.md)).
3. **A reviewer check**: a reviewer or evaluator that flags it if it slips past the first two ([post 12](../12-planner-generator-evaluator/index.md)).

Three independent layers from one failure: the model's goodwill, a deterministic gate, and an independent check. A failure has to defeat all three to recur. Not every failure earns all three, which the next section works out.

In code, the first two teeth are a few lines. The helper writes the proposed rule to a staging file, not the live memory file, because an agent should not write its own standing instructions unreviewed (the section "A ratchet only climbs if the steps are real").

```python
def propose_rule(cwd: str | Path, rule: str, why: str, check: str) -> None:
    """Turn a failure into two durable constraints: a memory-file line the model
    will read, and an enforcement check that catches a regression deterministically.

    The rule lands in a staging file; a person moves accepted lines into AGENTS.md.
    ``why`` is the provenance: the failure it came from, with a date or issue id.
    """
    proposed = Path(cwd, "AGENTS.proposed.md")
    with proposed.open("a", encoding="utf-8") as f:      # a person reviews this
        f.write(f"- {rule} [{why}]\n")

    enforce = Path(cwd, ".checks", "enforce.txt")
    enforce.parent.mkdir(parents=True, exist_ok=True)
    with enforce.open("a", encoding="utf-8") as f:       # a hook or reviewer reads this
        f.write(f"{check}\n")
```

`snippets/propose_rule.py` runs it on Osmani's example in a temporary directory and prints the staged line, `- Never comment out tests; delete them or fix them. [#455, 2026-06-08]`, the check, and `AGENTS.md unchanged: True`.

### The companion's `Ratchet`

The capstone companion, [`code/26-coding-agent/`](../../code/26-coding-agent/), ships a runnable ratchet. `Ratchet` in `memory.py` is a list of rules with an optional file path. `learn(rule)` appends a rule and returns `True`, or returns `False` and changes nothing when the identical string is already there; with a path set, it also appends the line to that file. `as_context()` renders the rules under "Learned rules (do not repeat past mistakes):", and the driver, `build()` in `driver.py`, hands that text to the generator on every attempt and every later task, calling `learn()` after each failed attempt with a rule made from the verifier's report.

Three things the class does not do. Its de-duplication is an exact-string match, so two reports that differ by one number make two rules, and nothing detects a contradiction. It writes straight into its file, with no staging step and no reviewer. And it never reads the file back: a harness that wants the rules next session loads them itself, as the snippet below does with `Ratchet(rules=..., path=...)`. The driver's default rule, here `[add] previously failed: add(2, 3) == -1, expected 5`, is a failure record: a rule's provenance without its destination. It is the mechanism, not the discipline, as [post 26](../26-capstone-coding-agent/index.md) says of its own build.

`snippets/ratchet_demo.py` imports the class and the driver unchanged and gives them a scripted generator that writes the buggy code until a rule about the task appears in its context:

```python
def generator(task, feedback, memory):
    """The scripted model: wrong until a rule about this task is in its context."""
    path, _, _, good, bad = TASKS[task.name]
    return {path: good if f"[{task.name}]" in memory else bad}
```

Run twice on the same task, once with the ratchet learning and once with learning switched off, it prints:

```text
Part 1: one task, the same generator, two runs (max_attempts=3)
  run 1, the ratchet learns (learn_after=1)
    attempt 1  fail
    attempt 2  pass
    stop reason: spec_complete; rules learned: 1
  run 2, learning switched off (learn_after=4)
    attempt 1  fail
    attempt 2  fail
    attempt 3  fail
    stop reason: task_failed; rules learned: 0
  the memory file after run 1, AGENTS.rules.md:
    [add] previously failed: add(2, 3) == -1, expected 5
  learn() on the same rule again returns False
```

The fix lands only after the rule exists: with learning on, the second attempt reads the rule and passes; with it off, three attempts make the same mistake and the task fails. The companion's own test, `test_ratchet_learns_from_failure_then_the_fix_lands`, asserts the first run's outcome, not the comparison. Here each bug happens once; a real model only usually complies, which is what the other two teeth are for.

---

## 5. Which teeth a failure earns

Not every failure earns all three teeth, and a harness that reflexively adds all three ends up with a memory file full of rules that apply to one directory. Two questions settle it: **is a violation deterministically detectable**, and **does the rule apply on every task or only on some?**

| Detectable? | Applies to | What the failure earns | Why |
| --- | --- | --- | --- |
| Yes | every task | Memory line **and** hook | The line prevents most violations cheaply; the hook catches the rest. Both are paid for on every task, and both earn it. |
| Yes | some tasks | Hook only, no memory line | A rule for one directory should not be read by every task. The hook is the documentation, and it speaks up exactly when it applies. |
| No | every task | Memory line **and** a reviewer check | Nothing can gate it, so expect drift and put an independent reader behind it ([post 12](../12-planner-generator-evaluator/index.md)). |
| No | some tasks | Neither: a skill or document loaded on demand | This is advice, not a rule. Progressive disclosure keeps it on disk and loads it only when the task matches ([post 07](../07-skills-mcp-runtime/index.md)). |

The second row is where memory files bloat. A rule for the payments directory is a real rule, so it feels as if it belongs in the file; thirty such rules later the file is a manual and the model has stopped reading any of it carefully. The discipline is noticing that "real" and "always relevant" are different properties, and only the second buys a line in a file that every session pays for.

---

## 6. Promotion: from observation to rule

The ratchet says what a rule becomes, not how an observation gets nominated in the first place; skipping that question produces the memory file that grew by automatic append. A lesson lives in one of three tiers, each with its own lifetime and price:

| Tier | Where it lives | Lifetime | What it costs to keep |
| --- | --- | --- | --- |
| Scratchpad | a working file inside the session ([post 08](../08-state-filesystem-git/index.md)) | dies with the session | nothing; read only when the agent chooses to look |
| Handoff file | the structured file a context reset is taken behind ([post 08](../08-state-filesystem-git/index.md)) | survives one reset, then goes stale | one read at the start of the next session |
| Memory file | `AGENTS.md` | permanent, until a person deletes it | every session, every task, indefinitely |

Promotion is the move up a tier, and it is a decision rather than an append. A lesson has to pass three tests:

- **It recurred.** One occurrence is an instance; two is a class. A rule written from a single event is a rule written from a sample of one.
- **It would be expensive to relearn.** A lesson the agent will rediscover in thirty seconds from an error message does not need carrying. One that cost an hour down a wrong path does.
- **It generalises past the task that produced it.** "The invoice service's tests need the clock frozen" is a rule. "Task 218 needed the clock frozen" is a log entry.

The asymmetry sets the default. Promotion is cheap to defer (the lesson stays a tier down and costs nothing until it recurs) and expensive to reverse (a line in the always-loaded file is read by every future session, and is hard to remove with confidence once nobody remembers what it was for). When a lesson sits on the boundary, it stays a tier down. If it matters, it will come back.

---

## 7. A ratchet only climbs if the steps are real

The mechanism has an obvious appeal and one dangerous property: **it is monotonic from the inside.** Nothing in the loop reverses a rule, so a *wrong* rule is exactly as durable as a right one. Rules leave only when a person removes them, deliberately, and the section "When memory becomes clutter" gives the four cases where that is correct.

The wrong rule usually arrives the same way. An agent fails, diagnoses the cause and writes the lesson, and the diagnosis is plausible but wrong. The test failed because of a race condition; the agent concluded that the mock was misconfigured, and now every future session carries a permanent instruction about mocks that addresses nothing. Worse, the real cause is now *harder* to find, because the file asserts an explanation that reads as authoritative to the next session.

Three disciplines keep the ratchet honest.

**A rule needs a reviewed root cause, not a plausible one.** An agent appending to its own memory file unreviewed is the hazard [post 18](../18-long-horizon-ralph/index.md) guards against for the spec: the system rewriting the document that governs it, from its own account of what went wrong. Having the agent *propose* rules and a person accept them costs seconds, and it is the difference between accumulating knowledge and accumulating folklore. `ctx-014` states the same rule for system prompts (every change a diff, every diff a reviewer and a justification), and `ctx-016` asks a confirmation step before a learned rule is written.

**Record why the rule exists.** A line with its reason attached, the failure it came from with a date or an issue number, is a line a future reader can evaluate; `ctx-014` uses the same convention for system-prompt rules. A bare imperative with no provenance can never be safely deleted, because nobody can tell whether it is load-bearing, which is how memory files become permanent and unprunable. Provenance is also what makes pruning possible at all: without it, "remove rules that no longer apply" has no way to identify them, and the file only grows.

**Treat the file as shared mutable state.** Once several agents work one repository ([post 17](../17-parallel-agents-shared-repo/index.md)), three worktrees can each diagnose the same failure and each propose a rule for it, and collapsing contradictions becomes a merge problem. The remedy is the one propose-and-accept already implies: workers append to a staging file, never to the live memory file, and the merge and de-duplication happen once, at review time, by whoever owns the file.

The figure below lays out a rule's whole life.

![Six stages of a rule on one timeline: a failure, the rule proposed to a staging file, a person accepting the root cause, the three teeth enforced, the hook's firing rate watched per rule, and the rule pruned when obsolete or made redundant by a new model, with braces marking earning the rule, the teeth, and watching and pruning, and a provenance note below.](diagrams/02-life-of-a-rule.svg)

*The teeth are one stage of six; earning the rule before it lands and watching it afterwards decide whether the file holds knowledge or folklore.*

---

## 8. Why it is a ratchet: reliability only climbs

The name is precise. A ratchet turns one way and cannot slip back, and neither can an agent whose failures become permanent rules. Part 2 of `snippets/ratchet_demo.py` runs four sessions with the same scripted generator, each adding one new task to the build, once with a memory file that every session reads back into `Ratchet(rules=..., path=...)` at its start and once with a ratchet that starts empty each time. It prints:

```text
Part 2: four sessions, one new task each
  session  tasks  rules read back  failed, with the file  failed, without
        1      1                0                      1                1
        2      2                1                      1                2
        3      3                2                      1                3
        4      4                3                      1                4
  failed attempts over four sessions: 4 with the file, 10 without
```

![Two panels computed by the snippet over four sessions: on the left, failed attempts per session, flat at 1 with the memory file and rising 1, 2, 3, 4 without it; on the right, bars of the rules read back at session start, 0, 1, 2 and 3.](diagrams/03-ratchet-over-time.svg)

*Each failure leaves a rule behind, and the next session starts on the step it left; without the file every session starts at the bottom.*

As the figure shows, with the file each session fails once, on the task it has never seen, and the rules read back climb by one a session. Without it every session re-makes every mistake the earlier ones already paid for: 10 failed attempts against 4. The numbers belong to this toy (one bug per task, one rule fixes it); the shape is the mechanism. [Post 04](../04-harness-beats-model/index.md)'s co-training loop improves the model inside its harness; the ratchet improves an agent with the model held fixed, because its harness accumulates constraints.

That hedge is load-bearing. A rule encodes a gap between what the model does and what the project needs; change the model and some gaps close, the one event that legitimately turns the ratchet backwards. The next section makes that an operational trigger.

---

## 9. When memory becomes clutter

The ratchet only turns forward, but the *file* is not sacred. Left to grow, it becomes long, is read every session, and the model starts skimming it: context rot relocated to the one file that most needs to be read ([post 09](../09-context-management-loop/index.md)). So the ratchet needs a counter-discipline of pruning:

- **Remove rules that no longer apply.** The convention changed; the old line is now noise. Delete it.
- **Collapse contradictions.** Two sessions added rules that conflict. Reconcile them into one.
- **Demote one-offs.** A line that turned out to be situational does not belong in the always-loaded file; it goes back down a tier.
- **Retire rules a better model made redundant.** The source of the ratchet states the removal criterion as plainly as the addition one: "You only add constraints when you've seen a real failure. You only remove them when a capable model has made them redundant." In Anthropic's words, which Osmani quotes, "every component in a harness encodes an assumption about what the model can't do on its own", and "When the model gets better at something, that component becomes load-bearing for nothing and should come out" (Osmani, 2026).

The fourth criterion is the only one that is *scheduled* rather than reactive. The other three depend on somebody noticing; a model upgrade is a discrete, dated event, the natural trigger for a memory-file review. It mirrors [post 04](../04-harness-beats-model/index.md), whose three runs check for a harness gap before a bigger model is bought: after the bigger model arrives, check which workarounds it has made obsolete. A rule that routes around a weakness the current model no longer has is pure cost.

The steady state is a file that *grows on failure and shrinks on obsolescence*. Add with the ratchet; prune with judgement.

---

## 10. Watching a rule after it lands

Pruning needs evidence, and the enforcement tooth supplies it. A rule with a hook behind it produces a signal every time the hook fires, and both extremes mean something:

- **A hook that never fires** is either a rule the memory line is successfully preventing, or a rule for a situation that no longer arises. The hook alone cannot tell those apart; the provenance note says what the rule was for, so someone can check whether that situation still exists.
- **A hook that fires constantly** means the memory line is not working. The rule is being enforced rather than followed, every run pays for the block, and the line is worth rewriting to be clearer.

That is only actionable if the signal is emitted. A blocking hook should write a span or increment a counter tagged with the rule's id ([post 21](../21-observability-traces/index.md)), so that "fires constantly" is a query over a few hundred runs rather than an impression. The firing rate per rule, sorted, *is* the prune list, and the provenance note turns each rate into a decision.

One cost is worth knowing before editing the file. Prompt caching matches an exact prefix, and the memory file renders near the front of that prefix, so editing it mid-run invalidates the cache from that point on: the next call pays the write premium (1.25 times base input on the five-minute tier) instead of a 0.1 times read on everything after the edit (Anthropic, "Prompt caching" documentation and "Pricing", consulted 14 October 2026; [post 23](../23-economics-haas/index.md)). Across sessions the entry has often expired anyway, since a five-minute cache write is valid for five minutes, so this is a *mid-run* cost. [Post 09](../09-context-management-loop/index.md) reaches the same conclusion about compaction. Here it argues for batching rule changes into a deliberate review, which propose-and-accept wanted for a different reason.

---

## 11. Make it run

All three snippets run offline from the series root with the standard library; `ratchet_demo.py` imports the companion's `Ratchet` and `build()` unchanged:

```bash
uv run python posts/10-continual-learning-ratchet/snippets/line_cost.py
uv run python posts/10-continual-learning-ratchet/snippets/propose_rule.py
uv run python posts/10-continual-learning-ratchet/snippets/ratchet_demo.py
```

The first prints the cost of carrying the file, the second stages a rule and its check without touching `AGENTS.md`, and the third prints the two-run comparison and the four sessions. To try the ratchet on a failure from a real agent, write its memory line, its hook and its check with `propose_rule()`, then add the task to `TASKS` in `ratchet_demo.py` with the buggy and the correct version. The companion's eight tests, including the ratchet's two, run from inside `code/26-coding-agent/`:

```bash
uv run --extra dev pytest -q
```

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A rule from a wrong diagnosis.** The agent blames the mock for a race condition and writes the rule itself; every later session carries the instruction, the race keeps failing, and the file now points the next investigation the wrong way.
- **A memory file that grows by append.** Every failed attempt adds a line, as the companion's default does; within weeks the file holds near-duplicates that differ by one number, and the model follows none of them reliably.
- **A rule with no hook behind it.** The line says to run the typechecker; the agent skips it on a busy run, nothing blocks the commit, and the convention drifts exactly as if the rule did not exist.
- **Rules written mid-run.** The harness appends a rule as it goes; every edit breaks the cached prefix, and the next call re-writes the whole conversation at the write premium.

---

## Common pitfalls

1. **Expecting the model to remember.** It cannot; only the harness can. Learning lives in a file, not in the weights.
2. **Fixing the instance without ratcheting it.** The class recurs; convert the failure into the teeth it earns.
3. **A memory file that is a style guide.** Long files are skimmed, not followed; earn every line.
4. **Rules without provenance.** A line that does not say which failure it came from can never be safely deleted, so the file only grows.
5. **Never pruning.** Remove obsolete, contradictory and model-redundant lines, and review the file at every model upgrade.

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (19 April 2026): the ratchet, the commented-out test example, "Pilot's checklist, not style guide", "Earn each line", and the paired criteria for adding and removing constraints.
- Agentic AI Foundation, "AGENTS.md" (agents.md, consulted 14 October 2026): the vendor-neutral memory-file convention, its stewardship, and the tools that read it.
- `ctx-014`, "The system prompt as software": the six rules for writing rules, review like code, and an issue id on every rule.
- `ctx-016`, "Memory systems": episodic, semantic and procedural memory, and why rules written by people belong in the system prompt or `AGENTS.md` rather than a memory store.
- Anthropic, "Prompt caching" documentation and "Pricing" (consulted 14 October 2026): exact-prefix matching, the cache-write and cache-read multipliers, and the Claude Opus 5 rate behind the cost of a line.
- ai-boost, "awesome-harness-engineering" (GitHub, consulted 14 October 2026): the Memory & State primitive, a reading list of memory systems and continual learning for agents.
- This series' companion [`code/26-coding-agent/`](../../code/26-coding-agent/): `Ratchet` with exact-string de-duplication, and the test that shows a fix landing only after the rule exists.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 11 - Verification loops: tests, self-critique, fail-fast](../11-verification-loops/index.md):** Part III opens with verification, a gate on the loop's exit, so the model believing a job is done cannot stand in for it being done.
- **[Post 13 - Hooks and deterministic enforcement: guardrails as code](../13-hooks-enforcement/index.md):** the ratchet's second tooth, turning a memory-file rule into a gate the model cannot bypass.
