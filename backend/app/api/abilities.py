"""
StarCourier Web - Abilities API Router
API endpoints для системы способностей

Автор: QuadDarv1ne
Версия: 2.0.0
"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.services.auth_service import get_current_user
from app.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Путь к файлу с данными
DATA_FILE = Path(__file__).parent.parent / "data" / "abilities.json"


def load_abilities_data() -> dict:
    """Загрузить данные о способностях из JSON"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Abilities data file not found")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing abilities JSON: {e}")
        return {}


@router.get("", response_model=Dict, summary="Получить все способности")
async def get_all_abilities():
    """
    Получить все способности из системы.
    
    Возвращает структуру со всеми ветками способностей:
    - alchemy (Алхимия)
    - biotics (Биотика)
    - psychic (Психика)
    - resonance (Резонанс)
    - carrier (Перевозка)
    - path (Путь)
    - final_battle (Финальная битва)
    """
    return load_abilities_data()


@router.get("/branches", response_model=List[str], summary="Получить список веток способностей")
async def get_ability_branches():
    """
    Получить список всех веток способностей.
    """
    data = load_abilities_data()
    metadata = data.get("metadata", {})
    return metadata.get("branches", [])


@router.get("/branch/{branch_name}", response_model=Dict, summary="Получить способности ветки")
async def get_branch_abilities(branch_name: str):
    """
    Получить все способности определённой ветки.
    
    Ветки:
    - **alchemy** — Алхимические рецепты и препараты
    - **biotics** — Биотические способности
    - **psychic** — Психические способности
    - **resonance** — Система Резонанса
    - **carrier** — Улучшения корабля
    - **path** — Способности пути (Альянс/Наблюдатель/Независимость)
    - **final_battle** — Способности для финальной битвы
    """
    data = load_abilities_data()
    
    if branch_name not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch '{branch_name}' not found. Available: {list(data.keys())}"
        )
    
    return data[branch_name]


@router.get("/ability/{ability_id}", response_model=Dict, summary="Получить способность по ID")
async def get_ability(ability_id: str, branch: Optional[str] = Query(None)):
    """
    Получить информацию о конкретной способности по ID.
    
    - **ability_id**: ID способности (например, alc_50, psy_100)
    - **branch**: Опционально, ветка способности для ускорения поиска
    """
    data = load_abilities_data()
    
    # Поиск по всем веткам
    for branch_name, abilities in data.items():
        if branch_name == "metadata":
            continue
        
        # Если указана ветка, пропускаем другие
        if branch and branch_name != branch:
            continue
        
        # Поиск в текущей ветке
        for key, ability in abilities.items():
            if ability.get("id") == ability_id or key == ability_id:
                return ability
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ability '{ability_id}' not found"
    )


@router.get("/by-level", response_model=Dict, summary="Получить способности по уровню")
async def get_abilities_by_level(
    min_level: int = Query(1, ge=1, le=100),
    max_level: int = Query(100, ge=1, le=100)
):
    """
    Получить способности, доступные в диапазоне уровней.
    
    - **min_level**: Минимальный уровень (1-100)
    - **max_level**: Максимальный уровень (1-100)
    """
    data = load_abilities_data()
    result = {}
    
    for branch_name, abilities in data.items():
        if branch_name == "metadata":
            continue
        
        branch_abilities = {}
        for key, ability in abilities.items():
            level_req = ability.get("level_required", 1)
            if min_level <= level_req <= max_level:
                branch_abilities[key] = ability
        
        if branch_abilities:
            result[branch_name] = branch_abilities
    
    return result


@router.get("/by-chapter/{chapter}", response_model=Dict, summary="Получить способности по главе")
async def get_abilities_by_chapter(chapter: int):
    """
    Получить способности, доступные в определённой главе.
    
    Полезно для фильтрации способностей по прогрессу игры.
    """
    if chapter < 1 or chapter > 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter must be between 1 and 18"
        )
    
    data = load_abilities_data()
    result = {}
    
    for branch_name, abilities in data.items():
        if branch_name == "metadata":
            continue
        
        branch_abilities = {}
        for key, ability in abilities.items():
            chapters = ability.get("chapters", [])
            if chapter in chapters:
                branch_abilities[key] = ability
        
        if branch_abilities:
            result[branch_name] = branch_abilities
    
    return result


@router.get("/search", response_model=List[Dict], summary="Поиск способностей")
async def search_abilities(
    query: str = Query(..., min_length=2),
    branch: Optional[str] = Query(None)
):
    """
    Поиск способностей по названию или описанию.
    
    - **query**: Поисковый запрос (минимум 2 символа)
    - **branch**: Опционально, ограничить поиск конкретной веткой
    """
    data = load_abilities_data()
    results = []
    query_lower = query.lower()
    
    for branch_name, abilities in data.items():
        if branch_name == "metadata":
            continue
        
        if branch and branch_name != branch:
            continue
        
        for key, ability in abilities.items():
            name = ability.get("name", "").lower()
            description = ability.get("description", "").lower()
            
            if query_lower in name or query_lower in description:
                results.append({
                    "id": ability.get("id"),
                    "key": key,
                    "name": ability.get("name"),
                    "description": ability.get("description"),
                    "branch": branch_name,
                    "level_required": ability.get("level_required")
                })
    
    return results


@router.get("/available", response_model=List[Dict], summary="Доступные способности для персонажа")
async def get_available_abilities(
    character_level: int = Query(1, ge=1, le=100),
    current_chapter: int = Query(1, ge=1, le=18),
    path: Optional[str] = Query(None),
    completed_quests: Optional[str] = Query(None),
    user: User = Depends(get_current_user)
):
    """
    Получить способности, доступные для текущего состояния персонажа.
    
    - **character_level**: Уровень персонажа (1-100)
    - **current_chapter**: Текущая глава (1-18)
    - **path**: Выбранный путь (alliance/observer/independence)
    - **completed_quests**: Список завершённых квестов через запятую
    """
    data = load_abilities_data()
    completed_quests_list = completed_quests.split(",") if completed_quests else []
    available = []
    
    for branch_name, abilities in data.items():
        if branch_name == "metadata":
            continue
        
        # Обработка способностей пути
        if branch_name == "path":
            if path and path in abilities:
                for key, ability in abilities[path].items():
                    unlock = ability.get("unlock", "")
                    if path in unlock and f"chapter_{current_chapter}" in unlock.lower():
                        available.append({
                            "id": ability.get("id"),
                            "name": ability.get("name"),
                            "description": ability.get("description"),
                            "branch": branch_name,
                            "path": path
                        })
            continue
        
        # Проверка остальных способностей
        for key, ability in abilities.items():
            level_req = ability.get("level_required", 1)
            chapters = ability.get("chapters", [])
            quest_unlock = ability.get("quest_unlock")
            quest_requirement = ability.get("quest_requirement")
            
            # Проверка уровня
            if character_level < level_req:
                continue
            
            # Проверка главы
            if chapters and current_chapter not in chapters:
                continue
            
            # Проверка квеста
            if quest_unlock and quest_unlock not in completed_quests_list:
                continue
            
            if quest_requirement and quest_requirement not in completed_quests_list:
                continue
            
            available.append({
                "id": ability.get("id"),
                "name": ability.get("name"),
                "description": ability.get("description"),
                "branch": branch_name,
                "level_required": level_req
            })
    
    return available


@router.get("/metadata", response_model=Dict, summary="Метаданные системы способностей")
async def get_abilities_metadata():
    """
    Получить метаданные системы способностей.
    
    Включает версию, описание и список веток.
    """
    data = load_abilities_data()
    return data.get("metadata", {})
