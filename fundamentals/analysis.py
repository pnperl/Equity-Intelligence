"""Fundamental analysis helpers built from yfinance info data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FundamentalSnapshot:
    """Normalized fundamental fields used by the scoring engine."""

    market_cap: float | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_book: float | None = None
    debt_to_equity: float | None = None
    return_on_equity: float | None = None
    profit_margins: float | None = None
    revenue_growth: float | None = None
    earnings_growth: float | None = None


def build_fundamental_snapshot(info: dict[str, Any]) -> FundamentalSnapshot:
    """Build a typed fundamental snapshot from a yfinance info dictionary."""
    return FundamentalSnapshot(
        market_cap=_to_float(info.get("marketCap")),
        trailing_pe=_to_float(info.get("trailingPE")),
        forward_pe=_to_float(info.get("forwardPE")),
        price_to_book=_to_float(info.get("priceToBook")),
        debt_to_equity=_to_float(info.get("debtToEquity")),
        return_on_equity=_to_float(info.get("returnOnEquity")),
        profit_margins=_to_float(info.get("profitMargins")),
        revenue_growth=_to_float(info.get("revenueGrowth")),
        earnings_growth=_to_float(info.get("earningsGrowth")),
    )


def score_fundamentals(snapshot: FundamentalSnapshot) -> float:
    """Score fundamentals on a 0-100 scale using valuation, quality, and growth."""
    score = 50.0
    if snapshot.trailing_pe and 0 < snapshot.trailing_pe <= 25:
        score += 10
    elif snapshot.trailing_pe and snapshot.trailing_pe > 60:
        score -= 10

    if snapshot.price_to_book and 0 < snapshot.price_to_book <= 5:
        score += 5
    elif snapshot.price_to_book and snapshot.price_to_book > 12:
        score -= 5

    if snapshot.debt_to_equity is not None:
        if snapshot.debt_to_equity <= 80:
            score += 10
        elif snapshot.debt_to_equity > 200:
            score -= 10

    if snapshot.return_on_equity and snapshot.return_on_equity >= 0.12:
        score += 10
    if snapshot.profit_margins and snapshot.profit_margins >= 0.10:
        score += 5
    if snapshot.revenue_growth and snapshot.revenue_growth > 0:
        score += 5
    if snapshot.earnings_growth and snapshot.earnings_growth > 0:
        score += 5

    return round(max(0, min(100, score)), 2)


def _to_float(value: Any) -> float | None:
    """Convert a value to float or return None when unavailable."""
    if value in (None, "", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
