# 10 · Continual learning & the ratchet — every mistake becomes a rule

> **TL;DR.** The model does not learn between sessions: its weights are frozen and it remembers nothing. But the *harness* can learn, by writing what it discovers to a file the next session reads. The discipline that makes this powerful is the **ratchet**: every time the agent fails, convert that failure into a durable constraint (a line in a memory file, a hook that enforces it, a reviewer check that catches it). Nothing inside the loop ever reverses a rule, so the agent's reliability climbs session over session: this is the last core primitive, the harness that gets better over time.
>
> **After reading this you will be able to:**
> - Set up a memory file the harness injects into every session, and keep it to a checklist, not a manual.
> - Apply the ratchet, and work out which of its three teeth a given failure actually earns.
> - Promote an observation into a rule deliberately, and prune the file before it becomes the clutter it was meant to prevent.
> - Write rules that can be enforced, and keep the ratchet honest with reviewed root causes and provenance.

![The ratchet mechanism: a failure (the agent shipped a quietly commented-out test) fanning into three durable constraints (a memory-file line, a hook, and a reviewer check, each with what it lands and when it acts), above a table of which of the three teeth a failure actually earns.](diagrams/01-ratchet-mechanism.svg)
*One failure, three independent layers. The model reads the rule, a hook enforces it, a reviewer catches it, so the mistake cannot recur.*

---

## 1. Stateless model, learning harness

The two posts before this one rested on the same fact: the model is stateless ([Post 03](../03-the-agent-loop/index.md)). It does not remember yesterday's session, and it never will within a fixed set of weights. So an agent that "learns from experience" is not learning in the model; it is learning in the *harness*, which writes down what it discovered and re-reads it next time.

[Post 08](../08-state-filesystem-git/index.md) gave the mechanism (files on disk) and [Post 09](../09-context-management-loop/index.md) gave the discipline of keeping the window small. This post uses both for a specific purpose: **accumulating knowledge across tasks and sessions.** Where Post 08's handoff file carried state *within* one long job, the memory file here carries lessons *across* many jobs. In the cognitive-science borrowing the Context Engineering series uses (Post 16), this is *procedural* and *semantic* memory (how the team does things here, and facts about this project) reduced to their runtime essence: a file the harness reads at the start of every session.

---

## 2. The memory file: read every session

The concrete artefact is a **memory file**: `AGENTS.md`, `CLAUDE.md`, or whatever your harness injects into context at the start of each session (Osmani, 2026). `AGENTS.md` is the vendor-neutral form of the convention, stewarded by the Agentic AI Foundation under the Linux Foundation and described by its own specification as "a README for agents"; a code search for the filename returns over 60,000 non-fork repositories, and the specification lists Codex, Jules, Cursor, Aider, VS Code, Devin and GitHub Copilot's Coding Agent among the tools that read it (Agentic AI Foundation, 2026). `CLAUDE.md` is the vendor-specific counterpart for Claude Code. The wider landscape of these files, and how they compose with a system prompt, is Context Engineering, Post 14 §4; what this series adds is the runtime behaviour.

That behaviour is simple and consequential. The harness reads the file at session start and prepends it, ahead of the first user turn, so it is part of the prompt prefix before the conversation has begun. That is what makes it *effectively part of the system prompt* rather than a document the model might go and consult — and it is what puts it in the cheapest and most cache-sensitive position in the window (§10). The file holds the project's conventions and hard-won lessons: the package manager to use, the test command, the patterns to follow, the mistakes not to repeat. Because it is loaded every session, it is the single highest-leverage piece of the *custom* harness ([Post 02](../02-anatomy-of-a-harness/index.md)).

### What a line actually costs

"Every line is paid for on every task" is worth pricing, because the honest number sharpens the argument rather than weakening it. Take a 40-line memory file at roughly 20 tokens a line: about 800 tokens. At a frontier-tier input price of $5 per million tokens, that is $0.004 for one uncached session; a cache read of the same prefix is billed at a tenth of the base rate, so $0.0004 (Anthropic, 2026). At a hundred sessions a day, a whole year of carrying that file costs somewhere between about $15 and $150, depending on how often the prefix is warm.

So the fortieth line is not expensive in money, and any memory-file discipline that is secretly a token budget will not survive contact with that arithmetic. The budget actually being spent is **attention**. A line the model skims dilutes the lines it should have followed and, worse, teaches it that this file contains material it can safely ignore. That is why the rule in the next section is "earn each line" and not "keep it under N tokens".

---

## 3. Earn each line: a checklist, not a manual

