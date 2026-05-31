"""Composite equity scoring engine."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ScoreBreakdown:
    """Structured score output for a stock."""

    technical: float
    risk: float
    overall: float
    rating: str


def score_stock(frame: pd.DataFrame) -> ScoreBreakdown:
    """Score a stock using the latest enriched indicator row."""
    if frame.empty:
        raise ValueError("Cannot score an empty DataFrame")

    latest = frame.dropna(subset=["Close"]).iloc[-1]
    technical = _technical_score(latest)
    risk = _risk_score(latest)
    overall = round((technical * 0.6) + (risk * 0.4), 2)
    return ScoreBreakdown(technical=technical, risk=risk, overall=overall, rating=_rating(overall))


def _technical_score(row: pd.Series) -> float:
    score = 50.0
    if row.get("Close", 0) > row.get("sma_50", float("inf")):
        score += 15
    if row.get("ema_20", 0) > row.get("sma_50", float("inf")):
        score += 10
    if row.get("macd", 0) > row.get("macd_signal", float("inf")):
        score += 10
    rsi_value = row.get("rsi_14", 50)
    if 55 <= rsi_value <= 70:
        score += 15
    elif rsi_value < 40 or rsi_value > 80:
        score -= 15
    return round(max(0, min(100, score)), 2)


def _risk_score(row: pd.Series) -> float:
    close = row.get("Close", 0)
    atr_value = row.get("atr_14", 0)
    if close <= 0 or pd.isna(atr_value):
        return 50.0
    atr_percent = (atr_value / close) * 100
    return round(max(0, min(100, 100 - (atr_percent * 10))), 2)


def _rating(score: float) -> str:
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Positive"
    if score >= 45:
        return "Neutral"
    return "Weak"
