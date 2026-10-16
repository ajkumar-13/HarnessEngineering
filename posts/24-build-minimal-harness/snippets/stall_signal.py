"""Post 24: what Build #1's no-progress check compares, and the three runs that show its limits.

Run from the series root:  uv run python posts/24-build-minimal-harness/snippets/stall_signal.py

Imports run() from code/24-minimal-harness unchanged. The check fingerprints each turn's tool calls (name and
arguments) and stops when the last no_progress_window=3 fingerprints are identical; it never looks at what the
tools returned. Three scripted runs, with a runner that executes nothing:
  1. a poll: the same command every turn while its output changes (a false positive);
  2. busywork: a different command every turn, none of which helps (a false negative);
  3. a correction: the same check re-run after each rejection by the gate, which resets the detector.
"""
import itertools
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "24-minimal-harness" / "src"))
from minimal_harness import (ScriptedModel, ToolRegistry, VerifyResult, make_bash_tool, run,  # noqa: E402
                             text_response, tool_response)


def bash(command, i):
    return tool_response("bash", {"command": command}, id=f"b{i}")


def main():
    states = itertools.cycle(["build queued", "build running", "build passed"])
    polling = ToolRegistry([make_bash_tool(runner=lambda c, t: (next(states), 0))])
    poll = run(ScriptedModel([bash("ci status", i) for i in range(20)]), polling, "wait for the build",
               max_iters=20)
    outputs = [m["content"][0]["content"] for m in poll.transcript if m["role"] == "user"
               and isinstance(m["content"], list)]
    print(f"1. poll 'ci status', output changing {outputs}: exit {poll.stop_reason.value} "
          f"at iteration {poll.iterations}")

    quiet = ToolRegistry([make_bash_tool(runner=lambda c, t: ("", 0))])
    busy = run(ScriptedModel([bash(f"echo {i}", i) for i in range(20)]), quiet, "do something", max_iters=20)
    print(f"2. 'echo 0', 'echo 1', ... for 20 turns, nothing achieved: exit {busy.stop_reason.value} "
          f"at iteration {busy.iterations}")

    verdicts = iter([VerifyResult(False, "1 test failed"), VerifyResult(False, "1 test failed"),
                     VerifyResult(True)])
    script = []
    for i in range(3):
        script += [bash("pytest -q", i), text_response("done")]
    fixed = run(ScriptedModel(script), quiet, "fix the test", verify=lambda c: next(verdicts), max_iters=20)
    print(f"3. 'pytest -q' then done, three times over, the first two rejected: exit {fixed.stop_reason.value} "
          f"at iteration {fixed.iterations}, verified {fixed.verified}")
    return dict(poll=poll, busy=busy, fixed=fixed)


if __name__ == "__main__":
    main()
