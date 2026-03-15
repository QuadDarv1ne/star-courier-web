"""
StarCourier Web - Inventory System
Система инвентаря для игры

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime


# ============================================================================
# ENUMS
# ============================================================================

class ItemRarity(str, Enum):
    """Редкость предмета"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ItemCategory(str, Enum):
    """Категория предмета"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"
    KEY_ITEM = "key_item"
    CRAFTING = "crafting"
    UPGRADE = "upgrade"


class ItemSubcategory(str, Enum):
    """Подкатегория предмета"""
    # Оружие
    PISTOL = "pistol"
    RIFLE = "rifle"
    ENERGY_WEAPON = "energy_weapon"
    MELEE = "melee"

    # Броня
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

    # Расходники
    HEALTH = "health"
    ENERGY_CELL = "energy_cell"
    BUFF = "buff"
    DEBUFF = "debuff"

    # Материалы
    COMMON_MATERIAL = "common_material"
    RARE_MATERIAL = "rare_material"
    EXOTIC = "exotic"


# ============================================================================
# MODELS
# ============================================================================

class ItemEffect(BaseModel):
    """Эффект предмета"""
    stat: str = Field(..., description="Статистика для изменения")
    value: int = Field(..., description="Значение изменения")
    duration: Optional[int] = Field(None, description="Длительность в секундах")
    is_buff: bool = Field(True, description="Это бафф или дебафф")


class Item(BaseModel):
    """
    Модель предмета
    
    Пример:
        Item(
            id="item_001",
            name="Энергетический меч",
            description="Меч из чистой энергии",
            category=ItemCategory.WEAPON,
            rarity=ItemRarity.RARE,
            value=500,
            weight=2.5,
            effects=[ItemEffect(stat="damage", value=25)]
        )
    """
    id: str = Field(..., description="Уникальный ID предмета")
    name: str = Field(..., description="Название предмета")
    description: str = Field(..., description="Описание предмета")
    category: ItemCategory = Field(..., description="Категория предмета")
    subcategory: Optional[ItemSubcategory] = Field(None, description="Подкатегория")
    rarity: ItemRarity = Field(default=ItemRarity.COMMON, description="Редкость")
    
    # Экономика
    value: int = Field(0, description="Стоимость в кредитах")
    weight: float = Field(0.0, description="Вес в кг")
    
    # Эффекты
    effects: List[ItemEffect] = Field(default_factory=list, description="Эффекты предмета")
    
    # Требования
    required_level: int = Field(0, description="Требуемый уровень")
    required_psychic: int = Field(0, description="Требуемая психика")
    
    # Метаданные
    icon: str = Field("📦", description="Эмодзи иконка")
    stackable: bool = Field(False, description="Можно складывать в стак")
    max_stack: int = Field(99, description="Максимум в стаке")
    tradeable: bool = Field(True, description="Можно торговать")
    
    # Временные метки
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Проверка названия"""
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Название должно быть от 2 до 100 символов')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Проверка описания"""
        if len(v) < 10 or len(v) > 1000:
            raise ValueError('Описание должно быть от 10 до 1000 символов')
        return v
    
    def get_rarity_color(self) -> str:
        """Получить цвет редкости"""
        colors = {
            ItemRarity.COMMON: "#9ca3af",
            ItemRarity.UNCOMMON: "#22c55e",
            ItemRarity.RARE: "#3b82f6",
            ItemRarity.EPIC: "#a855f7",
            ItemRarity.LEGENDARY: "#f59e0b",
            ItemRarity.ARTIFACT: "#ef4444"
        }
        return colors.get(self.rarity, "#9ca3af")
    
    def get_total_effect(self, stat: str) -> int:
        """Получить суммарный эффект на статистику"""
        return sum(
            effect.value for effect in self.effects 
            if effect.stat == stat and effect.is_buff
        )


class InventoryItem(BaseModel):
    """Предмет в инвентаре"""
    item: Item = Field(..., description="Предмет")
    quantity: int = Field(1, description="Количество", ge=1)
    equipped: bool = Field(False, description="Надето ли")
    acquired_at: datetime = Field(default_factory=datetime.utcnow, description="Когда получен")
    
    def get_total_weight(self) -> float:
        """Получить общий вес"""
        return self.item.weight * self.quantity
    
    def get_total_value(self) -> int:
        """Получить общую стоимость"""
        return self.item.value * self.quantity


