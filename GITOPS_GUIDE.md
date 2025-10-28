# GitOps Workflows - Quick Reference

## 🚀 What's Been Added

This repository now includes GitOps-style workflows to help manage Grafana users and Cerbos authorization policies without needing to learn Terraform immediately.

### Files Created

#### GitHub Actions Workflows
- `.github/workflows/bootstrap-grafana.yml` - Provisions Grafana teams and users
- `.github/workflows/deploy-cerbos-policies.yml` - Deploys Cerbos policies to remote server

#### Python Scripts
- `scripts/create_grafana_users.py` - Creates teams and users in Grafana via API

#### Cerbos Policies (Examples)
- `cerbos/policies/derived_roles.yaml` - Common role definitions (admin, team_member, team_lead, resource_owner)
- `cerbos/policies/common_variables.yaml` - Shared variables (business hours, weekend checks)
- `cerbos/policies/dashboard_policy.yaml` - Dashboard access control policies
- `cerbos/policies/alert_policy.yaml` - Alert management authorization policies

#### Configuration Examples
- `cerbos/docker-compose.example.yml` - Example Docker Compose for Cerbos
- `cerbos/config.example.yaml` - Example Cerbos server configuration

#### Documentation
- `README.md` - Complete documentation with architecture, usage, and next steps

---

## 🔐 Required GitHub Secrets

### For Bootstrap Grafana Workflow
```
GRAFANA_URL          # Example: https://grafana.example.com
GRAFANA_ADMIN_USER   # Default: admin
GRAFANA_ADMIN_PASS   # Your Grafana admin password
```

### For Deploy Cerbos Policies Workflow
```
SSH_HOST                      # IP or hostname of remote server
SSH_USER                      # SSH username
SSH_PRIVATE_KEY               # Private SSH key in PEM format
CERBOS_REMOTE_POLICIES_PATH   # Example: /opt/cerbos/policies
CERBOS_REMOTE_BASE_PATH       # Example: /opt/cerbos (contains docker-compose.yml)
SSH_PORT                      # Optional, defaults to 22
```

---

## 📋 How to Use

### Bootstrap Grafana Users

1. **Configure secrets** in GitHub repository settings (Settings → Secrets and variables → Actions)
2. **Edit user/team config** in `scripts/create_grafana_users.py`
3. **Trigger the workflow**:
   - Manually from Actions tab → "Bootstrap Grafana Users" → Run workflow
   - Or push changes to `main` or `chris` branch

### Deploy Cerbos Policies

1. **Set up Cerbos** on your remote server using `cerbos/docker-compose.example.yml`
2. **Configure secrets** in GitHub repository settings
3. **Edit policies** in `cerbos/policies/` directory
4. **Trigger the workflow**:
   - Manually from Actions tab → "Deploy Cerbos Policies" → Run workflow
   - Or push policy changes to `main` or `chris` branch

---

## 🎯 Example Use Cases

### Adding a New User
1. Edit `scripts/create_grafana_users.py`
2. Add user to `USERS_CONFIG` list
3. Commit and push to trigger workflow
4. User is automatically created in Grafana

### Updating Policies
1. Edit a policy file in `cerbos/policies/`
2. Commit and push changes
3. Policies are automatically deployed to server
4. Cerbos container restarts with new policies

### Code Review Workflow
1. Developer creates branch
2. Adds new policy for feature
3. Opens PR
4. Team reviews policy changes
5. After merge, policies auto-deploy

---

## 🛠️ Next Steps (Recommended)

### 1. OIDC Authentication (Recommended for production)
- Set up Keycloak, Auth0, Okta, or Azure AD
- Configure Grafana to use OIDC
- Centralized user management with SSO

### 2. Terraform Migration (Recommended for scale)
- Use Grafana Terraform Provider
- Declarative infrastructure as code
- Automated drift detection

### 3. Policy Testing (Recommended for safety)
- Add Cerbos policy test suite
- Run tests in GitHub Actions before deploy
- Prevent broken policies from being deployed

### 4. Containerized Bootstrap (Optional)
- Dockerize the Python script
- Run as one-shot service
- No local Python dependency

---

## 🧪 Testing Locally

### Test Grafana Bootstrap Script
```bash
# Set environment variables
export GRAFANA_URL=http://localhost:3002
export GRAFANA_ADMIN_USER=admin
export GRAFANA_ADMIN_PASS=admin123

# Install dependencies
pip install requests

# Run script
python scripts/create_grafana_users.py
```

### Validate Cerbos Policies
```bash
# Install Cerbos CLI
curl -L https://github.com/cerbos/cerbos/releases/latest/download/cerbos_Linux_x86_64.tar.gz | tar xz
sudo mv cerbos /usr/local/bin/

# Compile policies
cerbos compile cerbos/policies
```

---

## 🔍 Troubleshooting

### Grafana workflow fails
- ✅ Check if GRAFANA_URL is accessible from GitHub runners
- ✅ Verify admin credentials in secrets
- ✅ Ensure Grafana API is enabled

### Cerbos deployment fails
- ✅ Test SSH connection manually
- ✅ Verify SSH key has correct format and permissions
- ✅ Check remote paths exist and are writable
- ✅ Ensure docker-compose is installed on remote host

### Policies not loading
- ✅ Validate YAML syntax
- ✅ Check Cerbos container logs
- ✅ Verify policies directory path in Cerbos config

---

## 📚 Resources

- [Grafana HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [Cerbos Documentation](https://docs.cerbos.dev/)
- [Cerbos Policy Writing Guide](https://docs.cerbos.dev/cerbos/latest/policies/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Grafana Terraform Provider](https://registry.terraform.io/providers/grafana/grafana/latest)

---

## 🤝 Contributing

1. Create a feature branch
2. Make changes (policies, scripts, workflows)
3. Test locally if possible
4. Submit pull request
5. After review and merge, changes deploy automatically

---

**Questions?** Check the main [README.md](README.md) or create an issue.
