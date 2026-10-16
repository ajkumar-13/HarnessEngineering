"""Post 20: one tiny task in two shapes, with one shared tool function.

Run from the series root:  uv run python posts/20-sdk-landscape/snippets/two_shapes.py

Shape A is a loop that owns the control flow and takes tools and a goal: the `run()` of
code/24-minimal-harness, imported unchanged, standing in for a batteries-included SDK. Shape B is a graph wired
by hand: a small standard-library stand-in for a graph framework, with named nodes, explicit edges, a
checkpointer that is a plain dictionary, and an interrupt before the node that acts. Neither is a vendor's code;
the post's fences show the vendors' documented shapes. Both shapes run the same task with the same scripted
model and one shared tool function, `read_file`, reached through a different adapter in each. Shape B is stopped
at its interrupt and resumed by a second, freshly compiled graph that shares only the checkpointer, which is the
resumability a checkpointer buys. Tokens are counted with tiktoken's o200k_base encoding over the JSON each
shape sends to the model (Claude's tokenizer is not public), so the counts are illustrative. Apart from tiktoken
fetching its encoding file once and caching it, nothing touches the network; the one file read lives in a
temporary directory.
"""
import atexit
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

import tiktoken

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "24-minimal-harness" / "src"))
from minimal_harness import ScriptedModel, Tool, ToolRegistry, run, text_response, tool_response  # noqa: E402

ENC = tiktoken.get_encoding("o200k_base")
WORKDIR = Path(tempfile.mkdtemp(prefix="hrn20-"))
atexit.register(shutil.rmtree, WORKDIR, ignore_errors=True)
TASK = "Which version does config.txt pin? Answer with the version only."
SYSTEM = "You are a careful engineer. Read before you answer."


# The portable half: a plain function and the schema that describes it.
def read_file(args: dict) -> str:
    return (WORKDIR / args["path"]).read_text(encoding="utf-8")


READ_FILE = {
    "name": "read_file",
    "description": "Read a UTF-8 text file and return its contents.",
    "input_schema": {"type": "object",
                     "properties": {"path": {"type": "string"}},
                     "required": ["path"], "additionalProperties": False},
}

# Adapter A: a harness that takes a tool list and runs the loop itself.
registry = ToolRegistry([Tool(READ_FILE["name"], READ_FILE["description"],
                              READ_FILE["input_schema"], read_file)])


# Adapter B: a graph framework, where the same function becomes one node.
def act(state: dict) -> dict:
    call = state["pending"]
    return {**state, "pending": None,
            "messages": state["messages"] + [tool_result(call, read_file(call.input))]}


def tool_result(call, observation: str) -> dict:
    """The observation message, in the same shape code/24's loop appends."""
    return {"role": "user", "content": [{"type": "tool_result", "tool_use_id": call.id, "content": observation}]}


class Counting:
    """Wraps a model and counts, with tiktoken, the tokens of every request and response."""

    def __init__(self, model):
        self.model, self.calls, self.tokens_in, self.tokens_out = model, 0, 0, 0

    def respond(self, system, messages, tools):
        self.calls += 1
        self.tokens_in += len(ENC.encode(json.dumps({"system": system, "messages": messages, "tools": list(tools)})))
        response = self.model.respond(system, messages, tools)
        self.tokens_out += len(ENC.encode(json.dumps(response.content_blocks)))
        return response


# ---- shape B: a graph of nodes and explicit edges, a dictionary checkpointer, an interrupt -------------------
START, END = "__start__", "__end__"


class Graph:
    def __init__(self):
        self.nodes, self.edges = {}, {}

    def add_node(self, name, fn):
        self.nodes[name] = fn

    def add_edge(self, source, target):
        self.edges[source] = lambda state: target

    def add_conditional_edges(self, source, route):
        self.edges[source] = route

    def compile(self, checkpointer, interrupt_before=()):
        return App(self, checkpointer, set(interrupt_before))


