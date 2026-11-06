# Carepoint

Carepoint is a dark-blue-and-beige hospital management dashboard built around the existing patient, doctor, appointment, medical-record, billing, analytics, and CSV-export modules.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit opens the dashboard in your browser. The app starts with three sample doctors; patient and practice data is held in the current app session and is not stored between restarts. Use **Billing & reports → Export data** to download a ZIP containing the patients, doctors, appointments, and bills as CSV files.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), select **Create app** and connect this repository.
3. Choose the `main` branch and `app.py` as the app's main file.
4. Deploy. Cloud installs the packages from `requirements.txt` and picks up the theme from `.streamlit/config.toml`.

This dashboard is a demonstration, not a production medical-record system. It has no authentication or durable database, and its session data is lost when the app restarts. Do not enter real patient information. A real deployment needs access controls, secure persistent storage, backups, and appropriate privacy and regulatory safeguards.
