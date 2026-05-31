# Live Streamlit deployment

This project is designed to be deployed as a live Streamlit app, not as a GitHub Pages site. GitHub Pages only serves static files and cannot run the Python dashboard, call `yfinance`, or execute the scoring engine.

## Recommended host

Use Streamlit Community Cloud for the first live deployment.

## Deployment settings

Use these settings when creating the app:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/<USER>/Equity-Intelligence` |
| Branch | `main` |
| Main file path | `streamlit_app.py` preferred; `app.py` is also supported |
| Python version | `3.12` from Advanced settings |
| Dependencies | `requirements.txt` |

## Steps

1. Push the repository to GitHub.
2. Open `https://share.streamlit.io/` and sign in with GitHub.
3. Click **Create app**.
4. Choose **Yup, I have an app**.
5. Select this repository and the `main` branch.
6. Set **Main file path** to `streamlit_app.py`. If your deployment already points at `app.py`, that is now safe too because `app.py` opens the dashboard when no CLI symbol is supplied.
7. Open **Advanced settings** and select Python `3.12`.
8. Click **Deploy**.
9. Wait for the build logs to finish. The app will open on a `streamlit.app` URL.

## Why `streamlit_app.py` is at the repository root

Streamlit Community Cloud runs apps from the repository root and installs dependencies from `requirements.txt`. A root `streamlit_app.py` entrypoint is the least ambiguous configuration and imports the real dashboard implementation from `dashboard/streamlit_app.py`.

`app.py` remains available for CLI usage with `python app.py RELIANCE --period 1y`, but it also supports Streamlit deployments by launching the dashboard when no symbol argument is present. This prevents the repeated `app.py: error: the following arguments are required: symbol` failure if a live host points Streamlit at `app.py`.

## Troubleshooting checklist

- If imports fail, confirm the app path is exactly `streamlit_app.py`.
- If package installation fails, open the Streamlit build logs and verify every imported third-party package is listed in `requirements.txt`.
- If Python compatibility issues appear, delete and redeploy the app with Python `3.12` selected in Advanced settings.
- If market data does not load, retry with a liquid NSE symbol such as `RELIANCE`, `INFY`, or `TCS`; live data depends on Yahoo Finance availability.
- Do not add `.streamlit/secrets.toml` to git. Use the Streamlit Cloud secrets UI for private values.
