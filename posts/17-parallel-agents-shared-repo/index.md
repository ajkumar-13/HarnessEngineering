# 17 · Parallel agents on a shared repo — worktrees and task-claiming

> **TL;DR.** Many agents can work one codebase in parallel without a central orchestrator. They **claim tasks via files** (an exclusive create, so two agents never get the same task) and **isolate their edits in git worktrees** (one working copy per agent, so parallel changes never collide). The coordinator is the repository itself, which is what lets the swarm scale to more agents than any single lead could manage. The cost is merge and failure handling, which you trade for throughput.
>
> **After reading this you will be able to:**
> - Build a leaderless task board where agents claim work atomically through the filesystem.
> - Give each parallel agent an isolated working copy with a git worktree.
> - Weigh the throughput of a swarm against its coordination and merge cost.
> - Design for at-least-once execution, because a lease cannot tell a crashed agent from a slow one.

![A task board of three directories in the repo, open, claimed and done, holding the board mid-flight: two claims held, three finished, two still open. Three agent cards to the right show ada and linus working and grace between tasks, each naming the task it holds and the worktree it edits. A claim is one exclusive create and then a move: a token keyed on the task is created with O_CREAT and O_EXCL, so every agent but one gets FileExistsError, and only then does open/task-4 become claimed/task-4.ada, whose name carries the owner so a stale claim is attributable. Below, the claim in code, and the two failures that got it there: renaming and trusting the result handed one task to two agents in eight of eight trials under eight threads draining a four-hundred-task board, and renaming and checking the result afterwards passed its suite and then failed about one run in three.](diagrams/01-shared-repo-swarm.svg)
*No central orchestrator. The repository is the coordinator; a claim is an exclusive create.*

---

## 1. The shared-repo pattern

The swarm topology from [Post 16](../16-multi-agent-orchestration/index.md) has a surprising property: it needs no orchestrator at all. The largest published run of it is Anthropic's C compiler build, in which 16 Claude instances worked one repository across nearly 2,000 Claude Code sessions over two weeks, spending 2 billion input tokens and 140 million output tokens for just under $20,000, and producing a 100,000-line compiler in Rust that builds a bootable Linux 6.9 on x86, ARM and RISC-V and passes 99% of GCC's torture test suite (Carlini, 2026). The author is explicit about the topology: "I don't use an orchestration agent. Instead, I leave it up to each Claude agent to decide how to act."

The coordination that a lead agent would provide is instead carried by the **shared repository**. In that run the mechanism is small enough to describe in a sentence: an agent takes a lock on a task by writing a text file into `current_tasks/` and pushing it, so git's own rejection of a non-fast-forward push is what serialises the claim: where two agents try to claim the same task, git's synchronisation "forces the second agent to pick a different one" (Carlini, 2026). Each agent runs in its own Docker container with a bare upstream repository mounted, clones it locally, and restarts on a bare loop so it picks up the next task the moment one finishes.

This works because the two hard problems of a swarm, *who does what* and *who edits what*, both have file-based answers. Agents decide who does what by claiming task files (§2); they avoid editing the same thing by working in separate checkouts (§5). Nothing routes messages, nothing holds global state in memory, and an agent can join or die without telling anyone. The repository is the single source of truth, and that is the whole design.

---

## 2. Task-claiming via files

A task board is a directory of task files that move through states: `open/`, `claimed/`, `done/`. An agent takes work by **claiming** an open task, and the claim has to be safe against two agents reaching for the same one at the same instant.

The mechanism is an **exclusive create**. Claiming a task means creating one path that no other agent can create: `os.open` with `O_CREAT | O_EXCL` succeeds for exactly one caller and raises `FileExistsError` for all the rest, which POSIX (Portable Operating System Interface) requires and Windows provides through `CREATE_NEW` (IEEE and The Open Group, 2018). The rename that follows moves the task file into `claimed/` so the owner is readable off its name, and that move is atomic in its own right: a concurrent observer sees either the old link or the new one and never an interval in which neither exists. But atomic *visibility* is not exclusivity, and §4 is about how expensive that distinction turned out to be. The pattern is older than agents by three decades: the maildir mail spool format has concurrent deliveries write into `tmp/` and move into `new/` with no lock file and no lock server (Bernstein, c. 1995). Note where maildir gets its safety, though. Not from the rename, but from giving every message a name no other deliverer will generate, so no two deliveries ever contend for one path. A task board is a maildir with three states instead of three stages, and it needs the same discipline about names.

