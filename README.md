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
streamlit run dashboard/streamlit_app.py
```

## Development

Run tests before opening a pull request:

```bash
pytest
```