class App:
    """Runs the graph one node at a time and saves a checkpoint after every node, keyed by thread id."""

    def __init__(self, graph, checkpointer, interrupt_before):
        self.graph, self.saver, self.interrupt_before = graph, checkpointer, interrupt_before

    def _save(self, thread_id, next_node, state):
        self.saver.setdefault(thread_id, []).append({"next": next_node, "state": copy.deepcopy(state)})

    def invoke(self, state, thread_id, resume=False):
        if resume:                                  # pick up where the last checkpoint left off
            last = self.saver[thread_id][-1]
            node, state, skip_interrupt = last["next"], copy.deepcopy(last["state"]), True
        else:
            node, skip_interrupt = self.graph.edges[START](state), False
            self._save(thread_id, node, state)
        while node != END:
            if node in self.interrupt_before and not skip_interrupt:
                return {"interrupted_before": node, **state}
            skip_interrupt = False
            state = self.graph.nodes[node](state)
            node = self.graph.edges[node](state)
            self._save(thread_id, node, state)
        return state


def build_graph(model, tools, check=None):
    """reason -> act -> reason ... -> END; with `check`, a final answer passes through a check node first."""
    def reason(state):
        response = model.respond(SYSTEM, state["messages"], tools)
        messages = state["messages"] + [{"role": "assistant", "content": response.content_blocks}]
        if response.is_final():
            return {**state, "messages": messages, "answer": response.text}
        return {**state, "messages": messages, "pending": response.tool_uses[0]}

    graph = Graph()
    graph.add_node("reason", reason)
    graph.add_node("act", act)
    graph.add_edge(START, "reason")
    graph.add_edge("act", "reason")
    if check is None:
        graph.add_conditional_edges("reason", lambda s: "act" if s["pending"] else END)
    else:
        graph.add_node("check", check)
        graph.add_conditional_edges("reason", lambda s: "act" if s["pending"] else "check")
        graph.add_conditional_edges("check", lambda s: END if s["answer"] is not None else "reason")
    return graph


def new_state(task):
    return {"messages": [{"role": "user", "content": task}], "pending": None, "answer": None, "retries": 0}


def script():
    return ScriptedModel([tool_response("read_file", {"path": "config.txt"}, tokens=1), text_response("2.4.1")])


def show(messages):
    """One line per message after the task: the tool call, its result, the answer."""
    parts = []
    for m in messages[1:]:
        block = m["content"][0]
        if block["type"] == "tool_use":
            parts.append(f"tool_use {block['name']} {json.dumps(block['input'])}")
        elif block["type"] == "tool_result":
            parts.append(f"tool_result {json.dumps(block['content'])}")
        else:
            parts.append(f"answer {block['text']}")
    return " -> ".join(parts)


def main():
    (WORKDIR / "config.txt").write_text("name = parser\nversion = 2.4.1\n", encoding="utf-8")
    print(f"task: {TASK}")

    model_a = Counting(script())
    result = run(model_a, registry, TASK, system=SYSTEM)
    print(f"shape A, a loop that owns the control flow: {result.stop_reason.value}; {model_a.calls} model calls, "
          f"{model_a.tokens_in} input and {model_a.tokens_out} output tokens")

    saver = {}                                      # the checkpointer: a dictionary keyed by thread id
    model_b = Counting(script())
    first = build_graph(model_b, [READ_FILE]).compile(saver, interrupt_before=["act"])
    paused = first.invoke(new_state(TASK), "run-1")
    print(f"shape B, a graph wired by hand: stopped before {paused['interrupted_before']} "
          f"with {len(saver['run-1'])} checkpoints saved")
    second = build_graph(model_b, [READ_FILE]).compile(saver, interrupt_before=["act"])
    state = second.invoke(None, "run-1", resume=True)
    print(f"  a fresh graph sharing only the checkpointer resumed it to END; {model_b.calls} model calls, "
          f"{model_b.tokens_in} input and {model_b.tokens_out} output tokens, {len(saver['run-1'])} checkpoints")

    same = result.transcript == state["messages"] and (model_a.tokens_in, model_a.tokens_out) == (
        model_b.tokens_in, model_b.tokens_out)
    print(f"transcript of both: {show(state['messages'])}")
    print(f"same transcript, same tokens: {same}")
    assert same and result.answer == state["answer"] == "2.4.1"


if __name__ == "__main__":
    main()
