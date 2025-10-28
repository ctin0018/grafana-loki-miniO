# Grafana + Loki + MinIO Observability Stack

This repository provides a complete observability stack with Grafana, Loki, MinIO, and Alloy for log aggregation and monitoring. It also includes GitOps-style workflows for managing Grafana users and Cerbos authorization policies.

## Quick Start

### Local Development

1. Start the stack:
```bash
docker-compose -f docker-compose-production.yml up -d
```

2. Access the services:
- **Grafana**: http://localhost:3002 (admin/admin123)
- **MinIO Console**: http://localhost:9001 (admin/admin123)
- **Loki**: http://localhost:3101

### Components

- **Grafana**: Visualization and dashboarding
- **Loki**: Log aggregation system
- **MinIO**: S3-compatible object storage for Loki chunks
- **Alloy**: Data collection and forwarding
- **Nginx**: Reverse proxy gateway
- **VM Simulator**: Generates sample logs from 30 virtual machines

## GitOps Workflows

This repository includes two GitHub Actions workflows to manage infrastructure in a GitOps-friendly way.

### 1. Bootstrap Grafana Users

**Workflow**: `.github/workflows/bootstrap-grafana.yml`

Automatically creates teams and users in Grafana using the `scripts/create_grafana_users.py` script.

#### When it runs:
- Manual trigger (`workflow_dispatch`)
- On push to `main` or `chris` branch when the script or workflow changes

#### Required GitHub Secrets:
- `GRAFANA_URL` - Your Grafana instance URL (e.g., `https://grafana.example.com`)
- `GRAFANA_ADMIN_USER` - Admin username (default: `admin`)
- `GRAFANA_ADMIN_PASS` - Admin password

#### How to use:
1. Set the required secrets in your GitHub repository settings
2. Modify `scripts/create_grafana_users.py` to define your teams and users
3. Push changes or manually trigger the workflow from the Actions tab

#### Example configuration in script:
```python
TEAMS_CONFIG = [
    {"name": "Platform Team", "email": "platform@example.com"},
    {"name": "Security Team", "email": "security@example.com"},
]

USERS_CONFIG = [
    {
        "email": "john.doe@example.com",
        "name": "John Doe",
        "login": "john.doe",
        "password": "changeme123",
        "teams": ["Platform Team"],
    },
]
```

### 2. Deploy Cerbos Policies

**Workflow**: `.github/workflows/deploy-cerbos-policies.yml`

Automatically deploys Cerbos authorization policies to a remote server via SSH.

#### When it runs:
- Manual trigger (`workflow_dispatch`)
- On push to `main` or `chris` branch when files under `cerbos/policies/` change

#### Required GitHub Secrets:
- `SSH_HOST` - Remote host IP or hostname
- `SSH_USER` - SSH username
- `SSH_PRIVATE_KEY` - Private SSH key (PEM format) for authentication
- `CERBOS_REMOTE_POLICIES_PATH` - Absolute path on remote where policies are stored (e.g., `/opt/cerbos/policies`)
- `CERBOS_REMOTE_BASE_PATH` - Directory containing `docker-compose.yml` for Cerbos
- `SSH_PORT` - (Optional) SSH port, defaults to 22

#### How to use:
1. Set up Cerbos on your remote server with Docker Compose
2. Configure the required secrets in GitHub
3. Edit policy files in `cerbos/policies/`
4. Push changes - the workflow will copy policies and restart Cerbos

#### Example Cerbos policies included:
- `derived_roles.yaml` - Common role definitions
- `common_variables.yaml` - Shared variables
- `dashboard_policy.yaml` - Dashboard access control
- `alert_policy.yaml` - Alert management permissions

## How GitOps Helps

### Benefits:
✅ **Version Control**: All policies and configurations are tracked in Git  
✅ **Code Review**: Changes go through PR review before deployment  
✅ **Auditability**: Full history of who changed what and when  
✅ **Automation**: Changes deploy automatically after merge  
✅ **Collaboration**: Non-technical admins can propose changes via PRs  
✅ **Rollback**: Easy to revert to previous versions  

### Workflow Example:
1. Developer creates a new Cerbos policy for a feature
2. Opens PR with the policy YAML file
3. Team reviews the policy
4. After merge to `main`, GitHub Actions automatically deploys it
5. Cerbos container restarts with new policies

