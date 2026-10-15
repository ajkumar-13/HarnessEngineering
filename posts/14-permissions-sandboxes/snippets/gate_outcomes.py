"""Post 14, section 5: four gates in a row, and a trace that can say which one fired.

Run from the series root:  uv run python posts/14-permissions-sandboxes/snippets/gate_outcomes.py

Each call passes the deny-list hook of post 13's companion (`code/13-hooks/`, imported by path), the
permission table of permissions.py, an approver standing in for the human of post 15 (it says no), and the
sandbox of sandbox.py, in that order. The outcome tag is
`blocked` (hook), `denied` (permission or approver), `refused` (sandbox) or `ok`. A naive tagger that only
knows the hook and the approver is printed beside it: it files the sandbox refusal as `ok`. Standard library
and git; the jail is a temporary directory deleted at the end.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[2] / "code" / "13-hooks" / "src")]
from hook_system.hooks import deny_list  # noqa: E402
from permissions import decide  # noqa: E402
from sandbox import default_allow, sandboxed_run  # noqa: E402

HOOK = deny_list()                                              # the companion's five default rules
CALLS = [
    ("deployer", "bash", {"command": "rm -rf ~"}),
    ("deployer", "deploy", {"target": "production"}),
    ("deployer", "bash", {"command": "git status ../work-private"}),
    ("deployer", "bash", {"command": "git status --short"}),
]


def approver(tool: str, args: dict) -> bool:
    """The human of post 15, scripted: this one says no."""
    return False


def gated_call(role: str, tool: str, args: dict, jail: Path) -> tuple:
    """Run one call through the four gates; return (outcome, the gate that decided, what came back)."""
    decision = HOOK(tool, str(args.get("command", args)))      # 1. the hook, before anything runs
    if not decision.allow:
        return "blocked", "hook", decision.reason
    verdict = decide(role, tool, args)                          # 2. the permission table
    if verdict == "deny" or (verdict == "ask" and not approver(tool, args)):   # 3. the approver
        return "denied", "approver" if verdict == "ask" else "permission", f"{verdict}: refused"
    if tool == "bash":                                          # 4. the sandbox, inside the tool
        observation = sandboxed_run(args["command"], jail=jail, allow=default_allow(), log=lambda line: None)
        outcome = "refused" if observation.startswith("blocked:") else "ok"
        return outcome, "sandbox" if outcome == "refused" else "none", observation
    return "ok", "none", f"{tool} ran"


def naive_tag(outcome: str) -> str:
    """A tagger that knows the hook and the approver, and calls everything else a success."""
    return outcome if outcome in ("blocked", "denied") else "ok"


def run() -> list:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        jail = Path(tmp, "work")
        jail.mkdir()
        (jail / "README.txt").write_text("the task's only file\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=jail, check=True)
        return [(tool, args, *gated_call(role, tool, args, jail)) for role, tool, args in CALLS]


if __name__ == "__main__":
    print(f"{'call':<36} {'decided by':<11} {'outcome':<8} naive tag")
    for tool, args, outcome, gate, _ in run():
        shown = f"{tool} {args.get('command') or args.get('target')}"
        print(f"{shown:<36} {gate:<11} {outcome:<8} {naive_tag(outcome)}")
