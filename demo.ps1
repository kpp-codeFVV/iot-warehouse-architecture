$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "[1/3] Checking running services..."
Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5 *> $null
Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 5 *> $null
Invoke-RestMethod -Uri "http://localhost:8003/health" -TimeoutSec 5 *> $null

Write-Host "[2/3] Sending abnormal temperature and low-stock sample..."
docker compose -p iot-warehouse exec -T device-gateway python /workspace/scripts/data-gen/send_sample.py --abnormal --low-stock
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to send sample data. Please run start.bat first."
    exit 1
}

Start-Sleep -Seconds 1

Write-Host "[3/3] Querying alerts..."
$alerts = Invoke-RestMethod -Uri "http://localhost:8003/alerts" -TimeoutSec 5
$alerts | ConvertTo-Json -Depth 8

Write-Host ""
Write-Host "Demo finished. If count is greater than 0 and alertType is HIGH_TEMPERATURE, the main flow is working."
