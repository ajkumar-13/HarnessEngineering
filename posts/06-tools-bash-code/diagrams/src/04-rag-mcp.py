"""Post 06, section 10: RAG-MCP's two measurements, a shorter menu against the whole catalogue.

Run from the series root:  uv run python posts/06-tools-bash-code/diagrams/src/04-rag-mcp.py
Writes posts/06-tools-bash-code/diagrams/04-rag-mcp.svg.
Every value is cited, not run: Gan and Sun, "RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via
Retrieval-Augmented Generation" (arXiv:2505.03275, 6 May 2025), Table 1: "Blank Conditioning" (every MCP
description in the prompt) against RAG-MCP (retrieve the best match and send only its description), on the web-search subset of
MCPBench with qwen-max-0125. Drawn as hollow marks with the word "cited" and the grade, as hrn_fig_design.md
section 5 asks; the grade is the one section 10 gives. The ratios printed are computed here and asserted against
the body's wording.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

# source: Gan and Sun, arXiv:2505.03275, 6 May 2025, Table 1 (Blank Conditioning, RAG-MCP)
ACCURACY = [("every description", 13.62), ("retrieval first", 43.13)]       # % of trials, right server selected
PROMPT = [("every description", 2133.84), ("retrieval first", 1084.00)]      # average prompt tokens
for phrase in ("13.62% of the time", "raised it to 43.13%", "from 2,133.84 to 1,084.00 tokens",
               "the table gives 49%", "web-search subset of MCPBench", "`qwen-max-0125`",
               "the result is firm, for one model and one task family", "(Gan and Sun, arXiv, 6 May 2025)"):
    assert phrase in BODY, phrase
ratio = ACCURACY[1][1] / ACCURACY[0][1]
cut = 1 - PROMPT[1][1] / PROMPT[0][1]
assert 3.1 < ratio < 3.2 and round(cut * 100) == 49
assert "chose right three times as often and cost half the prompt" in BODY

fig = Figure(
    "04-rag-mcp", "A shorter menu chose the right tool three times as often",
    "Two cited measurements from the RAG-MCP paper, drawn as hollow marks: with every MCP server description in "
    "the prompt, the model selected the right server in 13.62% of trials and read 2,133.84 prompt tokens on "
    "average; retrieving the best match first raised selection to 43.13%, 3.2 times as often, and cut "
    "the average prompt to 1,084.00 tokens, 49% fewer. Both marked cited, graded firm: one model, qwen-max-0125, "
    "on the web-search subset of MCPBench.",
    subtitle="Cited: Gan and Sun, arXiv, 6 May 2025, Table 1; qwen-max-0125 on MCPBench web search.",
    data_w=True)

left, right = fig.row(2, y=136, h=264)
for box, rows, hi, ticks, unit, fmt, axis in (
        (left, ACCURACY, 50, [0, 10, 20, 30, 40, 50], "%", lambda v: f"{v:.2f}", "trials with the right server, %"),
        (right, PROMPT, 3000, [0, 1000, 2000, 3000], "", lambda v: f"{v:,.2f}", "average prompt tokens")):
    body = fig.panel(box)
    fig.dot_plot(body, [(label, [v]) for label, v in rows], 0, hi, ticks, colors=("ink",), hollow=True,
                 unit=unit, values=True, label_w=144, pad_right=72, fmt_tick=lambda v: f"{v:,g}", fmt_value=fmt,
                 axis_label=axis)

fig.text(left.x, 448, f"{ratio:.1f} times as often, cited, firm", "label")
fig.text(right.x, 448, f"{cut:.0%} fewer tokens, cited, firm", "label")
fig.legend(left.x, 472, [dict(color="ink", label="cited value", mark="circle", hollow=True)], direction="row")
fig.caption("One model and one task family: read it as a shape, not a constant.")
fig.write()
