"""Entrypoints for Equity Intelligence analysis.

The module supports two execution modes:

- ``python app.py SYMBOL --period 1y`` for CLI HTML report generation.
- ``streamlit run app.py`` for live dashboard hosting when a deployment platform
  is configured to use ``app.py`` as the Streamlit entrypoint.
"""

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
    """Run the CLI report flow or the Streamlit dashboard when no symbol is supplied."""
    parser = argparse.ArgumentParser(description="Analyze an NSE equity symbol or run the Streamlit dashboard.")
    parser.add_argument("symbol", nargs="?", help="NSE symbol, for example RELIANCE or INFY")
    parser.add_argument("--period", default="1y", help="yfinance period, for example 6mo, 1y, or 5y")
    args = parser.parse_args()

    if args.symbol:
        LOGGER.info("Analyzing %s", args.symbol)
        print(analyze_symbol(args.symbol, args.period))
        return

    LOGGER.info("No CLI symbol supplied; starting Streamlit dashboard entrypoint")
    _run_streamlit_dashboard()


def _run_streamlit_dashboard() -> None:
    """Run the dashboard implementation for Streamlit deployments that target app.py."""
    from dashboard.streamlit_app import main as dashboard_main

    dashboard_main()


if __name__ == "__main__":
    main()
