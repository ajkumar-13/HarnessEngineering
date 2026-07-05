# 05 · Agent failure modes — victory declaration, context anxiety, doom loops

> **TL;DR.** Autonomous agents do not fail randomly. They fail in a small set of recurring, nameable ways — and each one maps to a specific harness component you can change. This post catalogues six: victory declaration, context anxiety, one-shotting, doom loops, silent drift, and destructive action. Naming the mode turns "my agent is flaky" into a diagnosis, and the diagnosis names the fix. This is the runtime analogue of the Context Engineering series' five *context* failure modes.
>
> **After reading this you will be able to:**
> - Name the six recurring agent failure modes and recognise each from its symptom.
> - Map any observed failure to the single harness component that fixes it.
> - Read a trace to tell which mode you are looking at — and where in the loop it struck.

![A grid of six cards, one per failure mode: victory declaration, context anxiety, one-shotting, doom loop, silent drift, and destructive action — each with its symptom and the harness component that fixes it.](diagrams/01-failure-modes-grid.svg)
*Six modes, six fixes. The value of the taxonomy is that the fix is never "use a bigger model" — it is always a specific component.*

---

## 1. "My agent is flaky" is not a diagnosis

The Context Engineering series made an argument that a vague complaint about an LLM app almost always resolves into one of five named *context* failures — rot, poisoning, distraction, confusion, clash (Context Engineering, Post 06, after Breunig, 2025). Naming them was the first step to fixing them.

Agents that *run* — that loop, call tools, and act unattended — have their own taxonomy, one layer up. These are not failures of what the model *sees* on a single call; they are failures of what the harness *does* across many calls. And like their context-layer cousins, they are a short, finite list. Practitioners who instrument agents keep rediscovering the same handful (Faros AI, 2026). Six cover almost everything you will meet in production.

The payoff is the same as before: each mode maps to **one component to change**. Not a better prompt, not a bigger model — a specific piece of the harness anatomy from [Post 02](../02-anatomy-of-a-harness/index.md). Learn the six, and debugging becomes lookup instead of guesswork.

---

## 2. The six failure modes

Each mode below is stated as *symptom · why it happens · the fix*.

**1 · Victory declaration.** The agent announces the task is complete when it is not — tests still red, the feature half-built, the question half-answered. *Why:* the model is trained to be helpful and to conclude; left to self-assess, it skews positive about its own work. *Fix:* a **verification loop** that checks the work against ground truth (tests, a schema, an independent judge) before the loop is allowed to exit on a "final answer." This is the single most valuable component to add to a naive agent, and it is [Post 11](../11-verification-loops/index.md).

**2 · Context anxiety.** As the context window fills, output quality drops: the agent starts cutting corners, dropping steps, or racing to finish. *Why:* the model behaves as if it is running out of room and compresses its own effort — an emergent "rush" near the window's limit (Faros AI, 2026). *Fix:* active **context management** — compaction, tool-output offloading, and resets — so the working window never approaches the danger zone. That is [Post 09](../09-context-management-loop/index.md).

**3 · One-shotting.** The agent attempts the entire task in a single sweep, producing one large, undocumented change that is hard to review and usually wrong somewhere. *Why:* without structure, the model treats a multi-step task as one step. *Fix:* impose structure — a **planner / generator / evaluator split** that forces decomposition and staged review ([Post 12](../12-planner-generator-evaluator/index.md)). The harness makes the model plan before it acts.

**4 · Doom loop.** The agent repeats the same action — re-running a failing command, re-reading the same file — making no progress while looking busy. *Why:* nothing in a naive loop notices that the state has stopped changing. *Fix:* the **no-progress stop condition** from [Post 03](../03-the-agent-loop/index.md) — detect repeated tool calls or unchanged observations across *N* turns and break. This is exit ④; without it, a doom loop burns the entire budget.

**5 · Silent drift.** The agent quietly ignores your project's conventions — wrong test framework, wrong formatting, a pattern you have corrected before — and keeps doing so. *Why:* the convention was never durably part of what the harness sends, or it was and nothing enforces it. *Fix:* the **ratchet** — put the rule in a memory file the harness injects every session ([Post 10](../10-continual-learning-ratchet/index.md)) *and* back it with a **hook** that enforces it deterministically ([Post 13](../13-hooks-enforcement/index.md)). A convention that lives only in the model's goodwill will drift.

**6 · Destructive action.** The agent runs something dangerous — `rm -rf`, a force-push, a `DROP TABLE`. *Why:* it has real tools and a real blast radius, and judgement alone is not a safety mechanism. *Fix:* do not rely on the model to be careful; use a **deny-list hook** to block the class of command ([Post 13](../13-hooks-enforcement/index.md)) inside a **sandbox** that bounds what any command can reach ([Post 14](../14-permissions-sandboxes/index.md)).

---

## 3. Where they strike: failures cluster in the loop

These six are not scattered randomly through an agent's behaviour. Mapped onto the reason → act → observe loop from [Post 03](../03-the-agent-loop/index.md), they cluster at specific stages — which is exactly why each has a specific fix.

![The agent loop on the left; on the right, the six failure modes grouped by the loop stage where they strike — reason, act, observe, and across turns.](diagrams/02-where-failures-strike.svg)
*Failures have addresses. One-shotting and victory declaration are decisions made at REASON; destructive action happens at ACT; doom loops and context anxiety show up as the loop turns; silent drift spans every turn.*

