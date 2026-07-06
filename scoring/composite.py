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
    fundamental: float | None = None


def score_stock(frame: pd.DataFrame, fundamental_score: float | None = None) -> ScoreBreakdown:
    """Score a stock using the latest enriched indicator row."""
    if frame.empty:
        raise ValueError("Cannot score an empty DataFrame")

    valid = frame.dropna(subset=["Close"])
    if valid.empty:
        raise ValueError("No valid Close prices to score")
    latest = valid.iloc[-1]
    technical = _technical_score(latest)
    risk = _risk_score(latest)
    if fundamental_score is None:
        overall = round((technical * 0.6) + (risk * 0.4), 2)
    else:
        overall = round((technical * 0.5) + (risk * 0.25) + (fundamental_score * 0.25), 2)
    return ScoreBreakdown(
        technical=technical,
        risk=risk,
        fundamental=fundamental_score,
        overall=overall,
        rating=_rating(overall),
    )


def score_multi_timeframe(frames: dict[str, pd.DataFrame], fundamental_score: float | None = None) -> ScoreBreakdown:
    """Combine scores from multiple enriched timeframes into one score."""
    if not frames:
        raise ValueError("At least one timeframe is required")

    weights = _timeframe_weights(frames.keys())
    technical = 0.0
    risk = 0.0
    for name, frame in frames.items():
        score = score_stock(frame)
        technical += score.technical * weights[name]
        risk += score.risk * weights[name]

    technical = round(technical, 2)
    risk = round(risk, 2)
    if fundamental_score is None:
        overall = round((technical * 0.6) + (risk * 0.4), 2)
    else:
        overall = round((technical * 0.5) + (risk * 0.25) + (fundamental_score * 0.25), 2)
    return ScoreBreakdown(technical=technical, risk=risk, fundamental=fundamental_score, overall=overall, rating=_rating(overall))


def _timeframe_weights(names: object) -> dict[str, float]:
    """Return normalized timeframe weights, favoring longer-term frames."""
    preferred = {"short": 0.25, "medium": 0.35, "long": 0.40, "6mo": 0.25, "1y": 0.35, "2y": 0.40, "5y": 0.40}
    raw = {str(name): preferred.get(str(name), 1.0) for name in names}
    total = sum(raw.values())
    return {name: value / total for name, value in raw.items()}


def _technical_score(row: pd.Series) -> float:
    score = 50.0
    if row.get("Close", 0) > row.get("sma_50", float("inf")):
        score += 12
    if row.get("ema_20", 0) > row.get("ema_50", row.get("sma_50", float("inf"))):
        score += 8
    if row.get("macd", 0) > row.get("macd_signal", float("inf")):
        score += 10
    if row.get("plus_di_14", 0) > row.get("minus_di_14", float("inf")) and row.get("adx_14", 0) >= 20:
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
