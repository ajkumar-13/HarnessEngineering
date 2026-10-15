"""Post 14, section 5: four calls through four gates, the gate that decided each, and the tag the trace keeps.

Run from the series root:  uv run python posts/14-permissions-sandboxes/diagrams/src/03-which-gate-fired.py
Writes posts/14-permissions-sandboxes/diagrams/03-which-gate-fired.svg.
A section 4 trace of hrn_fig_design.md, one row per call: the gates are columns (purple headings), a gate the
call passed is a neutral cell with what it said, the gate that stopped it is a red cell, gates after it are
empty. Every cell is computed by running snippets/gate_outcomes.py (run(), decide() and naive_tag()) and the rows
are asserted against the output the post quotes.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
from gate_outcomes import CALLS, decide, naive_tag, run  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
RESULTS = run()
GATES = ["hook", "permission", "approver", "sandbox"]
STOP_WORD = {"hook": "blocked", "approver": "said no", "permission": "deny", "sandbox": "refused"}
rows = []
for (role, _, _), (tool, args, outcome, gate, _) in zip(CALLS, RESULTS):
    shown = args.get("command") or args.get("target")
    line = f"{tool + ' ' + shown:<36} {gate:<11} {outcome:<8} {naive_tag(outcome)}"
    assert line in BODY, line
    verdict = decide(role, tool, args)
    cells = []
    for g in GATES:
        if gate == g:
            cells.append(("stop", STOP_WORD[g]))
        elif cells and cells[-1][0] in ("stop", "none"):
            cells.append(("none", ""))
        elif g == "permission":
            cells.append(("pass", verdict))
        elif g == "approver":
            cells.append(("pass", "not asked") if verdict == "allow" else ("pass", "said yes"))
        else:
            cells.append(("pass", "passed"))
    rows.append((tool, shown, cells, outcome, naive_tag(outcome)))
assert [r[3] for r in rows] == ["blocked", "denied", "refused", "ok"]
assert [r[4] for r in rows] == ["blocked", "denied", "ok", "ok"]

fig = Figure(
    "03-which-gate-fired", "Each gate leaves its own word in the trace",
    "Four calls as rows across four purple gate columns, hook, permission, approver and sandbox, then the outcome "
    "and the naive tag. bash rm -rf ~ is stopped at the hook: blocked, tagged blocked. deploy production passes "
    "the hook, gets ask from the permission table, and the approver says no: denied, tagged denied. bash git "
    "status ../work-private passes the hook, is allowed, needs no approver, and the sandbox refuses it: refused, "
    "but the naive tag, in red, is ok. bash git status --short passes every gate: ok, tagged ok.",
    subtitle="Four calls from gate_outcomes.py; a red cell is the gate that stopped the call.",
    data_w=True)

XS, W = [296, 408, 520, 632], 96
OUT_X, NAIVE_X = 760, 856
YS, H = [160, 232, 304, 376], 56
for x, g in zip(XS, GATES):
    fig.text(x, 136, g, "label", color="gate", bold=True)
fig.text(OUT_X, 136, "outcome", "label", bold=True)
fig.text(NAIVE_X, 136, "naive tag", "label", bold=True)

for y, (tool, shown, cells, outcome, naive) in zip(YS, rows):
    fig.text(40, y + 22, tool, "label", bold=True)
    fig.text(40, y + 44, shown, "code")
    for x, (kind, word) in zip(XS, cells):
        if kind == "none":
            continue
        stop = kind == "stop"
        fig.card(x, y, W, H, color="error" if stop else None)
        fig.text(x + 12, y + 33, word, "label" if stop else "note", color="error" if stop else None)
    fig.text(OUT_X, y + 33, outcome, "label", bold=True)
    wrong = naive != outcome
    fig.text(NAIVE_X, y + 33, naive, "label", bold=wrong, color="error" if wrong else None)

fig.caption("The naive tag files the sandbox's refusal as ok, the same word as a call that ran.")
fig.write()
