"""Offline tests for the verification loop. Run: python -m pytest -q"""
import pytest

from verification_loop.checks import test_cases as build_verifier
from verification_loop.loop import VerifyResult, solve


def test_passes_first_attempt_is_silent():
    calls = []

    def verify(candidate):
        calls.append(candidate)
        return VerifyResult(True)

    result = solve(lambda feedback: "x", verify)
    assert result.verified
    assert result.attempts == 1
    assert len(calls) == 1  # success is silent: no retry once a check passes


def test_retries_until_green():
    verdicts = iter([VerifyResult(False, "nope"), VerifyResult(False, "still"), VerifyResult(True)])
    result = solve(lambda feedback: "cand", lambda c: next(verdicts))
    assert result.verified
    assert result.attempts == 3


def test_failure_report_is_threaded_back():
    seen = []

    def generate(feedback):
        seen.append(feedback)
        return "cand"

    verdicts = iter([VerifyResult(False, "err-1"), VerifyResult(True)])
    solve(generate, lambda c: next(verdicts))
    assert seen == [None, "err-1"]  # None first, then the previous failure report


def test_gives_up_after_max_attempts():
    result = solve(
        lambda feedback: "bad",
        lambda c: VerifyResult(False, "always fails"),
        max_attempts=3,
    )
    assert not result.verified
    assert result.attempts == 3
    assert "always fails" in result.report


def test_rejects_bad_max_attempts():
    with pytest.raises(ValueError):
        solve(lambda feedback: "x", lambda c: VerifyResult(True), max_attempts=0)


def test_test_cases_verifier_passes_and_reports():
    verify = build_verifier("f", [((2,), 4), ((3,), 9)])
    good = verify({"f": lambda x: x * x})
    assert good.ok and good.report == ""
    bad = verify({"f": lambda x: x + x})  # f(3) == 6, not 9
    assert not bad.ok and "expected 9" in bad.report


def test_test_cases_missing_function_is_reported_not_raised():
    verify = build_verifier("f", [((1,), 1)])
    result = verify({})
    assert not result.ok and "no callable" in result.report


def test_test_cases_exception_is_reported_not_raised():
    verify = build_verifier("f", [((0,), 1)])
    result = verify({"f": lambda x: 1 / x})  # ZeroDivisionError
    assert not result.ok and "ZeroDivisionError" in result.report


def test_demo_model_converges_in_three_attempts():
    from verification_loop.__main__ import make_mock_model

    verify = build_verifier(
        "is_prime",
        [((1,), False), ((2,), True), ((4,), False), ((13,), True), ((25,), False)],
    )
    result = solve(make_mock_model(), verify, max_attempts=5)
    assert result.verified
    assert result.attempts == 3  # buggy, buggy, then correct
