# StarCourier Web - Frontend Startup Script
Write-Host "🚀 Starting StarCourier Web Frontend..." -ForegroundColor Cyan

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Change to frontend directory
Set-Location frontend

# Start dev server
Write-Host "📍 Starting dev server on http://localhost:5173" -ForegroundColor Cyan
npm run dev

