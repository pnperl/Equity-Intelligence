"""Entrypoints for Equity Intelligence analysis.

The module supports two execution modes:

- ``python app.py SYMBOL --period 1y`` for CLI HTML report generation.
- ``streamlit run app.py`` for live dashboard hosting when a deployment platform
  is configured to use ``app.py`` as the Streamlit entrypoint.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from reports import render_stock_report
from services import analyze_stock

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger(__name__)


def analyze_symbol(symbol: str, period: str = "1y") -> str:
    """Fetch, enrich, score, and render an HTML report for a symbol."""
    analysis = analyze_stock(symbol, period=period)
    return render_stock_report(symbol=analysis.symbol, score=analysis.score)


def main() -> None:
    """Run the CLI report flow or the Streamlit dashboard when no symbol is supplied."""
    parser = argparse.ArgumentParser(description="Analyze an NSE equity symbol or run the Streamlit dashboard.")
    parser.add_argument("symbol", nargs="?", help="NSE symbol, for example RELIANCE or INFY")
    parser.add_argument("--period", default="1y", help="yfinance period, for example 6mo, 1y, or 5y")
    parser.add_argument("--output", help="Optional path to write the generated HTML report")
    args = parser.parse_args()

    if args.symbol:
        LOGGER.info("Analyzing %s", args.symbol)
        html = analyze_symbol(args.symbol, args.period)
        if args.output:
            Path(args.output).write_text(html, encoding="utf-8")
            LOGGER.info("Wrote report to %s", args.output)
        else:
            print(html)
        return

    LOGGER.info("No CLI symbol supplied; starting Streamlit dashboard entrypoint")
    _run_streamlit_dashboard()


def _run_streamlit_dashboard() -> None:
    """Run the dashboard implementation for Streamlit deployments that target app.py."""
    from dashboard.streamlit_app import main as dashboard_main

    dashboard_main()


if __name__ == "__main__":
    main()
