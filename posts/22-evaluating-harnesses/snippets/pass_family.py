"""Post 22: pass@1, pass@k and pass^k from one matrix of repeated trials, and why each answers a different question.

Run from the series root:  uv run python posts/22-evaluating-harnesses/snippets/pass_family.py

The counts are illustrative: ten tasks, each run eight times (n = 8), with c successes per task. The estimators are
the unbiased ones: pass@k = 1 - C(n - c, k) / C(n, k) averaged over tasks (Chen et al., 2021, "Evaluating Large
Language Models Trained on Code") and pass^k = C(c, k) / C(n, k) averaged over tasks (Yao et al., 2024, tau-bench).
Both use all n trials of a task, not only the first k. The last column raises the pooled pass@1 to the k-th power,
the shortcut that is wrong when tasks differ in difficulty: pass^k is an average of per-task reliabilities, and an
average of powers is not the power of an average.
"""
from math import comb

N = 8                                    # trials per task
COUNTS = [8, 8, 7, 6, 5, 4, 3, 2, 1, 0]  # successes per task, illustrative


def pass_at_1(counts, n):
    """Mean single-trial success; counts[t] is c, the successes of task t in n trials."""
    return sum(c / n for c in counts) / len(counts)


def pass_at_k(counts, n, k):
    """At least one of k trials succeeds: 1 - C(n - c, k) / C(n, k), averaged over tasks."""
    return sum(1 - comb(n - c, k) / comb(n, k) for c in counts) / len(counts)


def pass_hat_k(counts, n, k):
    """All k trials succeed: C(c, k) / C(n, k), averaged over tasks."""
    return sum(comb(c, k) / comb(n, k) for c in counts) / len(counts)


def main():
    p1 = pass_at_1(COUNTS, N)
    print(f"{len(COUNTS)} tasks, {N} trials each, successes per task: {COUNTS}")
    print(f"pass@1 = {p1:.3f}")
    print("  k   pass@k   pass^k   (pass@1)^k")
    for k in (1, 2, 4, 8):
        print(f"  {k}   {pass_at_k(COUNTS, N, k):.3f}    {pass_hat_k(COUNTS, N, k):.3f}    {p1 ** k:.3f}")
    return {"p1": p1, **{f"at{k}": pass_at_k(COUNTS, N, k) for k in (1, 2, 4, 8)},
            **{f"hat{k}": pass_hat_k(COUNTS, N, k) for k in (1, 2, 4, 8)}}


if __name__ == "__main__":
    main()
