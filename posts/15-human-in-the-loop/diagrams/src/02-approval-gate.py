"""Post 15, section 8: the snippet's run, drawn as the time each call spent at the approval gate.

Run from the series root:  uv run python posts/15-human-in-the-loop/diagrams/src/02-approval-gate.py
Writes posts/15-human-in-the-loop/diagrams/02-approval-gate.svg.
A timeline in the form of hrn_fig_design.md section 4, computed: the script imports
posts/15-human-in-the-loop/snippets/async_approval.py, runs its simulate() (the companion's run() and ApprovalGate
with the queued decider), and asserts each call's outcome against the record and the result. The bar lengths are
the snippet's configured REPLY_AFTER (0.1 s) and TIMEOUT (0.5 s); each measured wait is asserted to match them
within 0.08 s, so the drawing does not depend on how fast the machine was. Roles: time at the gate purple, a call
that ran orange, a denial red.
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("async_approval", POST / "snippets" / "async_approval.py")
snippet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snippet)

record, result, workspace, deployed = snippet.simulate()
R, T = snippet.REPLY_AFTER, snippet.TIMEOUT
assert (R, T) == (0.1, 0.5)
assert result.stop_reason.value == "completed"
assert sorted(workspace.files) == ["draft.md", "notes.md"] and deployed == []

# (call, reversibility note, who decided, approved, drawn wait, outcome)
ROWS = [("read_log build.log", "not gated", None, True, 0.0, "ran")]
EXPECT = [("reviewer", True, "approved, ran"), ("reviewer", False, "denied"),
          ("timeout", True, "ran, with a note"), ("timeout", False, "denied")]
NOTES = ["reversible", "irreversible", "reversible", "irreversible"]
for r, (who, ok, outcome), note in zip(record, EXPECT, NOTES):
    assert (r["who"], r["approved"]) == (who, ok), r
    wait = R if who == "reviewer" else T
    assert abs(r["waited"] - wait) < 0.08 and (who == "reviewer") == (r["waited"] < T), r
    ROWS.append((f"{r['tool']} {snippet.target(r['args'])}", note, who, ok, wait, outcome))
assert (snippet.IRREVERSIBLE == {"deploy"}) and len(ROWS) == 5

fig = Figure(
    "02-approval-gate", "Only the flagged calls wait, never past the timeout",
    "Five calls of the snippet's run on an axis of seconds spent at the gate, from 0 to 0.5. Reading build.log is "
    "not gated and runs without waiting. Writing notes.md waits 0.1 seconds for the reviewer, who approves it, and "
    "it runs. Deploying to production waits 0.1 seconds and the reviewer denies it. Writing draft.md waits the full "
    "0.5 seconds with no answer; it is reversible, so it runs with a note. Deploying to staging waits 0.5 seconds "
    "with no answer; it is irreversible, so it is denied.",
    subtitle="Computed: the companion's gate with the snippet's queued decider; replies take 0.1 s, the timeout is 0.5 s.",
    data_w=True)

X0, PX = 304, 800            # 0 s at x = 304, 800 units per second, so 0.5 s at x = 704
Y0, DY = 144, 56
fig.text(40, 112, "call", "head")
fig.text(X0, 112, "time at the gate", "head")
fig.text(736, 112, "outcome", "head")

def x(sec):
    return X0 + PX * sec

# the timeout, behind the bars
fig.edge((x(T), 128), (x(T), 392), color="ink-muted", dash="ref")
for i, (call, note, who, ok, wait, outcome) in enumerate(ROWS):
    y = Y0 + DY * i
    fig.text(40, y, call, "code")
    fig.text(40, y + 20, note, "note")
    if wait:
        fig.fill(Box(X0, y - 16, PX * wait, 24), "gate-soft")
        fig.outline(Box(X0, y - 16, PX * wait, 24), "gate", width=1)
        fig.marker(x(wait), y - 4, "diamond", "act" if ok else "error", size=10)
        fig.text(x(wait) + 12 if wait < T else x(wait) - 8, y, who if who == "reviewer" else "no answer",
                 "note", anchor="start" if wait < T else "end")
    fig.text(736, y, outcome, "label", color="act-ink" if ok else "error-ink")

# the time axis
fig.edge((X0, 400), (x(T), 400), color="ink-muted", width=1)
for k in range(6):
    s = k / 10
    fig.edge((x(s), 400), (x(s), 404), color="ink-muted", width=1)
    fig.text(x(s), 424, "0" if k == 0 else f"{s:.1f}", "tick", anchor="middle")
fig.text((X0 + x(T)) // 2, 452, "seconds the call waited at the gate; dashed: the timeout", "note", anchor="middle")

fig.caption("On expiry the default follows the call: deny what a checkpoint cannot undo, run the rest with a note.")
fig.write()
