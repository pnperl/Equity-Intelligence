"""HTML report rendering helpers."""

from __future__ import annotations

from html import escape

from scoring import ScoreBreakdown


def render_stock_report(symbol: str, score: ScoreBreakdown) -> str:
    """Render a compact HTML score report."""
    safe_symbol = escape(symbol.upper())
    fundamental = "N/A" if score.fundamental is None else f"{score.fundamental:.2f}"
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{safe_symbol} Equity Intelligence Report</title>
      </head>
      <body>
        <h1>{safe_symbol}</h1>
        <ul>
          <li>Technical Score: {score.technical:.2f}</li>
          <li>Risk Score: {score.risk:.2f}</li>
          <li>Fundamental Score: {fundamental}</li>
          <li>Overall Score: {score.overall:.2f}</li>
          <li>Rating: {escape(score.rating)}</li>
        </ul>
      </body>
    </html>
    """.strip()
