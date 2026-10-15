"""Post 14, hero (section 1): what a run inside the sandbox can reach, and the five constraints that bound it.

Run from the series root:  uv run python posts/14-permissions-sandboxes/diagrams/src/01-sandbox-boundary.py
Writes posts/14-permissions-sandboxes/diagrams/01-sandbox-boundary.svg.
A section 3 boundary form of hrn_fig_design.md: the sandbox is a gate-coloured frame; the bash tool (act, orange)
and the mounted workspace (state, green) are inside; each of the five constraints of section 1 is a gate bar on
the frame where one reach crosses it, and the reach is a red stub ending at that bar. The constraint names and
the outside targets are phrases of the post's body, asserted below. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("- **An allow-list.** Only named programs run", "- **A path boundary.** The tool reads and writes inside one directory",
               "- **Network isolation.** Default-deny", "- **A resource limit.** Processor and wall-clock time, memory, disk",
               "- **An ephemeral runtime.** A fresh container, wiped after the run, so a compromise does not accumulate",
               "The *mounted workspace* deliberately is not ephemeral", "a persistence channel a fresh container does not close",
               "tool that can publish counts as egress", "the five gate bars on the frame of the figure above"):
    assert phrase in BODY, phrase

ROWS = [  # (constraint on the frame, what it keeps out of reach)
    ("allow-list", "every program not named"),
    ("path jail", "the home directory, other projects"),
    ("network", "the internet beyond listed domains"),
    ("resource limit", "the host's processor, memory, disk"),
    ("ephemeral runtime", "the next run"),
]

fig = Figure(
    "01-sandbox-boundary", "A sandbox bounds what a run can reach",
    "A purple frame labelled sandbox holds an orange bash tool card (named programs, inside /work, no network, "
    "time-limited, fresh each run) and a green workspace card, mounted and kept. "
    "Five red arrows leave the bash tool and each ends at a purple gate bar on the frame's right edge, named "
    "allow-list, path jail, network, resource limit and ephemeral runtime, with the word blocked beside each. "
    "Outside the frame, in neutral cards, what each keeps out of reach: every program not named; the home "
    "directory and other projects; the internet beyond the listed domains; the host's processor, memory and disk; and "
    "the next run.",
    subtitle="Five constraints sit on one frame; every reach past it ends at a gate.",
    data_w=True)

FRAME = Box(40, 128, 424, 328)
YS = [176 + 44 * k for k in range(len(ROWS))]
fig.outline(FRAME, "gate", width=1.5, radius=8)
fig.text(40, 120, "sandbox", "head", color="gate")
fig.card(72, 152, 176, 224, heading="bash tool", lines=["named programs", "inside /work", "no network", "time-limited", "fresh each run"], style="label", color="act")
fig.card(72, 392, 352, 48, heading="workspace: mounted and kept", color="state")

fig.text(568, 120, "out of reach", "head")
for y, (gate, target) in zip(YS, ROWS):
    fig.arrow((248, y), (460, y), color="error")
    fig.text(452, y - 8, gate, "label", anchor="end", color="gate")
    fig.fill(Box(460, y - 16, 8, 32), "gate")
    fig.text(484, y + 5, "blocked", "label", color="error")
    fig.card(568, y - 18, 352, 36, color=None)
    fig.text(584, y + 5, target, "label")

fig.caption("The workspace outlives the run, so a poisoned file written there is a channel the box does not close.")
fig.write()
