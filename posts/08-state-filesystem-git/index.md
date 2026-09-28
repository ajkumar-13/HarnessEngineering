# 08 · State & the filesystem — durable memory and git as state

> **TL;DR.** The model is stateless, and the window it reads each turn is volatile, expensive, and small relative to the work: smaller in practice than the number on the box, because accuracy falls well before the nominal limit ([Post 03](../03-the-agent-loop/index.md), [Post 09](../09-context-management-loop/index.md)). The filesystem is the opposite (effectively unbounded, durable, and cheap), which makes it the harness's natural extension of memory: a place to write plans, offload big tool outputs, and pass work between steps. Put that filesystem under **git** and the agent's state becomes *versioned and reversible*: it can checkpoint after each verified step and roll back a bad one. And a single structured **handoff file** lets work survive a context reset entirely.
>
> **After reading this you will be able to:**
> - Decide what belongs in the window versus on disk, and why.
> - Use git as the agent's checkpoint/rollback mechanism, not just its version control.
> - Write a handoff file that lets a fresh session resume exactly where the last one stopped.
> - Choose between a flat file and a structured store with a test you can apply, rather than by habit.

![Two tiers. Above: the context window on the left (small, volatile, expensive) and a durable store on the right holding a filesystem of named files with their roles and a git commit chain with the checkpoint and rollback commands, connected by write/read arrows. Below: three cards pricing one offloaded build log, left in the window versus offloaded with a pointer, and the ratio between them.](diagrams/01-filesystem-durable-state.svg)
*The window is where the model thinks; disk is where the work lives. The harness moves state between them, and git makes the disk side reversible.*

---

## 1. The window is not where state lives

[Post 03](../03-the-agent-loop/index.md) established the uncomfortable fact underneath every agent: the model has no memory between calls, and the only state it sees is what the harness re-sends each turn, a growing list of messages it pays for in full on every call.

That window is not small in absolute terms. Frontier models ship with 200,000 tokens and more, and the largest reach into the millions. It is small *relative to the work*, and smaller still in practice than its advertised size, because retrieval accuracy and reasoning quality start falling long before the nominal limit is reached (*context rot*, [Post 09](../09-context-management-loop/index.md); Context Engineering, Posts 06 and 25). Usable capacity, not advertised capacity, is the binding constraint.

Lean on that window as the only store and three things go wrong. It fills, and the model's quality rots. It is costly, because every token in it rides along on every subsequent call. And it is volatile: one crash, one reset, and the work is gone.

The filesystem inverts all three properties. It is effectively unbounded at agent scale, cheap enough that holding state there is not a budget line, and it persists across turns and sessions (and across crashes, provided the write completed, which is the subject of §7). So the operating principle of this post is simple: **the window is for what the model needs to think about *now*; disk is for everything else.** The harness's job is to move state between the two: writing out what is not needed this instant, reading back what is.

State and the filesystem is component three of the eleven ([Post 02](../02-anatomy-of-a-harness/index.md)), and this post is the one that fills it in. It is also the runtime face of the *Write* primitive from the sibling series (Context Engineering, Post 08): when something might be needed later but not now, write it down.

---

## 2. The filesystem as scratchpad and inter-step bus

Three kinds of state belong on disk, and naming them tells you what to write.

- **Scratchpads and plans.** A `plan.md` or `task.md` that the agent writes early and re-reads as it works keeps its intent stable across a long tool detour. The mechanism is not bookkeeping, it is attention. Manus keeps a `todo.md` and rewrites it step by step, and reports that "by constantly rewriting the todo list, Manus is reciting its objectives into the end of the context", which "pushes the global plan into the model's recent attention span, avoiding 'lost-in-the-middle' issues" (Manus, 2025). That is why the file is *rewritten* rather than appended: each rewrite puts the goal back at the end of a window that has since filled with tool results, which is where the model attends best.
- **Offloaded tool output.** A tool that returns two thousand lines of log should not dump them into the window. Write them to `scratch/build.log` and return a *pointer*: "wrote 2,000 lines to scratch/build.log; grep it for errors." The rule that governs a good pointer is that the compression must be **restorable**: "the content of a web page can be dropped from the context as long as the URL is preserved, and a document's contents can be omitted if its path remains available in the sandbox" (Manus, 2025). Drop the content, keep the handle, and nothing has been lost that cannot be fetched back. Drop the content without a handle and it is not offloading, it is forgetting. (The runtime mechanics are [Post 09](../09-context-management-loop/index.md).)
- **Artefacts.** The actual product (generated code, a report, `output.json`) lives on disk, not in the transcript. The window holds a reference; the filesystem holds the thing.

