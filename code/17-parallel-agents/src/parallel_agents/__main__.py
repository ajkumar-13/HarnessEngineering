"""Demo: three agents drain a shared task board with no central coordinator.

Run:  python -m parallel_agents
Offline: a local temporary directory stands in for the shared repo.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from .task_board import TaskBoard, worktree_for


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        board = TaskBoard(Path(tmp))
        for i in range(1, 8):
            board.add(f"task-{i}", f"do work item {i}")

        agents = ["ada", "linus", "grace"]
        did = {a: [] for a in agents}

        # Real agents run concurrently; here we round-robin. The atomic claim is
        # what makes the concurrent version correct too.
        i = 0
        while board.open_tasks():
            agent = agents[i % len(agents)]
            task = board.claim(agent)
            if task:
                worktree_for(Path(tmp), agent)  # each agent edits in its own worktree
                board.complete(task, agent, result=f"{agent} finished {task}")
                did[agent].append(task)
            i += 1

        for agent in agents:
            print(f"{agent:6} did {did[agent]}")
        print("board:", board.counts())


if __name__ == "__main__":
    main()
