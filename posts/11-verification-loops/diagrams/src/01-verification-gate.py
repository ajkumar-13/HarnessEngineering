"""Post 11, the hero: a verification gate on exit (1), and the companion's three-attempt run beneath it.

Run from the series root:  uv run python posts/11-verification-loops/diagrams/src/01-verification-gate.py
Writes posts/11-verification-loops/diagrams/01-verification-gate.svg.
The loop is the compact card of hrn_fig_design.md section 1; the gate and its exits are gate (purple); the failure
report re-entering the loop is error (red); the model's candidates are model (blue). The lower half is computed:
the script runs the companion's solve() with its demo model and the demo's seven is_prime cases
(code/11-verification-loop, imported unchanged), records every verdict, and asserts the attempts, the reports and
the default cap; the three candidate expressions are asserted to be the demo's source text.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
COMPANION = POST.parents[1] / "code" / "11-verification-loop" / "src"
sys.path.insert(0, str(COMPANION))
from figkit import Figure, text_width  # noqa: E402
from verification_loop import solve  # noqa: E402
from verification_loop.__main__ import make_mock_model  # noqa: E402
from verification_loop.checks import test_cases  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
DEMO = (COMPANION / "verification_loop" / "__main__.py").read_text(encoding="utf-8")
CAP = inspect.signature(solve).parameters["max_attempts"].default
assert CAP == 5

CASES = [((1,), False), ((2,), True), ((3,), True), ((4,), False), ((9,), False), ((13,), True), ((25,), False)]
for args, expected in CASES:
    assert f"(({args[0]},), {expected})" in DEMO, args
verdicts = []
base = test_cases("is_prime", CASES)


def verify(candidate):
    result = base(candidate)
    verdicts.append(result)
    return result


sol = solve(make_mock_model(), verify, max_attempts=CAP)
assert sol.verified and sol.attempts == 3
REPORT = "is_prime(1,) == True, expected False"
assert [v.ok for v in verdicts] == [False, False, True]
assert [v.report for v in verdicts] == [REPORT, REPORT, ""]
CODE = ["all(n % d for d in range(2, n))",
        "all(n % d for d in range(2, int(n**0.5) + 1))",
        "n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))"]
for c in CODE:
    assert f"lambda n: {c}" in DEMO, c
assert "max_attempts=5" in BODY and "attempt 3 passes all 7 cases" in BODY

fig = Figure(
    "01-verification-gate", "A gate on the final answer turns done into verified",
    "Top: the loop, reason, act, observe, as one card, sends a candidate final answer, exit (1), into a purple "
    "verification gate. Pass leads to a card reading done, verified. Fail runs in red to a junction: while attempts "
    "remain, the failure report goes back into the loop as the next observation; when max_attempts=5 have failed, "
    "the run ends on a card reading unverified, flagged, rolled back or escalated. Bottom: the companion's demo, "
    "solve() over 7 is_prime cases. Attempt 1, all(n % d for d in range(2, n)), fails with is_prime(1,) == True, "
    "expected False; attempt 2, bounded by the square root, fails with the same report; attempt 3, guarded by "
    "n > 1, passes all 7 cases, verified on attempt 3.",
    subtitle=f"Below, computed: the companion's solve() on its demo model, 7 is_prime cases, max_attempts={CAP}.",
    height=720, data_w=True)

# the top half: loop card, gate, and the three ways out
LX, LY, LW, LH = 40, 120, 208, 80
CY = LY + LH // 2
GX = 432
JY = 272
fig.card(LX, LY, LW, LH, heading="the loop", lines=["reason, act, observe"], style="note")
fig.arrow((LX + LW, CY), (GX - 16, CY), label="candidate, exit (1)", side="below")
fig.marker(GX, CY, "diamond", "gate", size=24)
fig.text(GX, CY - 28, "verification gate", "label", anchor="middle", color="gate")

DX, DW = 584, 336
fig.arrow((GX + 16, CY), (DX, CY), label="pass", color="gate")
fig.card(DX, LY, DW, LH, heading="done", lines=["verified, not merely claimed"], style="note", color="gate")

fig.edge((GX, CY + 16), (GX, JY), color="error", width=1.5)
fig.text(GX + 12, CY + 52, "fail", "label", color="error")
fig.arrow((GX, JY), (DX, JY), label=f"{CAP} attempts failed", color="gate")
fig.card(DX, JY - LH // 2, DW, LH, heading="unverified", lines=["flagged, rolled back or escalated"], style="note",
         color="gate")
fig.edge((GX, JY), (LX + LW // 2, JY), color="error", width=1.5)
fig.arrow((LX + LW // 2, JY), (LX + LW // 2, LY + LH), color="error")
fig.text(LX + LW // 2 + 16, JY + 28, "attempts left: the report is the next observation", "label", color="error")

# the bottom half: the companion's run, one row per attempt
fig.text(40, 368, "The companion's run", "head")
CX, CW = 136, 528
assert max(text_width(c, 14, mono=True) for c in CODE) + 32 <= CW
for k, (code, v) in enumerate(zip(CODE, verdicts)):
    y = 384 + k * 96
    fig.text(40, y + 32, f"attempt {k + 1}", "label")
    fig.card(CX, y, CW, 52, lines=[code], style="code", color="model")
    fig.marker(CX + CW + 32, y + 26, "diamond", "gate", size=16)
    if v.ok:
        fig.text(CX + CW + 56, y + 32, f"pass: all {len(CASES)} cases", "label", color="gate")
    else:
        fig.text(CX + CW + 56, y + 32, "fail", "label", color="error")
        fig.text(CX + 16, y + 76, v.report, "code", color="error")

fig.caption("Attempt 2 changed the code and got the same report back; the report, not the code, is what repeats.")
fig.write()
