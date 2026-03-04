"""
StarCourier Web - Rate Limiting Middleware
Middleware для ограничения частоты запросов

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ============================================================================
# IN-MEMORY RATE LIMITER
# ============================================================================

class InMemoryRateLimiter:
    """In-memory rate limiter с скользящим окном"""
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._blocked: Dict[str, datetime] = {}
    
    def _cleanup_old_requests(self, key: str, window_seconds: int):
        """Очистка старых запросов"""
        cutoff = time.time() - window_seconds
        self._requests[key] = [
            t for t in self._requests[key] if t > cutoff
        ]
    
    def is_allowed(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> Tuple[bool, int, int]:
        """
        Проверка разрешения запроса
        
        Args:
            key: Ключ для идентификации клиента
            max_requests: Максимальное количество запросов
            window_seconds: Временное окно в секундах
        
        Returns:
            Кортеж (разрешено, оставшиеся_запросы, время_до_сброса)
        """
        now = time.time()
        
        # Проверка блокировки
        if key in self._blocked:
            if self._blocked[key] > datetime.utcnow():
                remaining = (self._blocked[key] - datetime.utcnow()).total_seconds()
                return False, 0, int(remaining)
            else:
                del self._blocked[key]
        
        # Очистка старых запросов
        self._cleanup_old_requests(key, window_seconds)
        
        # Проверка лимита
        current_count = len(self._requests[key])
        
        if current_count >= max_requests:
            oldest = min(self._requests[key]) if self._requests[key] else now
            reset_time = int(oldest + window_seconds - now)
            return False, 0, max(1, reset_time)
        
        # Добавление запроса
        self._requests[key].append(now)
        remaining = max_requests - len(self._requests[key])
        
        return True, remaining, window_seconds
    
    def block(self, key: str, duration_seconds: int):
        """Блокировка ключа на указанное время"""
        self._blocked[key] = datetime.utcnow() + timedelta(seconds=duration_seconds)
        logger.warning(f"🚫 Заблокирован ключ {key} на {duration_seconds} секунд")
    
    def reset(self, key: str):
        """Сброс лимитов для ключа"""
        if key in self._requests:
            del self._requests[key]
        if key in self._blocked:
            del self._blocked[key]


# ============================================================================
# RATE LIMITER CLASS
# ============================================================================

class RateLimiter:
    """Класс для настройки rate limiting"""
    
    # Лимиты по умолчанию
    DEFAULT_LIMITS = {
        "default": (100, 60),      # 100 запросов в минуту
        "auth": (10, 60),          # 10 запросов в минуту для авторизации
        "api": (60, 60),           # 60 запросов в минуту для API
        "game": (120, 60),         # 120 запросов в минуту для игры
        "websocket": (1000, 60),   # 1000 запросов в минуту для WebSocket
    }
    
    def __init__(self):
        self.limiter = InMemoryRateLimiter()
        self.custom_limits: Dict[str, Tuple[int, int]] = {}
    
    def get_limit(self, endpoint_type: str) -> Tuple[int, int]:
        """Получение лимита для типа endpoint"""
        if endpoint_type in self.custom_limits:
            return self.custom_limits[endpoint_type]
        return self.DEFAULT_LIMITS.get(endpoint_type, self.DEFAULT_LIMITS["default"])
    
    def set_limit(self, endpoint_type: str, max_requests: int, window_seconds: int):
        """Установка пользовательского лимита"""
        self.custom_limits[endpoint_type] = (max_requests, window_seconds)
    
    def check(
        self, 
        client_id: str, 
        endpoint_type: str = "default"
    ) -> Tuple[bool, int, int, int]:
        """
        Проверка лимита
        
        Returns:
            Кортеж (разрешено, оставшиеся_запросы, лимит, время_до_сброса)
        """
        max_requests, window = self.get_limit(endpoint_type)
        key = f"{endpoint_type}:{client_id}"
        
        allowed, remaining, reset_time = self.limiter.is_allowed(
            key, max_requests, window
        )
        
        return allowed, remaining, max_requests, reset_time
    
    def block_client(self, client_id: str, duration_seconds: int = 300):
        """Блокировка клиента"""
        self.limiter.block(client_id, duration_seconds)


# ============================================================================
# RATE LIMIT MIDDLEWARE
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware для rate limiting
    
    Добавляет заголовки X-RateLimit-* к ответам
    и блокирует клиентов, превышающих лимиты
    """
    
    def __init__(
        self, 
        app,
        rate_limiter: Optional[RateLimiter] = None,
        get_client_id: Optional[Callable[[Request], str]] = None
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.get_client_id = get_client_id or self._default_client_id
    
    def _default_client_id(self, request: Request) -> str:
        """Получение ID клиента по умолчанию (IP адрес)"""
        # Проверка X-Forwarded-For для проксированных запросов
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Проверка X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Использование client.host
        return request.client.host if request.client else "unknown"
    
    def _get_endpoint_type(self, request: Request) -> str:
        """Определение типа endpoint по пути"""
        path = request.url.path.lower()
        
        if "/auth/" in path or path.startswith("/api/auth"):
            return "auth"
        elif "/game/" in path or path.startswith("/api/game"):
            return "game"
        elif path.startswith("/ws") or "websocket" in path:
            return "websocket"
        elif path.startswith("/api"):
            return "api"
        else:
            return "default"
    
    def _is_exempt(self, request: Request) -> bool:
        """Проверка исключения из rate limiting"""
        path = request.url.path.lower()
        
        # Исключения: health checks, документация, статика
        exempt_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static",
        ]
        
        return any(path.startswith(exempt) for exempt in exempt_paths)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса"""
        
        # Пропуск исключённых путей
        if self._is_exempt(request):
            return await call_next(request)
        
        # Получение ID клиента и типа endpoint
        client_id = self.get_client_id(request)
        endpoint_type = self._get_endpoint_type(request)
        
        # Проверка лимита
        allowed, remaining, limit, reset_time = self.rate_limiter.check(
            client_id, endpoint_type
        )
        
        # Заголовки rate limit
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }
        
        if not allowed:
            logger.warning(
                f"⚠️ Rate limit exceeded for {client_id} on {endpoint_type}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "message": "Превышен лимит запросов",
                    "detail": {
                        "limit": limit,
                        "remaining": remaining,
                        "reset_after": reset_time
                    }
                },
                headers={
                    **headers,
                    "Retry-After": str(reset_time)
                }
            )
        
        # Выполнение запроса
        response = await call_next(request)
        
        # Добавление заголовков к ответу
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# ============================================================================
# DECORATOR FOR RATE LIMITING
# ============================================================================

def rate_limit(
    max_requests: int = 60,
    window_seconds: int = 60,
    key_func: Optional[Callable] = None
):
    """
    Декоратор для rate limiting отдельных endpoint'ов
    
    Usage:
        @router.get("/endpoint")
        @rate_limit(max_requests=10, window_seconds=60)
        async def my_endpoint(request: Request):
            ...
    """
    def decorator(func):
        # В FastAPI лучше использовать middleware, но это может быть полезно
        # для особых случаев
        func._rate_limit = {
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "key_func": key_func
        }
        return func
    return decorator


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()
