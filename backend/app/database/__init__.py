"""
StarCourier Web - Database Package
Пакет для работы с базой данных

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from app.database.connection import get_db, database, init_db, close_db
from app.database.models import Base, User, PlayerStats, GameSession, Achievement, AnalyticsEvent

__all__ = [
    "get_db",
    "database",
    "init_db",
    "close_db",
    "Base",
    "User",
    "PlayerStats",
    "GameSession",
    "Achievement",
    "AnalyticsEvent"
]