The core is a few lines, excerpted from the runnable companion in [`code/17-parallel-agents/`](../../code/17-parallel-agents/):

```python
# code/17-parallel-agents/src/parallel_agents/task_board.py
def claim(self, agent: str) -> Optional[str]:
    """Atomically claim one open task, or return None. Two agents never get the same one."""
    for name in self.open_tasks():
        src = self.root / "open" / name
        dst = self.root / "claimed" / f"{name}.{agent}"
        token = self.root / ".claims" / name               # keyed on the task, not the agent
        try:
            fd = os.open(token, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue                                       # someone else holds it; next
        os.close(fd)                                       # from here the task is ours alone
        try:
            os.rename(src, dst)                            # the move, not the exclusion
        except OSError:
            token.unlink(missing_ok=True)
            continue
        return name
    return None
```

No lock server, no database, no coordinator: the filesystem's own atomicity is the concurrency control. This is the state primitive of [Post 08](../08-state-filesystem-git/index.md) doing coordination duty, and it is why the earlier claim that "the repository is the bus" ([Post 16](../16-multi-agent-orchestration/index.md) §7) is literal.

An atomic primitive does not by itself buy you an atomic *claim*, and this board took two attempts to learn it. The first version returned `name` whenever the rename did not raise. Under eight threads draining a four-hundred-task board that handed the same task to two agents in eight of eight trials, while exactly four hundred files landed in `claimed/`: both agents believed they owned the work, and the board disagreed with both. The obvious repair was to stop inferring the effect from the absence of an error and check it instead, confirming that the destination existed and the source was gone before returning. That version passed its suite. It was still wrong, and it failed on a later run at roughly one trial in three, handing one task to two agents while only one of their two files existed on disk.

The second failure is the more instructive one, because the first repair was reasoning about the wrong thing. Two agents renaming one source to the *same* destination collide, and one of them loses. These two rename it to *different* destinations, `task-4.ada` and `task-4.linus`, so there is no contended name for the filesystem to arbitrate, and no amount of checking afterwards recovers an exclusion that was never requested. The token above is keyed on the task rather than on the claimant, which is what makes it a contended name and therefore a decidable one. **Ask the filesystem for exclusivity; do not check afterwards whether you happened to get it.**

The failure is also a lesson about tests. Every test that shipped with this board passed, because every one of them was single-threaded, and a race cannot occur in a schedule that never interleaves. A concurrency invariant needs a concurrent test (threads, a barrier, and a few hundred tasks), or the suite is asserting the property it is least able to see. The companion now ships nine tests, of which `test_concurrent_claims_are_exactly_once` is the only one that could ever have caught it.

Five details in that loop are load-bearing, and getting any of them wrong quietly breaks the guarantee.

**The rename must stay on one filesystem.** `rename` is atomic *within* a filesystem. Across a mount boundary it is not available as a single operation, and the runtime falls back to copy-then-delete, which has a window in the middle where the task exists in both places, or neither. Keep `open/`, `claimed/`, and `done/` under one root on one volume. The same caution applies to network filesystems, where the atomicity guarantee depends on the protocol and the server rather than on your code.

**The claim name carries the owner.** The destination is `claimed/<task>.<agent>`, not `claimed/<task>`. That one detail buys two things: you can see at a glance who holds what, and a stale claim can be attributed to the agent that abandoned it, which is what makes the lease of §4 implementable at all.

**Only the claimer may finish.** Completion checks that the claim file belongs to the agent completing it:

