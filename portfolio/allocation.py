"""Position sizing helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PositionSizingInput:
    """Inputs required to calculate risk-based position size."""

    capital: float
    entry_price: float
    stop_loss: float
    risk_per_trade: float = 0.01
    max_weight: float = 0.20


def position_size(inputs: PositionSizingInput) -> int:
    """Return share quantity constrained by risk and max allocation."""
    risk_per_share = abs(inputs.entry_price - inputs.stop_loss)
    if risk_per_share <= 0 or inputs.entry_price <= 0:
        raise ValueError("Entry price and stop loss must define positive per-share risk")

    risk_budget = inputs.capital * inputs.risk_per_trade
    max_by_risk = int(risk_budget // risk_per_share)
    max_by_weight = int((inputs.capital * inputs.max_weight) // inputs.entry_price)
    return max(0, min(max_by_risk, max_by_weight))
