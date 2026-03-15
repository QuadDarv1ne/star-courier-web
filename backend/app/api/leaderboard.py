"""
StarCourier Web - Leaderboard API Router
API endpoints для таблицы лидеров

Автор: QuadDarv1ne
Версия: 1.1.0
"""

import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Query

from app.models.auth import LeaderboardEntry

logger = logging.getLogger(__name__)

router = APIRouter()

# Путь к файлу статистики
DATA_DIR: Path = Path(__file__).parent.parent / "data"
PLAYER_STATS_FILE: Path = DATA_DIR / "player_stats.json"
USERS_FILE: Path = DATA_DIR / "users.json"


def _load_json(filepath: Path) -> dict:
    """Загрузка JSON файла
    
    Args:
        filepath: Путь к JSON файлу
        
    Returns:
        dict: Данные из файла или пустой словарь
    """
    if not filepath.exists():
        return {}
    try:
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_score(stats: dict) -> int:
    """
    Расчёт очков для таблицы лидеров.

    Формула:
    - Базовые очки за каждую пройденную сцену
    - Бонус за достижения
    - Штраф за низкие характеристики в конце
    - Бонус за специфичные концовки
    
    Args:
        stats: Статистика игрока
        
    Returns:
        int: Рассчитанные очки
    """
    base_score = stats.get("choices_made", 0) * 100
    
    # Бонус за достижения
    achievements_bonus = len(stats.get("achievements", [])) * 50
    
    # Бонус за концовки
    ending_bonus = {
        "awakening": 500,    # Лучшая концовка
        "guardian": 400,
        "sacrifice": 350,
        "combat_victory": 300,
        "defeat": 0          # Худшая концовка
    }
    ending_type = stats.get("ending_type", "")
    ending_score = ending_bonus.get(ending_type, 0)
    
    # Штраф за низкие характеристики
    final_stats = stats.get("stats", {})
    health = final_stats.get("health", 100)
    morale = final_stats.get("morale", 100)
    
    # Бонус за высокие характеристики в конце
    health_bonus = max(0, health - 50) * 2
    morale_bonus = max(0, morale - 50) * 2
    
    # Штраф за время (чем быстрее, тем лучше)
    playtime = stats.get("playtime", 0)
    time_bonus = max(0, 1000 - playtime // 60)  # Бонус за быстрое прохождение
    
    total_score = (
        base_score + 
        achievements_bonus + 
        ending_score + 
        health_bonus + 
        morale_bonus + 
        time_bonus
    )
    
    return max(0, total_score)


def get_leaderboard_data() -> List[dict]:
    """Получение данных для таблицы лидеров
    
    Returns:
        List[dict]: Список игроков с очками, отсортированный по score
    """
    player_stats: dict = _load_json(PLAYER_STATS_FILE)
    users: dict = _load_json(USERS_FILE)

    leaderboard: List[dict] = []

    for player_id, stats in player_stats.items():
        # Пропускаем незавершённые игры
        if not stats.get("ending_type"):
            continue

        user_id: str = stats.get("user_id")
        user: dict = users.get(user_id, {})

        score: int = calculate_score(stats)

        leaderboard.append({
            "player_id": player_id,
            "username": user.get("username", "Anonymous"),
            "score": score,
            "games_completed": 1,
            "achievements": len(stats.get("achievements", [])),
            "playtime": stats.get("playtime", 0),
            "ending_type": stats.get("ending_type"),
            "completed_at": stats.get("updated_at", "")
        })

    # Сортировка по очкам
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    return leaderboard


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[LeaderboardEntry],
            summary="Получить таблицу лидеров")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    sort_by: str = Query("score", regex="^(score|playtime|achievements)$",
                          description="Сортировка: score, playtime, achievements")
) -> List[LeaderboardEntry]:
    """
    Получение таблицы лидеров.

    Параметры сортировки:
    - **score**: по очкам (по умолчанию)
    - **playtime**: по времени игры (меньше = лучше)
    - **achievements**: по количеству достижений
    
    Args:
        limit: Количество записей (1-100)
        offset: Смещение для пагинации
        sort_by: Критерий сортировки
        
    Returns:
        List[LeaderboardEntry]: Список игроков с рангами
    """
    leaderboard: List[dict] = get_leaderboard_data()

    # Применение сортировки
    if sort_by == "playtime":
        leaderboard.sort(key=lambda x: x["playtime"])
    elif sort_by == "achievements":
        leaderboard.sort(key=lambda x: x["achievements"], reverse=True)
    else:  # score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)

    # Применение пагинации
    paginated = leaderboard[offset:offset + limit]

    # Добавление ранга
    result: List[LeaderboardEntry] = []
    for i, entry in enumerate(paginated):
        result.append(LeaderboardEntry(
            rank=offset + i + 1,
            username=entry["username"],
            score=entry["score"],
            games_completed=entry["games_completed"],
            achievements=entry["achievements"],
            playtime=entry["playtime"]
        ))

    return result


