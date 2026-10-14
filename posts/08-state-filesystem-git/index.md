# 08 - State and the filesystem: durable memory and git as state

> **TL;DR.** The model is stateless, and the window it reads each turn is volatile, expensive and small relative to the work, so a harness keeps its state on disk: plans, offloaded tool output and artefacts in files, the window holding only what the model needs this turn. Under git that state becomes reversible: checkpoint after each verified step and roll back a bad one. One structured handoff file, written atomically, lets the work survive a context reset.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the agent loop and why the harness re-sends the history every turn.
> **Safe to skip?** Skip it if the reader can already say why a tool result that arrives early is paid for on every later turn, write a checkpoint and rollback that survive a failed commit and a stray untracked file, and write a handoff file that cannot tear and that a fresh session checks before trusting.
>
> **After reading, you will be able to:**
>
> - Decide whether a piece of state belongs in the window or on disk by when it is needed, and use the filesystem as scratchpad and inter-step bus.
> - Work out what offloading one tool result saves a run, from its size, the turn it arrives and the iteration cap.
> - Checkpoint after each verified step and roll back a bad one under git, with the commit's return code checked, staging filtered and the clean scoped.
> - Write a handoff file that a fresh session can check and resume from, replace it atomically, and confirm that the write landed.
> - Choose between a flat file, SQLite and an index from the access pattern, the number of writers, partial-write safety and review.

![The agent loop, reason, act and observe, inside the context window, and a durable store on disk beside it: four files and a git history in which a bad step is reset to the last checkpoint. Act writes to disk; observe reads back on demand.](diagrams/01-filesystem-durable-state.svg)

*The window is where the model thinks; disk is where the work lives. The harness moves state between them, and git makes the disk side reversible.*

---

## 1. The window is not where state lives

Where should an agent's state live when the window is volatile, expensive, and small relative to the work? [Post 03](../03-the-agent-loop/index.md) established the fact underneath every agent: the model has no memory between calls, and the only state it sees is what the harness re-sends each turn, a growing list of messages it pays for in full on every call.

That window is not small in absolute terms (`ctx-025` gives frontier sizes). It is small *relative to the work*, and smaller in practice than advertised, because retrieval and reasoning degrade well before the nominal limit: *context rot* ([post 09](../09-context-management-loop/index.md)), measured in the benchmarks `ctx-006` and `ctx-025` report.

Used as the only store, it fills and quality rots, it charges for every token on every later call, and one crash or reset loses the work.

The filesystem inverts all three properties. It is effectively unbounded at agent scale, cheap enough that holding state there is not a budget line, and it persists across turns and sessions (and across crashes, provided the write completed, which a later section takes up). So the operating principle of this post is simple: **the window is for what the model needs to think about *now*; disk is for everything else.** The figure at the top draws that split: the loop inside the window, the store it writes and reads outside it.

State is component 03 of the eleven ([post 02](../02-anatomy-of-a-harness/index.md)), and the runtime face of the *write* strategy of `ctx-008`: when something might be needed later, write it down.

---

## 2. The filesystem as scratchpad and inter-step bus

Three kinds of state belong on disk, and naming them says what to write.

- **Scratchpads and plans.** A `plan.md` or `task.md` that the agent writes early and re-reads as it works keeps its intent stable across a long tool detour. The mechanism is not bookkeeping, it is attention. Manus keeps a `todo.md` and rewrites it step by step: "By constantly rewriting the todo list, Manus is reciting its objectives into the end of the context. This pushes the global plan into the model's recent attention span, avoiding 'lost-in-the-middle' issues and reducing goal misalignment" (Yichao "Peak" Ji, Manus, 18 July 2025). Each rewrite puts the goal back at the end of a window that has filled with tool results, which is why the file is rewritten, not appended.
- **Offloaded tool output.** A tool that returns two thousand lines of log should not dump them into the window. Write them to `scratch/build.log` and return a *pointer*: "wrote 2,000 lines to scratch/build.log; grep it for errors." The rule for a good pointer is that the compression must be **restorable**: "the content of a web page can be dropped from the context as long as the URL is preserved, and a document's contents can be omitted if its path remains available in the sandbox" (Manus, 2025). Drop the content without a handle and it is not offloading, it is forgetting ([post 09](../09-context-management-loop/index.md) covers the mechanics).
- **Artefacts.** The actual product (generated code, a report, `output.json`) lives on disk, not in the transcript. The window holds a reference; the filesystem holds the thing.

