"""Post 12, hero: three roles, what each reads, writes and never sees, and the evaluator's read-only registry.

Run from the series root:  uv run python posts/12-planner-generator-evaluator/diagrams/src/01-three-roles.py
Writes posts/12-planner-generator-evaluator/diagrams/01-three-roles.svg.
A section 3 form of hrn_fig_design.md: the planner's output is the model's (blue), the generator acts on the
repository (act, orange), the contract persists across attempts (state, green), the evaluator is a gate (purple)
inside a gate-coloured frame, its registry, and the NEEDS_WORK report that goes back is red. The reads, writes
and never-sees lines are the table of section 2, asserted against the body; the contract's counts (six criteria,
one of them judged) and the registries are snippets/three_roles.py's, asserted below.
"""
import contextlib
import io
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import three_roles as tr  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
kept, refused = tr.review(tr.plan(tr.TASK))
assert len(kept) == 6 and [c.number for c in kept if c.check is None] == [6]
probe = tr.Tools("evaluator", {"parse.py": ""}, {"read_file"})
try:
    probe.call("write_file", "parse.py", "x")
    raise AssertionError("the evaluator's registry accepted a write")
except PermissionError:
    pass
out = io.StringIO()
with contextlib.redirect_stdout(out):
    tr.main()
printed = out.getvalue()
assert "evaluator write_file refused: write_file is not in the evaluator's registry" in printed
m = re.search(r"files written: generator (\d+), evaluator (\d+)", printed)
GEN_W, EVAL_W = int(m.group(1)), int(m.group(2))
assert (GEN_W, EVAL_W) == (4, 0) and m.group(0) in BODY
for phrase in (
    "| Planner | The task as stated, and the repository it lands in | The plan and the numbered acceptance criteria "
    "| The work, which does not exist yet |",
    "| Generator | The plan, the contract, and the last report | The artefact, and nothing else "
    "| The evaluator's reasoning, beyond the report |",
    "| Evaluator | The contract and the finished work | PASS or NEEDS_WORK, and a report "
    "| The generator's plan of attack and chain of thought |",
):
    assert phrase in BODY, phrase

fig = Figure(
    "01-three-roles", "The grader is a separate agent that never sees the reasoning",
    "Three role cards. Top left, the planner, in blue: it reads the task and the repository, writes the plan and "
    "numbered criteria, and never sees the work, which does not exist yet. Its criteria go into a green contract "
    "card at top right: six numbered criteria agreed with the evaluator before attempt 1 and frozen, each routed "
    "to its cheapest verifier, only criterion 6 judged. Bottom left, the generator, in orange: it reads the plan, "
    "the contract and the last report, writes the artefact and nothing else, and never sees the evaluator's "
    "reasoning. Bottom right, the evaluator, in purple, inside a purple frame labelled registry: read_file only: "
    "it reads the contract and the finished work, writes PASS or NEEDS_WORK and a report, and never sees the "
    "generator's reasoning. The work crosses the frame to the evaluator; a red arrow carries NEEDS_WORK and the "
    "named failures back to the generator; PASS leads down to done. A note: in this post's run the evaluator "
    "called write_file once and was refused; files written, generator 4, evaluator 0.",
    subtitle="Each role reads, writes and never sees something different; the evaluator's registry has no write "
             "tool.",
    height=720, data_w=True)

KEY_DX, VAL_DX = 16, 120


def role(x, y, w, h, name, color, rows, note=None):
    fig.card(x, y, w, h, color=color)
    fig.text(x + 16, y + 32, name, "head", color=color)
    if note:
        fig.text(x + w - 16, y + 32, note, "note", anchor="end")
    for i, (key, value) in enumerate(rows):
        fig.text(x + KEY_DX, y + 64 + 28 * i, key, "note")
        fig.text(x + VAL_DX, y + 64 + 28 * i, value, "label")


LX, RX, CW, CH = 40, 576, 336, 144
TOP, BOT = 128, 392

role(LX, TOP, CW, CH, "planner", "model", [
    ("reads", "the task, the repository"),
    ("writes", "the plan, numbered criteria"),
    ("never sees", "the work: none exists yet")])
role(RX, TOP, 344, CH, "contract", "state", [
    ("criteria", f"{len(kept)}, frozen before attempt 1"),
    ("agreed", "by the planner and evaluator"),
    ("judged", "only criterion 6; code does the rest")])
role(LX, BOT, CW, CH, "generator", "act", [
    ("reads", "the plan, contract, last report"),
    ("writes", "the artefact, nothing else"),
    ("never sees", "the evaluator's reasoning")])

# the evaluator inside its registry
fig.outline(Box(560, 344, 360, 208), "gate", width=1.5, radius=8)
fig.text(904, 372, "registry: read_file only", "label", anchor="end", color="gate")
role(RX, BOT, 328, CH, "evaluator", "gate", [
    ("reads", "the contract, the finished work"),
    ("writes", "PASS or NEEDS_WORK, a report"),
    ("never sees", "the generator's reasoning")])

# what passes between them
fig.arrow((LX + CW, 200), (RX, 200), label="the criteria")
fig.arrow((120, TOP + CH), (120, BOT), label="the plan", side="right")
fig.arrow((608, TOP + CH), (296, BOT), via=[(608, 312), (296, 312)])
fig.text(452, 304, "the contract", "label", anchor="middle")
fig.arrow((680, TOP + CH), (680, BOT))
fig.text(692, 316, "the contract", "label")
fig.arrow((LX + CW, 440), (RX, 440), label="the work")
fig.arrow((RX, 504), (LX + CW, 504), color="error")
fig.text(468, 528, "NEEDS_WORK, report", "label", anchor="middle", color="error")

# PASS
fig.arrow((744, 552), (744, 592), label="PASS", side="right")
fig.card(RX, 592, 344, 48)
fig.text(RX + 16, 622, "done: every criterion of the contract met", "label")

# what the snippet's run showed
fig.text(LX, 592, "In this post's run the evaluator called write_file once:", "note")
fig.text(LX, 616, f"refused. Files written: generator {GEN_W}, evaluator {EVAL_W}.", "note")

fig.caption("The contract is fixed before the work, and the work crosses into a registry that can read but not write.")
fig.write()
