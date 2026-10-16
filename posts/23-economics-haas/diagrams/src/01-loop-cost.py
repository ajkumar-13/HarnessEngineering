"""Post 23, hero: cumulative dollars of one run, uncached against a cached static head and a rolling breakpoint.

Run from the series root:  uv run python posts/23-economics-haas/diagrams/src/01-loop-cost.py
Writes posts/23-economics-haas/diagrams/01-loop-cost.svg.
Every plotted value is cumulative() of snippets/loop_cost.py over 40 iterations of the series' running example
(6,000 input tokens on the first request, 3,100 more on each, 600 output tokens per iteration) at Claude Sonnet
4.6's rates on Anthropic's pricing page, consulted October 2026, asserted against the values the post states. The
sizes are illustrative, so every line is dashed and the legend says "illustrative" (hrn_fig_design.md section 5).
Roles: the uncached and static-head lines are neutral quantities (ink, ink-muted); the rolling breakpoint is the
cached history carried from turn to turn, which this series draws as state (green).
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("loop_cost", POST / "snippets" / "loop_cost.py")
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)

N = 40
xs = list(range(1, N + 1))
lines = {m: lc.cumulative(N, m) for m in ("uncached", "static head", "rolling")}
at = {m: (round(v[11], 2), round(v[-1], 2)) for m, v in lines.items()}
assert at == {"uncached": (0.94, 8.33), "static head": (0.79, 7.81), "rolling": (0.33, 1.60)}, at
for phrase in ("0.94 dollars at 12 iterations and 8.33 at 40", "0.33 and 1.60", "Claude Sonnet 4.6 rates"):
    assert phrase in BODY, phrase

fig = Figure(
    "01-loop-cost", "Uncached, a run's bill grows with the square of its length",
    "A line chart of cumulative dollars against loop iterations 1 to 40 for the series' illustrative running "
    "example at Claude Sonnet 4.6 rates, computed by the post's snippet. Uncached, the dashed line curves upward to "
    "0.94 dollars at 12 iterations and 8.33 at 40. A cached static head of 5,000 tokens runs just below it, 0.79 "
    "and 7.81. A rolling breakpoint, in green, rises almost straight, 0.33 at 12 and 1.60 at 40.",
    subtitle="Computed by snippets/loop_cost.py, illustrative sizes; Claude Sonnet 4.6, $3 and $15 per million, Oct 2026",
    data_w=True)

body = fig.panel(fig.row(1)[0])
STYLE = {"uncached": ("ink", "uncached"), "static head": ("ink-muted", "static head"),
         "rolling": ("state", "rolling breakpoint")}
ax = fig.line_chart(
    body,
    [dict(xs=xs, ys=lines[m], color=c, dash="proj", points=False, label=lab) for m, (c, lab) in STYLE.items()],
    x=(0, 40, [0, 10, 20, 30, 40]), y=(0, 9, [0, 3, 6, 9]),
    x_label="loop iteration", y_label="dollars, running total", label_w=160,
    fmt_x=lambda v: f"{v:g}", fmt_y=lambda v: f"${v:g}")
for m in ("uncached", "rolling"):
    for i in (12, 40):
        ax.point(i, lines[m][i - 1], "circle", STYLE[m][0], size=10, hollow=True)
tx, ty = ax.to_px(1.5, 8.8)
tx, ty = int(tx // 8 * 8), int(ty // 8 * 8)
fig.table(tx, ty, [["dollars at", "12", "40"],
                   ["uncached", f"{at['uncached'][0]:.2f}", f"{at['uncached'][1]:.2f}"],
                   ["static head", f"{at['static head'][0]:.2f}", f"{at['static head'][1]:.2f}"],
                   ["rolling breakpoint", f"{at['rolling'][0]:.2f}", f"{at['rolling'][1]:.2f}"]],
          [176, 64, 64], col_align=["start", "end", "end"])
fig.legend(body, [dict(color="ink", label="illustrative, computed", mark="dash"),
                  dict(color="ink", label="12 and 40 iterations", mark="circle", hollow=True)], direction="row")
fig.write()
