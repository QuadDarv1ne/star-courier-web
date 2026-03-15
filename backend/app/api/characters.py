"""
StarCourier Web - Characters API Router
API endpoints для персонажей

Автор: QuadDarv1ne
Версия: 1.1.0
"""

import logging
from typing import Dict

from fastapi import APIRouter, HTTPException, status

from app.models.game import CharacterInfo
from app.services.data_service import get_characters, get_character

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=Dict[str, CharacterInfo],
            summary="Получить всех персонажей")
async def list_characters() -> Dict[str, CharacterInfo]:
    """
    Получить список всех персонажей игры.

    Возвращает словарь с информацией о всех персонажах.
    
    Returns:
        Dict[str, CharacterInfo]: Словарь персонажей по ID
    """
    characters: Dict[str, dict] = get_characters()
    result: Dict[str, CharacterInfo] = {}

    for char_id, char_data in characters.items():
        result[char_id] = CharacterInfo(
            id=char_id,
            name=char_data.get("name", "Неизвестный"),
            role=char_data.get("role", ""),
            description=char_data.get("description", ""),
            relationship=char_data.get("initial_relationship", 50),
            avatar=char_data.get("avatar")
        )

    return result


@router.get("/{character_id}", response_model=CharacterInfo,
            summary="Получить персонажа по ID")
async def get_character_by_id(character_id: str) -> CharacterInfo:
    """
    Получить детальную информацию о персонаже по его ID.

    Args:
        character_id: Уникальный идентификатор персонажа
        
    Returns:
        CharacterInfo: Информация о персонаже
        
    Raises:
        HTTPException: 404 если персонаж не найден
    """
    char_data: Dict = get_character(character_id)

    if not char_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Персонаж '{character_id}' не найден"
        )

    return CharacterInfo(
        id=character_id,
        name=char_data.get("name", "Неизвестный"),
        role=char_data.get("role", ""),
        description=char_data.get("description", ""),
        relationship=char_data.get("initial_relationship", 50),
        avatar=char_data.get("avatar")
    )
