# 🏗️ StarCourier Web - Backend Архитектура

Документация по архитектуре backend приложения StarCourier Web.

---

## 📋 Содержание

- [Обзор архитектуры](#-обзор-архитектуры)
- [Структура проекта](#-структура-проекта)
- [Модули](#-модули)
- [Поток данных](#-поток-данных)
- [Паттерны проектирования](#-паттерны-проектирования)

---

## 🎯 Обзор архитектуры

### Технологический стек

- **Фреймворк**: FastAPI 0.115.6
- **База данных**: SQLite/PostgreSQL + SQLAlchemy 2.0 (async)
- **Валидация**: Pydantic 2.9
- **Аутентификация**: JWT (PyJWT)
- **Кэширование**: Memory/Redis
- **Миграции**: Alembic

### Архитектурные принципы

1. **Separation of Concerns** - разделение ответственности
2. **Single Responsibility** - каждый модуль отвечает за одну задачу
3. **Dependency Injection** - внедрение зависимостей
4. **Async First** - асинхронность по умолчанию
5. **Type Safety** - строгая типизация

---

## 📁 Структура проекта

```
backend/
├── alembic/                 # Миграции БД
│   ├── versions/           # Файлы миграций
│   ├── env.py              # Окружение Alembic
│   └── script.py.mako      # Шаблон миграций
│
├── app/                    # Основное приложение
│   ├── api/                # API endpoints (Controllers)
│   │   ├── auth.py         # Аутентификация
│   │   ├── game.py         # Игровая логика
│   │   ├── characters.py   # Персонажи
│   │   ├── scenes.py       # Сцены
│   │   ├── abilities.py    # Способности
│   │   ├── quests.py       # Квесты
│   │   ├── game_mechanics.py # Игровые механики
│   │   ├── leaderboard.py  # Таблица лидеров
│   │   ├── achievements.py # Достижения
│   │   ├── analytics.py    # Аналитика
│   │   ├── admin.py        # Администрирование
│   │   ├── data.py         # Экспорт/импорт
│   │   └── websocket.py    # WebSocket
│   │
│   ├── models/             # Pydantic модели (DTO)
│   │   ├── base.py         # Базовые модели
│   │   ├── auth.py         # Модели аутентификации
│   │   └── game.py         # Игровые модели
│   │
│   ├── database/           # База данных
│   │   ├── models.py       # SQLAlchemy модели
│   │   └── connection.py   # Подключение
│   │
│   ├── services/           # Бизнес-логика (Service Layer)
│   │   ├── auth_service.py
│   │   ├── game_service.py
│   │   ├── cache_service.py
│   │   ├── email_service.py
│   │   ├── notification_service.py
│   │   └── ...
│   │
│   ├── middleware/         # Middleware
│   │   ├── rate_limit.py   # Rate limiting
│   │   ├── security.py     # Безопасность
│   │   └── performance.py  # Метрики
│   │
│   ├── data/               # Игровые данные (JSON)
│   │   ├── scenes.json
│   │   ├── characters.json
│   │   └── ...
│   │
│   ├── validators.py       # Кастомные валидаторы
│   ├── exceptions.py       # Обработчики исключений
│   ├── config.py           # Конфигурация
│   └── main.py             # Точка входа
│
├── tests/                  # Тесты
│   ├── test_api.py
│   ├── test_services.py
│   └── ...
│
├── requirements.txt        # Зависимости
├── requirements-dev.txt    # Dev зависимости
├── alembic.ini             # Конфигурация Alembic
└── .env                    # Переменные окружения
```

---

## 🔧 Модули

### API Layer (Controllers)

**Расположение**: `app/api/`

**Ответственность**:
- Обработка HTTP запросов
- Валидация входных данных
- Вызов сервисов
- Формирование ответов

**Пример**:
```python
from fastapi import APIRouter, Depends
from app.services.auth_service import AuthService
from app.models.base import APIResponse

router = APIRouter()

@router.post("/login")
async def login(request: LoginRequest, auth_service: AuthService = Depends()):
    result = await auth_service.authenticate(request)
    return APIResponse.success(data=result, message="Вход выполнен")
```

### Service Layer

**Расположение**: `app/services/`

**Ответственность**:
- Бизнес-логика
- Работа с базой данных
- Кэширование
- Внешние API

**Пример**:
```python
class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate(self, request: LoginRequest) -> Token:
        user = await self.get_user(request.username)
        if not self.verify_password(request.password, user.password):
            raise UnauthorizedException()
        return self.generate_tokens(user)
```

### Data Layer

**Расположение**: `app/database/`

**Ответственность**:
- Модели данных (SQLAlchemy)
- Подключение к БД
- Миграции
- Репозитории

### Models (DTO)

**Расположение**: `app/models/`

**Ответственность**:
- Валидация данных
- Сериализация/десериализация
- Типизация

---

## 🔄 Поток данных

### Типичный запрос

```
1. HTTP Request
   ↓
2. Middleware (Rate Limiting, Security, Logging)
   ↓
3. Router (API Endpoint)
   ↓
4. Валидация (Pydantic)
   ↓
5. Service Layer (Бизнес-логика)
   ↓
6. Database Layer (SQLAlchemy)
   ↓
7. Database (SQLite/PostgreSQL)
   ↓
8. Обратный поток с данными
   ↓
9. Формирование ответа (Pydantic)
   ↓
10. HTTP Response
```

### Пример: Начало игры

```python
# 1. Request
POST /api/game/start
{
    "player_id": "uuid"
}

# 2. Router (app/api/game.py)
@router.post("/start")
async def start_game(request: GameStartRequest):
    # 3. Service
    game_service = GameService()
    result = await game_service.start_new_game(request.player_id)
    
    # 4. Response
    return APIResponse.success(data=result)

# 5. Service (app/services/game_service.py)
class GameService:
    async def start_new_game(self, player_id: str) -> GameData:
        # Проверка существующей игры
        existing = await self.get_game(player_id)
        if existing:
            raise ConflictException("Игра уже существует")
        
        # Создание новой игры
        game_data = self.create_initial_game_state()
        
        # Сохранение в БД
        await self.db.save(game_data)
        
        return game_data
```

---

## 🎨 Паттерны проектирования

### 1. Dependency Injection

FastAPI автоматически внедряет зависимости:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    db = AsyncSession()
    try:
        yield db
    finally:
        await db.close()

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    ...
```

### 2. Repository Pattern

```python
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

### 3. Service Layer Pattern

```python
class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        cache_service: CacheService
    ):
        self.user_repo = user_repo
        self.cache_service = cache_service
    
    async def get_user(self, user_id: str) -> User:
        # Проверка кэша
        cached = await self.cache_service.get(f"user:{user_id}")
        if cached:
            return cached
        
        # Запрос из БД
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Пользователь не найден")
        
        # Кэширование
        await self.cache_service.set(f"user:{user_id}", user, ttl=300)
        
        return user
```

### 4. Factory Pattern

```python
class ResponseBuilder:
    @staticmethod
    def success(data: Any, message: str) -> APIResponse:
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(message: str, error_code: ErrorCodeEnum) -> APIError:
        return APIError(
            status=StatusEnum.ERROR,
            message=message,
            error_code=error_code
        )
```

### 5. Strategy Pattern

```python
class CacheStrategy(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int) -> None:
        pass

class MemoryCacheStrategy(CacheStrategy):
    ...

class RedisCacheStrategy(CacheStrategy):
    ...

class CacheService:
    def __init__(self, strategy: CacheStrategy):
        self.strategy = strategy
```

---

## 🔐 Обработка ошибок

### Иерархия исключений

```
Exception
├── AppException
│   ├── NotFoundException (404)
│   ├── UnauthorizedException (401)
│   ├── ForbiddenException (403)
│   ├── ConflictException (409)
│   ├── TooManyRequestsException (429)
│   ├── ValidationAppException (422)
│   └── InternalServerException (500)
├── HTTPException
├── RequestValidationError
└── SQLAlchemyError
```

### Использование

```python
from app.exceptions import NotFoundException, UnauthorizedException

@router.get("/game/{game_id}")
async def get_game(game_id: str):
    game = await game_service.get_game(game_id)
    if not game:
        raise NotFoundException(
            message="Игра не найдена",
            details=ErrorDetail(field="game_id", value=game_id)
        )
    return APIResponse.success(data=game)
```

---

## 📊 Валидация данных

### Pydantic Validators

```python
from pydantic import BaseModel, Field, field_validator
from app.validators import PasswordValidator, UsernameValidator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        return UsernameValidator.validate_username(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return PasswordValidator.validate_password(v)
```

---

## 🚀 Middleware

### Последовательность выполнения

1. **PerformanceMiddleware** - сбор метрик
2. **SecurityMiddleware** - security headers
3. **RateLimitMiddleware** - rate limiting
4. **RequestLoggerMiddleware** - логирование
5. **GZipMiddleware** - сжатие
6. **CORSMiddleware** - CORS

### Создание middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # До запроса
        request.state.start_time = time.time()
        
        response = await call_next(request)
        
        # После запроса
        duration = time.time() - request.state.start_time
        response.headers["X-Process-Time"] = str(duration)
        
        return response
```

---

## 🧪 Тестирование

### Unit тесты

```python
import pytest
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_authenticate_success():
    service = AuthService(db=test_db)
    token = await service.authenticate(
        LoginRequest(username="test", password="Test123!")
    )
    assert token is not None
    assert token.access_token is not None
```

### Integration тесты

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## 📈 Производительность

### Кэширование

```python
from app.services.cache_service import CacheService

cache = CacheService()

# Get with cache
async def get_user_cached(user_id: str):
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return cached
    
    user = await db.get_user(user_id)
    await cache.set(f"user:{user_id}", user, ttl=300)
    return user
```

### Lazy Loading

```python
from sqlalchemy.orm import selectinload

# Eager loading
users = await db.execute(
    select(User).options(selectinload(User.games))
)
```

---

## 🔗 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

*Последнее обновление: 15 марта 2026*
