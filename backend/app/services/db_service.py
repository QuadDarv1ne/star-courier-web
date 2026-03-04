"""
StarCourier Web - Database Service
Сервис для работы с базой данных

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, update, delete, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    User, PlayerStats, GameSession, Achievement, 
    AnalyticsEvent, LeaderboardEntry, RateLimitEntry
)
from app.database.connection import get_or_create

logger = logging.getLogger(__name__)


# ============================================================================
# USER SERVICE
# ============================================================================

class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: str,
        username: str,
        email: str,
        password_hash: str,
        **kwargs
    ) -> User:
        """Создание пользователя"""
        user = User(
            id=user_id,
            username=username.lower(),
            email=email.lower(),
            password_hash=password_hash,
            **kwargs
        )
        session.add(user)
        await session.flush()
        return user
    
    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
        """Получение пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        stmt = select(User).where(User.username == username.lower())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        stmt = select(User).where(User.email == email.lower())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update(session: AsyncSession, user_id: str, **kwargs) -> Optional[User]:
        """Обновление пользователя"""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**kwargs, updated_at=datetime.utcnow())
            .returning(User)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_last_login(session: AsyncSession, user_id: str) -> None:
        """Обновление времени последнего входа"""
        await UserService.update(session, user_id, last_login=datetime.utcnow())
    
    @staticmethod
    async def delete(session: AsyncSession, user_id: str) -> bool:
        """Удаление пользователя"""
        stmt = delete(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.rowcount > 0
    
    @staticmethod
    async def get_top_players(session: AsyncSession, limit: int = 10) -> List[User]:
        """Получение топ игроков"""
        stmt = (
            select(User)
            .where(User.is_active == True)
            .order_by(desc(User.total_score))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


# ============================================================================
# PLAYER STATS SERVICE
# ============================================================================

class PlayerStatsService:
    """Сервис для работы со статистикой игроков"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: str,
        player_id: str = None,
        **kwargs
    ) -> PlayerStats:
        """Создание записи статистики"""
        stats = PlayerStats(
            id=str(uuid.uuid4()),
            user_id=user_id,
            player_id=player_id or str(uuid.uuid4()),
            visited_scenes=["start"],
            **kwargs
        )
        session.add(stats)
        await session.flush()
        return stats
    
    @staticmethod
    async def get_by_player_id(session: AsyncSession, player_id: str) -> Optional[PlayerStats]:
        """Получение статистики по player_id"""
        stmt = select(PlayerStats).where(PlayerStats.player_id == player_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: str) -> List[PlayerStats]:
        """Получение всех статистик пользователя"""
        stmt = select(PlayerStats).where(PlayerStats.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_scene(
        session: AsyncSession,
        player_id: str,
        scene_id: str,
        add_to_visited: bool = True
    ) -> Optional[PlayerStats]:
        """Обновление текущей сцены"""
        stats = await PlayerStatsService.get_by_player_id(session, player_id)
        if not stats:
            return None
        
        stats.current_scene = scene_id
        if add_to_visited and scene_id not in stats.visited_scenes:
            stats.visited_scenes = stats.visited_scenes + [scene_id]
        
        await session.flush()
        return stats
    
    @staticmethod
    async def update_stats(
        session: AsyncSession,
        player_id: str,
        stats_update: Dict[str, Any]
    ) -> Optional[PlayerStats]:
        """Обновление статистики"""
        stats = await PlayerStatsService.get_by_player_id(session, player_id)
        if not stats:
            return None
        
        # Обновление базовых полей
        for field in ['current_scene', 'ending_type', 'score', 'playtime', 'choices_made']:
            if field in stats_update:
                setattr(stats, field, stats_update[field])
        
        # Обновление JSON полей
        for field in ['stats', 'relationships', 'inventory', 'flags', 'achievements_unlocked']:
            if field in stats_update:
                setattr(stats, field, stats_update[field])
        
        stats.updated_at = datetime.utcnow()
        await session.flush()
        return stats


# ============================================================================
# GAME SESSION SERVICE
# ============================================================================

class GameSessionService:
    """Сервис для работы с игровыми сессиями"""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: str,
        device_info: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> GameSession:
        """Создание игровой сессии"""
        game_session = GameSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            device_info=device_info or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        session.add(game_session)
        await session.flush()
        return game_session
    
    @staticmethod
    async def get_active(session: AsyncSession, user_id: str) -> Optional[GameSession]:
        """Получение активной сессии пользователя"""
        stmt = (
            select(GameSession)
            .where(
                and_(
                    GameSession.user_id == user_id,
                    GameSession.status == "active"
                )
            )
            .order_by(desc(GameSession.started_at))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def complete(
        session: AsyncSession,
        session_id: str,
        ending_type: str,
        score: int
    ) -> Optional[GameSession]:
        """Завершение игровой сессии"""
        stmt = (
            update(GameSession)
            .where(GameSession.id == session_id)
            .values(
                status="completed",
                ending_type=ending_type,
                score=score,
                completed_at=datetime.utcnow()
            )
            .returning(GameSession)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_sessions(
        session: AsyncSession,
        user_id: str,
        limit: int = 10
    ) -> List[GameSession]:
        """Получение сессий пользователя"""
        stmt = (
            select(GameSession)
            .where(GameSession.user_id == user_id)
            .order_by(desc(GameSession.started_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


# ============================================================================
# ACHIEVEMENT SERVICE
# ============================================================================

class AchievementService:
    """Сервис для работы с достижениями"""
    
    @staticmethod
    async def unlock(
        session: AsyncSession,
        user_id: str,
        achievement_id: str,
        scene: str = None
    ) -> Achievement:
        """Разблокировка достижения"""
        achievement = Achievement(
            id=str(uuid.uuid4()),
            user_id=user_id,
            achievement_id=achievement_id,
            scene=scene
        )
        session.add(achievement)
        
        # Обновление счётчика достижений пользователя
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(achievements_count=User.achievements_count + 1)
        )
        
        await session.flush()
        return achievement
    
    @staticmethod
    async def get_user_achievements(
        session: AsyncSession,
        user_id: str
    ) -> List[Achievement]:
        """Получение достижений пользователя"""
        stmt = (
            select(Achievement)
            .where(Achievement.user_id == user_id)
            .order_by(desc(Achievement.unlocked_at))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def has_achievement(
        session: AsyncSession,
        user_id: str,
        achievement_id: str
    ) -> bool:
        """Проверка наличия достижения"""
        stmt = (
            select(Achievement)
            .where(
                and_(
                    Achievement.user_id == user_id,
                    Achievement.achievement_id == achievement_id
                )
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


# ============================================================================
# ANALYTICS SERVICE
# ============================================================================

class AnalyticsService:
    """Сервис для работы с аналитикой"""
    
    @staticmethod
    async def track_event(
        session: AsyncSession,
        event_type: str,
        event_name: str,
        user_id: str = None,
        session_id: str = None,
        event_data: dict = None,
        scene: str = None,
        device_type: str = None,
        ip_address: str = None
    ) -> AnalyticsEvent:
        """Отслеживание события"""
        event = AnalyticsEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            event_name=event_name,
            event_data=event_data or {},
            scene=scene,
            device_type=device_type,
            ip_address=ip_address
        )
        session.add(event)
        await session.flush()
        return event
    
    @staticmethod
    async def get_events_by_type(
        session: AsyncSession,
        event_type: str,
        limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Получение событий по типу"""
        stmt = (
            select(AnalyticsEvent)
            .where(AnalyticsEvent.event_type == event_type)
            .order_by(desc(AnalyticsEvent.timestamp))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_events(
        session: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> List[AnalyticsEvent]:
        """Получение событий пользователя"""
        stmt = (
            select(AnalyticsEvent)
            .where(AnalyticsEvent.user_id == user_id)
            .order_by(desc(AnalyticsEvent.timestamp))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_event_counts(
        session: AsyncSession,
        event_type: str = None,
        days: int = 7
    ) -> Dict[str, int]:
        """Получение количества событий по типам"""
        since = datetime.utcnow() - timedelta(days=days)
        
        if event_type:
            stmt = (
                select(AnalyticsEvent.event_name, func.count())
                .where(
                    and_(
                        AnalyticsEvent.event_type == event_type,
                        AnalyticsEvent.timestamp >= since
                    )
                )
                .group_by(AnalyticsEvent.event_name)
            )
        else:
            stmt = (
                select(AnalyticsEvent.event_type, func.count())
                .where(AnalyticsEvent.timestamp >= since)
                .group_by(AnalyticsEvent.event_type)
            )
        
        result = await session.execute(stmt)
        return dict(result.all())


# ============================================================================
# LEADERBOARD SERVICE
# ============================================================================

class LeaderboardService:
    """Сервис для работы с таблицей лидеров"""
    
    @staticmethod
    async def update_entry(session: AsyncSession, user_id: str) -> LeaderboardEntry:
        """Обновление записи в таблице лидеров"""
        # Получение пользователя
        user = await UserService.get_by_id(session, user_id)
        if not user:
            return None
        
        # Создание или обновление записи
        stmt = (
            select(LeaderboardEntry)
            .where(LeaderboardEntry.user_id == user_id)
        )
        result = await session.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if entry:
            entry.score = user.total_score
            entry.games_completed = user.games_completed
            entry.total_playtime = user.total_playtime
            entry.achievements_count = user.achievements_count
            entry.last_updated = datetime.utcnow()
        else:
            entry = LeaderboardEntry(
                id=str(uuid.uuid4()),
                user_id=user_id,
                score=user.total_score,
                games_completed=user.games_completed,
                total_playtime=user.total_playtime,
                achievements_count=user.achievements_count
            )
            session.add(entry)
        
        await session.flush()
        return entry
    
    @staticmethod
    async def recalculate_ranks(session: AsyncSession) -> None:
        """Пересчёт рангов"""
        # Получение всех записей отсортированных по очкам
        stmt = (
            select(LeaderboardEntry)
            .order_by(desc(LeaderboardEntry.score))
        )
        result = await session.execute(stmt)
        entries = list(result.scalars().all())
        
        # Обновление рангов
        for i, entry in enumerate(entries, 1):
            entry.rank = i
        
        await session.flush()
    
    @staticmethod
    async def get_top(
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получение топ лидеров"""
        # Присоединение данных пользователя
        stmt = (
            select(LeaderboardEntry, User)
            .join(User, LeaderboardEntry.user_id == User.id)
            .order_by(LeaderboardEntry.rank)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        
        leaders = []
        for entry, user in result.all():
            leaders.append({
                "rank": entry.rank,
                "user_id": user.id,
                "username": user.username,
                "score": entry.score,
                "games_completed": entry.games_completed,
                "total_playtime": entry.total_playtime,
                "achievements_count": entry.achievements_count
            })
        
        return leaders
    
    @staticmethod
    async def get_user_rank(
        session: AsyncSession,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Получение ранга пользователя"""
        stmt = (
            select(LeaderboardEntry, User)
            .join(User, LeaderboardEntry.user_id == User.id)
            .where(LeaderboardEntry.user_id == user_id)
        )
        result = await session.execute(stmt)
        row = result.one_or_none()
        
        if not row:
            return None
        
        entry, user = row
        return {
            "rank": entry.rank,
            "username": user.username,
            "score": entry.score,
            "games_completed": entry.games_completed,
            "achievements_count": entry.achievements_count
        }


# ============================================================================
# RATE LIMIT SERVICE
# ============================================================================

class RateLimitService:
    """Сервис для rate limiting"""
    
    @staticmethod
    async def check_rate_limit(
        session: AsyncSession,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Проверка rate limit
        
        Returns:
            Кортеж (разрешено_ли, оставшиеся_запросы)
        """
        now = datetime.utcnow()
        reset_at = now + timedelta(seconds=window_seconds)
        
        stmt = select(RateLimitEntry).where(RateLimitEntry.key == key)
        result = await session.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if not entry:
            # Создание новой записи
            entry = RateLimitEntry(
                id=str(uuid.uuid4()),
                key=key,
                count=1,
                reset_at=reset_at
            )
            session.add(entry)
            await session.flush()
            return True, max_requests - 1
        
        # Проверка истечения окна
        if entry.reset_at < now:
            entry.count = 1
            entry.reset_at = reset_at
            await session.flush()
            return True, max_requests - 1
        
        # Проверка лимита
        if entry.count >= max_requests:
            return False, 0
        
        # Увеличение счётчика
        entry.count += 1
        await session.flush()
        return True, max_requests - entry.count
    
    @staticmethod
    async def reset(session: AsyncSession, key: str) -> None:
        """Сброс rate limit для ключа"""
        stmt = delete(RateLimitEntry).where(RateLimitEntry.key == key)
        await session.execute(stmt)
