"""Post 20, section 2: the two axes that sort any option, with the four shapes and a harness of one's own placed.

Run from the series root:  uv run python posts/20-sdk-landscape/diagrams/src/02-build-vs-buy.py
Writes posts/20-sdk-landscape/diagrams/02-build-vs-buy.svg.
Placements, each from a page consulted 16 October 2026 (PLACED below): the Claude Agent SDK runs Claude models, also
through Amazon Bedrock, Google Cloud and Microsoft Foundry (Agent SDK quickstart); the Codex harness uses OpenAI's
provider by default and takes custom model providers in its configuration (Codex "Advanced configuration"); the
OpenAI Agents SDK documents non-OpenAI providers through built-in integration points ("Models"); LangGraph "does not
abstract prompts or architecture", so its nodes call whatever model the team wires in; this series' builds drive one
provider's client behind a `Model` protocol (code/24-minimal-harness models.py). The cells are categories, not
measured positions. Roles: products are neutral cards; nothing here is a model call, an action, state or a gate.
No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("**how much of the loop the product owns**", "**whether it is tied to one provider's models**",
               '"does not abstract prompts or architecture"', "a loop over one client SDK",
               "The figure below places the options on both"):
    assert phrase in BODY, phrase

# (column, row) -> entries; column 0 the team draws the loop, 1 the product ships it; row 0 one provider, 1 any
PLACED = {
    (1, 0): [("Claude Agent SDK", "Claude models, through several clouds"),
             ("Codex harness", "OpenAI by default; other providers configured")],
    (1, 1): [("OpenAI Agents SDK", "other providers through integration points")],
    (0, 1): [("LangGraph", "any model a node calls"), ("a harness of one's own", "any model behind a seam")],
    (0, 0): [("a loop over one client SDK", "this series' builds, behind a model seam")],
}
COLS = ["the team draws the loop", "the product ships the loop"]
ROWS = [["one provider's", "models, by default"], ["any provider's", "models"]]

fig = Figure(
    "02-build-vs-buy", "Who owns the loop, and whose models it runs",
    "Two axes and four cells. Across: the team draws the loop, or the product ships the loop. Down: one provider's "
    "models by default, or any provider's models. The product ships the loop and runs one provider's models: the "
    "Claude Agent SDK, Claude models through several clouds, and the Codex harness, OpenAI by default with other "
    "providers configured. The product ships the loop and runs any provider's models: the OpenAI Agents SDK, other "
    "providers through integration points. The team draws the loop over any provider's models: LangGraph, any model "
    "a node calls, and a harness of one's own, any model behind a seam. The team draws the loop over one provider: a "
    "loop over one client SDK, as this series' builds are, behind a model seam.",
    subtitle="Each option placed by what its documentation said in October 2026; cells are categories, not scores.",
    data_w=True)

GX, CW, GAP, GY, RH = 216, 344, 16, 136, 144
for c, label in enumerate(COLS):
    fig.text(GX + c * (CW + GAP) + 16, GY - 16, label, "head")
for r, lines in enumerate(ROWS):
    for k, line in enumerate(lines):
        fig.text(40, GY + r * (RH + GAP) + 32 + 20 * k, line, "head" if k == 0 else "label")
fig.arrow((GX, GY + 2 * RH + GAP + 12), (GX + 2 * CW + GAP, GY + 2 * RH + GAP + 12),
          label="more of the loop shipped", side="below")
for (c, r), entries in PLACED.items():
    x, y = GX + c * (CW + GAP), GY + r * (RH + GAP)
    fig.card(x, y, CW, RH)
    for k, (name, note) in enumerate(entries):
        fig.text(x + 16, y + 36 + 64 * k, name, "head")
        fig.text(x + 16, y + 60 + 64 * k, note, "note")

fig.caption("A model seam is what lets a hand-written loop move down a row without a rewrite.")
fig.write()
