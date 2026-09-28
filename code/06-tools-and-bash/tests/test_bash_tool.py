"""The bash tool's safety surface: dangerous commands are refused before running,
and every failure comes back as an observation instead of an exception."""
from tools.bash_tool import make_bash_tool


def recording_runner():
    """A fake runner that records calls, so tests can assert a command never ran."""
    calls: list[str] = []

    def runner(command, timeout):
        calls.append(command)
        return f"ran: {command}", 0

    runner.calls = calls  # type: ignore[attr-defined]
    return runner


def test_safe_command_reaches_the_runner():
    runner = recording_runner()
    tool = make_bash_tool(runner)
    out = tool.run({"command": "echo hi"})
    assert runner.calls == ["echo hi"]
    assert out == "ran: echo hi"


def test_dangerous_commands_blocked_and_never_run():
    runner = recording_runner()
    tool = make_bash_tool(runner)
    for cmd in ["rm -rf /", "sudo rm x", "git push origin main --force",
                "mkfs.ext4 /dev/sda"]:
        assert tool.run({"command": cmd}).startswith("blocked:")
    assert runner.calls == []  # the runner was never reached


def test_nonzero_exit_is_prefixed():
    tool = make_bash_tool(lambda command, timeout: ("boom", 2))
    assert tool.run({"command": "false"}) == "(exit 2) boom"


def test_runner_exception_becomes_an_observation():
    def runner(command, timeout):
        raise TimeoutError("timed out")

    tool = make_bash_tool(runner)
    out = tool.run({"command": "sleep 999"})
    assert out.startswith("error:") and "timed out" in out