## Next Steps (Recommended)

### 1. Add OIDC Authentication

Replace basic auth with enterprise SSO:
- Set up Keycloak or cloud IdP (Auth0, Okta, Azure AD)
- Configure Grafana to use OIDC
- Store client ID/secret in GitHub Secrets
- Manage users in the IdP instead of Grafana directly

**Benefits**: Centralized authentication, SSO, MFA support

### 2. Migrate to Terraform

Move from Python scripts to declarative infrastructure:
- Use the [Grafana Terraform Provider](https://registry.terraform.io/providers/grafana/grafana/latest)
- Define teams, users, dashboards, and data sources as code
- Add a GitHub Action to run `terraform apply`
- Store Terraform state in remote backend (S3, Terraform Cloud)

**Benefits**: Full infrastructure as code, drift detection, dependency management

### 3. Add Policy Testing

Validate Cerbos policies before deployment:
- Create test cases for policies
- Add GitHub Action to run Cerbos policy tests
- Use Cerbos CLI or API to validate policies
- Prevent broken policies from being deployed

**Benefits**: Catch policy errors early, ensure authorization rules work correctly

### 4. Containerize Bootstrap Script

Run bootstrap as a Docker service:
- Create a Dockerfile for the Python script
- Add it as a service in docker-compose
- Run as one-shot job or periodic task
- Remove Python dependency from local environment

**Benefits**: Consistency, no local Python setup needed, easier to run anywhere

## Architecture

```
┌─────────────┐
│   Nginx     │ :80 (Gateway)
└──────┬──────┘
       │
       ├──────> Grafana :3000
       └──────> MinIO :9000
                  │
                  │ S3 API
                  ▼
       ┌──────────────────┐
       │      Loki        │ :3100
       └──────────────────┘
                  ▲
                  │ Push logs
       ┌──────────────────┐
       │      Alloy       │ :12345
       └──────────────────┘
                  ▲
                  │ Scrape
       ┌──────────────────┐
       │  VM Simulator    │
       │  (30 VMs)        │
       └──────────────────┘
```

## Configuration Files

- `docker-compose-production.yml` - Main stack definition
- `loki/loki-config.yaml` - Loki configuration with MinIO backend
- `grafana/provisioning/` - Grafana provisioning configs
- `alloy/config.alloy` - Alloy data collection config
- `nginx/nginx.conf` - Nginx reverse proxy config
- `scripts/vm_log_simulator.py` - Log generator for testing

## Development

### View Logs
```bash
docker-compose -f docker-compose-production.yml logs -f [service-name]
```

### Restart Services
```bash
docker-compose -f docker-compose-production.yml restart [service-name]
```

### Stop Everything
```bash
docker-compose -f docker-compose-production.yml down
```

### Clean Volumes (⚠️ deletes data)
```bash
docker-compose -f docker-compose-production.yml down -v
```

## Security Notes

⚠️ **Change default passwords** in production  
⚠️ **Use secrets management** for credentials  
⚠️ **Enable TLS/HTTPS** for production deployments  
⚠️ **Rotate SSH keys** regularly  
⚠️ **Review Cerbos policies** carefully before deployment  
⚠️ **Use environment-specific configurations**  

## Troubleshooting

### Grafana won't start
- Check if port 3002 is already in use
- Verify permissions on mounted volumes
- Check logs: `docker logs grafana_container_miniO`

### Loki not receiving logs
- Verify Alloy is running and configured correctly
- Check Loki logs for errors
- Ensure MinIO bucket was created successfully

### MinIO connection issues
- Verify MinIO is healthy: `docker ps`
- Check MinIO credentials in environment variables
- Ensure bucket 'logs' was created

### SSH deployment fails
- Verify SSH key has correct permissions (600)
- Test SSH connection manually
- Check firewall rules on remote host
- Ensure remote paths exist and are writable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with docker-compose
5. Submit a pull request

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues and questions:
- Check the [Issues](../../issues) page
- Review logs in your containers
- Consult official documentation:
  - [Grafana Docs](https://grafana.com/docs/)
  - [Loki Docs](https://grafana.com/docs/loki/)
  - [Cerbos Docs](https://docs.cerbos.dev/)
  - [Alloy Docs](https://grafana.com/docs/alloy/)
