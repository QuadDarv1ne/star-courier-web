"""
Сервис игровых механик для глав 11-18
Управляет системами: Резонанс, Пути, Финалы, Ментальное состояние
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger('game_mechanics')


class PathType(Enum):
    """Типы путей развития"""
    ALLIANCE = "alliance"  # Альянс - флот, ресурсы, официальная поддержка
    OBSERVER = "observer"  # Наблюдатель - древние знания, Psychic усиление
    INDEPENDENCE = "independence"  # Независимость - свобода, сеть агентов


class EndingType(Enum):
    """Типы финалов"""
    EXILE = "exile"  # Изгнание - уничтожение якоря Сущности
    TREATY = "treaty"  # Договор - Хранительство Границы
    MERGE = "merge"  # Слияние - трансцендентная эволюция


@dataclass
class ResonanceSystem:
    """Система Резонанса"""
    level: int = 1  # 1-4
    experience: int = 0
    milestones: List[int] = field(default_factory=lambda: [0, 100, 300, 600])
    
    # Бонусы по уровням
    bonuses: Dict[int, Dict[str, Any]] = field(default_factory=lambda: {
        1: {"anomaly_detection_radius": 100, "description": "Основы - обнаружение аномалий"},
        2: {"anomaly_detection_radius": 500, "psychic_bonus": 10, "description": "Усиление - восприятие слабых мест"},
        3: {"anomaly_navigation": True, "entity_communication": True, "description": "Мастерство - навигация через аномалии"},
        4: {"reality_manipulation": True, "merge_ending_unlock": True, "description": "Трансцендентный - манипуляция реальностью"}
    })
    
    def gain_experience(self, amount: int) -> Dict[str, Any]:
        """Получить опыт Резонанса"""
        self.experience += amount
        result = {"gained": amount, "total": self.experience, "level_up": False}
        
        # Проверка повышения уровня
        if self.level < 4 and self.experience >= self.milestones[self.level]:
            self.level += 1
            result["level_up"] = True
            result["new_level"] = self.level
            result["bonus"] = self.bonuses.get(self.level, {})
            logger.info(f"Резонанс повышен до уровня {self.level}")
        
        return result
    
    def get_current_bonus(self) -> Dict[str, Any]:
        """Получить текущий бонус Резонанса"""
        return self.bonuses.get(self.level, {})


@dataclass
class MentalState:
    """Система ментального состояния"""
    mental_health: int = 100  # 0-100 (100 = идеально)
    entity_influence: int = 0  # 0-100 (0 = чист)
    corruption_risk: int = 0  # 0-100 (вероятность падения)
    
    # Пороги эффектов
    thresholds: Dict[str, List[int]] = field(default_factory=lambda: {
        "normal": [80, 100],
        "hallucinations": [60, 79],
        "visions": [40, 59],
        "serious": [20, 39],
        "critical": [0, 19]
    })
    
    def get_state(self) -> str:
        """Получить текущее состояние"""
        for state, (min_val, max_val) in self.thresholds.items():
            if min_val <= self.mental_health <= max_val:
                return state
        return "unknown"
    
    def get_effects(self) -> Dict[str, Any]:
        """Получить эффекты текущего состояния"""
        state = self.get_state()
        effects = {
            "normal": {"description": "Нормальное состояние", "penalties": {}},
            "hallucinations": {"description": "Лёгкие галлюцинации", "penalties": {"psychic": -5}},
            "visions": {"description": "Видения, снижение навыков", "penalties": {"all_skills": -10}},
            "serious": {"description": "Серьёзные нарушения", "penalties": {"all_skills": -20, "merge_risk": True}},
            "critical": {"description": "Потеря контроля", "penalties": {"auto_merge_ending": True}}
        }
        return effects.get(state, effects["normal"])
    
    def change_health(self, amount: int) -> int:
        """Изменить ментальное здоровье"""
        self.mental_health = max(0, min(100, self.mental_health + amount))
        return self.mental_health
    
    def change_influence(self, amount: int) -> int:
        """Изменить влияние Сущности"""
        self.entity_influence = max(0, min(100, self.entity_influence + amount))
        # Влияние влияет на ментальное здоровье
        if amount > 0:
            self.mental_health = max(0, self.mental_health - amount // 2)
        return self.entity_influence
    
    def apply_psychic_protection(self, psychic_level: int) -> int:
        """Применить защиту от Psychic способностей"""
        protection = psychic_level // 10  # 10% защиты за каждые 10 Psychic
        self.corruption_risk = max(0, self.corruption_risk - protection)
        return protection


@dataclass
class PathProgress:
    """Прогресс пути"""
    path: Optional[PathType] = None
    progress: int = 0  # 0-100
    choices_made: List[str] = field(default_factory=list)
    resources_gained: Dict[str, int] = field(default_factory=dict)
    
    # Бонусы путей
    path_bonuses: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "alliance": {
            "credits": 5000,
            "fleet_support": True,
            "equipment_discount": 40,
            "description": "Флот, ресурсы, официальная поддержка"
        },
        "observer": {
            "psychic_boost": 20,
            "ancient_knowledge": True,
            "resonance_boost": 2,
            "description": "Древние знания, Psychic усиление"
        },
        "independence": {
            "network_access": True,
            "smuggler_routes": True,
            "mercenary_discount": 50,
            "description": "Свобода, сеть агентов"
        }
    })
    
    def choose_path(self, path_type: PathType) -> Dict[str, Any]:
        """Выбрать путь развития"""
        self.path = path_type
        bonus = self.path_bonuses.get(path_type.value, {})
        logger.info(f"Выбран путь: {path_type.value}")
        return {"path": path_type.value, "bonus": bonus}
    
    def add_progress(self, amount: int, choice_id: str = "") -> int:
        """Добавить прогресс пути"""
        self.progress = min(100, self.progress + amount)
        if choice_id:
            self.choices_made.append(choice_id)
        return self.progress
    
    def get_bonus(self) -> Dict[str, Any]:
        """Получить бонус текущего пути"""
        if not self.path:
            return {}
        return self.path_bonuses.get(self.path.value, {})


@dataclass
class EndingSystem:
    """Система финалов"""
    available_endings: List[EndingType] = field(default_factory=lambda: [EndingType.EXILE])
    ending_requirements: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "exile": {
            "description": "Изгнание - уничтожение якоря Сущности",
            "requirements": {},
            "price": "Жертва (Курьер или соратник)",
            "result": "Галактика спасена, Курьер связан с местом победы"
        },
        "treaty": {
            "description": "Договор - Хранительство Границы",
            "requirements": {"psychic": 70, "or_empathy": 80},
            "price": "Вечное Хранительство",
            "result": "Ограниченное сосуществование"
        },
        "merge": {
            "description": "Слияние - трансцендентная эволюция",
            "requirements": {"psychic": 90, "resonance_level": 4},
            "price": "Потеря части человечности",
            "result": "Трансцендентная эволюция"
        }
    })
    
    def unlock_ending(self, ending_type: EndingType) -> bool:
        """Разблокировать финал"""
        if ending_type not in self.available_endings:
            self.available_endings.append(ending_type)
            logger.info(f"Разблокирован финал: {ending_type.value}")
            return True
        return False
    
    def check_requirements(self, ending_type: EndingType, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Проверить требования для финала"""
        ending_key = ending_type.value
        requirements = self.ending_requirements.get(ending_key, {}).get("requirements", {})
        
        result = {
            "available": ending_type in self.available_endings,
            "requirements_met": True,
            "missing": []
        }
        
        # Проверка Psychic
        if "psychic" in requirements:
            if player_stats.get("psychic", 0) < requirements["psychic"]:
                result["requirements_met"] = False
                result["missing"].append(f"Psychic {requirements['psychic']}+")
        
        # Проверка Empathy (альтернатива для Treaty)
        if "or_empathy" in requirements and ending_key == "treaty":
            if player_stats.get("empathy", 0) >= requirements["or_empathy"]:
                result["requirements_met"] = True
                result["missing"] = []
        
        # Проверка Резонанса
        if "resonance_level" in requirements:
            if player_stats.get("resonance_level", 1) < requirements["resonance_level"]:
                result["requirements_met"] = False
                result["missing"].append(f"Resonance Level {requirements['resonance_level']}")
        
        return result
    
    def get_ending_info(self, ending_type: EndingType) -> Dict[str, Any]:
        """Получить информацию о финале"""
        key = ending_type.value
        info = self.ending_requirements.get(key, {})
        info["type"] = key
        info["unlocked"] = ending_type in self.available_endings
        return info


