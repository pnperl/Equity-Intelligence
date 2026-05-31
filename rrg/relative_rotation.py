"""Relative strength calculations for sector rotation analysis."""

from __future__ import annotations

import pandas as pd


def relative_strength(asset_close: pd.Series, benchmark_close: pd.Series, window: int = 20) -> pd.DataFrame:
    """Calculate relative strength ratio and momentum against a benchmark."""
    aligned = pd.concat([asset_close, benchmark_close], axis=1, keys=["asset", "benchmark"]).dropna()
    ratio = aligned["asset"] / aligned["benchmark"]
    normalized = 100 * ratio / ratio.rolling(window=window, min_periods=window).mean()
    momentum = normalized - normalized.shift(window)
    return pd.DataFrame({"rs_ratio": normalized, "rs_momentum": momentum})
