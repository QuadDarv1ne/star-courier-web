"""
StarCourier Web - Security Middleware
Middleware для безопасности

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
import re
from typing import Callable, List, Optional
from datetime import datetime

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware для безопасности

    Добавляет:
    - Security заголовки (CSP, XSS Protection, etc.)
    - Защиту от распространённых атак
    - Проверку User-Agent
    - CORS headers (если не используется CORSMiddleware)
    """

    # Security headers по умолчанию
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    # Content Security Policy
    CSP_DIRECTIVES: dict = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "data:"],
        "connect-src": ["'self'", "ws:", "wss:"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
    
    # Паттерны для обнаружения атак
    ATTACK_PATTERNS = [
        # SQL Injection
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        # XSS
        r"<\s*script",
        r"javascript\s*:",
        r"on\w+\s*=",
        # Path Traversal
        r"\.\./|\.\.\\",
        # Command Injection
        r"[;&|`$]",
        r"\b(cat|ls|rm|wget|curl|bash|sh|nc|netcat)\b",
    ]
    
    # Заблокированные User-Agent
    BLOCKED_USER_AGENTS = [
        r"sqlmap",
        r"nikto",
        r"nmap",
        r"masscan",
        r"dirbuster",
        r"gobuster",
        r"wfuzz",
        r"burp",
        r"zap",
        r"scanner",
        r"crawler",
        r"spider",
    ]
    
    def __init__(
        self,
        app,
        enable_csp: bool = True,
        enable_attack_detection: bool = True,
        custom_headers: dict = None,
        allowed_hosts: List[str] = None,
        debug: bool = False
    ):
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_attack_detection = enable_attack_detection
        self.custom_headers = custom_headers or {}
        self.allowed_hosts = allowed_hosts
        self.debug = debug
        
        # Компиляция паттернов
        self._attack_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.ATTACK_PATTERNS
        ]
        self._blocked_agents = [
            re.compile(p, re.IGNORECASE) for p in self.BLOCKED_USER_AGENTS
        ]
    
    def _build_csp(self) -> str:
        """Построение CSP заголовка"""
        directives = []
        for directive, sources in self.CSP_DIRECTIVES.items():
            directives.append(f"{directive} {' '.join(sources)}")
        return "; ".join(directives)
    
    def _check_host(self, request: Request) -> bool:
        """Проверка Host заголовка"""
        if not self.allowed_hosts:
            return True
        
        host = request.headers.get("Host", "")
        return host in self.allowed_hosts or host.split(":")[0] in self.allowed_hosts
    
    def _check_user_agent(self, request: Request) -> bool:
        """Проверка User-Agent"""
        user_agent = request.headers.get("User-Agent", "")
        
        for pattern in self._blocked_agents:
            if pattern.search(user_agent):
                logger.warning(f"🚫 Blocked User-Agent: {user_agent}")
                return False
        
        return True
    
    def _detect_attack(self, request: Request) -> Optional[str]:
        """Обнаружение попыток атаки"""
        if not self.enable_attack_detection:
            return None
        
        # Проверка URL
        url = str(request.url)
        for pattern in self._attack_patterns:
            if pattern.search(url):
                return f"Suspicious pattern in URL: {url}"
        
        # Проверка query параметров
        query = str(request.query_params)
        if query:
            for pattern in self._attack_patterns:
                if pattern.search(query):
                    return f"Suspicious pattern in query: {query}"
        
        # Проверка заголовков
        for header, value in request.headers.items():
            if header.lower() not in ["authorization", "cookie"]:
                for pattern in self._attack_patterns:
                    if pattern.search(value):
                        return f"Suspicious pattern in header {header}"
        
        return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение IP клиента"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса"""
        
        client_ip = self._get_client_ip(request)
        
        # Проверка Host заголовка
        if not self._check_host(request):
            logger.warning(f"🚫 Invalid Host from {client_ip}")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Invalid Host header"}
            )
        
        # Проверка User-Agent
        if not self._check_user_agent(request):
            return JSONResponse(
                status_code=403,
                content={"status": "error", "message": "Forbidden"}
            )
        
        # Обнаружение атак
        attack = self._detect_attack(request)
        if attack:
            logger.warning(f"🚨 Potential attack detected from {client_ip}: {attack}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error", 
                    "message": "Invalid request"
                }
            )
        
        # Выполнение запроса
        response = await call_next(request)
        
        # Добавление security заголовков
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Добавление CSP
        if self.enable_csp and "text/html" in response.headers.get("content-type", ""):
            response.headers["Content-Security-Policy"] = self._build_csp()
        
        # Добавление пользовательских заголовков
        for header, value in self.custom_headers.items():
            response.headers[header] = value
        
        # Добавление Server заголовка (скрытие информации)
        response.headers["Server"] = "StarCourier"
        
        return response


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_nonce() -> str:
    """Генерация nonce для CSP"""
    import secrets
    import base64
    return base64.b64encode(secrets.token_bytes(16)).decode('utf-8')


def get_client_ip(request: Request) -> str:
    """Получение реального IP клиента"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"
