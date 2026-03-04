"""
StarCourier Web - Pydantic Models
Все модели данных для API

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# BASE MODELS
# ============================================================================

class StatUpdate(BaseModel):
    """Модель обновления статистики"""
    health: Optional[int] = 0
    morale: Optional[int] = 0
    knowledge: Optional[int] = 0
    team: Optional[int] = 0
    danger: Optional[int] = 0
    security: Optional[int] = 0
    fuel: Optional[int] = 0
    money: Optional[int] = 0
    psychic: Optional[int] = 0
    trust: Optional[int] = 0


class Choice(BaseModel):
    """Модель выбора в сцене"""
    text: str = Field(..., description="Текст выбора")
    next: str = Field(..., description="ID следующей сцены")
    stats: Optional[Dict[str, int]] = Field(None, description="Изменение статистики")
    difficulty: Optional[str] = Field(None, description="Сложность выбора")


class SceneResponse(BaseModel):
    """Модель ответа со сценой"""
    id: str = Field(..., description="ID сцены")
    title: str = Field(..., description="Название сцены")
    text: str = Field(..., description="Текст сцены")
    image: str = Field(..., description="Эмодзи сцены")
    character: str = Field(..., description="Персонаж, говорящий в сцене")
    choices: List[Choice] = Field(..., description="Доступные выборы")


class CharacterInfo(BaseModel):
    """Информация о персонаже"""
    id: str
    name: str
    role: str
    description: str
    relationship: int
    avatar: Optional[str] = None


# ============================================================================
# GAME REQUEST/RESPONSE MODELS
# ============================================================================

class GameStartRequest(BaseModel):
    """Модель запроса начала игры"""
    player_id: str = Field(..., description="Уникальный ID игрока")


class GameStartResponse(BaseModel):
    """Модель ответа начала игры"""
    status: str = "success"
    scene: SceneResponse
    stats: Dict[str, int]
    relationships: Dict[str, int]


class GameChoiceRequest(BaseModel):
    """Модель запроса выбора"""
    player_id: str = Field(..., description="ID игрока")
    next_scene: str = Field(..., description="ID следующей сцены")
    stats: Optional[Dict[str, int]] = Field(None, description="Изменение статистики")


class GameChoiceResponse(BaseModel):
    """Модель ответа на выбор"""
    status: str
    scene: Optional[SceneResponse] = None
    stats: Optional[Dict[str, int]] = None
    relationships: Optional[Dict[str, int]] = None
    choices_made: int = 0
    reason: Optional[str] = None
    game_over: Optional[bool] = None
    ending_type: Optional[str] = None


class PlayerStatsResponse(BaseModel):
    """Модель ответа со статистикой игрока"""
    current_scene: str
    stats: Dict[str, int]
    relationships: Dict[str, int]
    inventory: List[str]
    choices_made: int
    game_over: Optional[bool] = None


# ============================================================================
# CLOUD SAVE MODELS
# ============================================================================

class CloudSaveRequest(BaseModel):
    """Модель запроса облачного сохранения"""
    player_id: str = Field(..., description="ID игрока")
    save_data: dict = Field(..., description="Данные сохранения")


class CloudSaveResponse(BaseModel):
    """Модель ответа облачного сохранения"""
    status: str
    message: str
    save_id: Optional[str] = None


class CloudLoadRequest(BaseModel):
    """Модель запроса загрузки из облака"""
    player_id: str = Field(..., description="ID игрока")
    save_id: str = Field(..., description="ID сохранения")


class CloudSaveListResponse(BaseModel):
    """Модель ответа списка облачных сохранений"""
    status: str
    saves: List[dict]


# ============================================================================
# HEALTH CHECK MODELS
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Модель health check"""
    status: str
    version: str
    environment: str
    timestamp: str
    database: Optional[str] = None
    cache: Optional[str] = None


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Модель ошибки"""
    status: str = "error"
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None
