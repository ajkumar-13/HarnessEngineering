"""Post 17, sections 8 and 10: the merge-gate ceiling and the chance of a failure somewhere in a round.

Run from the series root:  uv run python posts/17-parallel-agents-shared-repo/snippets/gate_ceiling.py

Closed forms, with illustrative inputs:

  throughput   N agents each produce a verified branch every T minutes; one serialised merge gate takes G
               minutes per candidate. Landings per hour = min(60 N / T, 60 / G); the gate saturates at N* = T / G.
  Stripe       1,300 AI pull requests a week (reported by MindStudio, 9 April 2026), spread evenly over the 168
               hours of a week and landed through one serialised gate, leave the gate this many minutes each.
  failures     each agent fails a task independently with probability p; a round of N parallel tasks contains at
               least one failure with probability 1 - (1 - p)^N.

Standard library only.
"""
T, G = 30, 8                       # illustrative: a 30-minute task, an 8-minute gate
AGENTS = (1, 2, 3, 4, 8, 16)


def landings_per_hour(n, t=T, g=G):
    return min(60 * n / t, 60 / g)


def main():
    print(f"task T = {T} min, gate G = {G} min, so N* = T / G = {T / G:.2f} agents")
    print("agents  produced/h  ceiling/h  landed/h  gain")
    previous = 0.0
    for n in AGENTS:
        landed = landings_per_hour(n)
        print(f"{n:>6}  {60 * n / T:>10.1f}  {60 / G:>9.1f}  {landed:>8.1f}  {landed - previous:+.1f}")
        previous = landed
    print(f"gate halved to {G // 2} min: ceiling {60 / (G // 2):.1f}/h, N* = {T / (G // 2):.1f}")
    per_hour = 1300 / (7 * 24)
    print(f"Stripe: 1300 / 168 h = {per_hour:.2f} landings/h, so one gate has {60 / per_hour:.2f} min each")
    p = 0.05
    for n in (1, 16):
        print(f"p = {p}: N = {n:>2} parallel tasks, P(at least one failure) = {1 - (1 - p) ** n:.1%}")


if __name__ == "__main__":
    main()
