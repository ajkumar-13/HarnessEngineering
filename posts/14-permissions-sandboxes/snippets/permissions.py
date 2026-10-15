"""Post 14, section 2: permissions as data, a role table, argv-pattern rules and a default at the bottom.

Run from the series root:  uv run python posts/14-permissions-sandboxes/snippets/permissions.py

The role decides which tools a call may use; for the command tool, argv patterns decide which commands; an
unmatched call is refused. `ask` hands the call to an approval gate (post 15) instead of deciding it here.
Prints the verdict for six calls. Standard library only.
"""
import re

ROLES = {
    "reviewer": {"read_file": "allow", "bash": "allow", "write_file": "deny"},
    "deployer": {"read_file": "allow", "bash": "allow", "deploy": "ask"},
}
BASH_RULES = [                                # argv patterns, not bare program names
    (r"^git (status|diff|log)\b", "allow"),
    (r"^git push\b",              "ask"),
    (r"^rm\b",                    "deny"),
]

def decide(role: str, tool: str, args: dict) -> str:
    """Return 'allow', 'ask' or 'deny'. Default-deny: an unknown role, tool or command is 'deny'."""
    grant = ROLES.get(role, {}).get(tool, "deny")          # the role decides the tool
    if grant != "allow" or tool != "bash":
        return grant
    command = str(args.get("command", ""))
    for pattern, verdict in BASH_RULES:                   # the pattern decides the command
        if re.match(pattern, command):
            return verdict
    return "deny"


CALLS = [
    ("reviewer", "write_file", {"path": "src/app.py"}),
    ("reviewer", "bash", {"command": "git diff HEAD~1"}),
    ("deployer", "bash", {"command": "git push origin main"}),
    ("reviewer", "bash", {"command": "python -c \"print('hi')\""}),
    ("deployer", "deploy", {"target": "production"}),
    ("intern", "read_file", {"path": "README.md"}),
]

if __name__ == "__main__":
    for role, tool, args in CALLS:
        shown = args.get("command") or next(iter(args.values()))
        print(f"{role:<9} {tool:<11} {shown:<26} -> {decide(role, tool, args)}")
