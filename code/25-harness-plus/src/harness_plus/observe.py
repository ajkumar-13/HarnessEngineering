"""A tiny in-process tracer: the Post 21 observability wiring, no dependency.

A production stack would emit OpenTelemetry spans to a backend. The shape is the
same and small enough to build: a span has a name, attributes, and children, and
spans nest to form the trace tree for one run. This recorder keeps the tree in
memory so the demo can print it and a test can assert on it.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator, List


@dataclass
class Span:
    name: str
    attributes: dict = field(default_factory=dict)
    children: List["Span"] = field(default_factory=list)

    def set(self, key: str, value) -> "Span":
        self.attributes[key] = value
        return self

    def walk(self) -> "Iterator[tuple[int, Span]]":
        stack: list[tuple[int, Span]] = [(0, self)]
        while stack:
            depth, span = stack.pop()
            yield depth, span
            for child in reversed(span.children):
                stack.append((depth + 1, child))


class Tracer:
    """Opens nested spans via a context manager and keeps the root tree."""

    def __init__(self) -> None:
        self.root: Span | None = None
        self._stack: list[Span] = []

    @contextmanager
    def span(self, name: str, **attributes) -> "Iterator[Span]":
        span = Span(name, dict(attributes))
        if self._stack:
            self._stack[-1].children.append(span)
        elif self.root is None:
            self.root = span
        self._stack.append(span)
        try:
            yield span
        finally:
            self._stack.pop()

    def render(self) -> str:
        if self.root is None:
            return "(no trace)"
        lines = []
        for depth, span in self.root.walk():
            attrs = " ".join(f"{k}={v}" for k, v in span.attributes.items())
            lines.append("  " * depth + f"{span.name}" + (f"  [{attrs}]" if attrs else ""))
        return "\n".join(lines)

    def count(self, name: str) -> int:
        if self.root is None:
            return 0
        return sum(1 for _, s in self.root.walk() if s.name == name)
