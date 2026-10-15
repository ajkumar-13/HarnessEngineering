"""Post 13, section 7: near-miss tests for a deny-list, run against the companion's shipped patterns and a fix.

Run from the series root:  uv run python posts/13-hooks-enforcement/snippets/near_miss.py

Each case is a command one step away from a rule, with the verdict a correct guard should give. The companion's
deny_list() is imported unchanged from code/13-hooks/src; the fixed list replaces its rm and force-push patterns and
keeps the other three. Nothing is executed: a hook only returns a verdict. Standard library only.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "13-hooks" / "src"))
from hook_system.hooks import DEFAULT_DENY, deny_list  # noqa: E402

# (command, should it run?)
CASES = [
    ("git push --force origin main", False),
    ("git push --force-with-lease origin main", True),
    ("git push -f origin main", False),
    ("git push origin main --force", False),
    ("rm -rf /", False),
    ("rm -fr /", False),
    ("rm --recursive --force /", False),
    ("rm -rf ./build", True),
]

FIXED = [
    (r"\brm\s+(-[a-z]*(rf|fr)[a-z]*|--recursive\s+--force|--force\s+--recursive)\s+(/|~|\*)",
     "recursive delete of a broad path"),
    (r"\bgit\s+push\b.*(--force(?![\w-])|\s-f\b)", "force-push"),
] + DEFAULT_DENY[2:]


def verdict(hook, cmd: str, should_run: bool) -> str:
    allowed = hook("bash", cmd).allow
    if allowed == should_run:
        return "runs" if allowed else "blocked"
    return "MISSED" if allowed else "FALSE POSITIVE"


shipped, fixed = deny_list(), deny_list(FIXED)
print(f"{'command':40} {'should':8} {'shipped':15} fixed")
wrong = {"shipped": 0, "fixed": 0}
for cmd, should_run in CASES:
    a, b = verdict(shipped, cmd, should_run), verdict(fixed, cmd, should_run)
    wrong["shipped"] += a.isupper()
    wrong["fixed"] += b.isupper()
    print(f"{cmd:40} {'run' if should_run else 'block':8} {a:15} {b}")
print(f"wrong: shipped {wrong['shipped']} of {len(CASES)}, fixed {wrong['fixed']} of {len(CASES)}")
assert wrong == {"shipped": 5, "fixed": 0}
