# StarCourier Web - Setup Development Environment (PowerShell)
# Скрипт для настройки окружения разработки на Windows

$ErrorActionPreference = "Stop"

Write-Host "🚀 StarCourier Web - Настройка окружения разработки" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# ============================================================================
# ПРОВЕРКА ТРЕБОВАНИЙ
# ============================================================================

Write-Host "`n📋 Проверка требований..." -ForegroundColor Yellow

# Проверка Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 3 не найден" -ForegroundColor Red
    exit 1
}

# Проверка Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js не найден" -ForegroundColor Red
    exit 1
}

# Проверка npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm не найден" -ForegroundColor Red
    exit 1
}

# ============================================================================
# BACKEND SETUP
# ============================================================================

Write-Host "`n🐍 Настройка Backend..." -ForegroundColor Yellow

Set-Location backend

# Создание виртуального окружения
if (-not (Test-Path "venv")) {
    Write-Host "Создание виртуального окружения..."
    python -m venv venv
    Write-Host "✓ Виртуальное окружение создано" -ForegroundColor Green
} else {
    Write-Host "✓ Виртуальное окружение уже существует" -ForegroundColor Green
}

# Активация виртуального окружения
Write-Host "Активация виртуального окружения..."
.\venv\Scripts\Activate.ps1

# Обновление pip
Write-Host "Обновление pip..."
python -m pip install --upgrade pip

# Установка зависимостей
Write-Host "Установка зависимостей..."
pip install -r requirements.txt
Write-Host "✓ Зависимости установлены" -ForegroundColor Green

# Установка dev зависимостей
if (Test-Path "requirements-dev.txt") {
    Write-Host "Установка dev зависимостей..."
    pip install -r requirements-dev.txt
    Write-Host "✓ Dev зависимости установлены" -ForegroundColor Green
}

# Создание .env файла
if (-not (Test-Path ".env")) {
    Write-Host "Создание .env файла..."
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "✓ .env файл создан (отредактируйте при необходимости)" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env файл уже существует" -ForegroundColor Green
}

# Инициализация базы данных
Write-Host "Инициализация базы данных..."
alembic upgrade head
Write-Host "✓ База данных инициализирована" -ForegroundColor Green

Set-Location ..

# ============================================================================
# FRONTEND SETUP
# ============================================================================

Write-Host "`n🎨 Настройка Frontend..." -ForegroundColor Yellow

Set-Location frontend

# Установка зависимостей
Write-Host "Установка npm зависимостей..."
npm install
Write-Host "✓ npm зависимости установлены" -ForegroundColor Green

# Создание .env файла
if (-not (Test-Path ".env")) {
    Write-Host "Создание .env файла..."
    if (Test-Path ".env.example")) {
        Copy-Item .env.example .env
        Write-Host "✓ .env файл создан" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env файл уже существует" -ForegroundColor Green
}

Set-Location ..

# ============================================================================
# PRE-COMMIT HOOKS
# ============================================================================

Write-Host "`n🔧 Настройка pre-commit хуков..." -ForegroundColor Yellow

# Проверка наличия pre-commit
try {
    $precommitVersion = pre-commit --version 2>&1
    Write-Host "✓ pre-commit установлен" -ForegroundColor Green
} catch {
    Write-Host "⚠ pre-commit не найден. Установка..." -ForegroundColor Yellow
    pip install pre-commit
}

# Установка хуков
Write-Host "Установка pre-commit хуков..."
pre-commit install
pre-commit install --hook-type commit-msg
Write-Host "✓ Pre-commit хуки установлены" -ForegroundColor Green

# ============================================================================
# GIT CONFIGURATION
# ============================================================================

Write-Host "`n📇 Настройка Git..." -ForegroundColor Yellow

git config core.autocrlf false
Write-Host "✓ Git EOL настроен" -ForegroundColor Green

# ============================================================================
# VERIFICATION
# ============================================================================

Write-Host "`n✅ Проверка установки..." -ForegroundColor Yellow

# Проверка backend
Set-Location backend
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
python -c "import pydantic; print(f'Pydantic {pydantic.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__}')"
Set-Location ..

# Проверка frontend
Set-Location frontend
npm list vue | Select-Object -First 1
npm list pinia | Select-Object -First 1
Set-Location ..

# ============================================================================
# ЗАВЕРШЕНИЕ
# ============================================================================

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "✓ Настройка завершена успешно!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

Write-Host "`nСледующие шаги:" -ForegroundColor Yellow
Write-Host "1. Отредактируйте backend\.env при необходимости"
Write-Host "2. Отредактируйте frontend\.env при необходимости"
Write-Host "3. Запустите backend: cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
Write-Host "4. Запустите frontend: cd frontend; npm run dev"
Write-Host ""
Write-Host "Полезные команды:" -ForegroundColor Yellow
Write-Host "  Backend тесты:     cd backend; pytest tests/ -v"
Write-Host "  Frontend тесты:    cd frontend; npm run test"
Write-Host "  Lint backend:      cd backend; flake8 app/; mypy app/"
Write-Host "  Lint frontend:     cd frontend; npm run lint"
Write-Host "  Pre-commit test:   pre-commit run --all-files"
Write-Host ""
Write-Host "🚀 Удачи в разработке!" -ForegroundColor Green
