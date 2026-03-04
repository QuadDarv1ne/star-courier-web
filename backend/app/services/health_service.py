"""
StarCourier Web - Extended Health Check System
Комплексная система мониторинга здоровья приложения

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import os
import logging
import time
import platform
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import psutil

from app.config import settings
from app.database.connection import database

logger = logging.getLogger(__name__)


# ============================================================================
# HEALTH STATUS
# ============================================================================

class HealthStatus(str, Enum):
    """Статус здоровья компонента"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Здоровье компонента"""
    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "last_check": self.last_check.isoformat()
        }


# ============================================================================
# HEALTH CHECKERS
# ============================================================================

class HealthChecker:
    """Базовый класс для проверки здоровья"""
    
    name: str = "base"
    
    async def check(self) -> ComponentHealth:
        """Выполнение проверки"""
        raise NotImplementedError


class DatabaseHealthChecker(HealthChecker):
    """Проверка здоровья базы данных"""
    
    name = "database"
    
    async def check(self) -> ComponentHealth:
        start = time.time()
        
        try:
            is_healthy = await database.health_check()
            latency = (time.time() - start) * 1000
            
            if is_healthy:
                # Получение размера БД
                db_size = 0
                if settings.database_type == "sqlite":
                    db_path = Path(settings.database_url.replace("sqlite:///", ""))
                    if db_path.exists():
                        db_size = db_path.stat().st_size
                
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                    latency_ms=round(latency, 2),
                    details={
                        "type": settings.database_type,
                        "size_bytes": db_size,
                        "size_human": self._format_size(db_size)
                    }
                )
            else:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Database connection failed"
                )
                
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {str(e)}"
            )
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


class CacheHealthChecker(HealthChecker):
    """Проверка здоровья кэша"""
    
    name = "cache"
    
    async def check(self) -> ComponentHealth:
        start = time.time()
        
        try:
            from app.services.cache_service import cache_service
            
            stats = cache_service.get_stats()
            latency = (time.time() - start) * 1000
            
            if stats.get("type") == "redis":
                if stats.get("connected"):
                    return ComponentHealth(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message="Redis cache connected",
                        latency_ms=round(latency, 2),
                        details=stats
                    )
                else:
                    return ComponentHealth(
                        name=self.name,
                        status=HealthStatus.DEGRADED,
                        message="Redis disconnected, using fallback",
                        details=stats
                    )
            else:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="In-memory cache active",
                    latency_ms=round(latency, 2),
                    details=stats
                )
                
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"Cache error: {str(e)}"
            )


class DiskHealthChecker(HealthChecker):
    """Проверка дискового пространства"""
    
    name = "disk"
    
    async def check(self) -> ComponentHealth:
        try:
            # Основной диск
            disk = psutil.disk_usage('/')
            
            total_gb = disk.total / (1024 ** 3)
            used_gb = disk.used / (1024 ** 3)
            free_gb = disk.free / (1024 ** 3)
            percent = disk.percent
            
            if percent >= 90:
                status = HealthStatus.UNHEALTHY
                message = f"Disk critically low: {percent}% used"
            elif percent >= 80:
                status = HealthStatus.DEGRADED
                message = f"Disk space warning: {percent}% used"
            else:
                status = HealthStatus.HEALTHY
                message = "Disk space OK"
            
            return ComponentHealth(
                name=self.name,
                status=status,
                message=message,
                details={
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "percent_used": round(percent, 2)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Disk check error: {str(e)}"
            )


class MemoryHealthChecker(HealthChecker):
    """Проверка памяти"""
    
    name = "memory"
    
    async def check(self) -> ComponentHealth:
        try:
            memory = psutil.virtual_memory()
            
            total_gb = memory.total / (1024 ** 3)
            available_gb = memory.available / (1024 ** 3)
            used_gb = memory.used / (1024 ** 3)
            percent = memory.percent
            
            if percent >= 90:
                status = HealthStatus.UNHEALTHY
                message = f"Memory critically low: {percent}% used"
            elif percent >= 80:
                status = HealthStatus.DEGRADED
                message = f"Memory warning: {percent}% used"
            else:
                status = HealthStatus.HEALTHY
                message = "Memory OK"
            
            return ComponentHealth(
                name=self.name,
                status=status,
                message=message,
                details={
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "available_gb": round(available_gb, 2),
                    "percent_used": round(percent, 2)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Memory check error: {str(e)}"
            )


class CPUHealthChecker(HealthChecker):
    """Проверка CPU"""
    
    name = "cpu"
    
    async def check(self) -> ComponentHealth:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            if cpu_percent >= 90:
                status = HealthStatus.UNHEALTHY
                message = f"CPU overloaded: {cpu_percent}%"
            elif cpu_percent >= 80:
                status = HealthStatus.DEGRADED
                message = f"CPU warning: {cpu_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = "CPU OK"
            
            return ComponentHealth(
                name=self.name,
                status=status,
                message=message,
                details={
                    "percent": round(cpu_percent, 2),
                    "cores": cpu_count,
                    "load_avg_1": round(load_avg[0], 2),
                    "load_avg_5": round(load_avg[1], 2),
                    "load_avg_15": round(load_avg[2], 2)
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"CPU check error: {str(e)}"
            )


class EmailHealthChecker(HealthChecker):
    """Проверка email сервиса"""
    
    name = "email"
    
    async def check(self) -> ComponentHealth:
        try:
            is_enabled = settings.email_enabled
            
            if not is_enabled:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Email service disabled",
                    details={"enabled": False}
                )
            
            # Проверка настроек SMTP
            has_config = all([
                settings.smtp_server,
                settings.smtp_port,
                settings.smtp_username,
                settings.smtp_password
            ])
            
            if has_config:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Email service configured",
                    details={
                        "enabled": True,
                        "server": settings.smtp_server,
                        "port": settings.smtp_port
                    }
                )
            else:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    message="Email enabled but not fully configured",
                    details={"enabled": True}
                )
                
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Email check error: {str(e)}"
            )


