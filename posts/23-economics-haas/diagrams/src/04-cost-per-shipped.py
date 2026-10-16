"""Post 23, section 7: dollars per unit of work shipped for two illustrative harnesses, split into tokens and review.

Run from the series root:  uv run python posts/23-economics-haas/diagrams/src/04-cost-per-shipped.py
Writes posts/23-economics-haas/diagrams/04-cost-per-shipped.svg.
Every bar is shipped() of snippets/run_meter.py for its two harnesses (iterations, first-pass rate, review minutes
and escape rate all illustrative; review at a placeholder 90 dollars an hour; tokens at Claude Sonnet 4.6's rates,
October 2026), asserted against the table the post prints. A segment is the per-accepted figure divided by one
minus the escape rate, so the two segments sum to the per-shipped total. Values are printed to one decimal so the
segments add up on the figure. Roles: model tokens are the model's output, blue; a person's review time is
neutral (the human is ink in this series).
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("run_meter", POST / "snippets" / "run_meter.py")
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)

rows = []
for name, h in rm.HARNESSES.items():
    per_run, per_accepted, review, per_shipped = rm.shipped(h)
    tokens, people = per_accepted / (1 - h["escape"]), review / (1 - h["escape"])
    assert abs(tokens + people - per_shipped) < 1e-9
    rows.append((name, round(tokens, 1), round(people, 1), round(per_shipped, 2)))
assert rows == [("A, no gate", 0.8, 31.4, 32.19), ("B, gate on every step", 0.6, 9.4, 9.95)], rows
for phrase in ("0.8 dollars of model tokens and 31.4 of review", "0.6 and 9.4", "$32.19", "$9.95"):
    assert phrase in BODY, phrase

fig = Figure(
    "04-cost-per-shipped", "Per unit shipped, the tokens are the thin part",
    "A computed stacked bar chart of dollars per unit of work shipped for two illustrative harnesses. Harness A, "
    "with no verification gate: 0.8 dollars of model tokens and 31.4 of a person's review, 32.2 in all. Harness B, "
    "with a gate on every step: 0.6 of model tokens and 9.4 of review, 10.0 in all.",
    subtitle="Computed by snippets/run_meter.py; illustrative inputs, review priced at a placeholder $90 an hour.",
    data_w=True)

body = fig.panel(fig.row(1, h=296)[0])
ax = fig.stacked_bars(body, [(n, [t, p]) for n, t, p, _ in rows], ["model", "ink-muted"], 0, 35,
                      [0, 10, 20, 30], label_w=192, value_w=160, segment_labels=True,
                      fmt_tick=lambda v: f"${v:g}", fmt_value=lambda v: f"{v:.1f}",
                      axis_label="dollars per unit of work shipped")
fig.legend(body, [dict(color="model", label="model tokens"),
                  dict(color="ink-muted", label="review by a person")], direction="row")
fig.caption("The gate adds iterations to every run and removes most of the review.")
fig.write()
