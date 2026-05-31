"""Reusable technical indicators for OHLCV data."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """Calculate a simple moving average."""
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    """Calculate an exponential moving average."""
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Calculate the Relative Strength Index."""
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Calculate MACD line, signal line, and histogram."""
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    return pd.DataFrame(
        {
            "macd": macd_line,
            "macd_signal": signal_line,
            "macd_histogram": macd_line - signal_line,
        }
    )


def bollinger_bands(close: pd.Series, window: int = 20, deviations: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Band mid, upper, and lower series."""
    middle = sma(close, window)
    standard_deviation = close.rolling(window=window, min_periods=window).std()
    return pd.DataFrame(
        {
            "bb_middle": middle,
            "bb_upper": middle + deviations * standard_deviation,
            "bb_lower": middle - deviations * standard_deviation,
        }
    )


def atr(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    high_low = frame["High"] - frame["Low"]
    high_close = (frame["High"] - frame["Close"].shift()).abs()
    low_close = (frame["Low"] - frame["Close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()


def adx(frame: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Calculate ADX, +DI, and -DI trend-strength indicators."""
    high_diff = frame["High"].diff()
    low_diff = -frame["Low"].diff()
    plus_dm = pd.Series(np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0.0), index=frame.index)
    minus_dm = pd.Series(np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0.0), index=frame.index)
    atr_value = atr(frame, window).replace(0, pd.NA)
    plus_di = 100 * plus_dm.ewm(alpha=1 / window, min_periods=window, adjust=False).mean() / atr_value
    minus_di = 100 * minus_dm.ewm(alpha=1 / window, min_periods=window, adjust=False).mean() / atr_value
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)
    return pd.DataFrame(
        {
            "adx_14": dx.ewm(alpha=1 / window, min_periods=window, adjust=False).mean(),
            "plus_di_14": plus_di,
            "minus_di_14": minus_di,
        }
    )


def obv(frame: pd.DataFrame) -> pd.Series:
    """Calculate On-Balance Volume."""
    direction = np.sign(frame["Close"].diff().fillna(0))
    return (direction * frame["Volume"].fillna(0)).cumsum()


def daily_returns(close: pd.Series) -> pd.Series:
    """Calculate simple percentage returns."""
    return close.pct_change().fillna(0)


def add_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    """Add the platform's default indicator columns to an OHLCV DataFrame."""
    enriched = frame.copy()
    enriched["sma_20"] = sma(enriched["Close"], 20)
    enriched["sma_50"] = sma(enriched["Close"], 50)
    enriched["sma_200"] = sma(enriched["Close"], 200)
    enriched["ema_20"] = ema(enriched["Close"], 20)
    enriched["ema_50"] = ema(enriched["Close"], 50)
    enriched["rsi_14"] = rsi(enriched["Close"], 14)
    enriched = enriched.join(macd(enriched["Close"]))
    enriched = enriched.join(bollinger_bands(enriched["Close"]))
    enriched["atr_14"] = atr(enriched, 14)
    enriched = enriched.join(adx(enriched, 14))
    enriched["obv"] = obv(enriched)
    enriched["daily_return"] = daily_returns(enriched["Close"])
    return enriched
