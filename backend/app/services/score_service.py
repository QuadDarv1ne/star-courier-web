"""
StarCourier Web - Score Calculator Service
Продвинутая система расчёта очков

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# SCORE MULTIPLIERS
# ============================================================================

class EndingType(str, Enum):
    """Типы концовок"""
    BEST = "best"           # Лучшая концовка
    GOOD = "good"           # Хорошая концовка
    NEUTRAL = "neutral"     # Нейтральная концовка
    BAD = "bad"             # Плохая концовка
    WORST = "worst"         # Худшая концовка
    SECRET = "secret"       # Секретная концовка


class DifficultyLevel(str, Enum):
    """Уровни сложности"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    NIGHTMARE = "nightmare"


# Множители очков по типу концовки
ENDING_MULTIPLIERS = {
    EndingType.BEST: 2.0,
    EndingType.GOOD: 1.5,
    EndingType.NEUTRAL: 1.0,
    EndingType.BAD: 0.5,
    EndingType.WORST: 0.25,
    EndingType.SECRET: 3.0,
}

# Множители по сложности
DIFFICULTY_MULTIPLIERS = {
    DifficultyLevel.EASY: 0.5,
    DifficultyLevel.NORMAL: 1.0,
    DifficultyLevel.HARD: 1.5,
    DifficultyLevel.NIGHTMARE: 2.0,
}

# Очки за достижения по редкости
ACHIEVEMENT_POINTS = {
    "common": 10,
    "uncommon": 25,
    "rare": 50,
    "epic": 100,
    "legendary": 250,
}


# ============================================================================
# SCORE MODEL
# ============================================================================

@dataclass
class ScoreBreakdown:
    """Детализация очков"""
    base_score: int = 0
    choices_bonus: int = 0
    time_bonus: int = 0
    exploration_bonus: int = 0
    achievement_bonus: int = 0
    relationship_bonus: int = 0
    ending_multiplier: float = 1.0
    difficulty_multiplier: float = 1.0
    penalties: int = 0
    final_score: int = 0
    breakdown: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_final(self) -> int:
        """Расчёт итогового счёта"""
        total = (
            self.base_score +
            self.choices_bonus +
            self.time_bonus +
            self.exploration_bonus +
            self.achievement_bonus +
            self.relationship_bonus -
            self.penalties
        )
        
        # Применение множителей
        total = int(total * self.ending_multiplier * self.difficulty_multiplier)
        
        self.final_score = max(0, total)
        return self.final_score


# ============================================================================
# SCORE CALCULATOR
# ============================================================================

