# StarCourier Web - Backend Startup Script
Write-Host "🚀 Starting StarCourier Web Backend..." -ForegroundColor Cyan

# Function to check if port is available
function Test-PortAvailable {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue -State Listen
        return $null -eq $connection
    } catch {
        return $true
    }
}

# Find available port starting from 8080
$Port = 8080
$MaxPort = 8099
while (-not (Test-PortAvailable -Port $Port) -and $Port -lt $MaxPort) {
    $Port++
}

if (-not (Test-PortAvailable -Port $Port)) {
    Write-Host "❌ No available port found in range 8000-$MaxPort" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
if (Test-Path "backend-venv\Scripts\Activate.ps1") {
    . backend-venv\Scripts\Activate.ps1
    Write-Host "✅ Activated backend-venv" -ForegroundColor Green
} elseif (Test-Path "backend\venv\Scripts\Activate.ps1") {
    . backend\venv\Scripts\Activate.ps1
    Write-Host "✅ Activated backend\venv" -ForegroundColor Green
} else {
    Write-Host "⚠️ No virtual environment found" -ForegroundColor Yellow
}

# Change to backend/app directory
Set-Location backend\app

# Start server
Write-Host "📍 Starting server on http://localhost:$Port" -ForegroundColor Cyan
python -m uvicorn main:app --reload --host 0.0.0.0 --port $Port