Underneath all three sits one framing, which Manus states plainly: treat "the file system as the ultimate context ... unlimited in size, persistent by nature, and directly operable by the agent itself" (Manus, 2025). On that view the window is not the store at all. It is a small, expensive cache over the store, and the harness decides what to page in.

The filesystem also doubles as the **inter-step bus**: step one writes `parsed.json`, step five reads it. State flows between turns through files instead of through an ever-growing prompt. The same mechanism scales to *between agents*: a shared directory is how sub-agents coordinate ([Post 16](../16-multi-agent-orchestration/index.md) §7), and file-based task claiming is how a leaderless swarm coordinates with no orchestrator at all ([Post 17](../17-parallel-agents-shared-repo/index.md)). Much of orchestration reduces to "who writes which file."

---

## 3. What moving state to disk is worth

The window-versus-disk asymmetry is easy to argue with adjectives and more convincing with arithmetic. Take the build log from §2 and price it.

Two thousand lines of build output at roughly 50 characters a line is about 100,000 characters, and text like that runs near four characters to the token, so call it **25,000 tokens**. Suppose it arrives at iteration three of a twelve-iteration run. The loop re-sends the whole message history every turn ([Post 03](../03-the-agent-loop/index.md)), so that one tool result is not read once: it is read again on each of the nine calls that follow.

| | Left in the window | Offloaded, pointer returned |
|---|---|---|
| Tokens added at iteration 3 | ~25,000 | ~30 |
| Re-read on the 9 later calls | ~225,000 | ~270 |
| Total input tokens for one tool result | **~250,000** | **~300** |
| Cost at a frontier-tier rate near $5 per million input tokens | ~$1.25 | ~$0.0015 |
| Durable cost | none; it dies at the reset | ~100 KB on disk |
| Can the model still see the detail | only by scrolling a rotting window | yes, by `grep` on demand |

The list rate is illustrative and moves with model and vendor (Context Engineering, Post 25), but the ratio does not: offloading this one result is roughly an **800-fold** reduction in what the run pays to carry it, and the information is still there. That is the concrete shape of the rule that a run's cost is its iteration count times its *average* context size ([Post 23](../23-economics-haas/index.md)): a token you fail to offload early is a token you buy again on every later turn, and the later turns are the expensive ones.

Two consequences follow. Offloading is an economic move and not only a tidiness one, so it is worth doing automatically rather than when the window is already tight. And the threshold for "big" should be low: a few thousand characters is already worth a pointer, because the multiplier is the iteration count, not the size.

---

## 4. Git turns state into something reversible

A plain filesystem is durable but not *safe*: an agent that edits ten files and corrupts three has no way back. Put the working directory under **git** and the agent gains the capability that makes unattended running tolerable. Osmani compresses the whole of it into one sentence: "adding Git on top gives you versioning for free, so the agent can track progress, roll back errors, and branch experiments" (Osmani, 2026). Three capabilities, and most harnesses use only the middle one.

The pattern is **checkpoint after each verified step; revert on error.** Commit when a step verifies (tests green, a milestone reached), which presumes something able to decide that the step *is* verified: the subject of [Post 11](../11-verification-loops/index.md). A checkpoint taken on the model's own say-so is a checkpoint of a broken tree, and that is victory declaration wearing a commit hash ([Post 05](../05-agent-failure-modes/index.md)).

```python
import subprocess

PATHS = ["src/", "tests/"]          # the only paths a checkpoint may stage

def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

def checkpoint(cwd, label: str) -> str:
    """Commit the current state as a point the agent can return to."""
    _git("add", "-A", "--", *PATHS, cwd=cwd)
    r = _git("commit", "-m", f"checkpoint: {label}", "--allow-empty", cwd=cwd)
    if r.returncode:
        raise RuntimeError(f"checkpoint failed: {r.stderr.strip()}")
    return _git("rev-parse", "HEAD", cwd=cwd).stdout.strip()

def rollback(cwd, ref: str) -> None:
    """Discard tracked changes since `ref`, then drop the debris the step left."""
    _git("reset", "--hard", ref, cwd=cwd)
    _git("clean", "-fd", "--", *PATHS, cwd=cwd)
```