The most common way a memory file fails is by growing into a style guide nobody follows. The corrective is a hard discipline: **every line must earn its place, and the file stays a pilot's checklist, not a manual** (Osmani, 2026). Concretely:

- **Every line traces to a specific failure or a hard constraint.** "Use `uv`, not `pip`" earns its place because an agent once used `pip` and broke the lockfile. A line that traces to nothing is a line the model will learn to ignore.
- **Keep it short**: tens of lines, not hundreds. If it will not fit on a page, it is a manual, and the model reads a manual the way people do: not carefully.
- **Prefer rules with teeth.** "Never skip tests" is stronger when a hook enforces it (§4); a rule that lives only in the file drifts (the *silent drift* failure of [Post 05](../05-agent-failure-modes/index.md)).

The parallel to [Post 06](../06-tools-bash-code/index.md)'s tool curation is exact: the fewest lines that cover the space, each pulling its weight. A memory file is a context budget like any other.

### What a followable rule looks like

"Earn its place" governs *whether* a line exists. It says nothing about how to write one, and badly written rules are ignored just as reliably as unearned ones. The sibling series' six rules for rules apply directly here (Context Engineering, Post 14 §3), and three of them do most of the work in a memory file:

- **Say what to do, not only what to avoid.** "Don't use pip" leaves the agent to guess the alternative, and it will guess something. "Use `uv add`; the lockfile is authoritative" is a rule with a destination.
- **One concept per line.** A line that bundles the package manager, the test command, and the commit convention gets partially followed, and you cannot tell which third landed.
- **Be specific enough to check.** "Write good tests" cannot be enforced, reviewed, or violated in any detectable way. "Every new module needs a test file before the change is proposed for review" can be all three.

The test for a line is whether you could write the hook for it. If you cannot imagine what would deterministically catch a violation, the line is advice rather than a rule, and advice belongs in a skill or document the model loads only when the task calls for it ([Post 07](../07-skills-mcp-runtime/index.md)), not in the file it re-reads on every task forever.

### The same file, before and after

