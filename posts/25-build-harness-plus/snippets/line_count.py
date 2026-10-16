"""Count the lines of code/25-harness-plus as `wc -l` counts them (newline characters per file).

Run from the series root:  uv run python posts/25-build-harness-plus/snippets/line_count.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "code" / "25-harness-plus" / "src" / "harness_plus"
TESTS = ROOT / "code" / "25-harness-plus" / "tests"


def wc(path):
    return path.read_bytes().count(b"\n")


modules = {p.name: wc(p) for p in sorted(PKG.glob("*.py"))}
tests = {p.name: wc(p) for p in sorted(TESTS.glob("*.py"))}
for name, n in modules.items():
    print(f"{name:<14} {n:>4}")
layers = sum(modules[m] for m in ("hooks.py", "sandbox.py", "approval.py", "subagent.py"))
engine = sum(modules[m] for m in ("harness.py", "tools.py", "models.py"))
print(f"modules: {len(modules)}, {sum(modules.values())} lines; tests: {sum(tests.values())} lines in {len(tests)} file")
print(f"total: {sum(modules.values()) + sum(tests.values())} lines")
print(f"the four layers (hooks, sandbox, approval, subagent): {layers}; tracer (observe): {modules['observe.py']}")
print(f"the engine they wrap (harness, tools, models): {engine}")