Underneath all three sits one framing, which Manus states plainly: "we treat the file system as the ultimate context in Manus: unlimited in size, persistent by nature, and directly operable by the agent itself" (Manus, 2025). On that view the window is not the store at all. It is a small, expensive cache over the store, and the harness decides what to page in.

The filesystem also doubles as the **inter-step bus**: step one writes `parsed.json`, step five reads it, instead of state flowing through an ever-growing prompt. The same mechanism scales to *between agents*: a shared directory is how sub-agents coordinate ([post 16](../16-multi-agent-orchestration/index.md)), and file-based task claiming is how a leaderless swarm coordinates with no orchestrator at all ([post 17](../17-parallel-agents-shared-repo/index.md)). Much of orchestration reduces to "who writes which file."

---

## 3. What moving state to disk is worth

Two thousand lines of build output at 50 characters a line is 100,000 characters, and at the illustrative rule of about four characters to the token that is about **25,000 tokens**. Suppose it is the result of iteration 3 of a run capped at 12. The loop re-sends the whole history on every request ([post 03](../03-the-agent-loop/index.md)), so that one tool result is not read once: it rides on each of the nine requests after the turn it arrived in, 4 to 12. `uv run python posts/08-state-filesystem-git/snippets/offload_cost.py` generates such a log and prices both choices, uncached, at 3 dollars per million input tokens, the Claude Sonnet 4.6 input rate post 03 uses (Anthropic's pricing page, consulted October 2026):

```text
log: 2,000 lines, 100,000 characters, about 25,000 tokens; pointer: 59 characters, about 15 tokens
                        tokens  requests   carried   at $3/M
left in the window      25,000         9   225,000    0.6750
offloaded, pointer          15         9       135    0.0004
ratio: 1,667 to 1
```

By hand: $25{,}000 \times 9 = 225{,}000$ input tokens, 0.675 dollars at 3 dollars per million; the pointer carries $15 \times 9 = 135$. The rate moves with model and vendor (`ctx-005` sets out the pricing), and prompt caching cuts the re-read rate in both columns ([post 23](../23-economics-haas/index.md)), but the ratio does not move: it is the log's size over the pointer's, about 1,700 to 1. The offloaded log also survives a reset, and any line of it is a `grep` away. That is the concrete shape of the rule that a run's cost is its iteration count times its *average* context size ([post 23](../23-economics-haas/index.md)): a token not offloaded early is a token bought again on every later turn.

Two consequences follow. Offloading is an economic move and not only a tidiness one, so it is worth doing automatically rather than when the window is already tight. And the threshold for "big" should be low: a few thousand characters is already worth a pointer, because the multiplier is the number of turns left, not the size.

---

## 4. Git turns state into something reversible

A plain filesystem is durable but not *safe*: an agent that edits ten files and corrupts three has no way back. Put the working directory under **git** and the agent gains the capability that makes unattended running tolerable. Addy Osmani compresses it into one sentence: "Adding Git on top gives you versioning for free, so the agent can track progress, roll back errors, and branch experiments" (Osmani, 19 April 2026). Three capabilities; the pattern below uses the middle one.

The pattern is **checkpoint after each verified step; revert on error.** Commit when a step verifies (tests green, a milestone reached), which presumes something able to decide that the step *is* verified: the subject of [post 11](../11-verification-loops/index.md). A checkpoint taken on the model's own say-so is a checkpoint of a broken tree, and that is victory declaration wearing a commit hash ([post 05](../05-agent-failure-modes/index.md)).

```python
PATHS = ["src/", "tests/"]          # the only paths a checkpoint may stage

def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

def checkpoint(cwd, label: str) -> str:
    """Commit the current state as a point the agent can return to."""
    r = _git("add", "-A", "--", *PATHS, cwd=cwd)  # fails if a path is missing
    if not r.returncode:
        r = _git("commit", "-m", f"checkpoint: {label}", "--allow-empty", cwd=cwd)
    if r.returncode:
        raise RuntimeError(f"checkpoint failed: {r.stderr.strip()}")
    return _git("rev-parse", "HEAD", cwd=cwd).stdout.strip()

def rollback(cwd, ref: str) -> None:
    """Discard tracked changes since `ref`, then drop the debris the step left."""
    for args in (("reset", "--hard", ref), ("clean", "-fd", "--", *PATHS)):
        r = _git(*args, cwd=cwd)
        if r.returncode:
            raise RuntimeError(f"rollback failed: {r.stderr.strip()}")
```

With those two calls the loop can bound its own blast radius: `ref = checkpoint(cwd, "tests green")`, attempt the risky step, and on failure `rollback(cwd, ref)`. `uv run python posts/08-state-filesystem-git/snippets/git_checkpoint.py` does that in a temporary repository (fixed author and dates, so the hashes repeat). The risky step edits a tracked file, creates `src/debris.py` and offloads a log to the ignored `scratch/`, beside a colleague's untracked `notes.md`; then a checkpoint meets a crashed process's index lock:

```text
checkpoint 240d0e4  tests green
risky step: tests red, roll back
HEAD 240d0e4  src/parse.py: return line.split(',')
src/debris.py      removed  untracked, under src/
scratch/build.log  kept     ignored
notes.md           kept     untracked, outside the paths
checkpoint failed: fatal: Unable to create '.git/index.lock': File exists.
rev-parse HEAD still answers 240d0e4: unchecked, the loop would trust the old checkpoint
```

The figure below draws that run. Three details in the code are the difference between a rollback mechanism and a trap.

![Checkpoint 240d0e4 with tests green, a risky step with tests red, and a reset back to 240d0e4; what the rollback did to four paths, src/parse.py restored, src/debris.py removed, scratch/build.log and notes.md kept; and a checkpoint that fails on an index lock while rev-parse HEAD still answers 240d0e4.](diagrams/02-checkpoint-rollback.svg)

*A rollback restores what the step was allowed to touch and nothing else; a checkpoint that fails must say so.*

**Every return code is checked, and a failed checkpoint raises.** `git add` fails when a path is missing, and an unchecked failure lets an empty commit stand in for the work; `git commit` exits non-zero for ordinary reasons: no `user.email` in a fresh container, a pre-commit hook that rejects the change ([post 13](../13-hooks-enforcement/index.md)), an index lock left by a crashed process. Without the check, `checkpoint` still returns a hash, because `rev-parse HEAD` reports the *previous* commit, as the output's last line shows; the loop later rolls back to a state that predates the work it believed it had saved. A checkpoint that fails silently is worse than none, because the loop trusts it. The general rule: verify the effect, do not infer it from the absence of an error. [Post 17](../17-parallel-agents-shared-repo/index.md) meets the same class of bug in its task claim, where even a check afterwards fell short and only an exclusive create held.

**Staging is filtered.** A bare `git add -A` stages everything loose in the tree: the offloaded logs, a developer's `.env`, whatever the build wrote. Two defences apply together: a `.gitignore` covering the scratch space, and a path filter so a checkpoint stages only what the step was allowed to touch. A committed log is a permanent copy of whatever it contained, secrets included, so what a checkpoint may capture is a permissions question ([post 14](../14-permissions-sandboxes/index.md)).

**The clean is scoped.** `git reset --hard` restores tracked files but leaves any untracked file the bad step created. Scoped to the same paths, `git clean -fd` removes only debris where the step could write: `src/debris.py` goes, `notes.md` stays. Unscoped, it deletes *every* untracked file in the tree, a colleague's new source file included, and a local `.env` too unless `.gitignore` lists it. It leaves ignored files alone unless `-x` is added, so `scratch/` survives a rollback, as it should. Safest of all is a worktree the agent owns, where everything untracked is its own debris ([post 17](../17-parallel-agents-shared-repo/index.md)).

Two pieces of hygiene surround the pattern. `checkpoint:` commits are the right granularity for rollback and the wrong one for review, so they live on a branch squashed before it merges. And "checkpoint after each verified step" should not be left to the model's memory: the reliable version is a hook on the post-edit or pre-commit lifecycle point ([post 13](../13-hooks-enforcement/index.md)).

That leaves Osmani's third capability. **Branching turns rollback into speculation.** A branch per attempt keeps two attempts alive and chooses between them after verifying both, for one `git switch -c` each; it is the mechanism underneath the worktree-per-agent design ([post 17](../17-parallel-agents-shared-repo/index.md)).

---

## 5. What shipping harnesses actually checkpoint

Checkpointing is not a proposal. Two shipping tools build it in, and they made opposite choices about what the snapshot is made of.

**Aider commits.** Aider works directly in git: "Whenever aider edits a file, it commits those changes with a descriptive commit message", a message its `--weak-model` writes from the diffs and the chat history, and "`/undo` will undo and discard the last change" (Aider, "Git integration"). Checkpoint after each step and revert on demand, shipped as a default.

**The Claude Agent SDK (software development kit) journals its own edits.** With file checkpointing enabled, "the SDK creates backups of files before modifying them through the Write, Edit, or NotebookEdit tools", and a rewind deletes the files it created and restores the files it modified. The documented limits are the interesting part: changes made through Bash commands are not captured, a subagent's edits are not tracked, and creating, moving, or deleting directories is not undone (Anthropic, "Rewind file changes with checkpointing", Claude Agent SDK documentation, consulted October 2026).

| Mechanism | Covers | Misses | Restore granularity | Standing cost |
|---|---|---|---|---|
| Git commit per verified step | every change in the tracked tree, whatever made it | ignored paths, anything outside the repository | any past commit, on any branch | a commit per step; squash before review |
| Edit journal (pre-edit backups) | files the harness itself wrote | shell edits, subagent edits, directory changes | any checkpoint in this session | near zero; nothing to tidy up |
| No checkpoint | nothing | everything | none; the only undo is another agent turn | zero, until the first bad step |

That contrast is the strongest argument for git as the substrate. An edit journal is precise and cheap, and it leaves no commits to clean up. But an agent whose general-purpose tool is a shell ([post 06](../06-tools-bash-code/index.md)) mutates the tree in ways the journal never observes: a `sed -i`, a code generator, a dependency install. A rollback layer that misses some mutations is partial rollback; git snapshots the whole tree, whatever made the change. The two compose: the journal for instant undo of the harness's own edits, a git checkpoint at each verified step for the tree as a whole.

Anthropic's own long-running harness puts git and a progress file together. Its coding agent was asked "to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file", and "This allowed the model to use git to revert bad code changes and recover working states of the code base" (Justin Young, "Effective harnesses for long-running agents", Anthropic, 26 November 2025). The progress file is the subject of the next section.

---

## 6. Handoff files: state that outlives the window

Some work is bigger than any single context window: building a whole feature across many sessions. Osmani, reporting Anthropic's harness work, describes the escape as "full context resets, where the harness tears the session down and rebuilds it from a compact hand-off file" (Osmani, 2026). The filesystem is what lets the work survive that boundary, through a **handoff artefact**: one structured file that captures the spec, what is done, what is next, and the current state.

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

- **Spec is the goal, not the history.** It says what the work is for, and it does not change across resets. A spec that drifts each session leaves the loop optimising a moving target ([post 18](../18-long-horizon-ralph/index.md)).
- **Next is an executable instruction, not a topic.** "Run `pytest tests/test_rows.py` and fix the two failures" survives a reset. "Continue the parser" does not, because a fresh window has no idea what *continue* referred to.
- **State is checkable.** A branch name, the hash of the last checkpoint, and a test count let the resuming session *verify* the handoff before trusting it. That is what ties git and the handoff together: if the tree does not match the file, either the file is stale or the tree moved on without a verified checkpoint, and the right response is to say so rather than to build on it.
- **The handoff is rewritten, never appended.** Appended, the fresh session's first act is reading a diary instead of a brief.

There is also a timing rule: the file is written by the session whose window is about to be wiped, when it is least reliable. Written **at the checkpoint, before the risky step**, the handoff is a plan rather than a summary after the fact, and what remains if the risky step never returns.

`uv run python posts/08-state-filesystem-git/snippets/handoff.py` runs that whole life in a temporary repository. Session 1 checkpoints after two verified steps of four, writes the handoff, then commits a broken third step on its own say-so and is killed, taking every object it held with it. Session 2 receives only the directory:

```text
session 1: checkpoint 3db0e43 after 2 of 4 steps, handoff written
session 1: committed 050bacd on its own say-so, then killed
session 2: handoff names 3db0e43, HEAD is 050bacd
session 2: tree does not match the handoff; rolled back to 3db0e43
session 2: resumes at step 3, multiline quoted fields
session 2: checkpoint 4a5e5bd, 4 of 4 steps, broken step left in the tree: False
```

The State field caught the unverified commit, and the Next field put the fresh session on step 3 rather than step 1, as the figure below draws.

![Two sessions split by a context reset. Session 1 checkpoints 3db0e43, writes handoff.md, commits 050bacd unverified and is killed. Session 2 reads handoff.md, finds HEAD 050bacd against the named 3db0e43, rolls back, and resumes at step 3. Between them, handoff.md on disk with Spec, Done, Next and State.](diagrams/03-handoff-lifecycle.svg)

*The window is wiped at the reset; the file is not, and its State field lets the next session check the tree before trusting it.*

The pattern generalises well past coding. Anthropic describes structured note-taking: "Structured note-taking, or agentic memory, is a technique where the agent regularly writes notes persisted to memory outside of the context window", and of its agent playing Pokémon, "After context resets, the agent reads its own notes and continues multi-hour training sequences or dungeon explorations" (Anthropic, "Effective context engineering for AI agents", 29 September 2025). The handoff file is that habit given a fixed shape and a fixed location.

A long-horizon loop then becomes: read the handoff into a *fresh* window, do a chunk of work, rewrite the handoff, reset. The file is the source of truth; the window is disposable. This is the mechanism behind **Ralph loops** ([post 18](../18-long-horizon-ralph/index.md)) and the deliberate **context reset** of [post 09](../09-context-management-loop/index.md).

---

## 7. Writing to disk is not the same as having written

`handoff.md` is now the single point of failure for the entire long-horizon scheme, which makes it worth asking what happens when a process dies mid-write. The obvious implementation, `Path("handoff.md").write_text(...)`, truncates the file to zero length and then writes the new content. Interrupt it between those steps (a crash, a kill signal, a full volume) and what survives is half a file, which the next session resumes from as though it were the truth.

The fix costs a few lines: write to a temporary file in the same directory, then rename it over the target. POSIX (the Portable Operating System Interface standard) requires a rename to be atomic, so that a reader sees the whole old file or the whole new one and never a torn half (IEEE and The Open Group, 2018); Python's `os.replace` is that rename, and it replaces an existing target on Windows as well. Then read the file back, because the effect is what matters, not the absence of an error.

```python
def write_atomic(path: Path, text: str) -> None:
    """Replace `path` in one step, so a reader never sees a half-written file."""
    tmp = path.with_suffix(path.suffix + ".tmp")   # same directory, same filesystem
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)                          # atomic within one filesystem
    if path.read_text(encoding="utf-8") != text:   # confirm the effect, do not infer it
        raise OSError(f"{path} does not hold what was written")

def write_handoff(cwd, *, spec, done, next_up, state) -> None:
    write_atomic(Path(cwd, "handoff.md"),
                 f"# Handoff\n\n## Spec\n{spec}\n\n## Done\n{done}\n\n"
                 f"## Next\n{next_up}\n\n## State\n{state}\n")

def read_handoff(cwd):
    """The handoff, or None when there is none: the caller must tell those apart."""
    path = Path(cwd, "handoff.md")
    return path.read_text(encoding="utf-8") if path.exists() else None
```

The last part of `handoff.py` kills a rewrite of a 60-character handoff half-way, once with a plain write and once between the two steps of the atomic one:

```text
plain write killed:  30 of 60 characters, a torn file
atomic write killed: 60 of 60 characters, the old file whole: True
```

Three details in that code earn their place. The temporary file is created in the *same directory* as its target, because the rename is only atomic within a single filesystem, and the system temporary directory can be a different one. The read-back confirms that the file holds the text; it does not prove the text would survive a power cut, which needs `os.fsync` as well and is left out of this sketch. And `read_handoff` returns `None` rather than `""` for a missing file, so a resuming loop can distinguish "there is no handoff, start fresh deliberately" from "the handoff is empty, something went wrong".

[Post 17](../17-parallel-agents-shared-repo/index.md) leans on the same rename guarantee when it moves a claimed task file. Any file the loop rewrites in place wants it: `handoff.md`, `plan.md`, `todo.md`, a task-board entry.

---

## 8. Flat file, database, or index

Not all state wants to be a Markdown file. Access pattern, not size, decides, and four questions settle it. `ctx-025` resolves the structurally identical question, whether to load a corpus into the window or retrieve from it, with the same kind of explicit test.

1. **Is it read whole, or queried?** A plan, a handoff, a config file: read whole. "Find the three past tickets most like this one", or "look up the record for order 4471": queried. Whole reads want a file; queries want an index.
2. **Does more than one writer touch it?** One agent rewriting its own plan is safe. Two agents appending to a shared log can interleave their lines, and two that read, change and rewrite it lose each other's writes.
3. **Must it survive a partial write?** If a torn file would break the run, the state needs either the atomic rename above or a store with real transactions.
4. **Does a human need to diff it in review?** Handoffs, plans and specs get read by people and reviewed in pull requests, and a binary store is opaque there.

| | Flat file (`plan.md`, `handoff.md`) | SQLite (one file, transactions) | Index or vector store |
|---|---|---|---|
| Access pattern | read whole | queried over structured rows | queried by similarity |
| Concurrent writers | one; more needs one file per writer | many, serialised by the database | many |
| Partial-write safety | needs the atomic rename | transactional | the service's own guarantee |
| Diffable by a human in review | yes, under git | no, though a text dump is | no |
| Dependency | none | one embedded library | a service to run and keep in sync |
| Reach for it when | most harness state: plans, handoffs, artefacts | queries and counts over many records, still in one file | retrieval over a corpus too large to read whole |

Plans, handoffs and artefacts all land in the first column, and the bias should stay there: a flat file is inspectable, diffable under git, and free of a dependency. The rung easiest to overlook is the middle one: SQLite is still a single file, and adds real queries and atomic transactions, a long way short of a vector database. The third column is the province of retrieval-augmented generation (RAG) and memory systems, covered in `ctx-011` (RAG) and `ctx-016` (memory systems).

Where the flat file genuinely loses is question two, concurrency, and even there this series' answer is not a database: [post 17](../17-parallel-agents-shared-repo/index.md) gives each task its own file, claimed with an exclusive create, so no file has two writers.

---

## 9. Where state belongs

![Five places for state side by side: the window, for what is needed this turn and every turn; then, on disk, files for plans, output, artefacts and the handoff, git for checkpoints, SQLite for queried rows, an index for retrieval over a large corpus. Below, the two mirror-image mistakes of placement.](diagrams/04-where-state-belongs.svg)

*The deciding question is timing, then access: this turn and every turn goes in the window; everything else goes on disk, in the store its access pattern picks.*

The figure puts the whole post in one row. What decides the window is neither size nor importance. A one-line rule the model must honour on every turn belongs in the window even though it is tiny; a 40-byte intermediate result nobody reads again this session belongs on disk even though it is smaller still. Size is a proxy, and it produces two mirror-image mistakes:

- **State in the window that should be on disk.** Pasting a 2,000-line log into the transcript, keeping the running plan only in the conversation, carrying artefacts as message text. All of it bloats the window and dies on reset, at the price worked out above. Write it down.
- **State on disk that should be in the window.** The opposite over-correction: writing every trivial fact to a file the model must then re-read, so the agent spends its turns doing filesystem bookkeeping. If the model needs it *this turn and every turn*, it belongs in the prompt, not behind a read.

Two further mistakes look like disk problems and are placement failures in disguise. A working directory the agent edits with no git is durable but not reversible, so a bad step has nowhere to return to. And a `notes.md` the agent appends to forever becomes a 2,000-line read every turn: the ever-growing file is the window problem relocated to disk, which is why files want compaction as much as windows do ([post 09](../09-context-management-loop/index.md)).

State has a *right place*, decided by when it is needed. Put it there, version it, write it atomically, and leave a handoff so nothing important lives only in a window about to be wiped.

---

## 10. Make it run

The three snippets run offline from the series root, with the standard library and `git` on the path; each works in a temporary directory that it deletes:

```bash
uv run python posts/08-state-filesystem-git/snippets/offload_cost.py
uv run python posts/08-state-filesystem-git/snippets/git_checkpoint.py
uv run python posts/08-state-filesystem-git/snippets/handoff.py
```

They print the outputs quoted above. The last two together are this post's exercise: write the handoff for a task in progress, kill the session, start a fresh one that reads only the handoff, confirm it resumes at the right step, and roll back the bad commit. To try a variation, delete the `if r.returncode` check in `checkpoint` and watch the failed checkpoint return the old hash. `rollback` raises on either step too, since a failed `reset --hard` followed by a `clean` leaves the tree half restored.

---

## 11. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **Checkpointing on the model's word.** The commit lands after the agent says "tests pass" rather than after the tests run; the first rollback returns to a tree that is already red, and the run fails the same way again.
- **A pointer to a file that does not outlive the session.** The log goes to a per-session temporary directory wiped at the reset; the next session greps a missing path and re-runs the whole build.
- **The handoff's temporary file on another filesystem.** The `.tmp` is written to the system temporary directory and renamed onto a mounted workspace; on Linux `os.replace` fails with `OSError: [Errno 18] Invalid cross-device link`, and a copy-then-delete fallback is no longer atomic.
- **A scratch directory missing from `.gitignore`.** Every checkpoint commits the offloaded logs; the repository grows with each one, and a secret printed in one log is now in the history.
- **A handoff resumed without its State checked.** The fresh session trusts a Done field the tree no longer matches; it rebuilds work that a rollback discarded, or skips work it believes was finished.

---

## Common pitfalls

1. **Dumping big tool output into the transcript.** Offload it to a file and return a pointer that can fetch it back; the multiplier is every remaining turn.
2. **Running an editing agent without git.** No git means no rollback, which means no safe autonomy.
3. **Trusting a checkpoint that was never confirmed.** A failed commit still leaves `rev-parse HEAD` a hash to return; check the return code, and check what got staged.
4. **Rewriting the handoff in place.** A plain write killed half-way leaves a torn file that the next session resumes from; write a temporary file beside it, rename it over the target, and read it back.
5. **Reaching for a database by default.** Most agent state is read whole; use a store when the query the file cannot answer can be named.
6. **An append-only file that never compacts.** It recreates the context-rot problem on disk; rewrite or prune it.

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (19 April 2026): the filesystem as workspace, git as versioning for free, resets from a hand-off file.
- Yichao "Peak" Ji, "Context Engineering for AI Agents: Lessons from Building Manus" (Manus, 18 July 2025): the file system as context, restorable compression, `todo.md` recitation.
- Anthropic, "Effective context engineering for AI agents" (29 September 2025): structured note-taking across context resets.
- Justin Young, "Effective harnesses for long-running agents" (Anthropic, 26 November 2025): git commits and a progress file as the state a fresh session reads.
- Aider, "Git integration" (2024 to 2026): a shipping tool that commits every edit with a generated message and undoes the last one with `/undo`.
- Anthropic, "Rewind file changes with checkpointing" (Claude Agent SDK documentation, consulted October 2026): edit-journal checkpointing and its limits.
- ai-boost, awesome-harness-engineering (GitHub, 2026): the Memory and State primitive.
- IEEE and The Open Group, "rename" (POSIX, 2018 edition): the atomicity a handoff rewrite rests on.
- `ctx-008`: the *write* strategy, scratchpads, plan files and persistent state.
- `ctx-025`: the four-question test whose shape the flat file, database or index choice borrows.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 09 - Context management inside the loop: compaction, offloading, resets](../09-context-management-loop/index.md):** the runtime moves that keep the window small, using the disk and the handoff file this post set up.
- **[Post 10 - Continual learning and the ratchet: every mistake becomes a rule](../10-continual-learning-ratchet/index.md):** state that persists across tasks, the memory file that turns failures into rules.
