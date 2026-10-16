"""Post 17, sections 4 and 9: a lease sweeper and a fourth state on top of the companion's board.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/snippets/leases.py

The board is `TaskBoard` from code/17-parallel-agents/src, imported unchanged; the lease, the sweeper and the
`quarantine/` state are this snippet's, because the companion ships none of them. A lease is the claim file's
modification time: the claimer stamps it when it takes the task and again to renew it. The stamp is needed
because `os.rename` keeps a file's modification time, so a claim would otherwise look as old as the task.

The clock is simulated (seconds from 0), so the run is deterministic and takes no time. Two scenes:

  at-least-once   agent-a claims task-7 and goes quiet; the lease expires and the sweeper reopens the task;
                  agent-b claims it and finishes; agent-a wakes and finishes too. The task ran twice. Its work is
                  idempotent, so the second run changes nothing, and the companion's ownership check refuses
                  the second completion.
  quarantine      every holder of task-9 dies; after three reclaims the task leaves the rotation.

Standard library only.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "17-parallel-agents" / "src"))
from parallel_agents import TaskBoard  # noqa: E402

EPOCH = 1_800_000_000          # the simulated clock's zero, as a file time
LEASE_S, MAX_ATTEMPTS = 900, 3


def stamp(claim, now):
    """Take or renew the lease: the claim file's modification time is the moment it was last renewed."""
    os.utime(claim, (EPOCH + now, EPOCH + now))


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


def ensure(path, content):
    """Idempotent work: make the file hold `content`. Running it twice is the same as running it once."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return "unchanged"
    path.write_text(content, encoding="utf-8")
    return "written"


def at_least_once(root):
    board = TaskBoard(root)
    board.add("task-7", "make settings.toml hold the spec")
    out = root / "settings.toml"
    spec = 'retries = 3\n'
    events = []

    def log(t, who, what):
        events.append((t, who, what))

    assert board.claim("agent-a") == "task-7"
    stamp(root / "claimed" / "task-7.agent-a", 0)
    log(0, "agent-a", f"claims task-7; lease to t={LEASE_S}")
    stamp(root / "claimed" / "task-7.agent-a", 300)
    log(300, "agent-a", f"renews, then goes quiet; lease to t={300 + LEASE_S}")
    for t in (900, 1200):
        swept = reclaim_stale(root, t)
        log(t, "sweeper", "lease still live, nothing to do" if not swept else
            f"lease expired: task-7 back to open/ (attempt {swept[0][2]})")
    assert board.claim("agent-b") == "task-7"
    stamp(root / "claimed" / "task-7.agent-b", 1210)
    log(1210, "agent-b", "claims task-7")
    log(1500, "agent-b", f"does the work: settings.toml {ensure(out, spec)}")
    board.complete("task-7", "agent-b", result="settings.toml holds the spec")
    log(1500, "agent-b", "completes: task-7 in done/")
    log(1800, "agent-a", f"wakes, does the work: settings.toml {ensure(out, spec)}")
    try:
        board.complete("task-7", "agent-a")
        log(1800, "agent-a", "completes")
    except ValueError as refused:
        log(1800, "agent-a", f"completion refused: {refused}")
    return events, board.counts(), out.read_text(encoding="utf-8")


def quarantine(root):
    board = TaskBoard(root)
    board.add("task-9", "a task no agent can finish")
    events = []
    t = 0
    for agent in ("agent-c", "agent-d", "agent-e"):
        assert board.claim(agent) == "task-9"
        stamp(root / "claimed" / f"task-9.{agent}", t)
        events.append((t, agent, "claims task-9, then dies"))
        t += 1200
        (task_id, holder, attempts, state), = reclaim_stale(root, t)
        events.append((t, "sweeper", f"reclaims {task_id} from {holder}: attempt {attempts}, to {state}/"))
        t += 10
    left = board.claim("agent-f")
    events.append((t, "agent-f", f"claim returns {left}: nothing left to take"))
    return events, sorted(p.name for p in (root / "quarantine").iterdir())


def simulate():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        once = at_least_once(Path(a))
        stuck = quarantine(Path(b))
    return once, stuck


def main():
    (events, counts, final), (q_events, quarantined) = simulate()
    print(f"lease {LEASE_S} s, quarantine after {MAX_ATTEMPTS} reclaims; times are simulated seconds")
    print("at-least-once:")
    for t, who, what in events:
        print(f"  t={t:>5}  {who:<8} {what}")
    print(f"  board: {counts}; settings.toml: {final!r}")
    print("quarantine:")
    for t, who, what in q_events:
        print(f"  t={t:>5}  {who:<8} {what}")
    print(f"  quarantine/: {quarantined}")


if __name__ == "__main__":
    main()
