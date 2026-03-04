"""
StarCourier Web - Cache Service
Сервис кэширования с поддержкой Redis и in-memory fallback

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import os
import logging
import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List, Union
from functools import wraps
from collections import OrderedDict

from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# IN-MEMORY CACHE (Fallback)
# ============================================================================

class InMemoryCache:
    """
    In-memory кэш с LRU eviction и TTL
    
    Используется как fallback, когда Redis недоступен
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache: OrderedDict = OrderedDict()
        self._expiry: Dict[str, datetime] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def _evict_expired(self):
        """Удаление истёкших записей"""
        now = datetime.utcnow()
        expired_keys = [
            k for k, v in self._expiry.items()
            if v < now
        ]
        for key in expired_keys:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
    
    def _evict_lru(self):
        """Удаление старых записей при переполнении"""
        while len(self._cache) >= self._max_size:
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key, None)
            self._expiry.pop(oldest_key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        self._evict_expired()
        
        if key in self._cache:
            self._hits += 1
            # Перемещение в конец (LRU)
            self._cache.move_to_end(key)
            return self._cache[key]
        
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Установка значения в кэш"""
        self._evict_expired()
        self._evict_lru()
        
        ttl = ttl or self._default_ttl
        self._cache[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        if key in self._cache:
            del self._cache[key]
            del self._expiry[key]
            return True
        return False
    
    def clear(self):
        """Очистка всего кэша"""
        self._cache.clear()
        self._expiry.clear()
    
    def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        self._evict_expired()
        return key in self._cache
    
    def keys(self, pattern: str = None) -> List[str]:
        """Получение списка ключей"""
        self._evict_expired()
        if pattern:
            import fnmatch
            return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        return list(self._cache.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0
        
        return {
            "type": "memory",
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4)
        }


# ============================================================================
# REDIS CACHE (Primary)
# ============================================================================

class RedisCache:
    """
    Redis кэш для распределённых систем
    
    Требует установки: pip install redis
    """
    
    def __init__(self, redis_url: str, default_ttl: int = 300):
        self._redis_url = redis_url
        self._default_ttl = default_ttl
        self._client = None
        self._connected = False
        self._hits = 0
        self._misses = 0
    
    async def _get_client(self):
        """Получение Redis клиента"""
        if self._client is None:
            try:
                import redis.asyncio as redis
                self._client = redis.from_url(self._redis_url)
                await self._client.ping()
                self._connected = True
                logger.info("✅ Redis connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._connected = False
                return None
        
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из Redis"""
        client = await self._get_client()
        if not client:
            return None
        
        try:
            value = await client.get(key)
            if value:
                self._hits += 1
                return json.loads(value)
            self._misses += 1
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Установка значения в Redis"""
        client = await self._get_client()
        if not client:
            return
        
        try:
            ttl = ttl or self._default_ttl
            await client.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str) -> bool:
        """Удаление значения из Redis"""
        client = await self._get_client()
        if not client:
            return False
        
        try:
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self):
        """Очистка всего кэша (FLUSHDB)"""
        client = await self._get_client()
        if client:
            await client.flushdb()
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        client = await self._get_client()
        if not client:
            return False
        
        try:
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Получение списка ключей по паттерну"""
        client = await self._get_client()
        if not client:
            return []
        
        try:
            return [k.decode() for k in await client.keys(pattern)]
        except Exception as e:
            logger.error(f"Redis keys error: {e}")
            return []
    
    async def incr(self, key: str) -> int:
        """Инкремент значения"""
        client = await self._get_client()
        if not client:
            return 0
        
        try:
            return await client.incr(key)
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return 0
    
    async def expire(self, key: str, ttl: int):
        """Установка TTL для ключа"""
        client = await self._get_client()
        if client:
            await client.expire(key, ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0
        
        return {
            "type": "redis",
            "connected": self._connected,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4)
        }


# ============================================================================
# CACHE SERVICE
# ============================================================================

class CacheService:
    """
    Унифицированный сервис кэширования
    
    Использует Redis, если доступен, иначе in-memory
    """
    
    def __init__(self):
        self._redis_cache = None
        self._memory_cache = InMemoryCache()
        self._use_redis = settings.cache_enabled and settings.cache_type == "redis"
    
    async def initialize(self):
        """Инициализация кэша"""
        if self._use_redis:
            try:
                self._redis_cache = RedisCache(settings.redis_url)
                # Тестовое подключение
                client = await self._redis_cache._get_client()
                if not client:
                    logger.warning("⚠️ Redis unavailable, using in-memory cache")
                    self._use_redis = False
            except Exception as e:
                logger.warning(f"⚠️ Redis init failed: {e}, using in-memory cache")
                self._use_redis = False
        else:
            logger.info("📦 Using in-memory cache")
    
    @property
    def _cache(self):
        """Получение текущего кэша"""
        if self._use_redis and self._redis_cache:
            return self._redis_cache
        return self._memory_cache
    
    def _make_key(self, *args, **kwargs) -> str:
        """Создание ключа кэша"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)
        
        # Если ключ слишком длинный, хэшируем
        if len(key_string) > 200:
            return hashlib.md5(key_string.encode()).hexdigest()
        return key_string
    
    # Синхронные методы для in-memory
    
    def get_sync(self, key: str) -> Optional[Any]:
        """Синхронное получение из in-memory кэша"""
        if self._use_redis:
            logger.warning("Sync get called with Redis cache - use async version")
            return None
        return self._memory_cache.get(key)
    
    def set_sync(self, key: str, value: Any, ttl: int = None):
        """Синхронная установка в in-memory кэш"""
        if not self._use_redis:
            self._memory_cache.set(key, value, ttl)
    
    # Асинхронные методы
    
    async def get(self, key: str) -> Optional[Any]:
        """Асинхронное получение из кэша"""
        if self._use_redis and self._redis_cache:
            return await self._redis_cache.get(key)
        return self._memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Асинхронная установка в кэш"""
        if self._use_redis and self._redis_cache:
            await self._redis_cache.set(key, value, ttl)
        else:
            self._memory_cache.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Удаление из кэша"""
        if self._use_redis and self._redis_cache:
            return await self._redis_cache.delete(key)
        return self._memory_cache.delete(key)
    
    async def clear(self):
        """Очистка всего кэша"""
        if self._use_redis and self._redis_cache:
            await self._redis_cache.clear()
        else:
            self._memory_cache.clear()
    
    async def exists(self, key: str) -> bool:
        """Проверка существования"""
        if self._use_redis and self._redis_cache:
            return await self._redis_cache.exists(key)
        return self._memory_cache.exists(key)
    
    async def get_or_set(
        self, 
        key: str, 
        factory: callable,
        ttl: int = None
    ) -> Any:
        """
        Получение из кэша или вычисление и сохранение
        
        Args:
            key: Ключ кэша
            factory: Функция для вычисления значения (async)
            ttl: Время жизни в секундах
        
        Returns:
            Значение из кэша или вычисленное
        """
        # Проверяем кэш
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Вычисляем значение
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        # Сохраняем в кэш
        await self.set(key, value, ttl)
        
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        return self._cache.get_stats()


# ============================================================================
# CACHE DECORATOR
# ============================================================================

def cached(
    key_prefix: str = "",
    ttl: int = 300,
    key_builder: callable = None
):
    """
    Декоратор для кэширования результатов функций
    
    Usage:
        @cached(key_prefix="user", ttl=60)
        async def get_user(user_id: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создание ключа
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_service._make_key(key_prefix, *args, **kwargs)
            
            # Проверка кэша
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Выполнение функции
            result = await func(*args, **kwargs)
            
            # Сохранение в кэш
            await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

cache_service = CacheService()


# ============================================================================
# INITIALIZE ON STARTUP
# ============================================================================

async def init_cache():
    """Инициализация кэша при старте приложения"""
    await cache_service.initialize()
