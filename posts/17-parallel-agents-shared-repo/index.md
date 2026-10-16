# 17 - Parallel agents on a shared repo: worktrees and task-claiming

> **TL;DR.** Many agents can work one codebase in parallel with no central orchestrator: each claims a task by creating a file no other agent can also create, and edits in its own git worktree. The repository is the coordinator, so an agent can join or die without telling anyone. What remains is merge and failure handling: a gate that tests the merged result, a lease that reclaims an abandoned task, and work designed to run twice harmlessly, because a lease cannot tell a crashed agent from a slow one.
>
> **Prerequisites:** [post 16](../16-multi-agent-orchestration/index.md), the topologies, the swarm among them, and when a second agent pays for itself.
> **Safe to skip?** Skip it if the reader can already claim work through the filesystem without a double claim, give each agent its own working copy, and make a task that runs twice harmless.
>
> **After reading, you will be able to:**
>
> - Implement task-claiming by exclusive file creation, and test the exactly-once claim with concurrent threads rather than a single-threaded suite.
> - Add leases, reclaim and quarantine to a task board, releasing the claim token so that a reclaimed task can be claimed again.
> - Isolate each agent's edits in a git worktree, and choose between worktrees, clones and containers by where the agents run and what they execute.
> - Gate every merge on the candidate merged result, and size a swarm against the merge gate's ceiling of T/G agents.
> - Design for at-least-once execution with idempotent tasks, a deduplicating gate and a fencing token, since a lease cannot tell a crashed agent from a slow one.

![A task board of three directories drawn as state, open, claimed and done, beside the .claims token directory. Three agents act on it with no coordinator: ada and linus hold tasks, and grace claims task-6 by an exclusive create of its token and then a rename; any other agent creating that token gets FileExistsError.](diagrams/01-shared-repo-swarm.svg)

*No coordinator: the exclusive create decides who owns a task, and the rename that follows only makes the owner readable.*

---

## 1. The shared-repo pattern

How do many agents work one codebase in parallel with no central orchestrator and no task claimed twice? The swarm topology of [post 16](../16-multi-agent-orchestration/index.md) has a surprising property: it needs no orchestrator at all. A well-documented run of it is Nicholas Carlini's C compiler build, reported on Anthropic's engineering blog: 16 agents running Claude Opus 4.6 worked one repository over nearly 2,000 Claude Code sessions across two weeks, consuming 2 billion input tokens and 140 million output tokens for "a total cost just under $20,000", and produced a 100,000-line compiler in Rust that can build a bootable Linux 6.9 on x86, ARM and RISC-V (on x86 it calls out to GCC, the GNU Compiler Collection, for the 16-bit boot phase), with "a 99% pass rate on most compiler test suites including the GCC torture test suite" (Carlini, Anthropic Engineering, 5 February 2026). The figures are his own account, graded reported. On the topology he is explicit: "I don't use an orchestration agent. Instead, I leave it up to each Claude agent to decide how to act."

The coordination a lead agent would provide is carried instead by the **shared repository**. In that run the mechanism fits in a sentence: an agent takes a lock on a task by writing a text file into `current_tasks/`, and where two agents try to claim the same task, git's synchronisation "forces the second agent to pick a different one" (Carlini, 2026). Each agent runs in its own Docker container, clones a bare upstream repository and pushes back to it; when a session ends, a loop starts a new one in a fresh container.

This works because the two hard problems of a swarm, *who does what* and *who edits what*, both have file-based answers. Agents decide who does what by claiming task files; they avoid editing the same thing by working in separate checkouts. Nothing routes messages and nothing holds global state in memory. The repository is the single source of truth, and that is the whole design. The figure at the top draws the board this post builds, mid-flight.

---

## 2. Task-claiming via files

A task board is a directory of task files that move through states: `open/`, `claimed/`, `done/`. An agent takes work by **claiming** an open task, and the claim has to be safe against two agents reaching for the same one at the same instant.

The mechanism is an **exclusive create**. Claiming a task means creating one path that no other agent can create: `os.open` with `O_CREAT | O_EXCL` succeeds for exactly one caller and raises `FileExistsError` for all the rest. POSIX (the Portable Operating System Interface) specifies it: "The check for the existence of the file and the creation of the file if it does not exist shall be atomic with respect to other threads executing open() naming the same filename in the same directory with O_EXCL and O_CREAT set" (IEEE and The Open Group, 2018); on Windows the same flags map to the `CREATE_NEW` disposition of `CreateFile`, which fails when the file exists. The token is keyed on the task, not on the agent, so two agents reaching for one task contend for one name. Only after the create succeeds does the rename move the task file into `claimed/`, where the owner is readable off its name.

