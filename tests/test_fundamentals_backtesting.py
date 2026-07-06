"""Tests for fundamentals and backtesting."""

import pandas as pd

from backtesting import moving_average_crossover
from fundamentals import build_fundamental_snapshot, score_fundamentals
from indicators import add_indicators


def test_fundamental_snapshot_scores_quality_company() -> None:
    snapshot = build_fundamental_snapshot(
        {
            "trailingPE": 20,
            "priceToBook": 3,
            "debtToEquity": 40,
            "returnOnEquity": 0.18,
            "profitMargins": 0.16,
            "revenueGrowth": 0.08,
            "earningsGrowth": 0.12,
        }
    )

    assert score_fundamentals(snapshot) > 75


def test_moving_average_crossover_returns_extended_metrics() -> None:
    frame = pd.DataFrame(
        {
            "Open": range(1, 260),
            "High": range(2, 261),
            "Low": range(0, 259),
            "Close": range(1, 260),
            "Volume": [1000] * 259,
        }
    )
    enriched = add_indicators(frame)

    result = moving_average_crossover(enriched)

    assert result.total_return >= 0
    assert result.annualized_return >= 0
    assert result.trades >= 0
