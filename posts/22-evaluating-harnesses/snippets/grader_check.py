"""Post 22: validate the grader before trusting it, with an empty agent, an oracle, a re-grade and hand labels.

Run from the series root:  uv run python posts/22-evaluating-harnesses/snippets/grader_check.py

Six small tasks, each a fixture of files written to a fresh temporary directory, a grader that reads the files (the
world, not a transcript), and a reference solution. Three graders are flawed on purpose, one of each kind the post
names: one passes the empty run because its fixture already satisfies it, one rejects its own reference solution,
and one is flaky (its verdict depends on a simulated timing that changes between calls). validate() catches all
three without calling a model. The second half scores twelve hand-labelled candidate solutions against the graders
of the three sound tasks and prints the false-pass and false-fail rates; one candidate special-cases the test input,
the shape of a patch that a too-weak test lets through. Standard library only; every file lives under tempfile.
"""
import itertools
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_clock = itertools.count()


def read(ws, name):
    path = ws / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def defines_slugify(ws):
    scope = {}
    try:
        exec(read(ws, "util.py"), scope)
        return scope["slugify"]("Hello World") == "hello-world"
    except Exception:
        return False


def timed_suite(ws):
    """The summary is right, but the suite 'times out' on every third call: a flaky grader."""
    return "3 errors" in read(ws, "summary.txt") and next(_clock) % 3 != 2


@dataclass
class Task:
    id: str
    fixture: dict
    grader: Callable
    reference: dict

    def grade(self, edits):
        """Write the fixture and the run's edits to a fresh directory, then let the grader read it."""
        with tempfile.TemporaryDirectory(prefix=f"{self.id}-") as tmp:
            ws = Path(tmp)
            for name, text in {**self.fixture, **edits}.items():
                (ws / name).write_text(text, encoding="utf-8")
            return bool(self.grader(ws))


TASK_SET = [
    Task("set-port", {"app.ini": "port = 8000\n"},
         lambda ws: "port = 9000" in read(ws, "app.ini"), {"app.ini": "port = 9000\n"}),
    Task("add-slugify", {"util.py": "# helpers\n"}, defines_slugify,
         {"util.py": "def slugify(s):\n    return '-'.join(s.lower().split())\n"}),
    Task("rename-flag", {"cli.py": "VERBOSE = False\n"},
         lambda ws: "QUIET" in read(ws, "cli.py") and "VERBOSE" not in read(ws, "cli.py"),
         {"cli.py": "QUIET = True\n"}),
    Task("mention-harness", {"README.md": "A small harness for agents.\n"},           # already passes
         lambda ws: "harness" in read(ws, "README.md"), {"README.md": "A small harness for coding agents.\n"}),
    Task("bump-patch", {"VERSION": "1.3.0\n"},                                       # grader expects a minor bump
         lambda ws: read(ws, "VERSION").strip() == "1.4.0", {"VERSION": "1.3.1\n"}),
    Task("summarise-log", {"build.log": "error\nerror\nok\nerror\n"}, timed_suite,
         {"summary.txt": "3 errors\n"}),
]
EMPTY_RUN = {}                           # an agent that did nothing at all


# Run before the set is trusted, and again whenever a task is added.
def validate(task_set):
    bad = []
    for task in task_set:
        if task.grade(EMPTY_RUN):
            bad.append((task.id, "passes without the work being done"))
        if not task.grade(task.reference):
            bad.append((task.id, "the known-good solution fails its own grader"))
        if task.grade(task.reference) != task.grade(task.reference):
            bad.append((task.id, "disagrees with itself on an unchanged workspace"))
    return bad


# Hand-labelled candidates for the sound tasks: (task id, files the candidate wrote, a human's verdict).
LABELLED = [
    ("set-port", {"app.ini": "port = 9000\n"}, True),
    ("set-port", {"app.ini": "port = 9000\nport = 8000\n"}, False),   # two ports: the app reads the last one
    ("set-port", {"app.ini": "port=9000\n"}, True),                   # correct, but no spaces round '='
    ("set-port", {"app.ini": "port = 8000\n"}, False),
    ("add-slugify", {"util.py": "def slugify(s):\n    return '-'.join(s.lower().split())\n"}, True),
    ("add-slugify", {"util.py": "def slugify(s):\n    return 'hello-world'\n"}, False),   # special-cases the test
    ("add-slugify", {"util.py": "def slugify(s):\n    return s.lower()\n"}, False),
    ("add-slugify", {"util.py": "import re\ndef slugify(s):\n    return re.sub(r'\\s+', '-', s.strip().lower())\n"},
     True),
    ("rename-flag", {"cli.py": "QUIET = True\n"}, True),
    ("rename-flag", {"cli.py": "QUIET = True\nVERBOSE = False\n"}, False),
    ("rename-flag", {"cli.py": "# QUIET replaces the old flag\nQUIET = True\n"}, True),
    ("rename-flag", {"cli.py": "QUIETLY = 1\n"}, False),
]


def main():
    print(f"validating {len(TASK_SET)} tasks with an empty run, the reference solution and a re-grade")
    bad = validate(TASK_SET)
    for task_id, problem in bad:
        print(f"  BadTask {task_id}: {problem}")
    flagged = {task_id for task_id, _ in bad}
    print(f"sound: {', '.join(t.id for t in TASK_SET if t.id not in flagged)}")

    tasks = {t.id: t for t in TASK_SET}
    verdicts = [(tasks[tid].grade(files), label) for tid, files, label in LABELLED]
    false_pass = sum(g and not lab for g, lab in verdicts)
    false_fail = sum(lab and not g for g, lab in verdicts)
    wrong, right = sum(not lab for _, lab in verdicts), sum(lab for _, lab in verdicts)
    print(f"{len(LABELLED)} hand-labelled candidates on the sound tasks: {right} right, {wrong} wrong")
    print(f"false passes {false_pass} of {wrong} wrong candidates; false fails {false_fail} of {right} right ones")
    return {"bad": bad, "false_pass": false_pass, "false_fail": false_fail, "wrong": wrong, "right": right}


if __name__ == "__main__":
    main()
