"""Post 15, Make it run: the companion's approval gate, answered asynchronously, with one call timing out.

Run from the series root:  uv run python posts/15-human-in-the-loop/snippets/async_approval.py

The gate is `ApprovalGate` from code/25-harness-plus/src, imported unchanged, and the loop is that companion's
`run()`. The companion's gate is synchronous: `review` calls the decider and waits for a bool. What this snippet
adds is a decider. It puts each request on a queue that a reviewer thread drains, waits on a reply channel of its
own for at most TIMEOUT seconds, and when nobody answers it applies the when-nobody-answers policy: deny what a
checkpoint cannot undo, proceed with a note otherwise. It also keeps the record the companion does not keep (who
decided, what they decided, and how the wait ended). The model is the companion's ScriptedModel, so nothing
leaves the machine. Standard library only.
"""
import queue
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "25-harness-plus" / "src"))
from harness_plus import (ApprovalGate, ScriptedModel, Tool, ToolRegistry,  # noqa: E402
                          Workspace, make_write_file_tool, run, text_response, tool_response)

REPLY_AFTER = 0.1            # seconds the reviewer takes when they do answer
TIMEOUT = 0.5                # seconds a request waits before the no-answer policy applies
IRREVERSIBLE = {"deploy"}    # what a checkpoint cannot undo


@dataclass
class Request:
    id: int
    tool: str
    args: dict
    reason: str
    reply: queue.Queue = field(default_factory=queue.Queue)   # one channel per request


def queued_decider(outbox, record, timeout=TIMEOUT):
    """A Decider for ApprovalGate: send the request out of band, then wait for its reply or the timeout."""
    ids = iter(range(1, 10_000))

    def decide(tool, args, reason):
        request = Request(next(ids), tool, dict(args), reason)
        outbox.put(request)
        started = time.monotonic()
        try:
            who, approved, answered_id = request.reply.get(timeout=timeout)
            if answered_id != request.id:          # a reply to some other request is not consent
                who, approved = "mismatched reply", False
        except queue.Empty:
            who = "timeout"
            approved = tool not in IRREVERSIBLE    # no answer: deny the irreversible, proceed otherwise
        record.append(dict(id=request.id, tool=tool, args=dict(args), reason=reason, who=who,
                           approved=approved, waited=time.monotonic() - started))
        return approved

    return decide


def reviewer(outbox, answers):
    """The human, in another thread: answers some requests after a while and never sees the others."""
    while (request := outbox.get()) is not None:
        answer = answers.get((request.tool, target(request.args)))
        if answer is None:
            continue                               # asleep; the notification went to an unwatched channel
        time.sleep(REPLY_AFTER)
        request.reply.put(("reviewer", answer, request.id))


def target(args):
    return args.get("target") or args.get("path") or args.get("name")


def make_tools(workspace, deployed):
    read_log = Tool("read_log", "Read a log file.",
                    {"type": "object", "properties": {"name": {"type": "string"}},
                     "required": ["name"], "additionalProperties": False},
                    lambda a: f"read {a['name']}")
    deploy = Tool("deploy", "Deploy the current build to an environment.",
                  {"type": "object", "properties": {"target": {"type": "string"}},
                   "required": ["target"], "additionalProperties": False},
                  lambda a: (deployed.append(a["target"]), f"deployed to {a['target']}")[1],
                  sensitive=True)
    return ToolRegistry([read_log, make_write_file_tool(workspace, sensitive=True), deploy])


SCRIPT = [
    ("read_log", {"name": "build.log"}),
    ("write_file", {"path": "notes.md", "content": "release notes"}),
    ("deploy", {"target": "production"}),
    ("write_file", {"path": "draft.md", "content": "next steps"}),
    ("deploy", {"target": "staging"}),
]
ANSWERS = {("write_file", "notes.md"): True, ("deploy", "production"): False}   # the other two: no answer


def simulate():
    """One scripted run through the companion's loop; returns the record, the result and what changed."""
    workspace, deployed, record = Workspace(), [], []
    outbox = queue.Queue()
    thread = threading.Thread(target=reviewer, args=(outbox, ANSWERS), daemon=True)
    thread.start()

    model = ScriptedModel([tool_response(name, args, id=f"t{i}", tokens=10)
                           for i, (name, args) in enumerate(SCRIPT, 1)]
                          + [text_response("Done; the production deploy needs a person.", tokens=6)])
    gate = ApprovalGate(decide=queued_decider(outbox, record))
    result = run(model, make_tools(workspace, deployed), "Ship the release.", approval=gate)
    outbox.put(None)
    thread.join()
    return record, result, workspace, deployed


def main():
    record, result, workspace, deployed = simulate()
    print(f"reviewer answers after {REPLY_AFTER} s when they answer; a request waits at most {TIMEOUT} s")
    print(f"{'call':<22}{'gated':<7}{'decided by':<12}outcome")
    gated = iter(record)
    for name, args in SCRIPT:
        call = f"{name} {target(args)}"
        if name == "read_log":
            print(f"{call:<22}{'no':<7}{'-':<12}ran")
            continue
        r = next(gated)
        assert (r["waited"] < TIMEOUT) if r["who"] == "reviewer" else (r["waited"] >= TIMEOUT)
        if r["who"] == "reviewer":
            outcome = "approved, ran" if r["approved"] else "denied"
        else:
            outcome = ("no answer, reversible: ran, noted" if r["approved"]
                       else "no answer, irreversible: denied")
        print(f"{call:<22}{'yes':<7}{r['who']:<12}{outcome}")
    print(f"stop_reason: {result.stop_reason.value}")
    print(f"Result.denied: {result.denied}")
    print(f"workspace: {sorted(workspace.files)}; deployed: {deployed}")


if __name__ == "__main__":
    main()
