"""Post 08, section 4: checkpoint after a verified step, roll back a bad one, and catch a checkpoint that failed.

Run from the series root:  uv run python posts/08-state-filesystem-git/snippets/git_checkpoint.py

Real git commands in a temporary repository made under tempfile and deleted at the end. Author, committer and
dates are fixed in the environment, so the commit hashes are the same on every run. Standard library and git.
"""
import os
import re
import subprocess
import tempfile
from pathlib import Path

PATHS = ["src/", "tests/"]          # the only paths a checkpoint may stage

def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

def checkpoint(cwd, label: str) -> str:
    """Commit the current state as a point the agent can return to."""
    r = _git("add", "-A", "--", *PATHS, cwd=cwd)  # fails if a path is missing
    if not r.returncode:
        r = _git("commit", "-m", f"checkpoint: {label}", "--allow-empty", cwd=cwd)
    if r.returncode:
        raise RuntimeError(f"checkpoint failed: {r.stderr.strip()}")
    return _git("rev-parse", "HEAD", cwd=cwd).stdout.strip()

def rollback(cwd, ref: str) -> None:
    """Discard tracked changes since `ref`, then drop the debris the step left."""
    for args in (("reset", "--hard", ref), ("clean", "-fd", "--", *PATHS)):
        r = _git(*args, cwd=cwd)
        if r.returncode:
            raise RuntimeError(f"rollback failed: {r.stderr.strip()}")


FIXED = {"GIT_AUTHOR_NAME": "agent", "GIT_AUTHOR_EMAIL": "agent@example.com",
         "GIT_COMMITTER_NAME": "agent", "GIT_COMMITTER_EMAIL": "agent@example.com",
         "GIT_AUTHOR_DATE": "2026-07-20T09:00:00+00:00", "GIT_COMMITTER_DATE": "2026-07-20T09:00:00+00:00"}


def write(cwd, rel, text):
    path = Path(cwd, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def new_repo(cwd):
    """A repository whose scratch/ directory is ignored, with one source file and one test."""
    os.environ.update(FIXED)
    for args in (("init", "-q", "-b", "main"), ("config", "core.autocrlf", "false"),
                 ("config", "commit.gpgsign", "false")):
        _git(*args, cwd=cwd)
    write(cwd, ".gitignore", "scratch/\n")
    write(cwd, "src/parse.py", "def parse(line):\n    return line.split(',')\n")
    write(cwd, "tests/test_parse.py", "from parse import parse\n\nassert parse('a,b') == ['a', 'b']\n")
    _git("add", ".gitignore", cwd=cwd)


def demo(cwd):
    new_repo(cwd)
    ref = checkpoint(cwd, "tests green")
    print(f"checkpoint {ref[:7]}  tests green")

    # the risky step: one tracked edit, one new file in src/, one offloaded log, one note outside the paths
    write(cwd, "src/parse.py", "def parse(line):\n    return line.split(';')\n")
    write(cwd, "src/debris.py", "# half-written helper\n")
    write(cwd, "scratch/build.log", "1 failed, 0 passed\n")
    write(cwd, "notes.md", "a colleague's unsaved note\n")
    print("risky step: tests red, roll back")
    rollback(cwd, ref)

    head = _git("rev-parse", "HEAD", cwd=cwd).stdout.strip()
    source = Path(cwd, "src/parse.py").read_text(encoding="utf-8").splitlines()[1].strip()
    print(f"HEAD {head[:7]}  src/parse.py: {source}")
    for rel, why in (("src/debris.py", "untracked, under src/"), ("scratch/build.log", "ignored"),
                     ("notes.md", "untracked, outside the paths")):
        print(f"{rel:18} {'kept' if Path(cwd, rel).exists() else 'removed':8} {why}")

    # a checkpoint that fails: an index lock left behind by a crashed process
    Path(cwd, ".git", "index.lock").touch()
    write(cwd, "src/parse.py", "def parse(line):\n    return [f.strip() for f in line.split(',')]\n")
    try:
        print(f"checkpoint returned {checkpoint(cwd, 'strip fields')[:7]}")   # reached only without the check
    except RuntimeError as e:
        print(re.sub(r"'[^']*index\.lock'", "'.git/index.lock'", str(e).splitlines()[0]))
    head = _git("rev-parse", "HEAD", cwd=cwd).stdout.strip()
    print(f"rev-parse HEAD still answers {head[:7]}: unchecked, the loop would trust the old checkpoint")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        demo(tmp)
