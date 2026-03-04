"""
StarCourier Web - Achievements API Router
API endpoints для системы достижений

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter()

# Путь к файлам данных
DATA_DIR = Path(__file__).parent.parent / "data"
ACHIEVEMENTS_FILE = DATA_DIR / "achievements.json"


def _load_achievements() -> dict:
    """Загрузка определений достижений"""
    if not ACHIEVEMENTS_FILE.exists():
        return {"achievements": {}, "categories": {}, "rarity": {}}
    try:
        with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading achievements: {e}")
        return {"achievements": {}, "categories": {}, "rarity": {}}


def get_rarity(points: int) -> str:
    """Определение редкости по очкам"""
    if points <= 30:
        return "common"
    elif points <= 50:
        return "uncommon"
    elif points <= 75:
        return "rare"
    elif points <= 100:
        return "epic"
    else:
        return "legendary"


def get_rarity_color(rarity: str) -> str:
    """Получение цвета редкости"""
    data = _load_achievements()
    rarity_data = data.get("rarity", {})
    return rarity_data.get(rarity, {}).get("color", "#9ca3af")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/", summary="Получить все достижения")
async def get_all_achievements(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    include_hidden: bool = Query(False, description="Показать скрытые достижения")
):
    """
    Получение списка всех достижений.
    
    Параметры:
    - **category**: Фильтрация по категории (story, exploration, gameplay, stats, relationships, endings, challenges, meta)
    - **include_hidden**: Показать скрытые достижения (по умолчанию скрыты)
    """
    data = _load_achievements()
    achievements = data.get("achievements", {})
    
    result = []
    for ach_id, ach in achievements.items():
        # Пропускаем скрытые, если не запрошены
        if ach.get("hidden", False) and not include_hidden:
            continue
        
        # Фильтр по категории
        if category and ach.get("category") != category:
            continue
        
        rarity = get_rarity(ach.get("points", 0))
        
        result.append({
            "id": ach_id,
            "name": ach["name"],
            "description": ach["description"],
            "icon": ach["icon"],
            "category": ach["category"],
            "points": ach["points"],
            "hidden": ach.get("hidden", False),
            "rarity": rarity,
            "rarity_color": get_rarity_color(rarity)
        })
    
    # Сортировка по очкам
    result.sort(key=lambda x: x["points"], reverse=True)
    
    return {
        "total": len(result),
        "achievements": result
    }


@router.get("/categories", summary="Получить категории достижений")
async def get_achievement_categories():
    """
    Получение списка всех категорий достижений с описаниями.
    """
    data = _load_achievements()
    categories = data.get("categories", {})
    
    return {
        "total": len(categories),
        "categories": categories
    }


@router.get("/{achievement_id}", summary="Получить достижение по ID")
async def get_achievement(achievement_id: str):
    """
    Получение детальной информации о конкретном достижении.
    """
    data = _load_achievements()
    achievement = data.get("achievements", {}).get(achievement_id)
    
    if not achievement:
        raise HTTPException(
            status_code=404,
            detail=f"Достижение '{achievement_id}' не найдено"
        )
    
    rarity = get_rarity(achievement.get("points", 0))
    category_info = data.get("categories", {}).get(achievement.get("category"), {})
    
    return {
        "id": achievement_id,
        "name": achievement["name"],
        "description": achievement["description"],
        "icon": achievement["icon"],
        "category": achievement["category"],
        "category_info": category_info,
        "points": achievement["points"],
        "hidden": achievement.get("hidden", False),
        "rarity": rarity,
        "rarity_color": get_rarity_color(rarity),
        "requirement": achievement.get("requirement", {})
    }


@router.post("/check", summary="Проверить достижения игрока")
async def check_player_achievements(player_data: dict):
    """
    Проверка достижений для игрока.
    
    Отправьте данные игрока для проверки:
    ```json
    {
      "visited_scenes": ["start", "scene1", ...],
      "choices_made": 5,
      "decision_patterns": {"aggressive": 2, "diplomatic": 3, ...},
      "stats": {"health": 80, ...},
      "relationships": {"sara_nova": 90, ...},
      "ending_type": "awakening",
      "playtime_minutes": 15,
      "games_completed": 1
    }
    ```
    """
    data = _load_achievements()
    achievements = data.get("achievements", {})
    
    unlocked = []
    progress = {}
    
    for ach_id, ach in achievements.items():
        req = ach.get("requirement", {})
        req_type = req.get("type")
        is_unlocked = False
        current_progress = 0
        max_progress = 1
        
        if req_type == "scenes_visited":
            visited = set(player_data.get("visited_scenes", []))
            required = req.get("count", 1)
            current_progress = len(visited)
            max_progress = required
            is_unlocked = len(visited) >= required
            
        elif req_type == "all_scenes_visited":
            # Упрощённая проверка - в реальной игре нужно знать общее количество сцен
            visited = set(player_data.get("visited_scenes", []))
            current_progress = len(visited)
            max_progress = 58  # Количество сцен в игре
            is_unlocked = len(visited) >= 58
            
        elif req_type == "choice_pattern":
            pattern = req.get("pattern", "")
            required = req.get("count", 1)
            patterns = player_data.get("decision_patterns", {})
            current_progress = patterns.get(pattern, 0)
            max_progress = required
            is_unlocked = current_progress >= required
            
        elif req_type == "final_stat":
            stat = req.get("stat", "")
            min_val = req.get("min", 0)
            max_val = req.get("max", 100)
            stats = player_data.get("stats", {})
            stat_value = stats.get(stat, 0)
            current_progress = stat_value
            max_progress = 100
            if min_val > 0:
                is_unlocked = stat_value >= min_val
            elif max_val < 100:
                is_unlocked = stat_value <= max_val and stat_value > 0
                
        elif req_type == "stat_maxed":
            stat = req.get("stat", "")
            stats = player_data.get("stats", {})
            stat_value = stats.get(stat, 0)
            current_progress = stat_value
            max_progress = 100
            is_unlocked = stat_value >= 100
            
        elif req_type == "stat_threshold":
            stat = req.get("stat", "")
            min_val = req.get("min", 0)
            stats = player_data.get("stats", {})
            stat_value = stats.get(stat, 0)
            current_progress = stat_value
            max_progress = min_val
            is_unlocked = stat_value >= min_val
            
        elif req_type == "relationship_max":
            char = req.get("character", "")
            relationships = player_data.get("relationships", {})
            rel_value = relationships.get(char, 0)
            current_progress = rel_value
            max_progress = 100
            is_unlocked = rel_value >= 100
            
        elif req_type == "ending":
            ending = req.get("ending", "")
            player_ending = player_data.get("ending_type", "")
            is_unlocked = player_ending == ending
            
        elif req_type == "playtime":
            max_minutes = req.get("max_minutes", 999)
            playtime = player_data.get("playtime_minutes", 0)
            current_progress = playtime
            max_progress = max_minutes
            is_unlocked = playtime <= max_minutes and playtime > 0
            
        elif req_type == "no_pattern":
            pattern = req.get("pattern", "")
            patterns = player_data.get("decision_patterns", {})
            is_unlocked = patterns.get(pattern, 0) == 0 and player_data.get("games_completed", 0) > 0
            
        elif req_type == "games_completed":
            required = req.get("count", 1)
            completed = player_data.get("games_completed", 0)
            current_progress = completed
            max_progress = required
            is_unlocked = completed >= required
        
        # Записываем прогресс
        progress[ach_id] = {
            "current": current_progress,
            "max": max_progress,
            "percentage": min(100, (current_progress / max_progress * 100)) if max_progress > 0 else 0
        }
        
        if is_unlocked:
            rarity = get_rarity(ach.get("points", 0))
            unlocked.append({
                "id": ach_id,
                "name": ach["name"],
                "description": ach["description"],
                "icon": ach["icon"],
                "points": ach["points"],
                "rarity": rarity,
                "rarity_color": get_rarity_color(rarity),
                "unlocked_at": datetime.utcnow().isoformat()
            })
    
    # Сортировка разблокированных по очкам
    unlocked.sort(key=lambda x: x["points"], reverse=True)
    
    total_points = sum(a["points"] for a in unlocked)
    
    return {
        "unlocked_count": len(unlocked),
        "total_count": len(achievements),
        "total_points": total_points,
        "achievements": unlocked,
        "progress": progress
    }


@router.get("/stats/summary", summary="Статистика достижений")
async def get_achievements_stats():
    """
    Получение общей статистики по достижениям.
    """
    data = _load_achievements()
    achievements = data.get("achievements", {})
    
    # Подсчёт по категориям
    by_category = {}
    by_rarity = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0}
    hidden_count = 0
    total_points = 0
    
    for ach in achievements.values():
        category = ach.get("category", "unknown")
        by_category[category] = by_category.get(category, 0) + 1
        
        rarity = get_rarity(ach.get("points", 0))
        by_rarity[rarity] += 1
        
        if ach.get("hidden", False):
            hidden_count += 1
        
        total_points += ach.get("points", 0)
    
    return {
        "total_achievements": len(achievements),
        "total_points": total_points,
        "hidden_count": hidden_count,
        "by_category": by_category,
        "by_rarity": by_rarity
    }
