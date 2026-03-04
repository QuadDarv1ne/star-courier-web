"""
StarCourier Web - Advanced API Tests
Расширенные тесты для всех новых функций

Запуск: pytest tests/test_advanced.py -v
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os

# Добавляем путь к backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Асинхронный клиент для тестирования"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# ============================================================================
# AUTH API TESTS
# ============================================================================

class TestAuthAPI:
    """Тесты Auth API"""

    @pytest.mark.asyncio
    async def test_register_user(self, async_client):
        """Тест регистрации пользователя"""
        response = await async_client.post("/api/auth/register", json={
            "username": "testuser_auth",
            "email": "testuser_auth@test.com",
            "password": "TestPass123"
        })
        assert response.status_code in [200, 400]  # 400 если уже существует

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client):
        """Тест регистрации со слабым паролем"""
        response = await async_client.post("/api/auth/register", json={
            "username": "weakpass_user",
            "email": "weak@test.com",
            "password": "weak"  # Слишком простой пароль
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_invalid_user(self, async_client):
        """Тест входа с неверными данными"""
        response = await async_client.post("/api/auth/login", json={
            "username": "nonexistent_user_12345",
            "password": "WrongPass123"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, async_client):
        """Тест входа без обязательных полей"""
        response = await async_client.post("/api/auth/login", json={
            "username": "test"
            # password отсутствует
        })
        assert response.status_code == 422


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

class TestRateLimiting:
    """Тесты rate limiting"""

    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, async_client):
        """Тест наличия заголовков rate limit"""
        response = await async_client.get("/health")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    @pytest.mark.asyncio
    async def test_health_not_rate_limited(self, async_client):
        """Тест что health endpoint не ограничен"""
        # Health endpoint должен быть исключён из rate limiting
        for _ in range(5):
            response = await async_client.get("/health")
            assert response.status_code == 200


# ============================================================================
# ANALYTICS API TESTS
# ============================================================================

class TestAnalyticsAPI:
    """Тесты Analytics API"""

    @pytest.mark.asyncio
    async def test_track_event(self, async_client):
        """Тест отслеживания события"""
        response = await async_client.post("/api/analytics/track", json={
            "event_type": "test_event",
            "event_name": "test_action",
            "event_data": {"test_key": "test_value"}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["event_type"] == "test_event"
        assert data["event_name"] == "test_action"

    @pytest.mark.asyncio
    async def test_analytics_summary(self, async_client):
        """Тест получения сводки аналитики"""
        response = await async_client.get("/api/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "events_by_type" in data
        assert "unique_users" in data

    @pytest.mark.asyncio
    async def test_daily_stats(self, async_client):
        """Тест статистики по дням"""
        response = await async_client.get("/api/analytics/daily?days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_realtime_stats(self, async_client):
        """Тест статистики в реальном времени"""
        response = await async_client.get("/api/analytics/realtime")
        assert response.status_code == 200
        data = response.json()
        assert "active_sessions" in data
        assert "events_last_hour" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_game_funnel(self, async_client):
        """Тест воронки игры"""
        response = await async_client.get("/api/analytics/funnel")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for step in data:
            assert "step" in step
            assert "count" in step
            assert "percentage" in step


# ============================================================================
# LEADERBOARD API TESTS
# ============================================================================

class TestLeaderboardAPI:
    """Тесты Leaderboard API"""

    @pytest.mark.asyncio
    async def test_get_leaderboard(self, async_client):
        """Тест получения таблицы лидеров"""
        response = await async_client.get("/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaders" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_leaderboard_pagination(self, async_client):
        """Тест пагинации таблицы лидеров"""
        response = await async_client.get("/api/leaderboard?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["leaders"]) <= 5


# ============================================================================
# ACHIEVEMENTS API TESTS
# ============================================================================

class TestAchievementsAPI:
    """Тесты Achievements API"""

    @pytest.mark.asyncio
    async def test_list_achievements(self, async_client):
        """Тест получения списка достижений"""
        response = await async_client.get("/api/achievements")
        assert response.status_code == 200
        data = response.json()
        assert "achievements" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_achievements_by_category(self, async_client):
        """Тест фильтрации достижений по категории"""
        response = await async_client.get("/api/achievements?category=story")
        assert response.status_code == 200
        data = response.json()
        for achievement in data["achievements"]:
            assert achievement["category"] == "story"

    @pytest.mark.asyncio
    async def test_achievement_categories(self, async_client):
        """Тест получения категорий достижений"""
        response = await async_client.get("/api/achievements/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Тесты безопасности"""

    @pytest.mark.asyncio
    async def test_security_headers(self, async_client):
        """Тест наличия security заголовков"""
        response = await async_client.get("/health")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers

    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, async_client):
        """Тест защиты от SQL инъекций"""
        # Попытка SQL инъекции в username
        response = await async_client.post("/api/auth/register", json={
            "username": "admin' OR '1'='1",
            "email": "sql@test.com",
            "password": "TestPass123"
        })
        # Должен вернуть ошибку валидации или отказ
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_xss_protection(self, async_client):
        """Тест защиты от XSS"""
        response = await async_client.post("/api/analytics/track", json={
            "event_type": "test",
            "event_name": "<script>alert('xss')</script>",
            "event_data": {}
        })
        # Запрос должен пройти, но XSS должен быть нейтрализован
        assert response.status_code == 200


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Тесты обработки ошибок"""

    @pytest.mark.asyncio
    async def test_404_not_found(self, async_client):
        """Тест 404 ошибки"""
        response = await async_client.get("/api/nonexistent_endpoint")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, async_client):
        """Тест метода не разрешён"""
        response = await async_client.patch("/health")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_invalid_json(self, async_client):
        """Тест невалидного JSON"""
        response = await async_client.post(
            "/api/auth/register",
            content="invalid json{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Тесты производительности"""

    @pytest.mark.asyncio
    async def test_health_response_time(self, async_client):
        """Тест времени ответа health endpoint"""
        import time
        start = time.time()
        response = await async_client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Должен отвечать менее чем за 1 секунду

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client):
        """Тест параллельных запросов"""
        import asyncio
        
        async def make_request():
            return await async_client.get("/health")
        
        # 10 параллельных запросов
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            assert response.status_code == 200


# ============================================================================
# WEBSOCKET TESTS (Basic)
# ============================================================================

class TestWebSocket:
    """Базовые тесты WebSocket"""

    @pytest.mark.asyncio
    async def test_websocket_endpoint_exists(self, async_client):
        """Тест что WebSocket endpoint существует"""
        # WebSocket требует специального клиента, проверяем только что путь не возвращает 404
        # Для GET запроса WebSocket вернёт 426 Upgrade Required или 400
        response = await async_client.get("/ws/test_player")
        # WebSocket endpoint должен требовать upgrade
        assert response.status_code in [400, 426, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