```python
def complete(self, task_id: str, agent: str, result: str = "") -> None:
    claim = self.root / "claimed" / f"{task_id}.{agent}"
    if not claim.exists():
        raise ValueError(f"{agent!r} has not claimed {task_id!r}")
    claim.unlink()
    (self.root / "done" / task_id).write_text(result, encoding="utf-8")
```

Without that check, a confused agent can mark someone else's in-flight task done, and the board loses the one invariant it exists to hold.

**Catch the lost race, not every error.** The blanket except clause above is wider than the comment beside it. A permissions failure, a full disk, a read-only mount and a name that is too long all raise the same base exception, and all of them get reinterpreted as "someone else claimed it". A broken board then presents itself as an idle swarm, which is the hardest failure to diagnose because nothing looks wrong. Narrow the clause to the two outcomes a genuine lost race produces, a missing-source error where another agent has already moved the file and a file-exists error where the destination is taken, and let every other operating-system error propagate.

**An empty result means safety, not liveness.** The loop takes one snapshot of `open_tasks()` and walks it. A claim that returns nothing therefore means that every task the loop saw a moment ago lost its race, not that the board is empty: more work may have been open the whole time. A driver that treats an empty return as a shutdown signal retires agents while work remains. On an empty return, back off briefly and re-poll, and exit only when the board reads empty across a full poll interval. The same snapshot has a second cost: every agent scans the same `sorted()` order, so all of them contend on the same head task and the losers each burn a failed rename per round. Shuffling the candidate order removes that contention in one line.

---

## 3. The same primitive at two layers

A claim is a compare-and-set: read a task's state, and take it only if nothing has taken it since. What changes between deployments is not the idea but where the compare-and-set lives, and that is decided by whether the agents share a filesystem.

When they do, `rename` is the primitive, and §2 is the whole implementation. When they do not, the filesystem cannot arbitrate, because there is no single filesystem to arbitrate on. The primitive is then git's own reference update: a push is rejected unless it fast-forwards the remote branch, so exactly one of two agents pushing a lock file for the same task succeeds and the other is told to pull and try again. That is the mechanism the C compiler run used, and it is why its claim protocol is "write a file into `current_tasks/` and push" rather than a rename (Carlini, 2026). Each agent's cycle is the same shape as the local one with a synchronisation step folded in: take the lock, do the work, pull from upstream, merge whatever other agents landed while you were busy, push, and remove the lock.

The two versions have different costs and the same guarantee. A rename resolves in microseconds and every agent sees the result immediately, because there is one directory. A push resolves in a network round trip, and an agent only learns about other agents' work when it pulls, so the board's state is always slightly stale in every worker's view. Neither is more correct. The one that fits is decided by §6.

---

## 4. Leases, reclaim and quarantine

A claim with no expiry is a lock held by a process that might already be dead. The board would then have a task that is neither open nor done, held forever by an agent that will never return, and the swarm quietly loses a unit of work each time an agent crashes.

The fix is to bound the claim in time. A lock with a time bound is a **lease**, in the sense Gray and Cheriton gave the term: a holder's right to the resource expires on its own unless renewed, so a failure costs performance rather than correctness, and short leases keep that cost small (Gray and Cheriton, 1989). Applied to a task board, a lease means a sweeper can walk `claimed/`, look at each claim file's modification time, and return anything older than the lease to `open/`. Because the claim filename carries the owner (§2), the sweeper also knows which agent to attribute the abandonment to.

Two states are not enough once you have a lease, because a task that fails repeatedly will be reclaimed repeatedly. That is a doom loop ([Post 05](../05-agent-failure-modes/index.md)) spread across a swarm rather than trapped in one agent's loop, and it burns the whole fleet's budget on the one task nobody can do. The board needs an attempt counter and a fourth state. The companion ships the three states in `_STATES`, so the sweeper below is an extension of it rather than an excerpt from it; it is under twenty lines. Note the token: a task going back to `open/` has to have its claim token released, or the exclusive create in §3 will refuse it forever and the task is quarantined by accident:

