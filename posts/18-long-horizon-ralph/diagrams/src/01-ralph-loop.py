"""Post 18, the hero: the Ralph loop, a fresh process per task against four files on disk, and the driver's stops.

Run from the series root:  uv run python posts/18-long-horizon-ralph/diagrams/src/01-ralph-loop.py
Writes posts/18-long-horizon-ralph/diagrams/01-ralph-loop.svg.
The loop of hrn_fig_design.md section 1, opened into one Ralph iteration: the fresh context is the model's step
(blue), the task and its commit are act (orange), the gate the driver runs is gate (purple), the reset is
neutral. What persists is state (green): the four files snippets/ralph_driver.py keeps on disk. The four ways
the driver stops are gates (purple diamonds), named as the snippet names them; the script asserts each name and
default against the snippet's source so the figure cannot drift from the code.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
import ralph_driver as rd  # noqa: E402

SRC = (POST / "snippets" / "ralph_driver.py").read_text(encoding="utf-8")
sig = inspect.signature(rd.ralph).parameters
assert sig["max_iters"].default == 50 and sig["stale_cap"].default == 3
for name in ('"completed"', '"max_iters"', '"no_progress"', '"spec_moved"', "rev-list", "sha256"):
    assert name in SRC, name
assert str(rd.SPEC) == "spec\\feature_list.json" or str(rd.SPEC) == "spec/feature_list.json"

fig = Figure(
    "01-ralph-loop", "The window is thrown away; the disk keeps the work",
    "Top, a green band of four files on disk that survive every reset: the spec, saying what done means, written by "
    "a human; handoff.md, where the work stands, rewritten each iteration; status.json, one pass bit per check, "
    "written by the gate; and the git history, one commit per iteration. Below, one iteration as four cards left to right: "
    "a fresh process with an empty window reads the files; it does one task and commits it; the driver's gate runs "
    "every check and writes the pass bits; the process exits and the window is discarded; an arrow runs back to the "
    "start. Bottom, four purple diamonds: the driver stops on every check passing, exit (1); 50 iterations, exit (2); "
    "3 rounds with no new commit, exit (4); or spec bytes that moved, spec_moved.",
    subtitle="One task per fresh process against files on disk; after each one the driver checks, then decides.",
    height=720, data_w=True)

# the band: what survives the reset
BX, BY, BW, BH = 40, 112, 880, 180
fig.card(BX, BY, BW, BH, color="state")
fig.text(BX + 16, BY + 28, "On disk: survives every reset", "head")
FILES = [("the spec", ["what done means;", "a human writes it"]),
         ("handoff.md", ["where the work stands;", "rewritten each iteration"]),
         ("status.json", ["one pass bit per check;", "the gate writes it"]),
         ("git history", ["the work itself;", "one commit per iteration"])]
for k, (head, lines) in enumerate(FILES):
    fig.card(BX + 16 + k * 216, BY + 48, 200, 116, heading=head, lines=lines, style="label")

# the iteration: four steps
LY, LW, LH = 368, 196, 108
COLS = [40, 268, 496, 724]
STEPS = [("fresh context", ["a new process,", "an empty window"], "model"),
         ("one task", ["build it, commit it,", "rewrite the handoff"], "act"),
         ("the gate", ["the driver runs every", "check, writes the bits"], "gate"),
         ("reset", ["the process exits;", "the window is discarded"], None)]
cards = []
for x, (head, lines, role) in zip(COLS, STEPS):
    fig.card(x, LY, LW, LH, heading=head, lines=lines, color=role)
    cards.append((x, LY, LW, LH))
for (x0, _, w0, _), (x1, _, _, _) in zip(cards, cards[1:]):
    fig.arrow((x0 + w0, LY + LH // 2), (x1, LY + LH // 2))
# back to the start, under the row
RY = LY + LH + 40
fig.arrow((COLS[3] + LW // 2, LY + LH), (COLS[0] + LW // 2, LY + LH), via=((COLS[3] + LW // 2, RY),
          (COLS[0] + LW // 2, RY)), label="repeat, carrying nothing", side="below")

# between band and row: read down, write up
BB = BY + BH
fig.arrow((COLS[0] + 72, BB), (COLS[0] + 72, LY), label="reads all four", side="right", color="state")
fig.arrow((COLS[1] + 98, LY), (COLS[1] + 98, BB), label="handoff, commit", side="right", color="state")
fig.arrow((COLS[2] + 98, LY), (COLS[2] + 98, BB), label="pass bits", side="right", color="state")
fig.text(COLS[3] + 16, BB + 44, "nothing goes up", "note")

# the driver's stops
GY = 600
fig.text(40, GY - 24, "The driver stops on", "head")
STOPS = [("every check passes", "exit (1)"), ("50 iterations", "exit (2)"),
         ("3 rounds, no commit", "exit (4)"), ("spec bytes moved", "spec_moved")]
for x, (what, name) in zip(COLS, STOPS):
    fig.marker(x + 12, GY + 8, "diamond", "gate", size=16)
    fig.text(x + 32, GY + 13, what, "label")
    fig.text(x + 32, GY + 37, name, "code" if "_" in name else "label", color="gate")

fig.caption("Only the files cross the reset, and only the driver decides the work is done.")
fig.write()
