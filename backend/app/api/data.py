"""
StarCourier Web - Data Export/Import API
API для экспорта и импорта данных пользователя (GDPR compliance)

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import io
import json
import logging
import zipfile
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import get_db
from app.database.models import User, PlayerStats, GameSession, Achievement
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# MODELS
# ============================================================================

class ExportFormat(BaseModel):
    """Формат экспорта"""
    format: str = Field(default="json", description="json или csv")
    include_sessions: bool = Field(default=True)
    include_achievements: bool = Field(default=True)
    include_stats: bool = Field(default=True)


class ImportData(BaseModel):
    """Данные для импорта"""
    user_data: Optional[Dict[str, Any]] = None
    player_stats: Optional[List[Dict[str, Any]]] = None
    achievements: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None


class ExportResponse(BaseModel):
    """Ответ с информацией об экспорте"""
    status: str
    filename: str
    size_bytes: int
    created_at: str
    expires_at: Optional[str] = None


class ImportResponse(BaseModel):
    """Ответ с результатом импорта"""
    status: str
    message: str
    imported: Dict[str, int] = Field(default_factory=dict)


class DataSummary(BaseModel):
    """Сводка данных пользователя"""
    user_id: str
    username: str
    email: str
    created_at: str
    total_games: int
    total_playtime: int
    achievements_count: int
    total_score: int
    data_size_estimate: str


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/summary", response_model=DataSummary, summary="Сводка данных")
async def get_data_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение сводки данных пользователя
    
    Показывает, какие данные хранятся и их размер
    """
    # Подсчёт сессий
    sessions_stmt = select(GameSession).where(GameSession.user_id == user.id)
    sessions_result = await db.execute(sessions_stmt)
    sessions = sessions_result.scalars().all()
    
    # Подсчёт достижений
    achievements_stmt = select(Achievement).where(Achievement.user_id == user.id)
    achievements_result = await db.execute(achievements_stmt)
    achievements = achievements_result.scalars().all()
    
    # Подсчёт статистики
    stats_stmt = select(PlayerStats).where(PlayerStats.user_id == user.id)
    stats_result = await db.execute(stats_stmt)
    stats = stats_result.scalars().all()
    
    # Оценка размера данных
    data_size = len(json.dumps({
        "user": user.to_dict() if hasattr(user, 'to_dict') else {},
        "sessions": [s.to_dict() if hasattr(s, 'to_dict') else {} for s in sessions],
        "achievements": [a.to_dict() if hasattr(a, 'to_dict') else {} for a in achievements],
        "stats": [st.to_dict() if hasattr(st, 'to_dict') else {} for st in stats]
    }, default=str))
    
    return DataSummary(
        user_id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat(),
        total_games=len(sessions),
        total_playtime=user.total_playtime,
        achievements_count=len(achievements),
        total_score=user.total_score,
        data_size_estimate=_format_size(data_size)
    )


