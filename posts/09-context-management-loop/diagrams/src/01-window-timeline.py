"""Post 09, hero: one run's window, call by call, unmanaged against managed by the ladder.

Run from the series root:  uv run python posts/09-context-management-loop/diagrams/src/01-window-timeline.py
Writes posts/09-context-management-loop/diagrams/01-window-timeline.svg.
Every plotted value comes from snippets/ladder.py (table(): the input tokens of each call of the generated run,
unmanaged and managed, and the rungs that fired), asserted against the output the post quotes. The sizes and the
window are illustrative, so both curves are dashed and the subtitle says so (hrn_fig_design.md section 5). The two
runs are one neutral quantity told apart by ink against muted ink and a direct label; the triggers are gates
(purple), the overrun is an error (red), and each rung that fired is a hollow marker named where it sits.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
from ladder import HARD, SOFT, table  # noqa: E402
from transcript import WINDOW  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
plain, managed, events = table()
CALLS = list(range(2, 2 + len(plain)))
over = next(c for c, n in zip(CALLS, plain) if n > WINDOW)
rungs = [(c, r, b, a) for c, r, b, a, _ in events if r != "offload"]
offloads = [c for c, r, *_ in events if r == "offload"]
assert over == 54 and plain[over - 2] == 201_343
assert [(c, r) for c, r, *_ in rungs] == [(97, "clear"), (123, "clear"), (138, "compact")]
assert offloads == [10, 31, 52, 73, 94, 115] and rungs[-1][3] == 8_447
for phrase in ("unmanaged: call 54 would send 201,343 tokens, past the window",
               "managed: build logs offloaded at the tool boundary before calls 10, 31, 52, 73, 94, 115",
               " 138  compact   190,428    8,447  773 of 8,447 (9%)"):
    assert phrase in BODY, phrase


def fmt(v):
    return f"{v:,.0f}"


fig = Figure(
    "01-window-timeline", "A loop fills its own window; the ladder pushes back",
    "A line chart of input tokens sent on each model call, calls 2 to 141, of one generated run with illustrative "
    "sizes, both curves dashed. The unmanaged run, in muted ink, climbs in steps at each 2,000-line build log and "
    "passes the 200,000-token window at call 54 with 201,343 tokens, marked in red. The managed run, in ink, "
    "offloads the six build logs at the tool boundary before calls 10, 31, 52, 73, 94 and 115, marked with small "
    "triangles; clears spent tool results at call 97 and call 123 after crossing the soft trigger at 160,000 tokens; "
    "and compacts at call 138 on the hard trigger at 190,000, falling to 8,447 tokens. The triggers are purple "
    "dotted lines and the window a muted dotted line.",
    subtitle="Input tokens per call of one generated run, from snippets/ladder.py; sizes and window are illustrative.",
    data_w=True)

full = fig.panel(fig.row(1)[0])
body = Box(full.x, full.y, full.w - 160, full.h)
series = [dict(xs=CALLS[:over - 1], ys=plain[:over - 1], color="ink-muted", dash="proj", points=False, label=None),
          dict(xs=CALLS, ys=managed, color="ink", dash="proj", points=False, label=None)]
ax = fig.line_chart(
    body, series, x=(0, 142, [0, 20, 40, 60, 80, 100, 120, 140]), y=(0, 220_000, [0, 50_000, 100_000, 150_000, 200_000]),
    x_label="model call", y_label="input tokens sent", fmt_x=lambda v: f"{v:g}", fmt_y=fmt,
    ref_lines=[dict(y=WINDOW, label="window 200,000", color="ink-muted", at="left"),
               dict(y=HARD, label="hard trigger 95%", color="gate", at="right"),
               dict(y=SOFT, label="soft trigger 80%", color="gate", at="right")])
ax.point(over, plain[over - 2], "circle", "error", size=10, hollow=True)
ax.text(over, plain[over - 2], "past the window at call 54", "value", color="error", dx=12, dy=-8)
ax.text(22, plain[20], "unmanaged", "label", anchor="end", dx=-6, dy=-14)
ax.text(60, managed[58], "managed", "label", dx=4, dy=24)
for c in offloads:
    ax.point(c, managed[c - 2], "triangle", "ink", size=8, hollow=True)
ax.text(offloads[1], managed[offloads[1] - 2], "build logs offloaded", "note", dx=8, dy=22)
for (c, rung, before, after), dy in zip(rungs, (-10, -10, 0)):
    ax.point(c, after, "square" if rung == "clear" else "diamond", "ink", size=10, hollow=True)
NAMES = {97: "clear", 123: "clear", 138: "compact to 8,447"}
for (c, rung, before, after), (dx, dy, anchor) in zip(rungs, ((-10, 18, "end"), (10, 24, "start"), (-10, 5, "end"))):
    ax.text(c, after, NAMES[c], "value", anchor=anchor, dx=dx, dy=dy)
fig.caption("The cheap rungs postpone the expensive one: the run compacts once, at call 138.")
fig.write()
