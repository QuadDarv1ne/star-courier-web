# 🚀 StarCourier Web

**Интерактивная текстовая RPG в космической тематике**

Управляйте капитаном Максом Веллом на звездолёте "Элея", раскрывайте тайны древних артефактов и определяйте судьбу человечества.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D)
![License](https://img.shields.io/badge/license-MIT-green)

[![CI/CD](https://github.com/QuadDarv1ne/star-courier-web/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/QuadDarv1ne/star-courier-web/actions/workflows/ci-cd.yml)
[![Codecov](https://codecov.io/gh/QuadDarv1ne/star-courier-web/branch/main/graph/badge.svg)](https://codecov.io/gh/QuadDarv1ne/star-courier-web)

> **📢 Новое в версии 3.0:** Добавлены механики глав 11-18 — Система Резонанса, Пути развития (Альянс/Наблюдатель/Независимость), 3 финала, Ментальное состояние.
>
> 📖 [Документация по новым механикам](temp_extract/Star_Courier_Project/documentation/Star_Courier_New_Mechanics.md)

---

## 📋 Содержание

- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Установка](#-установка)
- [Запуск](#-запуск)
- [API документация](#-api-документация)
- [Структура проекта](#-структура-проекта)
- [Функции](#-функции)
- [Новые механики](#-новые-механики)
- [Разработка](#-разработка)
- [Вклад в проект](#-вклад-в-проект)

---

## ✨ Возможности

### 🎮 Игра
- Разветвлённый сюжет с множеством концовок
- Система отношений с персонажами
- Динамическая статистика персонажа
- Система достижений (22 достижения в 8 категориях)
- Таблица лидеров

### 🔧 Технологии
- **Backend**: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **Frontend**: Vue.js 3 + Pinia + Vite
- **PWA**: Офлайн поддержка
- **Security**: JWT, Rate Limiting, Security Headers

---

## 🛠 Технологии

### Backend
- **FastAPI** - асинхронный веб-фреймворк
- **SQLAlchemy** - ORM с async поддержкой
- **Alembic** - миграции базы данных
- **PyJWT** - аутентификация
- **bcrypt** - хэширование паролей

### Frontend
- **Vue.js 3** - Composition API
- **Pinia** - state management
- **Vite** - сборка
- **PWA** - Service Worker

### Инфраструктура
- **Docker** - контейнеризация
- **nginx** - reverse proxy
- **Redis** - кэширование (опционально)

---

## 📦 Установка

### Требования
- Python 3.10+
- Node.js 18+
- SQLite (по умолчанию) или PostgreSQL

### Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Миграции базы данных
alembic upgrade head

# Запуск
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build
```

### Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

---

## 🚀 Запуск

### Режим разработки

```bash
# Backend (порт 8000)
cd backend && uvicorn app.main:app --reload

# Frontend (порт 5173)
cd frontend && npm run dev
```

### Режим продакшена

```bash
# Сборка frontend
cd frontend && npm run build

# Запуск backend
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📚 API документация

После запуска backend доступна документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### Основные endpoints

| Endpoint | Описание |
|----------|----------|
| `/api/auth` | Аутентификация |
| `/api/game` | Игровой процесс |
| `/api/characters` | Персонажи |
| `/api/scenes` | Сцены |
| `/api/leaderboard` | Таблица лидеров |
| `/api/achievements` | Достижения |
| `/api/analytics` | Аналитика |
| `/api/admin` | Администрирование |
| `/api/data` | Экспорт/импорт данных |

---

## 📁 Структура проекта

```
star-courier-web/
├── backend/
│   ├── alembic/                 # Миграции БД
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   │   ├── admin.py         # Админ-панель
│   │   │   ├── analytics.py     # Аналитика
│   │   │   ├── auth.py          # Аутентификация
│   │   │   ├── data.py          # Экспорт/импорт
│   │   │   ├── game.py          # Игра
│   │   │   └── ...
│   │   ├── database/            # База данных
│   │   │   ├── models.py        # SQLAlchemy модели
│   │   │   └── connection.py    # Подключение
│   │   ├── middleware/          # Middleware
│   │   │   ├── rate_limit.py    # Rate limiting
│   │   │   ├── security.py      # Безопасность
│   │   │   └── performance.py   # Метрики
│   │   ├── models/              # Pydantic модели
│   │   ├── services/            # Бизнес-логика
│   │   │   ├── auth_service.py
│   │   │   ├── cache_service.py
│   │   │   ├── email_service.py
│   │   │   ├── health_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── score_service.py
│   │   │   └── backup_service.py
│   │   ├── data/                # Игровые данные
│   │   ├── config.py            # Конфигурация
│   │   └── main.py              # Точка входа
│   ├── tests/                   # Тесты
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Vue компоненты
│   │   ├── views/               # Страницы
│   │   ├── store/               # Pinia stores
│   │   ├── services/            # API сервисы
│   │   ├── locales/             # Переводы (i18n)
│   │   ├── plugins/             # Плагины
│   │   └── main.js
│   ├── public/
│   │   ├── sw.js                # Service Worker
│   │   └── manifest.json        # PWA manifest
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## ⚡ Функции

### 🔐 Аутентификация
- JWT токены (access + refresh)
- Регистрация с валидацией пароля
- Восстановление пароля по email

### 🛡 Безопасность
- Rate limiting (защита от DDoS)
- Security headers (CSP, XSS Protection)
- Защита от SQL-инъекций
- CORS

### 📊 Аналитика
- Отслеживание событий игры
- Статистика по сценам
- Воронка прохождения
- Real-time метрики

### 💾 База данных
- SQLite (по умолчанию) / PostgreSQL
- Async SQLAlchemy
- Alembic миграции
- Автоматические бэкапы

### 📦 Данные пользователя (GDPR)
- Экспорт в JSON/ZIP
- Импорт данных
- Полное удаление аккаунта

### 📈 Мониторинг
- Health checks
- Performance metrics
- Request timing
- Slow request detection

### 📧 Email
- Приветственные письма
- Уведомления о достижениях
- Восстановление пароля
- Еженедельные отчёты

### 🔔 Уведомления
- Real-time через WebSocket
- Offline уведомления
- Разные типы и приоритеты

---

## 🎮 Новые механики (Версия 3.0)

### 🌟 Система Резонанса
4 уровня развития способности чувствовать Сущность:
- **Уровень 1:** Обнаружение аномалий (радиус 100)
- **Уровень 2:** Усиление (радиус 500, восприятие слабых мест)
- **Уровень 3:** Мастерство (навигация через аномалии)
- **Уровень 4:** Трансцендентный (манипуляция реальностью)

### 🛤️ Система Путей
Выбор в главе 13 определяет союзников и бонусы:
- **Альянс:** Флот, ресурсы, официальная поддержка (+5000 кредитов)
- **Наблюдатель:** Древние знания, Psychic усиление (+20 Psychic)
- **Независимость:** Сеть агентов, контрабандистские маршруты

### 🎭 Система Финалов
3 уникальные концовки в главе 18:
- **Изгнание:** Уничтожение якоря Сущности (требуется жертва)
- **Договор:** Хранительство Границы (Psychic 70+ или Empathy 80+)
- **Слияние:** Трансцендентная эволюция (Psychic 90+ + Resonance 4)

### 🧠 Ментальное состояние
Отслеживание влияния Сущности (главы 16-17):
- **80-100:** Нормальное состояние
- **60-79:** Лёгкие галлюцинации
- **40-59:** Видения, снижение навыков
- **20-39:** Серьёзные нарушения
- **0-19:** Потеря контроля

### 📚 Новые данные
- **26 персонажей** с романтическими линиями
- **40+ квестов** для глав 6-18
- **50+ способностей** уровней 50-100
- **18 глав** в 4 арках

### 🔌 API для новых механик
```bash
GET  /api/game-mechanics/state          # Состояние игрока
POST /api/game-mechanics/resonance/gain # Опыт Резонанса
POST /api/game-mechanics/path/choose    # Выбор пути
POST /api/game-mechanics/ending/check   # Проверка финала
POST /api/game-mechanics/entity/contact # Контакт с Сущностью
```

📖 **Полная документация:** [NEW_MECHANICS.md](temp_extract/Star_Courier_Project/documentation/Star_Courier_New_Mechanics.md)

---

## 👨‍💻 Разработка

### Быстрый старт

```bash
# Клонируйте репозиторий
git clone https://github.com/QuadDarv1ne/star-courier-web.git
cd star-courier-web

# Настройте окружение (Linux/Mac)
./scripts/setup-dev.sh

# Настройте окружение (Windows PowerShell)
.\scripts\setup-dev.ps1
```

### Ручная настройка

#### Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate   # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск сервера разработки
npm run dev
```

### Инструменты разработчика

```bash
# Backend
cd backend
pytest tests/ -v                    # Запуск тестов
flake8 app/                         # Линтинг
mypy app/                           # Проверка типов
black app/                          # Форматирование

# Frontend
cd frontend
npm run test                        # Запуск тестов
npm run lint                        # Линтинг
npm run format                      # Форматирование
```

### Pre-commit хуки

```bash
# Установка pre-commit
pip install pre-commit
pre-commit install

# Запуск всех проверок
pre-commit run --all-files
```

---

## 🧪 Тестирование

```bash
# Backend тесты
cd backend
pytest tests/ -v --cov=app

# Frontend тесты
cd frontend
npm run test
```

---

## 🤝 Вклад в проект

Мы приветствуем вклад в проект! Пожалуйста, ознакомьтесь с:

- [CONTRIBUTING.md](CONTRIBUTING.md) - Гайд для контрибьюторов
- [TODO.md](TODO.md) - Дорожная карта проекта
- [CHANGELOG.md](CHANGELOG.md) - История изменений

### Как помочь

1. Найдите задачу в [TODO.md](TODO.md) или создайте Issue
2. Форкните репозиторий
3. Создайте ветку (`git checkout -b feature/your-feature`)
4. Внесите изменения и протестируйте
5. Отправьте Pull Request

---

## 📝 Конфигурация

### Переменные окружения (backend/.env)

```env
# Приложение
SC_APP_NAME=StarCourier Web
SC_ENVIRONMENT=development
SC_DEBUG=true

# База данных
SC_DATABASE_TYPE=sqlite
SC_DATABASE_URL=sqlite:///./starcourier.db

# JWT
JWT_SECRET_KEY=your-secret-key

# Email
SC_EMAIL_ENABLED=false
SC_SMTP_SERVER=smtp.gmail.com
SC_SMTP_PORT=587

# Redis (опционально)
SC_CACHE_ENABLED=false
SC_CACHE_TYPE=memory
```

---

## 👨‍💻 Команда и контакты

**Автор и ведущий разработчик:** QuadDarv1ne (Dupley Maxim Igorevich)

**Вкладчики:** [Список контрибьюторов](https://github.com/QuadDarv1ne/star-courier-web/graphs/contributors)

---

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

## 🙏 Благодарности

- FastAPI за отличный фреймворк
- Vue.js за реактивный frontend
- Всем контрибьюторам проекта

---

## 📚 Дополнительные ресурсы

- [Документация для разработчиков](temp_extract/Star_Courier_Project/documentation/README_DEVELOPERS.md)
- [Игровые механики](temp_extract/Star_Courier_Project/documentation/Star_Courier_New_Mechanics.md)
- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
