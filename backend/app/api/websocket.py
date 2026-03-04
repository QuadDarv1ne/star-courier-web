"""
StarCourier Web - WebSocket Router
Real-time коммуникация для multiplayer функций

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Менеджер WebSocket соединений.
    Управляет подключениями игроков и рассылкой сообщений.
    """

    def __init__(self):
        # Активные соединения: {player_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Комнаты игр: {game_id: set of player_ids}
        self.game_rooms: Dict[str, Set[str]] = {}
        # Метаданные соединений
        self.connection_metadata: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, player_id: str):
        """Принять новое соединение"""
        await websocket.accept()
        self.active_connections[player_id] = websocket
        self.connection_metadata[player_id] = {
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "game_id": None
        }
        logger.info(f"🔌 Игрок {player_id} подключился")
        await self.send_personal_message(player_id, {
            "type": "connection_established",
            "player_id": player_id,
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, player_id: str):
        """Обработать отключение"""
        if player_id in self.active_connections:
            del self.active_connections[player_id]

        # Удалить из комнаты игры
        metadata = self.connection_metadata.get(player_id, {})
        game_id = metadata.get("game_id")
        if game_id and game_id in self.game_rooms:
            self.game_rooms[game_id].discard(player_id)
            if not self.game_rooms[game_id]:
                del self.game_rooms[game_id]

        if player_id in self.connection_metadata:
            del self.connection_metadata[player_id]

        logger.info(f"🔌 Игрок {player_id} отключился")

    async def send_personal_message(self, player_id: str, message: dict):
        """Отправить сообщение конкретному игроку"""
        if player_id in self.active_connections:
            try:
                await self.active_connections[player_id].send_json(message)
            except Exception as e:
                logger.error(f"❌ Ошибка отправки сообщения {player_id}: {e}")

    async def broadcast(self, message: dict, exclude: Optional[Set[str]] = None):
        """Отправить сообщение всем подключенным игрокам"""
        exclude = exclude or set()
        for player_id, connection in self.active_connections.items():
            if player_id not in exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"❌ Ошибка broadcast для {player_id}: {e}")

    async def broadcast_to_game(self, game_id: str, message: dict,
                                 exclude: Optional[Set[str]] = None):
        """Отправить сообщение всем игрокам в комнате игры"""
        if game_id not in self.game_rooms:
            return

        exclude = exclude or set()
        for player_id in self.game_rooms[game_id]:
            if player_id not in exclude and player_id in self.active_connections:
                try:
                    await self.active_connections[player_id].send_json(message)
                except Exception as e:
                    logger.error(f"❌ Ошибка game broadcast для {player_id}: {e}")

    async def join_game_room(self, player_id: str, game_id: str):
        """Добавить игрока в комнату игры"""
        if game_id not in self.game_rooms:
            self.game_rooms[game_id] = set()

        self.game_rooms[game_id].add(player_id)

        if player_id in self.connection_metadata:
            self.connection_metadata[player_id]["game_id"] = game_id
            self.connection_metadata[player_id]["last_activity"] = datetime.now().isoformat()

        logger.info(f"🎮 Игрок {player_id} присоединился к игре {game_id}")

        # Уведомить других игроков
        await self.broadcast_to_game(game_id, {
            "type": "player_joined",
            "player_id": player_id,
            "game_id": game_id,
            "players_count": len(self.game_rooms[game_id]),
            "timestamp": datetime.now().isoformat()
        }, exclude={player_id})

    async def leave_game_room(self, player_id: str, game_id: str):
        """Удалить игрока из комнаты игры"""
        if game_id in self.game_rooms:
            self.game_rooms[game_id].discard(player_id)

            if player_id in self.connection_metadata:
                self.connection_metadata[player_id]["game_id"] = None

            logger.info(f"🚪 Игрок {player_id} покинул игру {game_id}")

            # Уведомить остальных
            await self.broadcast_to_game(game_id, {
                "type": "player_left",
                "player_id": player_id,
                "game_id": game_id,
                "players_count": len(self.game_rooms.get(game_id, set())),
                "timestamp": datetime.now().isoformat()
            })

    def get_connection_count(self) -> int:
        """Получить количество активных соединений"""
        return len(self.active_connections)

    def get_game_room_players(self, game_id: str) -> Set[str]:
        """Получить список игроков в комнате"""
        return self.game_rooms.get(game_id, set())


