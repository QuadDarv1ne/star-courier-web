"""
StarCourier Web - Performance Monitoring Middleware
Middleware для мониторинга производительности запросов

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ============================================================================
# METRICS DATA STRUCTURES
# ============================================================================

@dataclass
class RequestMetric:
    """Метрика запроса"""
    path: str
    method: str
    status_code: int
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    error: Optional[str] = None


@dataclass
class EndpointStats:
    """Статистика endpoint"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0
    last_request: Optional[datetime] = None
    
    @property
    def avg_duration_ms(self) -> float:
        if self.total_requests == 0:
            return 0
        return self.total_duration_ms / self.total_requests
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100


class PerformanceMetrics:
    """Хранилище метрик производительности"""

    def __init__(self, max_metrics: int = 10000) -> None:
        self._metrics: List[RequestMetric] = []
        self._endpoint_stats: Dict[str, EndpointStats] = defaultdict(EndpointStats)
        self._max_metrics: int = max_metrics
        self._slow_requests: List[RequestMetric] = []
        self._slow_threshold_ms: int = 1000  # Запросы медленнее 1 сек

    def add_metric(self, metric: RequestMetric) -> None:
        """Добавление метрики"""
        # Основное хранилище
        self._metrics.append(metric)
        if len(self._metrics) > self._max_metrics:
            self._metrics.pop(0)
        
        # Статистика по endpoint
        endpoint_key = f"{metric.method}:{metric.path}"
        stats = self._endpoint_stats[endpoint_key]
        stats.total_requests += 1
        stats.total_duration_ms += metric.duration_ms
        stats.min_duration_ms = min(stats.min_duration_ms, metric.duration_ms)
        stats.max_duration_ms = max(stats.max_duration_ms, metric.duration_ms)
        stats.last_request = metric.timestamp
        
        if metric.status_code < 400:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        # Медленные запросы
        if metric.duration_ms > self._slow_threshold_ms:
            self._slow_requests.append(metric)
            if len(self._slow_requests) > 100:
                self._slow_requests.pop(0)
    
    def get_stats(self) -> Dict:
        """Получение общей статистики"""
        if not self._metrics:
            return {
                "total_requests": 0,
                "avg_duration_ms": 0,
                "requests_per_minute": 0
            }
        
        # Расчёт запросов в минуту
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = sum(
            1 for m in self._metrics
            if m.timestamp >= one_minute_ago
        )
        
        return {
            "total_requests": len(self._metrics),
            "avg_duration_ms": round(
                sum(m.duration_ms for m in self._metrics) / len(self._metrics), 2
            ),
            "requests_per_minute": recent_requests,
            "slow_requests_count": len(self._slow_requests),
            "endpoints_tracked": len(self._endpoint_stats)
        }
    
    def get_endpoint_stats(self, path: str = None) -> Dict:
        """Получение статистики по endpoints"""
        if path:
            endpoint_key = path
            if endpoint_key in self._endpoint_stats:
                stats = self._endpoint_stats[endpoint_key]
                return {
                    "endpoint": endpoint_key,
                    "total_requests": stats.total_requests,
                    "successful_requests": stats.successful_requests,
                    "failed_requests": stats.failed_requests,
                    "success_rate": round(stats.success_rate, 2),
                    "avg_duration_ms": round(stats.avg_duration_ms, 2),
                    "min_duration_ms": round(stats.min_duration_ms, 2) if stats.min_duration_ms != float('inf') else 0,
                    "max_duration_ms": round(stats.max_duration_ms, 2),
                    "last_request": stats.last_request.isoformat() if stats.last_request else None
                }
            return {}
        
        return {
            endpoint: {
                "total_requests": stats.total_requests,
                "avg_duration_ms": round(stats.avg_duration_ms, 2),
                "success_rate": round(stats.success_rate, 2)
            }
            for endpoint, stats in sorted(
                self._endpoint_stats.items(),
                key=lambda x: x[1].total_requests,
                reverse=True
            )
        }
    
    def get_slow_requests(self, limit: int = 10) -> List[Dict]:
        """Получение списка медленных запросов"""
        sorted_slow = sorted(
            self._slow_requests,
            key=lambda x: x.duration_ms,
            reverse=True
        )[:limit]
        
        return [
            {
                "path": m.path,
                "method": m.method,
                "duration_ms": round(m.duration_ms, 2),
                "status_code": m.status_code,
                "timestamp": m.timestamp.isoformat()
            }
            for m in sorted_slow
        ]
    
    def get_hourly_distribution(self) -> Dict[str, int]:
        """Получение распределения запросов по часам"""
        distribution = defaultdict(int)
        
        for metric in self._metrics:
            hour = metric.timestamp.strftime("%Y-%m-%d %H:00")
            distribution[hour] += 1
        
        return dict(sorted(distribution.items()))
    
    def clear_old_metrics(self, hours: int = 24):
        """Очистка старых метрик"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self._metrics = [m for m in self._metrics if m.timestamp >= cutoff]
        self._slow_requests = [m for m in self._slow_requests if m.timestamp >= cutoff]


# Глобальное хранилище метрик
metrics = PerformanceMetrics()


# ============================================================================
# PERFORMANCE MIDDLEWARE
# ============================================================================

class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware для мониторинга производительности
    
    Собирает метрики:
    - Время выполнения запросов
    - Статистику по endpoints
    - Медленные запросы
    - Распределение по времени
    """
    
    def __init__(
        self,
        app,
        slow_threshold_ms: int = 1000,
        exclude_paths: set = None
    ):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        self.exclude_paths = exclude_paths or {"/health", "/metrics", "/favicon.ico"}
    
    def _should_track(self, path: str) -> bool:
        """Проверка необходимости отслеживания"""
        return not any(path.startswith(excluded) for excluded in self.exclude_paths)
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение IP клиента"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса"""
        path = request.url.path
        
        # Пропуск исключённых путей
        if not self._should_track(path):
            return await call_next(request)
        
        # Начало отсчёта
        start_time = time.time()
        error = None
        
        try:
            response = await call_next(request)
            
        except Exception as e:
            error = str(e)
            raise
        
        finally:
            # Расчёт времени
            duration_ms = (time.time() - start_time) * 1000
            
            # Создание метрики
            metric = RequestMetric(
                path=path,
                method=request.method,
                status_code=response.status_code if 'response' in locals() else 500,
                duration_ms=duration_ms,
                user_agent=request.headers.get("User-Agent"),
                ip_address=self._get_client_ip(request),
                error=error
            )
            
            # Сохранение метрики
            metrics.add_metric(metric)
            
            # Добавление заголовка с временем
            if 'response' in locals():
                response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
                
                # Предупреждение для медленных запросов
                if duration_ms > self.slow_threshold_ms:
                    logger.warning(
                        f"⚠️ Slow request: {request.method} {path} - {duration_ms:.2f}ms"
                    )
        
        return response


# ============================================================================
# METRICS API
# ============================================================================

def get_performance_stats() -> Dict:
    """Получение статистики производительности"""
    return {
        "overview": metrics.get_stats(),
        "endpoints": metrics.get_endpoint_stats(),
        "slow_requests": metrics.get_slow_requests(),
        "hourly_distribution": metrics.get_hourly_distribution()
    }


def reset_metrics():
    """Сброс всех метрик"""
    global metrics
    metrics = PerformanceMetrics()
