"""
StarCourier Web - Quests API Router
API endpoints для системы квестов

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
DATA_FILE = Path(__file__).parent.parent / "data" / "quests.json"


def load_quests_data() -> dict:
    """Загрузить данные о квестах из JSON"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Quests data file not found")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing quests JSON: {e}")
        return {}


@router.get("", response_model=Dict, summary="Получить все квесты")
async def get_all_quests():
    """
    Получить все квесты из системы.
    
    Включает основные квесты, побочные, квесты путей и финальные квесты.
    """
    return load_quests_data()


@router.get("/metadata", response_model=Dict, summary="Метаданные системы квестов")
async def get_quests_metadata():
    """
    Получить метаданные системы квестов.
    """
    data = load_quests_data()
    return data.get("metadata", {})


@router.get("/by-chapter/{chapter}", response_model=Dict, summary="Получить квесты по главе")
async def get_quests_by_chapter(chapter: int):
    """
    Получить все квесты для определённой главы.
    
    Полезно для отображения доступных квестов в текущей главе игры.
    """
    if chapter < 1 or chapter > 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter must be between 1 and 18"
        )
    
    data = load_quests_data()
    result = {}
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        if quest.get("chapter") == chapter:
            result[quest_id] = quest
    
    return result


@router.get("/by-type/{quest_type}", response_model=Dict, summary="Получить квесты по типу")
async def get_quests_by_type(quest_type: str):
    """
    Получить квесты определённого типа.
    
    Типы квестов:
    - **main** — Основные сюжетные квесты
    - **side** — Побочные квесты
    - **path** — Квесты пути (Альянс/Наблюдатель/Независимость)
    - **ability** — Квесты для получения способностей
    - **ending** — Финальные квесты
    """
    data = load_quests_data()
    result = {}
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        if quest.get("type") == quest_type:
            result[quest_id] = quest
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quests found for type '{quest_type}'"
        )
    
    return result


@router.get("/by-path/{path}", response_model=Dict, summary="Получить квесты пути")
async def get_path_quests(path: str):
    """
    Получить квесты для определённого пути.
    
    Пути:
    - **alliance** — Путь Альянса
    - **observer** — Путь Наблюдателя
    - **independence** — Путь Независимости
    """
    valid_paths = ["alliance", "observer", "independence"]
    if path not in valid_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid path. Must be one of: {valid_paths}"
        )
    
    data = load_quests_data()
    result = {}
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        if quest.get("path") == path:
            result[quest_id] = quest
    
    return result


@router.get("/quest/{quest_id}", response_model=Dict, summary="Получить квест по ID")
async def get_quest(quest_id: str):
    """
    Получить информацию о конкретном квесте по ID.
    
    - **quest_id**: ID квеста (например, q6_01, q13_01)
    """
    data = load_quests_data()
    
    if quest_id == "metadata":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot get metadata as a quest"
        )
    
    if quest_id not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quest '{quest_id}' not found"
        )
    
    return data[quest_id]


@router.get("/search", response_model=List[Dict], summary="Поиск квестов")
async def search_quests(
    query: str = Query(..., min_length=2),
    chapter: Optional[int] = Query(None, ge=1, le=18)
):
    """
    Поиск квестов по названию или описанию.
    
    - **query**: Поисковый запрос (минимум 2 символа)
    - **chapter**: Опционально, ограничить поиск конкретной главой
    """
    data = load_quests_data()
    results = []
    query_lower = query.lower()
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        # Фильтр по главе
        if chapter and quest.get("chapter") != chapter:
            continue
        
        name = quest.get("name", "").lower()
        description = quest.get("description", "").lower()
        
        if query_lower in name or query_lower in description:
            results.append({
                "id": quest.get("id"),
                "quest_id": quest_id,
                "name": quest.get("name"),
                "description": quest.get("description"),
                "chapter": quest.get("chapter"),
                "type": quest.get("type")
            })
    
    return results