class GameMechanicsManager:
    """Менеджер игровых механик"""
    
    def __init__(self):
        self.resonance = ResonanceSystem()
        self.mental_state = MentalState()
        self.path_progress = PathProgress()
        self.ending_system = EndingSystem()
        self.player_stats: Dict[str, Any] = {}
    
    def initialize_player(self, stats: Dict[str, Any]):
        """Инициализировать игрока"""
        self.player_stats = stats
        # Загрузка сохранённых данных
        if "resonance_level" in stats:
            self.resonance.level = stats["resonance_level"]
            self.resonance.experience = stats.get("resonance_experience", 0)
        if "mental_health" in stats:
            self.mental_state.mental_health = stats["mental_health"]
            self.mental_state.entity_influence = stats.get("entity_influence", 0)
        if "path" in stats:
            try:
                self.path_progress.path = PathType(stats["path"])
            except ValueError:
                pass
        if "ending_available" in stats:
            for ending in stats["ending_available"]:
                try:
                    self.ending_system.unlock_ending(EndingType(ending))
                except ValueError:
                    pass
    
    def get_player_state(self) -> Dict[str, Any]:
        """Получить состояние игрока"""
        return {
            "resonance": {
                "level": self.resonance.level,
                "experience": self.resonance.experience,
                "bonus": self.resonance.get_current_bonus()
            },
            "mental_state": {
                "health": self.mental_state.mental_health,
                "influence": self.mental_state.entity_influence,
                "state": self.mental_state.get_state(),
                "effects": self.mental_state.get_effects()
            },
            "path": {
                "type": self.path_progress.path.value if self.path_progress.path else None,
                "progress": self.path_progress.progress,
                "bonus": self.path_progress.get_bonus()
            },
            "endings": {
                "available": [e.value for e in self.ending_system.available_endings],
                "requirements": {
                    ending.value: self.ending_system.check_requirements(ending, self.player_stats)
                    for ending in self.ending_system.available_endings
                }
            }
        }
    
    def gain_resonance_exp(self, amount: int) -> Dict[str, Any]:
        """Получить опыт Резонанса"""
        return self.resonance.gain_experience(amount)
    
    def choose_path(self, path_type: str) -> Dict[str, Any]:
        """Выбрать путь развития"""
        try:
            path = PathType(path_type)
            return self.path_progress.choose_path(path)
        except ValueError:
            return {"error": f"Неизвестный путь: {path_type}"}
    
    def update_mental_state(self, health_change: int = 0, influence_change: int = 0) -> Dict[str, Any]:
        """Обновить ментальное состояние"""
        if health_change != 0:
            self.mental_state.change_health(health_change)
        if influence_change != 0:
            self.mental_state.change_influence(influence_change)
        
        return {
            "health": self.mental_state.mental_health,
            "influence": self.mental_state.entity_influence,
            "state": self.mental_state.get_state(),
            "effects": self.mental_state.get_effects()
        }
    
    def check_ending_availability(self, ending_type: str) -> Dict[str, Any]:
        """Проверить доступность финала"""
        try:
            ending = EndingType(ending_type)
            return self.ending_system.check_requirements(ending, self.player_stats)
        except ValueError:
            return {"error": f"Неизвестный финал: {ending_type}"}
    
    def apply_path_bonus(self, bonus_type: str) -> int:
        """Применить бонус пути"""
        if not self.path_progress.path:
            return 0
        
        bonus = self.path_progress.get_bonus()
        if bonus_type in bonus:
            return bonus[bonus_type]
        return 0
    
    def entity_contact(self, intensity: int) -> Dict[str, Any]:
        """Контакт с Сущностью"""
        influence_gain = intensity
        health_loss = intensity // 2
        corruption_gain = intensity // 3
        
        # Psychic защита
        psychic_protection = self.player_stats.get("psychic", 0) // 10
        influence_gain = max(0, influence_gain - psychic_protection)
        
        self.mental_state.change_influence(influence_gain)
        self.mental_state.change_health(-health_loss)
        self.mental_state.corruption_risk = min(100, self.mental_state.corruption_risk + corruption_gain)
        
        # Возможность разблокировки Resonance опыта
        resonance_exp = intensity // 2
        resonance_result = self.gain_resonance_exp(resonance_exp)
        
        return {
            "influence": self.mental_state.entity_influence,
            "health": self.mental_state.mental_health,
            "corruption_risk": self.mental_state.corruption_risk,
            "resonance": resonance_result,
            "state": self.mental_state.get_state()
        }
    
    def make_path_choice(self, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Сделать выбор, влияющий на путь"""
        path = choice_data.get("path")
        progress = choice_data.get("progress", 10)
        choice_id = choice_data.get("choice_id", "")

        # Если путь ещё не выбран, это влияет на выбор
        if not self.path_progress.path and path:
            # Устанавливаем путь
            path_enum = PathType(path) if isinstance(path, str) else path
            self.path_progress.path = path_enum
            self.path_progress.add_progress(progress * 2, choice_id)  # Удвоенный прогресс для первого выбора
        elif self.path_progress.path:
            # Сравниваем с учётом Enum
            path_value = path.value if hasattr(path, 'value') else path
            if self.path_progress.path.value == path_value:
                self.path_progress.add_progress(progress, choice_id)

        # Проверка на разблокировку Treaty финала
        if self.path_progress.progress >= 50:
            self.ending_system.unlock_ending(EndingType.TREATY)

        return {
            "path": self.path_progress.path.value if self.path_progress.path else None,
            "progress": self.path_progress.progress,
            "choices_made": len(self.path_progress.choices_made)
        }
    
    def get_resonance_description(self) -> str:
        """Получить описание текущего уровня Резонанса"""
        level = self.resonance.level
        descriptions = {
            1: "Вы чувствуете слабые искажения пространства вокруг.",
            2: "Аномалии становятся различимы, вы ощущаете присутствие Сущности.",
            3: "Вы можете навигировать через аномалии и общаться с Сущностью.",
            4: "Реальность подчиняется вашей воле. Вы на грани трансцендентности."
        }
        return descriptions.get(level, "Неизвестный уровень Резонанса.")


# Глобальный экземпляр (для использования в приложении)
_game_mechanics_manager: Optional[GameMechanicsManager] = None


def get_game_mechanics_manager() -> GameMechanicsManager:
    """Получить глобальный менеджер механик"""
    global _game_mechanics_manager
    if _game_mechanics_manager is None:
        _game_mechanics_manager = GameMechanicsManager()
    return _game_mechanics_manager


def reset_game_mechanics_manager():
    """Сбросить глобальный менеджер (для тестов)"""
    global _game_mechanics_manager
    _game_mechanics_manager = None
