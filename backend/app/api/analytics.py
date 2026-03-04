"""
StarCourier Web - Analytics API
API для аналитики игры

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import AnalyticsEvent, User, GameSession
from app.services.db_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# MODELS
# ============================================================================

class TrackEventRequest(BaseModel):
    """Запрос для отслеживания события"""
    event_type: str = Field(..., min_length=1, max_length=50)
    event_name: str = Field(..., min_length=1, max_length=100)
    event_data: dict = Field(default_factory=dict)
    scene: Optional[str] = None
    choice_id: Optional[str] = None
    device_type: Optional[str] = None


class EventResponse(BaseModel):
    """Ответ с событием"""
    id: str
    event_type: str
    event_name: str
    timestamp: datetime
    event_data: dict


class AnalyticsSummary(BaseModel):
    """Сводка аналитики"""
    total_events: int
    events_by_type: Dict[str, int]
    unique_users: int
    events_last_24h: int
    events_last_7d: int
    top_scenes: List[Dict[str, Any]]
    top_choices: List[Dict[str, Any]]


class DailyStats(BaseModel):
    """Статистика по дням"""
    date: str
    events: int
    unique_users: int
    sessions: int


class SceneAnalytics(BaseModel):
    """Аналитика по сценам"""
    scene_id: str
    visits: int
    unique_visitors: int
    avg_time_spent: float
    exit_rate: float


class FunnelStep(BaseModel):
    """Шаг воронки"""
    step: str
    count: int
    percentage: float


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/track", response_model=EventResponse, summary="Отслеживание события")
async def track_event(
    request: TrackEventRequest,
    session_id: Optional[str] = Query(None, description="ID сессии"),
    db: AsyncSession = Depends(get_db)
):
    """
    Отслеживание события аналитики
    
    Поддерживаемые типы событий:
    - scene_visit: Посещение сцены
    - choice_made: Сделан выбор
    - achievement_unlocked: Получено достижение
    - game_start: Начало игры
    - game_end: Конец игры
    - session_start: Начало сессии
    - session_end: Конец сессии
    """
    event = await AnalyticsService.track_event(
        session=db,
        event_type=request.event_type,
        event_name=request.event_name,
        session_id=session_id,
        event_data=request.event_data,
        scene=request.scene,
        device_type=request.device_type
    )
    
    return EventResponse(
        id=event.id,
        event_type=event.event_type,
        event_name=event.event_name,
        timestamp=event.timestamp,
        event_data=event.event_data
    )


@router.get("/summary", response_model=AnalyticsSummary, summary="Сводка аналитики")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=30, description="Период в днях"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение сводки аналитики за период
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    # Общее количество событий
    total_stmt = select(func.count()).select_from(AnalyticsEvent)
    total_result = await db.execute(total_stmt)
    total_events = total_result.scalar() or 0
    
    # События по типам
    type_stmt = (
        select(AnalyticsEvent.event_type, func.count())
        .where(AnalyticsEvent.timestamp >= since)
        .group_by(AnalyticsEvent.event_type)
    )
    type_result = await db.execute(type_stmt)
    events_by_type = dict(type_result.all())
    
    # Уникальные пользователи
    unique_users_stmt = (
        select(func.count(func.distinct(AnalyticsEvent.user_id)))
        .where(AnalyticsEvent.timestamp >= since)
    )
    unique_result = await db.execute(unique_users_stmt)
    unique_users = unique_result.scalar() or 0
    
    # События за последние 24 часа
    last_24h = datetime.utcnow() - timedelta(hours=24)
    stmt_24h = (
        select(func.count())
        .select_from(AnalyticsEvent)
        .where(AnalyticsEvent.timestamp >= last_24h)
    )
    result_24h = await db.execute(stmt_24h)
    events_last_24h = result_24h.scalar() or 0
    
    # События за последние 7 дней
    last_7d = datetime.utcnow() - timedelta(days=7)
    stmt_7d = (
        select(func.count())
        .select_from(AnalyticsEvent)
        .where(AnalyticsEvent.timestamp >= last_7d)
    )
    result_7d = await db.execute(stmt_7d)
    events_last_7d = result_7d.scalar() or 0
    
    # Топ сцен
    top_scenes_stmt = (
        select(
            AnalyticsEvent.scene,
            func.count().label("visits")
        )
        .where(
            and_(
                AnalyticsEvent.event_type == "scene_visit",
                AnalyticsEvent.timestamp >= since,
                AnalyticsEvent.scene.isnot(None)
            )
        )
        .group_by(AnalyticsEvent.scene)
        .order_by(desc("visits"))
        .limit(10)
    )
    top_scenes_result = await db.execute(top_scenes_stmt)
    top_scenes = [
        {"scene": row.scene, "visits": row.visits}
        for row in top_scenes_result.all()
    ]
    
    # Топ выборов
    top_choices_stmt = (
        select(
            AnalyticsEvent.choice_id,
            func.count().label("count")
        )
        .where(
            and_(
                AnalyticsEvent.event_type == "choice_made",
                AnalyticsEvent.timestamp >= since,
                AnalyticsEvent.choice_id.isnot(None)
            )
        )
        .group_by(AnalyticsEvent.choice_id)
        .order_by(desc("count"))
        .limit(10)
    )
    top_choices_result = await db.execute(top_choices_stmt)
    top_choices = [
        {"choice_id": row.choice_id, "count": row.count}
        for row in top_choices_result.all()
    ]
    
    return AnalyticsSummary(
        total_events=total_events,
        events_by_type=events_by_type,
        unique_users=unique_users,
        events_last_24h=events_last_24h,
        events_last_7d=events_last_7d,
        top_scenes=top_scenes,
        top_choices=top_choices
    )


@router.get("/daily", response_model=List[DailyStats], summary="Статистика по дням")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30, description="Период в днях"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики по дням
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    # SQLite не поддерживает date(), используем Python обработку
    events_stmt = (
        select(AnalyticsEvent)
        .where(AnalyticsEvent.timestamp >= since)
        .order_by(AnalyticsEvent.timestamp)
    )
    result = await db.execute(events_stmt)
    events = result.scalars().all()
    
    # Группировка по дням
    daily_data = {}
    for event in events:
        date_key = event.timestamp.strftime("%Y-%m-%d")
        if date_key not in daily_data:
            daily_data[date_key] = {
                "events": 0,
                "users": set(),
                "sessions": set()
            }
        daily_data[date_key]["events"] += 1
        if event.user_id:
            daily_data[date_key]["users"].add(event.user_id)
        if event.session_id:
            daily_data[date_key]["sessions"].add(event.session_id)
    
    return [
        DailyStats(
            date=date,
            events=data["events"],
            unique_users=len(data["users"]),
            sessions=len(data["sessions"])
        )
        for date, data in sorted(daily_data.items())
    ]


@router.get("/scenes", response_model=List[SceneAnalytics], summary="Аналитика по сценам")
async def get_scene_analytics(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение аналитики по сценам
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    # Получение всех посещений сцен
    stmt = (
        select(AnalyticsEvent)
        .where(
            and_(
                AnalyticsEvent.event_type == "scene_visit",
                AnalyticsEvent.timestamp >= since,
                AnalyticsEvent.scene.isnot(None)
            )
        )
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    # Группировка по сценам
    scene_data = {}
    for event in events:
        scene_id = event.scene
        if scene_id not in scene_data:
            scene_data[scene_id] = {
                "visits": 0,
                "visitors": set(),
                "exits": 0
            }
        scene_data[scene_id]["visits"] += 1
        if event.user_id:
            scene_data[scene_id]["visitors"].add(event.user_id)
    
    # Получение выходов из сцен (game_end)
    exit_stmt = (
        select(AnalyticsEvent)
        .where(
            and_(
                AnalyticsEvent.event_type == "game_end",
                AnalyticsEvent.timestamp >= since,
                AnalyticsEvent.scene.isnot(None)
            )
        )
    )
    exit_result = await db.execute(exit_stmt)
    exit_events = exit_result.scalars().all()
    
    for event in exit_events:
        if event.scene in scene_data:
            scene_data[event.scene]["exits"] += 1
    
    return [
        SceneAnalytics(
            scene_id=scene_id,
            visits=data["visits"],
            unique_visitors=len(data["visitors"]),
            avg_time_spent=0.0,  # Требует дополнительных данных
            exit_rate=data["exits"] / data["visits"] if data["visits"] > 0 else 0.0
        )
        for scene_id, data in sorted(
            scene_data.items(),
            key=lambda x: x[1]["visits"],
            reverse=True
        )
    ]


@router.get("/funnel", response_model=List[FunnelStep], summary="Воронка игры")
async def get_game_funnel(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение воронки прохождения игры
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    # Подсчёт событий по типам
    funnel_steps = [
        ("game_start", "Начало игры"),
        ("scene_visit", "Посещение сцен"),
        ("choice_made", "Сделанные выборы"),
        ("achievement_unlocked", "Полученные достижения"),
        ("game_end", "Завершение игры")
    ]
    
    results = []
    first_step_count = None
    
    for event_type, step_name in funnel_steps:
        stmt = (
            select(func.count())
            .select_from(AnalyticsEvent)
            .where(
                and_(
                    AnalyticsEvent.event_type == event_type,
                    AnalyticsEvent.timestamp >= since
                )
            )
        )
        result = await db.execute(stmt)
        count = result.scalar() or 0
        
        if first_step_count is None:
            first_step_count = count
        
        percentage = (count / first_step_count * 100) if first_step_count and first_step_count > 0 else 0.0
        
        results.append(FunnelStep(
            step=step_name,
            count=count,
            percentage=round(percentage, 2)
        ))
    
    return results


@router.get("/endings", summary="Статистика по концовкам")
async def get_endings_stats(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики по концовкам игры
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    # Получение всех завершённых игр
    stmt = (
        select(GameSession)
        .where(
            and_(
                GameSession.status == "completed",
                GameSession.completed_at >= since
            )
        )
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    # Подсчёт по типам концовок
    endings = {}
    total = len(sessions)
    
    for session in sessions:
        ending_type = session.ending_type or "unknown"
        if ending_type not in endings:
            endings[ending_type] = 0
        endings[ending_type] += 1
    
    return {
        "total_completions": total,
        "endings": [
            {
                "type": ending_type,
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0
            }
            for ending_type, count in sorted(
                endings.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
    }


@router.get("/realtime", summary="Реальное время")
async def get_realtime_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики в реальном времени
    """
    last_hour = datetime.utcnow() - timedelta(hours=1)
    
    # Активные сессии
    active_sessions_stmt = (
        select(func.count())
        .select_from(GameSession)
        .where(GameSession.status == "active")
    )
    active_result = await db.execute(active_sessions_stmt)
    active_sessions = active_result.scalar() or 0
    
    # События за последний час
    events_stmt = (
        select(func.count())
        .select_from(AnalyticsEvent)
        .where(AnalyticsEvent.timestamp >= last_hour)
    )
    events_result = await db.execute(events_stmt)
    events_last_hour = events_result.scalar() or 0
    
    # Уникальные пользователи за последний час
    users_stmt = (
        select(func.count(func.distinct(AnalyticsEvent.user_id)))
        .where(AnalyticsEvent.timestamp >= last_hour)
    )
    users_result = await db.execute(users_stmt)
    unique_users = users_result.scalar() or 0
    
    return {
        "active_sessions": active_sessions,
        "events_last_hour": events_last_hour,
        "unique_users_last_hour": unique_users,
        "timestamp": datetime.utcnow().isoformat()
    }
