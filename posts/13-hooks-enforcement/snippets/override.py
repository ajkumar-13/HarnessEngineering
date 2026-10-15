"""Post 13, section 7: an escape hatch for a pre-tool hook, a named, reasoned, single-use override with a log.

Run from the series root:  uv run python posts/13-hooks-enforcement/snippets/override.py

with_override wraps any pre-tool hook of the companion (code/13-hooks/src, imported unchanged): a blocked call
passes only when a token names the exact rule that blocked it and carries a reason, and the token is spent by
that one call. Not shipped in the companion. Standard library only.
"""
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "13-hooks" / "src"))
from hook_system.hooks import ALLOW, Decision, deny_list  # noqa: E402


@dataclass
class Token:
    reason: str     # why, in prose
    who: str        # the person granting it
    at: str         # when


def with_override(hook, tokens, log):
    """Wrap a pre-tool hook so a named, reasoned, single-use override can pass one call."""
    def gated(tool: str, args: str) -> Decision:
        decision = hook(tool, args)
        if decision.allow:
            return decision
        token = tokens.pop(decision.reason, None)          # one rule, one token
        if token is None or not token.reason.strip():      # no token, or no reason: stay blocked
            return decision
        log.append({"rule": decision.reason, "why": token.reason, "who": token.who,
                    "at": token.at, "command": f"{tool} {args}"})
        return ALLOW                                       # spent: the token is gone
    return gated


def show(label: str, decision: Decision) -> None:
    print(f"{label:34} -> {'allowed' if decision.allow else decision.reason}")


log: list = []
tokens = {
    "blocked: destructive SQL": Token("", "release-lead", "2026-10-15T10:02"),
    "blocked: force-push": Token("rewrite a leaked secret out of history", "release-lead", "2026-10-15T10:05"),
}
hook = with_override(deny_list(), tokens, log)
push = "git push --force origin main"

show("DROP TABLE, token has no reason", hook("sql", "DROP TABLE users"))
show("rm -rf /, no token for that rule", hook("bash", "rm -rf /"))
show("force-push, token for this rule", hook("bash", push))
show("force-push again, token spent", hook("bash", push))
print(f"override log: {log}")
print(f"tokens left: {sorted(tokens)}")
assert len(log) == 1 and list(tokens) == []
