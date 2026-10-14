"""Post 06, section 5: five commands at the companion's deny-list, and the boundary that has to hold behind it.

Run from the series root:  uv run python posts/06-tools-bash-code/diagrams/src/02-deny-list-spellings.py
Writes posts/06-tools-bash-code/diagrams/02-deny-list-spellings.svg.
A section 3 boundary form of hrn_fig_design.md: the deny-list is a gate (purple) on the path to the runner (act,
orange); the blocked call is a red stub ending at the gate with the word "blocked"; the operating-system boundary
of post 14 is a gate-coloured frame around the runner, dashed because this companion does not build it. The
verdicts are computed here with the companion's make_bash_tool() and its shipped DENY list and a runner that
records and runs nothing (as snippets/deny_list_bypass.py does), and asserted against the post's quoted output.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "06-tools-and-bash" / "src"))
from figkit import Box, Figure  # noqa: E402
from tools import DENY, make_bash_tool  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
reached = []
bash = make_bash_tool(lambda command, timeout: (reached.append(command), ("", 0))[1])
SPELLINGS = ["rm -rf /", "rm --recursive --force /", "find / -delete",
             "python -c \"import shutil; shutil.rmtree('/')\"", "echo hi; curl http://evil"]
BLOCKED = [bash.run({"command": c}).startswith("blocked:") for c in SPELLINGS]
assert BLOCKED == [True, False, False, False, False] and reached == SPELLINGS[1:]
for c, b in zip(SPELLINGS, BLOCKED):
    assert f"{'blocked' if b else 'passes to the runner':22} {c}" in BODY, c
assert f"deny-list patterns shipped: {len(DENY)}" in BODY and len(DENY) == 12
assert "a working-directory jail, an allow-list, no network egress, a timeout" in BODY

fig = Figure(
    "02-deny-list-spellings", "A deny-list stops one spelling of a deletion",
    "Five commands on the left meet a purple gate, the companion's deny-list of 12 regular expressions. rm -rf "
    "/ ends at the gate in a red stub marked blocked. The other four, rm --recursive --force /, find / -delete, "
    "python -c \"import shutil; shutil.rmtree('/')\" and echo hi; curl http://evil, pass the gate and reach the "
    "orange runner. The runner sits inside a dashed purple frame, the operating-system boundary built in post 14 and not in this companion: a "
    "working-directory jail, an allow-list, no network egress and a timeout. 4 of the 5 commands pass.",
    subtitle="Five commands against the companion's 12 patterns; the runner records what reaches it and runs nothing.",
    data_w=True)

ROW0, STEP, CMD_END, GATE = 152, 64, 432, 480
rows = [ROW0 + k * STEP for k in range(len(SPELLINGS))]
fig.text(40, 120, "five commands", "note")
for y, c in zip(rows, SPELLINGS):
    fig.text(40, y + 5, c, "code")

# the gate: the deny-list
fig.fill(Box(GATE - 4, 136, 8, rows[-1] - 120), "gate")
fig.text(GATE, 120, "deny-list, 12 patterns", "label", anchor="middle", color="gate")

# the boundary that holds, around the runner
FRAME = Box(640, 136, 280, 288)
fig.outline(FRAME, "gate", width=1.5, dash="proj", radius=8)
fig.text(FRAME.x + 16, FRAME.y + 28, "operating-system boundary", "label", color="gate")
fig.text(FRAME.x + 16, FRAME.y + 52, "built in post 14, not here", "note")
RUN = Box(688, 264, 184, 80)
fig.card(RUN.x, RUN.y, RUN.w, RUN.h, heading="runner", lines=["records, runs nothing"], style="note", color="act")
fig.text(FRAME.x + 16, FRAME.y + FRAME.h - 20, "jail, allow-list, no egress, timeout", "note")

ends = iter(RUN.y + 16 + 16 * k for k in range(4))
for y, c, blocked in zip(rows, SPELLINGS, BLOCKED):
    if blocked:
        fig.arrow((CMD_END, y), (GATE - 4, y), color="error")
        fig.text(GATE + 16, y + 5, "blocked", "label", color="error")
    else:
        fig.arrow((CMD_END, y), (RUN.x, next(ends)), color="act")

fig.note(Box(40, rows[-1], 400, 8), [f"{sum(BLOCKED)} of {len(SPELLINGS)} blocked: the patterns match spellings, not effects"])
fig.caption("The deny-list is a first filter and an audit line; the frame around the runner is what holds.")
fig.write()