```python
# An extension of the companion's board: a lease sweeper and a fourth state.
LEASE_S, MAX_ATTEMPTS = 900, 3

def reclaim_stale(root, now):
    """Return expired claims to open/; quarantine the ones that keep failing."""
    reclaimed = []
    for claim in sorted((root / "claimed").iterdir()):
        if now - claim.stat().st_mtime < LEASE_S:
            continue                                  # holder is still inside its lease
        task_id, _, agent = claim.name.rpartition(".")
        tally = root / "attempts" / task_id
        attempts = int(tally.read_text()) + 1 if tally.exists() else 1
        tally.parent.mkdir(exist_ok=True)
        tally.write_text(str(attempts))
        state = "quarantine" if attempts >= MAX_ATTEMPTS else "open"
        (root / state).mkdir(exist_ok=True)
        (root / ".claims" / task_id).unlink(missing_ok=True)   # release, or it is unclaimable
        os.rename(claim, root / state / task_id)      # one sweeper, so the move needs no lock
        reclaimed.append((task_id, agent, attempts, state))
    return reclaimed
```

Choose the lease from how long the work legitimately takes, with headroom: long enough that a slow but healthy agent is never reclaimed under normal load, short enough that a genuinely dead agent's task does not sit idle for an afternoon. Fifteen minutes suits a task sized to one verified branch; an hour suits a task that runs a full build. What you cannot do is choose a value that makes the underlying race go away, and §9 is about why.

---

## 5. Git worktrees for edit isolation

Claiming decides *who does what*; it does not stop two agents from editing the same files. If every agent worked in the same checkout, their edits would clobber each other. On one machine, a **git worktree** solves this: it gives each agent its own working directory and branch off the one repository.

```bash
git worktree add ../wt-ada    -b agent/ada
git worktree add ../wt-linus  -b agent/linus
git worktree add ../wt-grace  -b agent/grace
```

![One main repo with a single object database and one history, above three worktrees, one per agent on its own branch: ada running, linus crashed with its claim expired and its tree left locked, and grace verified and merging back through a gate that only lets a branch land after the candidate merge builds and its tests pass. A lifecycle panel gives the add, remove and unlock commands. Four panels below cover the consequences: a worktree costs a working copy rather than a copy of the history; add declines a branch already checked out elsewhere; a worktree is a checkout and not an environment, so each tree needs its own dependency install and a .worktreeinclude file to carry gitignored files across; and removal needs a sweeper, because nothing prunes the branches a long swarm leaves behind.](diagrams/02-worktree-isolation.svg)
*One repo, one working copy per agent. Parallel edits happen in isolation and merge back verified.*

Each agent edits only inside its own worktree, on its own branch, so no two agents touch the same working files at once. They share the repository's history but not its working state. When an agent finishes a task and its work passes verification ([Post 11](../11-verification-loops/index.md)), its branch merges back into the mainline. Isolation during the work, integration after it.

Where every agent runs on one machine against one filesystem, four properties of worktrees decide whether this beats giving every agent its own clone.

- **They share one object database.** A worktree costs a working copy, not a copy of the history. Adding the tenth agent is cheap even on a repository with years of commits, and every agent sees every other agent's merged work the moment it lands, because there is only one history.
- **Git refuses to check out one branch twice.** By default `git worktree add` declines when the branch is already checked out in another worktree. That is a free correctness guarantee, but only until someone passes `--force`, which the manual says plainly "overrides these safeguards". The realistic accident is not a developer typing it; it is a harness that retries a failed `git worktree add` with `--force` appended, which turns the guarantee off for every agent at once. Retry with a different branch name, never with `--force`.
- **A worktree is a fresh checkout, not a copy of your environment.** It contains tracked files and nothing else: no `node_modules`, no virtual environment, no build cache, no `.env`, and Git Large File Storage content arrives as pointer files. Every worktree therefore needs its own dependency install and its own gitignored configuration before an agent can do anything useful in it, and that setup, not disk space, is the real marginal cost of the tenth agent. A production harness has to supply both halves: Claude Code's worktree support tells you a worktree is a fresh checkout and to initialise your development environment there, and it reads a `.worktreeinclude` file in gitignore syntax that copies gitignored files such as `.env` into every worktree it creates (Anthropic, 2026). The same documentation names the Large File Storage trap: where the repository was set up with `git lfs install --local`, a new worktree holds pointer files until `git lfs pull` runs inside it.
- **Dead agents leave debris that has to be swept.** The clean exit path is `git worktree remove`, with `--force` where the tree is dirty. A crashed agent can leave a worktree *locked*, and `remove` refuses those until `git worktree unlock` runs, or `--force` is given twice. `git worktree prune` is neither of those: it is the repair for a directory somebody deleted out from under git, and git already clears stale registrations on its own `gc.worktreePruneExpire` schedule. The thing that genuinely needs a written policy is the branches, which nothing sweeps automatically and which a long-running swarm accumulates by the hundred.