# Глобальный менеджер соединений
manager = ConnectionManager()


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """
    WebSocket endpoint для real-time коммуникации.

    Поддерживаемые типы сообщений от клиента:
    - ping: проверка соединения
    - join_game: присоединиться к комнате игры
    - leave_game: покинуть комнату игры
    - game_action: выполнить действие в игре
    - chat_message: отправить сообщение в чат

    Типы сообщений от сервера:
    - connection_established: соединение установлено
    - pong: ответ на ping
    - player_joined: игрок присоединился
    - player_left: игрок покинул
    - game_update: обновление состояния игры
    - chat_message: сообщение чата
    - achievement_unlocked: достижение разблокировано
    - scene_update: обновление сцены
    """
    await manager.connect(websocket, player_id)

    try:
        while True:
            # Получаем сообщение
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal_message(player_id, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue

            # Обновляем время последней активности
            if player_id in manager.connection_metadata:
                manager.connection_metadata[player_id]["last_activity"] = datetime.now().isoformat()

            # Обрабатываем сообщение по типу
            message_type = message.get("type")

            if message_type == "ping":
                await manager.send_personal_message(player_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

            elif message_type == "join_game":
                game_id = message.get("game_id")
                if game_id:
                    await manager.join_game_room(player_id, game_id)

            elif message_type == "leave_game":
                game_id = message.get("game_id")
                if game_id:
                    await manager.leave_game_room(player_id, game_id)

            elif message_type == "game_action":
                game_id = message.get("game_id")
                action = message.get("action")
                if game_id and action:
                    # Broadcast action to all players in game
                    await manager.broadcast_to_game(game_id, {
                        "type": "game_update",
                        "player_id": player_id,
                        "action": action,
                        "data": message.get("data", {}),
                        "timestamp": datetime.now().isoformat()
                    })

            elif message_type == "chat_message":
                game_id = message.get("game_id")
                text = message.get("text", "").strip()
                if game_id and text:
                    await manager.broadcast_to_game(game_id, {
                        "type": "chat_message",
                        "player_id": player_id,
                        "text": text,
                        "timestamp": datetime.now().isoformat()
                    })

            elif message_type == "request_sync":
                # Запрос на синхронизацию состояния игры
                game_id = message.get("game_id")
                if game_id:
                    await manager.send_personal_message(player_id, {
                        "type": "sync_response",
                        "game_id": game_id,
                        "players": list(manager.get_game_room_players(game_id)),
                        "timestamp": datetime.now().isoformat()
                    })

            else:
                await manager.send_personal_message(player_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(player_id)

    except Exception as e:
        logger.error(f"❌ WebSocket error for {player_id}: {e}")
        manager.disconnect(player_id)


# ============================================================================
# HTTP ENDPOINTS FOR WEBSOCKET STATUS
# ============================================================================

@router.get("/status", summary="Статус WebSocket сервера")
async def get_websocket_status():
    """Получить информацию о состоянии WebSocket сервера"""
    return {
        "status": "active",
        "connections": manager.get_connection_count(),
        "game_rooms": len(manager.game_rooms),
        "rooms_details": {
            game_id: len(players)
            for game_id, players in manager.game_rooms.items()
        }
    }


@router.get("/players/{player_id}/status", summary="Статус игрока")
async def get_player_status(player_id: str):
    """Получить статус соединения игрока"""
    if player_id in manager.active_connections:
        metadata = manager.connection_metadata.get(player_id, {})
        return {
            "status": "connected",
            "player_id": player_id,
            "connected_at": metadata.get("connected_at"),
            "last_activity": metadata.get("last_activity"),
            "game_id": metadata.get("game_id")
        }
    return {
        "status": "disconnected",
        "player_id": player_id
    }
