"""
StarCourier Web - Combat System
Тактическая боевая система

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime
import random


# ============================================================================
# ENUMS
# ============================================================================

class CombatActionType(str, Enum):
    """Типы боевых действий"""
    ATTACK = "attack"
    DEFEND = "defend"
    ABILITY = "ability"
    ITEM = "item"
    FLEE = "flee"


class CombatTurn(str, Enum):
    """Чей ход"""
    PLAYER = "player"
    ENEMY = "enemy"


class CombatResult(str, Enum):
    """Результат боя"""
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"
    DRAW = "draw"


class Position(str, Enum):
    """Позиция в бою"""
    FRONT = "front"
    MIDDLE = "middle"
    BACK = "back"


# ============================================================================
# MODELS
# ============================================================================

class CombatStats(BaseModel):
    """Боевые характеристики"""
    health: int = Field(100, description="Здоровье")
    max_health: int = Field(100, description="Макс здоровье")
    energy: int = Field(50, description="Энергия")
    max_energy: int = Field(50, description="Макс энергия")
    
    damage: int = Field(10, description="Урон")
    defense: int = Field(5, description="Защита")
    speed: int = Field(10, description="Скорость")
    
    crit_chance: float = Field(0.1, description="Шанс крита")
    crit_damage: float = Field(1.5, description="Множитель крита")
    dodge_chance: float = Field(0.1, description="Шанс уклонения")
    accuracy: float = Field(0.9, description="Точность")


class CombatAbility(BaseModel):
    """Боевая способность"""
    id: str = Field(..., description="ID способности")
    name: str = Field(..., description="Название")
    description: str = Field(..., description="Описание")
    
    energy_cost: int = Field(0, description="Стоимость энергии")
    cooldown: int = Field(0, description="Перезарядка в ходах")
    
    damage_multiplier: float = Field(1.0, description="Множитель урона")
    effect: Optional[str] = Field(None, description="Дополнительный эффект")
    
    icon: str = Field("⚔️", description="Эмодзи иконка")


class CombatAction(BaseModel):
    """Действие в бою"""
    type: CombatActionType = Field(..., description="Тип действия")
    actor_id: str = Field(..., description="ID действующего")
    target_id: Optional[str] = Field(None, description="ID цели")
    
    ability: Optional[CombatAbility] = Field(None, description="Способность")
    item_id: Optional[str] = Field(None, description="ID предмета")
    
    position: Optional[Position] = Field(None, description="Позиция")
    
    @field_validator('type')
    @classmethod
    def validate_action(cls, v, info):
        if v == CombatActionType.ABILITY and not info.data.get('ability'):
            raise ValueError('Для способности нужна ability')
        if v == CombatActionType.ITEM and not info.data.get('item_id'):
            raise ValueError('Для предмета нужен item_id')
        return v


class CombatLogEntry(BaseModel):
    """Запись в боевом логе"""
    turn: int = Field(..., description="Номер хода")
    actor: str = Field(..., description="Кто действовал")
    action: str = Field(..., description="Что сделал")
    result: str = Field(..., description="Результат")
    damage: Optional[int] = Field(None, description="Урон")
    healing: Optional[int] = Field(None, description="Лечение")


class Combatant(BaseModel):
    """Участник боя"""
    id: str = Field(..., description="ID участника")
    name: str = Field(..., description="Имя")
    is_player: bool = Field(False, description="Это игрок?")
    
    stats: CombatStats = Field(..., description="Характеристики")
    abilities: List[CombatAbility] = Field(default_factory=list, description="Способности")
    
    position: Position = Field(Position.MIDDLE, description="Позиция")
    is_alive: bool = Field(True, description="Жив ли")
    
    # Временные эффекты
    buffs: Dict[str, int] = Field(default_factory=dict, description="Баффы")
    debuffs: Dict[str, int] = Field(default_factory=dict, description="Дебаффы")


class CombatState(BaseModel):
    """Состояние боя"""
    id: str = Field(..., description="ID боя")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Время начала")
    ended_at: Optional[datetime] = Field(None, description="Время конца")
    
    turn: int = Field(1, description="Текущий ход")
    current_turn: CombatTurn = Field(CombatTurn.PLAYER, description="Чей ход")
    
    player: Combatant = Field(..., description="Игрок")
    enemies: List[Combatant] = Field(default_factory=list, description="Враги")
    
    log: List[CombatLogEntry] = Field(default_factory=list, description="Лог боя")
    result: Optional[CombatResult] = Field(None, description="Результат")
    
    rewards: Dict[str, Any] = Field(default_factory=dict, description="Награды")


# ============================================================================
# COMBAT MANAGER
# ============================================================================

class CombatManager:
    """
    Менеджер боя
    
    Управление тактическим боем:
    - Инициализация боя
    - Обработка ходов
    - Расчёт урона
    - Проверка условий победы
    """
    
    def __init__(self):
        self.combats: Dict[str, CombatState] = {}
    
    def start_combat(
        self,
        player: Combatant,
        enemies: List[Combatant],
        rewards: Optional[Dict[str, Any]] = None
    ) -> CombatState:
        """Начать бой"""
        combat_id = f"combat_{datetime.utcnow().timestamp()}"
        
        combat = CombatState(
            id=combat_id,
            player=player,
            enemies=enemies,
            rewards=rewards or {}
        )
        
        # Определение первого хода (по скорости)
        player_speed = player.stats.speed
        enemy_speed = max(e.stats.speed for e in enemies)
        
        if enemy_speed > player_speed:
            combat.current_turn = CombatTurn.ENEMY
        
        self.combats[combat_id] = combat
        return combat
    
    def player_turn(
        self,
        combat_id: str,
        action: CombatAction
    ) -> Tuple[bool, str, CombatLogEntry]:
        """
        Ход игрока
        
        Returns:
            tuple: (успех, сообщение, запись лога)
        """
        combat = self.combats.get(combat_id)
        if not combat:
            return False, "Бой не найден", None
        
        if combat.current_turn != CombatTurn.PLAYER:
            return False, "Не ваш ход", None
        
        if combat.result:
            return False, "Бой завершён", None
        
        # Выполнение действия
        success, message, log_entry = self._execute_action(combat, action)
        
        if success:
            # Проверка победы
            if self._check_victory(combat):
                combat.result = CombatResult.VICTORY
                combat.ended_at = datetime.utcnow()
            
            # Переход хода к врагу
            elif not combat.result:
                combat.current_turn = CombatTurn.ENEMY
                combat.turn += 1
        
        return success, message, log_entry
    
    def enemy_turn(self, combat_id: str) -> Tuple[bool, str, List[CombatLogEntry]]:
        """
        Ход врага (AI)
        
        Returns:
            tuple: (успех, сообщение, записи лога)
        """
        combat = self.combats.get(combat_id)
        if not combat:
            return False, "Бой не найден", []
        
        if combat.current_turn != CombatTurn.ENEMY:
            return False, "Сейчас не ход врага", []
        
        if combat.result:
            return False, "Бой завершён", []
        
        log_entries = []
        
        # Простой AI: атаковать случайного живого противника
        for enemy in combat.enemies:
            if not enemy.is_alive:
                continue
            
            # Выбор цели
            target = combat.player if combat.player.is_alive else None
            if not target:
                continue
            
            # Создание действия
            action = CombatAction(
                type=CombatActionType.ATTACK,
                actor_id=enemy.id,
                target_id=target.id
            )
            
            # Выполнение
            success, message, log_entry = self._execute_action(combat, action)
            if success:
                log_entries.append(log_entry)
        
        # Проверка поражения
        if self._check_defeat(combat):
            combat.result = CombatResult.DEFEAT
            combat.ended_at = datetime.utcnow()
        else:
            combat.current_turn = CombatTurn.PLAYER
        
        return True, "Ход врага завершён", log_entries
    
    def _execute_action(
        self,
        combat: CombatState,
        action: CombatAction
    ) -> Tuple[bool, str, CombatLogEntry]:
        """Выполнить действие"""
        actor = self._get_combatant(combat, action.actor_id)
        if not actor:
            return False, "Действующий не найден", None
        
        if not actor.is_alive:
            return False, "Действующий мёртв", None
        
        # Выполнение по типу действия
        if action.type == CombatActionType.ATTACK:
            return self._execute_attack(combat, actor, action.target_id)
        elif action.type == CombatActionType.DEFEND:
            return self._execute_defend(combat, actor)
        elif action.type == CombatActionType.ABILITY:
            return self._execute_ability(combat, actor, action)
        elif action.type == CombatActionType.ITEM:
            return self._execute_item(combat, actor, action)
        elif action.type == CombatActionType.FLEE:
            return self._execute_flee(combat, actor)
        
        return False, "Неизвестное действие", None
    
    def _execute_attack(
        self,
        combat: CombatState,
        attacker: Combatant,
        target_id: str
    ) -> Tuple[bool, str, CombatLogEntry]:
        """Выполнить атаку"""
        target = self._get_combatant(combat, target_id)
        if not target:
            return False, "Цель не найдена", None
        
        if not target.is_alive:
            return False, "Цель мертва", None
        
        # Проверка уклонения
        if random.random() < target.stats.dodge_chance:
            log = CombatLogEntry(
                turn=combat.turn,
                actor=attacker.name,
                action="Атака",
                result=f"{target.name} уклонился!",
                damage=0
            )
            combat.log.append(log)
            return True, f"{target.name} уклонился от атаки", log
        
        # Проверка попадания
        if random.random() > attacker.stats.accuracy:
            log = CombatLogEntry(
                turn=combat.turn,
                actor=attacker.name,
                action="Атака",
                result="Промах!",
                damage=0
            )
            combat.log.append(log)
            return True, "Промах", log
        
        # Расчёт урона
        damage = self._calculate_damage(attacker, target)
        
        # Проверка крита
        is_crit = random.random() < attacker.stats.crit_chance
        if is_crit:
            damage = int(damage * attacker.stats.crit_damage)
        
        # Применение урона
        target.stats.health = max(0, target.stats.health - damage)
        if target.stats.health <= 0:
            target.is_alive = False
        
        # Создание лога
        crit_text = " (КРИТ!)" if is_crit else ""
        log = CombatLogEntry(
            turn=combat.turn,
            actor=attacker.name,
            action="Атака",
            result=f"{target.name} получил {damage}{crit_text} урона",
            damage=damage
        )
        combat.log.append(log)
        
        return True, f"Нанесено {damage}{crit_text} урона", log
    
    def _calculate_damage(
        self,
        attacker: Combatant,
        defender: Combatant
    ) -> int:
        """Рассчитать урон"""
        # Базовый урон
        damage = attacker.stats.damage
        
        # Учёт защиты
        defense = defender.stats.defense
        
        # Позиционные бонусы
        if attacker.position == Position.FRONT:
            damage = int(damage * 1.2)
        elif attacker.position == Position.BACK:
            damage = int(damage * 0.8)
        
        # Применение защиты
        final_damage = max(1, damage - defense)
        
        return final_damage
    
    def _execute_defend(
        self,
        combat: CombatState,
        defender: Combatant
    ) -> Tuple[bool, str, CombatLogEntry]:
        """Выполнить защиту"""
        # Временный бафф защиты
        defender.buffs['defense_up'] = defender.buffs.get('defense_up', 0) + 1
        
        log = CombatLogEntry(
            turn=combat.turn,
            actor=defender.name,
            action="Защита",
            result="Защита повышена"
        )
        combat.log.append(log)
        
        return True, "Защита повышена", log
    
    def _execute_ability(
        self,
        combat: CombatState,
        caster: Combatant,
        action: CombatAction
    ) -> Tuple[bool, str, CombatLogEntry]:
        """Выполнить способность"""
        ability = action.ability
        
        # Проверка энергии
        if caster.stats.energy < ability.energy_cost:
            return False, "Недостаточно энергии", None
        
        # Расход энергии
        caster.stats.energy -= ability.energy_cost
        
        # Применение способности
        target = self._get_combatant(combat, action.target_id) if action.target_id else caster
        
        damage = 0
        if ability.damage_multiplier > 1:
            damage = int(caster.stats.damage * ability.damage_multiplier)
            if target and target.is_alive:
                target.stats.health = max(0, target.stats.health - damage)
                if target.stats.health <= 0:
                    target.is_alive = False
        
        log = CombatLogEntry(
            turn=combat.turn,
            actor=caster.name,
            action=ability.name,
            result=f"Использовал {ability.name}",
            damage=damage if damage > 0 else None
        )
        combat.log.append(log)
        
        return True, f"Использовано {ability.name}", log
    
    def _execute_item(
        self,
        combat: CombatState,
        user: Combatant,
        action: CombatAction
    ) -> Tuple[bool, str, CombatLogEntry]:
        """Использовать предмет"""
        # Заглушка - реальная реализация зависит от системы предметов
        log = CombatLogEntry(
            turn=combat.turn,
            actor=user.name,
            action="Предмет",
            result=f"Использовал предмет {action.item_id}"
        )
        combat.log.append(log)
        
        return True, "Предмет использован", log
    
    def _execute_flee(
        self,
        combat: CombatState,
        actor: Combatant
    ) -> Tuple[bool, str, CombatLogEntry]:
        """Попытка бегства"""
        # Шанс бегства зависит от скорости
        flee_chance = 0.5 + (actor.stats.speed / 100)
        
        if random.random() < flee_chance:
            combat.result = CombatResult.FLED
            combat.ended_at = datetime.utcnow()
            
            log = CombatLogEntry(
                turn=combat.turn,
                actor=actor.name,
                action="Бегство",
                result="Успешное бегство!"
            )
            combat.log.append(log)
            
            return True, "Удалось сбежать!", log
        else:
            log = CombatLogEntry(
                turn=combat.turn,
                actor=actor.name,
                action="Бегство",
                result="Не удалось сбежать!"
            )
            combat.log.append(log)
            
            return True, "Не удалось сбежать!", log
    
    def _get_combatant(
        self,
        combat: CombatState,
        combatant_id: str
    ) -> Optional[Combatant]:
        """Получить участника боя"""
        if combat.player.id == combatant_id:
            return combat.player
        
        for enemy in combat.enemies:
            if enemy.id == combatant_id:
                return enemy
        
        return None
    
    def _check_victory(self, combat: CombatState) -> bool:
        """Проверить победу"""
        return all(not enemy.is_alive for enemy in combat.enemies)
    
    def _check_defeat(self, combat: CombatState) -> bool:
        """Проверить поражение"""
        return not combat.player.is_alive


# ============================================================================
# COMBATANT TEMPLATES
# ============================================================================

def create_player_combatant(
    name: str = "Макс Велл",
    level: int = 1
) -> Combatant:
    """Создать игрока для боя"""
    # Бонусы за уровень
    health_bonus = level * 10
    damage_bonus = level * 2
    
    return Combatant(
        id="player",
        name=name,
        is_player=True,
        stats=CombatStats(
            health=100 + health_bonus,
            max_health=100 + health_bonus,
            energy=50 + (level * 5),
            max_energy=50 + (level * 5),
            damage=10 + damage_bonus,
            defense=5 + level,
            speed=10 + level,
            crit_chance=0.1 + (level * 0.01),
            crit_damage=1.5 + (level * 0.1),
            dodge_chance=0.1 + (level * 0.01),
            accuracy=0.9
        ),
        abilities=[
            CombatAbility(
                id="ability_quick_shot",
                name="Быстрый выстрел",
                description="Быстрая атака с низким уроном",
                energy_cost=5,
                cooldown=0,
                damage_multiplier=0.8,
                icon="🔫"
            ),
            CombatAbility(
                id="ability_power_shot",
                name="Мощный выстрел",
                description="Медленная мощная атака",
                energy_cost=15,
                cooldown=2,
                damage_multiplier=2.0,
                icon="💥"
            ),
            CombatAbility(
                id="ability_defend",
                name="Защита",
                description="Повышает защиту",
                energy_cost=10,
                cooldown=1,
                damage_multiplier=0,
                effect="defense_up",
                icon="🛡️"
            )
        ]
    )


def create_enemy_combatant(
    name: str = "Бандит",
    level: int = 1
) -> Combatant:
    """Создать врага для боя"""
    return Combatant(
        id=f"enemy_{name}",
        name=name,
        is_player=False,
        stats=CombatStats(
            health=80 + (level * 8),
            max_health=80 + (level * 8),
            energy=30 + (level * 3),
            max_energy=30 + (level * 3),
            damage=8 + (level * 2),
            defense=3 + level,
            speed=8 + level,
            crit_chance=0.05,
            crit_damage=1.5,
            dodge_chance=0.05,
            accuracy=0.8
        ),
        position=Position.FRONT
    )


# ============================================================================
# EXPORT
# ============================================================================


__all__ = [
    # Enums
    'CombatActionType',
    'CombatTurn',
    'CombatResult',
    'Position',
    
    # Models
    'CombatStats',
    'CombatAbility',
    'CombatAction',
    'CombatLogEntry',
    'Combatant',
    'CombatState',
    
    # Manager
    'CombatManager',
    
    # Templates
    'create_player_combatant',
    'create_enemy_combatant',
]
