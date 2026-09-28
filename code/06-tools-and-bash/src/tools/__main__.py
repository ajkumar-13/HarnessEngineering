"""Offline demo: `python -m tools`.

Builds a registry with a sandboxed bash tool, then shows three dispatches — a
safe command (runs), a dangerous command (blocked by the deny-list), and a
malformed call (rejected by schema validation) — none of which can crash the loop.
"""
from .bash_tool import make_bash_tool
from .registry import ToolRegistry


def main() -> None:
    registry = ToolRegistry([make_bash_tool()])

    print("tools exposed to the model:")
    for spec in registry.specs():
        print(f"  - {spec['name']}: {spec['description'][:58]}...")
    print()

    cases = [
        ("safe", {"command": "echo hello from the bash tool"}),
        ("dangerous", {"command": "rm -rf /"}),
        ("malformed", {"cmd": "echo oops"}),   # wrong key -> schema rejects it
    ]
    for label, tool_input in cases:
        result = registry.dispatch("bash", tool_input)
        print(f"[{label:9}] dispatch('bash', {tool_input})")
        print(f"            -> {result}\n")


if __name__ == "__main__":
    main()
