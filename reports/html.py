"""HTML report rendering helpers."""

from __future__ import annotations

from scoring import ScoreBreakdown


def render_stock_report(symbol: str, score: ScoreBreakdown) -> str:
    """Render a compact HTML score report."""
    return f"""
    <html>
      <head><title>{symbol} Equity Intelligence Report</title></head>
      <body>
        <h1>{symbol}</h1>
        <ul>
          <li>Technical Score: {score.technical}</li>
          <li>Risk Score: {score.risk}</li>
          <li>Overall Score: {score.overall}</li>
          <li>Rating: {score.rating}</li>
        </ul>
      </body>
    </html>
    """.strip()
