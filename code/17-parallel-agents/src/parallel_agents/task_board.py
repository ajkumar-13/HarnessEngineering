"""A file-based task board: agents claim tasks atomically, with no central server.

Companion to Harness Engineering Post 17. Tasks are files in a directory, moving
open -> claimed -> done. Claiming is an atomic exclusive create: if two agents
race for the same task, exactly one ``O_CREAT | O_EXCL`` create succeeds and the
other gets ``FileExistsError`` and moves on. The rename that follows only moves
the file into ``claimed/``; it is not what makes the claim exclusive. See
``TaskBoard.claim`` for why the rename alone was not enough. Offline by design:
a local directory stands in for the shared repo, so there is no git and no
network. Real swarms use the same mechanism on the repo.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

_STATES = ("open", "claimed", "done")
_LOCKS = ".claims"


class TaskBoard:
    """A directory of task files in three states, claimed by exclusive create."""

    def __init__(self, root: Path):
        self.root = Path(root)
        for state in _STATES:
            (self.root / state).mkdir(parents=True, exist_ok=True)
        # Claims are serialised through this directory rather than through the
        # rename itself; see ``claim``. It is not one of the three states, so it
        # does not appear in ``counts`` and is not part of the board's shape.
        (self.root / _LOCKS).mkdir(parents=True, exist_ok=True)

    def add(self, task_id: str, body: str = "") -> None:
        # Re-opening a task must clear any spent claim token, or the task can
        # never be claimed again.
        (self.root / _LOCKS / task_id).unlink(missing_ok=True)
        (self.root / "open" / task_id).write_text(body, encoding="utf-8")

    def open_tasks(self) -> List[str]:
        return sorted(p.name for p in (self.root / "open").iterdir())

    def claim(self, agent: str) -> Optional[str]:
        """Atomically claim one open task, or return ``None`` if none are left.

        Exclusivity comes from an ``O_CREAT | O_EXCL`` create, not from the
        rename. Only one caller can create a given path with those flags: the
        kernel guarantees it on POSIX, and ``CreateFile`` with ``CREATE_NEW``
        does on Windows. The loser gets ``FileExistsError`` and moves on.

        The rename was the obvious primitive and it is not sufficient. Two
        agents renaming the same source to *different* destinations do not
        collide the way two agents renaming to the same destination would, and
        under real thread overlap both calls can return without raising while
        only one file lands. That failure is rare, so a suite that runs the
        board single-threaded, or threaded a handful of times, will not see it:
        this board was shipped with exactly that bug. ``test_board.py`` drains a
        400-task board with 8 threads behind a barrier, which reproduces it.

        The visible shape is unchanged: a claim is still ``claimed/<task>.<agent>``,
        so the owner is still readable off the name.
        """
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

    def complete(self, task_id: str, agent: str, result: str = "") -> None:
        """Mark a claimed task done. Only the agent that claimed it may complete it."""
        claim = self.root / "claimed" / f"{task_id}.{agent}"
        if not claim.exists():
            raise ValueError(f"{agent!r} has not claimed {task_id!r}")
        claim.unlink()
        (self.root / "done" / task_id).write_text(result, encoding="utf-8")

    def counts(self) -> Dict[str, int]:
        return {state: len(list((self.root / state).iterdir())) for state in _STATES}


def worktree_for(base: Path, agent: str) -> Path:
    """Give an agent an isolated working directory (a stand-in for ``git worktree add``).

    In a real repo this is ``git worktree add ../wt-<agent> -b agent/<agent>``; here
    it is a per-agent subdirectory, enough to show that no two agents share a copy.
    """
    worktree = Path(base) / "worktrees" / agent
    worktree.mkdir(parents=True, exist_ok=True)
    return worktree
