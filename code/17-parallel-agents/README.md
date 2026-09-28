# Parallel agents (Post 17)

A **file-based task board** with atomic claiming for a leaderless swarm. Companion to [Harness Engineering, Post 17 — Parallel agents on a shared repo](../../posts/17-parallel-agents-shared-repo/index.md).

## Run

```bash
python -m parallel_agents   # demo: three agents drain a 7-task board, no coordinator
python -m pytest -q         # offline test suite (no git, no network)
```

## What it shows

- **`TaskBoard`** — tasks are files moving `open/ → claimed/ → done/`.
- **`claim(agent)`** — an atomic `os.rename` from `open/` to `claimed/<task>.<agent>`. If two agents race for the same task, exactly one rename succeeds; the loser gets an error and takes the next task. That is the whole coordination mechanism: no central server, the repo is the coordinator.
- **`complete(task, agent)`** — only the agent that claimed a task may finish it.
- **`worktree_for(base, agent)`** — a per-agent working directory, standing in for `git worktree add ../wt-<agent> -b agent/<agent>`, so no two agents edit the same files at once.

The test suite proves the key invariant: across interleaved claims, **every task is claimed exactly once**.

## What's deliberately left out

- **Real git worktrees.** The isolation is shown with directories; production uses `git worktree` and merges verified commits back.
- **Real concurrency.** The demo round-robins; the atomic claim is what makes the genuinely-concurrent version correct.
- **Merge/conflict handling.** Integrating many branches is repo policy, sketched in the post.

MIT licensed.
