#!/usr/bin/env python3
"""
Create Grafana users and teams via Grafana HTTP API.
Usage: python create_grafana_users.py
Requires: requests (pip install requests)

This script will create two teams `platform_engineer` and `consultant`,
create two users with the same usernames, and add users to their teams.
"""
import os
import sys
import time
import requests

GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3002")
ADMIN_USER = os.environ.get("GRAFANA_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("GRAFANA_ADMIN_PASS", "admin123")

USERS = [
    {"login": "platform_engineer", "email": "platform@example.com", "name": "Platform Engineer", "password": "PlatformPass123"},
    {"login": "consultant", "email": "consultant@example.com", "name": "Consultant", "password": "ConsultantPass123"},
]

TEAMS = [
    {"name": "platform_engineer", "email": ""},
    {"name": "consultant", "email": ""},
]

session = requests.Session()
session.auth = (ADMIN_USER, ADMIN_PASS)
session.headers.update({"Content-Type": "application/json"})


def api_post(path, payload):
    url = f"{GRAFANA_URL}/api{path}"
    r = session.post(url, json=payload)
    if r.status_code not in (200, 201):
        print(f"POST {path} -> {r.status_code}: {r.text}")
    return r


def api_get(path):
    url = f"{GRAFANA_URL}/api{path}"
    r = session.get(url)
    if r.status_code != 200:
        print(f"GET {path} -> {r.status_code}: {r.text}")
    return r


def create_user(user):
    payload = {
        "name": user["name"],
        "login": user["login"],
        "email": user["email"],
        "password": user["password"],
    }
    r = api_post("/users", payload)
    if r.status_code in (200, 201):
        uid = r.json().get("id")
        print(f"Created user {user['login']} (id={uid})")
        return uid
    else:
        # Maybe the user exists, try to lookup
        r2 = api_get(f"/users/lookup?loginOrEmail={user['login']}")
        if r2.status_code == 200:
            print(f"User {user['login']} already exists")
            return r2.json().get('id')
    return None


def create_team(team):
    payload = {"name": team["name"], "email": team.get("email", "")}
    r = api_post("/teams", payload)
    if r.status_code in (200, 201):
        tid = r.json().get("teamId") or r.json().get("id")
        print(f"Created team {team['name']} (id={tid})")
        return tid
    else:
        # Try to find existing
        r2 = api_get(f"/teams/search?name={team['name']}")
        if r2.status_code == 200 and r2.json().get("totalCount", 0) > 0:
            teams = r2.json().get("teams", [])
            if teams:
                tid = teams[0].get("id")
                print(f"Team {team['name']} already exists (id={tid})")
                return tid
    return None


def add_user_to_team(user_id, team_id, role="Viewer"):
    # role can be Viewer or Editor
    path = f"/teams/{team_id}/members"
    payload = {"userId": user_id, "permission": role}
    r = api_post(path, payload)
    if r.status_code in (200, 201):
        print(f"Added user {user_id} to team {team_id} as {role}")
        return True
    else:
        print(f"Failed to add user {user_id} to team {team_id}: {r.status_code} {r.text}")
    return False


if __name__ == '__main__':
    # quick health check
    try:
        r = requests.get(f"{GRAFANA_URL}/api/health")
        if r.status_code != 200:
            print("Grafana API health check failed:", r.status_code, r.text)
            sys.exit(1)
    except Exception as e:
        print("Failed to reach Grafana API:", e)
        sys.exit(1)

    user_ids = {}
    for u in USERS:
        uid = create_user(u)
        if uid:
            user_ids[u['login']] = uid
        time.sleep(0.5)

    team_ids = {}
    for t in TEAMS:
        tid = create_team(t)
        if tid:
            team_ids[t['name']] = tid
        time.sleep(0.5)

    # Add users to teams
    for username, uid in user_ids.items():
        team_name = username
        tid = team_ids.get(team_name)
        if tid:
            add_user_to_team(uid, tid, role='Viewer')

    print("Done. Users created:")
    for u in USERS:
        print(f" - {u['login']} (password: {u['password']})")
