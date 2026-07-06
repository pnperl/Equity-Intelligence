"""High-level orchestration for stock analysis workflows."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from data import MarketDataClient
from fundamentals import FundamentalSnapshot, build_fundamental_snapshot, score_fundamentals
from indicators import add_indicators
from scoring import ScoreBreakdown, score_stock

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class StockAnalysis:
    """Complete analysis result for a single stock."""

    symbol: str
    history: pd.DataFrame
    score: ScoreBreakdown
    fundamentals: FundamentalSnapshot | None = None

    @property
    def latest_close(self) -> float:
        """Return the latest close price."""
        return float(self.history.dropna(subset=["Close"]).iloc[-1]["Close"])


def analyze_stock(symbol: str, period: str = "1y", include_fundamentals: bool = True) -> StockAnalysis:
    """Fetch data, indicators, fundamentals, and scores for one stock."""
    client = MarketDataClient()
    history = add_indicators(client.history(symbol, period=period))
    fundamentals = None
    fundamental_score = None
    if include_fundamentals:
        fundamentals = build_fundamental_snapshot(client.info(symbol))
        fundamental_score = score_fundamentals(fundamentals)
    score = score_stock(history, fundamental_score=fundamental_score)
    return StockAnalysis(symbol=symbol.upper(), history=history, score=score, fundamentals=fundamentals)


def analyze_watchlist(symbols: list[str], period: str = "1y") -> pd.DataFrame:
    """Analyze a watchlist and return a summary table."""
    columns = ["symbol", "close", "technical", "risk", "overall", "rating"]
    rows: list[dict[str, object]] = []
    for symbol in symbols:
        try:
            analysis = analyze_stock(symbol, period=period, include_fundamentals=False)
        except Exception:
            LOGGER.exception("Unable to analyze %s", symbol)
            continue
        rows.append(
            {
                "symbol": analysis.symbol,
                "close": analysis.latest_close,
                "technical": analysis.score.technical,
                "risk": analysis.score.risk,
                "overall": analysis.score.overall,
                "rating": analysis.score.rating,
            }
        )
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows).sort_values("overall", ascending=False)
