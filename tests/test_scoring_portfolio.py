"""Tests for scoring and portfolio sizing."""

import pandas as pd

from portfolio import PositionSizingInput, atr_stop_loss, equal_weight_allocation, position_size
from scoring import score_stock


def test_score_stock_returns_rating() -> None:
    frame = pd.DataFrame(
        [
            {
                "Close": 100,
                "sma_50": 90,
                "ema_20": 95,
                "macd": 2,
                "macd_signal": 1,
                "rsi_14": 60,
                "atr_14": 2,
            }
        ]
    )

    score = score_stock(frame)

    assert score.overall > 0
    assert score.rating in {"Strong", "Positive", "Neutral", "Weak"}


def test_position_size_respects_max_weight() -> None:
    inputs = PositionSizingInput(capital=100_000, entry_price=1_000, stop_loss=950)

    assert position_size(inputs) == 20


def test_atr_stop_and_equal_weight_allocation() -> None:
    assert atr_stop_loss(100, 5, multiplier=2) == 90

    allocation = equal_weight_allocation(["RELIANCE", "INFY"], capital=100_000)

    assert list(allocation["target_weight"]) == [0.2, 0.2]
