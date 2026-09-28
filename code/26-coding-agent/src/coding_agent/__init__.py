"""Capstone — a long-running, trusted coding-agent harness.

Companion to Harness Engineering, Post 26. Ties the series together: a Ralph-style
long-horizon driver (Posts 18-19), separated planner/generator/evaluator roles
(Post 12), the ratchet (Post 10), tracing (Post 21), and a cost ceiling
(Posts 19, 23). Offline by design.
"""
from .core import (Spec, Task, VerifyResult, Verifier, Workspace,
                   python_function_verifier)
from .cost import CostMeter
from .driver import BuildResult, Commit, Generator, build, plan
from .memory import Ratchet
from .observe import Span, Tracer

__all__ = [
    "Spec", "Task", "Workspace", "VerifyResult", "Verifier",
    "python_function_verifier",
    "CostMeter", "Ratchet", "Tracer", "Span",
    "build", "plan", "BuildResult", "Commit", "Generator",
]
