"""Post 04, section 7: the loop that trains models inside harnesses, one measurement of it, and its side effect.

Run from the series root:  uv run python posts/04-harness-beats-model/diagrams/src/03-co-training-loop.py
Writes posts/04-harness-beats-model/diagrams/03-co-training-loop.svg.
The four steps are Trivedy's ("The Anatomy of an Agent Harness", LangChain blog, 10 March 2026): "Useful primitives
are discovered, added to the harness, and then used when training the next generation of models. As this cycle
repeats, models become more capable within the harness they were trained in." The three numbers are cited from Ding
et al. (arXiv:2608.05156, 2026, abstract read 2026-10-14) and the side effect from the same Trivedy article; each is
asserted against index.md below. Roles: the harness steps are neutral, the model steps blue (model), the side
effect red (error: a regression).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

# cited from Ding et al., 2026: gain from discovered skills (points), passed rate with no scaffold (%), retention (%)
DING = {"gain": 8.1, "no_scaffold": 27.7, "retention": 85.2}
for phrase in ("Useful primitives are discovered, added to the harness, and then used when training the next "
               "generation of models. As this cycle repeats, models become more capable within the harness they "
               "were trained in.",
               "improve the passed rate by 8.1 percentage points", "still passes 27.7% \"without any external scaffold\"",
               "a retention of 85.2%", "\"Opus 4.6 in Claude Code scores far below Opus 4.6 in other harnesses\"",
               "(LangChain blog, 10 March 2026)", "creates this overfitting"):
    assert phrase in BODY, phrase
# the with-skills rate implied by the definition (post / with-skills); stated nowhere, so not drawn
assert 32 < DING["no_scaffold"] / (DING["retention"] / 100) < 33

fig = Figure(
    "03-co-training-loop", "Models are trained inside harnesses, and fit to them",
    "A cycle of four cards, clockwise: a useful primitive is discovered in a harness; it is added to the harness; "
    "the next model is trained with it; the model becomes more capable inside that harness. The first two are "
    "neutral harness steps, the last two blue model steps, and the cycle repeats each generation. Beside it, a card "
    "of cited measurements from Ding et al., 2026: discovered skills add 8.1 points on FeatureBench, the distilled "
    "model passes 27.7% with no scaffold, and 85.2% of the with-skills rate is kept. A red card names the side "
    "effect, overfitting: Opus 4.6 in Claude Code scores far below Opus 4.6 in other harnesses (Trivedy, 10 March "
    "2026).",
    subtitle="The loop as Trivedy describes it, 10 March 2026; cited measurements beside it.",
    data_w=True)

W, H, Y1, Y2 = 200, 96, 136, 320
STEPS = [(40, Y1, ["1. a useful primitive", "is discovered in", "a harness"], None),
         (280, Y1, ["2. it is added to", "the harness"], None),
         (280, Y2, ["3. the next model is", "trained with it"], "model"),
         (40, Y2, ["4. the model is more", "capable inside", "that harness"], "model")]
for x, y, lines, color in STEPS:
    fig.card(x, y, W, H, lines=lines, color=color, leading=20)
fig.arrow((240, Y1 + H / 2), (280, Y1 + H / 2))
fig.arrow((380, Y1 + H), (380, Y2))
fig.arrow((280, Y2 + H / 2), (240, Y2 + H / 2))
fig.arrow((140, Y2), (140, Y1 + H))
fig.text(260, (Y1 + H + Y2) / 2 + 5, "each generation", "note", anchor="middle")

RX, RW = 520, 400
fig.card(RX, Y1, RW, None, heading="Measured: Ding et al., 2026, cited",
         lines=[f"discovered skills: +{DING['gain']} points, FeatureBench",
                f"distilled, no scaffold: {DING['no_scaffold']}% passed",
                f"kept: {DING['retention']}% of the with-skills rate"], fit=True)
fig.card(RX, Y2, RW, None, heading="Side effect: overfitting",
         lines=["Opus 4.6 in Claude Code scores far below", "Opus 4.6 in other harnesses",
                "(Trivedy, 10 March 2026, cited)"], color="error", fit=True)
fig.caption("Optimise the fit to the task, not the brand: the native harness is a baseline to measure against, not a guaranteed best.")
fig.write()
