"""
StarCourier Web - Global Exception Handlers
Глобальные обработчики ошибок для FastAPI приложения

Автор: QuadDarv1ne
Версия: 2.0.0
"""

import logging
import traceback
from typing import Optional, Union
from datetime import datetime

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.base import (
    APIError,
    APIValidationError,
    ErrorDetail,
    ResponseBuilder,
    StatusEnum,
    ErrorCodeEnum,
    ValidationErrorDetail,
)

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTION HANDLER CLASSES
# ============================================================================


class AppException(Exception):
    """Базовое исключение приложения"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCodeEnum,
        status_code: int = 400,
        details: Optional[ErrorDetail] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    """Исключение для ресурса не найден"""
    
    def __init__(
        self,
        message: str = "Ресурс не найден",
        details: Optional[ErrorDetail] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.NOT_FOUND,
            status_code=404,
            details=details
        )


class UnauthorizedException(AppException):
    """Исключение для неавторизованного доступа"""
    
    def __init__(
        self,
        message: str = "Необходима авторизация",
        details: Optional[ErrorDetail] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.UNAUTHORIZED,
            status_code=401,
            details=details
        )


class ForbiddenException(AppException):
    """Исключение для запрещённого доступа"""
    
    def __init__(
        self,
        message: str = "Доступ запрещён",
        details: Optional[ErrorDetail] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.FORBIDDEN,
            status_code=403,
            details=details
        )


class ConflictException(AppException):
    """Исключение для конфликта данных"""
    
    def __init__(
        self,
        message: str = "Конфликт данных",
        details: Optional[ErrorDetail] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.CONFLICT,
            status_code=409,
            details=details
        )


class TooManyRequestsException(AppException):
    """Исключение для слишком частых запросов"""
    
    def __init__(
        self,
        message: str = "Слишком много запросов",
        details: Optional[ErrorDetail] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.TOO_MANY_REQUESTS,
            status_code=429,
            details=details
        )
        self.retry_after = retry_after


class ValidationAppException(AppException):
    """Исключение для ошибки валидации"""
    
    def __init__(
        self,
        message: str = "Ошибка валидации данных",
        details: Optional[ErrorDetail] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.VALIDATION_ERROR,
            status_code=422,
            details=details
        )


class InternalServerException(AppException):
    """Исключение для внутренней ошибки сервера"""
    
    def __init__(
        self,
        message: str = "Внутренняя ошибка сервера",
        details: Optional[ErrorDetail] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodeEnum.INTERNAL_ERROR,
            status_code=500,
            details=details
        )


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Обработчик исключений приложения
    
    Args:
        request: Запрос
        exc: Исключение приложения
    
    Returns:
        JSONResponse с деталями ошибки
    """
    logger.warning(f"App Exception: {exc.error_code.value} - {exc.message}")
    
    error = ResponseBuilder.error(
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Обработчик HTTP исключений
    
    Args:
        request: Запрос
        exc: HTTP исключение
    
    Returns:
        JSONResponse с деталями ошибки
    """
    # Маппинг HTTP кодов на ErrorCodeEnum
    error_code_map = {
        401: ErrorCodeEnum.UNAUTHORIZED,
        403: ErrorCodeEnum.FORBIDDEN,
        404: ErrorCodeEnum.NOT_FOUND,
        409: ErrorCodeEnum.CONFLICT,
        429: ErrorCodeEnum.TOO_MANY_REQUESTS,
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCodeEnum.INTERNAL_ERROR)
    
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    error = ResponseBuilder.error(
        message=str(exc.detail),
        error_code=error_code,
        details=ErrorDetail(reason=f"HTTP {exc.status_code}")
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
        headers=getattr(exc, "headers", None)
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Обработчик ошибок валидации
    
    Args:
        request: Запрос
        exc: Ошибка валидации
    
    Returns:
        JSONResponse с деталями ошибок валидации
    """
    logger.debug(f"Validation Error: {exc.errors()}")
    
    errors = []
    for error in exc.errors():
        errors.append(ValidationErrorDetail(
            loc=[str(loc) for loc in error.get("loc", [])],
            msg=error.get("msg", "Unknown error"),
            type=error.get("type", "unknown")
        ))
    
    validation_error = APIValidationError(
        status=StatusEnum.ERROR,
        errors=errors,
        path=str(request.url.path)
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=validation_error.model_dump(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic
    
    Args:
        request: Запрос
        exc: Ошибка валидации Pydantic
    
    Returns:
        JSONResponse с деталями ошибок
    """
    logger.debug(f"Pydantic Validation Error: {exc.errors()}")
    
    errors = []
    for error in exc.errors():
        errors.append(ValidationErrorDetail(
            loc=[str(loc) for loc in error.get("loc", [])],
            msg=error.get("msg", "Unknown error"),
            type=error.get("type", "unknown")
        ))
    
    validation_error = APIValidationError(
        status=StatusEnum.ERROR,
        errors=errors,
        path=str(request.url.path)
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=validation_error.model_dump(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Обработчик ошибок базы данных
    
    Args:
        request: Запрос
        exc: Ошибка SQLAlchemy
    
    Returns:
        JSONResponse с деталями ошибки
    """
    logger.error(f"Database Error: {str(exc)}", exc_info=True)
    
    # Определение типа ошибки БД
    if isinstance(exc, IntegrityError):
        error = ResponseBuilder.error(
            message="Ошибка целостности данных",
            error_code=ErrorCodeEnum.CONFLICT,
            details=ErrorDetail(reason="Нарушение целостности базы данных")
        )
        status_code = 409
    else:
        error = ResponseBuilder.error(
            message="Ошибка базы данных",
            error_code=ErrorCodeEnum.INTERNAL_ERROR,
            details=ErrorDetail(reason="Внутренняя ошибка БД")
        )
        status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Глобальный обработчик всех необработанных исключений
    
    Args:
        request: Запрос
        exc: Исключение
    
    Returns:
        JSONResponse с деталями ошибки
    """
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        exc_info=True,
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": str(request.url.path),
            "method": request.method,
        }
    )
    
    # В продакшене не показываем детали ошибки
    error = ResponseBuilder.internal_error(
        message="Внутренняя ошибка сервера",
        details=ErrorDetail(
            reason="Обратитесь к администратору"
        ) if False else None  # Заменить на True для debug режима
    )
    
    return JSONResponse(
        status_code=500,
        content=error.model_dump(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )


# ============================================================================
# REGISTER EXCEPTION HANDLERS
# ============================================================================


def register_exception_handlers(app: FastAPI) -> None:
    """
    Зарегистрировать все обработчики исключений
    
    Args:
        app: FastAPI приложение
    """
    # Исключения приложения
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(NotFoundException, app_exception_handler)
    app.add_exception_handler(UnauthorizedException, app_exception_handler)
    app.add_exception_handler(ForbiddenException, app_exception_handler)
    app.add_exception_handler(ConflictException, app_exception_handler)
    app.add_exception_handler(TooManyRequestsException, app_exception_handler)
    app.add_exception_handler(ValidationAppException, app_exception_handler)
    app.add_exception_handler(InternalServerException, app_exception_handler)
    
    # HTTP исключения
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Ошибки валидации
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    
    # Ошибки базы данных
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(IntegrityError, sqlalchemy_exception_handler)
    
    # Глобальный обработчик
    app.add_exception_handler(Exception, global_exception_handler)
    
    logger.info("✅ Обработчики исключений зарегистрированы")


# ============================================================================
# DEPENDENCIES
# ============================================================================


def get_request_id(request: Request) -> str:
    """
    Получить или создать ID запроса
    
    Args:
        request: Запрос
    
    Returns:
        str: ID запроса
    """
    if not hasattr(request.state, "request_id"):
        import uuid
        request.state.request_id = str(uuid.uuid4())
    
    return getattr(request.state, "request_id", None)


# ============================================================================
# EXPORT
# ============================================================================


__all__ = [
    # Exception classes
    'AppException',
    'NotFoundException',
    'UnauthorizedException',
    'ForbiddenException',
    'ConflictException',
    'TooManyRequestsException',
    'ValidationAppException',
    'InternalServerException',
    
    # Handlers
    'register_exception_handlers',
    'get_request_id',
]
