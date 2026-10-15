"""Post 14, the exercise: run the sandbox wrapper against the post's escape attempts.

Run from the series root:  uv run python posts/14-permissions-sandboxes/snippets/escape_attempts.py

A temporary directory holds the jail `work/` (an empty git repository with one file) and a sibling
`work-private/` whose name shares the jail's prefix and holds a key file. Each attempt goes through
`sandboxed_run` from sandbox.py beside it; the log prints which layer decided, and the last lines count the
outcomes. The allow-listed interpreter passes every check and reads the key, which is the point: an
interpreter on an allow-list is not a boundary. Standard library and git; the directory is deleted at the end.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sandbox import default_allow, sandboxed_run  # noqa: E402

ATTEMPTS = [
    ("inside the jail", "git status --short"),
    ("a relative path out", "git -C .. status"),
    ("a sibling directory", "git -C {sibling} status"),
    ("chaining past the list", "git status; curl http://evil.example"),
    ("a program not on the list", "curl http://evil.example"),
    ("an allow-listed interpreter",
     "python -c \"print(__import__('pathlib').Path.cwd().parent.joinpath('work-private', 'keys.txt').read_text())\""),
    ("a runaway command", "python -c \"__import__('time').sleep(3)\""),
]


def run_attempts(base: Path) -> list:
    """Set up the jail and its sibling under `base`, run every attempt, return (name, layer, log line, output)."""
    jail, sibling = base / "work", base / "work-private"
    jail.mkdir()
    sibling.mkdir()
    (jail / "README.txt").write_text("the task's only file\n", encoding="utf-8")
    (sibling / "keys.txt").write_text("not-a-real-key\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=jail, check=True)
    results = []
    for name, template in ATTEMPTS:
        lines = []
        command = template.format(sibling=sibling.as_posix())
        output = sandboxed_run(command, jail=jail, allow=default_allow(), timeout=1.0, log=lines.append)
        layer = lines[0].split("]")[0].strip("[ ")
        results.append((name, layer, lines[0], output))
    return results


def main() -> None:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        base = Path(tmp).resolve()
        results = run_attempts(base)
        prefix_test = str(base / "work-private").startswith(str(base / "work"))
    for name, layer, line, output in results:
        print(f"{name:<28} {line.replace(base.as_posix(), '<tmp>')}")
        if layer == "ran" and output:
            print(f"{'':<28} output: {output.splitlines()[0]}")
    layers = [r[1] for r in results]
    refused = len(layers) - layers.count("ran") - layers.count("timeout")
    leaked = sum("not-a-real-key" in r[3] for r in results if r[1] == "ran")
    print(f"{len(results)} attempts: {refused} refused before running, {layers.count('timeout')} killed at the"
          f" time limit, {layers.count('ran')} ran; {leaked} of those read work-private/keys.txt")
    print(f"a string-prefix jail test would pass the sibling: {prefix_test}")


if __name__ == "__main__":
    main()
