"""
StarCourier Web - FastAPI Backend
Главная точка входа приложения (РЕФАКТОРИНГ)

Автор: Dupley Maxim Igorevich
Версия: 2.0.0
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# Импорт конфигурации
from app.config import settings

# Импорт роутеров
from app.api import (
    game, characters, scenes, websocket, auth, leaderboard,
    achievements, analytics, admin, data, abilities, quests,
    game_mechanics, inventory, combat, game_integration
)

# Импорт сервисов
from app.services import data_service

# Импорт базы данных
from app.database import init_db, close_db

# Импорт middleware
from app.middleware import RateLimitMiddleware, RequestLoggerMiddleware, SecurityMiddleware
from app.middleware.rate_limit import RateLimiter, rate_limiter
from app.middleware.performance import PerformanceMiddleware, metrics

# Импорт кэша
from app.services.cache_service import init_cache

# Импорт моделей
from app.models import HealthCheckResponse, ErrorResponse

# Импорт обработчиков исключений
from app.exceptions import register_exception_handlers

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

logging.basicConfig(
    level=settings.get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("🚀 Запуск StarCourier Web...")
    logger.info(f"📦 Среда: {settings.environment}")
    logger.info(f"🔧 Debug режим: {settings.debug}")
    
    # Инициализация базы данных
    await init_db()
    logger.info("💾 База данных инициализирована")
    
    # Инициализация кэша
    await init_cache()
    logger.info("⚡ Кэш инициализирован")

    # Предзагрузка данных
    data_service.reload_data()
    scenes_count = len(data_service.get_scenes())
    characters_count = len(data_service.get_characters())
    logger.info(f"📊 Загружено: {scenes_count} сцен, {characters_count} персонажей")

    yield

    # Shutdown
    await close_db()
    logger.info("🛑 Остановка StarCourier Web...")


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="StarCourier Web API",
    description="""
    🚀 **Интерактивная текстовая RPG в космической тематике**

    Управляйте капитаном Максом Веллом на звездолёте "Элея",
    раскрывайте тайны древних артефактов и определяйте судьбу человечества.

    ## Основные возможности
    - 🎮 Интерактивные диалоги с разветвлённым сюжетом
    - 👥 Система отношений с членами команды
    - 📊 Динамическая статистика
    - 🌌 Множество концовок
    - 🏆 Таблица лидеров
    - 🎖️ Система достижений

    ## Документация
    - [Swagger UI](/docs)
    - [ReDoc](/redoc)
    """,
    version="2.0.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.redoc_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# Performance monitoring (первый для сбора метрик)
app.add_middleware(PerformanceMiddleware)

# Security middleware
app.add_middleware(SecurityMiddleware, debug=settings.debug)

# Rate limiting
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

# Request logger
app.add_middleware(RequestLoggerMiddleware)

# GZip сжатие
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

# Регистрация глобальных обработчиков исключений
register_exception_handlers(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик ошибок (резервный)
    
    Примечание: Основные обработчики зарегистрированы через register_exception_handlers()
    """
    # Этот обработчик остаётся как резервный
    logger.error(f"❌ Необработанная ошибка: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            message="Внутренняя ошибка сервера",
            details={"error": str(exc)} if settings.debug else None
        ).model_dump()
    )


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(auth.router, prefix="/api/auth", tags=["🔐 Аутентификация"])
app.include_router(game.router, prefix="/api/game", tags=["🎮 Игра"])
app.include_router(characters.router, prefix="/api/characters", tags=["👥 Персонажи"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["📋 Сцены"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["🏆 Лидеры"])
app.include_router(achievements.router, prefix="/api/achievements", tags=["🎖️ Достижения"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["📊 Аналитика"])
app.include_router(admin.router, prefix="/api/admin", tags=["👑 Администрирование"])
app.include_router(data.router, prefix="/api/data", tags=["📦 Данные"])
app.include_router(abilities.router, prefix="/api/abilities", tags=["⚡ Способности"])
app.include_router(quests.router, prefix="/api/quests", tags=["📜 Квесты"])
app.include_router(game_mechanics.router, prefix="/api/game-mechanics", tags=["🎮 Игровые механики"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["🎒 Инвентарь"])
app.include_router(combat.router, prefix="/api/combat", tags=["⚔️ Бой"])
app.include_router(game_integration.router, prefix="/api/game-integration", tags=["🎮 Интеграция"])
app.include_router(websocket.router, tags=["🔌 WebSocket"])


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse,
         tags=["🏥 Health"], summary="Проверка здоровья")
async def health_check():
    """
    Проверка работоспособности API.

    Возвращает статус сервера и метаданные.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now().isoformat(),
        database="connected" if settings.database_type == "sqlite" else "not_configured",
        cache="enabled" if settings.cache_enabled else "disabled"
    )


@app.get("/health/detailed", tags=["🏥 Health"], summary="Детальная проверка здоровья")
async def health_check_detailed():
    """
    Детальная проверка здоровья всех компонентов системы.
    
    Включает:
    - База данных
    - Кэш (Redis/Memory)
    - Дисковое пространство
    - Память
    - CPU
    - Email сервис
    - WebSocket
    """
    from app.services.health_service import health_check_service
    return await health_check_service.check_all()


@app.get("/metrics", tags=["📊 Metrics"], summary="Метрики производительности")
async def get_metrics():
    """
    Получение метрик производительности приложения.
    
    Включает:
    - Статистику запросов
    - Время ответа по endpoints
    - Медленные запросы
    - Распределение по времени
    """
    from app.middleware.performance import get_performance_stats
    return get_performance_stats()


@app.get("/", tags=["🏠 Root"], summary="Корневой endpoint")
async def root():
    """Корневой endpoint с информацией об API"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.docs_enabled else None,
        "health": "/health",
        "health_detailed": "/health/detailed",
        "metrics": "/metrics",
        "features": {
            "auth": "/api/auth",
            "game": "/api/game",
            "characters": "/api/characters",
            "scenes": "/api/scenes",
            "leaderboard": "/api/leaderboard",
            "achievements": "/api/achievements",
            "analytics": "/api/analytics",
            "admin": "/api/admin",
            "data": "/api/data",
            "websocket": "/ws/{player_id}"
        }
    }


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )
