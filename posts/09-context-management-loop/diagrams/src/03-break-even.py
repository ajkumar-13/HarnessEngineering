"""Post 09, section 7: what one compaction costs, net of what it saves, call by call after it.

Run from the series root:  uv run python posts/09-context-management-loop/diagrams/src/03-break-even.py
Writes posts/09-context-management-loop/diagrams/03-break-even.svg.
Every value comes from snippets/cache_cost.py (table(): the event cost and the saving per later call of a deep
and a shallow compaction of a 160,000-token session at Claude Sonnet 4.6's multipliers), asserted against the
output the post quotes. The net cost after n later calls is event - n * saved, a straight line. The sizes are
illustrative, so both lines are dashed and the subtitle says so (hrn_fig_design.md section 5); the two
compactions are one neutral quantity told apart by ink against muted ink, marker shape and a direct label.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
from cache_cost import table  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
rows = table()
deep, shallow = rows["deep"], rows["shallow"]
assert (round(deep["total"]), round(deep["saved"]), round(deep["calls"], 1)) == (56_250, 13_500, 4.2)
assert (round(shallow["total"]), round(shallow["saved"]), round(shallow["calls"], 1)) == (187_500, 3_000, 62.5)
for phrase in ("the compaction event                                    56,250   187,500",
               "calls to break even                                        4.2      62.5"):
    assert phrase in BODY, phrase

LO, HI, XMAX = -80_000, 240_000, 70


def fmt(v):
    return f"{v:,.0f}".replace("-", "\u2212")


def line(r):
    end = min(XMAX, (r["total"] - LO) / r["saved"])     # where the line leaves the plot, or its right edge
    return [0, end], [r["total"], r["total"] - r["saved"] * end]


fig = Figure(
    "03-break-even", "A deep compaction pays back fast; a shallow one barely",
    "A line chart of the net cost of one compaction of a 160,000-token session, in token-equivalents, against the "
    "number of later calls, both lines dashed and illustrative. The deep compaction, to 25,000 tokens, in ink, "
    "starts at 56,250 and falls by 13,500 a call, crossing zero after 4.2 calls, marked with a hollow circle. The "
    "shallow compaction, to 130,000 tokens, in muted ink, starts at 187,500 and falls by 3,000 a call, crossing zero "
    "after 62.5 calls, marked with a hollow square. A dotted line marks zero, break even.",
    subtitle="Net cost after compacting a 160,000-token session; snippets/cache_cost.py, illustrative sizes.",
    data_w=True)

full = fig.panel(fig.row(1)[0])
body = Box(full.x, full.y, full.w - 136, full.h)
(dx_, dy_), (sx_, sy_) = line(deep), line(shallow)
series = [dict(xs=dx_, ys=dy_, color="ink", dash="proj", points=False, label=None),
          dict(xs=sx_, ys=sy_, color="ink-muted", dash="proj", points=False, label=None)]
ax = fig.line_chart(
    body, series, x=(0, XMAX, [0, 10, 20, 30, 40, 50, 60, 70]), y=(LO, HI, [0, 100_000, 200_000]),
    x_label="later calls after the compaction", y_label="net cost, token-equivalents", fmt_x=lambda v: f"{v:g}",
    fmt_y=fmt, ref_lines=[dict(y=0, label="break even")])
ax.point(deep["calls"], 0, "circle", "ink", size=10, hollow=True)
ax.point(shallow["calls"], 0, "square", "ink", size=10, hollow=True)
ax.text(deep["calls"], 0, "deep: even after 4.2 calls", "value", dx=10, dy=-10)
ax.text(shallow["calls"], 0, "shallow: even after 62.5 calls", "value", anchor="end", dx=-10, dy=24)
ax.text(0, deep["total"], "deep, to 25,000: event 56,250", "label", dx=10, dy=-8)
ax.text(0, shallow["total"], "shallow, to 130,000: event 187,500", "label", dx=10, dy=-8)
fig.caption("The write premium is charged on the whole surviving prefix, so a shallow compaction earns little back.")
fig.write()
