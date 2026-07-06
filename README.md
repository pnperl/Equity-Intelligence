# Equity Intelligence

A production-oriented Python platform for Indian equity analysis. The project converts notebook-based research into reusable modules for data access, technical indicators, fundamental snapshots, composite scoring, relative rotation, portfolio sizing, backtesting, reporting, and a Streamlit dashboard.

## Project layout

```text
Equity-Intelligence/
├── app.py
├── requirements.txt
├── config/
│   └── settings.yaml
├── data/
├── indicators/
├── scoring/
├── fundamentals/
├── services/
├── rrg/
├── portfolio/
├── backtesting/
├── reports/
├── dashboard/
└── tests/
```

## Implemented capabilities

- Live NSE market data through `yfinance` with symbol normalization and validation.
- Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, OBV, and returns.
- Fundamental snapshot scoring from `yfinance` valuation, quality, leverage, and growth fields.
- Composite technical/risk/fundamental scoring with ratings.
- Watchlist scoring, RRG relative strength, risk-based position sizing, equal-weight allocation, ATR stops, and moving-average backtesting.
- CLI HTML reports and a multi-page Streamlit dashboard.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py RELIANCE --period 1y
python app.py INFY --period 2y --output reports/infy.html
```

## Dashboard

```bash
streamlit run streamlit_app.py
```

## Live Streamlit deployment

This project should be deployed as a live Streamlit app. GitHub Pages is not suitable for the dashboard because it only serves static files and cannot run Python, call `yfinance`, or execute the scoring engine.

Recommended Streamlit Community Cloud settings:

| Setting | Value |
| --- | --- |
| Branch | `main` |
| Main file path | `streamlit_app.py` preferred; `app.py` is also supported |
| Python version | `3.12` from Advanced settings |
| Dependencies | `requirements.txt` |

Deployment steps:

1. Push this repository to GitHub.
2. Open `https://share.streamlit.io/`.
3. Click **Create app** and connect the GitHub repository.
4. Select branch `main`.
5. Set **Main file path** to `streamlit_app.py`.
6. Select Python `3.12` in **Advanced settings**.
7. Click **Deploy** and wait for the `streamlit.app` URL.

If your host is already configured to run `app.py`, you can keep that setting; `app.py` now falls back to the Streamlit dashboard when no CLI symbol is supplied.

See `STREAMLIT_DEPLOYMENT.md` for the full live deployment checklist.

## Run from Android mobile

The dashboard is mobile-friendly, so there are two ways to use it from an Android device.

### Option 1: Use the deployed app in a browser (recommended)

1. Deploy the app to Streamlit Community Cloud using the steps above.
2. Open the resulting `streamlit.app` URL in Chrome (or any mobile browser) on your Android device.
3. Optionally tap the browser menu and choose **Add to Home screen** to launch it like a native app.

This requires no local setup and is the easiest way to run analysis on mobile.

### Option 2: Run locally on-device with Termux

You can run the full platform directly on Android using [Termux](https://f-droid.org/packages/com.termux/):

```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/<USER>/Equity-Intelligence.git
cd Equity-Intelligence
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501` in the Android browser. Replace `<USER>` with your GitHub username/org.

> Note: on-device installs of `numpy`/`pandas` can require compilation and may be slow or fail on some Android setups. Option 1 avoids this entirely.

## Development

Run tests before opening a pull request:

```bash
pytest
```
