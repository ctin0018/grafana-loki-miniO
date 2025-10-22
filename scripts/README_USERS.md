Provision Grafana users and teams

This folder contains a small script to create two users and teams in Grafana:
- platform_engineer
- consultant

Requirements:
- Python 3
- requests library (pip install requests)

Usage:

Set environment variables if you use non-default admin credentials or Grafana URL:

- GRAFANA_URL (default: http://localhost:3002)
- GRAFANA_ADMIN_USER (default: admin)
- GRAFANA_ADMIN_PASS (default: admin123)

Run:

python .\scripts\create_grafana_users.py

After running, two users will be created with passwords printed in the output. They will be added to teams with the same names.