The pattern is older than agents by three decades: Daniel J. Bernstein's maildir spool format, designed for qmail around 1995, has each delivery written into `tmp/` and moved into `new/` with "no locks" (Bernstein, c. 1995). Its safety comes not from the move but from giving every message "a unique name", so no two deliveries contend for one path. A task board needs the same discipline about names, with one contended name per task: the claim.

The core is a loop, excerpted from `task_board.py` in the runnable companion [`code/17-parallel-agents/`](../../code/17-parallel-agents/):

```python
        for name in self.open_tasks():
            src = self.root / "open" / name
            dst = self.root / "claimed" / f"{name}.{agent}"
            token = self.root / _LOCKS / name
            try:
                fd = os.open(token, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                continue  # another agent holds this task; try the next one
            os.close(fd)
            try:
                os.rename(src, dst)
            except OSError:
                # Nobody else can be mid-claim on this task, because nobody else
                # holds the token, so releasing it is safe and keeps the task
                # claimable if it reappears.
                token.unlink(missing_ok=True)
                continue
            return name
        return None
```

`_LOCKS` is the `.claims` directory. No lock server, no database, no coordinator: the exclusive create is the concurrency control. This is the state primitive of [post 08](../08-state-filesystem-git/index.md) doing coordination duty, and it is why the line from post 16 that the repository is the bus is literal.

### Why the rename alone was not enough

An atomic primitive does not by itself buy an exclusive *claim*, and this board took two attempts to learn it. The first version returned the task whenever the rename did not raise. The obvious repair confirmed afterwards that the destination existed and the source was gone. `snippets/jobs/rename_race.py` races both versions the way the companion's test races the board, eight threads behind a barrier draining a 400-task board, and counts the runs in which one task was handed to two agents. On a Windows machine one run printed:

```text
platform: Windows; 400 tasks, 8 threads per run
rename and trust: runs with a double claim: 8 of 8; files in claimed/ per run: [400]
rename and check: runs with a double claim: 5 of 20; files in claimed/ per run: [400]
```

The second count is the instructive one, and it moves: other runs of the same script gave 1 and 11 of 20. In every run exactly four hundred files landed in `claimed/`, so for each doubled task both renames had returned without an error and only one of the two names existed afterwards. Checking narrowed the window without closing it, because each check read a state another rename could still change. The same script under Linux, on an ext4 file system through the Windows Subsystem for Linux (WSL), printed 0 of 8 and 0 of 20, because there the loser's rename found its source gone and raised. Whether a rename alone excludes is a property of the platform and the filesystem. An exclusive create is specified to exclude, on both. **Ask the filesystem for exclusivity; do not check afterwards whether the claim happened to land.**

The failure is also a lesson about tests. Every test that first shipped with this board passed, because every one was single-threaded, and a race cannot occur in a schedule that never interleaves. A concurrency invariant needs a concurrent test: threads, a barrier, a few hundred tasks. The companion ships nine tests, and `test_concurrent_claims_are_exactly_once` is the only one that could have caught it.

### Four details that hold the guarantee

**The board stays on one filesystem.** `rename` across a mount boundary fails, and Python's `shutil.move` falls back to copy-then-delete, with a window in which the task exists in both places or neither. Keep `open/`, `claimed/`, `done/` and `.claims/` on one volume; on a network filesystem the exclusive create is only as good as the protocol and the server make it.

**The claim name carries the owner, and only the claimer may finish.** The destination is `claimed/<task>.<agent>`, so a stale claim can be attributed to the agent that abandoned it, which is what makes a lease sweeper implementable. Completion checks that the claim file belongs to the agent completing it:

```python
    def complete(self, task_id: str, agent: str, result: str = "") -> None:
        """Mark a claimed task done. Only the agent that claimed it may complete it."""
        claim = self.root / "claimed" / f"{task_id}.{agent}"
        if not claim.exists():
            raise ValueError(f"{agent!r} has not claimed {task_id!r}")
        claim.unlink()
        (self.root / "done" / task_id).write_text(result, encoding="utf-8")
```

Without that check, a confused agent can mark another agent's in-flight task done, and the board loses the one invariant it exists to hold.

**Catch the lost race, not every error.** The exclusion is caught narrowly: only `FileExistsError` means another agent holds the task, and any other failure of the create (a permissions error, a full disk, a read-only mount) propagates. The rename's clause is wider than that. Once the token is held, a failed rename is not a lost race but a missing source or a real fault, and the companion releases the token and moves on. A board whose `claimed/` directory has become unwritable then looks like an idle swarm, the hardest failure to diagnose because nothing looks wrong. A production board narrows that clause to `FileNotFoundError` and lets every other error propagate.