With those two calls the loop can bound its own blast radius: `ref = checkpoint(cwd, "tests green")`, attempt the risky step, and on failure `rollback(cwd, ref)`. Three details in that snippet are the difference between a rollback mechanism and a trap.

**The return code is checked, and a failed checkpoint raises.** `git commit` exits non-zero for ordinary reasons: no `user.email` configured in a fresh container, a pre-commit hook that rejects the change ([Post 13](../13-hooks-enforcement/index.md)), an index lock left behind by a crashed process. Without the check, `checkpoint` still returns a hash, because `rev-parse HEAD` cheerfully reports the *previous* commit. The loop then does exactly what it was told: attempt the risky step, fail, and roll back to a state that predates the work it believed it had saved. A checkpoint that fails silently is worse than no checkpoint at all, because the loop now trusts it. The general rule is the one [Post 17](../17-parallel-agents-shared-repo/index.md) §2 draws from the same class of bug: verify the effect, do not infer it from the absence of an error.

**Staging is filtered.** A bare `git add -A` stages everything loose in the tree, including the `scratch/` directory §2 just told you to fill with offloaded logs, a developer's `.env`, and whatever the build wrote. Two defences apply together: a `.gitignore` covering the agent's scratch space, and a path filter so a checkpoint can only stage what the step was allowed to touch. A checkpoint commit of an offloaded log is also a permanent, diffable copy of whatever that log contained, secrets included, so what an agent may write and what a checkpoint may capture are permissions questions ([Post 14](../14-permissions-sandboxes/index.md)).

**The clean is scoped.** `git reset --hard` restores tracked files but leaves behind any untracked file the bad step created, so a genuinely clean revert has to drop those too. Scoped to the same paths, `git clean -fd` removes only debris under the directories the step could touch. Unscoped, it deletes *every* untracked file in the tree, including ones the agent never went near: a colleague's unstaged new source file, a half-written note, a local `.env`. It also leaves ignored files alone unless you add `-x`, which is what you want, since `scratch/` should survive a rollback. Safest of all is a worktree the agent owns exclusively, where "everything untracked here" really is only its own debris ([Post 17](../17-parallel-agents-shared-repo/index.md)).

Two pieces of hygiene surround the pattern. A run of `checkpoint:` commits is the right granularity for rollback and the wrong granularity for review, so they live on a branch that is squashed before it merges. And "checkpoint after each verified step" is a policy the model has to remember to follow, which is the class of rule that should not be left to the model: the reliable version is a hook on the post-edit or pre-commit lifecycle point, not a line in a prompt ([Post 13](../13-hooks-enforcement/index.md)).

That leaves Osmani's third capability, the one most harnesses skip. **Branching turns rollback into speculation.** Checkpoint-and-revert commits to one attempt and undoes it if it fails; a branch per attempt keeps two attempts alive at once and chooses between them after verifying both. It costs one `git switch -c` per attempt, and it is the mechanism underneath the generator/evaluator split ([Post 12](../12-planner-generator-evaluator/index.md)) and the worktree-per-agent design ([Post 17](../17-parallel-agents-shared-repo/index.md)).

---

## 5. What shipping harnesses actually checkpoint

Checkpointing is not a proposal. Two widely used tools ship it, and they made opposite choices about what the snapshot is made of.

**Aider commits.** Aider works directly in git: "whenever aider edits a file, it commits those changes with a descriptive commit message", written by asking a cheaper model to summarise the diff, and `/undo` "will undo and discard the last change" (Aider, "Git integration"). Checkpoint after each step, revert on demand, shipped as a default rather than as a pattern to implement.

**The Claude Agent SDK (software development kit) journals its own edits.** Its file checkpointing "creates backups of files before modifying them through the Write, Edit, or NotebookEdit tools", and a rewind deletes the files it created and restores the files it modified. The documented limits are the interesting part: changes made through Bash commands are not captured, a subagent's edits are not tracked, and creating, moving, or deleting directories is not undone (Anthropic, "Rewind file changes with checkpointing", 2025–26).

| Mechanism | Covers | Misses | Restore granularity | Standing cost |
|---|---|---|---|---|
| Git commit per verified step | every change in the tracked tree, whatever made it | ignored paths, anything outside the repository | any past commit, on any branch | a commit per step; squash before review |
| Edit journal (pre-edit backups) | files the harness itself wrote | shell edits, subagent edits, directory changes | any checkpoint in this session | near zero; nothing to tidy up |
| No checkpoint | nothing | everything | none; the only undo is another agent turn | zero, until the first bad step |

