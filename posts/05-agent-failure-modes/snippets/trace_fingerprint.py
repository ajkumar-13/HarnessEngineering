"""Post 05, section 6: find the failure modes in an archive of finished runs, from the trace alone.

Run from the series root:  uv run python posts/05-agent-failure-modes/snippets/trace_fingerprint.py

The archive is made here: seven scripted runs of the companion loop, run() from
code/03-agent-loop/src/agent_loop/loop.py, imported unchanged, with stub tools that execute nothing. Each run
keeps what a run log keeps: its transcript, its stop reason, the downstream check's verdict, and the
reviewer's findings. The fingerprint is the companion's own _signature(). Thresholds are illustrative.
Standard library only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "03-agent-loop" / "src"))
from agent_loop import ScriptedModel, StopReason, Tool, ToolUse, run, text_response, tool_response  # noqa: E402
from agent_loop.loop import _signature  # noqa: E402

BUILD = iter(["queued", "running", "passed"])
TOOLS = [Tool("read_file", "read a file", lambda a: "def total(xs): ..."),
         Tool("run_tests", "run the tests", lambda a: "1 failed, 11 passed"),
         Tool("edit_file", "apply a patch", lambda a: f"patched {a['lines']} lines"),
         Tool("build_status", "poll the CI build", lambda a: next(BUILD)),
         Tool("bash", "run a shell command (a stub: nothing runs)", lambda a: "ok")]
DENY = re.compile(r"rm -rf|git push --force|DROP TABLE")

R, T, F = ("read_file", {"path": "app.py"}), ("run_tests", {}), ("build_status", {"id": 7})


def E(lines):
    return ("edit_file", {"path": "app.py", "lines": lines})


def archive_run(name, calls, answer, window, check_ok, findings):
    script = [tool_response(t, a, id=f"tu_{i}") for i, (t, a) in enumerate(calls, 1)]
    script += [text_response(answer)] if answer else []
    r = run(ScriptedModel(script), TOOLS, "Fix the failing test in app.py.", max_iters=8,
            no_progress_window=window)
    return {"name": name, "stop_reason": r.stop_reason, "checked_ok": check_ok,
            "findings": findings, "transcript": r.transcript}


runs = [
    archive_run("run-01", [R, T, E(3), T], "Fixed: the empty list is guarded.", 3, True, ["uses unittest"]),
    archive_run("run-02", [R], "Done: the tests pass.", 3, False, []),
    archive_run("run-03", [R] + [T] * 8, None, 9, False, ["uses unittest"]),       # an older config: no window
    archive_run("run-04", [R, T, T, T], None, 3, False, []),
    archive_run("run-05", [("bash", {"cmd": "make ci"}), F, F, F], None, 3, False, []),
    archive_run("run-06", [R, ("bash", {"cmd": "rm -rf build/"}), T], "Cleaned and fixed.", 3, True, []),
    archive_run("run-07", [R, E(412)], "Rewrote the module; done.", 3, False, ["uses unittest"]),
]


def turns(transcript):
    """One entry per assistant turn that called tools: its calls and the results that came back."""
    out = []
    for i, msg in enumerate(transcript):
        if msg["role"] != "assistant":
            continue
        uses = [ToolUse(b["id"], b["name"], b["input"]) for b in msg["content"] if b["type"] == "tool_use"]
        nxt = transcript[i + 1]["content"] if i + 1 < len(transcript) else []
        results = [b["content"] for b in nxt if isinstance(b, dict) and b.get("type") == "tool_result"]
        if uses:
            out.append({"tool_uses": uses, "results": results})
    return out


# The same fingerprint, run over an archive rather than a live loop.
def doom_loop_turns(transcript, window=3):
    sigs = [_signature(turn["tool_uses"]) for turn in transcript]
    return [i for i in range(window - 1, len(sigs))
            if len(set(sigs[i - window + 1:i + 1])) == 1]


def results_changed(trace, i, window=3):
    seen = [t["results"] for t in trace[i - window + 1:i + 1] if t["results"]]
    return len({str(r) for r in seen}) > 1


def one_shot(trace):
    sizes = [sum(u.input.get("lines", 0) for u in t["tool_uses"]) for t in trace]
    return sum(sizes) > 200 and max(sizes) >= 0.9 * sum(sizes)


hits = {name: set() for name in ("victory declaration", "context anxiety", "one-shotting", "doom loop",
                                 "silent drift", "destructive action")}
polls = set()
for r in runs:
    trace = turns(r["transcript"])
    flagged = doom_loop_turns(trace)
    if any(not results_changed(trace, i) for i in flagged):
        hits["doom loop"].add(r["name"])
    elif flagged:
        polls.add(r["name"])
    if one_shot(trace):
        hits["one-shotting"].add(r["name"])
    if any(DENY.search(str(u.input)) for t in trace for u in t["tool_uses"]):
        hits["destructive action"].add(r["name"])
for finding in {f for r in runs for f in r["findings"]}:
    recurring = [r["name"] for r in runs if finding in r["findings"]]
    if len(recurring) >= 3:
        hits["silent drift"].update(recurring)

# Victory declaration is a join, not a pattern: runs the harness called
# COMPLETED whose downstream check disagreed.
victory = [r for r in runs
           if r["stop_reason"] is StopReason.COMPLETED and not r["checked_ok"]]
hits["victory declaration"] = {r["name"] for r in victory}

if __name__ == "__main__":
    print(f"{'run':7} {'stop reason':12} check")
    for r in runs:
        print(f"{r['name']:7} {r['stop_reason'].value:12} {'passed' if r['checked_ok'] else 'failed'}")
    completed = [r["name"] for r in runs if r["stop_reason"] is StopReason.COMPLETED]
    print(f"\ncompleted, by stop reason alone: {', '.join(completed)}")
    for mode, names in hits.items():
        found = ", ".join(sorted(names)) or "needs a quality score per turn; this archive has none"
        print(f"{mode + ':':20} {len(names)}  {found}")
    print(f"identical calls, changing results (a poll, not a doom loop): {', '.join(sorted(polls))}")