**An empty result means safety, not liveness.** The loop takes one snapshot of `open_tasks()` and walks it. An empty return means every task the loop saw was taken by someone else, not that the board is empty, and a driver that treats it as a shutdown signal retires agents while work remains: back off, re-poll, and exit only when the board reads empty across a full poll interval. The snapshot has a second cost: every agent scans the same `sorted()` order, so all contend for the head task. Shuffling the candidate order removes that in one line.

---

## 3. The same primitive at two layers

A claim is a compare-and-set: read a task's state, and take it only if nothing has taken it since. What changes between deployments is not the idea but where the compare-and-set lives, and that is decided by whether the agents share a filesystem.

When they do, the exclusive create is the primitive, and the loop above is the whole implementation. When they do not, the filesystem cannot arbitrate, because there is no single filesystem to arbitrate on. The primitive is then git's own reference update: a push that does not fast-forward the remote branch is rejected, so of two agents pushing a lock file for the same task, the second is refused, pulls, finds the lock taken and picks another. That is the claim protocol of the compiler run, a lock file written into `current_tasks/` and pushed, rather than a local create (Carlini, 2026); the article does not spell out the git mechanics, and the rejected push is how git's synchronisation does it. Each agent's cycle is the local one with a synchronisation step folded in; in Carlini's words, "Claude works on the task, then pulls from upstream, merges changes from other agents, pushes its changes, and removes the lock."

The two versions have different costs and the same guarantee. A create resolves in microseconds and every agent sees the result at once. A push resolves in a network round trip, and an agent learns about other agents' work only when it pulls, so the board is always slightly stale in every worker's view. Which one fits is decided by where the agents run, the subject of the section on choosing the isolation boundary.

---

## 4. Leases, reclaim and quarantine

A claim with no expiry is a lock held by a process that might already be dead: a task neither open nor done, held by an agent that will never return, and the swarm quietly loses a unit of work every time an agent crashes.

The fix is to bound the claim in time. A lock with a time bound is a **lease**, in the sense Gray and Cheriton gave the term: a holder's right expires on its own unless renewed, and in the paper's words "Non-Byzantine failures affect performance, not correctness, with their effect minimized by short leases" (Gray and Cheriton, December 1989). On a task board, a sweeper walks `claimed/`, reads each claim file's modification time, and returns anything older than the lease to `open/`. One detail is easy to miss: `os.rename` keeps a file's modification time, so a fresh claim looks as old as the task that was waiting in `open/`. The claimer stamps the claim with `os.utime` when it takes the task, and stamps it again to renew. Because the claim name carries the owner, the sweeper also knows which agent abandoned the task.

Two states are not enough once a lease exists, because a task that fails every time is reclaimed every time. That is a doom loop ([post 05](../05-agent-failure-modes/index.md)) spread across a swarm rather than trapped in one agent's loop, and it burns the whole fleet's budget on the one task nobody can do. The board needs an attempt counter and a fourth state. The companion ships only the three states in `_STATES`, so the sweeper is an extension of it, in `snippets/leases.py`, not an excerpt from it. Note the token: a task going back to `open/` must have its claim token released, or the exclusive create refuses it forever and the task is quarantined by accident:

```python
def reclaim_stale(root, now):
    """Return expired claims to open/; quarantine the ones that keep failing."""
    reclaimed = []
    for claim in sorted((root / "claimed").iterdir()):
        if EPOCH + now - claim.stat().st_mtime < LEASE_S:
            continue                                  # holder is still inside its lease
        task_id, _, agent = claim.name.rpartition(".")
        tally = root / "attempts" / task_id
        attempts = int(tally.read_text()) + 1 if tally.exists() else 1
        state = "quarantine" if attempts >= MAX_ATTEMPTS else "open"
        (root / state).mkdir(exist_ok=True)
        try:
            os.rename(claim, root / state / task_id)  # one sweeper, so no other sweep moves it
        except FileNotFoundError:
            continue                                  # the holder completed first: nothing to reclaim
        tally.parent.mkdir(exist_ok=True)
        tally.write_text(str(attempts))
        (root / ".claims" / task_id).unlink(missing_ok=True)   # release, or it is unclaimable
        reclaimed.append((task_id, agent, attempts, state))
    return reclaimed
```