That contrast is the strongest argument for git as the substrate. An edit journal is precise and cheap, and it leaves no commits to clean up. But an agent whose most-used tool is a shell ([Post 06](../06-tools-bash-code/index.md)) mutates the tree in ways the journal never observes: a `sed -i`, a code generator, a dependency install. A rollback layer that does not cover every mutation is partial rollback, and the difference only becomes visible on the run where it matters. Git snapshots the whole tree, so it is indifferent to which tool made the change. The two also compose: keep the journal for instant, fine-grained undo of the harness's own edits, and take a git checkpoint at each verified step for the tree as a whole.

---

## 6. Handoff files: state that outlives the window

Some work is bigger than any single context window: building a whole feature across many sessions. Osmani's name for the escape is a full context reset, "where the harness tears the session down and rebuilds it from a compact hand-off file" (Osmani, 2026). The filesystem is what lets the work survive that boundary, through a **handoff artefact**: one structured file that captures the spec, what is done, what is next, and the current state.

![Three bands: the volatile window with session one writing progress, a context reset, and session two reading and resuming; the persistent disk holding the rule that makes each handoff field usable beside the handoff.md file itself, spec, done, next and state; and below them the timing rule and the atomic-write rule.](diagrams/02-handoff-lifecycle.svg)
*The window is wiped at the reset; the file is not. Each fresh session reads the handoff and resumes exactly where the last one stopped.*

The file is deliberately plain: Markdown that a human can also read and edit.

```markdown
# Handoff

## Spec
Parse the vendor comma-separated export into `rows.json`, one object per line item.

## Done
Header detection and type coercion. 5 of 7 tests green.

## Next
Run `pytest tests/test_rows.py`; fix `test_multiline_quoted` and
`test_negative_amounts`. Leave the header code alone.

## State
branch `feat/csv-parser`, last checkpoint `a41c9f2`, 5/7 tests green.
```

Four fields, and each carries a rule that decides whether a fresh session can actually use the file.

- **Spec is the goal, not the history.** It says what the work is for, and it does not change across resets. A spec that drifts each session leaves the loop optimising a moving target ([Post 18](../18-long-horizon-ralph/index.md)).
- **Next is an executable instruction, not a topic.** "Run `pytest tests/test_rows.py` and fix the two failures" survives a reset. "Continue the parser" does not, because a fresh window has no idea what *continue* referred to.
- **State is checkable.** A branch name, the hash of the last checkpoint from §4, and a test count let the resuming session *verify* the handoff before trusting it. That is what ties the two mechanisms of this post together: if the tree does not match the file, the file is stale, and the right response is to say so rather than to build on it.
- **The handoff is rewritten, never appended.** An appended handoff becomes the ever-growing file of §9, and the fresh session's first act is reading a diary instead of a brief.

There is also a timing rule, and it addresses the failure that kills handoffs in practice: the file is written by the session whose window is about to be wiped, at the moment that session is least reliable. Write the handoff **at the checkpoint, before the risky step**, and it is a plan rather than a post-hoc summary, and it is also what remains to resume from if the risky step never returns.

The pattern generalises well past coding. Anthropic describes "structured note-taking, or agentic memory ... where the agent regularly writes notes persisted to memory outside of the context window", and reports that its Pokémon-playing agent kept objectives and progress in notes so that "after context resets, the agent reads its own notes and continues multi-hour training sequences or dungeon explorations" (Anthropic, 2025). The handoff file is that habit given a fixed shape and a fixed location.

A long-horizon loop then becomes: read the handoff into a *fresh* window, do a chunk of work, rewrite the handoff, reset. The file is the source of truth; the window is disposable. This is the mechanism behind **Ralph loops** and long-horizon execution ([Post 18](../18-long-horizon-ralph/index.md)) and behind the deliberate **context reset** of [Post 09](../09-context-management-loop/index.md). Get the handoff right and an agent can work for hours across dozens of wiped windows without losing the thread.

---

## 7. Writing to disk is not the same as having written

`handoff.md` is now the single point of failure for the entire long-horizon scheme, which makes it worth asking what happens when a process dies mid-write. The obvious implementation, `Path("handoff.md").write_text(...)`, truncates the file to zero length and then writes the new content. Interrupt it between those two steps (a crash, a timeout, a kill signal, a full volume) and what survives is neither the old handoff nor the new one. It is half a file, and the next session resumes from it as though it were the truth.

