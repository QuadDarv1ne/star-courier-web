"""
StarCourier Web - Auth Models
Модели для аутентификации и авторизации

Автор: QuadDarv1ne
Версия: 1.0.0
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    """Базовая модель пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Модель для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        """Проверка сложности пароля"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v

    @field_validator('username')
    @classmethod
    def username_format(cls, v):
        """Проверка формата username"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username может содержать только буквы, цифры и подчёркивание')
        return v.lower()


class UserLogin(BaseModel):
    """Модель для входа"""
    username: str
    password: str


class UserResponse(UserBase):
    """Ответ с данными пользователя"""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    games_played: int = 0
    total_playtime: int = 0
    achievements_count: int = 0


class Token(BaseModel):
    """Модель токена"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # секунды


class TokenPayload(BaseModel):
    """Payload JWT токена"""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: str  # "access" или "refresh"


class PlayerStatsDB(BaseModel):
    """Статистика игрока в базе данных"""
    player_id: str
    user_id: str
    current_scene: str = "start"
    stats: dict = {}
    relationships: dict = {}
    inventory: List[str] = []
    choices_made: int = 0
    achievements: List[str] = []
    visited_scenes: List[str] = ["start"]
    playtime: int = 0
    ending_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LeaderboardEntry(BaseModel):
    """Запись в таблице лидеров"""
    rank: int
    username: str
    score: int
    games_completed: int
    achievements: int
    playtime: int


class AchievementDB(BaseModel):
    """Достижение в базе данных"""
    id: str
    name: str
    description: str
    icon: str
    category: str
    points: int
    unlocked_at: datetime