The companion in [`code/17-parallel-agents/`](../../code/17-parallel-agents/) stands the isolation up with per-agent directories through `worktree_for()` rather than real worktrees, which is enough to demonstrate that no two agents share a copy while keeping the tests free of a git dependency. Its demo drains a seven-task board across three agents with no coordinator; its suite asserts the invariant that matters, that across interleaved and genuinely threaded claims every task is claimed exactly once.

---

## 6. Choosing the isolation boundary

Sections 2 and 5 teach the one-machine design; §1's evidence is a many-machine design. Which one you are building is decided by where your agents run and how much you trust what they execute, and the choice fixes the claim primitive with it.

| Where the agents run | Isolation | Claim primitive | What it costs | The tell |
|---|---|---|---|---|
| One machine, one filesystem, tasks you trust | `git worktree` per agent | `rename` within the board directory (§2) | Branch and worktree debris to sweep; one dependency install per worktree | Merged work is visible to every agent the instant it lands, because there is one history |
| Many machines, or one machine with containers | Per-agent clone of a bare upstream repository | Push a lock file; git rejects the non-fast-forward (§3) | A pull and a push on every cycle, so each agent's view of the board is slightly stale | This is what the 16-agent compiler run did (Carlini, 2026) |
| One machine, but tasks that may be destructive | Container plus a clone inside it | Either, but the container boundary is the point | Image upkeep and container start-up per task | You want process and network isolation, not just file isolation ([Post 14](../14-permissions-sandboxes/index.md)) |

The third row is the one people skip. A worktree isolates *files* and nothing else: an agent in a worktree shares the machine's processes, its network, its environment variables and its credentials with every other agent. Where the tasks involve running code the agents themselves wrote, the blast radius argument of [Post 14](../14-permissions-sandboxes/index.md) applies with full force, and file isolation is not the isolation you were looking for.

---

## 7. Merge and conflict handling

Isolation defers the coordination problem to merge time rather than removing it. Several branches all changing one codebase will sometimes conflict, and the swarm needs a policy for it.

**Conflicts scale with overlap, not with branch size.** Small branches help only because a branch that does one claimed task usually touches a narrow set of files. The variable that actually governs the conflict rate is how disjoint the *decomposition* is: sixteen tiny branches that all edit the same code generator conflict constantly. The 16-agent run reports exactly that: "Merge conflicts are frequent, but Claude is smart enough to figure that out" (Carlini, 2026). Frequent conflicts at high agent counts are the normal case, not a sign that something is broken.

**Gate on the merged result, not on the branch.** A branch that is green on its own is not evidence that the mainline will be green after it lands, and for a swarm that difference is the main event. Branch A renames `parse_expr` to `parse_expression` and updates all seven of its callers; branch B adds an eighth call to `parse_expr`. Both suites pass. Git sees two disjoint hunks and merges them without a murmur. The mainline no longer builds. This is a **semantic conflict**, and no amount of testing the branches in isolation can see it, because the broken state exists in neither branch.

The remedy is to build the candidate merge and run the suite on that, landing only if it is green:

