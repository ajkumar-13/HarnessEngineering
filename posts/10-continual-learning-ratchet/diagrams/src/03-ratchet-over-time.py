"""Post 10, section 8: the ratchet over four sessions, computed by the post's snippet.

Run from the series root:  uv run python posts/10-continual-learning-ratchet/diagrams/src/03-ratchet-over-time.py
Writes posts/10-continual-learning-ratchet/diagrams/03-ratchet-over-time.svg.
Every plotted value is computed here by calling session() from snippets/ratchet_demo.py, which runs the companion's
Ratchet and build() (code/26-coding-agent) unchanged, and is asserted against the table section 8 quotes. Values
are counts from a scripted toy (one bug per task, one rule fixes it), so they are marked "computed", not measured.
Roles: the memory file is state (green); the run without one is ink.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ratchet_demo", POST / "snippets" / "ratchet_demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

names = list(demo.TASKS)
rules_back, failed_with, failed_without = [], [], []
with tempfile.TemporaryDirectory() as d:
    rules_file = Path(d) / "AGENTS.md"
    for k in range(1, len(names) + 1):
        at_start, fw, _ = demo.session(names[:k], rules_file)
        _, fwo, _ = demo.session(names[:k])
        rules_back.append(at_start)
        failed_with.append(fw)
        failed_without.append(fwo)
assert rules_back == [0, 1, 2, 3] and failed_with == [1, 1, 1, 1] and failed_without == [1, 2, 3, 4]
for k in range(4):
    row = f"{k + 1:>7}  {k + 1:>5}  {rules_back[k]:>15}  {failed_with[k]:>21}  {failed_without[k]:>15}"
    assert row in BODY, row
assert f"failed attempts over four sessions: {sum(failed_with)} with the file, {sum(failed_without)} without" in BODY

sessions = [1, 2, 3, 4]
fig = Figure(
    "03-ratchet-over-time", "With the file, each session fails only on its new task",
    "Two panels computed by snippets/ratchet_demo.py over four sessions, each adding one task. Left, failed "
    "attempts per session: with the memory file 1, 1, 1 and 1; without it 1, 2, 3 and 4, 10 in all against 4. "
    "Right, rules read back at the start of each session with the file: 0, 1, 2 and 3, a staircase that only "
    "climbs.",
    subtitle="Computed by the post's snippet with the companion's Ratchet; a scripted toy, not a measurement.",
    data_w=True)

left, right = fig.row(2)
body = fig.panel(left, "Failed attempts per session")
fig.line_chart(
    body,
    [dict(xs=sessions, ys=failed_without, color="ink", label="without the file", shape="square"),
     dict(xs=sessions, ys=failed_with, color="state", label="with the file", shape="circle")],
    x=(1, 4, [1, 2, 3, 4]), y=(0, 4, [0, 1, 2, 3, 4]), x_label="session", y_label="failed attempts",
    label_w=128)

body = fig.panel(right, "Rules read back at session start")
fig.bar_chart(
    body, [(f"session {s}", v, "state") for s, v in zip(sessions, rules_back)], 0, 4, [0, 1, 2, 3, 4],
    label_w=96, axis_label="rules in the memory file")

fig.caption(f"Over four sessions: {sum(failed_with)} failed attempts with the file, {sum(failed_without)} without.")
fig.write()
