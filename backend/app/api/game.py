"""
StarCourier Web - Game API Router
API endpoints для игровой логики

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.models.game import (
    GameStartRequest, GameStartResponse,
    GameChoiceRequest, GameChoiceResponse,
    PlayerStatsResponse, SceneResponse, Choice
)
from app.services.data_service import data_service, get_scene

logger = logging.getLogger(__name__)

router = APIRouter()

# Временное хранилище состояния игроков (в продакшене - база данных)
players_state: Dict[str, dict] = {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_game_over(stats: Dict[str, int]) -> tuple[bool, Optional[str]]:
    """Проверка условий конца игры"""
    if stats.get("health", 100) <= 0:
        return True, "health_depleted"
    if stats.get("morale", 100) <= 0:
        return True, "morale_depleted"
    return False, None


def is_ending_scene(scene_id: str) -> bool:
    """Проверка, является ли сцена финальной"""
    ending_keywords = ["ancient_awakening", "hide_artifact", "artifact_destruction",
                       "defend_station", "victory", "game_over"]
    return any(keyword in scene_id for keyword in ending_keywords)


def get_ending_type(scene_id: str) -> Optional[str]:
    """Определить тип концовки"""
    ending_types = {
        "ancient_awakening": "awakening",
        "hide_artifact": "guardian",
        "artifact_destruction": "sacrifice",
        "defend_station": "combat_victory",
        "game_over": "defeat"
    }
    for key, ending_type in ending_types.items():
        if key in scene_id:
            return ending_type
    return None


def apply_stat_changes(current_stats: Dict[str, int],
                       changes: Optional[Dict[str, int]]) -> Dict[str, int]:
    """Применить изменения статистики"""
    if not changes:
        return current_stats

    new_stats = current_stats.copy()
    for stat, change in changes.items():
        if stat in new_stats:
            new_stats[stat] = max(0, min(100, new_stats[stat] + change))
        else:
            new_stats[stat] = max(0, min(100, 50 + change))

    return new_stats


def format_scene_response(scene_id: str, scene_data: dict) -> SceneResponse:
    """Форматировать данные сцены для ответа"""
    choices = [
        Choice(
            text=choice.get("text", ""),
            next=choice.get("next", ""),
            stats=choice.get("stats"),
            difficulty=choice.get("difficulty")
        )
        for choice in scene_data.get("choices", [])
    ]

    return SceneResponse(
        id=scene_id,
        title=scene_data.get("title", "Без названия"),
        text=scene_data.get("text", ""),
        image=scene_data.get("image", "🎮"),
        character=scene_data.get("character", "Система"),
        choices=choices
    )


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/start", response_model=GameStartResponse,
             summary="Начать новую игру")
async def start_game(request: GameStartRequest):
    """
    Начать новую игру для игрока.

    Возвращает начальную сцену, статистику и отношения с персонажами.
    """
    player_id = request.player_id

    # Получаем начальную сцену
    scene_data = get_scene("start")
    if not scene_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Начальная сцена не найдена"
        )

    # Инициализируем состояние игрока
    players_state[player_id] = {
        "current_scene": "start",
        "stats": data_service.get_initial_stats(),
        "relationships": data_service.get_initial_relationships(),
        "inventory": ["Брекер кодов", "Боевой нож"],
        "choices_made": 0,
        "started_at": datetime.now().isoformat(),
        "visited_scenes": ["start"]
    }

    logger.info(f"🎮 Игрок {player_id} начал новую игру")

    return GameStartResponse(
        status="success",
        scene=format_scene_response("start", scene_data),
        stats=players_state[player_id]["stats"],
        relationships=players_state[player_id]["relationships"]
    )


@router.post("/choose", response_model=GameChoiceResponse,
             summary="Сделать выбор")
async def make_choice(request: GameChoiceRequest):
    """
    Сделать выбор и перейти к следующей сцене.

    Обновляет статистику и возвращает новую сцену.
    """
    player_id = request.player_id
    next_scene_id = request.next_scene

    # Проверяем существование игрока
    if player_id not in players_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Игрок не найден. Начните новую игру."
        )

    player = players_state[player_id]

    # Получаем следующую сцену
    scene_data = get_scene(next_scene_id)
    if not scene_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сцена '{next_scene_id}' не найдена"
        )

    # Применяем изменения статистики
    if request.stats:
        player["stats"] = apply_stat_changes(player["stats"], request.stats)

    # Обновляем состояние игрока
    player["current_scene"] = next_scene_id
    player["choices_made"] += 1
    if next_scene_id not in player.get("visited_scenes", []):
        player.setdefault("visited_scenes", []).append(next_scene_id)

    # Проверяем конец игры
    game_over, reason = check_game_over(player["stats"])
    ending_type = get_ending_type(next_scene_id) if is_ending_scene(next_scene_id) else None

    if game_over:
        logger.info(f"💀 Игрок {player_id} проиграл: {reason}")
    elif ending_type:
        logger.info(f"🏆 Игрок {player_id} достиг концовки: {ending_type}")

    return GameChoiceResponse(
        status="success",
        scene=format_scene_response(next_scene_id, scene_data),
        stats=player["stats"],
        relationships=player["relationships"],
        choices_made=player["choices_made"],
        game_over=game_over or bool(ending_type),
        ending_type=ending_type
    )


@router.get("/stats/{player_id}", response_model=PlayerStatsResponse,
            summary="Получить статистику игрока")
async def get_player_stats(player_id: str):
    """
    Получить текущую статистику и состояние игрока.
    """
    if player_id not in players_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Игрок не найден"
        )

    player = players_state[player_id]
    game_over, _ = check_game_over(player["stats"])

    return PlayerStatsResponse(
        current_scene=player["current_scene"],
        stats=player["stats"],
        relationships=player["relationships"],
        inventory=player.get("inventory", []),
        choices_made=player["choices_made"],
        game_over=game_over
    )


@router.get("/scene/{scene_id}", response_model=SceneResponse,
            summary="Получить сцену")
async def get_scene_by_id(scene_id: str):
    """
    Получить данные конкретной сцены по ID.
    """
    scene_data = get_scene(scene_id)
    if not scene_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сцена '{scene_id}' не найдена"
        )

    return format_scene_response(scene_id, scene_data)


@router.delete("/player/{player_id}",
               summary="Удалить данные игрока")
async def delete_player(player_id: str):
    """
    Удалить данные игрока (сбросить прогресс).
    """
    if player_id not in players_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Игрок не найден"
        )

    del players_state[player_id]
    logger.info(f"🗑️ Данные игрока {player_id} удалены")

    return {"status": "success", "message": "Прогресс игрока удалён"}
