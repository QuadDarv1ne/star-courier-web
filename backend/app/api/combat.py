"""
API для тактической боевой системы
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from app.services.combat_service import (
    CombatManager, CombatState, CombatAction, CombatActionType,
    CombatAbility, Position, Combatant, create_player_combatant,
    create_enemy_combatant
)
from app.models.base import APIResponse, ResponseBuilder, ErrorCodeEnum

logger = logging.getLogger('api.combat')

router = APIRouter()


# ============================================================================
# DEPENDENCIES
# ============================================================================

def get_combat_manager() -> CombatManager:
    """Получить менеджер боя"""
    return CombatManager()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CombatStartRequest(BaseModel):
    """Запрос на начало боя"""
    enemy_name: str = Field("Бандит", description="Имя врага")
    enemy_level: int = Field(1, description="Уровень врага", ge=1, le=50)
    player_level: int = Field(1, description="Уровень игрока", ge=1, le=50)


class CombatActionRequest(BaseModel):
    """Запрос на действие в бою"""
    action_type: CombatActionType = Field(..., description="Тип действия")
    target_id: Optional[str] = Field(None, description="ID цели")
    ability_id: Optional[str] = Field(None, description="ID способности")
    item_id: Optional[str] = Field(None, description="ID предмета")
    position: Optional[Position] = Field(None, description="Позиция")


# ============================================================================
# COMBAT ENDPOINTS
# ============================================================================

@router.post("/combat/start", tags=["⚔️ Бой"])
async def start_combat(
    request: CombatStartRequest,
    combat_manager: CombatManager = Depends(get_combat_manager)
):
    """
    Начать тактический бой.
    
    Параметры:
    - enemy_name: Имя врага
    - enemy_level: Уровень врага
    - player_level: Уровень игрока
    
    Возвращает:
    - Состояние боя
    - Первого ходящего (по скорости)
    """
    try:
        # Создание участников
        player = create_player_combatant("Макс Велл", request.player_level)
        enemy = create_enemy_combatant(request.enemy_name, request.enemy_level)
        
        # Награды за победу
        rewards = {
            "credits": 50 * request.enemy_level,
            "exp": 100 * request.enemy_level,
            "items": []
        }
        
        # Начало боя
        combat = combat_manager.start_combat(player, [enemy], rewards)
        
        return APIResponse(
            status="success",
            message="Бой начался!",
            data={
                "combat_id": combat.id,
                "player": combat.player.model_dump(),
                "enemies": [e.model_dump() for e in combat.enemies],
                "current_turn": combat.current_turn.value,
                "turn": combat.turn
            }
        )
    except Exception as e:
        logger.error(f"Ошибка начала боя: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/combat/{combat_id}", tags=["⚔️ Бой"])
async def get_combat_state(
    combat_id: str,
    combat_manager: CombatManager = Depends(get_combat_manager)
):
    """
    Получить текущее состояние боя.
    
    Включает:
    - Здоровье участников
    - Текущий ход
    - Лог действий
    """
    try:
        combat = combat_manager.combats.get(combat_id)
        
        if not combat:
            raise HTTPException(status_code=404, detail="Бой не найден")
        
        return APIResponse(
            status="success",
            message="Состояние боя получено",
            data={
                "combat_id": combat.id,
                "turn": combat.turn,
                "current_turn": combat.current_turn.value,
                "player": combat.player.model_dump(),
                "enemies": [e.model_dump() for e in combat.enemies],
                "log": [log.model_dump() for log in combat.log[-10:]],  # Последние 10 записей
                "result": combat.result.value if combat.result else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения состояния боя: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/combat/{combat_id}/action", tags=["⚔️ Бой"])
async def player_action(
    combat_id: str,
    request: CombatActionRequest,
    combat_manager: CombatManager = Depends(get_combat_manager)
):
    """
    Выполнить действие игрока в бою.
    
    Доступные действия:
    - attack: Атака цели
    - defend: Защита (повышает защиту)
    - ability: Использование способности
    - item: Использование предмета
    - flee: Попытка бегства
    
    Примеры:
    ```json
    {"action_type": "attack", "target_id": "enemy_Bandit"}
    {"action_type": "ability", "ability_id": "ability_power_shot", "target_id": "enemy_Bandit"}
    {"action_type": "defend"}
    {"action_type": "flee"}
    ```
    """
    try:
        combat = combat_manager.combats.get(combat_id)
        
        if not combat:
            raise HTTPException(status_code=404, detail="Бой не найден")
        
        if combat.result:
            raise HTTPException(status_code=400, detail="Бой уже завершён")
        
        # Создание действия
        ability = None
        if request.ability_id:
            ability = next(
                (a for a in combat.player.abilities if a.id == request.ability_id),
                None
            )
            if not ability:
                raise HTTPException(status_code=400, detail="Способность не найдена")
        
        action = CombatAction(
            type=request.action_type,
            actor_id=combat.player.id,
            target_id=request.target_id,
            ability=ability,
            item_id=request.item_id,
            position=request.position
        )
        
        # Выполнение действия
        success, message, log_entry = combat_manager.player_turn(combat_id, action)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Ход врага (если бой не завершён)
        enemy_logs = []
        if not combat.result:
            _, _, enemy_logs = combat_manager.enemy_turn(combat_id)
        
        return APIResponse(
            status="success",
            message=message,
            data={
                "player_action": log_entry.model_dump() if log_entry else None,
                "enemy_actions": [log.model_dump() for log in enemy_logs],
                "combat_state": {
                    "player": combat.player.model_dump(),
                    "enemies": [e.model_dump() for e in combat.enemies],
                    "result": combat.result.value if combat.result else None,
                    "rewards": combat.rewards if combat.result == "victory" else None
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка выполнения действия: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/combat/{combat_id}/flee", tags=["⚔️ Бой"])
async def flee_combat(
    combat_id: str,
    combat_manager: CombatManager = Depends(get_combat_manager)
):
    """
    Попытаться сбежать из боя.
    
    Шанс успеха зависит от:
    - Скорости игрока
    - Скорости врагов
    """
    try:
        combat = combat_manager.combats.get(combat_id)
        
        if not combat:
            raise HTTPException(status_code=404, detail="Бой не найден")
        
        action = CombatAction(
            type=CombatActionType.FLEE,
            actor_id=combat.player.id
        )
        
        success, message, log_entry = combat_manager.player_turn(combat_id, action)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return APIResponse(
            status="success",
            message=message,
            data={
                "result": combat.result.value if combat.result else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка бегства: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/combat/{combat_id}/log", tags=["⚔️ Бой"])
async def get_combat_log(
    combat_id: str,
    limit: int = Query(20, description="Количество записей", ge=1, le=100),
    combat_manager: CombatManager = Depends(get_combat_manager)
):
    """
    Получить лог боя.
    
    Возвращает последние N записей лога.
    """
    try:
        combat = combat_manager.combats.get(combat_id)
        
        if not combat:
            raise HTTPException(status_code=404, detail="Бой не найден")
        
        logs = combat.log[-limit:]
        
        return APIResponse(
            status="success",
            message="Лог боя получен",
            data={
                "logs": [log.model_dump() for log in logs],
                "total": len(combat.log)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения лога: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ABILITIES ENDPOINTS
# ============================================================================

@router.get("/combat/abilities", tags=["⚔️ Бой"])
async def get_abilities(
    combat_manager: CombatManager = Depends(get_combat_manager)
):
    """
    Получить все доступные боевые способности.
    """
    try:
        # В реальной реализации - загрузка из БД
        abilities = [
            CombatAbility(
                id="ability_quick_shot",
                name="Быстрый выстрел",
                description="Быстрая атака с низким уроном",
                energy_cost=5,
                cooldown=0,
                damage_multiplier=0.8,
                icon="🔫"
            ),
            CombatAbility(
                id="ability_power_shot",
                name="Мощный выстрел",
                description="Медленная мощная атака",
                energy_cost=15,
                cooldown=2,
                damage_multiplier=2.0,
                icon="💥"
            ),
            CombatAbility(
                id="ability_defend",
                name="Защита",
                description="Повышает защиту",
                energy_cost=10,
                cooldown=1,
                damage_multiplier=0,
                icon="🛡️"
            )
        ]
        
        return APIResponse(
            status="success",
            message="Способности получены",
            data={
                "abilities": [a.model_dump() for a in abilities]
            }
        )
    except Exception as e:
        logger.error(f"Ошибка получения способностей: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORT
# ============================================================================


__all__ = ["router"]
