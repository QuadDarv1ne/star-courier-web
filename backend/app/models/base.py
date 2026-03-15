"""
StarCourier Web - Base Response Models
Унифицированные модели для ответов API

Автор: QuadDarv1ne
Версия: 2.0.0
"""

from typing import Optional, Generic, TypeVar, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

# ============================================================================
# STATUS ENUMS
# ============================================================================


class StatusEnum(str, Enum):
    """Статус ответа API"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ErrorCodeEnum(str, Enum):
    """Коды ошибок API"""
    # Общие ошибки
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # Ошибки игры
    GAME_NOT_FOUND = "GAME_NOT_FOUND"
    GAME_ALREADY_EXISTS = "GAME_ALREADY_EXISTS"
    INVALID_CHOICE = "INVALID_CHOICE"
    SCENE_NOT_FOUND = "SCENE_NOT_FOUND"
    GAME_OVER = "GAME_OVER"
    
    # Ошибки аутентификации
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    
    # Ошибки данных
    SAVE_NOT_FOUND = "SAVE_NOT_FOUND"
    SAVE_INVALID = "SAVE_INVALID"
    DATA_CORRUPTED = "DATA_CORRUPTED"


# ============================================================================
# GENERIC RESPONSE MODELS
# ============================================================================

DataT = TypeVar('DataT')


class APIResponse(BaseModel, Generic[DataT]):
    """
    Универсальная модель ответа API
    
    Пример:
        {
            "status": "success",
            "message": "Операция выполнена успешно",
            "data": {...},
            "timestamp": "2026-03-15T10:30:00Z",
            "request_id": "uuid"
        }
    """
    status: StatusEnum = Field(..., description="Статус ответа")
    message: str = Field(..., description="Сообщение результата")
    data: Optional[DataT] = Field(None, description="Данные ответа")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время ответа")
    request_id: Optional[str] = Field(None, description="ID запроса для отладки")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Успешно",
                "data": {},
                "timestamp": "2026-03-15T10:30:00Z",
                "request_id": "req_123456"
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[DataT]):
    """
    Модель пагинированного ответа
    
    Пример:
        {
            "status": "success",
            "data": [...],
            "pagination": {
                "total": 100,
                "page": 1,
                "per_page": 20,
                "pages": 5
            }
        }
    """
    status: StatusEnum = Field(..., description="Статус ответа")
    data: List[DataT] = Field(..., description="Список данных")
    pagination: Dict[str, int] = Field(..., description="Информация о пагинации")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        data: List[DataT],
        total: int,
        page: int = 1,
        per_page: int = 20
    ) -> 'PaginatedResponse[DataT]':
        """Создать пагинированный ответ"""
        return cls(
            status=StatusEnum.SUCCESS,
            data=data,
            pagination={
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
        )


# ============================================================================
# ERROR RESPONSE MODELS
# ============================================================================


class ErrorDetail(BaseModel):
    """Детали ошибки"""
    field: Optional[str] = Field(None, description="Поле с ошибкой")
    value: Optional[Any] = Field(None, description="Некорректное значение")
    reason: Optional[str] = Field(None, description="Причина ошибки")


class APIError(BaseModel):
    """
    Модель ошибки API
    
    Пример:
        {
            "status": "error",
            "message": "Произошла ошибка",
            "error_code": "VALIDATION_ERROR",
            "details": {
                "field": "email",
                "value": "invalid",
                "reason": "Некорректный email"
            },
            "timestamp": "2026-03-15T10:30:00Z",
            "request_id": "req_123456"
        }
    """
    status: StatusEnum = Field(StatusEnum.ERROR, description="Статус ответа")
    message: str = Field(..., description="Сообщение ошибки")
    error_code: ErrorCodeEnum = Field(..., description="Код ошибки")
    details: Optional[ErrorDetail] = Field(None, description="Детали ошибки")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время ошибки")
    request_id: Optional[str] = Field(None, description="ID запроса для отладки")
    path: Optional[str] = Field(None, description="URL запроса")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "message": "Ошибка валидации",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "email",
                    "value": "invalid",
                    "reason": "Некорректный email"
                },
                "timestamp": "2026-03-15T10:30:00Z",
                "request_id": "req_123456"
            }
        }
    )


class ValidationErrorDetail(BaseModel):
    """Детали валидационной ошибки"""
    loc: List[str] = Field(..., description="Путь к полю")
    msg: str = Field(..., description="Сообщение ошибки")
    type: str = Field(..., description="Тип ошибки")


class APIValidationError(BaseModel):
    """
    Модель ошибки валидации
    
    Пример:
        {
            "status": "error",
            "message": "Ошибка валидации данных",
            "error_code": "VALIDATION_ERROR",
            "errors": [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email"
                }
            ],
            "timestamp": "2026-03-15T10:30:00Z"
        }
    """
    status: StatusEnum = Field(StatusEnum.ERROR, description="Статус ответа")
    message: str = Field("Ошибка валидации данных", description="Сообщение ошибки")
    error_code: ErrorCodeEnum = Field(ErrorCodeEnum.VALIDATION_ERROR, description="Код ошибки")
    errors: List[ValidationErrorDetail] = Field(..., description="Список ошибок валидации")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="URL запроса")


# ============================================================================
# HELPER CLASSES
# ============================================================================


class ResponseBuilder:
    """Билдер для создания ответов API"""
    
    @staticmethod
    def success(
        data: Optional[Any] = None,
        message: str = "Операция выполнена успешно"
    ) -> APIResponse:
        """Создать успешный ответ"""
        return APIResponse(
            status=StatusEnum.SUCCESS,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(
        message: str,
        error_code: ErrorCodeEnum,
        details: Optional[ErrorDetail] = None
    ) -> APIError:
        """Создать ответ с ошибкой"""
        return APIError(
            status=StatusEnum.ERROR,
            message=message,
            error_code=error_code,
            details=details
        )
    
    @staticmethod
    def validation_error(
        errors: List[ValidationErrorDetail],
        path: Optional[str] = None
    ) -> APIValidationError:
        """Создать ответ с ошибкой валидации"""
        return APIValidationError(
            status=StatusEnum.ERROR,
            errors=errors,
            path=path
        )
    
    @staticmethod
    def not_found(
        message: str = "Ресурс не найден",
        details: Optional[ErrorDetail] = None
    ) -> APIError:
        """Создать ответ 404"""
        return ResponseBuilder.error(
            message=message,
            error_code=ErrorCodeEnum.NOT_FOUND,
            details=details
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Необходима авторизация",
        details: Optional[ErrorDetail] = None
    ) -> APIError:
        """Создать ответ 401"""
        return ResponseBuilder.error(
            message=message,
            error_code=ErrorCodeEnum.UNAUTHORIZED,
            details=details
        )
    
    @staticmethod
    def forbidden(
        message: str = "Доступ запрещён",
        details: Optional[ErrorDetail] = None
    ) -> APIError:
        """Создать ответ 403"""
        return ResponseBuilder.error(
            message=message,
            error_code=ErrorCodeEnum.FORBIDDEN,
            details=details
        )
    
    @staticmethod
    def conflict(
        message: str = "Конфликт данных",
        details: Optional[ErrorDetail] = None
    ) -> APIError:
        """Создать ответ 409"""
        return ResponseBuilder.error(
            message=message,
            error_code=ErrorCodeEnum.CONFLICT,
            details=details
        )
    
    @staticmethod
    def too_many_requests(
        message: str = "Слишком много запросов",
        details: Optional[ErrorDetail] = None,
        retry_after: Optional[int] = None
    ) -> APIError:
        """Создать ответ 429"""
        error = ResponseBuilder.error(
            message=message,
            error_code=ErrorCodeEnum.TOO_MANY_REQUESTS,
            details=details
        )
        if retry_after:
            error.details = ErrorDetail(reason=f"Повторите через {retry_after} секунд")
        return error
    
    @staticmethod
    def internal_error(
        message: str = "Внутренняя ошибка сервера",
        details: Optional[ErrorDetail] = None
    ) -> APIError:
        """Создать ответ 500"""
        return ResponseBuilder.error(
            message=message,
            error_code=ErrorCodeEnum.INTERNAL_ERROR,
            details=details
        )


# ============================================================================
# EXPORT
# ============================================================================


__all__ = [
    # Enums
    'StatusEnum',
    'ErrorCodeEnum',
    
    # Response models
    'APIResponse',
    'PaginatedResponse',
    
    # Error models
    'ErrorDetail',
    'APIError',
    'ValidationErrorDetail',
    'APIValidationError',
    
    # Builder
    'ResponseBuilder',
]
