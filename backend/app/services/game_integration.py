"""
Интеграция игровых механик
Объединяет inventory, crafting, combat с основной игрой
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from app.services.inventory_service import InventoryManager, Item, create_starter_items
from app.services.crafting_service import CraftingManager, create_starter_recipes
from app.services.combat_service import CombatManager, create_player_combatant

logger = logging.getLogger('game_integration')


@dataclass
class PlayerGameData:
    """Полные данные игрока"""
    player_id: str
    stats: Dict[str, int] = field(default_factory=lambda: {
        'health': 100,
        'morale': 100,
        'psychic': 10,
        'money': 100
    })
    inventory: Optional[InventoryManager] = None
    crafting: Optional[CraftingManager] = None
    combat: Optional[CombatManager] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = InventoryManager(max_weight=50.0, max_slots=30)
        if self.crafting is None:
            self.crafting = CraftingManager()
            for recipe in create_starter_recipes():
                self.crafting.add_recipe(recipe)
        if self.combat is None:
            self.combat = CombatManager()


class GameIntegrationService:
    """
    Сервис интеграции игровых систем
    
    Объединяет:
    - Инвентарь
    - Крафт
    - Бой
    - Основную статистику
    """
    
    def __init__(self):
        self.players: Dict[str, PlayerGameData] = {}
    
    def get_or_create_player(self, player_id: str) -> PlayerGameData:
        """Получить или создать игрока"""
        if player_id not in self.players:
            self.players[player_id] = PlayerGameData(player_id=player_id)
            
            # Выдать стартовые предметы
            for item in create_starter_items():
                self.players[player_id].inventory.add_item(item)
            
            logger.info(f"Создан новый игрок {player_id}")
        
        return self.players[player_id]
    
    def get_inventory(self, player_id: str) -> InventoryManager:
        """Получить инвентарь игрока"""
        player = self.get_or_create_player(player_id)
        return player.inventory
    
    def get_crafting(self, player_id: str) -> CraftingManager:
        """Получить крафт игрока"""
        player = self.get_or_create_player(player_id)
        return player.crafting
    
    def craft_item(self, player_id: str, recipe_id: str) -> Dict[str, Any]:
        """
        Выполнить крафт для игрока
        
        Returns:
            результат крафта
        """
        player = self.get_or_create_player(player_id)
        recipe = player.crafting.get_recipe(recipe_id)
        
        if not recipe:
            return {'success': False, 'error': 'Рецепт не найден'}
        
        # Получить доступные предметы из инвентаря
        available_items = {}
        for inv_item in player.inventory.list_items():
            available_items[inv_item.item.id] = inv_item.quantity
        
        # Выполнить крафт
        result, message, data = player.crafting.craft(
            recipe,
            available_items,
            player.stats
        )
        
        # Добавить результат в инвентарь
        if data.get('quantity', 0) > 0:
            # В реальной реализации - создание предмета по ID
            pass
        
        return {
            'success': True,
            'result': result.value,
            'message': message,
            'data': data
        }
    
    def start_combat(self, player_id: str, enemy_name: str, enemy_level: int) -> Dict[str, Any]:
        """Начать бой для игрока"""
        player = self.get_or_create_player(player_id)
        
        # Создать участника боя из игрока
        combat_player = create_player_combatant(
            name="Макс Велл",
            level=player.stats.get('psychic', 1) // 10 + 1
        )
        
        # Перенести статы
        combat_player.stats.health = player.stats.get('health', 100)
        combat_player.stats.damage = 10 + player.stats.get('psychic', 10) // 5
        
        from app.services.combat_service import create_enemy_combatant
        enemy = create_enemy_combatant(enemy_name, enemy_level)
        
        # Награды
        rewards = {
            'credits': 50 * enemy_level,
            'exp': 100 * enemy_level,
            'items': []
        }
        
        combat = player.combat.start_combat(combat_player, [enemy], rewards)
        
        return {
            'combat_id': combat.id,
            'player': combat_player.model_dump(),
            'enemy': enemy.model_dump(),
            'first_turn': combat.current_turn.value
        }
    
    def get_player_state(self, player_id: str) -> Dict[str, Any]:
        """Получить полное состояние игрока"""
        player = self.get_or_create_player(player_id)
        
        return {
            'player_id': player.player_id,
            'stats': player.stats,
            'inventory': {
                'items_count': len(player.inventory.items),
                'total_weight': player.inventory.get_stats().total_weight,
                'max_weight': player.inventory.max_weight
            },
            'crafting': {
                'recipes_known': len(player.crafting.recipes),
                'skill_levels': player.crafting.skill_levels
            },
            'active_combats': len(player.combat.combats)
        }


# Глобальный экземпляр
game_integration = GameIntegrationService()


def get_game_integration() -> GameIntegrationService:
    """Получить сервис интеграции"""
    return game_integration
