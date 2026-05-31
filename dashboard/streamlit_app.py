"""Mobile-friendly Streamlit dashboard for Equity Intelligence."""

from __future__ import annotations

import logging

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import MarketDataClient
from indicators import add_indicators
from scoring import score_stock

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Equity Intelligence", page_icon="📈", layout="wide")
    st.title("Equity Intelligence Platform")
    st.caption("Live Indian equity analysis with indicators, scoring, and risk context.")

    symbol = st.sidebar.text_input("NSE Symbol", value="RELIANCE", help="Use NSE symbols such as RELIANCE, INFY, TCS, or HDFCBANK.")
    period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
    analyze = st.sidebar.button("Analyze", type="primary")

    if analyze or "latest_symbol" not in st.session_state:
        st.session_state.latest_symbol = symbol
        st.session_state.latest_period = period

    _render_analysis(st.session_state.latest_symbol, st.session_state.latest_period)


def _render_analysis(symbol: str, period: str) -> None:
    """Render the analysis panel and handle live-data failures gracefully."""
    try:
        with st.spinner(f"Fetching {symbol}..."):
            frame = _load_enriched_history(symbol, period)
            score = score_stock(frame)
    except Exception as exc:  # pragma: no cover - Streamlit UI guardrail
        LOGGER.exception("Unable to analyze %s", symbol)
        st.error(f"Unable to analyze {symbol}. Check the symbol and try again.")
        st.caption(f"Technical detail: {exc}")
        return

    metric_columns = st.columns(4)
    metric_columns[0].metric("Technical", score.technical)
    metric_columns[1].metric("Risk", score.risk)
    metric_columns[2].metric("Overall", score.overall)
    metric_columns[3].metric("Rating", score.rating)

    st.plotly_chart(_price_figure(frame), use_container_width=True)

    st.subheader("Latest indicator data")
    st.dataframe(frame.tail(20), use_container_width=True)


@st.cache_data(ttl=900, show_spinner=False)
def _load_enriched_history(symbol: str, period: str) -> pd.DataFrame:
    """Fetch and cache enriched market history for Streamlit sessions."""
    client = MarketDataClient()
    return add_indicators(client.history(symbol, period=period))


def _price_figure(frame: pd.DataFrame) -> go.Figure:
    """Build the dashboard price chart."""
    figure = go.Figure()
    figure.add_trace(
        go.Candlestick(
            x=frame.index,
            open=frame["Open"],
            high=frame["High"],
            low=frame["Low"],
            close=frame["Close"],
            name="Price",
        )
    )
    figure.add_trace(go.Scatter(x=frame.index, y=frame["sma_20"], name="SMA 20"))
    figure.add_trace(go.Scatter(x=frame.index, y=frame["sma_50"], name="SMA 50"))
    figure.update_layout(height=600, xaxis_rangeslider_visible=False)
    return figure


if __name__ == "__main__":
    main()
