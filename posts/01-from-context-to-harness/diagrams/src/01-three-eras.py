"""Post 01, section 1 (the hero): three eras on one axis, each with its bottleneck and its unit of work.

Run from the series root:  uv run python posts/01-from-context-to-harness/diagrams/src/01-three-eras.py
Writes posts/01-from-context-to-harness/diagrams/01-three-eras.svg.
The era spans and bottlenecks are Faros AI's (guide to harness engineering, 22 May 2026), as section 1 of
index.md states them; the units of work are section 1's; the three flags are dates the post states and cites in
sections 1 and 2. Every one is asserted against the body below. The axis is linear from 1 January 2022 to
1 January 2027; a month is placed at its middle and a day at its own date. Eras are neutral spans under the axis
(hrn_fig_design.md section 4); nothing is drawn in a role colour, because no part of the figure is a model call,
an action, state or a gate.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

# era name, first year, last year, bottleneck, unit of work (section 1)
ERAS = [
    ("Prompt engineering", 2022, 2023, "phrasing", "a message"),
    ("Context engineering", 2024, 2025, "information", "a window"),
    ("Harness engineering", 2026, 2026, "autonomy and control", "a whole run"),
]
for phrase in ("prompt engineering in 2022 to 2023, when the bottleneck was phrasing",
               "context engineering in 2024 to 2025, when it was information",
               "harness engineering in 2026, when it is autonomy and control",
               "a message, then a window, then a whole run", "published 22 May 2026"):
    assert phrase in BODY, phrase

# (year, month, day or None, row, date text, event text, phrase the post must contain)
FLAGS = [
    (2024, 12, 19, 0, "December 2024", "Building effective agents",
     "| 19 December 2024 | Anthropic Engineering, \"Building effective agents\""),
    (2025, 6, None, 1, "June 2025", "context engineering popularised",
     "popularised the phrase in a post on X in June 2025"),
    (2026, 3, 10, 2, "10 March 2026", "Agent = Model + Harness",
     "\"The Anatomy of an Agent Harness\" (LangChain blog, 10 March 2026) opens with the equation"),
]
for *_, phrase in FLAGS:
    assert phrase in BODY, phrase

X0, X1, Y0, Y1 = 40, 920, 2022, 2027          # the axis: 1 January 2022 to 1 January 2027
AY = 296                                       # axis baseline
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def xof(year, month=1, day=None):
    frac = (month - 1) / 12 + ((day - 1) / DAYS[month - 1] if day else 0.5) / 12
    return X0 + (year + frac - Y0) / (Y1 - Y0) * (X1 - X0)


fig = Figure(
    "01-three-eras", "Each era widened the surface the engineer works on",
    "A timeline from 2022 to 2026. Under the axis, three neutral era spans as Faros AI dates them, each with its "
    "bottleneck and its unit of work: prompt engineering, 2022 to 2023, phrasing, a message; context engineering, "
    "2024 to 2025, information, a window; harness engineering, 2026, autonomy and control, a whole run. Above the "
    "axis, three dated flags: Anthropic's Building effective agents in December 2024, context engineering "
    "popularised in June 2025, and Trivedy's Agent = Model + Harness on 10 March 2026. The caption says each era kept "
    "the work of the one before.",
    subtitle="Eras and bottlenecks as Faros AI dates them (May 2026); flags mark three dated articles the post cites.",
    data_w=True)

# eras: neutral spans under the axis, one card per era, spanning its years
TOP, BOT = AY + 36, 464
for name, y0, y1, neck, unit in ERAS:
    a, b = X0 + (y0 - Y0) * (X1 - X0) / (Y1 - Y0), X0 + (y1 + 1 - Y0) * (X1 - X0) / (Y1 - Y0)
    fig.card(a + 4, TOP, b - a - 8, BOT - TOP)
    tx = a + 14
    fig.text(tx, TOP + 28, name, "label", bold=True)
    fig.text(tx, TOP + 56, "bottleneck", "note")
    fig.text(tx, TOP + 76, neck, "label")
    fig.text(tx, TOP + 104, "unit of work", "note")
    fig.text(tx, TOP + 124, unit, "label")

# the axis, year boundaries, and year labels centred in each year
fig.edge((X0, AY), (X1, AY), color="ink", width=1.5)
for yr in range(Y0, Y1 + 1):
    x = X0 + (yr - Y0) * (X1 - X0) / (Y1 - Y0)
    fig.edge((x, AY - 6), (x, AY + 6), color="ink-muted", width=1)
    if yr < Y1:
        fig.text(x + (X1 - X0) / (Y1 - Y0) / 2, AY + 24, str(yr), "tick", anchor="middle")

# flags: a leader up from the axis, the date and the event to its left, each row higher than the last
ROWS = [(AY - 56, AY - 36), (AY - 116, AY - 96), (AY - 176, AY - 156)]
for year, month, day, row, date, event, _ in FLAGS:
    x = xof(year, month, day)
    date_y, event_y = ROWS[row]
    with fig.data():
        fig.edge((x, AY - 8), (x, date_y - 14), color="rule", width=1)
        fig.marker(x, AY, "circle", "ink", size=10)
        fig.text(x - 8, date_y, date, "value", anchor="end", snap=False)
        fig.text(x - 8, event_y, event, "label", anchor="end", snap=False)

fig.caption("Each era kept the work of the one before: the message sits inside the window, the window inside the run.")
fig.write()
