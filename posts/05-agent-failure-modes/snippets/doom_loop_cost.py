"""Post 05, section 3: what one doom loop costs with and without the no-progress exit.

Run from the series root:  uv run python posts/05-agent-failure-modes/snippets/doom_loop_cost.py

The loop is the companion's own, run() from code/03-agent-loop/src/agent_loop/loop.py, imported unchanged.
The model is scripted: its transcript grows by an illustrative 4,000 tokens a turn (one response plus one
tool result) and is re-read on every call, so turn k reads 4,000 x k input tokens. It reads a file, runs the
tests, makes an edit, and from turn 4 runs the same failing tests on every turn. Standard library only.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "03-agent-loop" / "src"))
from agent_loop import ScriptedModel, Tool, run, tool_response  # noqa: E402

PER_TURN = 4_000          # illustrative tokens added to the transcript per turn
FIRST_REPEAT = 4          # from this turn on, every call is the same
OPENING = [("read_file", {"path": "app.py"}), ("run_tests", {}),
           ("edit_file", {"path": "app.py", "patch": "guard the empty list"})]
TOOLS = [Tool("read_file", "read a file", lambda a: "def total(xs): ..."),
         Tool("run_tests", "run the test suite", lambda a: "1 failed, 11 passed"),
         Tool("edit_file", "apply a patch", lambda a: "patched app.py")]


def stuck_model(turns):
    script = []
    for k in range(1, turns + 1):
        name, args = OPENING[k - 1] if k < FIRST_REPEAT else ("run_tests", {})
        script.append(tool_response(name, args, id=f"tu_{k}", tokens=PER_TURN * k))
    return ScriptedModel(script)


def stuck_run(cap, window):
    """window=None switches the no-progress exit off: a window longer than the cap never fills."""
    return run(stuck_model(cap), TOOLS, "Fix the failing test.", max_iters=cap,
               no_progress_window=window or cap + 1)


def closed_form(n):
    return PER_TURN * n * (n + 1) // 2        # 4,000 x (1 + 2 + ... + n) = 2,000 n (n + 1)


rows = [("no-progress window of 3, cap of 12", stuck_run(12, 3)),
        ("cap of 12 only (the default)", stuck_run(12, None)),
        ("cap of 40 only", stuck_run(40, None))]
for _, r in rows:
    assert r.tokens_used == closed_form(r.iterations)

print(f"{'exits enabled':38} {'stop reason':>12} {'turn':>5} {'input tokens':>13}")
for label, r in rows:
    print(f"{label:38} {r.stop_reason.value:>12} {r.iterations:>5} {r.tokens_used:>13,}")
base = rows[0][1].tokens_used
print(f"cap of 12 / no progress: {rows[1][1].tokens_used / base:.2f} times")
print(f"cap of 40 / no progress: {rows[2][1].tokens_used / base:.2f} times")