```bash
git fetch origin agent/ada
git switch --detach origin/main
git merge --no-ff FETCH_HEAD || exit 1   # textual conflict: reject, do not land
pytest -q || exit 1                      # semantic conflict: rejected here, and only here
git push origin HEAD:main                # fast-forward; lose the race and the gate retries
```

This is solved infrastructure rather than something to invent. Graydon Hoare built the bors merge robot for Rust to enforce a rule he stated as automatically maintaining a repository of code that always passes all the tests (Hoare, 2014), and the pattern has descendants in GitHub's merge queue and in Zuul. Adopting one of them is cheaper than getting the last line's race right on your own.

That is also what "serialise the merge, not the work" really means. The work runs fully parallel; only the gate is serialised, and it is not bookkeeping. It is the only moment in the entire design when the combined state of every agent's work is ever verified. A failure or a conflict at the gate sends the task back to `open/` to be reclaimed rather than into the mainline, so the mainline stays the source of truth and a single agent's mistake is discarded rather than integrated.

---

## 8. Throughput versus coordination cost

The reason to run a swarm is throughput. Where a task fans out into many independent pieces (a large migration, a sweep across a codebase, a batch of similar fixes), a swarm moves far more work per hour than one agent could. One report puts Stripe at roughly 1,300 AI-generated pull requests a week, reviewed, merged and deployed (Chavez-Mattos, 2026), which works out at about 7.7 landings an hour sustained around the clock, and therefore at a merge gate that clears a candidate in under eight minutes, day and night.

That last step is the whole economics of §7 in one number, and it generalises. Take N agents, each producing a verified branch every T minutes, against a merge gate that costs G minutes of serialised verification. Sustained throughput is min(N/T, 1/G) tasks per minute. The gate saturates at N\* = T/G agents; every agent past that queues at the gate and buys nothing but conflict surface. With a 30-minute task and an 8-minute gate:

| Agents (N) | Branches produced per hour | Gate ceiling per hour | Sustained landings per hour | Gain over the previous row |
|---|---|---|---|---|
| 1 | 2.0 | 7.5 | 2.0 | — |
| 2 | 4.0 | 7.5 | 4.0 | +2.0 |
| 3 | 6.0 | 7.5 | 6.0 | +2.0 |
| 4 | 8.0 | 7.5 | **7.5** | +1.5 |
| 8 | 16.0 | 7.5 | 7.5 | 0 |
| 16 | 32.0 | 7.5 | 7.5 | 0 |

The numbers are illustrative, but the shape is not: N\* = 30/8 is under four, so the fifth agent adds throughput for nobody and conflict surface for everyone. Past saturation the fix is a faster or a parallelised gate, never a bigger swarm. Halving G to four minutes doubles the ceiling to 15 an hour and moves saturation out to about eight agents; adding twelve more agents at G = 8 moves it nowhere. Measure G before you size N.

Throughput is not free in tokens either. Every agent is a full context and a full loop, and that per-agent bill is priced in [Post 23](../23-economics-haas/index.md); this section prices only the coordination overhead sitting on top of it. The break-even is the same test as [Post 16](../16-multi-agent-orchestration/index.md) §6, now measured in merges and claimed files.

The failure case has a name and a witness. A swarm on work that was not actually parallel is an expensive single agent with extra conflicts, and the compiler run hit precisely that when it turned from the compiler's many independent features to the single goal of compiling the Linux kernel: that "is one giant task. Every agent would hit the same bug, fix that bug, and then overwrite each other's changes", so "having 16 agents running didn't help because each was stuck solving the same task" (Carlini, 2026). The diagnostic follows from it. Watch what your branches conflict *with*. Conflicts against the mainline are the ordinary tax of parallel work; branches conflicting with each other, at a rate that climbs as you add agents, mean the decomposition is wrong and no merge policy will rescue it.

---

## 9. At-least-once execution, not exactly-once

The atomic claim guarantees that two agents never claim a task *at the same moment*. It does not guarantee that a task is only ever worked once, and the gap between those two statements is where the subtle bugs live.

