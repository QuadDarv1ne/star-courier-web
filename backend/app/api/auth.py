"""
StarCourier Web - Auth API Router
API endpoints для аутентификации

Автор: QuadDarv1ne
Версия: 1.1.0
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends

from app.models.auth import (
    UserCreate, UserResponse, UserLogin, Token
)
from app.services.auth_service import auth_service, get_current_user, get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# REGISTRATION
# ============================================================================

@router.post("/register", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Регистрация нового пользователя")
async def register(user_data: UserCreate) -> UserResponse:
    """
    Регистрация нового пользователя.

    Требования к паролю:
    - Минимум 8 символов
    - Хотя бы одна заглавная буква
    - Хотя бы одна строчная буква
    - Хотя бы одна цифра

    Username может содержать только буквы, цифры и подчёркивание.
    
    Args:
        user_data: Данные пользователя для регистрации
        
    Returns:
        UserResponse: Данные зарегистрированного пользователя
        
    Raises:
        HTTPException: 500 при ошибке регистрации
    """
    try:
        user: UserResponse = auth_service.create_user(user_data)
        logger.info(f"✅ Пользователь зарегистрирован: {user.username}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации"
        )


# ============================================================================
# LOGIN
# ============================================================================

@router.post("/login", response_model=Token,
             summary="Вход в систему")
async def login(login_data: UserLogin) -> Token:
    """
    Вход в систему по username и паролю.

    Возвращает access_token и refresh_token.
    Access token действителен 30 минут.
    Refresh token действителен 7 дней.
    
    Args:
        login_data: Данные для входа (username, password)
        
    Returns:
        Token: Access и refresh токены
        
    Raises:
        HTTPException: 500 при ошибке входа
    """
    try:
        tokens: Token = auth_service.login(login_data)
        logger.info(f"✅ Пользователь вошёл: {login_data.username}")
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка входа: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при входе"
        )


# ============================================================================
# TOKEN REFRESH
# ============================================================================

@router.post("/refresh", response_model=Token,
             summary="Обновление токенов")
async def refresh_token(refresh_token: str) -> Token:
    """
    Обновление access токена с помощью refresh токена.

    Используйте refresh_token, полученный при входе.
    
    Args:
        refresh_token: Refresh токен для обновления
        
    Returns:
        Token: Новые access и refresh токены
        
    Raises:
        HTTPException: 500 при ошибке обновления
    """
    try:
        tokens: Token = auth_service.refresh_token(refresh_token)
        logger.info("✅ Токены обновлены")
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка обновления токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении токена"
        )


# ============================================================================
# USER PROFILE
# ============================================================================

@router.get("/me", response_model=UserResponse,
            summary="Получить профиль текущего пользователя")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Получение профиля текущего авторизованного пользователя.
    
    Требует заголовок: Authorization: Bearer {access_token}
    """
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        created_at=datetime.fromisoformat(current_user["created_at"]),
        last_login=datetime.fromisoformat(current_user["last_login"]) if current_user.get("last_login") else None,
        games_played=current_user.get("games_played", 0),
        total_playtime=current_user.get("total_playtime", 0),
        achievements_count=current_user.get("achievements_count", 0)
    )


@router.get("/me/stats",
            summary="Получить статистику игр пользователя")
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    """
    Получение всей игровой статистики пользователя.
    
    Возвращает список всех игровых сессий с результатами.
    """
    stats = auth_service.get_user_stats(current_user["id"])
    return {
        "user_id": current_user["id"],
        "username": current_user["username"],
        "games_count": len(stats),
        "games": stats
    }


# ============================================================================
# VALIDATION
# ============================================================================

@router.get("/validate",
            summary="Проверка валидности токена")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """
    Проверка валидности access токена.
    
    Возвращает информацию о пользователе, если токен валиден.
    """
    return {
        "valid": True,
        "user_id": current_user["id"],
        "username": current_user["username"]
    }


# ============================================================================
# LOGOUT
# ============================================================================

@router.post("/logout",
             summary="Выход из системы")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Выход из системы.
    
    В текущей реализации токены не инвалидируются на сервере.
    Клиент должен удалить токены локально.
    """
    logger.info(f"👋 Пользователь вышел: {current_user['username']}")
    return {
        "message": "Успешный выход",
        "note": "Удалите токены на клиенте"
    }


# ============================================================================
# ACCOUNT MANAGEMENT
# ============================================================================

@router.delete("/account",
               summary="Удаление аккаунта")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """
    Удаление аккаунта пользователя.
    
    ⚠️ Это действие необратимо! Все данные будут удалены.
    """
    user_id = current_user["id"]
    username = current_user["username"]
    
    # Удаление пользователя
    if user_id in auth_service.users:
        del auth_service.users[user_id]
        auth_service._save_users()
    
    # Удаление статистики
    stats_to_delete = [
        pid for pid, stats in auth_service.player_stats.items()
        if stats.get("user_id") == user_id
    ]
    for pid in stats_to_delete:
        del auth_service.player_stats[pid]
    auth_service._save_player_stats()
    
    logger.info(f"🗑️ Аккаунт удалён: {username}")
    
    return {
        "message": "Аккаунт успешно удалён",
        "username": username
    }
