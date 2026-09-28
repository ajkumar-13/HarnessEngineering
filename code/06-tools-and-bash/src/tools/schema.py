"""A tiny JSON-Schema-subset validator — enough to make a tool call a contract.

Supports: type (object / array / string / number / integer / boolean / null),
properties, required, enum, additionalProperties (bool), and items. Returns a
list of human-readable error strings; an empty list means valid. No external
dependencies — this is the whole validator Post 06 relies on.
"""
from __future__ import annotations

_TYPES = {
    "object": dict, "array": list, "string": str,
    "number": (int, float), "integer": int, "boolean": bool, "null": type(None),
}


def _type_ok(value, expected: str) -> bool:
    # bool is a subclass of int in Python — keep the JSON types distinct.
    if expected == "boolean":
        return isinstance(value, bool)
    if expected in ("integer", "number") and isinstance(value, bool):
        return False
    py = _TYPES.get(expected)
    return isinstance(value, py) if py is not None else True


def _typename(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    for name, py in _TYPES.items():
        if name not in ("boolean", "integer", "number") and isinstance(value, py):
            return name
    return type(value).__name__


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Return a list of validation errors for `instance` against `schema`."""
    errors: list[str] = []
    expected = schema.get("type")
    if expected and not _type_ok(instance, expected):
        return [f"{path}: expected {expected}, got {_typename(instance)}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")

    if expected == "object" and isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected property '{key}'")
        for key, value in instance.items():
            if key in props:
                errors += validate(value, props[key], f"{path}.{key}")

    if expected == "array" and isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors += validate(item, schema["items"], f"{path}[{i}]")

    return errors
