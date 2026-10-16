"""Post 23, section 8: where the vendor's boundary falls for a model API, an SDK the team hosts and a hosted runtime.

Run from the series root:  uv run python posts/23-economics-haas/diagrams/src/02-llm-api-vs-haas.py
Writes posts/23-economics-haas/diagrams/02-llm-api-vs-haas.svg.
No numbers. The placement follows the post's tier table: a model API keeps only the model behind the vendor's
boundary; an SDK the team hosts is the vendor's code (loop, tools, hooks, context management) run on the team's
machines (Anthropic, "Agent SDK overview"; post 20); a hosted runtime such as Claude Managed Agents or Amazon Bedrock
AgentCore Runtime keeps the loop and the session state on the vendor's side (Anthropic and AWS pricing pages,
consulted October 2026). What each bills is the table's "What the harness costs" column, shortened.
Roles (hrn_fig_design.md): the model is blue; the vendor's boundary is a gate-coloured frame (a trust boundary,
section 3); harness components are neutral cards named by the series' component names.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("**An SDK the team hosts**", "**A hosted agent runtime** runs the loop on the vendor's side",
               "the token bill does not", "The figure below draws where the vendor's boundary falls"):
    assert phrase in BODY, phrase

COLUMNS = [
    ("Model API", None, ("the team builds", ["loop, tools, hooks", "context management", "state"]), "tokens"),
    ("SDK the team hosts", None,
     ("the team runs", ["the vendor's SDK: loop,", "tools, hooks, context", "management"]), "tokens + own compute"),
    ("Hosted runtime", ["loop, tools, hooks", "context management, state"],
     ("the team sends", ["a task in", "an agent run out"]), "tokens + runtime"),
]

fig = Figure(
    "02-llm-api-vs-haas", "Renting the loop moves it inside the vendor's boundary",
    "Three columns, each with the vendor's boundary drawn as a purple frame. Model API: only the model is inside; "
    "the team builds the loop, tools, hooks, context management and state; it bills tokens. SDK the team hosts: "
    "only the model is inside; the team runs the vendor's SDK, which supplies the loop, tools, hooks and context "
    "management; it bills tokens plus the team's own compute. Hosted runtime: the model, the loop, tools, hooks, "
    "context management and state are all inside; the team sends a task in and gets an agent run out; it bills "
    "tokens plus runtime.",
    subtitle="What sits behind the vendor's boundary in each tier, and what each one bills.",
    data_w=True)

W, GUT = 272, 32
for k, (head, inside, (side, lines), bills) in enumerate(COLUMNS):
    x = 40 + k * (W + GUT)
    fig.text(x, 120, head, "head")
    frame = Box(x, 136, W, 176)
    fig.outline(frame, "gate", width=1.5, radius=8)
    fig.text(x + 16, 160, "vendor", "label", color="gate")
    fig.card(x + 16, 172, W - 32, 48, lines=["model"], color="model")
    if inside:
        fig.card(x + 16, 228, W - 32, None, lines=inside, fit=True)
    fig.text(x, 336, side, "note")
    fig.card(x, 348, W, None, lines=lines, fit=True)
    fig.text(x, 476, "bills " + bills, "label", bold=True)

fig.caption("Every tier bills tokens; renting the loop adds a runtime meter beside them.")
fig.write()
