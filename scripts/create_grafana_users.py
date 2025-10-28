#!/usr/bin/env python3
"""
Bootstrap Grafana users and teams via the Grafana HTTP API.
This script creates teams and users based on configuration.
"""

import os
import sys
import requests
import json
from typing import Dict, List, Optional

# Configuration from environment variables
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_ADMIN_USER = os.getenv("GRAFANA_ADMIN_USER", "admin")
GRAFANA_ADMIN_PASS = os.getenv("GRAFANA_ADMIN_PASS", "admin")

# Team and user configuration
# In a real scenario, you might load this from a YAML/JSON file
TEAMS_CONFIG = [
    {"name": "Platform Team", "email": "platform@example.com"},
    {"name": "Security Team", "email": "security@example.com"},
    {"name": "DevOps Team", "email": "devops@example.com"},
]

USERS_CONFIG = [
    {
        "email": "john.doe@example.com",
        "name": "John Doe",
        "login": "john.doe",
        "password": "changeme123",
        "teams": ["Platform Team"],
    },
    {
        "email": "jane.smith@example.com",
        "name": "Jane Smith",
        "login": "jane.smith",
        "password": "changeme123",
        "teams": ["Security Team"],
    },
    {
        "email": "bob.jones@example.com",
        "name": "Bob Jones",
        "login": "bob.jones",
        "password": "changeme123",
        "teams": ["DevOps Team", "Platform Team"],
    },
]


class GrafanaClient:
    """Simple Grafana API client for bootstrapping."""

    def __init__(self, url: str, username: str, password: str):
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({"Content-Type": "application/json"})

    def create_team(self, name: str, email: str = "") -> Optional[int]:
        """Create a team. Returns team ID if successful or already exists."""
        # Check if team already exists
        resp = self.session.get(f"{self.url}/api/teams/search?name={name}")
        if resp.status_code == 200:
            teams = resp.json().get("teams", [])
            for team in teams:
                if team["name"] == name:
                    print(f"✓ Team '{name}' already exists (ID: {team['id']})")
                    return team["id"]

        # Create new team
        payload = {"name": name, "email": email}
        resp = self.session.post(f"{self.url}/api/teams", json=payload)
        if resp.status_code == 200:
            team_id = resp.json().get("teamId")
            print(f"✓ Created team '{name}' (ID: {team_id})")
            return team_id
        else:
            print(f"✗ Failed to create team '{name}': {resp.status_code} {resp.text}")
            return None

    def create_user(
        self, email: str, name: str, login: str, password: str
    ) -> Optional[int]:
        """Create a user. Returns user ID if successful or already exists."""
        # Check if user already exists
        resp = self.session.get(f"{self.url}/api/users/lookup?loginOrEmail={login}")
        if resp.status_code == 200:
            user_id = resp.json().get("id")
            print(f"✓ User '{login}' already exists (ID: {user_id})")
            return user_id

        # Create new user
        payload = {
            "email": email,
            "name": name,
            "login": login,
            "password": password,
        }
        resp = self.session.post(f"{self.url}/api/admin/users", json=payload)
        if resp.status_code == 200:
            user_id = resp.json().get("id")
            print(f"✓ Created user '{login}' (ID: {user_id})")
            return user_id
        else:
            print(f"✗ Failed to create user '{login}': {resp.status_code} {resp.text}")
            return None

    def add_user_to_team(self, user_id: int, team_id: int, team_name: str, user_login: str):
        """Add a user to a team."""
        payload = {"userId": user_id}
        resp = self.session.post(f"{self.url}/api/teams/{team_id}/members", json=payload)
        if resp.status_code == 200:
            print(f"✓ Added user '{user_login}' to team '{team_name}'")
        elif resp.status_code == 409:
            print(f"✓ User '{user_login}' already in team '{team_name}'")
        else:
            print(
                f"✗ Failed to add user '{user_login}' to team '{team_name}': {resp.status_code} {resp.text}"
            )

    def get_team_id_by_name(self, name: str) -> Optional[int]:
        """Get team ID by name."""
        resp = self.session.get(f"{self.url}/api/teams/search?name={name}")
        if resp.status_code == 200:
            teams = resp.json().get("teams", [])
            for team in teams:
                if team["name"] == name:
                    return team["id"]
        return None


def main():
    """Main entry point for bootstrapping Grafana."""
    print("=" * 60)
    print("Grafana Bootstrap Script")
    print("=" * 60)
    print(f"Grafana URL: {GRAFANA_URL}")
    print(f"Admin User: {GRAFANA_ADMIN_USER}")
    print()

    client = GrafanaClient(GRAFANA_URL, GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASS)

    # Test connection
    try:
        resp = client.session.get(f"{client.url}/api/org")
        if resp.status_code != 200:
            print(f"✗ Failed to connect to Grafana: {resp.status_code}")
            sys.exit(1)
        print(f"✓ Connected to Grafana: {resp.json().get('name', 'Unknown Org')}")
        print()
    except Exception as e:
        print(f"✗ Failed to connect to Grafana: {e}")
        sys.exit(1)

    # Create teams
    print("Creating teams...")
    team_ids = {}
    for team_config in TEAMS_CONFIG:
        team_id = client.create_team(team_config["name"], team_config.get("email", ""))
        if team_id:
            team_ids[team_config["name"]] = team_id
    print()

    # Create users and assign to teams
    print("Creating users...")
    for user_config in USERS_CONFIG:
        user_id = client.create_user(
            user_config["email"],
            user_config["name"],
            user_config["login"],
            user_config["password"],
        )
        if user_id and "teams" in user_config:
            for team_name in user_config["teams"]:
                team_id = team_ids.get(team_name)
                if not team_id:
                    team_id = client.get_team_id_by_name(team_name)
                if team_id:
                    client.add_user_to_team(user_id, team_id, team_name, user_config["login"])
                else:
                    print(f"✗ Team '{team_name}' not found for user '{user_config['login']}'")
    print()

    print("=" * 60)
    print("Bootstrap complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
