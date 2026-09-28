"""A single general-purpose tool — bash — with a deny-list and an injectable runner.

The deny-list is checked BEFORE the command reaches the runner, so a dangerous
command is refused without being executed. The runner is injectable so the tests
run fully offline with no real shell. This is the *minimum* every bash tool needs;
real sandboxing (allow-lists, isolation, network egress) is Post 14.
"""
from __future__ import annotations

import re
from typing import Callable

from .registry import Tool

# Refused outright. A deny-list is never exhaustive — Post 14 argues for
# allow-lists + sandboxes — but it stops the common feet-guns from Post 05.
DENY = [
    r"\brm\s+-[rf]", r"\brm\s+--no-preserve-root", r"\bmkfs\b", r"\bdd\s+if=",
    r":\(\)\s*\{\s*:\s*\|\s*:", r"\bshutdown\b", r"\breboot\b",
    r"\bgit\s+push\b[^\n]*--force", r"\bsudo\b", r">\s*/dev/sd",
    r"\bDROP\s+TABLE\b", r"\bchmod\s+-R\s+0*777\s+/",
]

Runner = Callable[[str, float], "tuple[str, int]"]

BASH_SCHEMA = {
    "type": "object",
    "properties": {"command": {"type": "string"}},
    "required": ["command"],
    "additionalProperties": False,
}

BASH_DESCRIPTION = (
    "Run a shell command and return its combined stdout/stderr. Use for file "
    "operations, builds, tests, and one-off scripts. Do NOT use for destructive "
    "operations; dangerous commands are refused."
)


def subprocess_runner(command: str, timeout: float) -> "tuple[str, int]":
    import subprocess
    proc = subprocess.run(command, shell=True, capture_output=True,
                          text=True, timeout=timeout)
    output = (proc.stdout or "") + (proc.stderr or "")
    return output.strip(), proc.returncode


def make_bash_tool(runner: Runner = subprocess_runner, *, timeout: float = 10.0,
                   deny: list[str] = DENY) -> Tool:
    patterns = [re.compile(p, re.IGNORECASE) for p in deny]

    def run(args: dict) -> str:
        command = str(args.get("command", ""))
        for pattern in patterns:
            if pattern.search(command):
                return f"blocked: command matches a deny-list rule ({pattern.pattern})"
        try:
            output, code = runner(command, timeout)
        except Exception as e:
            return f"error: {type(e).__name__}: {e}"
        prefix = "" if code == 0 else f"(exit {code}) "
        return prefix + (output if output else "(no output)")

    return Tool("bash", BASH_DESCRIPTION, BASH_SCHEMA, run)
