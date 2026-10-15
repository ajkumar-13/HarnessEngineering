"""Post 14, section 1: a sandbox wrapper around the command tool, and the pre-filter it really is.

Run from the series root:  uv run python posts/14-permissions-sandboxes/snippets/sandbox.py

`sandboxed_run` refuses shell control characters, parses the command into an argument list with `shlex`
(so no shell ever runs), checks the program against an allow-list, resolves every argument against the
working-directory jail just before execution, runs the resolved executable with the jail as its working
directory, a bare environment and a timeout, and logs one line per decision naming the layer that decided.
Standard library only; runs on Windows and Linux. Run directly, it checks two commands without running them;
escape_attempts.py beside it runs the post's escape attempts.
"""
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

SHELL_CONTROL = re.compile(r"[;&|<>`\n]|\$\(")   # chaining, piping, redirection, substitution
BARE_ENV = {"SYSTEMROOT": os.environ["SYSTEMROOT"]} if os.name == "nt" else {}   # no secrets to leak


def default_allow() -> dict:
    """Program name -> the executable that runs. `python` is on it only to show why it must not be."""
    return {"git": shutil.which("git"), "python": sys.executable}


def sandboxed_run(command: str, *, jail: Path, allow: dict, timeout: float = 5.0, log=print) -> str:
    """Run one command inside the jail, or refuse it. A pre-filter, not a boundary on its own."""
    def decide(layer: str, verdict: str, detail: str) -> str:
        log(f"[{layer:<10}] {verdict}: {detail}")
        return f"{verdict}: {detail}"

    found = SHELL_CONTROL.search(command)
    if found:
        return decide("shell", "blocked", f"control character {found.group(0)!r} is refused")
    argv = shlex.split(command)
    if not argv or argv[0] not in allow:          # fail safe on anything not allow-listed
        return decide("allow-list", "blocked", f"{argv[0] if argv else '(empty)'} is not on the allow-list")
    root = jail.resolve()
    for token in argv[1:]:                        # resolved now, so '..', absolute paths and links count
        if not (root / token).resolve().is_relative_to(root):
            return decide("jail", "blocked", f"{token} resolves outside {root.name}/")
    try:
        proc = subprocess.run([allow[argv[0]], *argv[1:]], cwd=root, env=BARE_ENV,   # an argv list: no shell
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return decide("timeout", "blocked", f"killed after {timeout:g} s")
    decide("ran", "allowed", f"{argv[0]} exited {proc.returncode}")
    return (proc.stdout or proc.stderr).strip()


if __name__ == "__main__":
    here = Path.cwd()
    for command in ("git status; curl http://evil.example", "curl http://evil.example"):
        sandboxed_run(command, jail=here, allow=default_allow())
