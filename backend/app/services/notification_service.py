"""
StarCourier Web - Notification Service
Сервис уведомлений в реальном времени

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from fastapi import WebSocket

logger = logging.getLogger(__name__)


# ============================================================================
# NOTIFICATION TYPES
# ============================================================================

class NotificationType(str, Enum):
    """Типы уведомлений"""
    # Системные
    SYSTEM = "system"
    MAINTENANCE = "maintenance"
    UPDATE = "update"
    
    # Игровые
    ACHIEVEMENT = "achievement"
    LEVEL_UP = "level_up"
    GAME_INVITE = "game_invite"
    GAME_START = "game_start"
    GAME_END = "game_end"
    
    # Социальные
    FRIEND_REQUEST = "friend_request"
    FRIEND_ONLINE = "friend_online"
    MESSAGE = "message"
    
    # Лидерборд
    RANK_CHANGE = "rank_change"
    NEW_LEADER = "new_leader"
    
    # Администрация
    WARNING = "warning"
    BAN = "ban"
    KICK = "kick"
    
    # Другое
    ANNOUNCEMENT = "announcement"
    PROMOTION = "promotion"


class NotificationPriority(str, Enum):
    """Приоритет уведомления"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# ============================================================================
# NOTIFICATION MODEL
# ============================================================================

@dataclass
class Notification:
    """Модель уведомления"""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    read: bool = False
    read_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "read": self.read,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }


# ============================================================================
# CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        # user_id -> set of WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}
        # user_id -> list of pending notifications
        self._pending: Dict[str, List[Notification]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Принятие нового соединения"""
        await websocket.accept()
        
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(websocket)
        
        logger.info(f"🔌 User {user_id} connected ({len(self._connections[user_id])} connections)")
        
        # Отправка отложенных уведомлений
        await self._send_pending(user_id)
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Обработка отключения"""
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(websocket)
                if not self._connections[user_id]:
                    del self._connections[user_id]
        
        logger.info(f"🔌 User {user_id} disconnected")
    
    async def is_connected(self, user_id: str) -> bool:
        """Проверка, подключён ли пользователь"""
        return user_id in self._connections and len(self._connections[user_id]) > 0
    
    async def get_connected_count(self) -> int:
        """Количество подключённых пользователей"""
        return len(self._connections)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """Отправка сообщения конкретному пользователю"""
        if user_id not in self._connections:
            return False
        
        disconnected = set()
        sent = False
        
        for websocket in self._connections[user_id]:
            try:
                await websocket.send_json(message)
                sent = True
            except Exception as e:
                logger.warning(f"Failed to send to {user_id}: {e}")
                disconnected.add(websocket)
        
        # Удаление отключённых соединений
        async with self._lock:
            self._connections[user_id] -= disconnected
            if not self._connections[user_id]:
                del self._connections[user_id]
        
        return sent
    
    async def broadcast(self, message: Dict[str, Any], exclude: Set[str] = None):
        """Широковещательная отправка всем пользователям"""
        exclude = exclude or set()
        
        for user_id in list(self._connections.keys()):
            if user_id not in exclude:
                await self.send_to_user(user_id, message)
    
    async def _send_pending(self, user_id: str):
        """Отправка отложенных уведомлений"""
        if user_id not in self._pending:
            return
        
        notifications = self._pending.pop(user_id, [])
        
        for notification in notifications:
            await self.send_to_user(user_id, {
                "type": "notification",
                "data": notification.to_dict()
            })
    
    async def store_pending(self, user_id: str, notification: Notification):
        """Сохранение уведомления для офлайн пользователя"""
        if user_id not in self._pending:
            self._pending[user_id] = []
        
        # Ограничение количества отложенных уведомлений
        if len(self._pending[user_id]) >= 100:
            self._pending[user_id].pop(0)
        
        self._pending[user_id].append(notification)


# ============================================================================
# NOTIFICATION SERVICE
# ============================================================================

class NotificationService:
    """Сервис уведомлений"""
    
    def __init__(self):
        self.manager = ConnectionManager()
        self._notification_counter = 0
    
    def _generate_id(self) -> str:
        """Генерация ID уведомления"""
        self._notification_counter += 1
        return f"notif_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{self._notification_counter}"
    
    async def send_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Dict[str, Any] = None
    ) -> Notification:
        """
        Отправка уведомления пользователю
        
        Args:
            user_id: ID пользователя
            type: Тип уведомления
            title: Заголовок
            message: Сообщение
            priority: Приоритет
            data: Дополнительные данные
        
        Returns:
            Созданное уведомление
        """
        notification = Notification(
            id=self._generate_id(),
            type=type,
            title=title,
            message=message,
            priority=priority,
            data=data or {}
        )
        
        # Проверка подключения
        if await self.manager.is_connected(user_id):
            await self.manager.send_to_user(user_id, {
                "type": "notification",
                "data": notification.to_dict()
            })
            logger.info(f"📨 Notification sent to {user_id}: {title}")
        else:
            # Сохранение для позже
            await self.manager.store_pending(user_id, notification)
            logger.info(f"📨 Notification stored for offline user {user_id}: {title}")
        
        return notification
    
    async def broadcast_notification(
        self,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Dict[str, Any] = None,
        exclude: Set[str] = None
    ):
        """
        Широковещательная отправка уведомления
        """
        notification = Notification(
            id=self._generate_id(),
            type=type,
            title=title,
            message=message,
            priority=priority,
            data=data or {}
        )
        
        await self.manager.broadcast({
            "type": "notification",
            "data": notification.to_dict()
        }, exclude)
        
        logger.info(f"📢 Broadcast notification: {title}")
    
    async def send_to_multiple(
        self,
        user_ids: List[str],
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Dict[str, Any] = None
    ):
        """Отправка уведомления нескольким пользователям"""
        for user_id in user_ids:
            await self.send_notification(
                user_id, type, title, message, priority, data
            )
    
    # ========================================================================
    # СПЕЦИАЛИЗИРОВАННЫЕ МЕТОДЫ
    # ========================================================================
    
    async def notify_achievement(
        self,
        user_id: str,
        achievement_name: str,
        achievement_description: str,
        points: int
    ):
        """Уведомление о достижении"""
        return await self.send_notification(
            user_id,
            NotificationType.ACHIEVEMENT,
            "🎖️ Новое достижение!",
            f"{achievement_name}: {achievement_description}",
            NotificationPriority.HIGH,
            {
                "achievement_name": achievement_name,
                "points": points
            }
        )
    
    async def notify_rank_change(
        self,
        user_id: str,
        old_rank: int,
        new_rank: int
    ):
        """Уведомление об изменении ранга"""
        direction = "повысился" if new_rank < old_rank else "понизился"
        return await self.send_notification(
            user_id,
            NotificationType.RANK_CHANGE,
            f"🏆 Рейтинг {direction}!",
            f"Ваше место: #{new_rank} (было #{old_rank})",
            NotificationPriority.NORMAL,
            {"old_rank": old_rank, "new_rank": new_rank}
        )
    
    async def notify_system(
        self,
        user_id: str,
        title: str,
        message: str
    ):
        """Системное уведомление"""
        return await self.send_notification(
            user_id,
            NotificationType.SYSTEM,
            title,
            message,
            NotificationPriority.NORMAL
        )
    
    async def notify_warning(
        self,
        user_id: str,
        message: str,
        reason: str = None
    ):
        """Предупреждение"""
        return await self.send_notification(
            user_id,
            NotificationType.WARNING,
            "⚠️ Предупреждение",
            message,
            NotificationPriority.HIGH,
            {"reason": reason}
        )
    
    async def notify_announcement(
        self,
        title: str,
        message: str,
        data: Dict[str, Any] = None
    ):
        """Объявление всем пользователям"""
        return await self.broadcast_notification(
            NotificationType.ANNOUNCEMENT,
            f"📢 {title}",
            message,
            NotificationPriority.HIGH,
            data
        )
    
    async def notify_maintenance(
        self,
        message: str,
        scheduled_time: datetime = None
    ):
        """Уведомление о техработах"""
        return await self.broadcast_notification(
            NotificationType.MAINTENANCE,
            "🔧 Технические работы",
            message,
            NotificationPriority.URGENT,
            {"scheduled_time": scheduled_time.isoformat() if scheduled_time else None}
        )
    
    # ========================================================================
    # СТАТИСТИКА
    # ========================================================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики соединений"""
        return {
            "connected_users": await self.manager.get_connected_count(),
            "total_connections": sum(
                len(conns) for conns in self.manager._connections.values()
            ),
            "pending_notifications": sum(
                len(notifs) for notifs in self.manager._pending.values()
            )
        }


# Глобальный экземпляр
notification_service = NotificationService()
