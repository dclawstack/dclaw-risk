"""Unit tests for the FAIR Monte Carlo calculator.

Pure-math tests; no database, no HTTP, no LLM.
"""

import pytest

from app.services.fair_calculator import FairInputs, simulate


def test_simulate_percentiles_monotonic():
    result = simulate(
        FairInputs(
            loss_min=1_000,
            loss_mode=10_000,
            loss_max=100_000,
            freq_min=0.1,
            freq_max=1.0,
            iterations=5_000,
        ),
        seed=42,
    )
    assert result.p10 <= result.p50 <= result.p90
    assert result.mean > 0
    assert len(result.curve) > 10
    # Curve exceedance probabilities should be monotonically decreasing
    probs = [p["exceedance_probability"] for p in result.curve]
    assert probs == sorted(probs, reverse=True)


def test_simulate_zero_loss_when_inputs_zero():
    result = simulate(
        FairInputs(
            loss_min=0,
            loss_mode=0,
            loss_max=0,
            freq_min=0,
            freq_max=1,
            iterations=200,
        ),
        seed=1,
    )
    assert result.mean == 0
    assert result.p50 == 0


def test_simulate_deterministic_with_seed():
    a = simulate(
        FairInputs(
            loss_min=10,
            loss_mode=100,
            loss_max=1000,
            freq_min=0.5,
            freq_max=2.0,
            iterations=1000,
        ),
        seed=7,
    )
    b = simulate(
        FairInputs(
            loss_min=10,
            loss_mode=100,
            loss_max=1000,
            freq_min=0.5,
            freq_max=2.0,
            iterations=1000,
        ),
        seed=7,
    )
    assert a.mean == b.mean
    assert a.p50 == b.p50


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        FairInputs(
            loss_min=100,
            loss_mode=10,
            loss_max=1000,
            freq_min=0,
            freq_max=1,
            iterations=200,
        )
    with pytest.raises(ValueError):
        FairInputs(
            loss_min=10,
            loss_mode=100,
            loss_max=1000,
            freq_min=2.0,
            freq_max=1.0,
            iterations=200,
        )
