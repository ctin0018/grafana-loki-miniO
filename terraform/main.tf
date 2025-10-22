# Create Grafana users
resource "null_resource" "grafana_users" {
  for_each = { for user in var.users : user.login => user }

  triggers = {
    user_hash = sha256(jsonencode(each.value))
  }

  provisioner "local-exec" {
    command = <<-EOT
      python3 -c "
        import sys, os, json, requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        url = '${var.grafana_url}'
        admin_user = '${var.grafana_admin_user}'
        admin_pass = '''${var.grafana_admin_password}'''
        user_data = json.loads('''${jsonencode(each.value)}''')

        # Create session with retries
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Check if user exists
        lookup_resp = session.get(
            f'{url}/api/users/lookup',
            params={'loginOrEmail': user_data['login']},
            auth=(admin_user, admin_pass)
        )

        if lookup_resp.status_code == 404:
            # User doesn't exist, create it
            create_resp = session.post(
                f'{url}/api/admin/users',
                auth=(admin_user, admin_pass),
                json={
                    'name': user_data['name'],
                    'login': user_data['login'],
                    'email': user_data['email'],
                    'password': user_data['password']
                }
            )
            if create_resp.status_code in [200, 201]:
                print(f'Created user: {user_data[\"login\"]}')
            else:
                print(f'Failed to create user: {create_resp.status_code} - {create_resp.text}')
                sys.exit(1)
        else:
            print(f'User already exists: {user_data[\"login\"]}')
    "
    EOT

    interpreter = ["python3", "-c"]

    environment = {
      PYTHONIOENCODING = "utf-8"
    }
  }
}

# Create Grafana teams
resource "null_resource" "grafana_teams" {
  for_each = var.teams

  depends_on = [null_resource.grafana_users]

  triggers = {
    team_hash = sha256(jsonencode(each.value))
  }

  provisioner "local-exec" {
    command = <<-EOT
      python3 -c "
import sys, os, json, requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

url = '${var.grafana_url}'
admin_user = '${var.grafana_admin_user}'
admin_pass = '''${var.grafana_admin_password}'''
team_name = '${each.key}'
members = json.loads('''${jsonencode(each.value.members)}''')

# Create session
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
session.auth = (admin_user, admin_pass)

# Check if team exists
search_resp = session.get(f'{url}/api/teams/search', params={'name': team_name})
teams = search_resp.json().get('teams', [])
team_exists = any(t['name'] == team_name for t in teams)

if not team_exists:
    # Create team
    create_resp = session.post(f'{url}/api/teams', json={'name': team_name})
    if create_resp.status_code not in [200, 201]:
        print(f'Failed to create team: {create_resp.status_code} - {create_resp.text}')
        sys.exit(1)
    print(f'Created team: {team_name}')

# Get team ID
search_resp = session.get(f'{url}/api/teams/search', params={'name': team_name})
teams = search_resp.json().get('teams', [])
team_id = next((t['id'] for t in teams if t['name'] == team_name), None)

if not team_id:
    print(f'Could not find team ID for {team_name}')
    sys.exit(1)

# Add members to team
for member_login in members:
    # Get user ID
    user_resp = session.get(f'{url}/api/users/lookup', params={'loginOrEmail': member_login})
    if user_resp.status_code != 200:
        print(f'User not found: {member_login}')
        continue
    
    user_id = user_resp.json()['id']
    
    # Add to team
    add_resp = session.post(f'{url}/api/teams/{team_id}/members', json={'userId': user_id})
    if add_resp.status_code in [200, 201, 409]:  # 409 means already member
        print(f'Added {member_login} to team {team_name}')
    else:
        print(f'Failed to add member: {add_resp.status_code} - {add_resp.text}')
"
    EOT

    interpreter = ["python3", "-c"]

    environment = {
      PYTHONIOENCODING = "utf-8"
    }
  }
}