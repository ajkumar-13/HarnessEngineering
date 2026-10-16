"""Post 16, section 6: the coordination tax of the read fan-out, in billed input tokens and in seconds.

Run from the series root:  uv run python posts/16-multi-agent-orchestration/diagrams/src/03-the-coordination-tax.py
Writes posts/16-multi-agent-orchestration/diagrams/03-the-coordination-tax.svg.
A section 5 chart of hrn_fig_design.md, computed and illustrative: the script runs snippets/fan_out.py's main()
(the same run the post quotes, about three seconds) and draws its read fan-out rows. Left, the input of each design
in input-rate tokens, split into the shared prefix (paid once per call; written once and read five times when
cached) and everything else; right, the simulated seconds of each call on one time axis, from the snippet's
latency table. Every number is asserted against the snippet's rows and against the post's quoted output. The
prefix and the lead's calls are neutral quantities (ink and neutral fills); a worker's time is an action (orange).
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure, num  # noqa: E402
import fan_out as fo  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
out = io.StringIO()
with contextlib.redirect_stdout(out):
    reads, writes, _ = fo.main()
printed = out.getvalue()
for line in printed.splitlines():
    assert line in BODY, line                     # the post quotes the whole output

P = fo.tokens(fo.PREFIX)
single, uncached, cached = reads
assert single[1] == 1 and uncached[1] == cached[1] == 6
REST_SINGLE = single[2] - P
REST_MULTI = uncached[2] - 6 * P
PREFIX_CACHED = P * fo.CACHE_WRITE + 5 * P * fo.CACHE_READ
assert round(PREFIX_CACHED + REST_MULTI) == cached[3] and uncached[3] == uncached[2]
ROWS = [("one agent", P, REST_SINGLE, single[3], "1 call"),
        ("lead + 4 workers", 6 * P, REST_MULTI, uncached[3], "6 calls"),
        ("the same, cached", PREFIX_CACHED, REST_MULTI, cached[3], "1 write, 5 reads")]
assert (single[3], uncached[3], cached[3]) == (11659, 18065, 12974) and 6 * P == 7188
assert fo.WORKER_S == [10, 10, 10, 90] and (fo.PLAN_S, fo.MERGE_S) == (5, 5)
assert (single[6], uncached[6]) == (120, 100)

fig = Figure(
    "03-the-coordination-tax", "The prefix is paid per call; the clock waits for the slowest",
    f"Two panels for the read fan-out, computed by the post's fan_out.py and illustrative. Left, input in input-rate "
    f"tokens. One agent: {num(single[3])}, of which {num(P)} is the shared prefix. Lead and four workers, "
    f"uncached: {num(uncached[3])}, of which {num(6 * P)} is the prefix paid six times. The same, cached: "
    f"{num(cached[3])}, the prefix written once and read five times. Right, simulated seconds on one axis. One "
    f"agent does pieces of 10, 10, 10 and 90 seconds in turn, 120 seconds. The lead plans for 5 seconds, four "
    f"workers run in parallel for 10, 10, 10 and 90, and the lead merges for 5: 100 seconds.",
    subtitle="Read fan-out, computed by fan_out.py at Claude Sonnet 4.6 rates (Anthropic, October 2026); "
             "illustrative.",
    data_w=True)

# ---- left: billed input -----------------------------------------------------------------------------------
fig.text(40, 128, "Input, in input-rate tokens", "head")
X0, PX = 200, 224 / 20000
YS = [176, 248, 320]
with fig.data():
    for (label, prefix, rest, total, note), y in zip(ROWS, YS):
        fig.fill(Box(X0, y - 16, prefix * PX, 32), "rule", fit=False)
        fig.fill(Box(X0 + prefix * PX, y - 16, rest * PX, 32), "neutral-soft", fit=False)
        fig.outline(Box(X0 + prefix * PX, y - 16, rest * PX, 32), "rule", width=1)
        fig.text(X0 + total * PX + 8, y + 5, num(total), "value", color="ink")
for (label, prefix, rest, total, note), y in zip(ROWS, YS):
    fig.text(40, y - 4, label, "label")
    fig.text(40, y + 20, note, "note")
for t in (0, 10000, 20000):
    fig.edge((X0 + t * PX, 360), (X0 + t * PX, 364), color="ink-muted", width=1)
    fig.text(X0 + t * PX, 384, num(t), "tick", anchor="middle")
fig.edge((X0, 140), (X0, 360), color="ink-muted", width=1)
fig.legend(40, 424, [dict(color="rule", label="shared prefix, once per call"),
                     dict(color="rule", label="logs, results and framing", mark="outline")])

# ---- right: seconds --------------------------------------------------------------------------------------
fig.text(496, 128, "Wall-clock, in simulated seconds", "head")
T0, PT = 600, 272 / 120
lanes = [("one agent", [(0, 10, "act"), (10, 20, "act"), (20, 30, "act"), (30, 120, "act")], 120),
         ("lead plans", [(0, 5, "ink-muted")], None),
         ("worker 1", [(5, 15, "act")], None),
         ("worker 2", [(5, 15, "act")], None),
         ("worker 3", [(5, 15, "act")], None),
         ("worker 4", [(5, 95, "act")], None),
         ("lead merges", [(95, 100, "ink-muted")], 100)]
assert lanes[5][1][0][1] - lanes[5][1][0][0] == max(fo.WORKER_S)
with fig.data():
    for i, (label, bars, end) in enumerate(lanes):
        y = 168 + 32 * i + (16 if i else 0)
        for a, b, c in bars:
            fig.fill(Box(T0 + a * PT, y - 12, (b - a) * PT, 20), c + "-soft" if c == "act" else "neutral-soft",
                     fit=False)
            fig.outline(Box(T0 + a * PT, y - 12, (b - a) * PT, 20), c, width=1)
        fig.text(496, y + 4, label, "label")
        if end:
            fig.text(T0 + end * PT + 8, y + 4, f"{end} s", "value", color="ink")
for t in (0, 30, 60, 90, 120):
    fig.edge((T0 + t * PT, 400), (T0 + t * PT, 404), color="ink-muted", width=1)
    fig.text(T0 + t * PT, 424, str(t), "tick", anchor="middle")
fig.edge((T0, 144), (T0, 400), color="ink-muted", width=1)
fig.text(T0, 452, "seconds; one agent runs the four pieces in turn", "note")

fig.caption("Caching shrinks the repeated prefix; it never shrinks the wait for the slowest worker.")
fig.write()
