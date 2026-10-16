"""Post 23, section 9: the three rungs, build, adopt an SDK, rent a runtime, on two axes, with the crossover.

Run from the series root:  uv run python posts/23-economics-haas/diagrams/src/03-build-vs-rent.py
Writes posts/23-economics-haas/diagrams/03-build-vs-rent.svg.
The axes are how much of the harness is bought and what it costs to leave; post 20's figure 02 sorts the same
products by who owns the loop and whose models it runs, and the post names that difference. The rungs are
categories, not measured positions. Two numbers: the 803 implementation lines of this series' two builds, counted
by post 20's snippets/build_cost.py (imported here and re-run); and the crossover of 1.5 million runs a month,
computed by snippets/rent_or_build.py from a placeholder 30,000 dollars a month and the 0.02-dollar runtime fee of a
fifteen-minute Claude Managed Agents session (Anthropic, "Pricing", consulted October 2026), both asserted.
Roles: products and choices are neutral cards; nothing here is a model call, an action, state or a gate.
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bc = load("build_cost", POST.parent / "20-sdk-landscape" / "snippets" / "build_cost.py")
rb = load("rent_or_build", POST / "snippets" / "rent_or_build.py")
impl2, tests2, _ = bc.count("code/25-harness-plus")
union = impl2 + bc.lines([bc.ROOT / "code/24-minimal-harness/src/minimal_harness/verify.py"])
assert (union, union + tests2) == (803, 1036), (union, tests2)
fee = rb.session_metered(15 * 60)
runs = rb.crossover(fee)
assert round(fee, 2) == 0.02 and round(runs) == 1_500_000
for phrase in ("803 implementation lines, 1,036 with tests", "1,500,000 runs a month",
               "who owns the loop and whose models it runs", "how much of the harness is bought and what it costs"):
    assert phrase in BODY, phrase

fig = Figure(
    "03-build-vs-rent", "Each rung buys more of the harness and costs more to leave",
    "Three cards climbing from bottom left to top right on two axes: more of the harness bought, across, and a "
    "higher cost to leave, upward. Build: the team owns all of it; this series' two builds are 803 lines with no "
    "compaction. Adopt an SDK: the loop, tools and hooks are bought; the tie is a dependency. Rent a runtime: the "
    "session and state are bought too; the tie is the loop, the hook interface and the trace format. A note gives "
    "the runtime-fee crossover: 30,000 dollars a month over 0.02 dollars for a fifteen-minute session is 1.5 million runs a month.",
    subtitle="Rungs placed by category, not measured; the crossover is illustrative, from snippets/rent_or_build.py.",
    data_w=True)

O = (72, 448)
fig.arrow(O, (920, 448), label="more of the harness bought", side="below")
fig.arrow(O, (72, 112))
fig.text(88, 124, "higher cost to leave", "note")
RUNGS = [(104, 328, "Build", ["the team owns all of it", f"{union} lines, no compaction"]),
         (376, 228, "Adopt an SDK", ["loop, tools, hooks bought", "tie: a dependency"]),
         (648, 128, "Rent a runtime", ["session and state bought too", "tie: loop, hooks, traces"])]
for x, y, head, lines in RUNGS:
    fig.card(x, y, 264, None, heading=head, lines=lines, fit=True)
fig.text(648, 304, "Crossover, fifteen-minute sessions:", "note")
fig.text(648, 328, f"${rb.OWNED_MONTHLY:,} a month / ${fee:.2f} a session", "label")
fig.text(648, 352, f"= {runs / 1e6:.1f} million runs a month", "label", bold=True)
fig.caption("A few thousand runs a month sits far below the crossover, so volume rarely decides.")
fig.write()
