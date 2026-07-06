"""Simple vectorized backtesting utilities."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    """Summary statistics and equity curve for a backtest."""

    total_return: float
    annualized_return: float
    max_drawdown: float
    volatility: float
    sharpe: float
    trades: int
    equity_curve: pd.Series


def moving_average_crossover(frame: pd.DataFrame, fast: str = "sma_20", slow: str = "sma_50") -> BacktestResult:
    """Backtest a long-only moving-average crossover strategy."""
    if frame.empty:
        raise ValueError("Cannot backtest an empty DataFrame")
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
    total_return = float(equity_curve.iloc[-1] - 1)
    periods = max(len(strategy_returns), 1)
    annualized_return = float(equity_curve.iloc[-1] ** (252 / periods) - 1)
    volatility = float(strategy_returns.std() * (252**0.5))
    sharpe = float(annualized_return / volatility) if volatility else 0.0
    return BacktestResult(
        total_return=round(total_return, 4),
        annualized_return=round(annualized_return, 4),
        max_drawdown=round(float(drawdown.min()), 4),
        volatility=round(volatility, 4),
        sharpe=round(sharpe, 4),
        trades=trades,
        equity_curve=equity_curve,
    )
