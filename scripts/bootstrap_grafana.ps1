# Grafana Bootstrap Script for Windows
# Usage: .\bootstrap_grafana.ps1

param(
    [string]$GrafanaUrl = "http://localhost:3002",
    [string]$AdminUser = "admin",
    [string]$AdminPass = "admin123"
)

Write-Host "🚀 Bootstrapping Grafana with Terraform..." -ForegroundColor Cyan

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Terraform
$tfVersion = & terraform version -json 2>$null | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform not found. Please install Terraform 1.0+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Terraform $($tfVersion.terraform_version) found" -ForegroundColor Green

# Check Python
$pythonVersion = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion found" -ForegroundColor Green

# Check requests module
python -c "import requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Installing Python requests module..." -ForegroundColor Yellow
    pip install requests
}
Write-Host "✅ Python requests module available" -ForegroundColor Green

# Navigate to terraform directory
Push-Location -Path (Join-Path $PSScriptRoot "..\terraform")

try {
    # Initialize Terraform
    Write-Host "`n🔧 Initializing Terraform..." -ForegroundColor Yellow
    terraform init
    if ($LASTEXITCODE -ne 0) { throw "Terraform init failed" }

    # Create tfvars file
    Write-Host "`n📝 Creating terraform.tfvars..." -ForegroundColor Yellow
    @"
grafana_url            = "$GrafanaUrl"
grafana_admin_user     = "$AdminUser"
grafana_admin_password = "$AdminPass"
"@ | Out-File -FilePath "terraform.tfvars" -Encoding UTF8

    # Validate
    Write-Host "`n✔️  Validating configuration..." -ForegroundColor Yellow
    terraform validate
    if ($LASTEXITCODE -ne 0) { throw "Terraform validation failed" }

    # Plan
    Write-Host "`n📊 Planning changes..." -ForegroundColor Yellow
    terraform plan -out=tfplan
    if ($LASTEXITCODE -ne 0) { throw "Terraform plan failed" }

    # Ask for confirmation
    Write-Host "`n⚠️  Ready to apply changes." -ForegroundColor Yellow
    $confirm = Read-Host "Do you want to proceed? (yes/no)"
    
    if ($confirm -eq "yes") {
        # Apply
        Write-Host "`n🚀 Applying changes..." -ForegroundColor Yellow
        terraform apply tfplan
        if ($LASTEXITCODE -ne 0) { throw "Terraform apply failed" }

        # Show outputs
        Write-Host "`n📊 Terraform Outputs:" -ForegroundColor Cyan
        terraform output
        
        Write-Host "`n✅ Bootstrap complete!" -ForegroundColor Green
        Write-Host "🌐 Access Grafana at: $GrafanaUrl" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Apply cancelled by user" -ForegroundColor Yellow
    }

} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}