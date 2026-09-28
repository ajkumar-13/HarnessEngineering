"""Offline tests for the capstone — the driver, the ratchet, cost, and trace."""
from coding_agent import (CostMeter, Ratchet, Spec, Task, Tracer, Workspace,
                         build, python_function_verifier)

ADD_OK = "def add(a, b):\n    return a + b\n"
ADD_BUG = "def add(a, b):\n    return a - b\n"


def _add_task():
    return Task("add", python_function_verifier("calc.py", "add",
                                                [((2, 3), 5), ((1, 1), 2)]))


def _good_gen(task, feedback, memory):
    return {"calc.py": ADD_OK}


def test_build_completes_a_passing_spec():
    spec = Spec([_add_task()])
    res = build(spec, _good_gen)
    assert res.succeeded is True
    assert res.stop_reason == "spec_complete"
    assert res.completed == ["add"]
    assert len(res.commits) == 1
    assert res.commits[0].files["calc.py"] == ADD_OK


def test_ratchet_learns_from_failure_then_the_fix_lands():
    # buggy until a rule about 'add' exists in memory, then correct
    def gen(task, feedback, memory):
        return {"calc.py": ADD_OK if "[add]" in memory else ADD_BUG}

    ratchet = Ratchet()
    res = build(Spec([_add_task()]), gen, ratchet=ratchet, max_attempts=3)
    assert res.succeeded is True
    assert res.rules_learned                       # a rule was recorded
    assert any("[add]" in r for r in res.rules_learned)
    # it took a second attempt: the fix used the learned rule
    assert res.completed == ["add"]


def test_unfixable_task_stops_the_build():
    res = build(Spec([_add_task()]), lambda t, f, m: {"calc.py": ADD_BUG},
                max_attempts=3)
    assert res.succeeded is False
    assert res.stop_reason == "task_failed"
    assert res.failed_task == "add"
    assert res.completed == []


def test_budget_ceiling_stops_the_run():
    # a tiny budget: the very first attempt's cost exceeds it on the next check
    cost = CostMeter(budget_usd=0.00001)
    # first task passes but spends; a second task's pre-attempt check trips budget
    spec = Spec([_add_task(), _add_task()])
    res = build(spec, _good_gen, cost=cost, max_attempts=2)
    assert res.stop_reason == "budget"
    assert res.succeeded is False


def test_ratchet_is_append_only_and_dedupes():
    r = Ratchet()
    assert r.learn("rule one") is True
    assert r.learn("rule one") is False   # duplicate ignored
    assert r.learn("rule two") is True
    assert r.rules == ["rule one", "rule two"]
    assert "rule one" in r.as_context()


def test_cost_meter_prices_and_discounts_cache():
    c = CostMeter(input_price=3.0, output_price=15.0, cache_discount=0.1)
    c.add(input_tokens=1000, cached_tokens=800, output_tokens=200)
    # fresh 200 in @3/M + cached 800 @0.3/M + 200 out @15/M
    expected = (200 * 3.0 + 800 * 0.3 + 200 * 15.0) / 1_000_000
    assert abs(c.cost() - round(expected, 6)) < 1e-9


def test_trace_tree_has_the_expected_shape():
    tracer = Tracer()
    spec = Spec([_add_task()])
    res = build(spec, _good_gen, tracer=tracer)
    assert res.trace is not None
    assert tracer.count("build.run") == 1
    assert tracer.count("task") == 1
    assert tracer.count("generate") == 1
    assert tracer.count("evaluate") == 1
    assert res.trace.attributes.get("stop.reason") == "spec_complete"


def test_commits_snapshot_growing_workspace():
    spec = Spec([
        Task("add", python_function_verifier("calc.py", "add", [((2, 3), 5)])),
        Task("is_even", python_function_verifier("p.py", "is_even", [((4,), True)])),
    ])

    def gen(task, feedback, memory):
        if task.name == "add":
            return {"calc.py": ADD_OK}
        return {"p.py": "def is_even(n):\n    return n % 2 == 0\n"}

    res = build(spec, gen)
    assert res.succeeded is True
    # the second commit carries both files: state accumulates across tasks
    assert set(res.commits[1].files) == {"calc.py", "p.py"}
