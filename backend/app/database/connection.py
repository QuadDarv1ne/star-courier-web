"""
StarCourier Web - Database Connection
Управление подключением к базе данных с поддержкой async SQLite

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Optional

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database.models import Base

logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE ENGINE
# ============================================================================

class Database:
    """Менеджер базы данных"""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self._initialized = False
    
    def _get_database_url(self) -> str:
        """Получение URL базы данных"""
        if settings.database_type == "sqlite":
            db_path = Path(settings.database_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path}"
        elif settings.database_type == "postgresql":
            return settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            return settings.database_url
    
    async def init(self):
        """Инициализация базы данных"""
        if self._initialized:
            return
        
        logger.info("🗄️  Инициализация базы данных...")
        
        database_url = self._get_database_url()
        logger.info(f"📁 Database URL: {database_url.split('@')[-1] if '@' in database_url else database_url}")
        
        # Создание движка
        engine_kwargs = {
            "echo": settings.database_echo,
            "future": True,
        }
        
        if settings.database_type == "sqlite":
            # Специфичные настройки для SQLite
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 30,
                }
            })
        
        self.engine = create_async_engine(database_url, **engine_kwargs)
        
        # Настройка сессий
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        
        # Создание таблиц
        await self._create_tables()
        
        self._initialized = True
        logger.info("✅ База данных инициализирована")
    
    async def _create_tables(self):
        """Создание таблиц"""
        async with self.engine.begin() as conn:
            # Включение внешних ключей для SQLite
            if settings.database_type == "sqlite":
                await conn.execute(text("PRAGMA foreign_keys=ON"))
                await conn.execute(text("PRAGMA journal_mode=WAL"))
                await conn.execute(text("PRAGMA synchronous=NORMAL"))
                await conn.execute(text("PRAGMA cache_size=10000"))
                await conn.execute(text("PRAGMA temp_store=MEMORY"))
            
            # Создание таблиц
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("📊 Таблицы созданы")
    
    async def close(self):
        """Закрытие соединения с базой данных"""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("🔒 Соединение с базой данных закрыто")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение сессии базы данных"""
        if not self._initialized:
            await self.init()
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def execute_raw(self, sql: str, params: dict = None):
        """Выполнение сырого SQL запроса"""
        async with self.get_session() as session:
            result = await session.execute(text(sql), params or {})
            return result
    
    async def health_check(self) -> bool:
        """Проверка здоровья базы данных"""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Глобальный экземпляр
database = Database()


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных
    
    Example:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with database.get_session() as session:
        yield session


async def init_db():
    """Инициализация базы данных (вызывается при старте приложения)"""
    await database.init()


async def close_db():
    """Закрытие базы данных (вызывается при остановке приложения)"""
    await database.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def get_or_create(
    session: AsyncSession,
    model: type,
    defaults: dict = None,
    **kwargs
) -> tuple:
    """
    Получить или создать объект
    
    Args:
        session: Сессия БД
        model: Модель SQLAlchemy
        defaults: Значения по умолчанию для создания
        **kwargs: Параметры поиска
    
    Returns:
        Кортеж (объект, создан_ли_новый)
    """
    from sqlalchemy import select
    
    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()
    
    if instance:
        return instance, False
    
    # Создание нового объекта
    params = {**kwargs, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    await session.flush()
    
    return instance, True


async def bulk_insert(
    session: AsyncSession,
    model: type,
    data: list[dict]
) -> int:
    """
    Массовая вставка записей
    
    Args:
        session: Сессия БД
        model: Модель SQLAlchemy
        data: Список словарей с данными
    
    Returns:
        Количество вставленных записей
    """
    objects = [model(**item) for item in data]
    session.add_all(objects)
    await session.flush()
    return len(objects)


# ============================================================================
# EVENTS
# ============================================================================

@event.listens_for(AsyncSession, "before_commit")
def receive_before_commit(session):
    """Обработчик перед коммитом - обновление временных меток"""
    for instance in session.new:
        if hasattr(instance, 'created_at') and instance.created_at is None:
            instance.created_at = datetime.utcnow()
        if hasattr(instance, 'updated_at') and instance.updated_at is None:
            instance.updated_at = datetime.utcnow()
    
    for instance in session.dirty:
        if hasattr(instance, 'updated_at'):
            instance.updated_at = datetime.utcnow()
