# Harness Engineering cheatsheet

*One page. `Agent = Model + Harness`. The harness is everything that is not the model.*

---

## The agent loop

```
        +------------------------------------------+
        |                                          |
        v                                          |
   +---------+    +----------+    +----------+     |
   | REASON  |--> |   ACT    |--> | OBSERVE  |-----+
   | (model) |    |  (tool)  |    | (result) |
   +---------+    +----------+    +----------+
        |
        v   stop when ANY fires, checked in this order:
   (1) model returns a final answer    <- the intended exit (verify it, post 11)
   (2) hard iteration cap              <- infinite-loop backstop
   (3) token or time budget exhausted  <- cost ceiling
   (4) no progress detected            <- thrashing guard
```

**Most agent bugs are stop-condition bugs, not reasoning bugs.** Exits (2) to (4) are guards: a run that takes one did not finish, and should return where it stopped as well as why (post 19).

---

## The eleven components of a harness

| # | Component | One-line job |
|---|-----------|--------------|
| 01 | **Loop** | Drive the model through reason, act, observe; decide when to stop (post 03). |
| 02 | **Tools** | The agent's hands: bash and code execution are the general-purpose default, and ten focused tools beat fifty overlapping ones (Osmani's argument); skills and MCP extend them at runtime (posts 06, 07). |
| 03 | **State** | Durable memory on the filesystem; git for versioning and rollback (post 08). |
| 04 | **Context management** | Offload, clear, compact, reset: keep the window useful as it fills (post 09). |
| 05 | **Memory** | Carry knowledge across sessions in a memory file; the ratchet writes to it (post 10). |
| 06 | **Verification** | Check each step against ground truth; fail fast before errors compound (posts 11, 12). |
| 07 | **Hooks** | Deterministic enforcement of the rules the model cannot be trusted to keep (post 13). |
| 08 | **Permissions** | Sandbox, declarative rules and approvals: bound the blast radius (posts 14, 15). |
| 09 | **Orchestration** | Coordinate several agents as units, one level up; the default is one agent (posts 16, 17). |
| 10 | **Long-horizon patterns** | Ralph loops, context bridging, work across many fresh contexts (posts 18, 19). |
| 11 | **Observability** | A trace per run; find the failing component, then fix it (post 21). |

The loop is the centre. Components 2 to 5 feed it, 6 to 8 and 11 govern it, and 9 and 10 work at a larger scale.

---

## Agent failure modes and the fix

| Failure mode | Symptom | Harness fix |
|--------------|---------|-------------|
| **Victory declaration** | "Done!", but it is not | A verification gate on the final-answer exit (component 06) |
| **Context anxiety** | Rushes as the window fills | Compaction or a reset (component 04) |
| **One-shotting** | Attempts everything at once | A planner, generator, evaluator split (post 12) |
| **Doom loop** | Repeats, no progress | The no-progress exit, (4) |
| **Silent drift** | Ignores conventions, run after run | A memory-file line backed by a hook (the ratchet) |
| **Destructive action** | `rm -rf`, a force-push, `DROP TABLE` | A deny-list hook and a sandbox (components 07 and 08) |

*Legend: "component NN" is a row of the components table above; (1) to (4) are the loop exits; "post NN" is a post of this series.*

---

## The ratchet principle

> **Every mistake becomes a rule.** A failure turns into three durable constraints: a **memory-file line** (so the model reads it), a **hook** (so it is enforced), and a **reviewer check** (so it is caught). The same class of mistake does not recur.

---

## Which discipline does a problem belong to?

```
Is the problem about WHAT THE MODEL SEES in one call?
   -> yes: CONTEXT ENGINEERING  (the context-engineering series)
Is the problem about HOW THE MODEL RUNS: loop, tools, verification, guardrails?
   -> yes: HARNESS ENGINEERING  (this series)
Is the problem about COORDINATING MANY AGENTS as units?
   -> yes: ORCHESTRATION  (Part IV)
```

---

*Start reading at [post 01, From context to harness: the third era](posts/01-from-context-to-harness/index.md), or jump to the part needed: [I Foundations](posts/01-from-context-to-harness/index.md), [II Core primitives](posts/06-tools-bash-code/index.md), [III Control and reliability](posts/11-verification-loops/index.md), [IV Scale and orchestration](posts/16-multi-agent-orchestration/index.md), [V Production and builds](posts/21-observability-traces/index.md).*

*Terms in the [glossary](GLOSSARY.md), the fixed vocabulary in the [notation guide](notation_guide.md), sources in the [references](REFERENCES.md).*
