# Equity Intelligence

A production-oriented Python platform for Indian equity analysis. The project converts notebook-based research into reusable modules for data access, technical indicators, scoring, relative rotation, portfolio sizing, backtesting, reporting, and a Streamlit dashboard.

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
├── rrg/
├── portfolio/
├── backtesting/
├── reports/
├── dashboard/
└── tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py RELIANCE --period 1y
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

## Development

Run tests before opening a pull request:

```bash
pytest
```