@router.get("/stats",
            summary="Статистика таблицы лидеров")
async def get_leaderboard_stats():
    """
    Общая статистика таблицы лидеров.
    
    Возвращает:
    - Общее количество игроков
    - Средние показатели
    - Распределение по типам концовок
    """
    leaderboard = get_leaderboard_data()
    
    if not leaderboard:
        return {
            "total_players": 0,
            "average_score": 0,
            "average_playtime": 0,
            "endings_distribution": {}
        }
    
    total_score = sum(e["score"] for e in leaderboard)
    total_playtime = sum(e["playtime"] for e in leaderboard)
    
    # Распределение по концовкам
    endings_dist = {}
    for entry in leaderboard:
        ending = entry.get("ending_type", "unknown")
        endings_dist[ending] = endings_dist.get(ending, 0) + 1
    
    return {
        "total_players": len(leaderboard),
        "average_score": total_score // len(leaderboard) if leaderboard else 0,
        "average_playtime": total_playtime // len(leaderboard) if leaderboard else 0,
        "endings_distribution": endings_dist,
        "top_score": leaderboard[0]["score"] if leaderboard else 0,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/user/{username}",
            summary="Позиция игрока в таблице")
async def get_user_position(username: str):
    """
    Получение позиции конкретного игрока в таблице лидеров.
    """
    leaderboard = get_leaderboard_data()
    
    for i, entry in enumerate(leaderboard):
        if entry["username"].lower() == username.lower():
            return {
                "found": True,
                "rank": i + 1,
                "username": entry["username"],
                "score": entry["score"],
                "achievements": entry["achievements"],
                "playtime": entry["playtime"],
                "ending_type": entry["ending_type"]
            }
    
    return {
        "found": False,
        "message": f"Игрок '{username}' не найден в таблице лидеров"
    }


@router.get("/around/{username}",
            summary="Игроки вокруг указанного пользователя")
async def get_players_around(
    username: str,
    range_size: int = Query(5, ge=1, le=20, description="Количество игроков выше/ниже")
):
    """
    Получение игроков, которые находятся выше и ниже указанного пользователя.
    
    Полезно для показа позиции пользователя относительно других.
    """
    leaderboard = get_leaderboard_data()
    
    user_index = -1
    for i, entry in enumerate(leaderboard):
        if entry["username"].lower() == username.lower():
            user_index = i
            break
    
    if user_index == -1:
        return {
            "found": False,
            "message": f"Игрок '{username}' не найден"
        }
    
    start = max(0, user_index - range_size)
    end = min(len(leaderboard), user_index + range_size + 1)
    
    result = []
    for i in range(start, end):
        entry = leaderboard[i]
        result.append(LeaderboardEntry(
            rank=i + 1,
            username=entry["username"],
            score=entry["score"],
            games_completed=entry["games_completed"],
            achievements=entry["achievements"],
            playtime=entry["playtime"]
        ))
    
    return {
        "found": True,
        "current_user_rank": user_index + 1,
        "players": result
    }
