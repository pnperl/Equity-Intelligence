"""Tests for scoring and portfolio sizing."""

import pandas as pd

from portfolio import PositionSizingInput, position_size
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
