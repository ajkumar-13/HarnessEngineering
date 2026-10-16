# 17 - Parallel agents

The runnable companion to [17 - Parallel agents on a shared repo: worktrees and task-claiming](../../posts/17-parallel-agents-shared-repo/index.md). A file-based task board for a leaderless swarm: agents claim tasks through the filesystem, with no central server, in plain Python with no runtime dependencies.

## What is here

| File | What it is |
|------|-----------|
| `src/parallel_agents/task_board.py` | `TaskBoard`, with `add`, `open_tasks`, `claim`, `complete` and `counts`, and `worktree_for`. |
| `src/parallel_agents/__main__.py` | An offline demo, `python -m parallel_agents`. |
| `tests/test_board.py` | Nine tests, the last of them eight threads draining a 400-task board behind a barrier. No git and no network. |

## Quickstart (offline)

From this directory:

```bash
uv run python -m parallel_agents     # three agents drain a seven-task board, no coordinator
uv run --extra dev pytest -q         # the nine tests
```

The demo lets three agents take turns at the board and prints what each finished, then `board: {'open': 0, 'claimed': 0, 'done': 7}`.

## What it shows

- **`TaskBoard(root)`** keeps tasks as files in three directories, `open/`, `claimed/` and `done/`, plus a `.claims/` directory of claim tokens that is not one of the states. `add` clears any spent token for the task, so a re-added task can be claimed again.
- **`claim(agent)`** takes an open task in two steps. First it creates the token `.claims/<task>` with `os.open(token, O_CREAT | O_EXCL | O_WRONLY)`: exactly one caller can create a given path that way, and every other gets `FileExistsError` and tries the next task. Only then does it rename `open/<task>` to `claimed/<task>.<agent>`, so the owner is readable off the name. The exclusive create is what makes the claim exclusive; the rename is the move. If the rename fails, the token is released and the next task is tried.
- **Why not the rename alone.** The board first shipped claiming by rename, and every single-threaded test passed. `test_concurrent_claims_are_exactly_once` releases eight threads through a `threading.Barrier` onto a 400-task board and asserts that no task is claimed twice; it is the one test of the nine that can see a race.
- **`complete(task, agent, result)`** moves a task to `done/` only for the agent that claimed it; any other agent gets `ValueError`.
- **`worktree_for(base, agent)`** gives each agent its own directory, a stand-in for `git worktree add ../wt-<agent> -b agent/<agent>`, so no two agents edit the same copy.

## Left out on purpose

- **Real git worktrees.** The isolation is shown with directories; the post covers `git worktree` and merging verified branches back through a gate.
- **Leases, reclaim and quarantine.** A claim here never expires. The post's `snippets/leases.py` adds a lease sweeper and a `quarantine/` state on top of this board without changing it.
- **Concurrency in the demo.** The demo takes turns; the threaded test is where the claim meets real concurrency, and the post's `snippets/claim_race.py` repeats it eight times.
- **Merge and conflict handling.** Integrating many branches is repository policy, which the post sketches.

MIT licensed.
