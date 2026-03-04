"""
StarCourier Web - Auth Service (Database Version)
Сервис аутентификации и авторизации с поддержкой SQLite

Автор: QuadDarv1ne
Версия: 2.0.0
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import bcrypt
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import UserCreate, UserResponse, Token, PlayerStatsDB
from app.database.connection import get_db
from app.database.models import User
from app.services.db_service import UserService, PlayerStatsService

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "starcourier-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer(auto_error=False)


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """Хэширование пароля с bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================

def create_access_token(user_id: str, username: str) -> str:
    """Создание access токена"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Создание refresh токена"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодирование токена"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def create_tokens(user_id: str, username: str) -> Token:
    """Создание пары токенов"""
    access_token = create_access_token(user_id, username)
    refresh_token = create_refresh_token(user_id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ============================================================================
# AUTH SERVICE CLASS
# ============================================================================

class AuthService:
    """Сервис аутентификации с базой данных"""
    
    async def create_user(
        self, 
        session: AsyncSession, 
        user_data: UserCreate
    ) -> UserResponse:
        """Создание нового пользователя"""
        import uuid
        
        # Проверка существования username
        existing_user = await UserService.get_by_username(session, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким username уже существует"
            )
        
        # Проверка существования email
        existing_email = await UserService.get_by_email(session, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Генерация ID
        user_id = str(uuid.uuid4())
        
        # Создание пользователя
        user = await UserService.create(
            session,
            user_id=user_id,
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            password_hash=hash_password(user_data.password)
        )
        
        logger.info(f"👤 Создан новый пользователь: {user_data.username}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            games_played=user.games_played,
            total_playtime=user.total_playtime,
            achievements_count=user.achievements_count
        )
    
    async def authenticate_user(
        self, 
        session: AsyncSession, 
        username: str, 
        password: str
    ) -> Optional[User]:
        """Аутентификация пользователя"""
        user = await UserService.get_by_username(session, username)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Обновление last_login
        await UserService.update_last_login(session, user.id)
        
        return user
    
    async def login(
        self, 
        session: AsyncSession, 
        login_data
    ) -> Token:
        """Вход пользователя"""
        user = await self.authenticate_user(
            session, 
            login_data.username, 
            login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный username или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"🔐 Пользователь вошёл: {user.username}")
        
        return create_tokens(user.id, user.username)
    
    async def refresh_token(
        self, 
        session: AsyncSession, 
        refresh_token: str
    ) -> Token:
        """Обновление токенов"""
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный refresh токен"
            )
        
        user_id = payload.get("sub")
        user = await UserService.get_by_id(session, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        return create_tokens(user.id, user.username)
    
    async def get_current_user(
        self,
        session: AsyncSession,
        credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> User:
        """Получение текущего пользователя из токена"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Необходима авторизация",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или истёкший токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        user = await UserService.get_by_id(session, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        return user


# Глобальный экземпляр сервиса
auth_service = AuthService()


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_current_user(
    session: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """Dependency для получения текущего пользователя"""
    return await auth_service.get_current_user(session, credentials)


async def get_current_user_optional(
    session: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Dependency для опционального получения пользователя"""
    if not credentials:
        return None
    try:
        return await auth_service.get_current_user(session, credentials)
    except HTTPException:
        return None
