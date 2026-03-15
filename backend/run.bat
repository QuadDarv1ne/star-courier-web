@echo off
REM StarCourier Web - Запуск backend сервера
REM Автоматическая проверка свободного порта

echo ========================================
echo   StarCourier Web - Backend Server
echo ========================================
echo.

cd /d "%~dp0"

REM Проверка виртуального окружения
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Виртуальное окружение не найдено!
    echo Запустите: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Запуск сервера с авто-выбором порта
echo [INFO] Проверка свободного порта...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

REM Если порт 8000 занят, попробовать 8001
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARN] Порт 8000 занят, пробуем порт 8001...
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
)

pause
