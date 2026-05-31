"""Mobile-friendly Streamlit dashboard for Equity Intelligence."""

from __future__ import annotations

import logging

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backtesting import moving_average_crossover
from data import MarketDataClient
from indicators import add_indicators
from portfolio import PositionSizingInput, atr_stop_loss, equal_weight_allocation, position_size
from rrg import relative_strength
from scoring import score_stock
from services import analyze_watchlist

LOGGER = logging.getLogger(__name__)

DEFAULT_WATCHLIST = "RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK"


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Equity Intelligence", page_icon="📈", layout="wide")
    st.title("Equity Intelligence Platform")
    st.caption("Live Indian equity analysis with indicators, scoring, backtesting, RRG, and portfolio risk.")

    page = st.sidebar.radio("Page", ["Stock Analysis", "Watchlist", "Backtesting", "RRG", "Portfolio"], index=0)
    if page == "Stock Analysis":
        _stock_analysis_page()
    elif page == "Watchlist":
        _watchlist_page()
    elif page == "Backtesting":
        _backtesting_page()
    elif page == "RRG":
        _rrg_page()
    else:
        _portfolio_page()


def _stock_analysis_page() -> None:
    symbol = st.sidebar.text_input("NSE Symbol", value="RELIANCE", help="Use NSE symbols such as RELIANCE, INFY, TCS, or HDFCBANK.")
    period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1, key="stock_period")
    if st.sidebar.button("Analyze", type="primary") or "latest_symbol" not in st.session_state:
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

    latest = frame.iloc[-1]
    metric_columns = st.columns(5)
    metric_columns[0].metric("Close", f"{latest['Close']:.2f}")
    metric_columns[1].metric("Technical", score.technical)
    metric_columns[2].metric("Risk", score.risk)
    metric_columns[3].metric("Overall", score.overall)
    metric_columns[4].metric("Rating", score.rating)

    st.plotly_chart(_price_figure(frame), use_container_width=True)

    st.subheader("Latest indicator data")
    st.dataframe(frame.tail(20), use_container_width=True)


def _watchlist_page() -> None:
    st.subheader("Watchlist scoring")
    symbols_text = st.text_area("Comma-separated NSE symbols", value=DEFAULT_WATCHLIST)
    period = st.selectbox("Period", ["6mo", "1y", "2y"], index=1, key="watchlist_period")
    symbols = _parse_symbols(symbols_text)
    if st.button("Score watchlist", type="primary"):
        try:
            summary = analyze_watchlist(symbols, period=period)
        except Exception as exc:  # pragma: no cover - Streamlit UI guardrail
            LOGGER.exception("Unable to analyze watchlist")
            st.error("Unable to analyze watchlist.")
            st.caption(f"Technical detail: {exc}")
            return
        st.dataframe(summary, use_container_width=True, hide_index=True)


def _backtesting_page() -> None:
    st.subheader("Moving-average crossover backtest")
    symbol = st.text_input("NSE Symbol", value="RELIANCE", key="backtest_symbol")
    period = st.selectbox("Period", ["1y", "2y", "5y"], index=1, key="backtest_period")
    if st.button("Run backtest", type="primary"):
        try:
            frame = _load_enriched_history(symbol, period)
            result = moving_average_crossover(frame)
        except Exception as exc:  # pragma: no cover - Streamlit UI guardrail
            LOGGER.exception("Unable to backtest %s", symbol)
            st.error("Unable to run backtest.")
            st.caption(f"Technical detail: {exc}")
            return
        columns = st.columns(5)
        columns[0].metric("Total return", f"{result.total_return:.2%}")
        columns[1].metric("Annualized", f"{result.annualized_return:.2%}")
        columns[2].metric("Max drawdown", f"{result.max_drawdown:.2%}")
        columns[3].metric("Sharpe", result.sharpe)
        columns[4].metric("Trades", result.trades)
        st.line_chart(result.equity_curve)


def _rrg_page() -> None:
    st.subheader("Relative Rotation Graph data")
    symbol = st.text_input("NSE Symbol", value="RELIANCE", key="rrg_symbol")
    benchmark = st.text_input("Benchmark", value="^NSEI")
    if st.button("Calculate RRG", type="primary"):
        try:
            asset = _load_enriched_history(symbol, "1y")
            bench = _load_history(benchmark, "1y")
            rrg_frame = relative_strength(asset["Close"], bench["Close"])
        except Exception as exc:  # pragma: no cover - Streamlit UI guardrail
            LOGGER.exception("Unable to calculate RRG")
            st.error("Unable to calculate RRG.")
            st.caption(f"Technical detail: {exc}")
            return
        st.scatter_chart(rrg_frame.dropna(), x="rs_ratio", y="rs_momentum")
        st.dataframe(rrg_frame.tail(20), use_container_width=True)


def _portfolio_page() -> None:
    st.subheader("Portfolio allocation and risk")
    capital = st.number_input("Capital", min_value=1_000.0, value=100_000.0, step=5_000.0)
    symbols = _parse_symbols(st.text_area("Comma-separated symbols", value=DEFAULT_WATCHLIST, key="portfolio_symbols"))
    st.dataframe(equal_weight_allocation(symbols, capital), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Position sizing")
    entry = st.number_input("Entry price", min_value=1.0, value=1000.0)
    atr_value = st.number_input("ATR", min_value=0.0, value=25.0)
    risk = st.slider("Risk per trade", min_value=0.0025, max_value=0.05, value=0.01, step=0.0025)
    stop = atr_stop_loss(entry, atr_value)
    quantity = position_size(PositionSizingInput(capital=capital, entry_price=entry, stop_loss=stop, risk_per_trade=risk))
    st.metric("ATR stop loss", stop)
    st.metric("Suggested quantity", quantity)


@st.cache_data(ttl=900, show_spinner=False)
def _load_enriched_history(symbol: str, period: str) -> pd.DataFrame:
    """Fetch and cache enriched market history for Streamlit sessions."""
    client = MarketDataClient()
    return add_indicators(client.history(symbol, period=period))


@st.cache_data(ttl=900, show_spinner=False)
def _load_history(symbol: str, period: str) -> pd.DataFrame:
    """Fetch and cache raw market history for Streamlit sessions."""
    return MarketDataClient().history(symbol, period=period)


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


def _parse_symbols(symbols_text: str) -> list[str]:
    """Parse comma-separated symbols from dashboard input."""
    return [symbol.strip().upper() for symbol in symbols_text.split(",") if symbol.strip()]


if __name__ == "__main__":
    main()
