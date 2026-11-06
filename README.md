# Carepoint

Carepoint is a dark-blue-and-beige hospital management dashboard built around the existing patient, doctor, appointment, medical-record, billing, analytics, and CSV-export modules.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit opens the dashboard in your browser. The app starts with three sample doctors; patient and practice data is held in the current app session and is not stored between restarts. Use **Billing & reports → Export data** to download a ZIP containing the patients, doctors, appointments, and bills as CSV files.
