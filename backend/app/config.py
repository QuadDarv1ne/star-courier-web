"""
StarCourier Web - Configuration Settings
Управление конфигурацией приложения через Pydantic Settings

Загружает переменные из:
1. .env файла
2. Переменных окружения
3. Значений по умолчанию

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SETTINGS CLASS
# ============================================================================

class Settings(BaseSettings):
    """
    Главный класс конфигурации приложения
    
    Наследуется от BaseSettings для автоматической загрузки из .env
    """

    # ========================
    # APPLICATION SETTINGS
    # ========================
    
    app_name: str = "StarCourier Web"
    app_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    
    # ========================
    # SERVER SETTINGS
    # ========================
    
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    api_prefix: str = "/api"
    
    # CORS разрешённые источники
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Преобразование CORS origins в список"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # ========================
    # DATABASE SETTINGS
    # ========================
    
    database_type: str = "sqlite"  # sqlite, postgresql, mysql, mongodb
    database_url: str = "sqlite:///./starcourier.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_echo: bool = False  # Логировать SQL запросы
    
    # ========================
    # CACHE SETTINGS
    # ========================
    
    cache_enabled: bool = False
    cache_type: str = "memory"  # redis, memory
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300  # Time to live в секундах
    
    # ========================
    # AUTHENTICATION SETTINGS
    # ========================
    
    auth_enabled: bool = False
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    jwt_refresh_expiration_days: int = 7
    
    # ========================
    # EMAIL SETTINGS
    # ========================
    
    email_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "your-email@gmail.com"
    smtp_password: str = ""
    smtp_from_email: str = "noreply@starcourier.com"
    smtp_from_name: str = "StarCourier Web"
    
    # ========================
    # LOGGING SETTINGS
    # ========================
    
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file: str = "logs/app.log"
    log_max_bytes: int = 10485760  # 10MB
    log_backup_count: int = 5
    log_format: str = "text"  # json, text
    
    # ========================
    # GAME SETTINGS
    # ========================
    
    max_active_games: int = 1000
    session_timeout: int = 60  # минуты
    save_progress_to_db: bool = False
    auto_save_enabled: bool = False
    auto_save_interval: int = 5  # минуты
    
    # ========================
    # EXTERNAL APIs
    # ========================
    
    openai_api_key: Optional[str] = None
    sentry_dsn: Optional[str] = None
    
    # ========================
    # FRONTEND SETTINGS
    # ========================
    
    frontend_url: str = "http://localhost:5173"
    
    # ========================
    # DOCUMENTATION
    # ========================
    
    docs_enabled: bool = True
    redoc_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # ========================
    # PYDANTIC CONFIG
    # ========================
    
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
        env_prefix="SC_",
    )
    
    # ========================
    # СВОЙСТВА
    # ========================
    
    @property
    def is_production(self) -> bool:
        """Проверка, что это продакшен окружение"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Проверка, что это разработка"""
        return self.environment.lower() == "development"
    
    @property
    def is_staging(self) -> bool:
        """Проверка, что это staging окружение"""
        return self.environment.lower() == "staging"
    
    @property
    def database_connection_string(self) -> str:
        """Получить строку подключения к БД"""
        if self.database_type == "sqlite":
            return self.database_url
        elif self.database_type == "postgresql":
            return f"{self.database_url}?sslmode=require" if self.is_production else self.database_url
        else:
            return self.database_url
    
    @property
    def api_url(self) -> str:
        """Получить полный URL API"""
        return f"http://{self.server_host}:{self.server_port}{self.api_prefix}"
    
    @property
    def redis_connection_string(self) -> str:
        """Получить Redis строку подключения"""
        return self.redis_url
    
    # ========================
    # МЕТОДЫ
    # ========================
    
    def get_log_level(self) -> int:
        """Получить уровень логирования в формате logging"""
        import logging
        return getattr(logging, self.log_level.upper(), logging.INFO)
    
    def get_database_url(self, with_echo: bool = False) -> str:
        """
        Получить URL БД
        
        Args:
            with_echo: Логировать ли SQL запросы
            
        Returns:
            Строка подключения к БД
        """
        url = self.database_connection_string
        
        if with_echo and self.database_echo:
            if "?" in url:
                url += "&echo=true"
            else:
                url += "?echo=true"
        
        return url
    
    def log_config(self) -> None:
        """Логировать текущую конфигурацию (без чувствительных данных)"""
        logger.info("=" * 80)
        logger.info("📋 StarCourier Web Configuration")
        logger.info("=" * 80)
        logger.info(f"🏢 Application: {self.app_name} v{self.app_version}")
        logger.info(f"🌍 Environment: {self.environment}")
        logger.info(f"🐛 Debug: {self.debug}")
        logger.info(f"🖥️  Server: {self.server_host}:{self.server_port}")
        logger.info(f"💾 Database: {self.database_type}")
        logger.info(f"⚡ Cache: {self.cache_type} (enabled: {self.cache_enabled})")
        logger.info(f"🔑 Auth: {self.auth_enabled}")
        logger.info(f"📧 Email: {self.email_enabled}")
        logger.info(f"📊 Logging: {self.log_level}")
        logger.info(f"🎮 Max Games: {self.max_active_games}")
        logger.info(f"📚 Docs: {self.docs_enabled}")
        logger.info("=" * 80)