`EPOCH` is the zero of the snippet's simulated clock, and `LEASE_S, MAX_ATTEMPTS = 900, 3`. The order matters. The move comes first, so a holder that completed a moment earlier makes the sweep skip the task rather than count an attempt it never lost; the token is released last, once the task is back in `open/`. In the snippet's second scene every holder of `task-9` dies, and the board does what the counter is for:

```text
quarantine:
  t=    0  agent-c  claims task-9, then dies
  t= 1200  sweeper  reclaims task-9 from agent-c: attempt 1, to open/
  t= 1210  agent-d  claims task-9, then dies
  t= 2410  sweeper  reclaims task-9 from agent-d: attempt 2, to open/
  t= 2420  agent-e  claims task-9, then dies
  t= 3620  sweeper  reclaims task-9 from agent-e: attempt 3, to quarantine/
  t= 3630  agent-f  claim returns None: nothing left to take
  quarantine/: ['task-9']
```

Choose the lease from how long the work legitimately takes, with headroom: long enough that a slow but healthy agent is not reclaimed, short enough that a dead agent's task does not sit idle for an afternoon (as illustrative settings, fifteen minutes for a task sized to one verified branch, an hour for one that runs a full build). No value makes the underlying race go away, as the section on at-least-once execution shows.

---

## 5. Git worktrees for edit isolation

Claiming decides *who does what*; it does not stop two agents editing the same files. If every agent worked in one checkout, their edits would clobber each other. On one machine a **git worktree** solves this: each agent gets its own working directory and branch off the one repository.

```bash
git worktree add ../wt-ada    -b agent/ada
git worktree add ../wt-linus  -b agent/linus
git worktree add ../wt-grace  -b agent/grace
```

Each agent edits only inside its own worktree, on its own branch, sharing the repository's history but not its working state. When an agent finishes a task and its work passes verification ([post 11](../11-verification-loops/index.md)), its branch merges back into the mainline through a gate. Isolation during the work, integration after it. The figure below draws one repository with a worktree per agent, the gate the branches return through, and what a worktree does not isolate.

![One repository with one object database and one history above three worktrees, each on its own branch: wt-ada, wt-linus, wt-grace. Every branch returns to main through one merge gate that lands it only if the candidate merge builds and passes its tests. A note says what the worktrees still share: processes, network, environment and credentials.](diagrams/02-worktree-isolation.svg)

*A worktree isolates files and nothing else, and the only way back to main is through the gate.*

Where every agent runs on one machine against one filesystem, four properties of worktrees decide whether this beats giving every agent its own clone.

- **They share one object database.** A worktree costs a working copy, not a copy of the history. Adding the tenth agent is cheap even on a repository with years of commits, and every agent sees merged work the moment it lands, because there is only one history.
- **Git refuses to check out one branch twice.** By default `git worktree add <path> <branch>` refuses when the branch "is already checked out by another worktree", a free correctness guarantee until someone passes `--force`, which the manual says plainly "overrides these safeguards" (Git project, `git-worktree(1)`). The realistic accident is not a developer typing it; it is a harness that retries a failed `git worktree add` with `--force` appended, which turns the guarantee off for every agent at once. Retry with a different branch name, never with `--force`.
- **A worktree is a fresh checkout, not a copy of the environment.** It holds tracked files and nothing else: no `node_modules`, no virtual environment, no build cache, no `.env`. Every worktree needs its own dependency install and gitignored configuration, and that setup, not disk space, is the real marginal cost of the tenth agent. Claude Code's documentation says it directly, "A worktree is a fresh checkout, so initialize your development environment there", and its `.worktreeinclude` file, in `.gitignore` syntax, copies gitignored files such as `.env` into every worktree Claude Code creates (Anthropic, "Run parallel sessions with worktrees", Claude Code documentation, consulted October 2026). The same page names a trap in its own worktrees: where a repository set up Git Large File Storage (LFS) with `git lfs install --local`, a worktree Claude Code creates holds LFS pointer files until `git lfs pull` runs inside it, because Claude Code skips the filter drivers a repository's own configuration defines.
- **Dead agents leave debris that has to be swept.** The clean exit is `git worktree remove`, which removes only clean worktrees unless given `--force`. A harness that locks each worktree while its agent runs, as Claude Code does, can leave the lock behind when the agent is killed, and "To remove a locked worktree, specify --force twice", or run `git worktree unlock` first. `git worktree prune` only clears the records of worktrees whose directories somebody deleted, which git also does on its own over time (`gc.worktreePruneExpire`). What needs a written policy is the branches, which nothing sweeps and a long-running swarm accumulates by the hundred.

The companion stands the isolation up with per-agent directories through `worktree_for()` rather than real worktrees, enough to show that no two agents share a copy while keeping the tests free of git. Its demo drains a seven-task board across three agents taking turns, with no coordinator.