@router.get("/export", summary="Экспорт данных")
async def export_user_data(
    format: str = Query("json", description="Формат: json или zip"),
    include_sessions: bool = Query(True),
    include_achievements: bool = Query(True),
    include_stats: bool = Query(True),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Экспорт всех данных пользователя
    
    Поддерживаемые форматы:
    - json: Один JSON файл со всеми данными
    - zip: ZIP-архив с отдельными файлами
    
    Соответствует требованиям GDPR (право на перенос данных)
    """
    # Сбор данных
    export_data = {
        "export_info": {
            "exported_at": datetime.utcnow().isoformat(),
            "format_version": "1.0",
            "app_version": "2.0.0",
            "user_id": user.id,
            "username": user.username
        },
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "games_played": user.games_played,
            "games_completed": user.games_completed,
            "total_playtime": user.total_playtime,
            "total_score": user.total_score,
            "achievements_count": user.achievements_count,
            "language": user.language,
            "theme": user.theme,
            "settings": {
                "notifications_enabled": user.notifications_enabled,
                "sound_enabled": user.sound_enabled,
                "music_volume": user.music_volume,
                "sfx_volume": user.sfx_volume
            }
        }
    }
    
    # Игровые сессии
    if include_sessions:
        sessions_stmt = (
            select(GameSession)
            .where(GameSession.user_id == user.id)
            .order_by(GameSession.started_at.desc())
        )
        sessions_result = await db.execute(sessions_stmt)
        sessions = sessions_result.scalars().all()
        
        export_data["game_sessions"] = [
            {
                "id": s.id,
                "status": s.status,
                "current_scene": s.current_scene,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "duration_seconds": s.duration_seconds,
                "score": s.score,
                "choices_count": s.choices_count,
                "ending_type": s.ending_type
            }
            for s in sessions
        ]
    
    # Достижения
    if include_achievements:
        achievements_stmt = select(Achievement).where(Achievement.user_id == user.id)
        achievements_result = await db.execute(achievements_stmt)
        achievements = achievements_result.scalars().all()
        
        export_data["achievements"] = [
            {
                "id": a.id,
                "achievement_id": a.achievement_id,
                "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
                "scene": a.scene,
                "progress": a.progress
            }
            for a in achievements
        ]
    
    # Статистика
    if include_stats:
        stats_stmt = select(PlayerStats).where(PlayerStats.user_id == user.id)
        stats_result = await db.execute(stats_stmt)
        stats = stats_result.scalars().all()
        
        export_data["player_stats"] = [
            {
                "id": s.id,
                "player_id": s.player_id,
                "current_scene": s.current_scene,
                "stats": s.stats,
                "relationships": s.relationships,
                "inventory": s.inventory,
                "choices_made": s.choices_made,
                "visited_scenes": s.visited_scenes,
                "playtime": s.playtime,
                "score": s.score,
                "ending_type": s.ending_type
            }
            for s in stats
        ]
    
    # Формирование ответа
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    if format == "zip":
        # Создание ZIP архива
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Основные данные
            zip_file.writestr(
                f"user_data_{timestamp}.json",
                json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            )
            
            # README
            readme = f"""StarCourier Web - User Data Export
================================
Export Date: {datetime.utcnow().isoformat()}
User: {user.username}
User ID: {user.id}

Contents:
- user_data_{timestamp}.json: All exported data

This export is GDPR compliant.
To import this data, use the /api/data/import endpoint.
"""
            zip_file.writestr("README.txt", readme)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=starcourier_export_{timestamp}.zip"
            }
        )
    
    else:
        # JSON ответ
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        json_bytes = json_str.encode('utf-8')
        
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=starcourier_export_{timestamp}.json"
            }
        )


# ============================================================================
# IMPORT ENDPOINTS
# ============================================================================

@router.post("/import", response_model=ImportResponse, summary="Импорт данных")
async def import_user_data(
    data: ImportData,
    merge: bool = Query(True, description="Объединить с существующими данными"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Импорт данных пользователя
    
    При merge=True - данные объединяются с существующими
    При merge=False - существующие данные заменяются
    """
    imported = {
        "user_settings": 0,
        "player_stats": 0,
        "achievements": 0
    }
    
    try:
        # Импорт настроек пользователя
        if data.settings:
            for key, value in data.settings.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            imported["user_settings"] = len(data.settings)
        
        # Импорт статистики
        if data.player_stats:
            if not merge:
                # Удаление существующей статистики
                await db.execute(
                    delete(PlayerStats).where(PlayerStats.user_id == user.id)
                )
            
            for stat_data in data.player_stats:
                # Создание новой записи
                stat = PlayerStats(
                    user_id=user.id,
                    player_id=stat_data.get("player_id"),
                    current_scene=stat_data.get("current_scene", "start"),
                    stats=stat_data.get("stats", {}),
                    relationships=stat_data.get("relationships", {}),
                    inventory=stat_data.get("inventory", []),
                    choices_made=stat_data.get("choices_made", 0),
                    playtime=stat_data.get("playtime", 0),
                    score=stat_data.get("score", 0)
                )
                db.add(stat)
                imported["player_stats"] += 1
        
        # Импорт достижений
        if data.achievements:
            if not merge:
                await db.execute(
                    delete(Achievement).where(Achievement.user_id == user.id)
                )
            
            for ach_data in data.achievements:
                # Проверка существования
                existing = await db.execute(
                    select(Achievement).where(
                        Achievement.user_id == user.id,
                        Achievement.achievement_id == ach_data.get("achievement_id")
                    )
                )
                
                if not existing.scalar_one_or_none() or not merge:
                    achievement = Achievement(
                        user_id=user.id,
                        achievement_id=ach_data.get("achievement_id"),
                        scene=ach_data.get("scene"),
                        progress=ach_data.get("progress", 100)
                    )
                    db.add(achievement)
                    imported["achievements"] += 1
        
        await db.commit()
        
        logger.info(f"📦 Data imported for user {user.username}: {imported}")
        
        return ImportResponse(
            status="success",
            message="Data imported successfully",
            imported=imported
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import failed: {str(e)}"
        )


# ============================================================================
# DELETE ENDPOINTS (GDPR Right to be Forgotten)
# ============================================================================

@router.delete("/delete", summary="Удаление данных")
async def delete_user_data(
    confirm: bool = Query(False, description="Подтверждение удаления"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Полное удаление данных пользователя
    
    Соответствует требованиям GDPR (право на забвение)
    
    ⚠️ Это действие необратимо!
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion must be confirmed with confirm=true"
        )
    
    user_id = user.id
    username = user.username
    
    try:
        # Удаление связанных данных (каскадом через модели)
        await db.execute(delete(Achievement).where(Achievement.user_id == user_id))
        await db.execute(delete(PlayerStats).where(PlayerStats.user_id == user_id))
        await db.execute(delete(GameSession).where(GameSession.user_id == user_id))
        
        # Удаление пользователя
        await db.execute(delete(User).where(User.id == user_id))
        
        await db.commit()
        
        logger.info(f"🗑️ User {username} ({user_id}) deleted all data")
        
        return {
            "status": "success",
            "message": f"All data for user '{username}' has been permanently deleted",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_size(size_bytes: int) -> str:
    """Форматирование размера"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
