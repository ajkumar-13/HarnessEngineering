"""Post 08, section 6: the handoff file carries the work from a killed session to a fresh one.

Run from the series root:  uv run python posts/08-state-filesystem-git/diagrams/src/03-handoff-lifecycle.py
Writes posts/08-state-filesystem-git/diagrams/03-handoff-lifecycle.svg.
Every hash, step and field is read from a fresh run of snippets/handoff.py and asserted against the output the post
quotes; the handoff fields are the file session 1 wrote, read back from a run of session_one() alone. Files are
state cards (hrn_fig_design.md section 4); the unverified commit and the kill are red, the check against HEAD is a
gate, the rollback an action.
"""
import contextlib
import io
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import handoff  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
OUT = subprocess.run([sys.executable, str(POST / "snippets" / "handoff.py")], capture_output=True, text=True,
                     check=True).stdout
SESSION = [line for line in OUT.splitlines() if line.startswith("session")]
assert "```text\n" + "\n".join(SESSION) + "\n```" in BODY, "the post quotes a different run"
good, bad = SESSION[0].split()[3], SESSION[1].split()[3]
final = SESSION[5].split()[3].rstrip(",")
assert SESSION[2] == f"session 2: handoff names {good}, HEAD is {bad}"
assert SESSION[3].endswith(f"rolled back to {good}") and SESSION[4].endswith("resumes at step 3, multiline quoted fields")
assert SESSION[5].endswith("4 of 4 steps, broken step left in the tree: False")

with tempfile.TemporaryDirectory() as tmp:          # the file session 1 leaves behind
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            handoff.session_one(tmp)
    except handoff.Killed:
        pass
    FIELDS = handoff.sections(handoff.read_handoff(tmp))
assert FIELDS["Done"].endswith("2 of 4 steps verified.") and FIELDS["State"].endswith(good)
assert FIELDS["Next"] == "multiline quoted fields; negative amounts" and FIELDS["Spec"] == handoff.SPEC

fig = Figure(
    "03-handoff-lifecycle", "The handoff file carries the work across a reset",
    f"Three columns. Session 1: checkpoint {good} after 2 of 4 steps, write handoff.md, commit {bad} unverified, "
    "killed; its window is wiped at the reset. In the middle, handoff.md on disk: Spec, the goal; Done, 2 of 4 "
    f"steps verified; Next, multiline quoted fields then negative amounts; State, last checkpoint {good}. Session "
    f"2 reads only the file: it names {good} but HEAD is {bad}, so it rolls back to {good}, resumes at step 3, "
    f"and checkpoints {final} with 4 of 4 steps.",
    subtitle="A run of handoff.py: session 1 is killed after an unverified commit; session 2 has only the file.",
    data_w=True)


def events(x, title, rows, note=None, note_color=None):
    fig.text(x, 124, title, "head")
    boxes = []
    for k, (text, role) in enumerate(rows):
        b = Box(x, 144 + 52 * k, 288, 40)
        fig.card(b.x, b.y, b.w, b.h, color=role)
        fig.text(b.x + 16, b.y + 26, text, "label")
        boxes.append(b)
    if note:
        fig.text(x, boxes[-1].y + boxes[-1].h + 28, note, "label", color=note_color)
    return boxes


s1 = events(40, "session 1", [(f"checkpoint {good}, 2 of 4 steps", "state"), ("write handoff.md", "act"),
                              (f"commit {bad}, unverified", "error"), ("killed: memory gone", "error")],
            note="window wiped at the reset", note_color="error")
s2 = events(632, "session 2", [(f"read handoff.md: {good}", "state"), (f"HEAD is {bad}: no match", "gate"),
                               (f"rollback to {good}", "act"), ("resume at step 3", "model"),
                               (f"checkpoint {final}, 4 of 4", "state")])

# the file on disk, between the sessions
card = Box(360, 144, 240, 264)
fig.card(card.x, card.y, card.w, card.h, color="state")
fig.text(card.x + 16, card.y + 28, "handoff.md", "code")
rows = [("## Spec", "the goal, unchanged"), ("## Done", "2 of 4 steps verified"),
        ("## Next", FIELDS["Next"].split("; ")[0] + ";"), (None, FIELDS["Next"].split("; ")[1]),
        ("## State", "last checkpoint " + good)]
y = card.y + 60
for head, value in rows:
    if head:
        fig.text(card.x + 16, y, head, "code")
        y += 20
    fig.text(card.x + 16, y, value, "note")
    y += 28 if head != "## Next" else 20
fig.text(card.x + card.w // 2, card.y + card.h + 28, "on disk: survives the reset", "label", anchor="middle",
         color="state")
fig.arrow((s1[1].x + s1[1].w, s1[1].y + 20), (card.x, s1[1].y + 20))
fig.arrow((card.x + card.w, s2[0].y + 20), (s2[0].x, s2[0].y + 20))

fig.caption("The State field lets the fresh session check the tree before it trusts the file.")
fig.write()