---

## 6. Choosing the isolation boundary

The task board and the worktrees above are a one-machine design; the compiler run of the first section is a many-machine design. Which one a team is building is decided by where its agents run and how much it trusts what they execute, and that choice fixes the claim primitive with it.

| Where the agents run | Isolation | Claim primitive | What it costs | The tell |
|---|---|---|---|---|
| One machine, one filesystem, tasks the team trusts | `git worktree` per agent | Exclusive create of a token, then a rename, within the board directory | Branch and worktree debris to sweep; one dependency install per worktree | Merged work is visible to every agent the instant it lands, because there is one history |
| Many machines, or one machine with containers | Per-agent clone of a bare upstream repository | Push a lock file; git rejects the push that does not fast-forward | A pull and a push on every cycle, so each agent's view of the board is slightly stale | What the 16-agent compiler run did (Carlini, 2026) |
| One machine, but tasks that may be destructive | Container plus a clone inside it | Either; the container boundary is the point | Image upkeep and container start-up per task | Process and network isolation are needed, not just file isolation ([post 14](../14-permissions-sandboxes/index.md)) |

The third row is the one teams skip. A worktree isolates *files* and nothing else: its agent shares the machine's processes, network, environment variables and credentials with every other agent. Where the tasks run code the agents themselves wrote, the blast-radius argument of [post 14](../14-permissions-sandboxes/index.md) applies with full force, and file isolation is not the isolation the design needs.

---

## 7. Merge and conflict handling

Isolation defers the coordination problem to merge time rather than removing it. Several branches all changing one codebase will sometimes conflict, and the swarm needs a policy for it.

**Conflicts scale with overlap, not with branch size.** What governs the conflict rate is how disjoint the *decomposition* is: sixteen tiny branches that all edit the same code generator conflict constantly. The compiler run reports exactly that, "Merge conflicts are frequent, but Claude is smart enough to figure that out" (Carlini, 2026). Frequent conflicts at high agent counts are the normal case, not a sign that something is broken.

**Gate on the merged result, not on the branch.** A branch green on its own is no evidence that the mainline will be green after it lands. Branch A renames `parse_expr` to `parse_expression` and updates all seven of its callers; branch B adds an eighth call to `parse_expr`. Both suites pass. Git sees two disjoint hunks and merges them without a murmur. The mainline no longer builds. This is a **semantic conflict**, and no amount of testing the branches in isolation can see it, because the broken state exists in neither branch. The remedy is to build the candidate merge and run the suite on that, landing only if it is green. The commands, as a gate script would run them:

```bash
git fetch origin main agent/ada
git switch --detach origin/main
git merge --no-ff origin/agent/ada || exit 1   # textual conflict: reject, do not land
pytest -q || exit 1                            # semantic conflict: rejected here, and only here
git push origin HEAD:main                      # fast-forward; lose the race and the gate retries
```

This is solved infrastructure. Graydon Hoare built the bors merge robot for Rust to enforce the not rocket science rule, to "automatically maintain a repository of code that always passes all the tests" (Hoare, graydon2 blog, 2014), and GitHub's merge queue serves the same purpose. Adopting one is cheaper than getting the last line's race right alone.

That is what "serialise the merge, not the work" means. The work runs fully parallel; only the gate is serialised, and it is the only moment in the design when the combined state of every agent's work is verified. A failure or a conflict at the gate sends the task back to `open/` rather than into the mainline, so one agent's mistake is discarded rather than integrated.

---

## 8. Throughput against coordination cost

The reason to run a swarm is throughput. Where a task fans out into many independent pieces (a large migration, a batch of similar fixes), a swarm moves far more work per hour than one agent. One secondary report puts Stripe at "roughly 1,300 AI-generated pull requests every week", "reviewed, merged, and deployed" (MindStudio blog, edited by Luis Chavez-Mattos, 9 April 2026); the article attributes the figure to Stripe without linking a primary source, so it is graded reported. Spread evenly over the 168 hours of a week and landed through one serialised gate, $1{,}300 / 168 = 7.74$ landings an hour leave that gate $60 / 7.74 = 7.75$ minutes per candidate, day and night. That last step is this series' arithmetic, not the source's claim, and it is the economics of the merge gate in one number.

It generalises. Take $N$ agents, each producing a verified branch every $T$ minutes, against a merge gate that costs $G$ minutes of serialised verification. Sustained throughput is $\min(N/T, 1/G)$ tasks per minute, and the gate saturates at $N^* = T/G$ agents; every agent past that queues at the gate and buys nothing but conflict surface. With an illustrative 30-minute task and an 8-minute gate, `snippets/gate_ceiling.py` prints:

