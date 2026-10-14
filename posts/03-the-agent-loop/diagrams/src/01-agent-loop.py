"""Post 03, the hero: the reason, act, observe cycle and the four exits the stop check leads to.

Run from the series root:  uv run python posts/03-the-agent-loop/diagrams/src/01-agent-loop.py
Writes posts/03-the-agent-loop/diagrams/01-agent-loop.svg.
This is the series' reference drawing of the loop (hrn_fig_design.md section 1): reason (model, blue), act (act,
orange), observe (state, green), clockwise, and the exits leaving as gate-coloured arrows labelled with what fires
them. The stop check sits where the companion checks it, after each model call and before the tools run. The
companion's settings are read from code/03-agent-loop (the defaults of run() and the StopReason values) and
asserted; the exit names and conditions are section 7's and the notation guide's, asserted against the body.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "03-agent-loop" / "src"))
from figkit import Figure  # noqa: E402
from agent_loop import StopReason, run  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
DEFAULTS = {k: v.default for k, v in inspect.signature(run).parameters.items() if v.default is not inspect._empty}
assert DEFAULTS["max_iters"] == 12 and DEFAULTS["token_budget"] is None and DEFAULTS["no_progress_window"] == 3
assert [s.value for s in StopReason] == ["completed", "max_iters", "budget", "no_progress"]

# exit heading, what fires it (section 7), the companion's setting, phrases the body must contain
EXITS = [
    ("(1) final answer", "terminal stop_reason, no tool call", "completed",
     "**(1) Final answer: the exit the loop is for.**"),
    ("(2) iteration cap", "turns reach the cap", f"max_iters={DEFAULTS['max_iters']}", "**(2) Iteration cap.**"),
    ("(3) budget", "tokens or seconds reach the ceiling", f"token_budget={DEFAULTS['token_budget']}",
     "**(3) Budget.** A ceiling in tokens or wall-clock seconds"),
    ("(4) no progress", "the same calls 3 turns running", f"no_progress_window={DEFAULTS['no_progress_window']}",
     "**(4) No progress.**"),
]
for *_, phrase in EXITS:
    assert phrase in BODY, phrase
assert "The companion's window is 3" in BODY and "The companion's default of 12 is a demo number" in BODY

fig = Figure(
    "01-agent-loop", "The loop is three steps; the engineering is in four exits",
    "The agent loop as a clockwise cycle of three cards: reason, the model call, in blue; act, run the tools, in "
    "orange; observe, append the results, in green; an arrow from observe back to reason carries the next call with "
    "the whole history. Between reason and act a purple diamond, the stop check, runs after every model call and "
    "leads to four purple exit cards, in order: (1) final answer, a terminal stop_reason and no tool call, "
    "completed in the companion; (2) iteration cap, turns reach the cap, max_iters=12; (3) budget, tokens or "
    "seconds reach the ceiling, token_budget=None, so off by default; (4) no progress, the same calls 3 turns "
    "running, no_progress_window=3. When no exit fires the run goes on to act.",
    subtitle="After every model call the harness checks exits (1), (3) and (4); the cap (2) fires as the turns run out.",
    data_w=True)

W, H = 176, 84
REASON = (48, 112)
ACT = (304, 352)
OBSERVE = (48, 352)
GX, GY = ACT[0] + W // 2, REASON[1] + H // 2          # the stop check: on the reason row, above act
for (x, y), name, what, role in [(REASON, "reason", "the model call", "model"),
                                 (ACT, "act", "run the tools", "act"),
                                 (OBSERVE, "observe", "append the results", "state")]:
    fig.card(x, y, W, H, heading=name, lines=[what], style="note", color=role)

# the cycle, clockwise: reason -> stop check -> act -> observe -> reason
fig.arrow((REASON[0] + W, GY), (GX - 16, GY), label="response")
fig.arrow((GX, GY + 16), (GX, ACT[1]), label="no exit fired")
fig.arrow((ACT[0], ACT[1] + H // 2), (OBSERVE[0] + W, ACT[1] + H // 2), label="results")
fig.arrow((OBSERVE[0] + H, OBSERVE[1]), (OBSERVE[0] + H, REASON[1] + H), label="next call, whole history")
fig.marker(GX, GY, "diamond", "gate", size=24)
fig.text(GX, GY - 24, "stop check", "label", anchor="middle", color="gate")

# the exits: a gate-coloured bus from the stop check to four cards, checked top to bottom
CX, CW, CH, BUS = 592, 328, 84, 560
ys = [112 + k * (CH + 8) for k in range(4)]
fig.edge((GX + 16, GY), (BUS, GY), color="gate", width=1.5)
fig.edge((BUS, GY), (BUS, ys[-1] + CH // 2), color="gate", width=1.5)
for y, (head, fires, setting, _) in zip(ys, EXITS):
    fig.arrow((BUS, y + CH // 2), (CX, y + CH // 2), color="gate")
    fig.card(CX, y, CW, CH, heading=head, lines=[fires], style="note", color="gate")
    fig.text(CX + CW - 16, y + 32, setting, "code", anchor="end")

assert "only the first of them means the work may be done" in BODY
fig.caption("Only exit (1) can mean the work is done, and verification still has to confirm it.")
fig.write()
