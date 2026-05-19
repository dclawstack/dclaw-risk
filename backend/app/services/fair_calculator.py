"""FAIR-style quantitative risk calculator.

Uses a triangular distribution for loss magnitude and a uniform distribution
for loss event frequency, then aggregates iteration draws into annualised loss
exposure samples. Returns standard percentiles plus a loss-exceedance curve.

This is intentionally lightweight (numpy only). It approximates the full FAIR
ontology — sufficient for a P0 demo and for unit-testable math.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FairInputs:
    loss_min: float
    loss_mode: float
    loss_max: float
    freq_min: float
    freq_max: float
    iterations: int = 10_000

    def __post_init__(self) -> None:
        if not (self.loss_min <= self.loss_mode <= self.loss_max):
            raise ValueError("loss_min <= loss_mode <= loss_max required")
        if self.freq_min > self.freq_max:
            raise ValueError("freq_min <= freq_max required")
        if self.iterations < 100:
            raise ValueError("iterations must be >= 100")


@dataclass(frozen=True)
class FairResult:
    samples: np.ndarray
    p10: float
    p50: float
    p90: float
    mean: float
    curve: list[dict[str, float]]


def simulate(inputs: FairInputs, seed: int | None = None) -> FairResult:
    rng = np.random.default_rng(seed)
    n = inputs.iterations

    if inputs.loss_min == inputs.loss_max:
        losses_per_event = np.full(n, inputs.loss_mode)
    else:
        losses_per_event = rng.triangular(
            inputs.loss_min, inputs.loss_mode, inputs.loss_max, size=n
        )

    if inputs.freq_min == inputs.freq_max:
        frequencies = np.full(n, inputs.freq_min)
    else:
        frequencies = rng.uniform(inputs.freq_min, inputs.freq_max, size=n)

    annualised = losses_per_event * frequencies

    p10, p50, p90 = np.percentile(annualised, [10, 50, 90])
    mean = float(np.mean(annualised))

    curve = _exceedance_curve(annualised)

    return FairResult(
        samples=annualised,
        p10=float(p10),
        p50=float(p50),
        p90=float(p90),
        mean=mean,
        curve=curve,
    )


def _exceedance_curve(samples: np.ndarray, points: int = 50) -> list[dict[str, float]]:
    """Loss-exceedance curve: probability that annualised loss >= L.

    Returns a list of {loss, exceedance_probability} points sorted by loss
    ascending. Suitable for direct charting in the frontend.
    """
    sorted_samples = np.sort(samples)
    qs = np.linspace(0.0, 0.999, points)
    losses = np.quantile(sorted_samples, qs)
    exceedances = 1.0 - qs
    return [
        {"loss": float(loss), "exceedance_probability": float(prob)}
        for loss, prob in zip(losses, exceedances, strict=True)
    ]
