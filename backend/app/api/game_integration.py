"""
API для интеграции игровых механик
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.game_integration import get_game_integration, GameIntegrationService

logger = logging.getLogger('api.game_integration')

router = APIRouter()


def get_integration() -> GameIntegrationService:
    return get_game_integration()


class PlayerStateRequest(BaseModel):
    player_id: str = Field(..., description="ID игрока")


class CraftRequest(BaseModel):
    player_id: str = Field(..., description="ID игрока")
    recipe_id: str = Field(..., description="ID рецепта")


class CombatStartRequest(BaseModel):
    player_id: str = Field(..., description="ID игрока")
    enemy_name: str = Field("Бандит", description="Имя врага")
    enemy_level: int = Field(1, description="Уровень врага", ge=1, le=50)


@router.get("/game-integration/{player_id}", tags=["🎮 Интеграция"])
async def get_player_state(
    player_id: str,
    integration: GameIntegrationService = Depends(get_integration)
):
    """Получить полное состояние игрока со всеми механиками"""
    try:
        state = integration.get_player_state(player_id)
        return {
            "status": "success",
            "data": state
        }
    except Exception as e:
        logger.error(f"Ошибка получения состояния: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/game-integration/craft", tags=["🎮 Интеграция"])
async def craft_item(
    request: CraftRequest,
    integration: GameIntegrationService = Depends(get_integration)
):
    """Выполнить крафт для игрока"""
    try:
        result = integration.craft_item(request.player_id, request.recipe_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка крафта: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/game-integration/combat/start", tags=["🎮 Интеграция"])
async def start_combat(
    request: CombatStartRequest,
    integration: GameIntegrationService = Depends(get_integration)
):
    """Начать бой для игрока"""
    try:
        result = integration.start_combat(
            request.player_id,
            request.enemy_name,
            request.enemy_level
        )
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Ошибка начала боя: {e}")
        raise HTTPException(status_code=500, detail=str(e))
