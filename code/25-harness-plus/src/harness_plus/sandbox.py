"""A sandbox around the bash tool: allow-list + working-dir jail + timeout.

A deny-list stops the feet-guns you thought of; an allow-list stops the ones you
did not (Post 14). Build #2's bash tool refuses any program not explicitly
allowed, refuses paths that escape the jail, and caps every command's runtime.
The real executor is injected, so the tests exercise the boundary offline with
no shell.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .tools import Tool

Runner = Callable[[str, float], "tuple[str, int]"]

# Chaining, piping, redirection, substitution, and background operators. Any of
# these turns one approved command into two, one of which was never checked.
SHELL_CONTROL = re.compile(r"[;&|<>`\n]|\$\(")


def _within(token: str, jail: str) -> bool:
    """True if ``token`` resolves inside ``jail``.

    A raw ``startswith`` is not a path test: it puts ``/worksecrets`` inside a
    ``/work`` jail because the *string* matches. Compare resolved paths instead,
    so only real descendants pass.
    """
    from pathlib import PurePosixPath
    t = PurePosixPath(token)
    j = PurePosixPath(jail)
    return t == j or j in t.parents

def subprocess_runner(command: str, timeout: float) -> "tuple[str, int]":
    """Execute without a shell, so the allow-list means what it says.

    ``shell=True`` would let one allow-listed program carry a second, un-checked
    one after a ``;`` or a ``|``. Splitting the string ourselves and passing an
    argv list means the only program that runs is the one ``check`` approved.
    """
    import shlex
    import subprocess
    argv = shlex.split(command)
    proc = subprocess.run(argv, shell=False, capture_output=True,
                          text=True, timeout=timeout)
    return ((proc.stdout or "") + (proc.stderr or "")).strip(), proc.returncode


@dataclass
class Sandbox:
    """The execution boundary. ``allow`` lists permitted program names; any
    command whose first token is not on it is refused. ``jail`` is the only
    directory paths may touch, checked crudely by refusing ``..`` and absolute
    paths outside the jail. ``timeout`` caps runtime."""
    allow: list[str] = field(default_factory=lambda: ["echo", "ls", "cat", "git"])
    #: NOTE: allow-listing an interpreter allow-lists everything it can run.
    #: ``python -c "..."`` carries no shell metacharacters, so it passes every
    #: check here while executing arbitrary code. ``python`` and ``pytest`` are
    #: therefore deliberately NOT in the default allow-list; a caller that needs
    #: them (as ``__main__`` does, to run the test suite) must opt in explicitly
    #: and should pair that with an OS-level boundary, not this allow-list alone.
    jail: str = "/work"
    timeout: float = 5.0

    def check(self, command: str) -> "str | None":
        stripped = command.strip()
        if not stripped:
            return "blocked: empty command"
        # Checked before the allow-list, because these are what let an allowed
        # program smuggle a disallowed one: "echo hi; curl evil" passes any
        # first-token check ever written.
        found = SHELL_CONTROL.search(stripped)
        if found:
            return f"blocked: shell control character {found.group(0)!r} is refused"
        prog = stripped.split()[0]
        if prog not in self.allow:
            return f"blocked: '{prog}' is not on the allow-list {self.allow}"
        if ".." in command:
            return "blocked: path traversal ('..') is refused"
        for token in stripped.split():
            if token.startswith("/") and not _within(token, self.jail):
                return f"blocked: '{token}' is outside the jail {self.jail!r}"
        return None

    def make_bash_tool(self, runner: Runner = subprocess_runner, *,
                       sensitive: bool = False) -> Tool:
        def run(args: dict) -> str:
            command = str(args.get("command", ""))
            problem = self.check(command)
            if problem:
                return problem
            try:
                output, code = runner(command, self.timeout)
            except Exception as e:
                return f"error: {type(e).__name__}: {e}"
            prefix = "" if code == 0 else f"(exit {code}) "
            return prefix + (output if output else "(no output)")

        return Tool(
            "bash",
            "Run a shell command inside the sandbox (allow-listed programs, "
            "jailed paths, bounded runtime).",
            {"type": "object", "properties": {"command": {"type": "string"}},
             "required": ["command"], "additionalProperties": False},
            run, sensitive=sensitive,
        )
