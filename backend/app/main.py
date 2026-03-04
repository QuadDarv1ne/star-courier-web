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
from app.api import game, characters, scenes

# Импорт сервисов
from app.services import data_service

# Импорт моделей
from app.models import HealthCheckResponse, ErrorResponse

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

    # Предзагрузка данных
    data_service.reload_data()
    scenes_count = len(data_service.get_scenes())
    characters_count = len(data_service.get_characters())
    logger.info(f"📊 Загружено: {scenes_count} сцен, {characters_count} персонажей")

    yield

    # Shutdown
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик ошибок"""
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

app.include_router(game.router, prefix="/api/game", tags=["🎮 Игра"])
app.include_router(characters.router, prefix="/api/characters", tags=["👥 Персонажи"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["📋 Сцены"])


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


@app.get("/", tags=["🏠 Root"], summary="Корневой endpoint")
async def root():
    """Корневой endpoint с информацией об API"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.docs_enabled else None,
        "health": "/health"
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
