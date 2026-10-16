"""Post 17, section 9: one task claimed exclusively at every step, and still run twice.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/diagrams/src/03-at-least-once.py
Writes posts/17-parallel-agents-shared-repo/diagrams/03-at-least-once.svg.
A timeline (hrn_fig_design.md section 4), computed: the script imports
posts/17-parallel-agents-shared-repo/snippets/leases.py, runs its simulate() (the companion's TaskBoard with the
snippet's lease and sweeper on a simulated clock), and draws every event of the at-least-once scene at its
simulated time, asserting each one against the snippet's log. Roles: claims and work orange (act), the lease and
the sweeper purple (gate), done/ and the file green (state), the refused completion red (error).
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("leases", POST / "snippets" / "leases.py")
snippet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snippet)

(events, counts, final), _ = snippet.simulate()
LEASE = snippet.LEASE_S
assert LEASE == 900
EXPECT = [
    (0, "agent-a", "claims task-7; lease to t=900"),
    (300, "agent-a", "renews, then goes quiet; lease to t=1200"),
    (900, "sweeper", "lease still live, nothing to do"),
    (1200, "sweeper", "lease expired: task-7 back to open/ (attempt 1)"),
    (1210, "agent-b", "claims task-7"),
    (1500, "agent-b", "does the work: settings.toml written"),
    (1500, "agent-b", "completes: task-7 in done/"),
    (1800, "agent-a", "wakes, does the work: settings.toml unchanged"),
    (1800, "agent-a", "completion refused: 'agent-a' has not claimed 'task-7'"),
]
assert events == EXPECT, events
assert counts == {"open": 0, "claimed": 0, "done": 1} and final == "retries = 3\n"

fig = Figure(
    "03-at-least-once", "Every claim was exclusive, and task-7 still ran twice",
    "A timeline in simulated seconds from 0 to 1,800 in three lanes. Agent A claims task-7 at 0, renews its "
    "900-second lease at 300 and goes quiet. On the board lane the sweeper finds the lease live at 900 and "
    "expired at 1,200, and puts task-7 back in open. Agent B claims it at 1,210, works, and at 1,500 writes "
    "settings.toml and completes the task into done. At 1,800 agent A wakes and does the same work, which finds "
    "settings.toml unchanged, and its completion is refused because it no longer holds the claim. One task, two "
    "executions, one effect.",
    subtitle=f"Computed: snippets/leases.py on the companion's board; simulated seconds, a {LEASE}-second lease.",
    data_w=True)

X0, X1, TMAX = 216, 864, 1800          # 0.36 units a second, so 300-second ticks land on the 4-unit grid


def x(t):
    return X0 + (X1 - X0) * t / TMAX


def xs(t):
    """x(t) snapped to the 4-unit grid, for labels."""
    return 4 * round(x(t) / 4)


LANES = {"agent A": 168, "board": 280, "agent B": 392}
for name, y in LANES.items():
    fig.text(40, y + 5, name, "head")
    fig.edge((X0, y), (X1, y), color="grid", width=0.75)

# agent A: works, renews, goes quiet, wakes
ya = LANES["agent A"]
fig.fill(Box(x(0), ya - 8, x(300) - x(0), 16), "act-soft")
fig.outline(Box(x(0), ya - 8, x(300) - x(0), 16), "act", width=1)
fig.text(x(0), ya - 20, "claims", "label")
fig.text(x(300) + 4, ya - 20, "renews", "label")
with fig.data():
    fig.edge((x(300), ya), (x(1800) - 8, ya), color="ink-muted", width=1.5, dash="proj")
fig.text(x(750), ya + 28, "quiet: a hung call", "note", anchor="middle")
fig.marker(x(1800), ya, "diamond", "error", size=10)
fig.text(x(1800), ya - 20, "wakes; settings.toml unchanged", "label", anchor="end")
fig.text(x(1800), ya + 28, "completion refused", "label", anchor="end", color="error-ink")

# the lease and the sweeper
yb = LANES["board"]
fig.fill(Box(x(300), yb - 36, x(1200) - x(300), 16), "gate-soft")
fig.outline(Box(x(300), yb - 36, x(1200) - x(300), 16), "gate", width=1)
fig.text(x(300) + 8, yb - 44, f"agent A's lease, renewed at 300, runs {LEASE} s", "note")
for t in (900, 1200):
    fig.marker(x(t), yb, "diamond", "gate", size=10)
fig.text(x(900), yb + 28, "sweep: live", "label", anchor="middle")
fig.text(x(1200) + 8, yb + 28, "sweep: expired, reopened", "label")
fig.marker(x(1500), yb, "square", "state", size=10)
fig.text(x(1500) + 12, yb - 12, "task-7 in done/", "label", color="state-ink")

# agent B: claims, works, completes
yc = LANES["agent B"]
fig.fill(Box(x(1210), yc - 8, x(1500) - x(1210), 16), "act-soft")
fig.outline(Box(x(1210), yc - 8, x(1500) - x(1210), 16), "act", width=1)
fig.text(xs(1210) - 4, yc - 20, "claims at 1,210", "label", anchor="end")
fig.text(x(1500), yc + 28, "writes settings.toml, completes", "label", anchor="end")

# the axis
fig.edge((X0, 440), (X1, 440), color="ink-muted", width=1)
for t in range(0, 1801, 300):
    fig.edge((x(t), 440), (x(t), 444), color="ink-muted", width=1)
    fig.text(x(t), 464, f"{t:,}", "tick", anchor="middle")
fig.text(X0 - 16, 464, "s", "tick", anchor="end")

fig.caption("Idempotent work made the second run change nothing; the ownership check refused its completion.")
fig.write()
