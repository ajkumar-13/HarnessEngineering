"""Post 03, section 9: four scripted traces and the turn on which each no-progress detector stops them.

Run from the series root:  uv run python posts/03-the-agent-loop/diagrams/src/04-no-progress.py
Writes posts/03-the-agent-loop/diagrams/04-no-progress.svg.
The traces, the three detectors and the firing turns all come from snippets/no_progress.py (first_fire over
TRACES and DETECTORS), asserted against the table the post quotes. A turn-by-turn picture is a row of turns
(hrn_fig_design.md section 1); each cell is the turn's observation, a tool result, so it is act-coloured. Where a
detector fires, its mark goes under that turn: gate-coloured when stopping is right (the doom loop), red when it
stops a run that was making progress.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
from no_progress import DETECTORS, TRACES, first_fire  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
FIRES = {name: [first_fire(trace, f, w) for _, f, w in DETECTORS] for name, trace in TRACES.items()}
assert FIRES == {"doom loop": [3, 3, 3], "build poll": [3, None, None], "long build": [3, 3, None],
                 "healthy edits": [None, None, None]}
for line in ("doom loop                    turn 3              turn 3              turn 3",
             "build poll                   turn 3               never               never",
             "long build                   turn 3              turn 3               never",
             "healthy edits                 never               never               never"):
    assert line in BODY, line

SHAPES = ["square", "circle", "diamond"]
LABELS = ["calls only (companion)", "+ observation", "+ window 6, polling"]

fig = Figure(
    "04-no-progress", "Only the doom loop should stop",
    "Four scripted traces as rows of turns, each cell the turn's observation. Doom loop, run_tests, returns 1 failed "
    "five times. Build poll, build_status, returns running, running, passed, then run_tests returns all passed. Long "
    "build, build_status, returns running five times, then passed. Healthy edits, edit_file on a new line each turn, "
    "returns ok five times. Marks under turn 3 show where each detector fires, window 3 unless noted: the "
    "calls-only fingerprint, a square, stops the doom loop, the build poll and the long build; with the observation "
    "folded in, a circle, the doom loop and the long build; with a window of 6 for build_status, a diamond, only the "
    "doom loop. Stopping the doom loop is drawn in the gate colour; the other stops are false positives, in red. "
    "No detector stops the healthy edits.",
    subtitle="Where each no-progress detector fires, window 3 unless noted; traces from snippets/no_progress.py.",
    data_w=True)

LX, CX, CW, CH, CS = 40, 184, 80, 40, 84          # label column, first cell, cell width and height, cell step
ROW0, RS = 136, 84                                 # first row top, row step
for t in range(1, 7):
    fig.text(CX + (t - 1) * CS + CW // 2, ROW0 - 12, f"turn {t}", "tick", anchor="middle")
CALL = {"doom loop": "run_tests", "build poll": "build_status", "long build": "build_status",
        "healthy edits": "edit_file"}
for r, (name, trace) in enumerate(TRACES.items()):
    y = ROW0 + r * RS
    fig.text(LX, y + 16, name, "label", bold=True)
    fig.text(LX, y + 36, CALL[name], "code")
    for t, (calls, obs) in enumerate(trace, start=1):
        x = CX + (t - 1) * CS
        fig.card(x, y, CW, CH, radius=4, color="act")
        fig.text(x + CW // 2, y + 25, obs, "label", anchor="middle")
    for k, turn in enumerate(FIRES[name]):
        if turn:
            x = CX + (turn - 1) * CS + CW // 2 + (k - 1) * 20
            fig.marker(x, y + CH + 16, SHAPES[k], "gate" if name == "doom loop" else "red", size=12)

LEG = 708
fig.text(LEG, ROW0 + 4, "detector", "head")
fig.legend(LEG, ROW0 + 32, [dict(color="ink", label=lab, mark=shape) for shape, lab in zip(SHAPES, LABELS)])
fig.text(LEG, ROW0 + 132, "the stop", "head")
fig.legend(LEG, ROW0 + 160, [dict(color="gate", label="right: a doom loop"),
                             dict(color="red", label="wrong: progress stopped")])
assert TRACES["build poll"][-1][0][0].name == "run_tests" and TRACES["build poll"][-1][1] == "all passed"
fig.caption("Folding in the result spares a build that changes; a wider window spares one that takes its time.")
fig.write()
