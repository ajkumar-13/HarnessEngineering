"""Post 02, section 7: the coordination tax of orchestration, priced with Anthropic's cited multipliers.

Run from the series root:  uv run python posts/02-anatomy-of-a-harness/diagrams/src/02-coordination-tax.py
Writes posts/02-anatomy-of-a-harness/diagrams/02-coordination-tax.svg.

Every value is computed by the post's snippet, snippets/coordination_tax.py: the cited multipliers (about 4x and
15x the tokens of a chat; Anthropic, "How we built our multi-agent research system", 13 June 2025) applied to an
illustrative 40,000-token chat. Because the base is illustrative, the bars are dashed outlines with the word
"illustrative" (hrn_fig_design.md section 5); one series, so ink and neutral, no role colour.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure, Box  # noqa: E402
from coordination_tax import rows, coordination_tax  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
ROWS = rows()
TAX, CHATS = coordination_tax()
assert [(s, m, t) for s, m, t, _ in ROWS] == [("one chat turn", 1, 40_000), ("single agent in a loop", 4, 160_000),
                                              ("orchestrator with sub-agents", 15, 600_000)]
assert (TAX, CHATS) == (440_000, 11)
for phrase in ("about 4× more tokens than chat interactions", "about 15× more tokens than chats",
               "an illustrative task whose chat form costs 40,000 tokens", "440,000 tokens, eleven chats' worth",
               "(13 June 2025)"):
    assert phrase in BODY, phrase

fig = Figure(
    "02-coordination-tax", "An orchestrator costs eleven chats more than one agent",
    "A horizontal bar chart of tokens per task, with dashed illustrative bars on one axis from 0 to 600,000. "
    "One chat turn uses 40,000 tokens; a single agent in a loop 160,000, four times the chat; an orchestrator "
    "with sub-agents 600,000, fifteen times. A brace under the axis spans 160,000 to 600,000 and is labelled the "
    "coordination tax, 440,000 tokens or eleven chats. Multipliers cited from Anthropic, 13 June 2025.",
    subtitle="Multipliers cited from Anthropic (13 June 2025), applied to an illustrative 40,000-token task.",
    data_w=True)

X0, X1, HI = 248, 720, 600_000
TICKS = [0, 200_000, 400_000, 600_000]
TOP, ROW, BAR = 112, 80, 48


def sx(v):
    return X0 + (X1 - X0) * v / HI


def fmt(v):
    return f"{v:,.0f}"


plot_bottom = TOP + 3 * ROW
with fig.data():
    for t in TICKS:
        fig.edge((sx(t), TOP), (sx(t), plot_bottom), color="grid", width=0.75)
        fig.text(sx(t), plot_bottom + 20, fmt(t), "tick", anchor="middle")
    fig.edge((X0, TOP), (X0, plot_bottom), color="ink-muted", width=1)
LABELS = {"one chat turn": "One chat turn", "single agent in a loop": "Single agent in a loop",
          "orchestrator with sub-agents": "Orchestrator, sub-agents"}
for k, (shape, m, tokens, _) in enumerate(ROWS):
    y = TOP + 16 + k * ROW
    fig.text(40, y + 29, LABELS[shape], "label")
    bar = Box(X0, y, sx(tokens) - X0, BAR)
    fig.fill(bar, "neutral-soft", fit=False)
    fig.outline(bar, "ink-muted", width=1.5, dash="proj")
    fig.text(sx(tokens) + 8, y + 29, f"{fmt(tokens)}, {m}× the chat" if m > 1 else fmt(tokens), "value",
             color="ink")
fig.text(X0 + (X1 - X0) / 2, plot_bottom + 44, "tokens per task", "note", anchor="middle")
with fig.data():
    fig.edge((sx(160_000), TOP + 16 + ROW + BAR), (sx(160_000), plot_bottom + 24), color="ink-muted", dash="ref")
fig.brace(sx(160_000), sx(600_000), plot_bottom + 68,
          label=f"coordination tax: {fmt(TAX)} tokens, {CHATS:.0f} chats", side="below")
fig.legend(40, plot_bottom + 72, [dict(color="ink-muted", label="illustrative", mark="dashed-outline")])
fig.write()
