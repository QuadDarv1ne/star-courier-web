"""
StarCourier Web - API Tests
Тесты для всех API endpoints

Запуск: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Добавляем путь к backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app


client = TestClient(app)


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

class TestHealthCheck:
    """Тесты health check endpoint"""

    def test_health_returns_200(self):
        """Health check должен возвращать 200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_contains_status(self):
        """Health check должен содержать статус"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self):
        """Корневой endpoint должен работать"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "StarCourier Web"


# ============================================================================
# GAME API TESTS
# ============================================================================

class TestGameAPI:
    """Тесты Game API"""

    def test_start_game(self):
        """Тест начала новой игры"""
        response = client.post("/api/game/start", json={"player_id": "test_player_1"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "scene" in data
        assert data["scene"]["id"] == "start"
        assert "stats" in data
        assert "relationships" in data

    def test_start_game_scene_has_choices(self):
        """Начальная сцена должна иметь выборы"""
        response = client.post("/api/game/start", json={"player_id": "test_player_2"})
        data = response.json()
        assert len(data["scene"]["choices"]) >= 1

    def test_get_scene(self):
        """Тест получения конкретной сцены"""
        response = client.get("/api/game/scene/start")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "start"
        assert "title" in data
        assert "text" in data

    def test_get_nonexistent_scene(self):
        """Тест получения несуществующей сцены"""
        response = client.get("/api/game/scene/nonexistent_scene")
        assert response.status_code == 404

    def test_make_choice(self):
        """Тест совершения выбора"""
        # Сначала начинаем игру
        client.post("/api/game/start", json={"player_id": "test_player_3"})

        # Делаем выбор
        response = client.post("/api/game/choose", json={
            "player_id": "test_player_3",
            "next_scene": "command_center",
            "stats": {"morale": 10}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["scene"]["id"] == "command_center"

    def test_make_choice_nonexistent_player(self):
        """Тест выбора несуществующим игроком"""
        response = client.post("/api/game/choose", json={
            "player_id": "nonexistent_player",
            "next_scene": "start"
        })
        assert response.status_code == 404

    def test_get_player_stats(self):
        """Тест получения статистики игрока"""
        # Начинаем игру
        client.post("/api/game/start", json={"player_id": "test_player_4"})

        # Получаем статистику
        response = client.get("/api/game/stats/test_player_4")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "relationships" in data
        assert "choices_made" in data

    def test_delete_player(self):
        """Тест удаления игрока"""
        # Создаём игрока
        client.post("/api/game/start", json={"player_id": "test_player_5"})

        # Удаляем
        response = client.delete("/api/game/player/test_player_5")
        assert response.status_code == 200

        # Проверяем, что игрок удалён
        response = client.get("/api/game/stats/test_player_5")
        assert response.status_code == 404


# ============================================================================
# CHARACTERS API TESTS
# ============================================================================

class TestCharactersAPI:
    """Тесты Characters API"""

    def test_list_characters(self):
        """Тест получения списка персонажей"""
        response = client.get("/api/characters")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # Минимум 3 персонажа

    def test_get_character(self):
        """Тест получения конкретного персонажа"""
        response = client.get("/api/characters/sara_nova")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sara_nova"
        assert data["name"] == "Сара Нова"

    def test_get_nonexistent_character(self):
        """Тест получения несуществующего персонажа"""
        response = client.get("/api/characters/nonexistent")
        assert response.status_code == 404


# ============================================================================
# SCENES API TESTS
# ============================================================================

class TestScenesAPI:
    """Тесты Scenes API"""

    def test_list_scenes(self):
        """Тест получения списка сцен"""
        response = client.get("/api/scenes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 10  # Минимум 10 сцен

    def test_scenes_count(self):
        """Тест подсчёта сцен"""
        response = client.get("/api/scenes/count")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 10


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Интеграционные тесты"""

    def test_full_game_flow(self):
        """Тест полного игрового цикла"""
        player_id = "integration_test_player"

        # 1. Начинаем игру
        response = client.post("/api/game/start", json={"player_id": player_id})
        assert response.status_code == 200
        initial_stats = response.json()["stats"]

        # 2. Делаем несколько выборов
        choices = ["command_center", "sigma_station", "defend_station"]
        for scene in choices:
            response = client.post("/api/game/choose", json={
                "player_id": player_id,
                "next_scene": scene
            })
            # Игнорируем ошибки (сцена может не существовать)

        # 3. Проверяем финальную статистику
        response = client.get(f"/api/game/stats/{player_id}")
        assert response.status_code == 200

        # 4. Удаляем игрока
        response = client.delete(f"/api/game/player/{player_id}")
        assert response.status_code == 200


# ============================================================================
# GAME HELPERS TESTS
# ============================================================================

class TestGameHelpers:
    """Тесты вспомогательных функций игры"""

    def test_check_game_over_health(self):
        """Проверка конца игры по здоровью"""
        from app.api.game import check_game_over
        
        # Игра не окончена
        is_over, reason = check_game_over({"health": 50, "morale": 50})
        assert is_over is False
        assert reason is None
        
        # Игра окончена (health)
        is_over, reason = check_game_over({"health": 0, "morale": 50})
        assert is_over is True
        assert reason == "health_depleted"

    def test_check_game_over_morale(self):
        """Проверка конца игры по морали"""
        from app.api.game import check_game_over
        
        # Игра окончена (morale)
        is_over, reason = check_game_over({"health": 50, "morale": 0})
        assert is_over is True
        assert reason == "morale_depleted"

    def test_is_ending_scene(self):
        """Проверка финальных сцен"""
        from app.api.game import is_ending_scene
        
        assert is_ending_scene("ancient_awakening") is True
        assert is_ending_scene("hide_artifact") is True
        assert is_ending_scene("start") is False
        assert is_ending_scene("command_center") is False

    def test_get_ending_type(self):
        """Проверка типа концовки"""
        from app.api.game import get_ending_type
        
        assert get_ending_type("ancient_awakening") == "awakening"
        assert get_ending_type("hide_artifact") == "guardian"
        assert get_ending_type("start") is None

    def test_apply_stat_changes(self):
        """Проверка применения изменений статистики"""
        from app.api.game import apply_stat_changes
        
        stats = {"health": 100, "morale": 75, "knowledge": 30}
        
        # Положительное изменение
        new_stats = apply_stat_changes(stats, {"health": 10, "morale": -5})
        assert new_stats["health"] == 100  # capped at 100
        assert new_stats["morale"] == 70
        assert new_stats["knowledge"] == 30  # unchanged
        
        # Отрицательное изменение
        new_stats = apply_stat_changes(stats, {"health": -50})
        assert new_stats["health"] == 50

        # Изменение за пределами диапазона
        new_stats = apply_stat_changes(stats, {"health": -150})
        assert new_stats["health"] == 0  # capped at 0


# ============================================================================
# CHARACTERS API TESTS
# ============================================================================

class TestCharactersAPI:
    """Тесты Characters API"""

    def test_list_characters(self):
        """Тест получения списка персонажей"""
        response = client.get("/api/characters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Должен быть хотя бы один персонаж
        assert len(data) >= 1

    def test_character_has_required_fields(self):
        """Проверка полей персонажа"""
        response = client.get("/api/characters")
        data = response.json()
        
        for char_id, char_data in data.items():
            assert "id" in char_data
            assert "name" in char_data
            assert "role" in char_data
            assert "description" in char_data

    def test_get_character_by_id(self):
        """Тест получения персонажа по ID"""
        # Получаем список персонажей
        response = client.get("/api/characters")
        characters = response.json()
        
        if characters:
            # Берём первый ID персонажа
            char_id = list(characters.keys())[0]
            response = client.get(f"/api/characters/{char_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == char_id

    def test_get_character_not_found(self):
        """Тест 404 для несуществующего персонажа"""
        response = client.get("/api/characters/nonexistent_character")
        assert response.status_code == 404


# ============================================================================
# SCENES API TESTS
# ============================================================================

class TestScenesAPI:
    """Тесты Scenes API"""

    def test_list_scenes(self):
        """Тест получения списка сцен"""
        response = client.get("/api/scenes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Должно быть хотя бы 10 сцен
        assert len(data) >= 10

    def test_scenes_count(self):
        """Тест подсчёта сцен"""
        response = client.get("/api/scenes/count")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "endings" in data
        assert data["total"] >= 10
        assert data["endings"] >= 0

    def test_scenes_count_matches_list(self):
        """Проверка что count совпадает с количеством сцен в списке"""
        scenes_response = client.get("/api/scenes")
        count_response = client.get("/api/scenes/count")
        
        scenes = scenes_response.json()
        count = count_response.json()
        
        assert count["total"] == len(scenes)


# ============================================================================
# LEADERBOARD API TESTS
# ============================================================================

class TestLeaderboardAPI:
    """Тесты Leaderboard API"""

    def test_get_leaderboard(self):
        """Тест получения таблицы лидеров"""
        response = client.get("/api/leaderboard/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_leaderboard_limit_parameter(self):
        """Тест параметра limit"""
        response = client.get("/api/leaderboard/?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_leaderboard_default_limit(self):
        """Тест limit по умолчанию (10)"""
        response = client.get("/api/leaderboard/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10

    def test_leaderboard_entry_has_fields(self):
        """Проверка полей записи в таблице лидеров"""
        response = client.get("/api/leaderboard/")
        data = response.json()
        
        if data:
            entry = data[0]
            assert "rank" in entry
            assert "username" in entry
            assert "score" in entry
            assert "games_completed" in entry
            assert "achievements" in entry
            assert "playtime" in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
