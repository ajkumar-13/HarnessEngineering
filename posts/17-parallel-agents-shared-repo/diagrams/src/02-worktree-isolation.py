"""Post 17, section 5: one repository, one worktree per agent, and one way back to main.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/diagrams/src/02-worktree-isolation.py
Writes posts/17-parallel-agents-shared-repo/diagrams/02-worktree-isolation.svg.
A boundary form (hrn_fig_design.md section 3): the repository and the worktrees are state cards, green; the
boundary the worktrees give is a gate-coloured frame labelled with what it isolates, files only; the merge gate
is a gate card, purple. The worktree paths and branch names are the post's `git worktree add` commands, and the
gate's condition and the list of what worktrees still share are the post's words, asserted below. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
TREES = [("ada", "../wt-ada", "agent/ada"), ("linus", "../wt-linus", "agent/linus"),
         ("grace", "../wt-grace", "agent/grace")]
for _, path, branch in TREES:
    assert f"git worktree add {path}" in BODY.replace("    ", " ").replace("   ", " ").replace("  ", " ") \
        and f"-b {branch}" in BODY, (path, branch)
for phrase in ("**They share one object database.**", "build the candidate merge and run the suite on that",
               "processes, network, environment variables and credentials", "A worktree isolates *files* and nothing else"):
    assert phrase in BODY, phrase

fig = Figure(
    "02-worktree-isolation", "One working copy per agent, one way back to main",
    "At the top, the main repository with one object database and one history. Below it, inside a frame "
    "labelled files only, three worktrees made by git worktree add, each a separate working copy on its own "
    "branch: ../wt-ada on agent/ada, ../wt-linus on agent/linus and ../wt-grace on agent/grace, each edited by "
    "its agent alone. Every branch goes down into one merge gate, which lands it on main only if the candidate "
    "merge builds and its tests pass. A note says what the worktrees still share: processes, network, "
    "environment variables and credentials.",
    subtitle="Worktrees share the repository's history; each branch lands only through the merge gate.",
    data_w=True)

# the repository
fig.card(336, 112, 288, 64, color="state")
fig.text(352, 138, "main repository", "label", bold=True)
fig.text(352, 162, "one object database, one history", "note")
fig.text(648, 168, "git worktree add, one per agent", "note")

# the boundary: files only
frame = Box(40, 216, 856, 160)
fig.outline(frame, "gate", width=1.5, radius=8)
fig.text(56, 240, "worktrees: isolate files only", "label", color="gate-ink")
cards = []
for k, (agent, path, branch) in enumerate(TREES):
    x = 64 + 280 * k
    fig.card(x, 256, 248, 104, color="state")
    fig.text(x + 16, 282, path, "code")
    fig.text(x + 16, 306, f"branch {branch}", "code")
    fig.text(x + 16, 336, f"{agent} edits here, alone", "label", color="act-ink")
    cards.append(Box(x, 256, 248, 104))
    fig.arrow((480, 176), (x + 124, 254))

# the merge gate and the way back
gate = Box(336, 408, 288, 64)
fig.card(gate.x, gate.y, gate.w, gate.h, color="gate")
fig.text(352, 434, "merge gate", "label", bold=True)
fig.text(352, 458, "candidate merge builds, tests pass", "note")
for b, xe in zip(cards, (400, 480, 560)):
    fig.arrow((b.x + b.w // 2, 360), (xe, 406))
fig.arrow((624, 440), (626, 128), via=((912, 440), (912, 128)))
fig.text(904, 116, "lands on main", "label", anchor="end", color="gate-ink")

# what is still shared
fig.text(56, 412, "still shared by every worktree:", "note")
fig.text(56, 436, "processes, network,", "note")
fig.text(56, 460, "environment variables, credentials", "note")

fig.caption("A worktree isolates files and nothing else; tasks that run untrusted code need a container.")
fig.write()
