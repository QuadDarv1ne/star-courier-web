"""
StarCourier Web - Data Service
Сервис для загрузки и кэширования данных игры

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

# Базовый путь к данным
DATA_DIR = Path(__file__).parent.parent / "data"


class DataService:
    """Сервис для работы с данными игры"""

    def __init__(self):
        self._scenes_cache: Optional[Dict[str, Any]] = None
        self._characters_cache: Optional[Dict[str, Any]] = None
        self._cache_valid = False

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Загрузка JSON файла"""
        filepath = DATA_DIR / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Загружен файл: {filename}")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Файл не найден: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON в {filename}: {e}")
            return {}

    def get_scenes(self) -> Dict[str, Any]:
        """Получить все сцены"""
        if self._scenes_cache is None:
            self._scenes_cache = self._load_json("scenes.json")
        return self._scenes_cache

    def get_scene(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Получить конкретную сцену по ID"""
        scenes = self.get_scenes()
        return scenes.get(scene_id)

    def get_characters(self) -> Dict[str, Any]:
        """Получить всех персонажей"""
        if self._characters_cache is None:
            self._characters_cache = self._load_json("characters.json")
        return self._characters_cache

    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Получить конкретного персонажа по ID"""
        characters = self.get_characters()
        return characters.get(character_id)

    def get_scene_list(self) -> Dict[str, str]:
        """Получить список всех сцен (ID + название)"""
        scenes = self.get_scenes()
        return {scene_id: scene_data.get("title", "Без названия")
                for scene_id, scene_data in scenes.items()}

    def get_initial_stats(self) -> Dict[str, int]:
        """Получить начальную статистику игрока"""
        return {
            "health": 100,
            "morale": 75,
            "knowledge": 30,
            "team": 50,
            "danger": 0,
            "security": 20,
            "fuel": 100,
            "money": 1000,
            "psychic": 0,
            "trust": 50
        }

    def get_initial_relationships(self) -> Dict[str, int]:
        """Получить начальные отношения с персонажами"""
        characters = self.get_characters()
        return {
            char_id: char_data.get("initial_relationship", 50)
            for char_id, char_data in characters.items()
            if char_id not in ["max_well"]  # Главный герой не в отношениях
        }

    def clear_cache(self) -> None:
        """Очистить кэш"""
        self._scenes_cache = None
        self._characters_cache = None
        self._cache_valid = False
        logger.info("🗑️ Кэш данных очищен")

    def reload_data(self) -> None:
        """Перезагрузить все данные"""
        self.clear_cache()
        self.get_scenes()
        self.get_characters()
        self._cache_valid = True
        logger.info("🔄 Данные перезагружены")


# Глобальный экземпляр сервиса
data_service = DataService()


# Удобные функции-обёртки
def get_scenes() -> Dict[str, Any]:
    """Получить все сцены"""
    return data_service.get_scenes()


def get_scene(scene_id: str) -> Optional[Dict[str, Any]]:
    """Получить сцену по ID"""
    return data_service.get_scene(scene_id)


def get_characters() -> Dict[str, Any]:
    """Получить всех персонажей"""
    return data_service.get_characters()


def get_character(character_id: str) -> Optional[Dict[str, Any]]:
    """Получить персонажа по ID"""
    return data_service.get_character(character_id)
