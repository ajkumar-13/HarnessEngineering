"""Post 21, section 7: replay a recorded run against a changed harness, and see what each continuation does at
the first divergence.

Run from the series root:  uv run python posts/21-observability-traces/snippets/replay.py

The recording is four tool calls with their results, as the tool spans of a trace keep them. The changed
harness makes the same two reads in the other order, then a lint call the recording never saw, then the
tests and the edit. Four continuations replay it: a list consumed in order (the naive replay), stop at the
first call whose signature differs, look results up by signature and stop on a miss, and look up by signature
with a fall-through to a live tool on a miss. The live tool is a stand-in that returns a canned result; in a
real harness it runs inside the sandbox. Standard library only.
"""
import json

RECORDING = [  # (tool, args, result), in the order the original run made the calls
    ("read_file", {"path": "src/parser.py"}, "def parse(line): ..."),
    ("read_file", {"path": "tests/test_parser.py"}, "def test_parse(): ..."),
    ("run_tests", {}, "1 failed, 41 passed"),
    ("edit", {"path": "src/parser.py", "line": 2}, "edited"),
]
CHANGED = [  # what the changed harness asks for, in its order
    ("read_file", {"path": "tests/test_parser.py"}),
    ("read_file", {"path": "src/parser.py"}),
    ("lint", {"path": "src/parser.py"}),
    ("run_tests", {}),
    ("edit", {"path": "src/parser.py", "line": 2}),
]


def replay_tool(recording, name, args, live=None):
    """Look a recorded tool result up by call signature, not by position."""
    key = json.dumps([name, args], sort_keys=True)
    if key in recording:
        return recording[key], "replayed"
    if live is None:
        return None, "diverged"          # stop here; grade the progress so far
    return live(name, args), "live"      # the sandboxed fall-through of post 14


def by_position(calls):
    out = []
    for k, (name, args) in enumerate(calls):
        _, _, result = RECORDING[k]
        right = (RECORDING[k][0], RECORDING[k][1]) == (name, args)
        out.append("replayed" if right else "wrong result")
        if k + 1 == len(RECORDING):
            out.extend(["no recording"] * (len(calls) - k - 1))
            break
    return out


def stop_at_divergence(calls):
    out = []
    for k, (name, args) in enumerate(calls):
        if k >= len(RECORDING) or (RECORDING[k][0], RECORDING[k][1]) != (name, args):
            return out + ["diverged"]
        out.append("replayed")
    return out


def by_signature(calls, live=None):
    keyed = {json.dumps([n, a], sort_keys=True): r for n, a, r in RECORDING}
    out = []
    for name, args in calls:
        _, how = replay_tool(keyed, name, args, live)
        out.append(how)
        if how == "diverged":
            break
    return out


def main():
    live = lambda name, args: f"(live stand-in) {name}"  # noqa: E731
    rows = [("in order, a list", by_position(CHANGED)),
            ("stop at the first divergence", stop_at_divergence(CHANGED)),
            ("by signature, stop on a miss", by_signature(CHANGED)),
            ("by signature, live on a miss", by_signature(CHANGED, live))]
    print("changed harness asks for: " + ", ".join(f"{n} {a.get('path', '')}".strip() for n, a in CHANGED))
    print(f"{'continuation':<30}{'right results':>15}  per call")
    for name, outcome in rows:
        answered = sum(o in ("replayed", "live") for o in outcome)
        print(f"{name:<30}{answered:>9} of {len(CHANGED)}  {', '.join(outcome)}")
    wrong = by_position(CHANGED).count("wrong result")
    print(f"the list hands {wrong} calls a result recorded for a different call, and nothing flags it")


if __name__ == "__main__":
    main()
