"""
StarCourier Web - Scenes API Router
API endpoints для сцен (отладочные)

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from typing import Dict

from fastapi import APIRouter

from app.services.data_service import data_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=Dict[str, str],
            summary="Получить список всех сцен")
async def list_scenes():
    """
    Получить список всех сцен игры (только ID и названия).

    Полезно для отладки и навигации.
    """
    return data_service.get_scene_list()


@router.get("/count",
            summary="Получить количество сцен")
async def get_scenes_count():
    """
    Получить общее количество сцен в игре.
    """
    scenes = data_service.get_scenes()
    return {
        "total": len(scenes),
        "endings": sum(1 for s in scenes.values()
                       if "конец" in s.get("title", "").lower())
    }
