"""Post 05, section 6: five archived runs drawn turn by turn, and the mode each one's shape names.

Run from the series root:  uv run python posts/05-agent-failure-modes/diagrams/src/03-trace-signatures.py
Writes posts/05-agent-failure-modes/diagrams/03-trace-signatures.svg.
Every run, turn, tool call, result, stop reason and check verdict comes from snippets/trace_fingerprint.py,
imported (it builds its archive by running the companion loop of code/03-agent-loop/); the mode named on each
row is the snippet's own hit list. Turn-by-turn form of hrn_fig_design.md section 1: a tool call is an act chip
(orange), the final answer a model chip (blue), a failing turn red, a result returned green, the exit purple.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure, text_width  # noqa: E402
import trace_fingerprint as tf  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
RUNS = {r["name"]: r for r in tf.runs}
ROWS = [("run-02", "victory declaration"), ("run-07", "one-shotting"), ("run-04", "doom loop"),
        ("run-05", None), ("run-06", "destructive action")]
for name, mode in ROWS:
    if mode:
        assert name in tf.hits[mode], (name, mode)
assert tf.polls == {"run-05"} and "run-07" in tf.hits["victory declaration"]
for phrase in ("three identical `build_status` calls whose results changed from `queued` to `running`",
               "Run-06 passed its check and is still the incident", "Run-07 is both one-shotting and victory"):
    assert phrase in BODY, phrase


def chips(run):
    """(label, colour) per turn, then the final answer if the run gave one."""
    trace = tf.turns(run["transcript"])
    doom = {j for i in tf.doom_loop_turns(trace) if not tf.results_changed(trace, i)
            for j in range(i - 2, i + 1)}
    out = []
    for k, t in enumerate(trace):
        u = t["tool_uses"][0]
        if u.name == "bash":
            label = u.input["cmd"]
        elif u.name == "edit_file":
            label = f"edit, {u.input['lines']} lines"
        else:
            label = u.name
        bad = (k in doom or tf.DENY.search(label) is not None
               or (u.name == "edit_file" and run["name"] in tf.hits["one-shotting"]))
        if not t["results"]:
            result = ("not run", None)          # exit (4) fired before this call executed
        elif u.name == "build_status":
            result = (t["results"][0], "state")
        else:
            result = None
        out.append((label, "error" if bad else "act", result))
    if run["stop_reason"] is tf.StopReason.COMPLETED:
        out.append(("final answer", "model", None))
    return out


fig = Figure(
    "03-trace-signatures", "The shape of a run names the mode",
    "Five runs from the post's archive, one row each, turns left to right as chips. Victory declaration, run-02: "
    "read_file, then a final answer; the run ends completed and its check fails. One-shotting, run-07: read_file, "
    "one edit of 412 lines in red, a final answer; completed, check failed. Doom loop, run-04: read_file, then "
    "run_tests three times in red; stopped as no_progress. A poll, not a doom loop, run-05: make ci, then "
    "build_status three times with results queued and running, the third not run; stopped as no_progress all the same. Destructive "
    "action, run-06: read_file, rm -rf build/ in red, run_tests, a final answer; completed, check passed.",
    subtitle="Archive of snippets/trace_fingerprint.py, run through the companion loop of post 03.",
    data_w=True)

LEFT, CHIP0, EXIT_X = 40, 216, 760
ROW_H, TOP = 68, 112
for r, (name, mode) in enumerate(ROWS):
    run = RUNS[name]
    y = TOP + r * ROW_H
    fig.text(LEFT, y + 20, mode or "a poll, not a doom loop", "label", bold=True,
             color="error" if mode else None)
    fig.text(LEFT, y + 40, name, "note")
    x = CHIP0
    for label, color, result in chips(run):
        code = color != "model"
        w = max(96, int(text_width(label, 14, mono=code) + 24 + 7) // 8 * 8)
        fig.card(x, y + 4, w, 32, color=color, radius=4)
        fig.text(x + w / 2, y + 24, label, "code" if code else "label", anchor="middle", snap=False)
        if result:
            fig.text(x + w / 2, y + 56, result[0], "note", anchor="middle", color=result[1], snap=False)
        x += w + 8
    assert x <= EXIT_X - 8, (name, x)
    fig.text(EXIT_X, y + 24, run["stop_reason"].value, "code", color="gate")
    ok = run["checked_ok"]
    fig.text(EXIT_X, y + 44, "check passed" if ok else "check failed", "note",
             color=None if ok else "error")

fig.legend(LEFT, 472, [dict(color="act", label="tool call", mark="outline"),
                       dict(color="model", label="final answer", mark="outline"),
                       dict(color="error", label="the failing turn", mark="outline"),
                       dict(color="state", label="result returned", mark="square"),
                       dict(color="gate", label="exit that fired", mark="square")], direction="row")
fig.caption("Of three completed runs, two failed their check and one ran rm -rf; a healthy poll stopped on no progress.")
fig.write()
