"""Demo: a hook registry blocks a destructive command and catches a broken edit.

Run:  python -m hook_system
Offline: no API key, no network.
"""
from __future__ import annotations

from .hooks import HookRegistry, deny_list, gated_call, post_edit_tests


def main() -> None:
    # Pre-tool: a deny-list gates every command. Blocked calls never execute.
    registry = HookRegistry().add_pre_tool(deny_list())
    for tool, args in [("bash", "ls -la"), ("bash", "rm -rf /"), ("bash", "git push --force")]:
        out = gated_call(registry, tool, args, execute=lambda t, a: f"ran: {t} {a}")
        print(f"{args!r:20} -> {out}")

    # Post-edit: run tests after a .py edit. Here "tests" fail if the edit contains BUG.
    def make_runner(content: str):
        def run_tests():
            ok = "BUG" not in content
            return ok, ("" if ok else "assertion failed: BUG marker present")
        return run_tests

    for content in ["def add(a, b): return a + b", "def add(a, b): return a - b  # BUG"]:
        reg = HookRegistry().add_post_edit(post_edit_tests(make_runner(content)))
        problems = reg.after_edit("math_utils.py", content)
        print(f"edit -> {'ok' if not problems else problems[0]}")


if __name__ == "__main__":
    main()
