$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "[1/3] Checking Docker Desktop..."
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker is not running. Please open Docker Desktop first, then run start.bat again."
    exit 1
}

Write-Host "[2/3] Starting services with Docker Compose..."
docker compose -p iot-warehouse up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start services."
    exit 1
}

function Wait-Health {
    param(
        [int]$Port,
        [string]$Name
    )

    for ($i = 1; $i -le 60; $i++) {
        try {
            Invoke-RestMethod -Uri "http://localhost:$Port/health" -TimeoutSec 2 *> $null
            Write-Host "$Name is ready."
            return
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    Write-Host "$Name did not become ready in time. Check logs with:"
    Write-Host "docker compose -p iot-warehouse logs $Name"
    exit 1
}

Write-Host "[3/3] Waiting for service health checks..."
Wait-Health -Port 8001 -Name "device-gateway"
Wait-Health -Port 8002 -Name "inventory-service"
Wait-Health -Port 8003 -Name "alert-service"

Write-Host ""
Write-Host "All services are running."
Write-Host "device-gateway:     http://localhost:8001/health"
Write-Host "inventory-service:  http://localhost:8002/health"
Write-Host "alert-service:      http://localhost:8003/health"
Write-Host ""
Write-Host "To send demo data, run demo.bat."
