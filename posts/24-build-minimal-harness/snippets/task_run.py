"""Post 24: the companion's demo, one line per iteration, then the same script with the gate taken out.

Run from the series root:  uv run python posts/24-build-minimal-harness/snippets/task_run.py

Runs main() of code/24-minimal-harness/src/minimal_harness/__main__.py unchanged, with its own printing
captured, and keeps the Result that main() gets back from run(). The demo's scripted model, task, tools and
verifier are the companion's. A second run passes the same script through run() with verify=None, so only the
harness changes. Token counts are the ones the demo sets by hand on each scripted response, not a live model's.
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "24-minimal-harness" / "src"))
import minimal_harness.__main__ as demo  # noqa: E402

REAL_RUN = demo.run


def run_demo(**override):
    """Call the demo's main(); return the Result its run() produced and the file it left."""
    captured = {}

    def recording_run(*args, **kwargs):
        kwargs.update(override)
        captured["result"] = REAL_RUN(*args, **kwargs)
        captured["workspace"] = kwargs["workspace"]
        return captured["result"]

    demo.run = recording_run
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            demo.main()
    finally:
        demo.run = REAL_RUN
    return captured["result"], captured["workspace"]


def body_line(source):
    """The return line of the function the agent wrote."""
    return next(line.strip() for line in source.splitlines() if line.strip().startswith("return"))


def iterations(result):
    """One row per model call: what the model did, and what the harness did with it."""
    rows, messages = [], result.transcript[1:]
    for i, msg in enumerate(messages):
        if msg["role"] != "assistant":
            continue
        calls = [b for b in msg["content"] if b["type"] == "tool_use"]
        after = messages[i + 1]["content"] if i + 1 < len(messages) else None
        if calls:
            call = calls[0]
            did = f"{call['name']} {call['input']['path']}: {body_line(call['input']['content'])}"
            seen = after[0]["content"]
        else:
            did = "final answer"
            seen = after if isinstance(after, str) else "the gate passes and run() returns"
        rows.append((did, seen))
    return rows


def main():
    gated, ws = run_demo()
    print("the companion's demo, with the palindrome gate:")
    for n, (did, seen) in enumerate(iterations(gated), 1):
        print(f"  iteration {n}  model: {did}")
        print(f"               harness: {seen}")
    print(f"  stop_reason {gated.stop_reason.value}, verified {gated.verified}, "
          f"iterations {gated.iterations}, tokens_used {gated.tokens_used}")

    bare, ws_bare = run_demo(verify=None)
    print("\nthe same model and script, two harnesses:")
    for name, r, w in (("verify=None", bare, ws_bare), ("palindrome gate", gated, ws)):
        print(f"  {name:16} {r.stop_reason.value}, verified {r.verified}, {r.iterations} iterations, "
              f"{r.tokens_used} tokens, leaves: {body_line(w.files['solution.py'])}")
    return dict(gated=gated, bare=bare, rows=iterations(gated),
                files=(body_line(ws_bare.files["solution.py"]), body_line(ws.files["solution.py"])))


if __name__ == "__main__":
    main()