Rules about rules are hard to apply in the abstract. Here is one project's memory file in the two states such files are usually found in. First, the style-guide shape:

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
- Delete a failing test or fix it; never skip it. [#455, 2026-06-08]
```

Read the diff against the three tests above and every line moves for a reason. "Write clean, idiomatic code" and "Prefer good test coverage" are not specific enough to check, so no hook could catch a violation: they are advice, and they go. The third bad line bundles three concepts, so it splits into two rules with destinations, and the commit-atomicity clause turned out to be folklore nobody could trace to a failure, so it did not survive the split. "Don't break the build" says only what to avoid. Each surviving line carries the issue and the date that motivated it, which is what §9 will need in order to prune it later, and each of the four is something a pre-commit hook could deterministically detect.

---

## 4. The ratchet: one failure, three constraints

Here is the practice that turns a memory file from documentation into a *learning mechanism*. When the agent fails, do not just fix the immediate problem: **convert the failure into durable constraints so it cannot recur** (Osmani, 2026). Osmani's worked example is an agent that ships a change with a commented-out test: the next version of the memory file says never to comment out tests, the next version of the pre-commit hook greps the diff for the skip markers, and the next version of the reviewer sub-agent flags commented-out tests as a blocker (Osmani, 2026). Generalised, that example is three teeth, and this series treats the triple as the unit:

1. **A memory-file line**: the model reads it every session and *usually* complies.
2. **A hook**: deterministic enforcement that blocks the mistake even when the model forgets ([Post 13](../13-hooks-enforcement/index.md)).
3. **A reviewer check**: a reviewer or evaluator that flags it if it slips through the first two ([Post 12](../12-planner-generator-evaluator/index.md)).

Three independent layers from one failure: the model's goodwill, a deterministic gate, and an independent check. A failure that has to defeat all three is a failure that does not recur. Not every failure earns all three, which is what §5 works out.

In code, the first two teeth are a few lines. Note what the helper does *not* do. It writes the proposed rule to a staging file rather than into the live memory file, because a rule is a standing instruction and §7 argues that an agent should not be writing its own standing instructions unreviewed.

```python
from pathlib import Path

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

The phrasing that stuck is Osmani's: **"every mistake becomes a rule"** (Osmani, 2026). An agent whose harness does this should have each class of bug once, subject to the caveat §7 raises.

The series ships a runnable version of the same idea. `memory.py` in [`code/26-coding-agent/`](../../code/26-coding-agent/) defines a `Ratchet` with two methods: `learn()` appends a rule and reports whether it was new, so a repeated lesson cannot be ratcheted twice (which is half of §9's collapse-contradictions discipline done in code rather than by review), and `as_context()` renders the accumulated rules for injection at the top of the next attempt. Its suite makes the thesis executable rather than asserted: `test_ratchet_learns_from_failure_then_the_fix_lands` drives a generator that emits the bug until a rule about it exists in memory, and the correct code once it does. Run `python -m pytest -q` in that directory to watch it happen.

---

## 5. Which teeth a failure earns

Not every failure earns all three teeth, and a harness that reflexively adds all three ends up with a memory file full of rules that apply to one directory. Two questions settle it: **is a violation deterministically detectable**, and **does the rule apply on every task or only on some of them?**

| Detectable? | Applies to | What the failure earns | Why |
| --- | --- | --- | --- |
| Yes | every task | Memory line **and** hook | The line prevents most violations cheaply; the hook catches the rest. Both are paid for on every task, and both earn it. |
| Yes | some tasks | Hook only, no memory line | A rule relevant to one directory should not be read by every task. The hook is the documentation, and it speaks up exactly when it applies. |
| No | every task | Memory line **and** a reviewer check | Nothing can gate it, so expect drift and put an independent reader behind it ([Post 12](../12-planner-generator-evaluator/index.md)). |
| No | some tasks | Neither: a skill or document loaded on demand | This is advice, not a rule. Progressive disclosure keeps it on disk and loads it only when the task matches ([Post 07](../07-skills-mcp-runtime/index.md)). |

The second row is where memory files bloat. A rule that applies to the payments directory is a real rule, so it feels like it belongs in the file; thirty such rules later the file is a manual and the model has stopped reading any of it carefully. The discipline is noticing that "real" and "always relevant" are different properties, and only the second one buys a line in a file that every session pays for.

---

## 6. Promotion: from observation to rule

Section 4 says what a rule becomes once you have decided it is one. It does not say how an observation gets nominated in the first place, and skipping that question is what produces the memory file that grew by automatic append.

A lesson lives in one of three tiers, each with a different lifetime and a different price:

| Tier | Where it lives | Lifetime | What it costs to keep |
| --- | --- | --- | --- |
| Scratchpad | a working file inside the session ([Post 08](../08-state-filesystem-git/index.md)) | dies with the session | nothing; read only when the agent chooses to look |
| Handoff file | the structured handoff a context reset is taken behind ([Post 08](../08-state-filesystem-git/index.md)) | survives one reset, then goes stale | one read at the start of the next session |
| Memory file | `AGENTS.md` (§2) | permanent, until a person deletes it | every session, every task, indefinitely |

Promotion is the move up a tier, and it is a decision rather than an append. Three tests, all of which a lesson has to pass:

- **It recurred.** One occurrence is an instance; two is a class. A rule written from a single event is a rule written from a sample of one, and §7 covers what usually goes wrong with those.
- **It would be expensive to relearn.** A lesson the agent will rediscover in thirty seconds from an error message does not need carrying. One that cost an hour down a wrong path does.
- **It generalises past the task that produced it.** "The invoice service's tests need the clock frozen" is a rule. "Task 218 needed the clock frozen" is a log entry.

The asymmetry sets the default. Promotion is cheap to defer (the lesson stays a tier down and costs nothing until it recurs) and expensive to reverse (a line in the always-loaded file is read by every future session, and §7 explains why it is hard to remove with confidence once nobody remembers what it was for). When a lesson sits on the boundary, leave it a tier down. If it matters, it will come back.

---

## 7. A ratchet only climbs if the steps are real

![A five-stage lifecycle: a failure, a reviewed root cause, a rule you could write a hook for, the three teeth, and finally what the hook's firing rate tells you later, laid out three stages across the top and two below, with the sequence wrapping from the third down to the fourth.](diagrams/03-life-of-a-rule.svg)
*The hero figure draws the ratchet working. This one draws what a rule has to survive before it becomes permanent, and what tells you afterwards whether it still should be.*

The mechanism has an obvious appeal and one dangerous property: **it is monotonic from the inside.** Nothing in the loop ever reverses a rule, so a *wrong* rule is exactly as durable as a right one. Rules leave only when a person removes them, deliberately, and §9 gives the four cases where that is correct.

The wrong rule usually arrives the same way. An agent fails, diagnoses the cause, and writes the lesson — and the diagnosis is plausible but wrong. The test failed because of a race condition; the agent concluded the mock was misconfigured, and now every future session carries a permanent instruction about mocks that addresses nothing. Worse, the real cause is now *harder* to find, because the file asserts an explanation that reads authoritatively to the next session.

Three disciplines keep the ratchet honest.

**A rule needs a reviewed root cause, not a plausible one.** Letting an agent append to its own memory file unreviewed is the [Post 18](../18-long-horizon-ralph/index.md) spec problem in a different costume: the system writes its own standing instructions from its own account of what went wrong. Having the agent *propose* rules and a person accept them costs seconds and is the difference between accumulating knowledge and accumulating folklore. The sibling series reached the same place for system prompts and states it as a rule: every change is a diff, every diff has a reviewer, every diff has a justification (Context Engineering, Post 14 §3).

**Record why the rule exists.** A line with a one-clause reason attached, the failure it came from with a date or an issue number, is a line a future reader can evaluate; the same convention holds for system-prompt rules (Context Engineering, Post 14 §3). A bare imperative with no provenance can never be safely deleted, because nobody can tell whether it is load-bearing, which is how memory files become permanent and unprunable. That is also what makes §9's pruning possible at all: without provenance, "remove rules that no longer apply" has no way to identify them, and the file only ever grows.

**Treat the file as shared mutable state.** Once several agents work one repository ([Post 17](../17-parallel-agents-shared-repo/index.md)), three worktrees can each diagnose the same underlying failure and each propose a rule for it, and "collapse contradictions" stops being a review problem and becomes a merge problem. The remedy is the one propose-and-accept already implies, for a second and independent reason: workers append to a staging file, never to the live memory file, and the merge and de-duplication happen once, at review time, by whoever owns the file.

Read the figure end to end and the shape of the discipline is clear. The ratchet's teeth (step four) are the part everyone implements; the steps on either side of them, earning the rule and then watching it, are the parts that decide whether the mechanism accumulates knowledge or folklore.

---

## 8. Why it's a ratchet: reliability only climbs

The name is precise. A ratchet turns one way and cannot slip back, and so does an agent whose failures become permanent rules.

![A staircase rising from zero to four rules in force across four dated sessions, each step a rule earned from a failure and tagged with its issue number, against a dashed flat line at zero for the same sessions without a memory file, above a panel listing the four rules the file now holds.](diagrams/02-ratchet-over-time.svg)
*Each failure adds a step; nothing in the loop ever removes one; the staircase only climbs. Without a memory file, every session starts at the bottom.*

This is the mechanism behind the co-training-independent version of "the harness gets better over time" ([Post 04](../04-harness-beats-model/index.md)): even with a *fixed* model, an agent improves session over session because its harness accumulates constraints. The contrast is stark. Without a memory file, every session begins from zero: the agent re-discovers, and re-makes, the same mistakes forever. The ratchet is what converts a stateless model into a system that visibly learns.

The hedge in that sentence is load-bearing. The staircase climbs monotonically only while the model is held fixed, because a rule encodes the gap between what the model does and what the project needs. Change the model and some of those gaps close — the one event that legitimately turns the ratchet backwards. The next section makes that an operational trigger.

---

## 9. When memory becomes clutter

The ratchet only turns forward, but the *file* is not sacred. A memory file, left to grow, undoes its own purpose: it becomes long, is read every session, and the model starts skimming it, which is context rot relocated to the one file you most need read ([Post 09](../09-context-management-loop/index.md)).

So the ratchet needs a counter-discipline of pruning:

- **Remove rules that no longer apply.** The convention changed; the old line is now noise. Delete it.
- **Collapse contradictions.** Two sessions added rules that conflict. Reconcile them into one.
- **Demote one-offs.** A line that turned out to be situational, not a real rule, does not belong in the always-loaded file (§6).
- **Retire rules a better model made redundant.** The source of the ratchet states the removal criterion as plainly as the addition one: you add constraints only when you have seen a real failure, and you remove them only when a capable model has made them redundant, because scaffolding for something the model has since learned to do "becomes load-bearing for nothing and should come out" (Osmani, 2026).

That fourth criterion is the only one that is *scheduled* rather than reactive. The other three depend on somebody noticing; a model upgrade is a discrete, dated event, which makes it the natural trigger for a memory-file review. It also closes a loop back to [Post 04](../04-harness-beats-model/index.md), whose rule is to check whether an underperforming agent has a harness gap before reaching for a bigger model; the mirror-image discipline is to check, after the bigger model arrives, which of your harness workarounds it has just made obsolete. A rule written to route around a weakness the current model no longer has is pure cost.

The steady state is a file that *grows on failure and shrinks on obsolescence*: always the current, minimal set of load-bearing rules. Add with the ratchet; prune with judgement. That balance is what keeps a memory file a checklist a model will actually follow, session after session.

---

## 10. Watching a rule after it lands

Pruning needs evidence, and the enforcement tooth supplies it. A rule with a hook behind it (§4) produces a signal every time it fires, and the two extremes both mean something:

- **A hook that never fires** is either a rule the memory line is successfully preventing, or a rule for a situation that no longer arises. You cannot tell those apart from the hook alone, which is precisely why the provenance note matters: it says what the rule was for, so you can check whether that situation still exists.
- **A hook that fires constantly** means the memory line is not working. The rule is being enforced rather than followed, every run pays for the block, and the line is worth rewriting to be clearer (§3) rather than leaving it as a tripwire.

That is only actionable if the signal is emitted. A blocking hook should write a span or increment a counter tagged with the rule's id, exactly as any other harness component emits one ([Post 21](../21-observability-traces/index.md)), so that "fires constantly" is a query over a few hundred runs rather than an impression. The firing rate per rule, sorted, *is* the prune list — and the provenance note is what turns each rate into a decision.

There is one cost worth knowing about before you edit the file. Prompt caching is an exact prefix match, and the memory file renders near the front of that prefix, so editing it mid-run invalidates everything downstream: the rest of that session re-pays uncached input, plus the write premium to put the new prefix back into cache (Anthropic, "Prompt caching" documentation; [Post 23](../23-economics-haas/index.md)). Across sessions the entry has usually expired anyway, since the default cache lifetime is measured in minutes, so this is specifically a *mid-run* cost. [Post 09](../09-context-management-loop/index.md) reaches the same conclusion about compaction: the move that preserves the prefix is the cheap one. Here it argues for batching rule changes into a deliberate review rather than appending as you go, which §7 wanted for an entirely different reason.

---

## Common pitfalls

- **Letting the agent write its own standing instructions.** A rule from a plausible-but-wrong diagnosis is as permanent as a correct one, and a line with no provenance can never be safely deleted because nobody can tell whether it is load-bearing (§7).
- **A rule you could not write a hook for, or one you could and did not.** If a violation is undetectable, the line is advice and belongs in a skill loaded on demand; if it is detectable and important, back it with a hook, because a line the model can ignore will drift (§3, §5).
- **Expecting the model to remember.** It cannot; only the harness can. Learning lives in a file, not in the weights (§1).
- **A memory file that is a style guide.** Long files are skimmed, not followed. Keep it a checklist; earn every line (§3).
- **Fixing a failure without ratcheting it.** If you only fix the instance, the class recurs. Convert it into a durable constraint (§4).
- **Never pruning.** A memory file that only grows becomes context clutter. Remove obsolete, contradictory and model-redundant lines (§9).
- **Auto-appending everything.** Not every observation is a rule. Promote lessons that recur; leave one-offs in the scratchpad (§6).

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (2026): the ratchet principle, `AGENTS.md`, "earn each line", and the paired criteria for adding and removing constraints.
- Agentic AI Foundation, "AGENTS.md" specification (2026): the vendor-neutral memory-file convention, its stewardship, and the list of agents that read it.
- Context Engineering, Post 14, "The system prompt as software" (2026): the six rules for writing rules, the reviewed-like-code discipline, and a worked file with issue ids on every line.
- Context Engineering, Post 16, "Memory systems" (2026): the memory taxonomy (episodic, semantic, procedural) and why procedural memory belongs in a file rather than a store.
- Anthropic, "Prompt caching" documentation (2025) and the published application programming interface (API) price list (2026): exact-prefix matching, the cached-read and cache-write multipliers, and the per-token rates behind the arithmetic in §2 and §10.
- awesome-harness-engineering (2026): the "Memory & State" section (memory files, continual learning).
- This series' companion code, [`code/26-coding-agent/`](../../code/26-coding-agent/) (2026): a runnable `Ratchet` with de-duplication, and the test that shows a fix landing only after the rule exists.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 11: Verification loops](../11-verification-loops/index.md)**: Part III opens with the machinery behind the ratchet's third tooth, a gate on the loop's exit, so the model believing a job is done cannot stand in for it being done.
- **[Post 13: Hooks & deterministic enforcement](../13-hooks-enforcement/index.md)**: the ratchet's second tooth, turning a memory-file rule into a gate the model cannot bypass.
- **[Post 21: Observability & trace-driven repair](../21-observability-traces/index.md)**: where the firing rates of §10 come from, and how a failing trace becomes a ratcheted fix.
- **[Post 02: The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: with Part II complete, revisit the map; you have now built every component that *feeds* the model.
