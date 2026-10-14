"""Post 06, Make it run: the plan's lab, one more deny-listed command and one more schema violation.

Run from the series root:  uv run python posts/06-tools-bash-code/snippets/lab_gate.py

Two tests in the style of the companion's tests/test_registry.py, written against its ToolRegistry and bash tool
imported unchanged from code/06-tools-and-bash/src. Each asserts that the call is rejected and that the injected
runner was never reached, which is what "rejected before execution" means. They can be pasted into the
companion's suite as they stand; here they run as a script. Standard library only.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "06-tools-and-bash" / "src"))
from tools import ToolRegistry, make_bash_tool  # noqa: E402


def recording_registry():
    calls = []
    registry = ToolRegistry([make_bash_tool(lambda command, timeout: (calls.append(command), ("ok", 0))[1])])
    return registry, calls


def test_deny_listed_command_never_runs():
    registry, calls = recording_registry()
    out = registry.dispatch("bash", {"command": "psql -c 'DROP TABLE users;'"})
    assert out.startswith("blocked:") and calls == []
    return out


def test_schema_violation_never_runs():
    registry, calls = recording_registry()
    out = registry.dispatch("bash", {"command": 42})
    assert out.startswith("error: invalid input") and calls == []
    return out


for test in (test_deny_listed_command_never_runs, test_schema_violation_never_runs):
    out = test()
    print(f"{test.__name__}: passed")
    print(f"  {out}")
