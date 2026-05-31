"""Command-line entry point for Equity Intelligence analysis."""

from __future__ import annotations

import argparse
import logging

from data import MarketDataClient
from indicators import add_indicators
from reports import render_stock_report
from scoring import score_stock

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger(__name__)


def analyze_symbol(symbol: str, period: str = "1y") -> str:
    """Fetch, enrich, score, and render an HTML report for a symbol."""
    client = MarketDataClient()
    frame = add_indicators(client.history(symbol, period=period))
    score = score_stock(frame)
    return render_stock_report(symbol=symbol.upper(), score=score)


def main() -> None:
    """Parse CLI arguments and print an HTML report."""
    parser = argparse.ArgumentParser(description="Analyze an NSE equity symbol.")
    parser.add_argument("symbol", help="NSE symbol, for example RELIANCE or INFY")
    parser.add_argument("--period", default="1y", help="yfinance period, for example 6mo, 1y, or 5y")
    args = parser.parse_args()
    LOGGER.info("Analyzing %s", args.symbol)
    print(analyze_symbol(args.symbol, args.period))


if __name__ == "__main__":
    main()
