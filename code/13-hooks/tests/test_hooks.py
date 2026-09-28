"""Offline tests for the hook system. Run: python -m pytest -q"""
from hook_system.hooks import (
    Decision,
    HookRegistry,
    deny_list,
    gated_call,
    post_edit_tests,
)


def test_deny_list_blocks_dangerous_commands():
    hook = deny_list()
    assert not hook("bash", "rm -rf /").allow
    assert not hook("bash", "git push --force origin main").allow
    assert not hook("sql", "DROP TABLE users").allow


def test_deny_list_allows_safe_commands():
    hook = deny_list()
    assert hook("bash", "ls -la").allow
    assert hook("bash", "git status").allow
    assert hook("bash", "pytest -q").allow


def test_check_tool_first_block_wins():
    reg = HookRegistry().add_pre_tool(lambda t, a: Decision(True)).add_pre_tool(deny_list())
    assert reg.check_tool("bash", "ls").allow
    blocked = reg.check_tool("bash", "rm -rf /")
    assert not blocked.allow
    assert "recursive delete" in blocked.reason


def test_gated_call_does_not_execute_when_blocked():
    reg = HookRegistry().add_pre_tool(deny_list())
    ran = []

    def execute(tool, args):
        ran.append((tool, args))
        return "executed"

    out = gated_call(reg, "bash", "rm -rf /", execute)
    assert "blocked" in out
    assert ran == []  # the dangerous command never ran


def test_gated_call_executes_when_allowed():
    reg = HookRegistry().add_pre_tool(deny_list())
    out = gated_call(reg, "bash", "echo hi", execute=lambda t, a: f"ran {a}")
    assert out == "ran echo hi"


def test_post_edit_reports_failing_tests():
    reg = HookRegistry().add_post_edit(post_edit_tests(lambda: (False, "1 failed")))
    problems = reg.after_edit("m.py", "code")
    assert problems and "tests failed" in problems[0]


def test_post_edit_clean_when_tests_pass():
    reg = HookRegistry().add_post_edit(post_edit_tests(lambda: (True, "")))
    assert reg.after_edit("m.py", "code") == []


def test_post_edit_ignores_non_python_files():
    reg = HookRegistry().add_post_edit(post_edit_tests(lambda: (False, "should not run")))
    assert reg.after_edit("README.md", "text") == []  # hook only fires on .py


def test_empty_registry_enforces_nothing():
    reg = HookRegistry()
    assert reg.check_tool("bash", "rm -rf /").allow  # no hooks, no enforcement
    assert reg.after_edit("m.py", "x") == []
