"""Portfolio allocation and position sizing helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


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
    if inputs.capital <= 0:
        raise ValueError("Capital must be positive")
    if not 0 < inputs.risk_per_trade <= 1:
        raise ValueError("risk_per_trade must be in the range (0, 1]")
    if not 0 < inputs.max_weight <= 1:
        raise ValueError("max_weight must be in the range (0, 1]")

    risk_budget = inputs.capital * inputs.risk_per_trade
    max_by_risk = int(risk_budget // risk_per_share)
    max_by_weight = int((inputs.capital * inputs.max_weight) // inputs.entry_price)
    return max(0, min(max_by_risk, max_by_weight))


def atr_stop_loss(entry_price: float, atr_value: float, multiplier: float = 2.0) -> float:
    """Calculate a long-position ATR stop loss."""
    if entry_price <= 0 or atr_value < 0:
        raise ValueError("Entry price must be positive and ATR cannot be negative")
    return round(entry_price - (atr_value * multiplier), 2)


def equal_weight_allocation(symbols: list[str], capital: float, max_weight: float = 0.20) -> pd.DataFrame:
    """Create an equal-weight target allocation capped by max position weight."""
    if not symbols:
        raise ValueError("At least one symbol is required")
    if capital <= 0:
        raise ValueError("Capital must be positive")
    unique_symbols = list(dict.fromkeys(symbol.strip().upper() for symbol in symbols if symbol.strip()))
    if not unique_symbols:
        raise ValueError("At least one valid symbol is required")
    weight = min(1 / len(unique_symbols), max_weight)
    return pd.DataFrame(
        {
            "symbol": unique_symbols,
            "target_weight": [weight] * len(unique_symbols),
            "target_value": [round(capital * weight, 2)] * len(unique_symbols),
        }
    )
