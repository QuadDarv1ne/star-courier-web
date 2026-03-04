"""
StarCourier Web - Database Models
SQLAlchemy модели для базы данных

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def to_dict(self):
        """Преобразование модели в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TimestampMixin:
    """Миксин для временных меток"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Профиль
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Статистика
    games_played = Column(Integer, default=0)
    games_completed = Column(Integer, default=0)
    total_playtime = Column(Integer, default=0)  # в минутах
    achievements_count = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    
    # Настройки
    language = Column(String(5), default="ru")
    theme = Column(String(20), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    sound_enabled = Column(Boolean, default=True)
    music_volume = Column(Integer, default=80)
    sfx_volume = Column(Integer, default=100)
    
    # Статус
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    # Связи
    player_stats = relationship("PlayerStats", back_populates="user", cascade="all, delete-orphan")
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    
    # Индексы
    __table_args__ = (
        Index('ix_users_username_lower', username),
        Index('ix_users_email_lower', email),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class PlayerStats(Base, TimestampMixin):
    """Статистика игрока по играм"""
    __tablename__ = "player_stats"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Состояние игры
    current_scene = Column(String(100), default="start")
    stats = Column(JSON, default=dict)
    relationships = Column(JSON, default=dict)
    inventory = Column(JSON, default=list)
    flags = Column(JSON, default=dict)
    
    # Прогресс
    choices_made = Column(Integer, default=0)
    visited_scenes = Column(JSON, default=list)
    achievements_unlocked = Column(JSON, default=list)
    
    # Результаты
    playtime = Column(Integer, default=0)  # в секундах
    ending_type = Column(String(50), nullable=True)
    score = Column(Integer, default=0)
    
    # Связи
    user = relationship("User", back_populates="player_stats")
    
    def __repr__(self):
        return f"<PlayerStats(id={self.id}, user_id={self.user_id})>"


class GameSession(Base):
    """Сессия игры"""
    __tablename__ = "game_sessions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player_stats_id = Column(String(36), ForeignKey("player_stats.id", ondelete="SET NULL"), nullable=True)
    
    # Состояние
    status = Column(String(20), default="active")  # active, paused, completed, abandoned
    current_scene = Column(String(100), default="start")
    
    # Время
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Результаты
    ending_type = Column(String(50), nullable=True)
    score = Column(Integer, default=0)
    choices_count = Column(Integer, default=0)
    
    # Метаданные
    device_info = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Связи
    user = relationship("User", back_populates="game_sessions")
    
    # Индексы
    __table_args__ = (
        Index('ix_game_sessions_user_status', user_id, status),
        Index('ix_game_sessions_started', started_at),
    )
    
    def __repr__(self):
        return f"<GameSession(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Achievement(Base):
    """Достижения пользователей"""
    __tablename__ = "user_achievements"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(String(100), nullable=False)  # ID достижения из achievements.json
    
    # Время получения
    unlocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Метаданные
    scene = Column(String(100), nullable=True)  # Сцена, где получено
    progress = Column(Integer, default=100)  # Прогресс (для многоуровневых достижений)
    
    # Связи
    user = relationship("User", back_populates="achievements")
    
    # Индексы
    __table_args__ = (
        Index('ix_user_achievements_user_achievement', user_id, achievement_id, unique=True),
    )
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, user_id={self.user_id}, achievement_id={self.achievement_id})>"


class AnalyticsEvent(Base):
    """События аналитики"""
    __tablename__ = "analytics_events"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(36), ForeignKey("game_sessions.id", ondelete="SET NULL"), nullable=True)
    
    # Событие
    event_type = Column(String(50), nullable=False, index=True)  # scene_visit, choice_made, achievement_unlocked, etc.
    event_name = Column(String(100), nullable=False)
    event_category = Column(String(50), default="gameplay")
    
    # Данные
    event_data = Column(JSON, default=dict)
    
    # Контекст
    scene = Column(String(100), nullable=True)
    choice_id = Column(String(100), nullable=True)
    
    # Время
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Устройство
    device_type = Column(String(20), nullable=True)  # desktop, mobile, tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Индексы
    __table_args__ = (
        Index('ix_analytics_events_type_timestamp', event_type, timestamp),
        Index('ix_analytics_events_user_timestamp', user_id, timestamp),
    )
    
    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, type={self.event_type}, name={self.event_name})>"


class RateLimitEntry(Base):
    """Записи для rate limiting"""
    __tablename__ = "rate_limits"
    
    id = Column(String(36), primary_key=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    count = Column(Integer, default=1)
    reset_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RateLimitEntry(key={self.key}, count={self.count})>"


class LeaderboardEntry(Base):
    """Записи таблицы лидеров (материализованный вид)"""
    __tablename__ = "leaderboard_entries"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Рейтинг
    rank = Column(Integer, nullable=False, index=True)
    score = Column(Integer, default=0, nullable=False, index=True)
    
    # Статистика
    games_completed = Column(Integer, default=0)
    total_playtime = Column(Integer, default=0)
    achievements_count = Column(Integer, default=0)
    
    # Время
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Индексы
    __table_args__ = (
        Index('ix_leaderboard_rank', rank),
        Index('ix_leaderboard_score', score.desc()),
    )
    
    def __repr__(self):
        return f"<LeaderboardEntry(user_id={self.user_id}, rank={self.rank}, score={self.score})>"


class GameContent(Base):
    """Кэшированный контент игры (сцены, персонажи)"""
    __tablename__ = "game_content"
    
    id = Column(String(36), primary_key=True)
    content_type = Column(String(20), nullable=False)  # scene, character, achievement
    content_id = Column(String(100), nullable=False)  # ID из JSON
    content_data = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Индексы
    __table_args__ = (
        Index('ix_game_content_type_id', content_type, content_id, unique=True),
    )
    
    def __repr__(self):
        return f"<GameContent(type={self.content_type}, id={self.content_id})>"
