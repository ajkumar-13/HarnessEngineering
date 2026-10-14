"""Post 08, section 4: one checkpoint, one bad step, a scoped rollback, and a checkpoint that fails.

Run from the series root:  uv run python posts/08-state-filesystem-git/diagrams/src/02-checkpoint-rollback.py
Writes posts/08-state-filesystem-git/diagrams/02-checkpoint-rollback.svg.
Every hash, path and verdict is read from a fresh run of snippets/git_checkpoint.py (fixed author and dates, so
the hashes repeat) and asserted against the output the post quotes. Commits are state cards (hrn_fig_design.md
section 4), the bad step and the failed checkpoint are red.
"""
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
OUT = subprocess.run([sys.executable, str(POST / "snippets" / "git_checkpoint.py")], capture_output=True,
                     text=True, check=True).stdout
assert "```text\n" + OUT + "```" in BODY, "the post quotes a different run"
lines = OUT.splitlines()
REF = lines[0].split()[1]
assert lines[2].startswith(f"HEAD {REF}") and lines[-1].startswith(f"rev-parse HEAD still answers {REF}")
PATHS = [tuple(line.split(None, 2)) for line in lines[3:6]]
assert [p for p, *_ in PATHS] == ["src/debris.py", "scratch/build.log", "notes.md"]
FAILED = lines[6]
assert FAILED == "checkpoint failed: fatal: Unable to create '.git/index.lock': File exists."
ROWS = [["path", "after the rollback", "why"], ["src/parse.py", "restored", "tracked, under src/"]]
ROWS += [[p, verdict, why] for p, verdict, why in PATHS]

fig = Figure(
    "02-checkpoint-rollback", "A rollback restores only what the step could touch",
    f"Three cards left to right: checkpoint {REF} with tests green, a risky step in red with tests red, and after "
    f"the rollback HEAD back at {REF}. A table of four paths: src/parse.py restored because it is tracked; "
    "src/debris.py removed, untracked under src/; scratch/build.log kept because it is ignored; notes.md kept, "
    "untracked outside the paths. Below, in red, a checkpoint that fails on a leftover index.lock while "
    f"rev-parse HEAD still answers {REF}.",
    subtitle="A run of git_checkpoint.py: the reset restores tracked files; the scoped clean removes only debris.",
    data_w=True)

cards = [Box(40, 120, 232, 64), Box(364, 120, 232, 64), Box(688, 120, 232, 64)]
for b, head, note, role in zip(cards, (REF, "risky step", f"HEAD {REF}"),
                               ("checkpoint: tests green", "tests red", "after the rollback"),
                               ("state", "error", "state")):
    fig.card(b.x, b.y, b.w, b.h, color=role)
    fig.text(b.x + 16, b.y + 26, head, "code" if head != "risky step" else "label")
    fig.text(b.x + 16, b.y + 50, note, "note")
fig.chain(cards, labels=["attempt", "rollback"])

fig.table(40, 216, ROWS, [264, 240, 376], col_align=["start", "start", "start"])

bad = Box(40, 400, 880, 64)
fig.card(bad.x, bad.y, bad.w, bad.h, color="error")
fig.text(56, 426, FAILED, "code")
fig.text(56, 450, f"rev-parse HEAD still answers {REF}: only the return-code check raises", "note")

fig.caption("Ignored and out-of-scope files survive the rollback; a failed commit must not return a hash.")
fig.write()
