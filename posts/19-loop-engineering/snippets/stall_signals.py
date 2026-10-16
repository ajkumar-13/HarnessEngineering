"""Post 19, what you compare decides what you detect: three stall signals over four scripted traces.

Run from the series root:  uv run python posts/19-loop-engineering/snippets/stall_signals.py

Each turn of a trace records the tool call the agent made, the state of the working tree after it (a hash of
the files), and the verifier's score (failing tests). Each detector fires when the last three values of its
signal are identical: the tool-call signature (the companion's own `_signature` from code/03-agent-loop,
imported unchanged), the effect on disk, and the verifier's score. The traces are scripted, not
measured. Standard library only.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "03-agent-loop" / "src"))
from agent_loop import ToolUse  # noqa: E402
from agent_loop.loop import _signature  # noqa: E402

WINDOW = 3


def tree(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]


def turn(name, args, files, failing):
    return {"sig": _signature([ToolUse("tu", name, args)]), "effect": tree(files), "score": failing}


def stalled_at(trace, key):
    """The turn on which the last WINDOW values of `key` are first all equal, or None."""
    for t in range(WINDOW, len(trace) + 1):
        if len({turn[key] for turn in trace[t - WINDOW:t]}) == 1:
            return t
    return None


SRC = {"parser.py": "v1"}
TRACES = {
    "doom loop: the same call": [turn("run_tests", {"path": "tests/"}, SRC, 3) for _ in range(6)],
    "wandering: new calls, no edits": [turn("read_file", {"path": p}, SRC, 3)
                                       for p in ("a.py", "b.py", "c.py", "d.py", "e.py", "f.py")],
    "busy edits, no closer": [turn("edit_file", {"path": "parser.py", "rev": k}, {"parser.py": f"v{k}"}, 3)
                              for k in range(2, 8)],
    "healthy: tests 3, 2, 1, 0": [turn("edit_file", {"path": "parser.py", "rev": k}, {"parser.py": f"v{k}"}, f)
                                  for k, f in zip(range(2, 6), (3, 2, 1, 0))],
}
SIGNALS = [("sig", "signature"), ("effect", "effect on disk"), ("score", "verifier score")]

if __name__ == "__main__":
    print(f"{'trace':32}" + "".join(f"{label:>16}" for _, label in SIGNALS))
    for name, trace in TRACES.items():
        cells = []
        for key, _ in SIGNALS:
            t = stalled_at(trace, key)
            cells.append(f"turn {t}" if t else "never")
        print(f"{name:32}" + "".join(f"{c:>16}" for c in cells))
