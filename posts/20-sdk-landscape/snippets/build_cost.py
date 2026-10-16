"""Post 20: the price of rolling a harness of one's own, read off this series' two builds.

Run from the series root:  uv run python posts/20-sdk-landscape/snippets/build_cost.py

Counts the lines (as `wc -l` counts them: newline characters, comments and blank lines included) of the Python
files under code/24-minimal-harness and code/25-harness-plus, split into implementation (`src/`) and tests
(`tests/`), and counts the test functions. Build #2 carries its own loop and tool registry but no verifier, so the
union of the two feature sets is Build #2 plus Build #1's `verify.py`. Reads files only.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILDS = [("Build #1", "code/24-minimal-harness"), ("Build #2", "code/25-harness-plus")]


def lines(paths):
    return sum(p.read_bytes().count(b"\n") for p in paths)


def count(directory):
    base = ROOT / directory
    src, tests = sorted((base / "src").rglob("*.py")), sorted((base / "tests").rglob("*.py"))
    n_tests = sum(len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M)) for p in tests)
    return lines(src), lines(tests), n_tests


def main():
    totals = {}
    for name, directory in BUILDS:
        impl, test, n = count(directory)
        totals[name] = impl, test
        print(f"{name} ({directory}): {impl} implementation lines, {test} test lines, {n} tests")
    verifier = lines([ROOT / "code/24-minimal-harness/src/minimal_harness/verify.py"])
    union = totals["Build #2"][0] + verifier
    print(f"union: Build #2's {totals['Build #2'][0]} implementation lines plus Build #1's {verifier}-line verifier "
          f"= {union}")


if __name__ == "__main__":
    main()
