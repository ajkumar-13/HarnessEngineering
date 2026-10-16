"""Post 17, the hero: the companion's task board mid-flight, three agents and no coordinator.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/diagrams/src/01-shared-repo-swarm.py
Writes posts/17-parallel-agents-shared-repo/diagrams/01-shared-repo-swarm.svg.
A state form (hrn_fig_design.md section 4): the board's three directories are state cards, green; the .claims
token directory is a gate, purple, because its job is to exclude; the agents are act cards, orange. The board
drawn is computed: the script drives the companion's TaskBoard (code/17-parallel-agents/src, unchanged) through
the sequence the figure shows, asserts every directory listing it draws, and asserts that a second exclusive
create of grace's token raises FileExistsError.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "17-parallel-agents" / "src"))
from parallel_agents import TaskBoard  # noqa: E402

AGENTS = ("ada", "linus", "grace")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    board = TaskBoard(root)
    for i in range(1, 8):
        board.add(f"task-{i}")
    finished = {}
    for agent in AGENTS:                        # each agent claims and finishes one task
        finished[agent] = board.claim(agent)
        board.complete(finished[agent], agent)
    held = {agent: board.claim(agent) for agent in AGENTS}   # then each takes the next one
    LIST = {d: sorted(p.name for p in (root / d).iterdir()) for d in ("open", "claimed", "done", ".claims")}
    try:                                        # a second agent reaching for grace's task
        os.close(os.open(root / ".claims" / held["grace"], os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        LOSER = "created"
    except FileExistsError:
        LOSER = "FileExistsError"

assert finished == {"ada": "task-1", "linus": "task-2", "grace": "task-3"}, finished
assert held == {"ada": "task-4", "linus": "task-5", "grace": "task-6"}, held
assert LIST == {"open": ["task-7"], "claimed": ["task-4.ada", "task-5.linus", "task-6.grace"],
                "done": ["task-1", "task-2", "task-3"],
                ".claims": [f"task-{i}" for i in range(1, 7)]}, LIST
assert LOSER == "FileExistsError"

fig = Figure(
    "01-shared-repo-swarm", "No coordinator: an exclusive create decides each claim",
    "The companion's task board mid-flight. On the left, three directories in the repository drawn as state: "
    "open holds task-7; claimed holds task-4.ada, task-5.linus and task-6.grace; done holds task-1, task-2 and "
    "task-3. Below them the .claims directory holds one token per task taken, task-1 to task-6. On the right, "
    "three agents with no coordinator: ada holds task-4 and finished task-1, linus holds task-5 and finished "
    "task-2, and grace, who finished task-3, has just claimed task-6 in "
    "two steps, an exclusive create of the token .claims/task-6 and then the rename of open/task-6 to "
    "claimed/task-6.grace. A second agent creating the same token gets FileExistsError and moves on.",
    subtitle="Computed from the companion's board: three tasks done, three held, one open, one token per claim.",
    data_w=True)

# the board: state, in the repository
board_box = Box(40, 112, 472, 360)
fig.outline(board_box, "state", width=1.5, radius=8)
fig.text(56, 140, "task board: files in the repository", "head", color="state")
COLS = [("open/", LIST["open"]), ("claimed/", LIST["claimed"]), ("done/", LIST["done"])]
for k, (name, files) in enumerate(COLS):
    x = 56 + k * 152
    fig.card(x, 160, 136, 152, color="state")
    fig.text(x + 16, 188, name, "code")
    fig.text(x + 16, 192 + 20, f"{len(files)} file{'s' if len(files) > 1 else ''}", "note")
    for j, f in enumerate(files):
        fig.text(x + 16, 244 + 24 * j, f, "code")
fig.outline(Box(216, 272, 120, 28), "state", width=2.5, radius=4)       # the file grace's rename made

fig.card(56, 336, 440, 120, color="gate")
fig.text(72, 364, ".claims/", "code")
fig.text(152, 364, "one token per task taken", "note")
for i, tok in enumerate(LIST[".claims"]):
    fig.text(72 + (i % 3) * 136, 396 + 28 * (i // 3), tok, "code")
fig.outline(Box(336, 404, 68, 28), "gate", width=2.5, radius=4)        # the token grace created

# the agents: act, no coordinator
fig.text(568, 140, "three agents, no coordinator", "head")
for k, agent in enumerate(("ada", "linus")):
    y = 160 + 72 * k
    fig.card(568, y, 352, 56, color="act")
    fig.text(584, y + 34, agent, "label", bold=True)
    fig.text(664, y + 34, f"holds {held[agent]}; finished {finished[agent]}", "label")
fig.card(568, 304, 352, 168, color="act")
fig.text(584, 332, "grace", "label", bold=True)
fig.text(664, 332, "claims task-6", "label")
fig.text(584, 364, "1  exclusive create of the token", "label")
fig.text(608, 388, "os.open(token, O_CREAT | O_EXCL)", "code")
fig.text(584, 420, "2  only then, the rename", "label")
fig.text(608, 444, "os.rename(src, dst)", "code")

fig.arrow((568, 388), (498, 412))       # step 1 lands in .claims/
fig.arrow((568, 324), (276, 314), via=((276, 324),))   # step 2 lands in claimed/, under done/

fig.caption(f"A second agent creating .claims/task-6 gets {LOSER} and moves on to task-7.")
fig.write()
