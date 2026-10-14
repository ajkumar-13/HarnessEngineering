"""Post 06, section 7: three kinds of wrongness, and where the companion catches each.

Run from the series root:  uv run python posts/06-tools-bash-code/snippets/three_gates.py

Every call goes through the companion's ToolRegistry.dispatch() and its bash tool, imported unchanged from
code/06-tools-and-bash/src. The runner is injected, as in the companion's tests: it records each command it is
handed and never starts a shell. For the one command that reaches it, it answers as `cat` answers for a file
that does not exist (exit status 1). The last column says whether the runner was reached. Standard library only.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "06-tools-and-bash" / "src"))
from tools import ToolRegistry, make_bash_tool  # noqa: E402

ran = []


def scripted_runner(command, timeout):
    """Record the command; answer as a shell would, without running anything."""
    ran.append(command)
    if command.startswith("cat /tmp/nope"):
        return "cat: /tmp/nope: No such file or directory", 1
    return "", 0


registry = ToolRegistry([make_bash_tool(scripted_runner)])
CALLS = [
    ("schema-invalid", {"cmd": "ls"}),
    ("valid, semantically wrong", {"command": "cat /tmp/nope"}),
    ("valid and dangerous", {"command": "rm -rf /"}),
]
for kind, call in CALLS:
    before = len(ran)
    seen = registry.dispatch("bash", call)
    print(f"{kind}: {call}")
    print(f"  loop sees: {seen}")
    print(f"  runner reached: {'yes' if len(ran) > before else 'no'}")
print(f"commands handed to the runner: {ran}")
