"""Market data access layer backed by yfinance."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import pandas as pd
import yfinance as yf

LOGGER = logging.getLogger(__name__)

REQUIRED_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def normalize_nse_symbol(symbol: str, suffix: str = ".NS") -> str:
    """Return a yfinance-compatible NSE symbol.

    Existing index symbols and already-suffixed symbols are left unchanged.
    """
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise ValueError("Symbol cannot be blank")
    if cleaned.startswith("^") or cleaned.endswith(suffix):
        return cleaned
    return f"{cleaned}{suffix}"


@dataclass(frozen=True)
class MarketDataClient:
    """Download and validate OHLCV market and fundamental data."""

    exchange_suffix: str = ".NS"

    def history(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical OHLCV data for an NSE symbol or index."""
        normalized = normalize_nse_symbol(symbol, self.exchange_suffix)
        LOGGER.info("Downloading history for %s", normalized)
        frame = _download_history(normalized, period, interval)
        _validate_ohlcv(frame, normalized)
        return frame

    def histories(self, symbols: list[str], period: str = "1y", interval: str = "1d") -> dict[str, pd.DataFrame]:
        """Fetch historical data for multiple symbols, skipping failures with logs."""
        histories: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            try:
                histories[symbol] = self.history(symbol, period=period, interval=interval)
            except Exception:
                LOGGER.exception("Unable to download history for %s", symbol)
        return histories

    def info(self, symbol: str) -> dict[str, Any]:
        """Fetch the yfinance info dictionary for a symbol."""
        normalized = normalize_nse_symbol(symbol, self.exchange_suffix)
        LOGGER.info("Downloading info for %s", normalized)
        return _download_info(normalized)


def _validate_ohlcv(frame: pd.DataFrame, symbol: str) -> None:
    """Validate that downloaded data contains the expected OHLCV columns."""
    missing = [column for column in REQUIRED_OHLCV_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{symbol} data is missing required columns: {missing}")


@lru_cache(maxsize=256)
def _download_history(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """Cached wrapper around yfinance.download."""
    frame = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    cleaned = frame.dropna(how="all")
    if cleaned.empty:
        raise ValueError(f"No market data returned for {symbol}")
    return cleaned


@lru_cache(maxsize=256)
def _download_info(symbol: str) -> dict[str, Any]:
    """Cached wrapper around yfinance.Ticker.info."""
    info = yf.Ticker(symbol).info
    return dict(info or {})
