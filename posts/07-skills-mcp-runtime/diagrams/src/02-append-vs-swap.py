"""Post 07, section 6: tokens reused from the prompt cache on each turn, under eager loading, swap and append.

Run from the series root:  uv run python posts/07-skills-mcp-runtime/diagrams/src/02-append-vs-swap.py
Writes posts/07-skills-mcp-runtime/diagrams/02-append-vs-swap.svg.
A section 5 chart of hrn_fig_design.md. Every plotted value is computed by run() and billed() of the post's
snippet snippets/prefix_cache.py; its token counts are illustrative (tiktoken o200k_base as a stand-in), so every
line is dashed and the subtitle says so. Swap is the failure (error red), append keeps what was appended (state
green), eager is the neutral baseline (ink); each also differs by marker shape.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
from prefix_cache import billed, run  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
R = {s: run(s) for s in ("eager", "swap", "append")}
BILLED = {s: round(billed(rows)) for s, rows in R.items()}
assert [r for _, r in R["swap"]] == [0, 0, 0, 0, 0, 506]
assert BILLED == {"eager": 2_681, "swap": 3_397, "append": 1_489}, BILLED
assert round(billed(R["swap"]) / billed(R["append"]), 2) == 2.28
for phrase in ("billed as  2,681", "billed as  3,397", "billed as  1,489", "swap / append billed: 2.28 times",
               "Swapping sends the fewest tokens of the three and costs the most"):
    assert phrase in BODY, phrase

turns = list(range(1, 7))
fig = Figure(
    "02-append-vs-swap", "Swapping the tool block throws the cache away",
    "A line chart of tokens reused from the prompt cache on each of six turns, for the same run built three ways. "
    "Eager loading, all 13 skill schemas in the tool block, reuses 0, then 1,427, 1,454, 1,480, 1,504 and 1,528, "
    "and is billed 2,681 token-equivalents. Swap, which rebuilds the tool block, reuses nothing on turns 1 to 5 and "
    "506 on turn 6, billed 3,397. Append reuses 0, 405, 667, 693, 861 and 885, billed 1,489. Cache reads count 0.1 "
    "and writes 1.25 of the base rate. Illustrative counts from snippets/prefix_cache.py.",
    subtitle="Same six-turn run, three ways; billed in token-equivalents. Illustrative counts, snippets/prefix_cache.py.",
    data_w=True)

body = fig.panel(fig.row(1)[0])
ax = fig.line_chart(
    body,
    [dict(xs=turns, ys=[r for _, r in R["eager"]], color="ink", dash="proj", shape="circle",
          label=f"eager: billed {BILLED['eager']:,}"),
     dict(xs=turns, ys=[r for _, r in R["append"]], color="state", dash="proj", shape="diamond",
          label=f"append: billed {BILLED['append']:,}"),
     dict(xs=turns, ys=[r for _, r in R["swap"]], color="error", dash="proj", shape="square",
          label=f"swap: billed {BILLED['swap']:,}")],
    x=(1, 6, turns), y=(0, 1_600, [0, 400, 800, 1_200, 1_600]),
    x_label="turn", y_label="tokens reused from the cache", fmt_x=lambda v: f"{v:g}",
    fmt_y=lambda v: f"{v:,.0f}", label_w=176)
ax.text(3.5, 0, "tool block changed: nothing reused", "label", anchor="middle", color="error", dy=-14)
fig.caption("Swap sends the fewest tokens and is billed the most: 2.28 times the cost of appending.")
fig.write()
