#!/bin/bash
# StarCourier Web - Setup Development Environment
# Скрипт для настройки окружения разработки

set -e

echo "🚀 StarCourier Web - Настройка окружения разработки"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# ПРОВЕРКА ТРЕБОВАНИЙ
# ============================================================================

echo -e "\n${YELLOW}📋 Проверка требований...${NC}"

# Проверка Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 не найден"
    exit 1
fi

# Проверка Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js не найден"
    exit 1
fi

# Проверка npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm $NPM_VERSION"
else
    echo -e "${RED}✗${NC} npm не найден"
    exit 1
fi

# ============================================================================
# BACKEND SETUP
# ============================================================================

echo -e "\n${YELLOW}🐍 Настройка Backend...${NC}"

cd backend

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Виртуальное окружение создано"
else
    echo -e "${GREEN}✓${NC} Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
source venv/bin/activate

# Обновление pip
echo "Обновление pip..."
pip install --upgrade pip

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Зависимости установлены"

# Установка dev зависимостей
if [ -f "requirements-dev.txt" ]; then
    echo "Установка dev зависимостей..."
    pip install -r requirements-dev.txt
    echo -e "${GREEN}✓${NC} Dev зависимости установлены"
fi

# Создание .env файла
if [ ! -f ".env" ]; then
    echo "Создание .env файла..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env файл создан (отредактируйте при необходимости)"
else
    echo -e "${GREEN}✓${NC} .env файл уже существует"
fi

# Инициализация базы данных
echo "Инициализация базы данных..."
alembic upgrade head
echo -e "${GREEN}✓${NC} База данных инициализирована"

cd ..

# ============================================================================
# FRONTEND SETUP
# ============================================================================

echo -e "\n${YELLOW}🎨 Настройка Frontend...${NC}"

cd frontend

# Установка зависимостей
echo "Установка npm зависимостей..."
npm install
echo -e "${GREEN}✓${NC} npm зависимости установлены"

# Создание .env файла
if [ ! -f ".env" ]; then
    echo "Создание .env файла..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env файл создан"
else
    echo -e "${GREEN}✓${NC} .env файл уже существует"
fi

cd ..

# ============================================================================
# PRE-COMMIT HOOKS
# ============================================================================

echo -e "\n${YELLOW}🔧 Настройка pre-commit хуков...${NC}"

# Проверка наличия pre-commit
if command -v pre-commit &> /dev/null; then
    echo "Установка pre-commit хуков..."
    pre-commit install
    pre-commit install --hook-type commit-msg
    echo -e "${GREEN}✓${NC} Pre-commit хуки установлены"
else
    echo -e "${YELLOW}⚠${NC} pre-commit не найден. Установка..."
    pip install pre-commit
    pre-commit install
    pre-commit install --hook-type commit-msg
    echo -e "${GREEN}✓${NC} Pre-commit установлен и настроен"
fi

# ============================================================================
# GIT CONFIGURATION
# ============================================================================

echo -e "\n${YELLOW}📇 Настройка Git...${NC}"

# Настройка end-of-line
git config core.autocrlf input
echo -e "${GREEN}✓${NC} Git EOL настроен"

# ============================================================================
# VERIFICATION
# ============================================================================

echo -e "\n${YELLOW}✅ Проверка установки...${NC}"

# Проверка backend
cd backend
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
python -c "import pydantic; print(f'Pydantic {pydantic.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__}')"
cd ..

# Проверка frontend
cd frontend
npm list vue | head -1
npm list pinia | head -1
cd ..

# ============================================================================
# ЗАВЕРШЕНИЕ
# ============================================================================

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}✓ Настройка завершена успешно!${NC}"
echo -e "${GREEN}==================================================${NC}"

echo -e "\n${YELLOW}Следующие шаги:${NC}"
echo "1. Отредактируйте backend/.env при необходимости"
echo "2. Отредактируйте frontend/.env при необходимости"
echo "3. Запустите backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "4. Запустите frontend: cd frontend && npm run dev"
echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo "  Backend тесты:     cd backend && pytest tests/ -v"
echo "  Frontend тесты:    cd frontend && npm run test"
echo "  Lint backend:      cd backend && flake8 app/ && mypy app/"
echo "  Lint frontend:     cd frontend && npm run lint"
echo "  Pre-commit test:   pre-commit run --all-files"
echo ""
echo -e "${GREEN}🚀 Удачи в разработке!${NC}"
