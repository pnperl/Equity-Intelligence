"""Typed settings loader for the Equity Intelligence platform."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class MarketSettings:
    """Market data defaults."""

    exchange_suffix: str = ".NS"
    default_period: str = "1y"
    default_interval: str = "1d"
    benchmark_symbol: str = "^NSEI"


@dataclass(frozen=True)
class ScoringSettings:
    """Composite scoring weights and thresholds."""

    technical_weight: float = 0.6
    risk_weight: float = 0.4
    bullish_rsi_threshold: float = 55
    bearish_rsi_threshold: float = 45
    max_atr_percent: float = 6


@dataclass(frozen=True)
class PortfolioSettings:
    """Portfolio risk settings."""

    max_position_weight: float = 0.20
    risk_per_trade: float = 0.01
    atr_stop_multiplier: float = 2.0


@dataclass(frozen=True)
class AppSettings:
    """Application settings grouped by domain."""

    market: MarketSettings = MarketSettings()
    scoring: ScoringSettings = ScoringSettings()
    portfolio: PortfolioSettings = PortfolioSettings()


def load_settings(path: str | Path = "config/settings.yaml") -> AppSettings:
    """Load settings from YAML, falling back to safe defaults for missing values."""
    settings_path = Path(path)
    if not settings_path.exists():
        return AppSettings()

    raw = yaml.safe_load(settings_path.read_text()) or {}
    return AppSettings(
        market=MarketSettings(**_section(raw, "market")),
        scoring=ScoringSettings(**_section(raw, "scoring")),
        portfolio=PortfolioSettings(**_section(raw, "portfolio")),
    )


def _section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    """Return a YAML section as a dictionary."""
    value = raw.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"Settings section {name!r} must be a mapping")
    return value
