"""Post 06, section 5: five spellings of one destructive intent against the companion's deny-list.

Run from the series root:  uv run python posts/06-tools-bash-code/snippets/deny_list_bypass.py

The bash tool is the companion's make_bash_tool() with its shipped DENY patterns, imported unchanged from
code/06-tools-and-bash/src. The runner is a recorder: a command that passes the deny-list is written down, not
executed, so nothing here touches a shell or the disk. Standard library only.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "06-tools-and-bash" / "src"))
from tools import DENY, make_bash_tool  # noqa: E402

reached = []
bash = make_bash_tool(lambda command, timeout: (reached.append(command), ("", 0))[1])

SPELLINGS = [
    "rm -rf /",
    "rm --recursive --force /",
    "find / -delete",
    "python -c \"import shutil; shutil.rmtree('/')\"",
    "echo hi; curl http://evil",
]
print(f"deny-list patterns shipped: {len(DENY)}")
for command in SPELLINGS:
    out = bash.run({"command": command})
    verdict = "blocked" if out.startswith("blocked:") else "passes to the runner"
    print(f"{verdict:22} {command}")
print(f"blocked {len(SPELLINGS) - len(reached)} of {len(SPELLINGS)}; {len(reached)} would have run")