| Agents (N) | Branches produced per hour | Gate ceiling per hour | Sustained landings per hour | Gain over the previous row |
|---|---|---|---|---|
| 1 | 2.0 | 7.5 | 2.0 | +2.0 |
| 2 | 4.0 | 7.5 | 4.0 | +2.0 |
| 3 | 6.0 | 7.5 | 6.0 | +2.0 |
| 4 | 8.0 | 7.5 | **7.5** | +1.5 |
| 8 | 16.0 | 7.5 | 7.5 | 0 |
| 16 | 32.0 | 7.5 | 7.5 | 0 |

The numbers are illustrative, but the shape is not: $N^* = 30/8 = 3.75$, so the fifth agent adds throughput for nobody and conflict surface for everyone. Past saturation the fix is a faster or a parallelised gate, never a bigger swarm. Halving $G$ to four minutes doubles the ceiling to 15 an hour and moves saturation out to 7.5 agents; adding twelve more agents at $G = 8$ moves it nowhere. Measure $G$ before sizing $N$.

Throughput is not free in tokens either: every agent is a full context and a full loop, a bill priced in [post 23](../23-economics-haas/index.md); this section prices only the coordination on top of it. The break-even is the same test as the coordination tax of [post 16](../16-multi-agent-orchestration/index.md), now measured in merges and claimed files.

The failure case has a name and a witness. A swarm on work that was not actually parallel is an expensive single agent with extra conflicts, and the compiler run hit precisely that when it turned from the compiler's many independent tests to compiling the Linux kernel, which "is one giant task. Every agent would hit the same bug, fix that bug, and then overwrite each other's changes", so that "Having 16 agents running didn't help because each was stuck solving the same task" (Carlini, 2026). His fix restored independence rather than adding agents: GCC compiled most of the kernel as a known-good oracle and the new compiler a random subset, so different agents chased different bugs. The diagnostic follows. Watch what the branches conflict *with*. Conflicts against the mainline are the ordinary tax of parallel work; branches conflicting with each other, at a rate that climbs as agents are added, mean the decomposition is wrong and no merge policy will rescue it.

---

## 9. At-least-once execution, not exactly-once

The exclusive claim guarantees that two agents never hold a task *at the same moment*. It does not guarantee that a task is worked only once, and the gap between those two statements is where the subtle bugs live.

Take the reclaim of the lease section. An agent claims a task, starts work, and goes quiet: a hung model call, a lost network, a machine that was paused rather than killed. The lease expires, the sweeper reopens the task, another agent claims it and does it. Then the first agent wakes and finishes too. Nothing was violated: each claim was exclusive, and the board behaved exactly as designed. The task simply ran twice. The first scene of `snippets/leases.py` runs that sequence on the companion's board:

```text
at-least-once:
  t=    0  agent-a  claims task-7; lease to t=900
  t=  300  agent-a  renews, then goes quiet; lease to t=1200
  t=  900  sweeper  lease still live, nothing to do
  t= 1200  sweeper  lease expired: task-7 back to open/ (attempt 1)
  t= 1210  agent-b  claims task-7
  t= 1500  agent-b  does the work: settings.toml written
  t= 1500  agent-b  completes: task-7 in done/
  t= 1800  agent-a  wakes, does the work: settings.toml unchanged
  t= 1800  agent-a  completion refused: 'agent-a' has not claimed 'task-7'
  board: {'open': 0, 'claimed': 0, 'done': 1}; settings.toml: 'retries = 3\n'
```

![A timeline in simulated seconds, 0 to 1,800, in three lanes. Agent A claims task-7 at 0, renews at 300 and goes quiet. The sweeper finds the lease live at 900 and expired at 1,200, and reopens the task. Agent B claims it at 1,210, writes settings.toml and completes at 1,500. Agent A wakes at 1,800, finds the file unchanged, and its completion is refused.](diagrams/03-at-least-once.svg)

*Every claim in this run was exclusive and the task still ran twice; idempotent work and the ownership check made the second run harmless.*

From outside, a crashed agent cannot be told from a slow one, which is why every system of this shape settles for **at-least-once execution** and makes the second execution harmless. The timeline above, drawn from that run, shows two of three ways, in rough order of preference:

