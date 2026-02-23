# StarCourier Web - Backend Startup Script
Write-Host "🚀 Starting StarCourier Web Backend..." -ForegroundColor Cyan

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
Write-Host "📍 Starting server on http://localhost:8000" -ForegroundColor Cyan
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

