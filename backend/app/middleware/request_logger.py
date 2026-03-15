"""
StarCourier Web - Request Logger Middleware
Middleware для логирования запросов

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
import time
import json
from typing import Callable
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов

    Логирует:
    - Метод и путь запроса
    - Время обработки
    - Статус ответа
    - IP клиента
    - User-Agent
    """

    # Пути, которые не нужно логировать
    SKIP_PATHS: set = {
        "/health",
        "/metrics",
        "/favicon.ico",
    }

    # Чувствительные заголовки, которые нужно скрыть
    SENSITIVE_HEADERS: set = {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "x-auth-token",
    }

    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        skip_paths: set = None
    ) -> None:
        super().__init__(app)
        self.log_request_body: bool = log_request_body
        self.log_response_body: bool = log_response_body
        self.skip_paths: set = skip_paths or self.SKIP_PATHS

    def _get_client_ip(self, request: Request) -> str:
        """Получение IP клиента"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _sanitize_headers(self, headers: dict) -> dict:
        """Скрытие чувствительных заголовков"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.SENSITIVE_HEADERS:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized
    
    def _should_skip(self, path: str) -> bool:
        """Проверка необходимости пропуска логирования"""
        return any(path.startswith(skip) for skip in self.skip_paths)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса"""
        
        # Пропуск определённых путей
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        # Начало отсчёта времени
        start_time = time.time()
        
        # Сбор информации о запросе
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Логирование запроса
        log_data = {
            "type": "request",
            "method": method,
            "path": path,
            "query": query,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.log_request_body and method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    log_data["body_size"] = len(body)
            except Exception:
                pass
        
        logger.info(f"📥 {method} {path} - Client: {client_ip}")
        
        # Выполнение запроса
        try:
            response = await call_next(request)
            
            # Вычисление времени обработки
            process_time = time.time() - start_time
            
            # Логирование ответа
            log_data.update({
                "type": "response",
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2)
            })
            
            # Определение уровня логирования по статусу
            status_code = response.status_code
            if status_code < 400:
                log_level = logging.INFO
                emoji = "📤"
            elif status_code < 500:
                log_level = logging.WARNING
                emoji = "⚠️"
            else:
                log_level = logging.ERROR
                emoji = "❌"
            
            logger.log(
                log_level,
                f"{emoji} {method} {path} - {status_code} - "
                f"{process_time*1000:.2f}ms - Client: {client_ip}"
            )
            
            # Добавление заголовка с временем обработки
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as e:
            # Логирование ошибок
            process_time = time.time() - start_time
            logger.error(
                f"❌ {method} {path} - Error: {str(e)} - "
                f"{process_time*1000:.2f}ms - Client: {client_ip}"
            )
            raise
