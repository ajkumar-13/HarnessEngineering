"""Post 13, section 2: the lab run drawn turn by turn, a block before the act and a report after it.

Run from the series root:  uv run python posts/13-hooks-enforcement/diagrams/src/02-block-vs-report.py
Writes posts/13-hooks-enforcement/diagrams/02-block-vs-report.svg.
Every outcome is computed here by running snippets/block_vs_report.py's own functions (imported) in a temporary
directory: the gate's reason, the executor's call count, whether the marker file survived, the post-edit report and
whether the broken edit stayed on disk. Turn-by-turn form of hrn_fig_design.md section 1: the model's proposal
blue, the act orange, the pre-tool hook a purple gate, the post-edit hook a neutral card (it reports, as in the
hero), what persists green, the block and the failure red.
"""
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import block_vs_report as lab  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")

with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    guarded = lab.HookRegistry().add_pre_tool(lab.deny_list()).add_pre_tool(lab.deny_list(lab.ADDED_RULE))
    reason, kept, calls = lab.pre_tool(cwd, guarded)
    reports = lab.HookRegistry().add_post_edit(lab.post_edit_tests(lab.run_tests(cwd)))
    broken = "def add(a, b):\n    return a - b\n"
    (cwd / "calc.py").write_text(broken, encoding="utf-8")
    problems = reports.after_edit("calc.py", broken)
    stays = (cwd / "calc.py").read_text(encoding="utf-8") == broken

assert reason == "blocked: recursive delete of the workspace" and calls == 0 and kept
assert len(problems) == 1 and problems[0].endswith("AssertionError: add(2, 2) != 4") and stays
for line in (f"'rm -rf workspace' -> {reason}", f"executor calls: {calls}; marker file exists afterwards: {kept}",
             f"report: {problems[0]}", f"the broken edit is still on disk: {stays}"):
    assert line in BODY, line
ERROR = problems[0].rsplit(": ", 2)[-2] + ": " + problems[0].rsplit(": ", 1)[-1]   # AssertionError: add(2, 2) != 4

fig = Figure(
    "02-block-vs-report", "A block lands before the act; a report lands after it",
    "Two runs from snippets/block_vs_report.py, turns left to right, with a dashed line marking the act. Top, "
    "pre-tool: the model proposes rm -rf workspace; the purple pre-tool hook blocks it, recursive delete of the "
    "workspace; the executor, drawn dashed, is never called, 0 calls; marker.txt still exists. Bottom, post-edit: "
    "the model proposes an edit to calc.py; nothing stands in front of it; act writes calc.py and it stays; the "
    "post-edit hook runs the tests and reports AssertionError: add(2, 2) != 4.",
    subtitle="Computed by running snippets/block_vs_report.py with the hooks of code/13-hooks.",
    data_w=True)

XS, CW, CH = [128, 328, 528, 728], 176, 84
ACT_LINE = 512
ROWS = (152, 312)
fig.edge((ACT_LINE, 120), (ACT_LINE, 448), color="rule", dash="proj")
fig.text(ACT_LINE + 8, 132, "the act", "note")

# row 1: pre-tool, the block
y = ROWS[0]
fig.text(40, y + 36, "pre-tool", "label", bold=True)
fig.card(XS[0], y, CW, CH, heading="model proposes", color="model")
fig.text(XS[0] + 16, y + 64, lab.COMMAND, "code")
fig.card(XS[1], y, CW - 16, CH, heading="pre-tool hook", color="gate")
fig.text(XS[1] + 16, y + 64, "blocked", "label", color="error", bold=True)
fig.outline(Box(XS[2], y, CW, CH), "act", width=1.5, dash="proj", radius=8)
fig.text(XS[2] + 16, y + 32, "executor", "head")
fig.text(XS[2] + 16, y + 64, f"calls: {calls}", "note")
fig.card(XS[3], y, CW, CH, heading="marker.txt", color="state")
fig.text(XS[3] + 16, y + 64, "still exists" if kept else "deleted", "label")
fig.arrow((XS[0] + CW, y + 42), (XS[1], y + 42))
fig.note(Box(XS[0], y, 384, CH), [reason])

# row 2: post-edit, the report
y, CH2 = ROWS[1], 108
fig.text(40, y + 36, "post-edit", "label", bold=True)
fig.card(XS[0], y, CW, CH, heading="model proposes", color="model")
fig.text(XS[0] + 16, y + 64, "edit calc.py", "label")
fig.arrow((XS[0] + CW, y + 42), (XS[2], y + 42), label="nothing in front")
fig.card(XS[2], y, CW, CH2, heading="act", lines=["calc.py written", "and it stays" if stays else "and undone"],
         color="act")
fig.card(XS[3], y, CW, CH2, heading="post-edit hook", lines=["runs the tests", "reports"])
fig.arrow((XS[2] + CW, y + 42), (XS[3], y + 42))
fig.text(XS[3] + CW, y + CH2 + 28, ERROR, "note", anchor="end", color="error")

fig.caption("Only the hook in front of the act can keep it from happening; the one after can only say it did.")
fig.write()
