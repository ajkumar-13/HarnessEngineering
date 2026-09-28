"""dispatch() validates before it executes, and never raises into the loop."""
from tools.registry import Tool, ToolRegistry

SCHEMA = {
    "type": "object",
    "properties": {"x": {"type": "integer"}},
    "required": ["x"],
    "additionalProperties": False,
}


def make_registry(run):
    return ToolRegistry([Tool("double", "double x", SCHEMA, run)])


def test_valid_dispatch_runs():
    reg = make_registry(lambda a: str(a["x"] * 2))
    assert reg.dispatch("double", {"x": 21}) == "42"


def test_invalid_input_is_not_executed():
    ran: list[int] = []
    reg = make_registry(lambda a: (ran.append(1), "ok")[1])
    out = reg.dispatch("double", {"x": "not-an-int"})
    assert out.startswith("error: invalid input")
    assert ran == []  # run() was never called


def test_unknown_tool():
    reg = make_registry(lambda a: "ok")
    assert reg.dispatch("nope", {"x": 1}) == "error: unknown tool 'nope'"


def test_tool_exception_is_caught():
    def boom(a):
        raise ValueError("kaboom")

    reg = make_registry(boom)
    out = reg.dispatch("double", {"x": 1})
    assert out.startswith("error: ValueError") and "kaboom" in out


def test_specs_shape():
    reg = make_registry(lambda a: "ok")
    spec = reg.specs()[0]
    assert spec["name"] == "double" and "input_schema" in spec
