"""Market data access layer backed by yfinance."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
import yfinance as yf

LOGGER = logging.getLogger(__name__)


def normalize_nse_symbol(symbol: str, suffix: str = ".NS") -> str:
    """Return a yfinance-compatible NSE symbol.

    Existing index symbols and already-suffixed symbols are left unchanged.
    """
    cleaned = symbol.strip().upper()
    if cleaned.startswith("^") or cleaned.endswith(suffix):
        return cleaned
    return f"{cleaned}{suffix}"


@dataclass(frozen=True)
class MarketDataClient:
    """Download and validate OHLCV market data."""

    exchange_suffix: str = ".NS"

    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical OHLCV data for an NSE symbol or index."""
        normalized = normalize_nse_symbol(symbol, self.exchange_suffix)
        LOGGER.info("Downloading history for %s", normalized)
        frame = _download_history(normalized, period, interval)
        if frame.empty:
            raise ValueError(f"No market data returned for {normalized}")
        return frame


@lru_cache(maxsize=256)
def _download_history(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """Cached wrapper around yfinance.download."""
    frame = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    return frame.dropna(how="all")
