"""Post 11, tests as ground truth: the companion's test_cases() turns (args, expected) pairs into a verifier.

Run from the series root:  uv run python posts/11-verification-loops/snippets/test_cases_report.py
It imports code/11-verification-loop unchanged and prints the verdict on three candidates: a wrong one,
one that raises, and a namespace that defines nothing.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "11-verification-loop" / "src"))

from verification_loop.checks import test_cases

verify = test_cases("is_prime", [((1,), False), ((2,), True), ((25,), False)])
print(verify({"is_prime": lambda n: all(n % d for d in range(2, n))}))
print(verify({"is_prime": lambda n: not [d for d in range(2, n) if n % d == 0][0]}))
print(verify({}))
