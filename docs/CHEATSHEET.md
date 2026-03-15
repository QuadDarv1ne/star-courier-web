# 🛠️ StarCourier Web - Шпаргалка разработчика

Быстрый справочник по командам для разработки проекта.

---

## 📦 Установка и настройка

### Первая установка

```bash
# Windows (PowerShell)
.\scripts\setup-dev.ps1

# Linux/Mac
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh
```

### Ручная установка

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate   # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 🚀 Запуск

### Backend

```bash
cd backend
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate   # Windows

# Режим разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Продакшен режим
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# С логированием
uvicorn app.main:app --reload --log-level debug
```

### Frontend

```bash
cd frontend

# Режим разработки
npm run dev

# Продакшен сборка
npm run build

# Предпросмотр сборки
npm run preview
```

### Docker

```bash
# Сборка и запуск
docker-compose up -d

# Сборка с пересборкой образов
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

---

## 🧪 Тестирование

### Backend

```bash
cd backend
source venv/bin/activate

# Все тесты
pytest tests/ -v

# С покрытием
pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

# Конкретный тест
pytest tests/test_api.py::test_health_check -v

# С логированием
pytest tests/ -v -o log_cli=true -o log_cli_level=INFO

# Параллельный запуск
pytest tests/ -v -n auto

# Только упавшие тесты
pytest tests/ -v --lf

# Тесты с маркером
pytest tests/ -v -m "slow"
```

### Frontend

```bash
cd frontend

# Все тесты
npm run test

# Watch режим
npm run test:watch

# С покрытием
npm run test:coverage

# Конкретный тест
npm run test -- --run tests/unit/game.test.js
```

---

## 🔍 Линтинг и форматирование

### Backend

```bash
cd backend
source venv/bin/activate

# Flake8 (линтинг)
flake8 app/ tests/ --count --statistics

# Black (форматирование)
black app/ tests/

# Black (проверка)
black --check app/ tests/

# isort (сортировка импортов)
isort app/ tests/

# isort (проверка)
isort --check-only app/ tests/

# mypy (проверка типов)
mypy app/ --ignore-missing-imports

# Всё сразу
flake8 app/ && isort --check-only app/ && black --check app/ && mypy app/
```

### Frontend

```bash
cd frontend

# ESLint
npm run lint

# ESLint (исправление)
npm run lint -- --fix

# Prettier (форматирование)
npm run format

# Prettier (проверка)
npm run format -- --check
```

---

## 🔧 Pre-commit

```bash
# Установка хуков
pre-commit install
pre-commit install --hook-type commit-msg

# Запуск всех проверок
pre-commit run --all-files

# Запуск конкретного хука
pre-commit run flake8 --all-files
pre-commit run black --all-files

# Пропуск проверок (не рекомендуется)
git commit -m "msg" --no-verify
```

---

## 📊 База данных

```bash
cd backend
source venv/bin/activate

# Создать миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1

# Откатить к конкретной
alembic downgrade base

# Показать текущую
alembic current

# История миграций
alembic history

# Очистить БД
rm starcourier.db
alembic upgrade head
```

---

## 🐛 Отладка

### Backend

```bash
# Запуск с debugpy
python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app

# В коде
import debugpy
debugpy.breakpoint()

# Логирование
uvicorn app.main:app --log-level debug
```

### Frontend

```javascript
// В коде
debugger;
console.log('Debug:', variable);
console.table(array);
```

---

## 📈 Мониторинг

### Health Check

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Детальная проверка
curl http://localhost:8000/health/detailed

# Метрики
curl http://localhost:8000/metrics
```

### Логи

```bash
# Backend логи
docker-compose logs -f backend
tail -f logs/app.log

# Frontend логи
docker-compose logs -f frontend

# Все логи
docker-compose logs -f
```

---

## 🧹 Очистка

### Backend

```bash
cd backend

# Удалить кэш Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Удалить coverage
rm -rf htmlcov/
rm -f .coverage
rm -f coverage.xml
```

### Frontend

```bash
cd frontend

# Удалить node_modules
rm -rf node_modules/

# Удалить сборку
rm -rf dist/

# Удалить кэш
rm -rf .vite/
rm -rf .vitest/
rm -f .eslintcache
```

### Полная очистка

```bash
# Всё сразу
git clean -fdx
docker-compose down -v
rm -rf backend/venv/ frontend/node_modules/
```

---

## 🔐 Безопасность

### Проверка зависимостей

```bash
# Backend
cd backend
pip install safety
safety check -r requirements.txt

# Frontend
cd frontend
npm audit
npm audit fix
```

### Генерация секретов

```bash
# JWT секрет
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Пароль
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📦 Зависимости

### Backend

```bash
cd backend

# Обновить pip
pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt

# Установить dev зависимости
pip install -r requirements-dev.txt

# Обновить зависимости
pip list --outdated
pip install --upgrade package_name

# Заморозить зависимости
pip freeze > requirements.txt
```

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Установить конкретную версию
npm install package@version

# Обновить зависимости
npm update

# Проверить устаревшие
npm outdated

# Обновить мажорные версии
npx npm-check-updates -u
npm install
```

---

## 🚀 Деплой

### Продакшен сборка

```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend
npm run build

# Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Проверка перед деплоем

```bash
# Backend
pytest tests/ -v --cov=app
flake8 app/
mypy app/

# Frontend
npm run test
npm run lint
npm run build
```

---

## 🎯 Полезные сниппеты

### Создать новую API endpoint

```python
# backend/app/api/new_feature.py
from fastapi import APIRouter
from app.models import ResponseModel

router = APIRouter()

@router.get("/endpoint")
async def get_endpoint():
    return ResponseModel(
        status="success",
        message="Description",
        data={}
    )
```

### Создать Vue компонент

```vue
<!-- frontend/src/components/NewComponent.vue -->
<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true }
})

const emit = defineEmits(['update'])
</script>

<template>
  <div class="component">
    <h2>{{ title }}</h2>
  </div>
</template>

<style scoped>
.component {
  padding: 1rem;
}
</style>
```

---

## 📞 Troubleshooting

### Backend не запускается

```bash
# Проверить зависимости
pip install -r requirements.txt

# Проверить БД
alembic upgrade head

# Проверить логи
tail -f logs/app.log
```

### Frontend не собирается

```bash
# Очистить кэш
rm -rf node_modules/
rm -rf package-lock.json
npm install

# Проверить версию Node
node --version  # Требуется 18+
```

### Тесты не проходят

```bash
# Очистить кэш pytest
rm -rf .pytest_cache/
rm -rf __pycache__/

# Запустить с verbose
pytest tests/ -v -s
```

---

*Последнее обновление: 15 марта 2026*
