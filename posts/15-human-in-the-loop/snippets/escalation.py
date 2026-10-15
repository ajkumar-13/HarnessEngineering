"""Post 15: escalation triggers, the companion's approval policy widened until it can see the run.

Run from the series root:  uv run python posts/15-human-in-the-loop/snippets/escalation.py

The companion's policy, `ApprovalGate.needs_approval(tool_name, sensitive, args)` in code/25-harness-plus, sees one
call and returns a bool. This version also sees the run, and returns the reason a human is needed (or None),
because what the request should ask differs by signal. The thresholds (0.6 confidence, 80% of the budget) are
illustrative. Standard library only.
"""
import json
from dataclasses import dataclass, field


@dataclass
class RunState:
    verifier_confidence: float = 1.0
    calls: list = field(default_factory=list)       # (tool, args) of every call so far, oldest first
    tokens_used: int = 0
    token_budget: int = 100_000
    flagged: set = field(default_factory=set)       # tools a permission rule flags without forbidding

    def repeat_count(self, tool_name, args):
        """How many of the most recent calls, running back from the last, were this exact call."""
        this = (tool_name, json.dumps(args, sort_keys=True))
        n = 0
        for name, a in reversed(self.calls):
            if (name, json.dumps(a, sort_keys=True)) != this:
                break
            n += 1
        return n

    def permission_flagged(self, tool_name, args):
        return tool_name in self.flagged


def needs_approval(tool_name, sensitive, args, run_state):
    """The reason this call needs a human, or None when the run may go on alone."""
    if sensitive:
        return "sensitive tool"
    if run_state.verifier_confidence < 0.6:              # post 11: a check passed weakly
        return "low verifier confidence"
    if run_state.repeat_count(tool_name, args) >= 1:     # post 05: twice running, before exit (4)
        return "repeated call"
    if run_state.tokens_used > 0.8 * run_state.token_budget:
        return "budget threshold"
    if run_state.permission_flagged(tool_name, args):    # post 14: flagged, not forbidden
        return "out-of-policy action"
    return None


CASES = [
    ("write_file, marked sensitive", "write_file", True, {"path": "a.md"}, RunState()),
    ("edit after a weak check", "edit", False, {"path": "a.py"}, RunState(verifier_confidence=0.4)),
    ("run_tests, same as last call", "run_tests", False, {"k": "parse"},
     RunState(calls=[("run_tests", {"k": "parse"})])),
    ("read_file at 85,000 tokens", "read_file", False, {"path": "b.py"}, RunState(tokens_used=85_000)),
    ("fetch, flagged by a rule", "fetch", False, {"url": "x"}, RunState(flagged={"fetch"})),
    ("read_file, nothing unusual", "read_file", False, {"path": "b.py"},
     RunState(calls=[("run_tests", {"k": "parse"})], tokens_used=12_000)),
]

if __name__ == "__main__":
    for label, tool, sensitive, args, state in CASES:
        print(f"{label:<32}{needs_approval(tool, sensitive, args, state) or 'no human needed'}")
