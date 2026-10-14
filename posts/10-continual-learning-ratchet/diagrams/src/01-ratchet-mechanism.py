"""Post 10, hero: one failure becomes the ratchet's three teeth.

Run from the series root:  uv run python posts/10-continual-learning-ratchet/diagrams/src/01-ratchet-mechanism.py
Writes posts/10-continual-learning-ratchet/diagrams/01-ratchet-mechanism.svg.
The failure and the three teeth are Osmani's worked example as section 4 quotes it ("Agent Harness Engineering",
19 April 2026); the script asserts each quoted piece against the body. Roles (hrn_fig_design.md section 0): the
failure is red at the source; the memory-file line is green, because it is state (a rule the ratchet wrote, read
by the model, which can still ignore it); the hook and the reviewer check are purple gates. No numbers.
"""
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, text_width  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in (
    "his worked example is a pull request (PR) with a commented-out test, merged by accident",
    "says 'never comment out tests; delete them or fix them.'",
    "The next version of my pre-commit hook greps for `.skip(` and `xit(` in the diff.",
    "The next version of my reviewer subagent flags commented-out tests as a blocker",
    "1. **A memory-file line**: the model reads it every session",
    "2. **A hook**: deterministic enforcement",
    "3. **A reviewer check**: a reviewer or evaluator that flags it if it slips past the first two",
):
    assert phrase in BODY, phrase

fig = Figure(
    "01-ratchet-mechanism", "One failure becomes three durable constraints",
    "On the left a red card, a failure: a pull request with a commented-out test is merged. Three arrows fan out "
    "from it to three cards on the right, each acting at a different moment. One, in green, a memory-file line in "
    "AGENTS.md, read at every session start: never comment out tests; delete them or fix them. Two, in purple, a "
    "hook that acts on every commit: the pre-commit hook greps the diff for .skip( and xit(. Three, in purple, a "
    "reviewer check that acts at review: the reviewer sub-agent flags commented-out tests as a blocker.",
    subtitle="Osmani's worked example: the model reads the rule, a hook blocks the mistake, a reviewer catches "
             "what slips.",
    data_w=True)

# the failure, red at the source
fx, fy, fw, fh = 40, 224, 248, 128
fig.card(fx, fy, fw, fh, color="error")
fig.text(fx + 16, fy + 32, "a failure", "head", color="error")
fig.text(fx + 16, fy + 64, "a pull request with a", "label")
fig.text(fx + 16, fy + 88, "commented-out test", "label")
fig.text(fx + 16, fy + 112, "is merged", "label")

# the three teeth
CX, CW, CH = 360, 560, 112
TEETH = [
    (104, "state", "1  memory-file line", "read at every session start",
     [("label", "never comment out tests; delete them or fix them.")], "in AGENTS.md"),
    (232, "gate", "2  hook", "on every commit",
     [("label", "the pre-commit hook greps the diff for")], ("code", ".skip(  and  xit(")),
    (360, "gate", "3  reviewer check", "at review",
     [("label", "the reviewer sub-agent flags commented-out tests")], "as a blocker"),
]
for y, role, head, when, line, note in TEETH:
    fig.card(CX, y, CW, CH, color=role)
    fig.text(CX + 16, y + 32, head, "head", color=role)
    fig.text(CX + CW - 16, y + 32, when, "note", anchor="end")
    x = CX + 16
    for style, s in line:
        fig.text(x, y + 64, s, style)
        w = text_width(s, 14, mono=True) if style == "code" else text_width(s, 14, weight=400)
        x = math.ceil((x + w) / 4) * 4
    style, s = note if isinstance(note, tuple) else ("note", note)
    fig.text(CX + 16, y + 88, s, style)
    fig.arrow((fx + fw, fy + fh // 2), (CX, y + CH // 2))

fig.caption("Not every failure earns all three; detectability and scope decide which.")
fig.write()