# ============================================================================
# SINGLETON PATTERN - КЭШИРОВАНИЕ SETTINGS
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Получить конфигурацию приложения (синглтон)
    
    Используется кэширование (@lru_cache) чтобы Settings
    создавался только один раз.
    
    Returns:
        Settings: Объект конфигурации
        
    Example:
        from config import get_settings
        settings = get_settings()
        print(settings.database_url)
    """
    logger.info("⚙️  Инициализация конфигурации...")
    settings = Settings()
    settings.log_config()
    return settings


# ============================================================================
# ОКРУЖЕНИЕ-СПЕЦИФИЧНЫЕ КОНФИГУРАЦИИ
# ============================================================================

class DevelopmentSettings(Settings):
    """Настройки для разработки"""
    debug: bool = True
    database_echo: bool = True
    log_level: str = "DEBUG"
    cache_enabled: bool = False


class ProductionSettings(Settings):
    """Настройки для продакшена"""
    debug: bool = False
    database_echo: bool = False
    log_level: str = "INFO"
    cache_enabled: bool = True
    auth_enabled: bool = True


class StagingSettings(Settings):
    """Настройки для staging"""
    debug: bool = False
    database_echo: bool = False
    log_level: str = "INFO"
    cache_enabled: bool = True


def get_settings_by_env(env: Optional[str] = None) -> Settings:
    """
    Получить конфигурацию в зависимости от окружения
    
    Args:
        env: Окружение (development, staging, production)
        
    Returns:
        Settings: Объект конфигурации для окружения
    """
    if env is None:
        base_settings = Settings()
        env = base_settings.environment
    
    if env.lower() == "production":
        return ProductionSettings()
    elif env.lower() == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()


# ============================================================================
# ЭКСПОРТ
# ============================================================================

# Глобальный объект конфигурации
settings = get_settings()

__all__ = [
    "Settings",
    "DevelopmentSettings",
    "ProductionSettings",
    "StagingSettings",
    "get_settings",
    "get_settings_by_env",
    "settings"
]


# ============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    """
    Примеры использования config.py
    
    Запуск: python config.py
    """
    
    import logging
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # -------- Пример 1: Использование глобального объекта settings --------
    print("\n📌 Пример 1: Глобальный объект settings")
    print(f"App Name: {settings.app_name}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Is Production: {settings.is_production}")
    print(f"Is Development: {settings.is_development}")
    
    # -------- Пример 2: Использование функции get_settings() --------
    print("\n📌 Пример 2: Функция get_settings()")
    custom_settings = get_settings()
    print(f"Server URL: {custom_settings.server_host}:{custom_settings.server_port}")
    print(f"Database: {custom_settings.database_type}")
    print(f"Cache Enabled: {custom_settings.cache_enabled}")
    
    # -------- Пример 3: Получение конфигурации для конкретного окружения --------
    print("\n📌 Пример 3: Конфигурация для окружения")
    prod_settings = get_settings_by_env("production")
    print(f"Production Debug: {prod_settings.debug}")
    print(f"Production Cache: {prod_settings.cache_enabled}")
    print(f"Production Auth: {prod_settings.auth_enabled}")
    
    dev_settings = get_settings_by_env("development")
    print(f"Development Debug: {dev_settings.debug}")
    print(f"Development Cache: {dev_settings.cache_enabled}")
    
    # -------- Пример 4: Работа с CORS origins --------
    print("\n📌 Пример 4: CORS origins")
    print(f"CORS Origins String: {settings.cors_origins}")
    print(f"CORS Origins List: {settings.cors_origins_list}")
    
    # -------- Пример 5: Логирование конфигурации --------
    print("\n📌 Пример 5: Логирование конфигурации")
    settings.log_config()
    
    # -------- Пример 6: Специальные методы --------
    print("\n📌 Пример 6: Специальные методы")
    print(f"Log Level (int): {settings.get_log_level()}")
    print(f"Database URL: {settings.get_database_url()}")
    print(f"API URL: {settings.api_url}")