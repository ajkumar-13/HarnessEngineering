"""Offline tests for the file-based task board. Run: python -m pytest -q"""
import pytest

from parallel_agents.task_board import TaskBoard, worktree_for


def make_board(tmp_path, n=5):
    board = TaskBoard(tmp_path)
    for i in range(1, n + 1):
        board.add(f"task-{i}")
    return board


def test_add_and_list_open(tmp_path):
    board = make_board(tmp_path, 3)
    assert board.open_tasks() == ["task-1", "task-2", "task-3"]


def test_claim_removes_task_from_open(tmp_path):
    board = make_board(tmp_path, 2)
    task = board.claim("ada")
    assert task in {"task-1", "task-2"}
    assert task not in board.open_tasks()


def test_claim_returns_none_when_empty(tmp_path):
    board = TaskBoard(tmp_path)
    assert board.claim("ada") is None


def test_each_task_claimed_exactly_once(tmp_path):
    board = make_board(tmp_path, 6)
    agents = ["a", "b", "c"]
    claimed = []
    i = 0
    while board.open_tasks():
        task = board.claim(agents[i % len(agents)])
        if task:
            claimed.append(task)
        i += 1
    assert sorted(claimed) == [f"task-{i}" for i in range(1, 7)]
    assert len(claimed) == len(set(claimed))  # no task claimed twice


def test_interleaved_claims_never_collide(tmp_path):
    board = make_board(tmp_path, 4)
    a_got, b_got = [], []
    while board.open_tasks():
        ta = board.claim("a")
        tb = board.claim("b")
        if ta:
            a_got.append(ta)
        if tb:
            b_got.append(tb)
    assert set(a_got).isdisjoint(b_got)
    assert sorted(a_got + b_got) == ["task-1", "task-2", "task-3", "task-4"]


def test_complete_moves_task_to_done(tmp_path):
    board = make_board(tmp_path, 1)
    task = board.claim("ada")
    board.complete(task, "ada", result="done it")
    assert board.counts()["done"] == 1
    assert board.open_tasks() == []
    assert (tmp_path / "done" / task).read_text(encoding="utf-8") == "done it"


def test_complete_requires_the_claiming_agent(tmp_path):
    board = make_board(tmp_path, 1)
    task = board.claim("ada")
    with pytest.raises(ValueError):
        board.complete(task, "linus")  # linus did not claim it


def test_worktree_is_isolated_per_agent(tmp_path):
    a = worktree_for(tmp_path, "ada")
    b = worktree_for(tmp_path, "linus")
    assert a != b
    assert a.exists() and b.exists()


def test_concurrent_claims_are_exactly_once(tmp_path):
    """The invariant the board exists to demonstrate, under real threads.

    Every other test here is single-threaded, so none of them can observe the
    race: two agents each being told they own the same task while only one file
    lands in ``claimed/``. This is the shape of test that can.
    """
    import threading

    board = TaskBoard(tmp_path)
    n_tasks, n_threads = 400, 8
    for i in range(n_tasks):
        board.add(f"task-{i}")

    claims = []
    lock = threading.Lock()
    barrier = threading.Barrier(n_threads)

    def worker(agent):
        barrier.wait()  # maximise overlap on the first claim
        while True:
            name = board.claim(f"a{agent}")
            if name is None:
                return
            with lock:
                claims.append(name)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(claims) == len(set(claims)), "a task was claimed by two agents"
    assert len(claims) == n_tasks
