"""
StarCourier Web - Custom Validators
Пользовательские валидаторы для данных

Автор: QuadDarv1ne
Версия: 2.0.0
"""

import re
from typing import Optional, List, Any
from pydantic import field_validator, model_validator, ValidationInfo
from datetime import datetime, timedelta


# ============================================================================
# PASSWORD VALIDATORS
# ============================================================================

class PasswordValidator:
    """Валидаторы для паролей"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @staticmethod
    def validate_password(value: str) -> str:
        """
        Проверка сложности пароля
        
        Требования:
        - Минимум 8 символов
        - Максимум 128 символов
        - Хотя бы одна заглавная буква
        - Хотя бы одна строчная буква
        - Хотя бы одна цифра
        - Хотя бы один специальный символ
        """
        if len(value) < PasswordValidator.MIN_LENGTH:
            raise ValueError(f'Пароль должен быть не менее {PasswordValidator.MIN_LENGTH} символов')
        
        if len(value) > PasswordValidator.MAX_LENGTH:
            raise ValueError(f'Пароль должен быть не более {PasswordValidator.MAX_LENGTH} символов')
        
        if not re.search(r'[A-Z]', value):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        
        if not re.search(r'[a-z]', value):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        
        if not re.search(r'\d', value):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Пароль должен содержать хотя бы один специальный символ')
        
        return value
    
    @staticmethod
    def validate_password_strength(value: str) -> int:
        """
        Оценка сложности пароля (0-100)
        
        Returns:
            int: Уровень сложности (0-100)
        """
        score = 0
        
        # Длина
        if len(value) >= 8:
            score += 20
        if len(value) >= 12:
            score += 20
        if len(value) >= 16:
            score += 10
        
        # Разнообразие символов
        if re.search(r'[A-Z]', value):
            score += 10
        if re.search(r'[a-z]', value):
            score += 10
        if re.search(r'\d', value):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            score += 20
        
        return min(score, 100)


# ============================================================================
# USERNAME VALIDATORS
# ============================================================================

class UsernameValidator:
    """Валидаторы для имён пользователей"""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
    
    @staticmethod
    def validate_username(value: str) -> str:
        """
        Проверка имени пользователя
        
        Требования:
        - 3-50 символов
        - Только буквы, цифры и подчёркивание
        - Не может начинаться с цифры
        """
        if len(value) < UsernameValidator.MIN_LENGTH:
            raise ValueError(f'Имя пользователя должно быть не менее {UsernameValidator.MIN_LENGTH} символов')
        
        if len(value) > UsernameValidator.MAX_LENGTH:
            raise ValueError(f'Имя пользователя должно быть не более {UsernameValidator.MAX_LENGTH} символов')
        
        if not UsernameValidator.PATTERN.match(value):
            raise ValueError('Имя пользователя может содержать только буквы, цифры и подчёркивание')
        
        if value[0].isdigit():
            raise ValueError('Имя пользователя не может начинаться с цифры')
        
        return value.lower()
    
    @staticmethod
    def is_valid_username(value: str) -> bool:
        """Быстрая проверка валидности имени"""
        try:
            UsernameValidator.validate_username(value)
            return True
        except ValueError:
            return False


# ============================================================================
# EMAIL VALIDATORS
# ============================================================================

class EmailValidator:
    """Валидаторы для email"""
    
    PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_email(value: str) -> str:
        """
        Проверка email адреса
        
        Требования:
        - Стандартный формат email
        - Валидный домен
        """
        value = value.strip().lower()
        
        if not EmailValidator.PATTERN.match(value):
            raise ValueError('Некорректный email адрес')
        
        # Проверка длины
        if len(value) > 254:
            raise ValueError('Email слишком длинный')
        
        # Проверка домена
        domain = value.split('@')[1]
        if len(domain) > 253:
            raise ValueError('Домен слишком длинный')
        
        if '..' in domain:
            raise ValueError('Домен не может содержать последовательные точки')
        
        return value
    
    @staticmethod
    def normalize_email(value: str) -> str:
        """Нормализация email (lowercase + trim)"""
        return value.strip().lower()


# ============================================================================
# GAME DATA VALIDATORS
# ============================================================================

class GameDataValidator:
    """Валидаторы для игровых данных"""
    
    @staticmethod
    def validate_scene_id(value: str) -> str:
        """Проверка ID сцены"""
        if not value or len(value) > 100:
            raise ValueError('Некорректный ID сцены')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValueError('ID сцены может содержать только буквы, цифры и подчёркивание')
        
        return value
    
    @staticmethod
    def validate_player_name(value: str) -> str:
        """Проверка имени игрока"""
        value = value.strip()
        
        if len(value) < 2:
            raise ValueError('Имя должно быть не менее 2 символов')
        
        if len(value) > 50:
            raise ValueError('Имя должно быть не более 50 символов')
        
        return value.title()
    
    @staticmethod
    def validate_stat_value(value: int, min_val: int = 0, max_val: int = 100) -> int:
        """Проверка значения статистики"""
        if not isinstance(value, int):
            raise ValueError('Значение статистики должно быть целым числом')
        
        if value < min_val or value > max_val:
            raise ValueError(f'Значение должно быть от {min_val} до {max_val}')
        
        return value
    
    @staticmethod
    def validate_chapter(value: int) -> int:
        """Проверка номера главы"""
        if not isinstance(value, int) or value < 1 or value > 18:
            raise ValueError('Номер главы должен быть от 1 до 18')
        
        return value
    
    @staticmethod
    def validate_choice_id(value: str) -> str:
        """Проверка ID выбора"""
        if not value or len(value) > 100:
            raise ValueError('Некорректный ID выбора')
        
        return value


# ============================================================================
# DATE/TIME VALIDATORS
# ============================================================================

class DateTimeValidator:
    """Валидаторы для дат и времени"""
    
    @staticmethod
    def validate_not_future(value: datetime) -> datetime:
        """Проверка, что дата не в будущем"""
        if value > datetime.utcnow():
            raise ValueError('Дата не может быть в будущем')
        
        return value
    
    @staticmethod
    def validate_not_too_old(
        value: datetime,
        max_age_days: int = 365
    ) -> datetime:
        """Проверка, что дата не слишком старая"""
        max_age = datetime.utcnow() - timedelta(days=max_age_days)
        
        if value < max_age:
            raise ValueError(f'Дата слишком старая (максимум {max_age_days} дней)')
        
        return value
    
    @staticmethod
    def validate_date_range(
        value: datetime,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None
    ) -> datetime:
        """Проверка диапазона дат"""
        if min_date and value < min_date:
            raise ValueError(f'Дата должна быть после {min_date}')
        
        if max_date and value > max_date:
            raise ValueError(f'Дата должна быть до {max_date}')
        
        return value


# ============================================================================
# PAGINATION VALIDATORS
# ============================================================================

class PaginationValidator:
    """Валидаторы для пагинации"""
    
    MIN_PAGE = 1
    MAX_PAGE = 10000
    MIN_PER_PAGE = 1
    MAX_PER_PAGE = 100
    
    @staticmethod
    def validate_page(value: int) -> int:
        """Проверка номера страницы"""
        if not isinstance(value, int):
            raise ValueError('Номер страницы должен быть целым числом')
        
        if value < PaginationValidator.MIN_PAGE:
            return PaginationValidator.MIN_PAGE
        
        if value > PaginationValidator.MAX_PAGE:
            raise ValueError(f'Номер страницы слишком большой (максимум {PaginationValidator.MAX_PAGE})')
        
        return value
    
    @staticmethod
    def validate_per_page(value: int) -> int:
        """Проверка количества элементов на странице"""
        if not isinstance(value, int):
            raise ValueError('Количество элементов должно быть целым числом')
        
        if value < PaginationValidator.MIN_PER_PAGE:
            return PaginationValidator.MIN_PER_PAGE
        
        if value > PaginationValidator.MAX_PER_PAGE:
            return PaginationValidator.MAX_PER_PAGE
        
        return value


# ============================================================================
# EXPORT
# ============================================================================


__all__ = [
    'PasswordValidator',
    'UsernameValidator',
    'EmailValidator',
    'GameDataValidator',
    'DateTimeValidator',
    'PaginationValidator',
]
