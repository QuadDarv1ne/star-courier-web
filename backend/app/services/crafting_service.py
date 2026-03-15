"""
StarCourier Web - Crafting System
Система крафта предметов

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime
import random


# ============================================================================
# ENUMS
# ============================================================================

class CraftingSkill(str, Enum):
    """Навыки крафта"""
    ALCHEMY = "alchemy"
    BIOTICS = "biotics"
    TECHNOLOGY = "technology"
    ENGINEERING = "engineering"


class CraftingResult(str, Enum):
    """Результат крафта"""
    SUCCESS = "success"
    CRITICAL_SUCCESS = "critical_success"
    FAILURE = "failure"
    CRITICAL_FAILURE = "critical_failure"


# ============================================================================
# MODELS
# ============================================================================

class CraftingMaterial(BaseModel):
    """Материал для крафта"""
    item_id: str = Field(..., description="ID предмета")
    quantity: int = Field(..., description="Требуемое количество", ge=1)


class CraftingRecipe(BaseModel):
    """
    Рецепт крафта
    
    Пример:
        CraftingRecipe(
            id="recipe_001",
            name="Энергетическая ячейка",
            skill=CraftingSkill.TECHNOLOGY,
            required_level=5,
            materials=[
                CraftingMaterial(item_id="material_001", quantity=5),
                CraftingMaterial(item_id="material_002", quantity=3)
            ],
            result_item_id="craft_001",
            result_quantity=1,
            craft_time=60
        )
    """
    id: str = Field(..., description="Уникальный ID рецепта")
    name: str = Field(..., description="Название рецепта")
    description: str = Field(..., description="Описание рецепта")
    
    # Требования
    skill: CraftingSkill = Field(..., description="Требуемый навык")
    required_level: int = Field(1, description="Требуемый уровень навыка", ge=1, le=10)
    required_psychic: int = Field(0, description="Требуемая психика", ge=0)
    
    # Материалы
    materials: List[CraftingMaterial] = Field(..., description="Требуемые материалы")
    
    # Результат
    result_item_id: str = Field(..., description="ID результата")
    result_quantity: int = Field(1, description="Количество результата", ge=1)
    
    # Время и шанс
    craft_time: int = Field(10, description="Время крафта в секундах", ge=1)
    base_success_chance: float = Field(1.0, description="Базовый шанс успеха", ge=0, le=1)
    
    # Метаданные
    icon: str = Field("🔨", description="Эмодзи иконка")
    category: str = Field("general", description="Категория рецепта")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Название должно быть от 2 до 100 символов')
        return v
    
    def get_success_chance(self, skill_level: int, psychic: int = 0) -> float:
        """
        Рассчитать шанс успеха
        
        Args:
            skill_level: Уровень навыка игрока
            psychic: Психика игрока
        
        Returns:
            float: Шанс успеха от 0 до 1
        """
        # Базовый шанс
        chance = self.base_success_chance
        
        # Бонус за уровень навыка
        if skill_level > self.required_level:
            chance += (skill_level - self.required_level) * 0.05
        
        # Бонус за психику
        if psychic >= self.required_psychic:
            chance += (psychic - self.required_psychic) * 0.01
        
        # Ограничиваем от 0.1 до 1.0
        return max(0.1, min(1.0, chance))


class CraftingSession(BaseModel):
    """Сессия крафта"""
    recipe_id: str = Field(..., description="ID рецепта")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    result: Optional[CraftingResult] = Field(None, description="Результат")
    quality: float = Field(0.0, description="Качество результата", ge=0, le=1)


class CraftingStats(BaseModel):
    """Статистика крафта"""
    total_crafted: int = Field(0, description="Всего скрафчено")
    successful: int = Field(0, description="Успешных")
    failed: int = Field(0, description="Неудачных")
    critical_successes: int = Field(0, description="Критических успехов")
    critical_failures: int = Field(0, description="Критических провалов")
    
    @property
    def success_rate(self) -> float:
        """Процент успеха"""
        if self.total_crafted == 0:
            return 0.0
        return self.successful / self.total_crafted


# ============================================================================
# CRAFTING MANAGER
# ============================================================================

class CraftingManager:
    """
    Менеджер крафта
    
    Управление крафтом:
    - Проверка рецептов
    - Расход материалов
    - Расчёт результатов
    - Прогресс навыка
    """
    
    def __init__(self):
        self.recipes: Dict[str, CraftingRecipe] = {}
        self.skill_levels: Dict[CraftingSkill, int] = {
            CraftingSkill.ALCHEMY: 1,
            CraftingSkill.BIOTICS: 1,
            CraftingSkill.TECHNOLOGY: 1,
            CraftingSkill.ENGINEERING: 1
        }
        self.skill_exp: Dict[CraftingSkill, int] = {
            skill: 0 for skill in CraftingSkill
        }
        self.stats: Dict[CraftingSkill, CraftingStats] = {
            skill: CraftingStats() for skill in CraftingSkill
        }
    
    def add_recipe(self, recipe: CraftingRecipe) -> None:
        """Добавить рецепт"""
        self.recipes[recipe.id] = recipe
    
    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """Получить рецепт"""
        return self.recipes.get(recipe_id)
    
    def can_craft(
        self,
        recipe: CraftingRecipe,
        available_items: Dict[str, int],
        player_stats: Dict[str, int]
    ) -> tuple[bool, str]:
        """
        Проверить, можно ли скрафтить
        
        Args:
            recipe: Рецепт
            available_items: Доступные предметы {item_id: quantity}
            player_stats: Статистика игрока
        
        Returns:
            tuple: (можно ли, причина)
        """
        # Проверка уровня навыка
        skill_level = self.skill_levels.get(recipe.skill, 1)
        if skill_level < recipe.required_level:
            return False, f"Требуется уровень навыка {recipe.required_level}"
        
        # Проверка психики
        if player_stats.get('psychic', 0) < recipe.required_psychic:
            return False, f"Требуется психика {recipe.required_psychic}"
        
        # Проверка материалов
        for material in recipe.materials:
            available = available_items.get(material.item_id, 0)
            if available < material.quantity:
                return False, f"Недостаточно {material.item_id}"
        
        return True, ""
    
    def craft(
        self,
        recipe: CraftingRecipe,
        available_items: Dict[str, int],
        player_stats: Dict[str, int]
    ) -> tuple[CraftingResult, str, Dict[str, Any]]:
        """
        Выполнить крафт
        
        Args:
            recipe: Рецепт
            available_items: Доступные предметы
            player_stats: Статистика игрока
        
        Returns:
            tuple: (результат, сообщение, данные)
        """
        # Проверка возможности
        can_craft, reason = self.can_craft(recipe, available_items, player_stats)
        if not can_craft:
            return CraftingResult.FAILURE, reason, {}
        
        # Расход материалов
        consumed_items = {}
        for material in recipe.materials:
            available_items[material.item_id] -= material.quantity
            consumed_items[material.item_id] = material.quantity
        
        # Расчёт результата
        skill_level = self.skill_levels.get(recipe.skill, 1)
        success_chance = recipe.get_success_chance(
            skill_level,
            player_stats.get('psychic', 0)
        )
        
        roll = random.random()
        
        # Определение результата
        if roll < 0.05:  # 5% критический провал
            result = CraftingResult.CRITICAL_FAILURE
            message = "Критический провал! Материалы потеряны."
            quantity = 0
        elif roll > 0.95:  # 5% критический успех
            result = CraftingResult.CRITICAL_SUCCESS
            message = "Критический успех! Получено x2 предметов."
            quantity = recipe.result_quantity * 2
        elif roll < success_chance:
            result = CraftingResult.SUCCESS
            message = "Успешный крафт!"
            quantity = recipe.result_quantity
        else:
            result = CraftingResult.FAILURE
            message = "Крафт не удался. Материалы потеряны."
            quantity = 0
        
        # Обновление статистики
        self._update_stats(recipe.skill, result)
        
        # Опыт за крафт
        exp_gained = 0
        if result in [CraftingResult.SUCCESS, CraftingResult.CRITICAL_SUCCESS]:
            exp_gained = self._calculate_exp(recipe, result)
            self._add_exp(recipe.skill, exp_gained)
        
        return result, message, {
            'result_item_id': recipe.result_item_id,
            'quantity': quantity,
            'consumed_items': consumed_items,
            'exp_gained': exp_gained,
            'skill_level': self.skill_levels[recipe.skill]
        }
    
    def _update_stats(self, skill: CraftingSkill, result: CraftingResult) -> None:
        """Обновить статистику"""
        stats = self.stats[skill]
        stats.total_crafted += 1
        
        if result == CraftingResult.SUCCESS:
            stats.successful += 1
        elif result == CraftingResult.CRITICAL_SUCCESS:
            stats.successful += 1
            stats.critical_successes += 1
        elif result == CraftingResult.FAILURE:
            stats.failed += 1
        elif result == CraftingResult.CRITICAL_FAILURE:
            stats.failed += 1
            stats.critical_failures += 1
    
    def _calculate_exp(self, recipe: CraftingRecipe, result: CraftingResult) -> int:
        """Рассчитать полученный опыт"""
        base_exp = recipe.required_level * 10
        
        if result == CraftingResult.CRITICAL_SUCCESS:
            base_exp *= 2
        
        return base_exp
    
    def _add_exp(self, skill: CraftingSkill, exp: int) -> None:
        """Добавить опыт навыку"""
        self.skill_exp[skill] += exp
        
        # Проверка повышения уровня
        exp_needed = self.skill_levels[skill] * 100
        if self.skill_exp[skill] >= exp_needed:
            self.skill_levels[skill] += 1
            self.skill_exp[skill] -= exp_needed
    
    def get_available_recipes(
        self,
        player_stats: Dict[str, int]
    ) -> List[CraftingRecipe]:
        """Получить доступные рецепты"""
        available = []
        
        for recipe in self.recipes.values():
            skill_level = self.skill_levels.get(recipe.skill, 1)
            if skill_level >= recipe.required_level:
                if player_stats.get('psychic', 0) >= recipe.required_psychic:
                    available.append(recipe)
        
        return available


# ============================================================================
# RECIPE TEMPLATES
# ============================================================================

def create_starter_recipes() -> List[CraftingRecipe]:
    """Создать стартовые рецепты"""
    return [
        CraftingRecipe(
            id="recipe_medkit",
            name="Малая аптечка",
            description="Базовая медицина для путешествий",
            skill=CraftingSkill.BIOTICS,
            required_level=1,
            materials=[
                CraftingMaterial(item_id="herb_001", quantity=3),
                CraftingMaterial(item_id="cloth_001", quantity=1)
            ],
            result_item_id="medkit_small",
            result_quantity=1,
            craft_time=30,
            icon="💊"
        ),
        CraftingRecipe(
            id="recipe_energy_cell",
            name="Энергетическая ячейка",
            description="Источник энергии для оружия",
            skill=CraftingSkill.TECHNOLOGY,
            required_level=2,
            materials=[
                CraftingMaterial(item_id="crystal_001", quantity=2),
                CraftingMaterial(item_id="metal_001", quantity=3)
            ],
            result_item_id="energy_cell",
            result_quantity=5,
            craft_time=60,
            icon="🔋"
        ),
        CraftingRecipe(
            id="recipe_alchemy_potion",
            name="Алхимический эликсир",
            description="Увеличивает психику на 10 минут",
            skill=CraftingSkill.ALCHEMY,
            required_level=3,
            required_psychic=20,
            materials=[
                CraftingMaterial(item_id="essence_001", quantity=1),
                CraftingMaterial(item_id="herb_rare_001", quantity=5)
            ],
            result_item_id="potion_psychic",
            result_quantity=1,
            craft_time=120,
            base_success_chance=0.8,
            icon="🧪"
        )
    ]


# ============================================================================
# EXPORT
# ============================================================================


__all__ = [
    # Enums
    'CraftingSkill',
    'CraftingResult',
    
    # Models
    'CraftingMaterial',
    'CraftingRecipe',
    'CraftingSession',
    'CraftingStats',
    
    # Manager
    'CraftingManager',
    
    # Templates
    'create_starter_recipes',
]