Reading the map:

- **At REASON** — where the model decides — live the *judgement* failures: it decides it is done when it is not (victory declaration), or decides to do everything at once (one-shotting).
- **At ACT** — where a tool runs — lives the *blast-radius* failure: the dangerous command (destructive action).
- **At OBSERVE / loop-back** — where the loop turns again — live the *iteration* failures: repeating with no change (doom loop), or degrading as the window fills (context anxiety).
- **Across turns** — spanning the whole loop — lives the *consistency* failure: ignoring conventions run after run (silent drift).

This is the deeper reason the taxonomy is useful: a failure's *location in the loop* points at the component that governs that location. The fix follows from the address.

---

## 4. Detecting them from a trace

You cannot fix what you cannot see, so most of this list is only actionable once you have observability ([Post 21](../21-observability-traces/index.md)). Each mode has a characteristic signature in a run's trace:

- **Victory declaration** — the loop exited on a "final answer" (stop ①), but a downstream check (tests, the user) later failed. Signal: *completed runs with failing outcomes.*
- **Context anxiety** — quality metrics fall as a function of turn number or tokens used, not task difficulty. Signal: *late-run answers are worse than early-run ones.*
- **One-shotting** — a single enormous tool call or diff with no intermediate steps. Signal: *one turn does almost everything.*
- **Doom loop** — the same tool-call signature repeats. Signal: *identical `(tool, args)` across consecutive turns* — exactly what stop ④ watches for.
- **Silent drift** — the same reviewer or lint finding recurs across many runs. Signal: *a rule you "fixed" keeps reappearing.*
- **Destructive action** — a tool call matching a dangerous pattern. Signal: *a command on the deny-list was attempted* (ideally blocked before it ran).

A practical debugging habit: when an agent misbehaves, do not ask "why is the model bad?" Ask "which of the six is this, and where in the loop did it strike?" The trace usually answers both.

---

## 5. The triage table

Collapsed to a lookup — the fastest path from symptom to fix:

| You observe… | Failure mode | Change this component |
| ------------ | ------------ | --------------------- |
| "Done!" but it isn't | Victory declaration | Verification loop ([Post 11](../11-verification-loops/index.md)) |
| Quality drops late in a long run | Context anxiety | Context management ([Post 09](../09-context-management-loop/index.md)) |
| One giant undocumented change | One-shotting | Planner / evaluator ([Post 12](../12-planner-generator-evaluator/index.md)) |
| Same action, no change | Doom loop | No-progress stop ([Post 03](../03-the-agent-loop/index.md)) |
| Ignores your conventions | Silent drift | Memory file + hook ([Posts 10](../10-continual-learning-ratchet/index.md) · [13](../13-hooks-enforcement/index.md)) |
| Dangerous command | Destructive action | Deny-list hook + sandbox ([Posts 13](../13-hooks-enforcement/index.md) · [14](../14-permissions-sandboxes/index.md)) |

Keep this table nearby. Most of Part III of the series is one column of it, in depth.

---

## 6. Naming is the first fix

The reason this taxonomy matters is not that it is complete — it is that it is *actionable*. "My agent is flaky" invites you to reach for the one lever that almost never helps: a bigger model. Naming the mode redirects you to the lever that does — a specific, buildable component. The failure has an address; the address has a fix.

The rest of the series builds those fixes. When you reach [Post 11](../11-verification-loops/index.md) (verification) or [Post 13](../13-hooks-enforcement/index.md) (hooks), you will already know exactly which failure you are buying insurance against.

---

## Common pitfalls

- **Reaching for a bigger model first.** Five of the six modes are unaffected by model choice; they are harness gaps (§1, and Post 04). Diagnose before you upgrade.
- **Trusting the model's own "done".** Stopping on a final answer means the model *believes* it is finished, not that it *is*. Victory declaration is the default failure of any agent without a verification loop (§2.1).
- **Treating a doom loop as a reasoning problem.** It is a missing stop condition, not a dumb model. Add exit ④ (§2.4; Post 03).
- **Fixing silent drift with a stern system prompt.** A convention held only by the model's goodwill drifts. Enforce it with a hook (§2.5).
- **Relying on the model to avoid destructive commands.** Judgement is not a safety control. Block the class of command deterministically (§2.6).
- **Debugging without a trace.** Most of these modes are invisible until you can see the run. Observability is a prerequisite, not a nicety (§4).
- **Assuming one fix per agent.** A real agent usually needs three or four of these components, not one.

---

## Further reading

- Faros AI, "Harness Engineering" (2026) — victory declaration, context anxiety, and one-shotting as named production failure modes.
- Martin Fowler, "Humans and Agents in Software Engineering Loops" (2026) — how these failures surface in human–agent workflows and where a human must intervene.
- Drew Breunig, "How Long Contexts Fail" (2025) — the context-layer failure taxonomy this runtime one parallels (via the Context Engineering series, Post 06).
- Addy Osmani, "Agent Harness Engineering" (2026) — the ratchet and hooks as the fix for silent drift and destructive action.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the ACT stage in depth — the surface where destructive action is prevented or permitted.
- **[Post 11 — Verification loops](../11-verification-loops/index.md)**: the fix for victory declaration, the most common failure of all.
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: revisit the loop and its stop conditions — the home of doom loops and context anxiety.
