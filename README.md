# 🚀 StarCourier Web

**Интерактивная текстовая RPG в космической тематике**

Управляйте капитаном Максом Веллом на звездолёте "Элея", раскрывайте тайны древних артефактов и определяйте судьбу человечества.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D)

---

## 📋 Содержание

- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Установка](#-установка)
- [Запуск](#-запуск)
- [API документация](#-api-документация)
- [Структура проекта](#-структура-проекта)
- [Функции](#-функции)

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

## 👨‍💻 Автор

**QuadDarv1ne** (Dupley Maxim Igorevich)

---

## 📄 Лицензия

MIT License

---

## 🙏 Благодарности

- FastAPI за отличный фреймворк
- Vue.js за реактивный frontend
- Всем контрибьюторам
