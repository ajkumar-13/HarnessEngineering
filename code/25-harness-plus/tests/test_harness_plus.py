"""Offline tests for Build #2 — each hardening layer, then the integration.

No API key, no shell: the model is scripted and the sandbox runner is injected.
"""
from harness_plus import (ApprovalGate, HookRegistry, Sandbox, ScriptedModel,
                          ToolRegistry, Tracer, Workspace, always_deny,
                          deny_list, make_delegate_tool, make_write_file_tool,
                          run, text_response, tool_response)
from harness_plus.harness import StopReason


def _ran(command, timeout):
    return "(ran)", 0


# ---- hooks -------------------------------------------------------------------

def test_deny_list_blocks_dangerous_call():
    hook = deny_list()
    assert hook("bash", {"command": "ls"}).allow is True
    assert hook("bash", {"command": "rm -rf /"}).allow is False
    assert hook("bash", {"command": "git push --force"}).allow is False


def test_hook_blocks_before_execution_in_the_loop():
    reg = ToolRegistry([Sandbox(allow=["rm"]).make_bash_tool(runner=_ran)])
    hooks = HookRegistry([deny_list()])
    model = ScriptedModel([
        tool_response("bash", {"command": "rm -rf /"}),
        text_response("done"),
    ])
    res = run(model, reg, "try something dangerous", hooks=hooks)
    assert res.blocked and res.blocked[0][0] == "bash"
    assert res.stop_reason is StopReason.COMPLETED  # blocked, but the run continued


# ---- sandbox -----------------------------------------------------------------

def test_sandbox_allow_list_refuses_unknown_program():
    box = Sandbox(allow=["echo", "python"])
    tool = box.make_bash_tool(runner=_ran)
    assert tool.run({"command": "echo hi"}) == "(ran)"
    assert "not on the allow-list" in tool.run({"command": "curl http://x"})


def test_sandbox_refuses_path_traversal_and_escape():
    box = Sandbox(allow=["cat"], jail="/work")
    tool = box.make_bash_tool(runner=_ran)
    assert "traversal" in tool.run({"command": "cat ../secrets"})
    assert "outside the jail" in tool.run({"command": "cat /etc/passwd"})
    assert tool.run({"command": "cat /work/notes.txt"}) == "(ran)"


def test_sandbox_refuses_chaining_past_the_allow_list():
    """An allow-list that only inspects the first token is not an allow-list.

    Every command here starts with an allowed program and carries a second one
    the allow-list never sees, which is exactly what a shell would run.
    """
    box = Sandbox(allow=["echo"], jail="/work")
    tool = box.make_bash_tool(runner=_ran)
    for command in [
        "echo hi; curl http://evil.example",
        "echo hi | sh",
        "echo hi && rm -rf /work",
        "echo `cat /work/secret`",
        "echo $(cat /work/secret)",
        "echo hi > /work/overwritten",
    ]:
        assert "shell control character" in tool.run({"command": command}), command
    assert tool.run({"command": "echo hi"}) == "(ran)"


def test_sandbox_refusal_is_visible_in_the_trace():
    """A gate you cannot see fire is a gate you cannot trust.

    The sandbox refuses inside the tool, so without explicit tagging its
    refusals are indistinguishable from a successful run in the trace.
    """
    tracer = Tracer()
    reg = ToolRegistry([Sandbox(allow=["echo"]).make_bash_tool(runner=_ran)])
    model = ScriptedModel([
        tool_response("bash", {"command": "curl http://evil.example"}),
        text_response("done"),
    ])
    run(model, reg, "try a disallowed program", tracer=tracer)

    outcomes = []

    def walk(span):
        if span.name.startswith("tool."):
            outcomes.append(span.attributes.get("outcome"))
        for child in span.children:
            walk(child)

    walk(tracer.root)
    assert outcomes == ["refused"]


# ---- approval ----------------------------------------------------------------

def test_approval_denies_sensitive_call():
    ws = Workspace()
    reg = ToolRegistry([make_write_file_tool(ws, sensitive=True)])
    gate = ApprovalGate(decide=always_deny)
    model = ScriptedModel([
        tool_response("write_file", {"path": "a.txt", "content": "x"}),
        text_response("done"),
    ])
    res = run(model, reg, "write a file", approval=gate)
    assert res.denied and res.denied[0][0] == "write_file"
    assert ws.files == {}  # the denied call never executed