class ScoreCalculator:
    """Калькулятор очков"""
    
    # Базовые значения
    BASE_POINTS_PER_SCENE = 10
    POINTS_PER_CHOICE = 5
    POINTS_PER_MINUTE_FAST = 2      # Бонус за быстрое прохождение
    POINTS_PER_UNIQUE_SCENE = 15
    POINTS_PER_ACHIEVEMENT_BASE = 10
    POINTS_PER_MAX_RELATIONSHIP = 50
    PENALTY_PER_DEATH = 100
    
    # Пороги для бонусов
    FAST_COMPLETION_MINUTES = 30     # Быстрое прохождение
    EXPLORATION_THRESHOLD = 0.5     # % от всех сцен для бонуса
    
    def __init__(self, total_scenes: int = 50):
        """
        Args:
            total_scenes: Общее количество сцен в игре
        """
        self.total_scenes = total_scenes
    
    def calculate(
        self,
        visited_scenes: List[str],
        choices_made: int,
        playtime_seconds: int,
        achievements: List[Dict[str, Any]],
        relationships: Dict[str, int],
        ending_type: str = "neutral",
        difficulty: str = "normal",
        stats: Dict[str, int] = None,
        deaths: int = 0,
        hints_used: int = 0
    ) -> ScoreBreakdown:
        """
        Расчёт очков для завершённой игры
        
        Args:
            visited_scenes: Посещённые сцены
            choices_made: Количество сделанных выборов
            playtime_seconds: Время игры в секундах
            achievements: Полученные достижения
            relationships: Уровни отношений с персонажами
            ending_type: Тип концовки
            difficulty: Уровень сложности
            stats: Финальная статистика персонажа
            deaths: Количество смертей
            hints_used: Использованных подсказок
        
        Returns:
            Детализация очков
        """
        breakdown = ScoreBreakdown()
        
        # 1. Базовые очки за сцены
        breakdown.base_score = len(visited_scenes) * self.BASE_POINTS_PER_SCENE
        breakdown.breakdown["scenes_visited"] = len(visited_scenes)
        breakdown.breakdown["base_points"] = breakdown.base_score
        
        # 2. Бонус за выборы
        breakdown.choices_bonus = choices_made * self.POINTS_PER_CHOICE
        breakdown.breakdown["choices_made"] = choices_made
        breakdown.breakdown["choices_bonus"] = breakdown.choices_bonus
        
        # 3. Бонус за время (быстрое прохождение)
        playtime_minutes = playtime_seconds / 60
        if playtime_minutes > 0:
            if playtime_minutes <= self.FAST_COMPLETION_MINUTES:
                # Бонус за быстрое прохождение
                time_saved = self.FAST_COMPLETION_MINUTES - playtime_minutes
                breakdown.time_bonus = int(time_saved * self.POINTS_PER_MINUTE_FAST)
                breakdown.breakdown["fast_completion"] = True
            else:
                breakdown.time_bonus = 0
        
        breakdown.breakdown["playtime_minutes"] = round(playtime_minutes, 2)
        breakdown.breakdown["time_bonus"] = breakdown.time_bonus
        
        # 4. Бонус за исследование
        exploration_rate = len(visited_scenes) / max(self.total_scenes, 1)
        if exploration_rate >= self.EXPLORATION_THRESHOLD:
            # Бонус за исследование более 50% сцен
            breakdown.exploration_bonus = int(
                len(visited_scenes) * self.POINTS_PER_UNIQUE_SCENE * exploration_rate
            )
        
        breakdown.breakdown["exploration_rate"] = round(exploration_rate, 2)
        breakdown.breakdown["exploration_bonus"] = breakdown.exploration_bonus
        
        # 5. Бонус за достижения
        for achievement in achievements:
            rarity = achievement.get("rarity", "common")
            points = ACHIEVEMENT_POINTS.get(rarity, self.POINTS_PER_ACHIEVEMENT_BASE)
            breakdown.achievement_bonus += points
        
        breakdown.breakdown["achievements_count"] = len(achievements)
        breakdown.breakdown["achievement_bonus"] = breakdown.achievement_bonus
        
        # 6. Бонус за отношения
        max_relationships = sum(
            1 for rel in relationships.values() 
            if rel >= 80  # Максимальный уровень
        )
        breakdown.relationship_bonus = max_relationships * self.POINTS_PER_MAX_RELATIONSHIP
        breakdown.breakdown["max_relationships"] = max_relationships
        breakdown.breakdown["relationship_bonus"] = breakdown.relationship_bonus
        
        # 7. Множитель концовки
        ending_enum = EndingType(ending_type) if ending_type in [e.value for e in EndingType] else EndingType.NEUTRAL
        breakdown.ending_multiplier = ENDING_MULTIPLIERS.get(ending_enum, 1.0)
        breakdown.breakdown["ending_type"] = ending_type
        breakdown.breakdown["ending_multiplier"] = breakdown.ending_multiplier
        
        # 8. Множитель сложности
        difficulty_enum = DifficultyLevel(difficulty) if difficulty in [d.value for d in DifficultyLevel] else DifficultyLevel.NORMAL
        breakdown.difficulty_multiplier = DIFFICULTY_MULTIPLIERS.get(difficulty_enum, 1.0)
        breakdown.breakdown["difficulty"] = difficulty
        breakdown.breakdown["difficulty_multiplier"] = breakdown.difficulty_multiplier
        
        # 9. Штрафы
        breakdown.penalties = (deaths * self.PENALTY_PER_DEATH) + (hints_used * 10)
        breakdown.breakdown["deaths"] = deaths
        breakdown.breakdown["hints_used"] = hints_used
        breakdown.breakdown["penalties"] = breakdown.penalties
        
        # 10. Бонус от статистики
        if stats:
            stat_bonus = self._calculate_stat_bonus(stats)
            breakdown.base_score += stat_bonus
            breakdown.breakdown["stat_bonus"] = stat_bonus
        
        # Финальный расчёт
        breakdown.calculate_final()
        
        return breakdown
    
    def _calculate_stat_bonus(self, stats: Dict[str, int]) -> int:
        """Расчёт бонуса от финальной статистики"""
        bonus = 0
        
        # Бонус за высокие значения положительных статов
        positive_stats = ["health", "morale", "knowledge", "team", "security"]
        for stat in positive_stats:
            value = stats.get(stat, 0)
            if value >= 80:
                bonus += 20
            elif value >= 60:
                bonus += 10
        
        # Бонус за низкие значения отрицательных статов
        negative_stats = ["danger"]
        for stat in negative_stats:
            value = stats.get(stat, 100)
            if value <= 20:
                bonus += 15
        
        return bonus
    
    def calculate_leaderboard_score(
        self,
        games_completed: int,
        total_playtime_minutes: int,
        achievements_count: int,
        avg_score: int
    ) -> int:
        """
        Расчёт очков для таблицы лидеров
        
        Комплексный рейтинг на основе всех достижений игрока
        """
        score = 0
        
        # Базовые очки за игры
        score += games_completed * 100
        
        # Бонус за время в игре (до определённого лимита)
        max_time_bonus = 1000
        time_bonus = min(total_playtime_minutes // 10, max_time_bonus)
        score += time_bonus
        
        # Очки за достижения
        score += achievements_count * 50
        
        # Средний счёт
        score += avg_score
        
        return score
    
    def get_rank(self, score: int) -> Dict[str, Any]:
        """
        Получение ранга по очкам
        
        Returns:
            Информация о ранге
        """
        ranks = [
            {"name": "Novice", "min_score": 0, "icon": "🌟", "color": "#9CA3AF"},
            {"name": "Explorer", "min_score": 500, "icon": "🚀", "color": "#60A5FA"},
            {"name": "Captain", "min_score": 1500, "icon": "👨‍✈️", "color": "#34D399"},
            {"name": "Commander", "min_score": 3000, "icon": "🎖️", "color": "#FBBF24"},
            {"name": "Admiral", "min_score": 5000, "icon": "⭐", "color": "#F472B6"},
            {"name": "Legend", "min_score": 8000, "icon": "👑", "color": "#A78BFA"},
            {"name": "StarCourier", "min_score": 12000, "icon": "🌌", "color": "#FCD34D"},
        ]
        
        current_rank = ranks[0]
        next_rank = None
        
        for i, rank in enumerate(ranks):
            if score >= rank["min_score"]:
                current_rank = rank
                next_rank = ranks[i + 1] if i + 1 < len(ranks) else None
        
        result = {
            "rank": current_rank["name"],
            "icon": current_rank["icon"],
            "color": current_rank["color"],
            "current_score": score,
            "min_score": current_rank["min_score"]
        }
        
        if next_rank:
            result["next_rank"] = next_rank["name"]
            result["next_rank_icon"] = next_rank["icon"]
            result["points_to_next"] = next_rank["min_score"] - score
        
        return result


# Глобальный экземпляр
score_calculator = ScoreCalculator()