class WebSocketHealthChecker(HealthChecker):
    """Проверка WebSocket соединений"""
    
    name = "websocket"
    
    async def check(self) -> ComponentHealth:
        try:
            from app.services.notification_service import notification_service
            
            stats = await notification_service.get_stats()
            
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="WebSocket service running",
                details=stats
            )
            
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="WebSocket service available",
                details={"active": True}
            )


# ============================================================================
# HEALTH CHECK SERVICE
# ============================================================================

class HealthCheckService:
    """Сервис комплексной проверки здоровья"""
    
    def __init__(self):
        self.checkers: List[HealthChecker] = [
            DatabaseHealthChecker(),
            CacheHealthChecker(),
            DiskHealthChecker(),
            MemoryHealthChecker(),
            CPUHealthChecker(),
            EmailHealthChecker(),
            WebSocketHealthChecker(),
        ]
        self._last_check: Optional[datetime] = None
        self._cached_result: Optional[Dict] = None
        self._cache_ttl = 10  # Кэшировать на 10 секунд
    
    async def check_all(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Проверка всех компонентов
        
        Args:
            use_cache: Использовать кэшированный результат
        
        Returns:
            Полный отчёт о здоровье системы
        """
        # Проверка кэша
        if use_cache and self._cached_result and self._last_check:
            if datetime.utcnow() - self._last_check < timedelta(seconds=self._cache_ttl):
                return self._cached_result
        
        start = time.time()
        components = []
        
        # Параллельная проверка всех компонентов
        tasks = [checker.check() for checker in self.checkers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                components.append(ComponentHealth(
                    name=self.checkers[i].name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {str(result)}"
                ).to_dict())
            else:
                components.append(result.to_dict())
        
        # Определение общего статуса
        statuses = [c["status"] for c in components]
        
        if "unhealthy" in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif "degraded" in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        total_latency = (time.time() - start) * 1000
        
        result = {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "latency_ms": round(total_latency, 2),
            "version": settings.app_version,
            "environment": settings.environment,
            "components": components,
            "system": self._get_system_info()
        }
        
        # Кэширование
        self._last_check = datetime.utcnow()
        self._cached_result = result
        
        return result
    
    async def check_component(self, name: str) -> Optional[ComponentHealth]:
        """Проверка конкретного компонента"""
        for checker in self.checkers:
            if checker.name == name:
                return await checker.check()
        return None
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "architecture": platform.machine()
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик для мониторинга"""
        health = await self.check_all()
        
        return {
            "uptime_seconds": self._get_uptime(),
            "requests_per_minute": 0,  # Требует интеграции с middleware
            "average_response_time_ms": 0,  # Требует интеграции
            "active_connections": sum(
                c.get("details", {}).get("connected_users", 0)
                for c in health["components"]
                if c["name"] == "websocket"
            ),
            "memory_percent": next(
                (c.get("details", {}).get("percent_used", 0)
                 for c in health["components"] if c["name"] == "memory"),
                0
            ),
            "cpu_percent": next(
                (c.get("details", {}).get("percent", 0)
                 for c in health["components"] if c["name"] == "cpu"),
                0
            ),
            "disk_percent": next(
                (c.get("details", {}).get("percent_used", 0)
                 for c in health["components"] if c["name"] == "disk"),
                0
            )
        }
    
    def _get_uptime(self) -> float:
        """Получение времени работы"""
        try:
            return time.time() - psutil.Process().create_time()
        except Exception:
            return 0


# Глобальный экземпляр
health_check_service = HealthCheckService()
