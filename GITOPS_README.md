GitOps-style workflows for Grafana + Cerbos

Overview

This repository includes two GitHub Actions workflows to help manage Grafana users and Cerbos policies in a GitOps-friendly way without immediately learning Terraform.

Workflows

1) Bootstrap Grafana Users - `.github/workflows/bootstrap-grafana.yml`
- Purpose: Runs `scripts/create_grafana_users.py` to create teams and users in Grafana.
- Trigger: Manual (`workflow_dispatch`) or on push to `main` or `chris` branch.
- Required GitHub secrets:
  - `GRAFANA_URL` (e.g., https://grafana.example.com)
  - `GRAFANA_ADMIN_USER` (default: admin)
  - `GRAFANA_ADMIN_PASS` (admin password)

2) Deploy Cerbos Policies - `.github/workflows/deploy-cerbos-policies.yml`
- Purpose: Copies `cerbos/policies/*` to a remote host and restarts the Cerbos container.
- Trigger: Manual or on push when files under `cerbos/policies/` change.
- Required GitHub secrets:
  - `SSH_HOST` - remote host IP or hostname
  - `SSH_USER` - username for SSH
  - `SSH_PRIVATE_KEY` - private SSH key (PEM) for the SSH_USER
  - `CERBOS_REMOTE_POLICIES_PATH` - absolute path on remote host where policies are stored (e.g., /opt/cerbos/policies)
  - `CERBOS_REMOTE_BASE_PATH` - directory containing `docker-compose.yml` for Cerbos on remote host
  - `SSH_PORT` - (optional)

How this helps

- You can edit Cerbos policy YAML files in the repository. When you push, the `deploy-cerbos-policies` workflow can automatically copy them to the server and restart Cerbos.
- Non-technical admins can open PRs that modify policies; after review and merge, the policies are deployed automatically.
- The `bootstrap-grafana` workflow provides a simple way to create initial users/teams. This is suitable for bootstrapping and small clients.

Next steps (recommended)

- Add an OIDC provider (Keycloak or cloud IdP) and configure Grafana to use it. Store client/secret in GitHub secrets and manage IdP users there for scale.
- Move from Python-based provisioning to Terraform with the Grafana provider for fully declarative Grafana resource management.
- Optionally add a GitHub Action that calls Cerbos API to run policy checks or tests before deploying.

If you want I can:
- Scaffold Terraform for Grafana resources (teams and users) and a GitHub Action to apply it.
- Containerize the bootstrap script so you don't need Python locally and run it as a one-shot Docker service.

Tell me which of the next steps you'd like; I'll implement it.