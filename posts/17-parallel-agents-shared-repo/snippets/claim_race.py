"""Post 17, Make it run: the companion's task board drained by eight threads, with no double claim.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/snippets/claim_race.py

The board is `TaskBoard` from code/17-parallel-agents/src, imported unchanged. Each trial adds 400 tasks to a
fresh board in a temporary directory, releases eight agent threads together through a `threading.Barrier`, and
lets every agent call `claim` until it returns None. A double claim is a task that two agents were both told
they own. The trials are repeated because a race that is rare in one trial is still a race. Which agent wins
which task changes from run to run, so the per-agent split is printed last and is not part of the result.
Standard library only.
"""
import sys
import tempfile
import threading
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "17-parallel-agents" / "src"))
from parallel_agents import TaskBoard  # noqa: E402

TASKS, THREADS, TRIALS = 400, 8, 8


def drain(board, n_threads=THREADS):
    """Release n_threads agents at once; return every (agent, task) claim they were told succeeded."""
    claims, lock = [], threading.Lock()
    barrier = threading.Barrier(n_threads)

    def agent(name):
        barrier.wait()                       # every agent reaches for the head task at the same instant
        while (task := board.claim(name)) is not None:
            with lock:
                claims.append((name, task))

    threads = [threading.Thread(target=agent, args=(f"agent-{i}",)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return claims


def trial():
    with tempfile.TemporaryDirectory() as tmp:
        board = TaskBoard(Path(tmp))
        for i in range(TASKS):
            board.add(f"task-{i:03d}")
        claims = drain(board)
        per_task = Counter(task for _, task in claims)
        doubles = sum(1 for n in per_task.values() if n > 1)
        on_disk = sorted(p.name for p in (Path(tmp) / "claimed").iterdir())
        owners_match = on_disk == sorted(f"{task}.{agent}" for agent, task in claims)
        return dict(claims=len(claims), doubles=doubles, counts=board.counts(),
                    owners_match=owners_match, per_agent=Counter(agent for agent, _ in claims))


def main():
    results = [trial() for _ in range(TRIALS)]
    print(f"{TRIALS} trials, {TASKS} tasks, {THREADS} threads released by a barrier")
    print("double claims per trial:", [r["doubles"] for r in results])
    print("claims per trial:       ", sorted({r["claims"] for r in results}))
    print("board after each trial: ", sorted({tuple(r["counts"].items()) for r in results}))
    print("every claim file names the agent that was told it won:", all(r["owners_match"] for r in results))
    split = sorted(results[0]["per_agent"].values())
    print(f"first trial, claims per agent (varies by run): {split}")
    assert all(r["doubles"] == 0 and r["claims"] == TASKS and r["owners_match"] for r in results)


if __name__ == "__main__":
    main()
