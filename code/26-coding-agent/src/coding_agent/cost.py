"""A per-run cost and latency meter with a hard budget ceiling (Post 23).

Every attempt spends tokens and seconds. The meter sums them across the whole
long-horizon run and prices them. The budget ceiling is an economic guardrail
*and* a stop condition (Post 19): when the run would exceed it, the driver stops
rather than spending without bound.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostMeter:
    """Prices are US dollars per million tokens; ``budget_usd`` is the ceiling
    (``None`` means unbounded). ``cache_discount`` models the cheaper re-read of
    a cached prefix across iterations (Post 23)."""
    input_price: float = 3.0     # $ / 1M input tokens
    output_price: float = 15.0   # $ / 1M output tokens
    budget_usd: float | None = None
    cache_discount: float = 0.1  # cached input tokens cost 10% of the base rate

    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0

    def add(self, *, input_tokens: int = 0, output_tokens: int = 0,
            cached_tokens: int = 0, seconds: float = 0.0) -> None:
        self.input_tokens += input_tokens
        self.cached_tokens += cached_tokens
        self.output_tokens += output_tokens
        self.seconds += seconds

    def cost(self) -> float:
        fresh_in = self.input_tokens - self.cached_tokens
        dollars = (
            fresh_in * self.input_price
            + self.cached_tokens * self.input_price * self.cache_discount
            + self.output_tokens * self.output_price
        ) / 1_000_000
        return round(dollars, 6)

    def over_budget(self) -> bool:
        return self.budget_usd is not None and self.cost() >= self.budget_usd

    def summary(self) -> str:
        return (f"${self.cost():.4f} · {self.input_tokens} in "
                f"({self.cached_tokens} cached) · {self.output_tokens} out "
                f"· {self.seconds:.1f}s")
