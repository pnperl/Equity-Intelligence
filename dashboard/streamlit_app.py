"""Mobile-friendly Streamlit dashboard for Equity Intelligence."""

from __future__ import annotations

import logging

import plotly.graph_objects as go
import streamlit as st

from data import MarketDataClient
from indicators import add_indicators
from scoring import score_stock

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Equity Intelligence", layout="wide")
    st.title("Equity Intelligence Platform")
    st.caption("Indian equity analysis with indicators, scoring, and risk context.")

    symbol = st.sidebar.text_input("NSE Symbol", value="RELIANCE")
    period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)

    if st.sidebar.button("Analyze", type="primary"):
        _render_analysis(symbol, period)


def _render_analysis(symbol: str, period: str) -> None:
    client = MarketDataClient()
    with st.spinner(f"Fetching {symbol}..."):
        frame = add_indicators(client.history(symbol, period=period))
        score = score_stock(frame)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Technical", score.technical)
    metric_columns[1].metric("Risk", score.risk)
    metric_columns[2].metric("Overall", score.overall)
    metric_columns[3].metric("Rating", score.rating)

    figure = go.Figure()
    figure.add_trace(go.Candlestick(x=frame.index, open=frame["Open"], high=frame["High"], low=frame["Low"], close=frame["Close"], name="Price"))
    figure.add_trace(go.Scatter(x=frame.index, y=frame["sma_20"], name="SMA 20"))
    figure.add_trace(go.Scatter(x=frame.index, y=frame["sma_50"], name="SMA 50"))
    figure.update_layout(height=600, xaxis_rangeslider_visible=False)
    st.plotly_chart(figure, use_container_width=True)

    st.subheader("Latest indicator data")
    st.dataframe(frame.tail(20), use_container_width=True)


if __name__ == "__main__":
    main()
