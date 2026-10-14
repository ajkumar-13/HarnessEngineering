"""No-progress detection, exit (4): the companion's fingerprint, its false positive, and the folded fix.

signature() is the companion's _signature (asserted equal below). no_progress() is its window check. Four
scripted traces of (tool call, observation) per turn are fed to three detectors: the calls only, as the
companion fingerprints them; the calls with each turn's observation folded in; and the folded fingerprint with
a wider window of 6 for a tool that is legitimately polled. Every window is 3 unless that tool is the one polled.

Run from the series root:  uv run python posts/03-the-agent-loop/snippets/no_progress.py
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "03-agent-loop" / "src"))
from agent_loop import ToolUse  # noqa: E402
from agent_loop.loop import _signature  # noqa: E402


def signature(tool_uses):
    """A stable fingerprint of a turn's tool calls, the companion's _signature."""
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)


def no_progress(recent, window=3):
    """Exit (4): the last `window` fingerprints are all the same."""
    last = recent[-window:]
    return len(last) == window and len(set(last)) == 1


def folded(tool_uses, observation):
    """The same fingerprint with the turn's observation folded in."""
    return json.dumps([signature(tool_uses), observation])


TEST = [ToolUse("t", "run_tests", {"path": "tests/"})]
POLL = [ToolUse("t", "build_status", {"job": "ci-42"})]
TRACES = {
    "doom loop": [(TEST, "1 failed")] * 5,
    "build poll": [(POLL, "running")] * 2 + [(POLL, "passed"), (TEST, "all passed")],
    "long build": [(POLL, "running")] * 5 + [(POLL, "passed")],
    "healthy edits": [([ToolUse("t", "edit_file", {"line": n})], "ok") for n in range(1, 6)],
}


POLLED = {"build_status": 6}          # a per-tool window for a tool that is meant to be polled


def first_fire(trace, fingerprint, windows=None):
    recent = []
    for turn, (calls, obs) in enumerate(trace, start=1):
        recent.append(fingerprint(calls, obs))
        if no_progress(recent, (windows or {}).get(calls[0].name, 3)):
            return turn
    return None


DETECTORS = [("calls only", lambda calls, obs: signature(calls), None),
             ("+ observation", folded, None),
             ("+ polled window 6", folded, POLLED)]

if __name__ == "__main__":
    a = [ToolUse("t", "read_file", {"path": "src/main.py", "lines": 40})]
    b = [ToolUse("t", "read_file", {"lines": 40, "path": "src/main.py"})]
    assert signature(a) == _signature(a)
    unsorted = [json.dumps([[tu.name, tu.input] for tu in x]) for x in (a, b)]
    print(f"same call, keys in two orders: sorted equal {signature(a) == signature(b)}, "
          f"unsorted equal {unsorted[0] == unsorted[1]}")
    print(f"{'trace':15}" + "".join(f"{name:>20}" for name, _, _ in DETECTORS))
    for name, trace in TRACES.items():
        fires = [first_fire(trace, f, w) for _, f, w in DETECTORS]
        print(f"{name:15}" + "".join(f"{f'turn {t}' if t else 'never':>20}" for t in fires))
