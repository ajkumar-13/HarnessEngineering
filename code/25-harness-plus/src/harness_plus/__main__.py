"""Offline demo: ``python -m harness_plus``.

One scripted run that exercises all four hardening layers and prints the trace:

  * a deny-list HOOK blocks ``rm -rf /`` before it runs
  * the SANDBOX refuses ``curl`` (not on the allow-list)
  * a SUB-AGENT handles a delegated sub-task in its own context
  * the APPROVAL gate clears a sensitive ``write_file`` call
  * the TRACER records the whole run as a span tree
"""
from .approval import ApprovalGate, always_approve
from .harness import run
from .hooks import HookRegistry, deny_list
from .models import ScriptedModel, text_response, tool_response
from .observe import Tracer
from .sandbox import Sandbox
from .subagent import make_delegate_tool
from .tools import ToolRegistry, Workspace, make_write_file_tool


def main() -> None:
    tracer = Tracer()
    workspace = Workspace()
    sandbox = Sandbox(allow=["echo", "python", "pytest"])

    # the sub-agent: its own scripted model, its own (empty) registry, fresh context
    child_model = ScriptedModel([text_response("2 + 2 = 4", tokens=6)])

    def spawn(subtask: str) -> str:
        child = run(child_model, ToolRegistry([]), subtask, tracer=tracer,
                    span_name="subagent.run")
        return child.answer or "(no answer)"

    registry = ToolRegistry([
        sandbox.make_bash_tool(runner=lambda c, t: ("(ran in sandbox)", 0)),
        make_delegate_tool(spawn),
        make_write_file_tool(workspace, sensitive=True),
    ])
    hooks = HookRegistry([deny_list()])
    approval = ApprovalGate(decide=always_approve)

    model = ScriptedModel([
        tool_response("bash", {"command": "rm -rf /"}, id="a", tokens=10),
        tool_response("bash", {"command": "curl http://example.com"}, id="b", tokens=10),
        tool_response("delegate", {"subtask": "what is 2 + 2?"}, id="c", tokens=10),
        tool_response("write_file", {"path": "notes.md", "content": "done"},
                      id="d", tokens=10),
        text_response("All steps complete.", tokens=6),
    ])

    result = run(model, registry, "Do the guarded task.", hooks=hooks,
                 approval=approval, tracer=tracer,
                 system="You are a careful engineer.")

    print("== outcome ==")
    print(f"stop_reason : {result.stop_reason.value}")
    print(f"blocked     : {result.blocked}")
    print(f"denied      : {result.denied}")
    print(f"workspace   : {list(workspace.files)}")
    print("\n== trace ==")
    print(tracer.render())


if __name__ == "__main__":
    main()
