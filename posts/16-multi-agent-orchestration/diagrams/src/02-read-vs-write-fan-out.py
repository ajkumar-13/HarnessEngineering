"""Post 16, section 4: the read fan-out merges with nothing to reconcile; the write fan-out does not.

Run from the series root:  uv run python posts/16-multi-agent-orchestration/diagrams/src/02-read-vs-write-fan-out.py
Writes posts/16-multi-agent-orchestration/diagrams/02-read-vs-write-fan-out.svg.
A section 3 form of hrn_fig_design.md, computed: the script imports snippets/fan_out.py, runs its four read workers
and four write workers and both merges, and draws what they return. Every count and value on the figure comes from
those calls and is asserted against the body. Roles: a dispatched worker is an action (orange), the shared settings
file is state (green), the lead is neutral, and a disagreement is an error (red; dashed where the merge cannot see
it).
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import fan_out as fo  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")

# the read fan-out
reads = [fo.read_worker(s) for s in fo.SERVICES]
merged, conflicts = fo.read_merge(reads)
assert merged == fo.read_single() and conflicts == 0
per_service = merged["per_service"]
totals = merged["totals"]

# the write fan-out
writes = [fo.write_worker(f) for f in fo.FEATURES]
values, conflicts_w, silent = fo.write_merge(writes)
assert conflicts_w == ["shared.timeout", "shared.date_format"] and silent == ["session-lifetime"]
picked = {}
for r in map(json.loads, writes):
    for e in r["edits"]:
        picked.setdefault(e["key"], []).append(e["value"])
assert picked["shared.timeout"] == ['"30s"', "10"]
assert picked["shared.date_format"] == ['"iso8601"', '"%d/%m/%Y"']
assert values["http.session_ttl_s"] == "3600" and values["cache.session_minutes"] == "30"
for phrase in ('a timeout of `"30s"` against `10`', "`http.session_ttl_s = 3600` and `cache.session_minutes = 30`",
               "two shared keys come back written twice with different values"):
    assert phrase in BODY, phrase

fig = Figure(
    "02-read-vs-write-fan-out", "Reads never have to agree; writes do",
    f"Two panels computed by the post's fan_out.py. Left, a read fan-out: four workers each count the errors in one "
    f"service log, api {per_service['api']}, auth {per_service['auth']}, billing {per_service['billing']} and "
    f"search {per_service['search']}; the lead's merge gives E101 {totals['E101']}, E204 {totals['E204']}, E307 "
    f"{totals['E307']} and E410 {totals['E410']}, equal to the single agent's answer, with 0 conflicts. Right, a "
    f"write fan-out: workers for retry, http, logging and cache edit one settings file. shared.timeout is written "
    f"as \"30s\" and as 10, and shared.date_format as iso8601 and as %d/%m/%Y: 2 conflicts the merge sees. The "
    f"session lifetime is written as http.session_ttl_s = 3600 and cache.session_minutes = 30, an hour against "
    f"half an hour under different keys: 1 disagreement that merges cleanly.",
    subtitle="Computed by fan_out.py: four scripted workers per task, and the lead's merge of what they return.",
    data_w=True)

L, R, W = 40, 496, 424
fig.text(L, 128, "Read fan-out: one log each", "head")
fig.text(R, 128, "Write fan-out: one settings file", "head")
YS = [152, 212, 272, 332]

# left: four readers into the lead
for s, y, t in zip(fo.SERVICES, YS, (216, 244, 272, 300)):
    fig.card(L, y, 160, 40, color="act")
    fig.text(L + 16, y + 25, f"{s}: {per_service[s]} errors", "label")
    fig.arrow((L + 160, y + 20), (L + 224, t))
fig.card(L + 224, 192, 200, 132)
fig.text(L + 240, 224, "lead merges", "head")
fig.text(L + 240, 256, f"E101 {totals['E101']}, E204 {totals['E204']}", "label")
fig.text(L + 240, 280, f"E307 {totals['E307']}, E410 {totals['E410']}", "label")
fig.text(L + 240, 304, "= one agent's answer", "note")
fig.text(L, 412, "0 conflicts to reconcile", "label")
fig.text(L, 436, "results are independent by construction", "note")

# right: four writers into one shared file
for f, y in zip(fo.FEATURES, YS):
    fig.card(R, y, 104, 40, color="act")
    fig.text(R + 16, y + 25, f, "label")
    fig.arrow((R + 104, y + 20), (R + 144, y + 20))
FX, FW = R + 144, 280
fig.card(FX, 144, FW, 236, color="state")
fig.text(FX + 16, 168, "settings.toml", "code")
rows = [(196, "shared.timeout", '"30s" against 10'),
        (252, "shared.date_format", '"iso8601" against "%d/%m/%Y"')]
for y, key, both in rows:
    fig.outline(Box(FX + 8, y - 16, FW - 16, 52), "error", width=1.5, radius=4)
    fig.text(FX + 16, y + 4, key, "code")
    fig.text(FX + 16, y + 28, both, "label", color="error")
fig.outline(Box(FX + 8, 308, FW - 16, 64), "error", width=1.5, radius=4, dash="proj")
fig.text(FX + 16, 332, "http.session_ttl_s = 3600", "code")
fig.text(FX + 16, 360, "cache.session_minutes = 30", "code")
fig.text(R, 412, f"{len(conflicts_w)} keys written twice: conflicts the merge sees", "label", color="error")
fig.text(R, 436, f"{len(silent)} session lifetime, an hour against half an hour, merged cleanly", "label", color="error")
fig.text(R, 460, "dashed: the disagreement no key-level merge can see", "note")

fig.caption("The costly disagreement is the one that merges cleanly.")
fig.write()
