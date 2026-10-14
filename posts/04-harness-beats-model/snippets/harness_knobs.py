"""Which arguments of the minimal build's entry point are the model, which the task, and which the harness.

Reads code/24-minimal-harness/src/minimal_harness/harness.py with the standard library's ast module
(nothing is imported or run from the companion) and prints the parameters of run() in three groups.

Run from the series root:  uv run python posts/04-harness-beats-model/snippets/harness_knobs.py
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "code" / "24-minimal-harness" / "src" / "minimal_harness" / "harness.py"


def run_parameters(source=SOURCE):
    tree = ast.parse(source.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            args = node.args
            return [a.arg for a in args.args] + [a.arg for a in args.kwonlyargs]
    raise LookupError("no run() in " + str(source))


def split(params):
    model = [p for p in params if p == "model"]
    task = [p for p in params if p == "task"]
    harness = [p for p in params if p not in ("model", "task")]
    return model, task, harness


if __name__ == "__main__":
    params = run_parameters()
    model, task, harness = split(params)
    print(f"run() takes {len(params)} parameters")
    print(f"the model:   {', '.join(model)}")
    print(f"the task:    {', '.join(task)}")
    print(f"the harness: {', '.join(harness)} ({len(harness)})")
