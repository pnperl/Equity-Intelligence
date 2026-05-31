"""Simple vectorized backtesting utilities."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    """Summary statistics and equity curve for a backtest."""

    total_return: float
    max_drawdown: float
    trades: int
    equity_curve: pd.Series


def moving_average_crossover(frame: pd.DataFrame, fast: str = "sma_20", slow: str = "sma_50") -> BacktestResult:
    """Backtest a long-only moving-average crossover strategy."""
    required = {"Close", fast, slow}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing columns for backtest: {sorted(missing)}")

    signals = (frame[fast] > frame[slow]).astype(int)
    positions = signals.shift(1).fillna(0)
    returns = frame["Close"].pct_change().fillna(0)
    strategy_returns = positions * returns
    equity_curve = (1 + strategy_returns).cumprod()
    drawdown = equity_curve / equity_curve.cummax() - 1
    trades = int(signals.diff().abs().fillna(0).sum())
    return BacktestResult(
        total_return=round(float(equity_curve.iloc[-1] - 1), 4),
        max_drawdown=round(float(drawdown.min()), 4),
        trades=trades,
        equity_curve=equity_curve,
    )
