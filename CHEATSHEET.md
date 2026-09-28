# Harness Engineering — Cheatsheet

*One page. `Agent = Model + Harness`. The harness is everything that is not the model.*

---

## The agent loop

```
        ┌──────────────────────────────────────────┐
        │                                          │
        ▼                                          │
   ┌─────────┐    ┌──────────┐     ┌──────────┐    │
   │ REASON  │──▶ │   ACT    │──▶ │ OBSERVE  │────┘
   │ (model) │    │ (tool)   │     │ (result) │
   └─────────┘    └──────────┘     └──────────┘
        │
        ▼   stop when ANY fires:
   ① model returns a final answer    ← the intended exit (verify it, Post 11)
   ② hard max-iteration cap          ← infinite-loop backstop
   ③ token / time budget exhausted   ← cost ceiling
   ④ no-progress detection           ← thrashing guard
```

**Most agent bugs are stop-condition bugs, not reasoning bugs.**

---

## The eleven components of a harness

| # | Component | One-line job |
|---|-----------|--------------|
| 1 | **Agent loop** | Drive the model reason→act→observe; decide when to stop. |
| 2 | **Tools / code exec** | The agent's hands — bash and code beat fifty bespoke tools. |
| 3 | **State / filesystem** | Durable memory; git for versioning and rollback. |
| 4 | **Context management** | Compaction, tool-output offloading, resets — fight context rot. |
| 5 | **Memory / continual learning** | Carry knowledge across sessions; the ratchet. |
| 6 | **Verification** | Check each step; fail fast before errors compound. |
| 7 | **Hooks / enforcement** | Deterministic rules the model can't be trusted to keep. |
| 8 | **Permissions / sandbox** | Bound the blast radius; isolate execution. |
| 9 | **Orchestration** | Coordinate multiple agents as units (one level up). |
| 10 | **Long-horizon patterns** | Ralph loops, context bridging, multi-context builds. |
| 11 | **Observability** | Traces per run; see it, then fix the failing component. |

---

## Agent failure modes → the fix

| Failure mode | Symptom | Harness fix |
|--------------|---------|-------------|
| **Victory declaration** | "Done!" — but it isn't | Verification loop (#6) |
| **Context anxiety** | Rushes as window fills | Compaction / reset (#4) |
| **One-shotting** | Attempts everything at once | Planner/generator split (Post 12) |
| **Doom loop** | Repeats, no progress | No-progress stop condition (④) |
| **Silent drift** | Ignores conventions | Memory file + hook (the ratchet) |
| **Destructive action** | `rm -rf`, force-push | Deny-list hook + sandbox (#7, #8) |

*Legend: `#N` = the harness component numbered above · `④` = the loop exit · `Post N` = a later post.*

---

## The ratchet principle

> **Every mistake becomes a rule.** A failure turns into three durable constraints:
> a **memory-file line** (so the model reads it), a **hook** (so it's enforced), and a **reviewer check** (so it's caught). Nothing regresses twice.

---

## Decision tree — which discipline?

```
Is the problem about WHAT THE MODEL SEES in one call?
   └─ yes → CONTEXT ENGINEERING  (the prior series)
Is the problem about HOW THE MODEL RUNS — loop, tools, verify, guardrails?
   └─ yes → HARNESS ENGINEERING  (this series)
Is the problem about COORDINATING MANY AGENTS as units?
   └─ yes → ORCHESTRATION  (Part IV)
```

---

*Start reading at [Post 01 — From context to harness](posts/01-from-context-to-harness/index.md), or jump to the part you need: [I Foundations](posts/01-from-context-to-harness/index.md) · [II Core primitives](posts/06-tools-bash-code/index.md) · [III Control & reliability](posts/11-verification-loops/index.md) · [IV Scale & orchestration](posts/16-multi-agent-orchestration/index.md) · [V Production & builds](posts/21-observability-traces/index.md).*

*Terms in [GLOSSARY.md](GLOSSARY.md). Sources in [REFERENCES.md](REFERENCES.md). The series plan, for contributors, is [HARNESS-PLAN.md](HARNESS-PLAN.md).*
