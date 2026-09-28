"""The schema validator is the tool contract — test what it accepts and rejects."""
from tools.schema import validate

SCHEMA = {
    "type": "object",
    "properties": {
        "command": {"type": "string"},
        "count": {"type": "integer"},
        "mode": {"type": "string", "enum": ["fast", "slow"]},
    },
    "required": ["command"],
    "additionalProperties": False,
}


def test_valid_minimal():
    assert validate({"command": "ls"}, SCHEMA) == []


def test_missing_required():
    errs = validate({}, SCHEMA)
    assert any("missing required property 'command'" in e for e in errs)


def test_wrong_type():
    errs = validate({"command": "ls", "count": "three"}, SCHEMA)
    assert any("expected integer" in e for e in errs)


def test_additional_property_rejected():
    errs = validate({"command": "ls", "extra": 1}, SCHEMA)
    assert any("unexpected property 'extra'" in e for e in errs)


def test_enum_accepts_and_rejects():
    assert validate({"command": "ls", "mode": "fast"}, SCHEMA) == []
    errs = validate({"command": "ls", "mode": "warp"}, SCHEMA)
    assert any("is not one of" in e for e in errs)


def test_bool_is_not_an_integer():
    errs = validate({"command": "ls", "count": True}, SCHEMA)
    assert any("expected integer" in e for e in errs)
