"""Post 26, "Layout": the companion's modules, their line counts, its tests, and what it imports.

Run from the series root:  uv run python posts/26-capstone-coding-agent/snippets/line_count.py

Reads code/26-coding-agent/ without importing it. A line count is the number of newline characters in the file,
which is what `wc -l` prints. Tests are counted as the top-level `def test_` functions. Imports are read with
ast, and a module counts as standard library when its top-level name is in sys.stdlib_module_names; a relative
import (from .core import ...) stays inside the package.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMP = ROOT / "code" / "26-coding-agent"
PKG = COMP / "src" / "coding_agent"
TESTS = COMP / "tests" / "test_coding_agent.py"
ORDER = ["__init__.py", "__main__.py", "core.py", "driver.py", "memory.py", "observe.py", "cost.py"]
ROLE = {"__init__.py": "the public surface, re-exported",
        "__main__.py": "the offline demo: python -m coding_agent",
        "core.py": "Workspace, Task, Spec, VerifyResult, the verifier",
        "driver.py": "plan() and build(): the long-horizon loop",
        "memory.py": "Ratchet: learn(), as_context()",
        "observe.py": "Span, Tracer: nested spans, render()",
        "cost.py": "CostMeter: prices, cache discount, ceiling"}


def lines(path):
    return path.read_bytes().count(b"\n")


def imports(path):
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            found.add(node.module.split(".")[0])
    return found


def main():
    assert sorted(p.name for p in PKG.glob("*.py")) == sorted(ORDER)
    counts = {name: lines(PKG / name) for name in ORDER}
    n_tests = sum(1 for node in ast.parse(TESTS.read_text(encoding="utf-8")).body
                  if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
    print("code/26-coding-agent/")
    print("  src/coding_agent/")
    for name in ORDER:
        print(f"    {name:<20}{counts[name]:>4}   {ROLE[name]}")
    print("  tests/")
    print(f"    {TESTS.name:<20}{lines(TESTS):>4}   {n_tests} tests")
    print(f"source: {sum(counts.values())} lines across {len(ORDER)} modules; tests: {lines(TESTS)} lines")
    outside = set()
    for name in ORDER:
        outside |= {m for m in imports(PKG / name) if m not in sys.stdlib_module_names}
    print(f"imports from outside the standard library: {sorted(outside) or 'none'}")


if __name__ == "__main__":
    main()
