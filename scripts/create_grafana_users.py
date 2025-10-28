#!/usr/bin/env python3
"""
Provision Grafana users and teams from a JSON/YAML spec.
Usage:
  python create_grafana_users.py --spec path/to/spec.yaml
Environment:
  GRAFANA_URL              (default http://localhost:3000)
  GRAFANA_ADMIN_USER       (fallback when no token, default admin)
  GRAFANA_ADMIN_PASS       (fallback when no token, default admin)
  GRAFANA_TOKEN            (optional HTTP header bearer token)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List

import requests

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3000")
ADMIN_USER = os.environ.get("GRAFANA_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("GRAFANA_ADMIN_PASS", "admin")
GRAFANA_TOKEN = os.environ.get("GRAFANA_TOKEN")

TEAM_PERMISSION = {"Viewer": 1, "Editor": 2}
DEFAULT_SPEC = {
    "users": [
        {
            "login": "platform_lead",
            "name": "Platform Lead",
            "email": "platform.lead@example.com",
            "password": "ChangeMe!1",
        },
        {
            "login": "platform_member",
            "name": "Platform Member",
            "email": "platform.member@example.com",
            "password": "ChangeMe!1",
        },
        {
            "login": "consultant",
            "name": "Consultant",
            "email": "consultant@example.com",
            "password": "ChangeMe!1",
        },
    ],
    "teams": [
        {
            "name": "platform_engineering",
            "email": "",
            "members": [
                {"login": "platform_lead", "role": "Editor"},
                {"login": "platform_member", "role": "Viewer"},
            ],
        },
        {
            "name": "consultants",
            "email": "",
            "members": [{"login": "consultant", "role": "Viewer"}],
        },
    ],
}

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})
if GRAFANA_TOKEN:
    session.headers["Authorization"] = f"Bearer {GRAFANA_TOKEN}"
else:
    session.auth = (ADMIN_USER, ADMIN_PASS)


def api_request(method: str, path: str, expected: Iterable[int], **kwargs):
    url = f"{GRAFANA_URL.rstrip('/')}/api{path}"
    resp = session.request(method, url, timeout=15, **kwargs)
    if resp.status_code not in expected:
        print(f"{method} {path} -> {resp.status_code}: {resp.text}")
        return None
    if resp.content:
        try:
            return resp.json()
        except ValueError:
            return resp.text
    return None


def ensure_user(user: Dict) -> int | None:
    payload = {
        "name": user["name"],
        "login": user["login"],
        "email": user["email"],
        "password": user["password"],
    }
    created = api_request("POST", "/users", {200, 201}, json=payload)
    if created:
        uid = created.get("id")
        print(f"[user] created {user['login']} (id={uid})")
        return uid

    lookup = api_request(
        "GET", f"/users/lookup?loginOrEmail={user['login']}", {200}
    )
    if lookup:
        print(f"[user] exists {user['login']} (id={lookup.get('id')})")
        return lookup.get("id")
    return None


def ensure_team(team: Dict) -> int | None:
    payload = {"name": team["name"], "email": team.get("email", "")}
    created = api_request("POST", "/teams", {200, 201}, json=payload)
    if created:
        tid = created.get("teamId") or created.get("id")
        print(f"[team] created {team['name']} (id={tid})")
        return tid

    search = api_request(
        "GET", f"/teams/search?name={team['name']}", {200}
    )
    if search and search.get("totalCount"):
        tid = search["teams"][0]["id"]
        print(f"[team] exists {team['name']} (id={tid})")
        return tid
    return None


def list_team_members(team_id: int) -> Dict[int, Dict]:
    members = api_request("GET", f"/teams/{team_id}/members", {200}) or []
    return {item["userId"]: item for item in members}


def add_member(team_id: int, user_id: int, role: str) -> None:
    payload = {
        "userId": user_id,
        "permission": TEAM_PERMISSION.get(role, TEAM_PERMISSION["Viewer"]),
    }
    api_request("POST", f"/teams/{team_id}/members", {200, 201}, json=payload)
    print(f"[team] add user {user_id} -> team {team_id} as {role}")


def remove_member(team_id: int, user_id: int) -> None:
    api_request("DELETE", f"/teams/{team_id}/members/{user_id}", {200, 202, 204})
    print(f"[team] removed user {user_id} from team {team_id}")


def sync_team_members(team_id: int, member_specs: List[Dict], user_ids: Dict[str, int]):
    desired = {}
    for member in member_specs:
        login = member["login"]
        if login not in user_ids:
            print(f"[warn] user {login} missing, skipping membership")
            continue
        desired[user_ids[login]] = member.get("role", "Viewer")

    current = list_team_members(team_id)

    for user_id, role in desired.items():
        if user_id not in current:
            add_member(team_id, user_id, role)
        else:
            current_perm = current[user_id].get("permission")
            wanted_perm = TEAM_PERMISSION.get(role, TEAM_PERMISSION["Viewer"])
            if current_perm != wanted_perm:
                remove_member(team_id, user_id)
                add_member(team_id, user_id, role)

    for user_id in set(current) - set(desired):
        remove_member(team_id, user_id)


def load_spec(path: str | None) -> Dict:
    if not path:
        return DEFAULT_SPEC
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(spec_path)
    with spec_path.open("r", encoding="utf-8") as fh:
        text = fh.read()
    if spec_path.suffix.lower() in {".yaml", ".yml"}:
        if not yaml:
            raise RuntimeError("pyyaml not installed; pip install pyyaml")
        return yaml.safe_load(text)
    return json.loads(text)


def health_check() -> None:
    resp = session.get(f"{GRAFANA_URL.rstrip('/')}/api/health", timeout=10)
    if resp.status_code != 200:
        print("Grafana API health check failed:", resp.status_code, resp.text)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision Grafana identities.")
    parser.add_argument(
        "--spec",
        help="Path to JSON/YAML spec file (defaults to in-script sample).",
    )
    args = parser.parse_args()

    health_check()
    spec = load_spec(args.spec)

    user_ids: Dict[str, int] = {}
    for user in spec.get("users", []):
        uid = ensure_user(user)
        if uid is not None:
            user_ids[user["login"]] = uid
        time.sleep(0.3)

    for team in spec.get("teams", []):
        tid = ensure_team(team)
        if tid is None:
            print(f"[error] failed to ensure team {team['name']}")
            continue
        sync_team_members(tid, team.get("members", []), user_ids)
        time.sleep(0.3)


if __name__ == "__main__":
    main()
