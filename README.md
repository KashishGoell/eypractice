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

## Deploy to an Azure Linux VM with Nginx

This project is a Streamlit application, not a static website. Copying it into `/var/www/html` does not start the app; Nginx must reverse-proxy requests to the running Streamlit service.

The following steps assume the repository is cloned at `/home/azureuser/eypractice`, the VM user is `azureuser`, and Nginx is already installed. Run them in the VM shell:

```bash
cd /home/azureuser/eypractice
git pull origin main
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
sudo chown -R azureuser:azureuser /home/azureuser/eypractice
sudo cp deploy/eypractice.service /etc/systemd/system/eypractice.service
sudo systemctl daemon-reload
sudo systemctl enable --now eypractice
```

Back up the existing default Nginx site configuration and point Nginx at Streamlit:

```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.carepoint-backup
sudo cp /home/azureuser/eypractice/deploy/nginx.conf /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl reload nginx
```

If `nginx -t` reports another `default_server`, inspect `/etc/nginx/sites-enabled/` and disable the conflicting default site before reloading. Allow inbound TCP port 80 in the VM's Azure Network Security Group. Then open the VM's public IP; Nginx proxies it to Streamlit on localhost port 8501. Check `sudo systemctl status eypractice` and `sudo journalctl -u eypractice -n 100 --no-pager` if the app does not start.

If you deployed the old static website to `/var/www/html`, that directory is no longer used by this proxy configuration. The previous Nginx configuration is backed up as `default.carepoint-backup` so you can restore it if needed.

This dashboard is a demonstration, not a production medical-record system. It has no authentication or durable database, and its session data is lost when the app restarts. Do not enter real patient information. A real deployment needs access controls, secure persistent storage, backups, and appropriate privacy and regulatory safeguards.