@router.get("/available", response_model=List[Dict], summary="Доступные квесты для игрока")
async def get_available_quests(
    current_chapter: int = Query(1, ge=1, le=18),
    completed_quests: Optional[str] = Query(None),
    path: Optional[str] = Query(None),
    character_level: int = Query(1, ge=1, le=100),
    user: User = Depends(get_current_user)
):
    """
    Получить квесты, доступные для текущего состояния игрока.
    
    - **current_chapter**: Текущая глава (1-18)
    - **completed_quests**: Список завершённых квестов через запятую
    - **path**: Выбранный путь (alliance/observer/independence)
    - **character_level**: Уровень персонажа (1-100)
    """
    data = load_quests_data()
    completed_quests_list = completed_quests.split(",") if completed_quests else []
    available = []
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        # Проверка главы
        if quest.get("chapter") != current_chapter:
            continue
        
        # Проверка пути
        quest_path = quest.get("path")
        if quest_path and path != quest_path:
            continue
        
        # Проверка требуемых квестов
        requires = quest.get("requires", [])
        if isinstance(requires, str):
            requires = [requires]
        
        if requires and not all(rq in completed_quests_list for rq in requires):
            continue
        
        # Проверка уровня
        level_req = quest.get("level_required", 1)
        if character_level < level_req:
            continue
        
        available.append({
            "id": quest.get("id"),
            "quest_id": quest_id,
            "name": quest.get("name"),
            "description": quest.get("description"),
            "type": quest.get("type"),
            "objectives": quest.get("objectives", []),
            "rewards": quest.get("rewards", {})
        })
    
    return available


@router.get("/main-story", response_model=List[Dict], summary="Основные сюжетные квесты")
async def get_main_story_quests(
    up_to_chapter: int = Query(18, ge=1, le=18)
):
    """
    Получить все основные сюжетные квесты до определённой главы.
    
    - **up_to_chapter**: Максимальная глава для включения квестов
    """
    data = load_quests_data()
    result = []
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        if quest.get("type") == "main" and quest.get("chapter", 0) <= up_to_chapter:
            result.append({
                "id": quest.get("id"),
                "quest_id": quest_id,
                "name": quest.get("name"),
                "description": quest.get("description"),
                "chapter": quest.get("chapter"),
                "objectives": quest.get("objectives", []),
                "rewards": quest.get("rewards", {}),
                "unlocks": quest.get("unlocks", [])
            })
    
    # Сортировка по главе
    result.sort(key=lambda x: x.get("chapter", 0))
    
    return result


@router.get("/ending-quests", response_model=List[Dict], summary="Финальные квесты")
async def get_ending_quests():
    """
    Получить все финальные квесты (концовки).
    
    Включает квесты для трёх концовок:
    - Изгнание
    - Договор
    - Слияние
    """
    data = load_quests_data()
    result = []
    
    for quest_id, quest in data.items():
        if quest_id == "metadata":
            continue
        
        if quest.get("type") == "ending" or quest.get("ending_quest"):
            result.append({
                "id": quest.get("id"),
                "quest_id": quest_id,
                "name": quest.get("name"),
                "description": quest.get("description"),
                "ending": quest.get("ending"),
                "requirement": quest.get("requirement"),
                "objectives": quest.get("objectives", []),
                "rewards": quest.get("rewards", {})
            })
    
    return result


@router.get("/rewards/{quest_id}", response_model=Dict, summary="Награды за квест")
async def get_quest_rewards(quest_id: str):
    """
    Получить информацию о наградах за квест.
    """
    data = load_quests_data()
    
    if quest_id not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quest '{quest_id}' not found"
        )
    
    quest = data[quest_id]
    return {
        "quest_id": quest_id,
        "name": quest.get("name"),
        "rewards": quest.get("rewards", {})
    }


@router.get("/tree/{quest_id}", response_model=Dict, summary="Дерево зависимостей квеста")
async def get_quest_tree(quest_id: str):
    """
    Получить дерево зависимостей квеста.
    
    Показывает, какие квесты требуются для этого квеста
    и какие квесты разблокируются после его завершения.
    """
    data = load_quests_data()
    
    if quest_id not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quest '{quest_id}' not found"
        )
    
    quest = data[quest_id]
    
    # Поиск квестов, которые требуют этот квест
    unlocks = []
    for qid, q in data.items():
        if qid == "metadata":
            continue
        
        requires = q.get("requires", [])
        if isinstance(requires, str):
            requires = [requires]
        
        if quest_id in requires:
            unlocks.append({
                "id": q.get("id"),
                "quest_id": qid,
                "name": q.get("name")
            })
    
    return {
        "quest_id": quest_id,
        "name": quest.get("name"),
        "requires": quest.get("requires", []),
        "unlocks": unlocks
    }
