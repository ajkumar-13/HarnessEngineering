"""Post 17, section 2: the two rename-only boards the companion replaced, raced the way its test races it.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/snippets/jobs/rename_race.py

Two claim functions that use the rename as the whole claim, each on a fresh 400-task board drained by eight
threads behind a barrier, as in claim_race.py:

  rename and trust   return the task whenever os.rename did not raise
  rename and check   also confirm afterwards that the destination exists and the source is gone

A run counts when at least one task was claimed by two agents. Whether a rename alone excludes depends on the
platform and the filesystem, so the counts printed here are a measurement of this machine, and they change from
run to run. Standard library only.
"""
import os
import platform
import sys
import tempfile
import threading
from pathlib import Path

sys.dont_write_bytecode = True
TASKS, THREADS = 400, 8


def rename_and_trust(root, agent):
    for name in sorted(p.name for p in (root / "open").iterdir()):
        try:
            os.rename(root / "open" / name, root / "claimed" / f"{name}.{agent}")
        except OSError:
            continue
        return name
    return None


def rename_and_check(root, agent):
    for name in sorted(p.name for p in (root / "open").iterdir()):
        src, dst = root / "open" / name, root / "claimed" / f"{name}.{agent}"
        try:
            os.rename(src, dst)
        except OSError:
            continue
        if dst.exists() and not src.exists():   # confirm the effect instead of inferring it
            return name
    return None


def one_run(claim):
    """One drained board: (tasks claimed twice, claims reported, files in claimed/)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for state in ("open", "claimed"):
            (root / state).mkdir()
        for i in range(TASKS):
            (root / "open" / f"task-{i:03d}").write_text("", encoding="utf-8")
        claims, lock = [], threading.Lock()
        barrier = threading.Barrier(THREADS)

        def agent(name):
            barrier.wait()
            while any((root / "open").iterdir()):
                task = claim(root, name)
                if task is not None:
                    with lock:
                        claims.append(task)

        threads = [threading.Thread(target=agent, args=(f"agent-{i}",)) for i in range(THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return len(claims) - len(set(claims)), len(claims), len(list((root / "claimed").iterdir()))


def main():
    print(f"platform: {platform.system()}; {TASKS} tasks, {THREADS} threads per run")
    for label, claim, runs in (("rename and trust", rename_and_trust, 8), ("rename and check", rename_and_check, 20)):
        results = [one_run(claim) for _ in range(runs)]
        bad = sum(1 for doubles, _, _ in results if doubles)
        files = sorted({f for _, _, f in results})
        print(f"{label}: runs with a double claim: {bad} of {runs}; files in claimed/ per run: {files}")


if __name__ == "__main__":
    main()
