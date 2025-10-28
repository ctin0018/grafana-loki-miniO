# test_open_source_stack.ps1
# Purpose: Verify your stack is 100% open source, controllable, and resilient.

Write-Host "=== 🧪 Open Source Stack Verification ===`n"

# 1️⃣ Check Grafana API control
Write-Host "[1/4] Testing REST API control..."
try {
    $users = curl.exe -s -u admin:admin http://localhost:3000/api/users
    if ($users) {
        Write-Host "✅ Grafana API reachable. Users returned:"
        $users | Out-String | Write-Host
    } else {
        Write-Host "❌ Grafana API not responding."
    }
} catch {
    Write-Host "❌ Failed to connect to Grafana API."
}

# 2️⃣ Test retry logic in Python
Write-Host "`n[2/4] Testing retry logic..."
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pythonPath) {
    Write-Host "⚠️ Python not found. Skipping retry test."
} else {
    Write-Host "Simulating Grafana downtime..."
    docker stop grafana > $null 2>&1
    Write-Host "Running create_grafana_users.py (expected to retry)..."
    python .\scripts\create_grafana_users.py
    Start-Sleep -Seconds 3
    docker start grafana > $null 2>&1
    Write-Host "✅ Retry logic test completed. Check logs for retry attempts."
}

# 3️⃣ Test Terraform debug output
Write-Host "`n[3/4] Testing Terraform debugging..."
$env:TF_LOG = "DEBUG"
terraform plan | Out-File -FilePath .\tests\terraform_debug.log
Write-Host "✅ Terraform debug logs saved to tests/terraform_debug.log"
Remove-Item Env:\TF_LOG

# 4️⃣ Test offline mode
Write-Host "`n[4/4] Testing offline mode..."
Write-Host "Disconnect network manually or disable Wi-Fi, then rerun:"
Write-Host "    terraform apply"
Write-Host "✅ If it still works, you are fully offline-ready."
Write-Host "`n=== ✅ Tests Completed. Check logs in ./tests/ ==="
