"""Post 24: how big Build #1 is, counted rather than estimated.

Run from the series root:  uv run python posts/24-build-minimal-harness/snippets/line_count.py

Two measures, both stated on each line. "wc -l" counts newline characters, so comments, docstrings and blank
lines are included (the measure post 20's build_cost.py uses for the same files). "code lines" leaves out blank
lines, lines that are only a comment, and docstrings. The companion under code/24-minimal-harness is read and
imported unchanged; nothing is written.
"""
import inspect
import io
import re
import sys
import tokenize
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
COMPANION = ROOT / "code" / "24-minimal-harness"
sys.path.insert(0, str(COMPANION / "src"))
from minimal_harness import harness, tools  # noqa: E402

PACKAGE = COMPANION / "src" / "minimal_harness"
ENGINE = ["models.py", "tools.py", "verify.py", "harness.py"]
OTHER = ["__init__.py", "__main__.py"]


def wc_l(text):
    return text.count("\n")


def code_lines(text):
    """Lines carrying a token other than a comment, a docstring or a newline."""
    keep = set()
    prev = tokenize.NEWLINE
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        kind = tok.type
        if kind in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
                    tokenize.ENDMARKER):
            if kind == tokenize.NEWLINE:
                prev = kind
            continue
        if kind == tokenize.STRING and prev in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            prev = tokenize.STRING   # a statement that is only a string: a docstring
            continue
        prev = kind
        keep.update(range(tok.start[0], tok.end[0] + 1))
    return len(keep)


def main():
    sizes = {}
    for name in ENGINE + OTHER:
        text = (PACKAGE / name).read_text(encoding="utf-8")
        sizes[name] = (wc_l(text), code_lines(text))
        print(f"{name:12} {sizes[name][0]:4} lines (wc -l), {sizes[name][1]:4} code lines")
    engine = sum(sizes[n][0] for n in ENGINE)
    total = engine + sum(sizes[n][0] for n in OTHER)
    print(f"engine (the four modules): {engine} lines (wc -l), {sum(sizes[n][1] for n in ENGINE)} code lines")
    print(f"package (six files): {total} lines (wc -l), {sum(s[1] for s in sizes.values())} code lines")

    test_text = (COMPANION / "tests" / "test_harness.py").read_text(encoding="utf-8")
    n_tests = len(re.findall(r"^def test_", test_text, re.M))
    print(f"tests/test_harness.py: {wc_l(test_text)} lines (wc -l), {n_tests} tests")

    run_src = inspect.getsource(harness.run)
    print(f"run(): {wc_l(run_src)} lines (wc -l), {code_lines(run_src)} code lines")
    lines = run_src.splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines) if "if resp.is_final():" in l)
    end = next(i for i, l in enumerate(lines) if l.strip() == "continue")
    gate = inspect.cleandoc("".join(lines[start:end + 1])) + "\n"
    print(f"the gate block (from 'if resp.is_final():' to 'continue'): {code_lines(gate)} code lines")
    dispatch = inspect.getsource(tools.ToolRegistry.dispatch)
    print(f"ToolRegistry.dispatch: {wc_l(dispatch)} lines (wc -l), {code_lines(inspect.cleandoc(dispatch))} code lines")
    print(f"deny-list patterns in tools.DENY: {len(tools.DENY)}")
    return dict(sizes=sizes, engine=engine, total=total, tests=n_tests, test_lines=wc_l(test_text),
                run_lines=wc_l(run_src), run_code=code_lines(run_src), gate_code=code_lines(gate),
                deny=len(tools.DENY))


if __name__ == "__main__":
    main()