The fix costs four lines: write to a temporary file in the same directory, then rename it over the target. A rename within one filesystem is atomic, so a reader sees either the whole old file or the whole new one and never a torn half.

```python
import os
from pathlib import Path

def write_atomic(path: Path, text: str) -> None:
    """Replace `path` in one step, so a reader never sees a half-written file."""
    tmp = path.with_suffix(path.suffix + ".tmp")   # same directory, same filesystem
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)                          # atomic within one filesystem

def write_handoff(cwd, *, spec, done, next_up, state) -> None:
    write_atomic(Path(cwd, "handoff.md"),
                 f"# Handoff\n\n## Spec\n{spec}\n\n## Done\n{done}\n\n"
                 f"## Next\n{next_up}\n\n## State\n{state}\n")

def read_handoff(cwd):
    """The handoff, or None when there is none: the caller must tell those apart."""
    path = Path(cwd, "handoff.md")
    return path.read_text(encoding="utf-8") if path.exists() else None
```

Two details in that snippet earn their place. The temporary file is created in the *same directory* as its target, because `os.replace` is only atomic within a single filesystem, and the system temporary directory is frequently a different one. And `read_handoff` returns `None` rather than `""` for a missing file, so a resuming loop can distinguish "there is no handoff, start fresh deliberately" from "the handoff is empty, something went wrong". Starting from nothing by accident is the precise failure the handoff exists to prevent.

This is one primitive doing two jobs across the series. [Post 17](../17-parallel-agents-shared-repo/index.md) §3 uses an exclusive create so that two agents can never claim the same task, and the rename that follows does the same job it does here: it ensures a crash cannot destroy the file the next session depends on. Any file the loop rewrites in place wants it: `handoff.md`, `plan.md`, `todo.md`, a task-board entry, a cached index.

---

## 8. Flat file, database, or index

Not all state wants to be a Markdown file. The choice is decided by access pattern rather than by size, and four questions settle it. The sibling series resolves the structurally identical question, whether to load a corpus into the window or retrieve from it, with the same kind of explicit test (Context Engineering, Post 25).

1. **Is it read whole, or queried?** A plan, a handoff, a config file: read whole. "Find the three past tickets most like this one", or "look up the record for order 4471": queried. Whole reads want a file; queries want an index.
2. **Does more than one writer touch it?** One agent rewriting its own plan is safe. Two agents appending to a shared log will interleave and lose writes.
3. **Must it survive a partial write?** If a torn file would break the run, the state needs either the atomic rename of §7 or a store with real transactions.
4. **Does a human need to diff it in review?** Handoffs, plans and specs get read by people and reviewed in pull requests, and a binary store is opaque there.

| | Flat file (`plan.md`, `handoff.md`) | SQLite (one file, transactions) | Index or vector store |
|---|---|---|---|
| Access pattern | read whole | queried over structured rows | queried by similarity |
| Concurrent writers | one; more needs one file per writer | many, serialised by the database | many |
| Partial-write safety | needs the atomic rename of §7 | transactional | the service's own guarantee |
| Diffable by a human in review | yes, under git | no, though a text dump is | no |
| Dependency | none | one embedded library | a service to run and keep in sync |
| Reach for it when | most harness state: plans, handoffs, artefacts | queries and counts over many records, still in one file | retrieval over a corpus too large to read whole |

Most harness state lands in the first column, and the bias should stay there: a flat file is inspectable, diffable under git, and free of a dependency. The rung most implementers skip is the middle one. SQLite is a single file, so it keeps the one-artefact, git-adjacent property that makes the first column attractive, while adding real queries and atomic transactions; it is where to go when the atomic rename of §7 stops scaling, and it is a long way short of a vector database. The third column is the province of retrieval-augmented generation (RAG) and memory systems, covered end to end in the sibling series (Context Engineering, Post 11 for RAG and Post 16 for memory systems).

The case where the flat file genuinely loses is question two, concurrency, and this series' answer to it is not a database. [Post 17](../17-parallel-agents-shared-repo/index.md) gives each task its own file and claims it with an exclusive create, so there is never more than one writer per file. Concurrency does not imply a database; it implies fewer shared writers.

---

## 9. Where state belongs