class InventoryStats(BaseModel):
    """Статистика инвентаря"""
    total_items: int = Field(0, description="Всего предметов")
    total_weight: float = Field(0.0, description="Общий вес")
    total_value: int = Field(0, description="Общая стоимость")
    equipped_items: int = Field(0, description="Надетые предметы")
    categories: Dict[str, int] = Field(default_factory=dict, description="По категориям")


# ============================================================================
# INVENTORY MANAGER
# ============================================================================

class InventoryManager:
    """
    Менеджер инвентаря
    
    Управление инвентарём игрока:
    - Добавление/удаление предметов
    - Экипировка
    - Проверка требований
    - Ограничения по весу
    """
    
    def __init__(
        self,
        max_weight: float = 100.0,
        max_slots: int = 50
    ):
        self.max_weight = max_weight
        self.max_slots = max_slots
        self.items: Dict[str, InventoryItem] = {}
        self.equipped: Dict[str, InventoryItem] = {}
    
    def get_stats(self) -> InventoryStats:
        """Получить статистику инвентаря"""
        stats = InventoryStats(
            total_items=len(self.items),
            total_weight=sum(item.get_total_weight() for item in self.items.values()),
            total_value=sum(item.get_total_value() for item in self.items.values()),
            equipped_items=len(self.equipped),
            categories={}
        )
        
        # Подсчёт по категориям
        for item in self.items.values():
            cat = item.item.category.value
            stats.categories[cat] = stats.categories.get(cat, 0) + item.quantity
        
        return stats
    
    def can_add_item(self, item: Item, quantity: int = 1) -> tuple[bool, str]:
        """
        Проверить, можно ли добавить предмет
        
        Returns:
            tuple: (можно ли добавить, причина если нельзя)
        """
        # Проверка места
        if len(self.items) >= self.max_slots and item.id not in self.items:
            return False, "Инвентарь полон"
        
        # Проверка веса
        current_weight = sum(i.get_total_weight() for i in self.items.values())
        new_weight = item.weight * quantity
        
        if current_weight + new_weight > self.max_weight:
            return False, f"Превышен лимит веса ({current_weight + new_weight:.1f}/{self.max_weight} кг)"
        
        return True, ""
    
    def add_item(self, item: Item, quantity: int = 1) -> tuple[bool, str]:
        """
        Добавить предмет в инвентарь
        
        Returns:
            tuple: (успех, сообщение)
        """
        # Проверка возможности добавления
        can_add, reason = self.can_add_item(item, quantity)
        if not can_add:
            return False, reason
        
        # Если предмет уже есть и стакается
        if item.id in self.items and item.stackable:
            existing = self.items[item.id]
            existing.quantity += quantity
            return True, f"Добавлено {quantity} x {item.name}"
        
        # Новый предмет
        self.items[item.id] = InventoryItem(item=item, quantity=quantity)
        return True, f"Получен предмет: {item.name}"
    
    def remove_item(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        """
        Удалить предмет из инвентаря
        
        Returns:
            tuple: (успех, сообщение)
        """
        if item_id not in self.items:
            return False, "Предмет не найден"
        
        inv_item = self.items[item_id]
        
        # Нельзя удалить экипированный предмет
        if inv_item.equipped:
            return False, "Сначала снимите экипировку"
        
        # Удаляем полностью или частично
        if inv_item.quantity <= quantity:
            del self.items[item_id]
            return True, f"Удалено: {inv_item.item.name}"
        else:
            inv_item.quantity -= quantity
            return True, f"Удалено {quantity} x {inv_item.item.name}"
    
    def equip_item(self, item_id: str) -> tuple[bool, str]:
        """
        Экипировать предмет
        
        Returns:
            tuple: (успех, сообщение)
        """
        if item_id not in self.items:
            return False, "Предмет не найден"
        
        inv_item = self.items[item_id]
        
        # Проверка требований
        if inv_item.item.required_level > 0:
            return False, f"Требуется уровень {inv_item.item.required_level}"
        
        # Уже экипировано
        if inv_item.equipped:
            return False, "Предмет уже экипирован"
        
        # Снимаем предмет из того же слота
        slot = self._get_item_slot(inv_item.item)
        if slot and slot in self.equipped:
            self.unequip_item(slot)
        
        # Экипируем
        inv_item.equipped = True
        self.equipped[slot] = inv_item
        
        return True, f"Экипировано: {inv_item.item.name}"
    
    def unequip_item(self, item_id: str) -> tuple[bool, str]:
        """
        Снять предмет
        
        Returns:
            tuple: (успех, сообщение)
        """
        if item_id not in self.items:
            return False, "Предмет не найден"
        
        inv_item = self.items[item_id]
        
        if not inv_item.equipped:
            return False, "Предмет не экипирован"
        
        inv_item.equipped = False
        slot = self._get_item_slot(inv_item.item)
        if slot in self.equipped:
            del self.equipped[slot]
        
        return True, f"Снято: {inv_item.item.name}"
    
    def _get_item_slot(self, item: Item) -> str:
        """Получить слот для предмета"""
        slot_map = {
            ItemCategory.WEAPON: "weapon",
            ItemCategory.ARMOR: "armor",
            ItemSubcategory.SHIELD: "offhand",
            ItemSubcategory.PISTOL: "sidearm",
        }
        
        if item.subcategory and item.subcategory.value in slot_map:
            return slot_map[item.subcategory.value]
        
        return slot_map.get(item.category.value, "other")
    
    def get_equipped_bonuses(self) -> Dict[str, int]:
        """Получить бонусы от экипировки"""
        bonuses = {}
        
        for inv_item in self.equipped.values():
            for effect in inv_item.item.effects:
                if effect.is_buff:
                    bonuses[effect.stat] = bonuses.get(effect.stat, 0) + effect.value
        
        return bonuses
    
    def list_items(
        self,
        category: Optional[ItemCategory] = None,
        rarity: Optional[ItemRarity] = None
    ) -> List[InventoryItem]:
        """
        Получить список предметов с фильтрами
        
        Args:
            category: Фильтр по категории
            rarity: Фильтр по редкости
        
        Returns:
            List[InventoryItem]: Список предметов
        """
        items = list(self.items.values())
        
        if category:
            items = [i for i in items if i.item.category == category]
        
        if rarity:
            items = [i for i in items if i.item.rarity == rarity]
        
        return items


# ============================================================================
# ITEM TEMPLATES
# ============================================================================

def create_starter_items() -> List[Item]:
    """Создать стартовые предметы"""
    return [
        Item(
            id="starter_pistol",
            name="Стартовый пистолет",
            description="Стандартный энергетический пистолет",
            category=ItemCategory.WEAPON,
            subcategory=ItemSubcategory.PISTOL,
            rarity=ItemRarity.COMMON,
            value=100,
            weight=1.5,
            effects=[ItemEffect(stat="damage", value=10)],
            icon="🔫"
        ),
        Item(
            id="medkit_small",
            name="Малая аптечка",
            description="Восстанавливает 25 здоровья",
            category=ItemCategory.CONSUMABLE,
            subcategory=ItemSubcategory.HEALTH,
            rarity=ItemRarity.COMMON,
            value=25,
            weight=0.3,
            effects=[ItemEffect(stat="health", value=25, duration=0)],
            stackable=True,
            max_stack=10,
            icon="💊"
        ),
        Item(
            id="credit_chip",
            name="Кредитный чип",
            description="Содержит 100 кредитов",
            category=ItemCategory.KEY_ITEM,
            rarity=ItemRarity.COMMON,
            value=100,
            weight=0.1,
            icon="💳"
        )
    ]


# ============================================================================
# EXPORT
# ============================================================================


__all__ = [
    # Enums
    'ItemRarity',
    'ItemCategory',
    'ItemSubcategory',
    
    # Models
    'ItemEffect',
    'Item',
    'InventoryItem',
    'InventoryStats',
    
    # Manager
    'InventoryManager',
    
    # Templates
    'create_starter_items',
]
