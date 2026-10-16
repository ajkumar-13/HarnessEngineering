"""A sub-agent's limits are a parameter list: the demo's spawn against one that forwards them.

Run from the series root:  uv run python posts/25-build-harness-plus/snippets/spawn_limits.py

Imports code/25-harness-plus by path, unchanged. The parent has token_budget=100 and delegates once.
The child is a scripted model that would spend 100 tokens a turn for five turns.
  1. The demo's spawn passes only the tracer: the child gets the default limits and its tokens never
     reach the parent's counter.
  2. The forwarding spawn passes the gates, a cap, and the budget the parent has left, read from a
     ledger that both models charge (the companion's run() keeps its counter private, so the ledger
     lives in the caller).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "25-harness-plus" / "src"))

from harness_plus import (ApprovalGate, HookRegistry, ScriptedModel, ToolRegistry, Tracer,  # noqa: E402
                          deny_list, make_delegate_tool, run, text_response, tool_response)

BUDGET = 100


class Ledger:
    """Counts every token any model in the run spends, parent and child alike."""

    def __init__(self):
        self.spent = 0

    def charge(self, model):
        respond = model.respond

        def counted(system, messages, tools):
            resp = respond(system, messages, tools)
            self.spent += resp.tokens
            return resp

        model.respond = counted
        return model


def child_script():
    turns = [tool_response("lookup", {"page": n}, id=f"c{n}", tokens=100) for n in range(4)]
    return ScriptedModel(turns + [text_response("the answer", tokens=100)])


def parent_script():
    return ScriptedModel([tool_response("delegate", {"subtask": "look it up"}, id="p", tokens=10),
                          text_response("done", tokens=10)])


def demo_run():
    ledger, tracer = Ledger(), Tracer()
    child_model = ledger.charge(child_script())

    def spawn(subtask: str) -> str:
        child = run(child_model, ToolRegistry([]), subtask, tracer=tracer,
                    span_name="subagent.run")
        return child.answer or "(no answer)"

    parent = run(ledger.charge(parent_script()), ToolRegistry([make_delegate_tool(spawn)]),
                 "delegate once", token_budget=BUDGET, tracer=tracer)
    return parent, ledger, tracer


def forwarding_run():
    ledger, tracer = Ledger(), Tracer()
    hooks, approval = HookRegistry([deny_list()]), ApprovalGate()
    child_model = ledger.charge(child_script())
    child_registry = ToolRegistry([])

    def spawn(subtask: str) -> str:
        child = run(child_model, child_registry, subtask,
                    hooks=hooks, approval=approval,          # the gates are a parameter
                    max_iters=4, token_budget=BUDGET - ledger.spent,
                    tracer=tracer, span_name="subagent.run")
        return child.answer or "(no answer)"

    parent = run(ledger.charge(parent_script()), ToolRegistry([make_delegate_tool(spawn)]),
                 "delegate once", hooks=hooks, approval=approval, token_budget=BUDGET, tracer=tracer)
    return parent, ledger, tracer


for label, (parent, ledger, tracer) in [("demo spawn", demo_run()), ("forwarding spawn", forwarding_run())]:
    child = [s for _, s in tracer.root.walk() if s.name == "subagent.run"][0]
    child_tokens = sum(s.attributes["tokens"] for _, s in child.walk() if s.name == "model.call")
    print(f"{label}: parent stop={parent.stop_reason.value} tokens_used={parent.tokens_used}; "
          f"child stop={child.attributes['stop.reason']} iterations={tracer.count('iteration') - parent.iterations} "
          f"tokens={child_tokens}; ledger={ledger.spent} against a budget of {BUDGET}")
