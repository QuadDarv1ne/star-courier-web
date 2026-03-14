"""
API для управления игровыми механиками глав 11-18
Резонанс, Пути, Финалы, Ментальное состояние
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.game_mechanics_service import get_game_mechanics_manager, PathType, EndingType

logger = logging.getLogger('api.game_mechanics')

router = APIRouter()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ResonanceGainRequest(BaseModel):
    """Запрос на получение опыта Резонанса"""
    amount: int = Field(..., description="Количество опыта", ge=1, le=100)


class PathChoiceRequest(BaseModel):
    """Запрос на выбор пути"""
    path: str = Field(..., description="Тип пути", pattern="^(alliance|observer|independence)$")


class PathProgressRequest(BaseModel):
    """Запрос на прогресс пути"""
    choice_id: str = Field("", description="ID выбора")
    progress: int = Field(10, description="Количество прогресса", ge=1, le=50)


class MentalStateUpdateRequest(BaseModel):
    """Запрос на обновление ментального состояния"""
    health_change: int = Field(0, description="Изменение здоровья", ge=-100, le=100)
    influence_change: int = Field(0, description="Изменение влияния Сущности", ge=-100, le=100)


class EndingCheckRequest(BaseModel):
    """Запрос на проверку финала"""
    ending_type: str = Field(..., description="Тип финала", pattern="^(exile|treaty|merge)$")


class EntityContactRequest(BaseModel):
    """Запрос на контакт с Сущностью"""
    intensity: int = Field(..., description="Интенсивность контакта", ge=1, le=100)


class PlayerStatsUpdateRequest(BaseModel):
    """Запрос на обновление статистики игрока"""
    psychic: Optional[int] = Field(None, ge=0, le=100)
    empathy: Optional[int] = Field(None, ge=0, le=100)
    resonance_level: Optional[int] = Field(None, ge=1, le=4)
    mental_health: Optional[int] = Field(None, ge=0, le=100)
    entity_influence: Optional[int] = Field(None, ge=0, le=100)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/state", tags=["🎮 Игровые механики"])
async def get_player_state():
    """
    Получить текущее состояние игрока.
    
    Включает:
    - Уровень Резонанса и бонусы
    - Ментальное состояние
    - Прогресс пути
    - Доступные финалы
    """
    try:
        manager = get_game_mechanics_manager()
        state = manager.get_player_state()
        
        return ResponseModel(
            status="success",
            message="Состояние игрока получено",
            data=state
        )
    except Exception as e:
        logger.error(f"Ошибка получения состояния: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resonance/gain", tags=["🎮 Игровые механики"])
async def gain_resonance_experience(request: ResonanceGainRequest):
    """
    Получить опыт Резонанса.
    
    Опыт получается за:
    - Контакт с аномалиями
    - Использование Psychic способностей
    - Контакт с Сущностью
    """
    try:
        manager = get_game_mechanics_manager()
        result = manager.gain_resonance_exp(request.amount)
        
        return ResponseModel(
            status="success",
            message=f"Получено {request.amount} опыта Резонанса",
            data=result
        )
    except Exception as e:
        logger.error(f"Ошибка получения опыта Резонанса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/path/choose", tags=["🎮 Игровые механики"])
async def choose_path(request: PathChoiceRequest):
    """
    Выбрать путь развития.
    
    Доступные пути:
    - **alliance** - Альянс (флот, ресурсы)
    - **observer** - Наблюдатель (знания, Psychic)
    - **independence** - Независимость (свобода, сеть)
    """
    try:
        manager = get_game_mechanics_manager()
        result = manager.choose_path(request.path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ResponseModel(
            status="success",
            message=f"Выбран путь: {request.path}",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка выбора пути: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/path/progress", tags=["🎮 Игровые механики"])
async def update_path_progress(request: PathProgressRequest):
    """
    Обновить прогресс пути.
    
    Прогресс получается за выборы, соответствующие пути.
    При достижении 50 прогресса разблокируется финал Договора.
    """
    try:
        manager = get_game_mechanics_manager()
        result = manager.make_path_choice({
            "choice_id": request.choice_id,
            "progress": request.progress,
            "path": manager.path_progress.path.value if manager.path_progress.path else None
        })
        
        return ResponseModel(
            status="success",
            message="Прогресс пути обновлён",
            data=result
        )
    except Exception as e:
        logger.error(f"Ошибка обновления прогресса пути: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mental-state/update", tags=["🎮 Игровые механики"])
async def update_mental_state(request: MentalStateUpdateRequest):
    """
    Обновить ментальное состояние.
    
    Возвращает текущее состояние и эффекты:
    - normal (80-100) - нормальное состояние
    - hallucinations (60-79) - лёгкие галлюцинации
    - visions (40-59) - видения
    - serious (20-39) - серьёзные нарушения
    - critical (0-19) - потеря контроля
    """
    try:
        manager = get_game_mechanics_manager()
        result = manager.update_mental_state(
            health_change=request.health_change,
            influence_change=request.influence_change
        )
        
        return ResponseModel(
            status="success",
            message="Ментальное состояние обновлено",
            data=result
        )
    except Exception as e:
        logger.error(f"Ошибка обновления ментального состояния: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ending/check", tags=["🎮 Игровые механики"])
async def check_ending_availability(request: EndingCheckRequest):
    """
    Проверить доступность финала.
    
    Требования финалов:
    - **exile** - любой путь
    - **treaty** - Psychic 70+ или Empathy 80+
    - **merge** - Psychic 90+ и Resonance Level 4
    """
    try:
        manager = get_game_mechanics_manager()
        result = manager.check_ending_availability(request.ending_type)
        
        return ResponseModel(
            status="success",
            message=f"Проверка финала: {request.ending_type}",
            data=result
        )
    except Exception as e:
        logger.error(f"Ошибка проверки финала: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entity/contact", tags=["🎮 Игровые механики"])
async def entity_contact(request: EntityContactRequest):
    """
    Установить контакт с Сущностью.
    
    Контакт влияет на:
    - Влияние Сущности (entity_influence)
    - Ментальное здоровье
    - Риск коррупции
    - Опыт Резонанса
    
    Psychic способности снижают негативные эффекты.
    """
    try:
        manager = get_game_mechanics_manager()
        result = manager.entity_contact(request.intensity)
        
        return ResponseModel(
            status="success",
            message=f"Контакт с Сущностью (интенсивность: {request.intensity})",
            data=result
        )
    except Exception as e:
        logger.error(f"Ошибка контакта с Сущностью: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/player-stats/update", tags=["🎮 Игровые механики"])
async def update_player_stats(request: PlayerStatsUpdateRequest):
    """
    Обновить статистику игрока.
    
    Используется для синхронизации с основной системой игры.
    """
    try:
        manager = get_game_mechanics_manager()
        
        # Обновление статистики
        if request.psychic is not None:
            manager.player_stats["psychic"] = request.psychic
        if request.empathy is not None:
            manager.player_stats["empathy"] = request.empathy
        if request.resonance_level is not None:
            manager.player_stats["resonance_level"] = request.resonance_level
        if request.mental_health is not None:
            manager.player_stats["mental_health"] = request.mental_health
        if request.entity_influence is not None:
            manager.player_stats["entity_influence"] = request.entity_influence
        
        # Проверка разблокировки финалов
        if manager.player_stats.get("psychic", 0) >= 70 or manager.player_stats.get("empathy", 0) >= 80:
            manager.ending_system.unlock_ending(EndingType.TREATY)
        
        if manager.player_stats.get("psychic", 0) >= 90 and manager.player_stats.get("resonance_level", 1) >= 4:
            manager.ending_system.unlock_ending(EndingType.MERGE)
        
        return ResponseModel(
            status="success",
            message="Статистика игрока обновлена",
            data=manager.get_player_state()
        )
    except Exception as e:
        logger.error(f"Ошибка обновления статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resonance/description", tags=["🎮 Игровые механики"])
async def get_resonance_description():
    """
    Получить описание текущего уровня Резонанса.
    """
    try:
        manager = get_game_mechanics_manager()
        description = manager.get_resonance_description()
        
        return ResponseModel(
            status="success",
            message="Описание Резонанса",
            data={
                "level": manager.resonance.level,
                "description": description,
                "bonus": manager.resonance.get_current_bonus()
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения описания Резонанса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/path/bonus/{bonus_type}", tags=["🎮 Игровые механики"])
async def get_path_bonus(bonus_type: str):
    """
    Получить бонус текущего пути.
    
    Доступные типы бонусов:
    - credits, fleet_support, equipment_discount (Альянс)
    - psychic_boost, ancient_knowledge, resonance_boost (Наблюдатель)
    - network_access, smuggler_routes, mercenary_discount (Независимость)
    """
    try:
        manager = get_game_mechanics_manager()
        bonus_value = manager.apply_path_bonus(bonus_type)
        
        return ResponseModel(
            status="success",
            message=f"Бонус пути: {bonus_type}",
            data={
                "path": manager.path_progress.path.value if manager.path_progress.path else None,
                "bonus_type": bonus_type,
                "value": bonus_value
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения бонуса пути: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/endings", tags=["🎮 Игровые механики"])
async def get_all_endings():
    """
    Получить информацию обо всех финалах.
    """
    try:
        manager = get_game_mechanics_manager()
        endings = {}
        
        for ending in EndingType:
            endings[ending.value] = manager.ending_system.get_ending_info(ending)
        
        return ResponseModel(
            status="success",
            message="Информация о финалах",
            data=endings
        )
    except Exception as e:
        logger.error(f"Ошибка получения информации о финалах: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", tags=["🎮 Игровые механики"])
async def reset_mechanics():
    """
    Сбросить все механики (для тестов или новой игры).
    """
    try:
        from app.services.game_mechanics_service import reset_game_mechanics_manager
        reset_game_mechanics_manager()
        
        return ResponseModel(
            status="success",
            message="Механики сброшены",
            data={}
        )
    except Exception as e:
        logger.error(f"Ошибка сброса механик: {e}")
        raise HTTPException(status_code=500, detail=str(e))