![A three-lane timeline: agent A claims task-7, starts work, and goes quiet; the board's lease expires and returns the task to open; agent B claims it and finishes; then agent A wakes up and finishes too. Below, three mitigations: make the task idempotent, let the merge gate deduplicate, or compare-and-set on finish.](diagrams/03-at-least-once.svg)
*Seven steps, no bug. Every claim in this sequence was atomic, and the task still ran twice.*

Consider the reclaim of §4. An agent claims a task, starts work, and goes quiet: a hung model call, a lost network, a machine that was paused rather than killed. The lease expires, another agent reclaims the task and does it. Then the first agent wakes up and finishes too. Nothing was violated: each claim was atomic, and the board behaved exactly as designed. The task simply ran twice.

You cannot distinguish "crashed" from "slow" from outside, which is why every system of this shape settles for **at-least-once execution** and works instead to make the second execution harmless. Three ways to do that, in rough order of preference:

- **Make the task idempotent.** If the work is "ensure this file matches the spec" rather than "append a line", running it twice is indistinguishable from running it once. This is by far the cheapest fix, and it is mostly a matter of how tasks are phrased.
- **Let the merge gate deduplicate.** Two branches doing the same task produce the same change; the first merges, the second becomes an empty diff or a conflict and is discarded. The gate of §7 is already the deduplication point. It only has to be allowed to reject a duplicate rather than treat it as a failure.
- **Make the completion a compare-and-set.** The ownership check already in `complete()` (§2) is exactly this: a finish that refuses unless the agent still holds the claim. Presented in §2 as a guard against confusion, it is the same three lines.

The third one has a limit worth knowing, because it is where most designs stop and it is not sufficient on its own. Kleppmann's argument about distributed locks applies directly: you "cannot fix this problem by inserting a check on the lock expiry just before writing back to storage", since the process can be paused between the check and the write (Kleppmann, 2016). The durable version pushes the check down to the resource, which keeps the highest token it has seen and "rejects any writes on which the token has gone backwards". In a shared-repo swarm the resource is the merge gate, and the token is the claim generation: give each reclaim an incrementing attempt number, carry it on the branch, and have the gate refuse a branch whose number is stale. That converts double *work* into single *effect* and costs only the loser's tokens.

What does not work is tuning the lease until the problem goes away. A shorter lease reclaims live agents more often; a longer one leaves genuinely dead tasks stuck for longer. There is no setting that removes the race, only settings that trade its two failure modes against each other. Pick the lease for how long the work legitimately takes (§4), and make double execution harmless by design.

---

## 10. Failure isolation across the swarm

A leaderless design has a real reliability advantage: **no single point of failure**. An agent can crash mid-task and the swarm continues, because its claimed but unfinished task returns to `open/` on the next sweep and is reclaimed by another. There is no coordinator whose death stops everyone.

At swarm scale that recovery path is not a contingency, it is the ordinary case, and one line of arithmetic shows why. If each agent fails independently with probability p on a given task, the chance that a batch of N parallel tasks contains at least one failure is 1 - (1 - p)^N. At an optimistic p = 0.05, a single agent fails on one task in twenty, while sixteen agents produce at least one failure 56% of the time. Assume any given round has a casualty and you will be right more often than not. That is why the reliability story here is reclaim, quarantine and observation rather than any attempt to stop agents failing.

The corresponding risk is the task that no agent can finish, claimed and released and reclaimed forever, which is what the attempt counter and the `quarantine/` state of §4 exist to stop: after a small number of failures the task leaves the rotation and waits for a human ([Post 15](../15-human-in-the-loop/index.md)) instead of consuming the fleet. And because many agents multiply the failure surface, per-agent traces ([Post 21](../21-observability-traces/index.md)) are what make a swarm debuggable at all. A trace that does not carry the agent identity and the task identifier turns sixteen concurrent stories into one unreadable one.

---

## Common pitfalls

- **Claiming without atomicity, or across a mount boundary.** A read-then-write claim lets two agents take the same task, and `rename` is atomic only within one volume: a board split across filesystems degrades to copy-then-delete and the guarantee is gone (§2).
- **Trusting the primitive instead of checking the effect.** `os.rename` not raising is not proof the claim landed. Confirm the move before acting on it, catch only the two errors a genuine lost race produces rather than every filesystem failure, and test the invariant with real threads (§2).
- **Treating an empty claim as an empty board.** An empty return means every task the loop saw lost its race, not that no work remains. Back off and re-poll instead of retiring the agent (§2).
- **No lease, and no quarantine behind it.** A crashed agent's task, claimed forever, is lost work; a task that fails forever burns the whole fleet's budget. Bound the claim in time and retire the repeat offender (§4).
- **Expecting a worktree to be an environment, or a sandbox.** It is a fresh checkout of tracked files: no dependencies, no `.env`, Large File Storage pointers instead of content, and no process or network isolation whatsoever. Never let a harness retry a failed `git worktree add` with `--force`, either; that switches off the one guarantee stopping two agents landing on one branch (§5, §6).
- **Gating on the branch instead of the merged result.** Two branches can each be green, merge without a textual conflict, and still break the mainline. Build the candidate merge and test that (§7).
- **A swarm past the gate ceiling, or on work that was not parallel.** Beyond N\* = T/G the extra agents queue and contribute only conflict surface, and if the tasks were never independent the swarm is an expensive single agent. The tell is branches conflicting with each other rather than with the mainline (§8).
- **Assuming a claim means exactly-once.** Atomic claiming stops two agents starting together; it does not stop a reclaimed task running twice. Make the work idempotent, or let the merge gate discard the duplicate (§9).
- **No per-agent trace.** Many agents multiply the failure surface; without traces carrying the agent and task identity a swarm is undebuggable (§10).

---

## Further reading

- Carlini, N., "Building a C compiler with a team of parallel Claudes" (2026): the 16-agent leaderless run this post is drawn from, with its token cost, its lock-file claim protocol, and the one task it could not parallelise.
- Anthropic, "Effective harnesses for long-running agents" (2025): the *sequential* multi-context build and its handoff artefacts. A different problem from this post's; Post 18 is where it belongs.
- Gray, C. and Cheriton, D., "Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency" (1989): where the lease comes from, and why short ones make failure a performance cost rather than a correctness one.
- Kleppmann, M., "How to do distributed locking" (2016): why checking a lease just before writing is not enough, and what a fencing token does instead.
- Bernstein, D. J., maildir specification for qmail (c. 1995): the thirty-year-old production precedent for claiming work by renaming a file between directories, lock-free by design.
- Git project, `git-worktree(1)` manual: the reference for `add --force`, `remove`, `unlock` and `prune`. Read it before you write a sweeper.
- Anthropic, "Run parallel sessions with worktrees" (2026): what a production harness has to provide around worktrees, including `.worktreeinclude` and the Large File Storage pointer trap.
- Hoare, G., "technicalities: 'not rocket science' (the story of monotone and bors)" (2014): the always-green-mainline rule and the merge-queue lineage that enforces it.
- Chavez-Mattos, L., "How Stripe Ships 1,300 AI PRs a Week: Harness Engineering" (2026): the Stripe throughput figure this post's gate arithmetic is anchored to.
- awesome-harness-engineering (2026): the Task Runners & Orchestration section.
- Context Engineering, Post 13, "Isolate strategies": the token-level break-even for fanning work out across agents, the cost side of this post's throughput case.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 18 — Long-horizon & multi-context execution](../18-long-horizon-ralph/index.md)**: when the work is too big for one context, not just too much for one agent.
- **[Post 08 — State & the filesystem](../08-state-filesystem-git/index.md)**: the file-and-git primitives the whole swarm is built on.
- **[Post 16 — Multi-agent orchestration](../16-multi-agent-orchestration/index.md)**: where the swarm sits among the topologies, and when to choose it.
