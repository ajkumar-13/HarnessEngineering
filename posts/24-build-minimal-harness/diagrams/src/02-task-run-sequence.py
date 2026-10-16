"""Post 24, section 7: the companion's demo run turn by turn, and the same script with the gate taken out.

Run from the series root:  uv run python posts/24-build-minimal-harness/diagrams/src/02-task-run-sequence.py
Writes posts/24-build-minimal-harness/diagrams/02-task-run-sequence.svg.

The turn-by-turn form of hrn_fig_design.md section 1: one column per iteration, the model's output (model, blue)
above what the harness did with it (an observation, state, green; a verdict of the gate, gate, purple), a failed
check red where it happened, the exit named at the end. Computed: the script imports snippets/task_run.py and runs
it (its printing is discarded), which runs the companion's own demo unchanged and then the same script with
verify=None. Every byte count, report, iteration count and token total is read from those two Results, asserted,
and checked against the post's quotation of the snippet's output.
"""
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("task_run", POST / "snippets" / "task_run.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)
with contextlib.redirect_stdout(io.StringIO()) as out:
    r = tr.main()
for line in out.getvalue().splitlines():
    assert line in BODY, line                      # the body quotes the snippet's output verbatim

gated, bare, rows = r["gated"], r["bare"], r["rows"]
assert (gated.stop_reason.value, gated.verified, gated.iterations, gated.tokens_used) == ("completed", True, 4, 54)
assert (bare.stop_reason.value, bare.verified, bare.iterations, bare.tokens_used) == ("completed", True, 2, 28)
BUG, FIX = "return s == s  # bug: always true", "return s == s[::-1]"
assert r["files"] == (BUG, FIX)
REPORT = rows[1][1].removeprefix("verification failed: ")
assert REPORT == "is_palindrome('abc',) == True, expected False"
WROTE = [rows[0][1], rows[2][1]]
assert WROTE == ["wrote 60 bytes to solution.py", "wrote 46 bytes to solution.py"]
EXTRA = (gated.iterations - bare.iterations, gated.tokens_used - bare.tokens_used)
assert EXTRA == (2, 26)

fig = Figure(
    "02-task-run-sequence", "The gate overrules the first claim of done",
    "Two runs of the companion's demo, one column per iteration. Top, with the palindrome gate: iteration 1, the "
    f"model writes solution.py with {BUG.split('  #')[0]} and the harness reports {WROTE[0]}; iteration 2, the "
    f"model gives a final answer and the gate fails it with the report {REPORT}, which goes back to the model; "
    f"iteration 3, the model writes {FIX} and the harness reports {WROTE[1]}; iteration 4, a final answer the gate "
    f"passes, exit (1) completed, verified, {gated.iterations} iterations, {gated.tokens_used} tokens. Bottom, the "
    f"same script with verify=None: iteration 1 the same; iteration 2 the final answer ends the run as completed "
    f"and reported verified after {bare.iterations} iterations and {bare.tokens_used} tokens, and the bug ships.",
    subtitle="Computed by snippets/task_run.py from the companion's demo; its token counts are set by hand.",
    height=720, data_w=True)

X0, CW, GAP = 120, 184, 16
COLS = [X0 + k * (CW + GAP) for k in range(4)]
H = 56


def cell(k, y, role, first, second=None, mono_second=False, word_role=None):
    box = Box(COLS[k], y, CW, H)
    fig.fill(box, "neutral-soft" if role == "neutral" else f"{role}-soft", radius=8)
    fig.outline(box, "border" if role == "neutral" else f"{role}-line", radius=8)
    fig.text(box.x + 12, y + 24, first, "label", color=word_role)
    if second:
        fig.text(box.x + 12, y + 44, second, "code" if mono_second else "note")
    return box


def lane(top, heading, n):
    fig.text(40, top, heading, "head")
    for k in range(n):
        fig.text(COLS[k] + 12, top + 28, f"iteration {k + 1}", "note")
    fig.text(40, top + 72, "model", "label")
    fig.text(40, top + 144, "harness", "label")
    return top + 44, top + 116


# top lane: the demo with the gate
MY, HY = lane(128, "With the palindrome gate: the companion's demo", gated.iterations)
cell(0, MY, "model", "write_file", BUG.split("  #")[0], mono_second=True)
cell(1, MY, "model", "final answer", "claims done")
cell(2, MY, "model", "write_file", FIX, mono_second=True)
cell(3, MY, "model", "final answer", "claims fixed")
cell(0, HY, "state", WROTE[0].removesuffix(" to solution.py"), "observation")
cell(1, HY, "error", "gate: fail", "report sent back", word_role="error")
cell(2, HY, "state", WROTE[1].removesuffix(" to solution.py"), "observation")
cell(3, HY, "gate", "gate: pass, exit (1)", f"{gated.iterations} iterations, {gated.tokens_used} tokens",
     word_role="gate")
fig.arrow((COLS[1] + CW, HY + 16), (COLS[2], MY + H - 16), color="error")
fig.text(40, HY + H + 36, "report", "label", color="error")
fig.text(COLS[1] + 12, HY + H + 36, REPORT, "code", color="error")

# bottom lane: the same script, no gate
MY2, HY2 = lane(436, "The same script with verify=None", bare.iterations)
cell(0, MY2, "model", "write_file", BUG.split("  #")[0], mono_second=True)
cell(1, MY2, "model", "final answer", "claims done")
cell(0, HY2, "state", WROTE[0].removesuffix(" to solution.py"), "observation")
cell(1, HY2, "neutral", "no gate", "exit (1) completed")
ship = Box(COLS[2], HY2, 2 * CW + GAP, H)
fig.fill(ship, "error-soft", radius=8)
fig.outline(ship, "error", width=1.5, radius=8)
fig.text(ship.x + 12, HY2 + 24, f"ships the bug: {bare.iterations} iterations, {bare.tokens_used} tokens", "label",
         color="error")
fig.text(ship.x + 12, HY2 + 44, "reported verified, file still returns s == s", "note")
fig.arrow((COLS[1] + CW, HY2 + H // 2), (COLS[2], HY2 + H // 2), color="error")

fig.caption(f"The same model and script: the gate costs {EXTRA[0]} iterations and {EXTRA[1]} tokens, and the "
            "file is correct.")
fig.write()
