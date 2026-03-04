"""
StarCourier Web - Admin API
API для административной панели

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete, and_, or_, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import (
    User, PlayerStats, GameSession, Achievement, 
    AnalyticsEvent, LeaderboardEntry
)
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# ADMIN MODELS
# ============================================================================

class AdminStats(BaseModel):
    """Статистика для админ-панели"""
    total_users: int
    active_users_today: int
    active_users_week: int
    total_games: int
    games_today: int
    total_achievements_unlocked: int
    total_playtime_hours: float
    avg_session_duration: float


class UserAdminView(BaseModel):
    """Пользователь для админ-панели"""
    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_premium: bool
    games_played: int
    total_score: int
    created_at: datetime
    last_login: Optional[datetime]


class UserListResponse(BaseModel):
    """Список пользователей"""
    users: List[UserAdminView]
    total: int
    page: int
    pages: int


class GameSessionAdminView(BaseModel):
    """Сессия игры для админ-панели"""
    id: str
    user_id: str
    username: str
    status: str
    score: int
    choices_count: int
    duration_seconds: int
    started_at: datetime
    completed_at: Optional[datetime]


class SystemHealth(BaseModel):
    """Состояние системы"""
    database: str
    cache: str
    email: str
    rate_limit: str
    active_connections: int
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


class AdminActionRequest(BaseModel):
    """Запрос на административное действие"""
    action: str
    reason: Optional[str] = None
    duration: Optional[int] = None  # Для временных банов (в часах)


class AdminActionResponse(BaseModel):
    """Ответ на административное действие"""
    success: bool
    message: str
    action: str
    target_id: str


# ============================================================================
# ADMIN DEPENDENCY
# ============================================================================

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Проверка прав администратора"""
    # В реальном приложении проверять роль в БД
    # Пока проверяем по списку или флагу
    admin_usernames = ["admin", "administrator", "root"]
    
    if user.username.lower() not in admin_usernames and not getattr(user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    
    return user


# ============================================================================
# STATS ENDPOINTS
# ============================================================================

@router.get("/stats", response_model=AdminStats, summary="Общая статистика")
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение общей статистики для административной панели
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    # Общее количество пользователей
    total_users_stmt = select(func.count()).select_from(User)
    total_users = (await db.execute(total_users_stmt)).scalar() or 0
    
    # Активные пользователи сегодня
    active_today_stmt = (
        select(func.count(func.distinct(GameSession.user_id)))
        .where(GameSession.started_at >= today)
    )
    active_users_today = (await db.execute(active_today_stmt)).scalar() or 0
    
    # Активные пользователи за неделю
    active_week_stmt = (
        select(func.count(func.distinct(GameSession.user_id)))
        .where(GameSession.started_at >= week_ago)
    )
    active_users_week = (await db.execute(active_week_stmt)).scalar() or 0
    
    # Общее количество игр
    total_games_stmt = select(func.count()).select_from(GameSession)
    total_games = (await db.execute(total_games_stmt)).scalar() or 0
    
    # Игры сегодня
    games_today_stmt = (
        select(func.count())
        .select_from(GameSession)
        .where(GameSession.started_at >= today)
    )
    games_today = (await db.execute(games_today_stmt)).scalar() or 0
    
    # Всего достижений разблокировано
    achievements_stmt = select(func.count()).select_from(Achievement)
    total_achievements = (await db.execute(achievements_stmt)).scalar() or 0
    
    # Общее время игры (в часах)
    playtime_stmt = select(func.sum(GameSession.duration_seconds)).select_from(GameSession)
    total_playtime_seconds = (await db.execute(playtime_stmt)).scalar() or 0
    total_playtime_hours = total_playtime_seconds / 3600
    
    # Средняя длительность сессии
    avg_duration_stmt = (
        select(func.avg(GameSession.duration_seconds))
        .where(GameSession.status == "completed")
    )
    avg_session = (await db.execute(avg_duration_stmt)).scalar() or 0
    
    return AdminStats(
        total_users=total_users,
        active_users_today=active_users_today,
        active_users_week=active_users_week,
        total_games=total_games,
        games_today=games_today,
        total_achievements_unlocked=total_achievements,
        total_playtime_hours=round(total_playtime_hours, 2),
        avg_session_duration=round(avg_session, 2)
    )


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users", response_model=UserListResponse, summary="Список пользователей")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    active_only: bool = Query(False),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка пользователей с пагинацией и поиском
    """
    # Базовый запрос
    base_stmt = select(User)
    count_stmt = select(func.count()).select_from(User)
    
    # Фильтры
    if active_only:
        base_stmt = base_stmt.where(User.is_active == True)
        count_stmt = count_stmt.where(User.is_active == True)
    
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        base_stmt = base_stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)
    
    # Подсчёт общего количества
    total = (await db.execute(count_stmt)).scalar() or 0
    
    # Пагинация
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Получение пользователей
    stmt = (
        base_stmt
        .order_by(desc(User.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return UserListResponse(
        users=[
            UserAdminView(
                id=u.id,
                username=u.username,
                email=u.email,
                is_active=u.is_active,
                is_verified=u.is_verified,
                is_premium=u.is_premium,
                games_played=u.games_played,
                total_score=u.total_score,
                created_at=u.created_at,
                last_login=u.last_login
            )
            for u in users
        ],
        total=total,
        page=page,
        pages=pages
    )


@router.get("/users/{user_id}", summary="Детали пользователя")
async def get_user_details(
    user_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение детальной информации о пользователе
    """
    # Получение пользователя
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получение игровых сессий
    sessions_stmt = (
        select(GameSession)
        .where(GameSession.user_id == user_id)
        .order_by(desc(GameSession.started_at))
        .limit(10)
    )
    sessions_result = await db.execute(sessions_stmt)
    sessions = sessions_result.scalars().all()
    
    # Получение достижений
    achievements_stmt = (
        select(Achievement)
        .where(Achievement.user_id == user_id)
        .order_by(desc(Achievement.unlocked_at))
    )
    achievements_result = await db.execute(achievements_stmt)
    achievements = achievements_result.scalars().all()
    
    return {
        "user": UserAdminView(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_premium=user.is_premium,
            games_played=user.games_played,
            total_score=user.total_score,
            created_at=user.created_at,
            last_login=user.last_login
        ),
        "recent_sessions": [
            {
                "id": s.id,
                "status": s.status,
                "score": s.score,
                "started_at": s.started_at.isoformat(),
                "duration": s.duration_seconds
            }
            for s in sessions
        ],
        "achievements": [
            {
                "id": a.achievement_id,
                "unlocked_at": a.unlocked_at.isoformat(),
                "scene": a.scene
            }
            for a in achievements
        ]
    }


@router.post("/users/{user_id}/action", response_model=AdminActionResponse, summary="Действие над пользователем")
async def user_action(
    user_id: str,
    action: AdminActionRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Выполнение административного действия над пользователем
    
    Поддерживаемые действия:
    - ban: Заблокировать пользователя
    - unban: Разблокировать пользователя
    - verify: Подтвердить email
    - make_premium: Дать премиум статус
    - remove_premium: Убрать премиум статус
    - reset_stats: Сбросить статистику
    - delete: Удалить пользователя
    """
    # Получение пользователя
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Выполнение действия
    try:
        if action.action == "ban":
            user.is_active = False
            message = f"Пользователь {user.username} заблокирован"
        
        elif action.action == "unban":
            user.is_active = True
            message = f"Пользователь {user.username} разблокирован"
        
        elif action.action == "verify":
            user.is_verified = True
            message = f"Email пользователя {user.username} подтверждён"
        
        elif action.action == "make_premium":
            user.is_premium = True
            message = f"Пользователь {user.username} получил премиум"
        
        elif action.action == "remove_premium":
            user.is_premium = False
            message = f"Премиум пользователя {user.username} удалён"
        
        elif action.action == "reset_stats":
            user.games_played = 0
            user.games_completed = 0
            user.total_playtime = 0
            user.total_score = 0
            user.achievements_count = 0
            message = f"Статистика пользователя {user.username} сброшена"
        
        elif action.action == "delete":
            await db.execute(delete(User).where(User.id == user_id))
            message = f"Пользователь {user.username} удалён"
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Неизвестное действие: {action.action}"
            )
        
        await db.commit()
        
        logger.info(f"Admin {admin.username} performed {action.action} on user {user.username}")
        
        return AdminActionResponse(
            success=True,
            message=message,
            action=action.action,
            target_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to perform admin action: {e}")
        raise HTTPException(status_code=500, detail="Ошибка выполнения действия")


# ============================================================================
# GAME SESSIONS
# ============================================================================

@router.get("/sessions", summary="Список игровых сессий")
async def list_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка игровых сессий
    """
    # Базовый запрос с JOIN
    stmt = (
        select(GameSession, User)
        .join(User, GameSession.user_id == User.id)
    )
    
    if status_filter:
        stmt = stmt.where(GameSession.status == status_filter)
    
    # Подсчёт
    count_stmt = select(func.count()).select_from(GameSession)
    if status_filter:
        count_stmt = count_stmt.where(GameSession.status == status_filter)
    
    total = (await db.execute(count_stmt)).scalar() or 0
    
    # Пагинация
    stmt = stmt.order_by(desc(GameSession.started_at)).offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    
    return {
        "sessions": [
            {
                "id": session.id,
                "user_id": session.user_id,
                "username": user.username,
                "status": session.status,
                "score": session.score,
                "choices_count": session.choices_count,
                "duration_seconds": session.duration_seconds,
                "started_at": session.started_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
            for session, user in rows
        ],
        "total": total,
        "page": page
    }


# ============================================================================
# SYSTEM HEALTH
# ============================================================================

@router.get("/health", response_model=SystemHealth, summary="Состояние системы")
async def get_system_health(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение состояния системы
    """
    from app.database.connection import database
    
    # Проверка базы данных
    db_health = "healthy" if await database.health_check() else "unhealthy"
    
    # Проверка кэша (заглушка)
    cache_health = "not_configured"
    
    # Проверка email
    email_health = "enabled" if True else "disabled"  # settings.email_enabled
    
    # Rate limiting
    rate_limit_health = "active"
    
    # Активные соединения (WebSocket)
    active_connections = 0  # WebSocket manager не импортирован здесь
    
    return SystemHealth(
        database=db_health,
        cache=cache_health,
        email=email_health,
        rate_limit=rate_limit_health,
        active_connections=active_connections
    )


# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/analytics/charts", summary="Данные для графиков")
async def get_chart_data(
    days: int = Query(7, ge=1, le=30),
    chart_type: str = Query("users", description="Тип графика: users, games, playtime, achievements"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение данных для графиков аналитики
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    if chart_type == "users":
        # Новые пользователи по дням
        stmt = (
            select(
                func.date(User.created_at).label("date"),
                func.count().label("count")
            )
            .where(User.created_at >= since)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        result = await db.execute(stmt)
        data = [{"date": str(r.date), "count": r.count} for r in result.all()]
    
    elif chart_type == "games":
        # Игры по дням
        stmt = (
            select(
                func.date(GameSession.started_at).label("date"),
                func.count().label("count")
            )
            .where(GameSession.started_at >= since)
            .group_by(func.date(GameSession.started_at))
            .order_by(func.date(GameSession.started_at))
        )
        result = await db.execute(stmt)
        data = [{"date": str(r.date), "count": r.count} for r in result.all()]
    
    elif chart_type == "playtime":
        # Время игры по дням
        stmt = (
            select(
                func.date(GameSession.started_at).label("date"),
                func.sum(GameSession.duration_seconds).label("seconds")
            )
            .where(GameSession.started_at >= since)
            .group_by(func.date(GameSession.started_at))
            .order_by(func.date(GameSession.started_at))
        )
        result = await db.execute(stmt)
        data = [{"date": str(r.date), "hours": round(r.seconds / 3600, 2) if r.seconds else 0} for r in result.all()]
    
    elif chart_type == "achievements":
        # Достижения по дням
        stmt = (
            select(
                func.date(Achievement.unlocked_at).label("date"),
                func.count().label("count")
            )
            .where(Achievement.unlocked_at >= since)
            .group_by(func.date(Achievement.unlocked_at))
            .order_by(func.date(Achievement.unlocked_at))
        )
        result = await db.execute(stmt)
        data = [{"date": str(r.date), "count": r.count} for r in result.all()]
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown chart type: {chart_type}")
    
    return {"chart_type": chart_type, "data": data}


# ============================================================================
# CONTENT MANAGEMENT
# ============================================================================

@router.get("/content/stats", summary="Статистика контента")
async def get_content_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики по контенту игры
    """
    from app.services import data_service
    
    scenes = data_service.get_scenes()
    characters = data_service.get_characters()
    
    # Подсчёт посещений сцен
    scene_visits_stmt = (
        select(
            AnalyticsEvent.scene,
            func.count().label("visits")
        )
        .where(AnalyticsEvent.event_type == "scene_visit")
        .group_by(AnalyticsEvent.scene)
    )
    scene_visits = dict((await db.execute(scene_visits_stmt)).all())
    
    # Популярные сцены
    popular_scenes = sorted(
        scene_visits.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return {
        "total_scenes": len(scenes),
        "total_characters": len(characters),
        "popular_scenes": [
            {"scene_id": s[0], "visits": s[1]}
            for s in popular_scenes
        ],
        "scenes": [
            {
                "id": s.get("id"),
                "title": s.get("title"),
                "visits": scene_visits.get(s.get("id"), 0)
            }
            for s in scenes[:20]
        ]
    }
