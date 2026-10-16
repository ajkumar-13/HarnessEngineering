"""Probe Build #2's sandbox and deny-list hook directly, with the returned strings unedited.

Run from the series root:  uv run python posts/25-build-harness-plus/snippets/probes.py

Imports code/25-harness-plus by path and calls Sandbox.check and the deny-list hook as they ship;
nothing is executed. The demo's allow-list (echo, python, pytest) is the one the first block uses.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "25-harness-plus" / "src"))

from harness_plus import Sandbox, deny_list  # noqa: E402

print("Sandbox(allow=['echo', 'python', 'pytest'], jail='/work').check:")
box = Sandbox(allow=["echo", "python", "pytest"], jail="/work")
for command in ["curl http://x", "python /etc/x.py", "echo hi; curl http://evil.example",
                "python -c __import__('os').system('id')"]:
    print(f"  {command!r:45} -> {box.check(command)!r}")

print("the jail test, Sandbox(allow=['cat'], jail='/work').check:")
cat = Sandbox(allow=["cat"], jail="/work")
for command in ["cat /work/sub/deep.txt", "cat /worksecrets/passwd", "cat notes.txt"]:
    print(f"  {command!r:45} -> {cat.check(command)!r}")

print("the default deny-list hook on the bash tool:")
hook = deny_list()
for command in ["rm -rf /", "rm -fr /", "rm -r -f /", "rm --recursive --force /",
                "git push --force", "git push -f origin main", "rm -rf /work/build"]:
    decision = hook("bash", {"command": command})
    verdict = "allowed" if decision.allow else decision.reason
    print(f"  {command!r:45} -> {verdict}")