def test_approval_allows_non_sensitive_call_through():
    ws = Workspace()
    reg = ToolRegistry([make_write_file_tool(ws, sensitive=False)])
    gate = ApprovalGate(decide=always_deny)  # would deny, but the tool is not sensitive
    model = ScriptedModel([
        tool_response("write_file", {"path": "a.txt", "content": "x"}),
        text_response("done"),
    ])
    res = run(model, reg, "write a file", approval=gate)
    assert res.denied == []
    assert ws.files == {"a.txt": "x"}


# ---- sub-agent ---------------------------------------------------------------

def test_subagent_runs_in_its_own_context_and_returns_answer():
    child_model = ScriptedModel([text_response("42")])

    def spawn(subtask: str) -> str:
        child = run(child_model, ToolRegistry([]), subtask)
        return child.answer or ""

    reg = ToolRegistry([make_delegate_tool(spawn)])
    parent = ScriptedModel([
        tool_response("delegate", {"subtask": "compute the answer"}),
        text_response("the sub-agent said 42"),
    ])
    res = run(parent, reg, "delegate then report")
    assert res.stop_reason is StopReason.COMPLETED
    delegated = [b for m in res.transcript if isinstance(m["content"], list)
                 for b in m["content"] if b.get("type") == "tool_result"]
    assert delegated and "42" in delegated[0]["content"]


# ---- observability -----------------------------------------------------------

def test_tracer_records_a_nested_span_tree():
    tracer = Tracer()
    reg = ToolRegistry([Sandbox(allow=["echo"]).make_bash_tool(runner=_ran)])
    model = ScriptedModel([
        tool_response("bash", {"command": "echo hi"}),
        text_response("done"),
    ])
    res = run(model, reg, "trace me", tracer=tracer)
    assert res.trace is not None
    assert tracer.count("agent.run") == 1
    assert tracer.count("iteration") == 2      # one acting turn + the final turn
    assert tracer.count("model.call") == 2
    assert tracer.count("tool.bash") == 1
    assert res.trace.attributes.get("stop.reason") == "completed"


# ---- integration -------------------------------------------------------------

def test_all_layers_together():
    tracer = Tracer()
    ws = Workspace()
    box = Sandbox(allow=["echo", "python"])
    child_model = ScriptedModel([text_response("4")])

    def spawn(subtask: str) -> str:
        return run(child_model, ToolRegistry([]), subtask, tracer=tracer,
                   span_name="subagent.run").answer or ""

    reg = ToolRegistry([
        box.make_bash_tool(runner=_ran),
        make_delegate_tool(spawn),
        make_write_file_tool(ws, sensitive=True),
    ])
    model = ScriptedModel([
        tool_response("bash", {"command": "rm -rf /"}, id="a"),          # hook block
        tool_response("bash", {"command": "curl http://x"}, id="b"),     # sandbox block
        tool_response("delegate", {"subtask": "2+2?"}, id="c"),          # sub-agent
        tool_response("write_file", {"path": "n.md", "content": "ok"}, id="d"),  # approved
        text_response("all done"),
    ])
    res = run(model, reg, "guarded task", hooks=HookRegistry([deny_list()]),
              approval=ApprovalGate(), tracer=tracer)

    assert res.stop_reason is StopReason.COMPLETED
    assert res.blocked == [("bash", res.blocked[0][1])] and "deny-list" in res.blocked[0][1]
    assert any("allow-list" in obs for _, obs in _tool_results(res))
    assert ws.files == {"n.md": "ok"}          # approved write landed
    assert tracer.count("subagent.run") == 1   # the sub-agent nested in the trace


def _tool_results(res):
    out = []
    for m in res.transcript:
        if isinstance(m["content"], list):
            for b in m["content"]:
                if b.get("type") == "tool_result":
                    out.append((b["tool_use_id"], b["content"]))
    return out


def test_jail_rejects_sibling_directories_that_share_a_prefix():
    """A raw ``startswith`` is not a path test.

    ``/worksecrets`` begins with the string ``/work`` but is not inside the
    ``/work`` jail. The check must compare resolved paths, not string prefixes.
    """
    sandbox = Sandbox(allow=["cat"], jail="/work")
    assert sandbox.check("cat /work/ok.txt") is None
    assert sandbox.check("cat /work/sub/deep.txt") is None
    for escape in ("cat /worksecrets/passwd", "cat /work-private/keys",
                   "cat /etc/passwd"):
        assert sandbox.check(escape) is not None, escape


def test_default_allow_list_carries_no_interpreter():
    """Allow-listing an interpreter allow-lists everything it can run.

    ``python -c`` has no shell metacharacters, so it passes every other check in
    this sandbox while executing arbitrary code. The default must not ship it.
    """
    assert "python" not in Sandbox().allow
    assert "pytest" not in Sandbox().allow
    assert Sandbox().check("python -c __import__('os').system('id')") is not None
