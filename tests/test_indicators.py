"""Tests for technical indicators."""

import pandas as pd

from indicators import add_indicators, sma


def test_sma_calculates_expected_values() -> None:
    series = pd.Series([1, 2, 3, 4, 5])

    result = sma(series, 3)

    assert result.iloc[-1] == 4


def test_add_indicators_preserves_rows() -> None:
    frame = pd.DataFrame(
        {
            "Open": range(1, 61),
            "High": range(2, 62),
            "Low": range(0, 60),
            "Close": range(1, 61),
            "Volume": [1000] * 60,
        }
    )

    enriched = add_indicators(frame)

    assert len(enriched) == len(frame)
    assert "rsi_14" in enriched.columns
    assert "macd" in enriched.columns