- **Make the task idempotent.** If the work is "ensure this file matches the spec" rather than "append a line", running it twice is indistinguishable from running it once: agent A's late run found `settings.toml` already right. It is the cheapest fix, and mostly a matter of how tasks are phrased.
- **Let the merge gate deduplicate.** Two branches doing the same task produce the same change; the first merges, and the second becomes an empty diff or a conflict. The gate only has to be allowed to discard a duplicate rather than treat it as a failure.
- **Make the completion a compare-and-set.** The ownership check in `complete()` is exactly this: a finish that refuses unless the agent still holds the claim, which is why agent A's completion was refused. Presented earlier as a guard against confusion, it is the same three lines.

The third is where most designs stop, and it is not sufficient. It protects the board, not the work: agent A's branch still exists, and a check made just before acting can go stale before the action lands. Martin Kleppmann's argument about distributed locks applies directly: "You cannot fix this problem by inserting a check on the lock expiry just before writing back to storage", since the process can be paused between the check and the write (Kleppmann, personal blog, 8 February 2016). The durable version pushes the check down to the resource, using a fencing token, "a number that increases (e.g. incremented by the lock service) every time a client acquires the lock", and a resource "rejecting any writes on which the token has gone backwards". In a shared-repo swarm the resource is the merge gate, and the token is the claim generation: give each reclaim an incrementing attempt number (the sweeper's tally already counts them), carry it on the branch, and have the gate refuse a branch whose number is stale. That converts double *work* into a single *effect* and costs only the loser's tokens.

Tuning the lease does not make the problem go away. A shorter lease reclaims live agents more often; a longer one leaves dead tasks stuck for longer. No setting removes the race; settings only trade its two failure modes. Pick the lease for how long the work takes, and make double execution harmless by design.

---

## 10. Failure isolation across the swarm

A leaderless design has a real reliability advantage: **no single point of failure**. An agent can crash mid-task and the swarm continues, because its unfinished task returns to `open/` on the next sweep; there is no coordinator whose death stops everyone.

At swarm scale that recovery path is not a contingency but the ordinary case, and one line of arithmetic shows why. If each agent fails a given task independently with probability $p$, a round of $N$ parallel tasks contains at least one failure with probability $1 - (1 - p)^N$. At an illustrative $p = 0.05$, a single agent fails one task in twenty, while sixteen agents produce at least one failure in a round $1 - 0.95^{16} = 56.0\%$ of the time, as `snippets/gate_ceiling.py` prints. That is why the reliability story here is reclaim, quarantine and observation rather than any attempt to stop agents failing.

The corresponding risk is the task that no agent can finish, claimed and released and reclaimed forever, which is what the attempt counter and the `quarantine/` state exist to stop: after a small number of failures the task leaves the rotation and waits for a human ([post 15](../15-human-in-the-loop/index.md)) instead of consuming the fleet. And per-agent traces ([post 21](../21-observability-traces/index.md)) are what make a swarm debuggable: a trace that does not carry the agent and task identifiers turns sixteen concurrent stories into one unreadable one.

---

## 11. Make it run

This post's exercise is to reproduce zero double claims over eight threads and four hundred tasks. The companion's nine tests, the threaded one among them, and its demo run from inside `code/17-parallel-agents/`:

```bash
uv run --extra dev pytest -q
uv run python -m parallel_agents
```

The demo prints each agent's tasks and `board: {'open': 0, 'claimed': 0, 'done': 7}`. The four snippets run from the series root with the standard library, importing the companion unchanged where they use it:

```bash
uv run python posts/17-parallel-agents-shared-repo/snippets/claim_race.py
uv run python posts/17-parallel-agents-shared-repo/snippets/jobs/rename_race.py
uv run python posts/17-parallel-agents-shared-repo/snippets/leases.py
uv run python posts/17-parallel-agents-shared-repo/snippets/gate_ceiling.py
```

`claim_race.py` is the exercise. It drains a fresh 400-task board with eight threads released by a barrier, eight times over, and prints:

```text
8 trials, 400 tasks, 8 threads released by a barrier
double claims per trial: [0, 0, 0, 0, 0, 0, 0, 0]
claims per trial:        [400]
board after each trial:  [(('open', 0), ('claimed', 400), ('done', 0))]
every claim file names the agent that was told it won: True
```

then the first trial's claims per agent, which change from run to run; it takes about twelve seconds. `jobs/rename_race.py` races the two rename-only boards quoted earlier in about forty seconds idle (longer on a loaded machine, so the validator leaves it out), and its counts measure the machine it runs on. `leases.py` prints the two timelines quoted above, and `gate_ceiling.py` the throughput table and the failure arithmetic. To try a variation, set `THREADS = 1` in `rename_race.py` and watch both rename-only boards stop double-claiming: a race needs interleaving, which is why a single-threaded suite never saw one. Then, in `leases.py`, delete the line that releases the token and watch the assertion on `agent-b`'s claim fail, with the task back in `open/` and unclaimable.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **The claim is the rename.** A board that treats a successful rename as ownership passes every single-threaded test and, where two renames of one file can both succeed, hands one task to two agents.
- **The lease starts at the wrong time.** The claimer never stamps the claim, the rename keeps the task's old modification time, and the sweeper reclaims a task that waited in `open/` longer than the lease the moment it is taken.
- **A reclaim that keeps the token.** The sweeper returns a task to `open/` without deleting `.claims/<task>`; every exclusive create fails on it, and the task sits there forever.
- **A retry with `--force`.** The harness retries a failed `git worktree add` with `--force`, and two agents land on one branch.
- **A green branch landed without a candidate merge.** Two branches each pass their suites and merge without a textual conflict, and the mainline no longer builds.
- **A completion check treated as a fence.** The late agent's `complete()` is refused, but its branch reaches the gate anyway and lands a stale copy of the work.

---

## Common pitfalls

1. **Trusting a primitive for a guarantee it does not specify.** A rename moves a file atomically; whether it excludes a second claimer depends on the platform. Claim by exclusive create, and test the invariant with real threads behind a barrier.
2. **Treating an empty claim as an empty board.** An empty return means every task the loop saw was taken by someone else, not that no work remains; back off and re-poll instead of retiring the agent.
3. **No lease, and no quarantine behind it.** A crashed agent's task, claimed forever, is lost work; a task that fails forever burns the whole fleet's budget. Bound the claim in time and retire the repeat offender.
4. **Expecting a worktree to be an environment, or a sandbox.** It is a fresh checkout of tracked files: no dependencies, no `.env`, and no process or network isolation; tasks that run untrusted code need a container.
5. **A swarm past the gate ceiling, or on work that was not parallel.** Beyond $N^* = T/G$ the extra agents queue and add only conflict surface; the tell of non-parallel work is branches conflicting with each other rather than with the mainline.
6. **Assuming a claim means exactly-once.** Exclusive claiming stops two agents holding a task together; it does not stop a reclaimed task running twice. Make the work idempotent, let the gate discard duplicates, and fence the gate with the claim generation.

---

## Further reading

- Nicholas Carlini, "Building a C compiler with a team of parallel Claudes" (Anthropic Engineering, 5 February 2026): the 16-agent leaderless run, its cost, its lock-file claims, and the one task that would not parallelise until the harness changed.
- IEEE and The Open Group, `open()` and `rename()` (*The Open Group Base Specifications Issue 7, 2018 edition*, IEEE Std 1003.1-2017): what an exclusive create guarantees, and what a rename does.
- D. J. Bernstein, the maildir format for qmail (c. 1995): concurrent writers coordinated through a directory with no locks.
- Cary G. Gray and David R. Cheriton, "Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency" (Symposium on Operating Systems Principles, December 1989): where the lease comes from.
- Martin Kleppmann, "How to do distributed locking" (personal blog, 8 February 2016): why a check just before writing is not enough, and what a fencing token does instead.
- Git project, `git-worktree(1)` manual: `add --force`, `remove`, `lock`, `unlock` and `prune`.
- Anthropic, "Run parallel sessions with worktrees" (Claude Code documentation, consulted October 2026): `.worktreeinclude`, worktree locks and the LFS pointer trap.
- Graydon Hoare, "technicalities: 'not rocket science' (the story of monotone and bors)" (graydon2 blog, 2014): the always-green mainline and the merge robot that enforces it.
- MindStudio, "How Stripe Ships 1,300 AI PRs a Week: Harness Engineering" (MindStudio blog, edited by Luis Chavez-Mattos, 9 April 2026): the reported Stripe figure behind the gate arithmetic.
- Justin Young, "Effective harnesses for long-running agents" (Anthropic Engineering, 26 November 2025): the *sequential* multi-context build, a different problem, taken up in [post 18](../18-long-horizon-ralph/index.md).
- ai-boost, awesome-harness-engineering (GitHub, 2026): the Task Runners & Orchestration primitive, which lists the compiler run beside tools that run agents in parallel worktrees.
- `ctx-013`, "Isolate strategies": the token-level break-even for fanning work out across agents.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 18 - Long-horizon and multi-context execution: Ralph loops and context bridging](../18-long-horizon-ralph/index.md):** when the work is too big for one context, not just too much for one agent.
- **[Post 23 - The economics of a harness and Harness-as-a-Service](../23-economics-haas/index.md):** the per-agent bill this post leaves aside, and the queue-and-worker shape run as a service.
