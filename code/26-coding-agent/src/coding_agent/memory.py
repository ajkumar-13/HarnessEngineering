"""The ratchet: every failure becomes a durable rule (Post 10).

When a task fails in a way worth remembering, the driver asks the ratchet to
learn a rule. The rule is injected into the generator's context on every later
attempt and every later task, so the same mistake cannot recur. This is how a
long run gets *better* as it goes instead of repeating itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Ratchet:
    """An append-only list of learned rules, optionally mirrored to a file."""
    rules: List[str] = field(default_factory=list)
    path: Optional[str] = None

    def learn(self, rule: str) -> bool:
        """Record a rule if it is new. Returns True if it was added."""
        if rule in self.rules:
            return False
        self.rules.append(rule)
        if self.path is not None:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(rule + "\n")
        return True

    def as_context(self) -> str:
        """Render the rules for injection into the generator (a pilot's
        checklist, not a style guide — Post 10)."""
        if not self.rules:
            return ""
        lines = "\n".join(f"- {r}" for r in self.rules)
        return "Learned rules (do not repeat past mistakes):\n" + lines