![Two columns split by a dashed line: state needed this turn and every turn belongs in the window, listing the task, the last tool result, the always-on rules, and pointers; state needed later or only sometimes belongs on disk, listing the full plan, big tool output, artefacts, and the handoff. Below, two cards name the mirror-image mistakes.](diagrams/03-where-state-belongs.svg)
*The deciding question is not size, it is timing: this turn and every turn, or later and only sometimes.*

The deciding question in the figure is neither size nor importance. A one-line rule the model must honour on every turn belongs in the window even though it is tiny; a 40-byte intermediate result nobody reads again this session belongs on disk even though it is smaller still. Size is a proxy that happens to correlate, and it is the proxy that produces the two mistakes below, which are mirror images of each other:

- **State in the window that should be on disk.** Pasting a 2,000-line log into the transcript, keeping the running plan only in the conversation, carrying artefacts as message text. All of it bloats the window and dies on reset, at the price §3 worked out. Write it down (§2).
- **State on disk that should be in the window.** The opposite over-correction: writing every trivial fact to a file the model must then re-read, so the agent spends its turns doing filesystem bookkeeping. If the model needs it *this turn and every turn*, it belongs in the prompt, not behind a read.

Two further mistakes look like disk problems and are placement failures in disguise. A working directory the agent edits with no git is durable but not reversible, so a bad step has nowhere to return to (§4). And a `notes.md` the agent appends to forever becomes a 2,000-line read every turn: the ever-growing file is the window problem relocated to disk, which is why files want compaction as much as windows do (§2, and [Post 09](../09-context-management-loop/index.md)).

The through-line: state has a *right place*, decided by when it is needed. Put it there, version it, write it atomically, and give the agent a handoff so nothing important lives only in a window that is about to be wiped.

---

## Common pitfalls

- **Treating the window as the only store.** It is small relative to the work, costly, and volatile; disk is none of those. Move state out (§1).
- **Dumping big tool output into the transcript.** Offload it to a file and return a pointer that can fetch it back (§2, §3).
- **Running an editing agent without git.** No git means no rollback, which means no safe autonomy (§4).
- **Trusting a checkpoint that was never confirmed.** A commit that failed still leaves a hash to return, and the rollback target then predates the work. Check the return code, and check what got staged (§4).
- **Losing the thread at a reset.** Without a handoff file, a fresh session starts from nothing; without an atomic write, it may start from half a file (§6, §7).
- **Reaching for a database by default.** Most agent state is read whole; a flat file is simpler, inspectable, and git-diffable. Use a store when you can name the query the file cannot answer (§8).
- **An append-only file that never compacts.** It recreates the context-rot problem on disk. Prune it (§9).

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (2026): the filesystem as the agent's workspace, git as versioning for free (track progress, roll back errors, branch experiments), and full context resets rebuilt from a hand-off file.
- Manus, "Context Engineering for AI Agents: Lessons from Building Manus" (2025): the file system as the ultimate context, restorable compression, and `todo.md` recitation as an attention mechanism.
- Anthropic, "Effective context engineering for AI agents" (2025): structured note-taking, and an agent that resumes multi-hour sequences from its own notes after a context reset.
- Aider, "Git integration" (2024–26): a shipping harness that commits every edit with a generated message and undoes the last one with `/undo`.
- Anthropic, "Rewind file changes with checkpointing" (2025–26): edit-journal checkpointing in the Claude Agent SDK, and the documented limits that argue for git as the substrate.
- awesome-harness-engineering (2026): the "Memory & State" section (filesystem, git, handoff artefacts).
- Context Engineering, Post 08, the *Write* primitive: scratchpads, plan files, and persistent state.
- Context Engineering, Post 25: the four-question test whose shape §8 borrows, and the cost arithmetic behind §3.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 09 — Context management inside the loop](../09-context-management-loop/index.md)**: compaction, offloading, and resets (the runtime moves that keep the window small using the disk this post set up).
- **[Post 10 — Continual learning & the ratchet](../10-continual-learning-ratchet/index.md)**: state that persists *across* tasks (the memory file and the discipline of turning failures into rules).
- **[Post 17 — Parallel agents on a shared repo](../17-parallel-agents-shared-repo/index.md)**: the same file and git primitives doing coordination duty (a worktree per agent, task claiming by exclusive create).
- **[Post 18 — Long-horizon & multi-context execution](../18-long-horizon-ralph/index.md)**: the handoff file at scale (Ralph loops and work that spans dozens of windows).
- **[Post 03 — The agent loop](../03-the-agent-loop/index.md)**: the stateless model, and why the harness must re-send state every turn, that this post makes durable.
