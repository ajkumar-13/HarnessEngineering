"""Post 19, section 7: an inner verify loop inside an outer task loop, one budget shared, outcomes reported up.

Run from the series root:  uv run python posts/19-loop-engineering/diagrams/src/02-nested-loops.py
Writes posts/19-loop-engineering/diagrams/02-nested-loops.svg.
A section 3 form of hrn_fig_design.md: the outer task loop of post 18 as a neutral frame, the inner verify loop of
post 11 as a frame inside it, generation blue (model), the verification gate and the outcome check purple (gate),
the failure report re-entering red (error), the commit green (state). The inner loop reports an outcome, not its
activity; three unverified outcomes in a row are the outer loop's exit (4). The attempt cap is read from post 11's
companion and asserted; the wording is asserted against the body.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "11-verification-loop" / "src"))
from figkit import Box, Figure  # noqa: E402
from verification_loop import solve  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
CAP = inspect.signature(solve).parameters["max_attempts"].default
assert CAP == 5 and "an attempt cap, five by default in post 11's companion" in BODY
for phrase in ["three tasks in a row ending unverified is a stalled run",
               "The outer detector must watch the inner loop's **outcome**, not its activity",
               "| (3) budget | a per-task share, or a draw against a shared pool | the run ceiling"]:
    assert phrase in BODY, phrase

fig = Figure(
    "02-nested-loops", "The inner loop gets a step right; the outer advances",
    "An outer task loop, post 18's, drawn as a frame: pick the next task, run the inner loop, check its outcome, "
    "and either commit and advance or count the task as unverified, then take the next task in a fresh context. "
    "Inside it, the inner verify loop of post 11: generate a candidate in blue, verify it at a purple gate, and on "
    f"a failure send the report back in red; it reports an outcome after a pass or after {CAP} attempts. Three "
    "unverified outcomes in a row are exit (4) for the outer loop. Below, one run budget feeds both loops: a fixed "
    "share per task, or a shared pool with a per-task cap.",
    subtitle=f"The inner loop reports an outcome, after a pass or {CAP} attempts; the outer loop reads only that.",
    data_w=True)

# the outer frame and its return path
OUT = Box(40, 128, 880, 272)
fig.outline(OUT, "rule", width=1.5, radius=8)
fig.text(40, 116, "outer task loop, one task per pass (post 18)", "head")
PICK = (64, 224, 136, 72)
fig.card(*PICK, heading="pick", lines=["the next task"], style="note")

# the inner frame: generate, verify, report fed back
INN = Box(232, 176, 392, 192)
fig.outline(INN, "gate-line", width=1.5, radius=8)
fig.text(248, 200, "inner verify loop (post 11)", "note")
GEN = (256, 224, 136, 72)
fig.card(*GEN, heading="generate", lines=["a candidate"], style="note", color="model")
VX, VY = 480, 260
fig.arrow((GEN[0] + GEN[2], VY), (VX - 16, VY))
fig.marker(VX, VY, "diamond", "gate", size=24)
fig.text(VX, VY - 24, "verify", "label", anchor="middle", color="gate")
fig.edge((VX, VY + 16), (VX, 336), color="error", width=1.5)
fig.edge((VX, 336), (GEN[0] + GEN[2] // 2, 336), color="error", width=1.5)
fig.arrow((GEN[0] + GEN[2] // 2, 336), (GEN[0] + GEN[2] // 2, GEN[1] + GEN[3]), color="error")
fig.text(VX - 12, 356, "fail: the report goes back", "note", anchor="end", color="error")

# the outcome, checked by the outer loop
OX, OY = 672, VY
fig.arrow((VX + 16, VY), (OX - 16, VY), label="outcome")
fig.marker(OX, OY, "diamond", "gate", size=24)
COMMIT = (720, 176, 176, 72)
UNV = (720, 300, 176, 72)
fig.card(*COMMIT, heading="verified", lines=["commit, advance"], style="note", color="state")
fig.card(*UNV, heading="unverified", lines=["3 in a row: exit (4)"], style="note", color="error")
fig.edge((OX, OY - 16), (OX, COMMIT[1] + COMMIT[3] // 2), color="gate", width=1.5)
fig.arrow((OX, COMMIT[1] + COMMIT[3] // 2), (COMMIT[0], COMMIT[1] + COMMIT[3] // 2), color="gate")
fig.edge((OX, OY + 16), (OX, UNV[1] + UNV[3] // 2), color="gate", width=1.5)
fig.arrow((OX, UNV[1] + UNV[3] // 2), (UNV[0], UNV[1] + UNV[3] // 2), color="gate")
fig.arrow((PICK[0] + PICK[2], VY), (GEN[0], VY))

# either outcome, the outer loop takes the next task in a fresh context
RX, RY = 908, 160
for card in (COMMIT, UNV):
    fig.edge((card[0] + card[2], card[1] + card[3] // 2), (RX, card[1] + card[3] // 2), color="arrow", width=1.5)
fig.edge((RX, UNV[1] + UNV[3] // 2), (RX, RY), color="arrow", width=1.5)
fig.edge((RX, RY), (PICK[0] + PICK[2] // 2, RY), color="arrow", width=1.5)
fig.arrow((PICK[0] + PICK[2] // 2, RY), (PICK[0] + PICK[2] // 2, PICK[1]))
fig.text(456, RY - 8, "next task, fresh context", "note", anchor="middle")

# the run budget both loops draw on
BUD = Box(40, 424, 880, 40)
fig.fill(BUD, "neutral-soft", radius=8)
fig.outline(BUD, "border", width=1, radius=8)
fig.text(56, 450, "one run budget, exit (3) for both: a fixed share per task, or a shared pool with a per-task cap",
         "label")

fig.caption("Busy retries change the state on every pass; only the outcome tells the outer loop whether it moved.")
fig.write()
