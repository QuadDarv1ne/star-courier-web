# 📡 StarCourier Web - API Документация

Полная документация по API endpoints проекта StarCourier Web.

**Base URL:** `http://localhost:8000/api`  
**Версия API:** v1  
**Формат запросов/ответов:** JSON

---

## 📋 Содержание

- [Аутентификация](#-аутентификация)
- [Игра](#-игра)
- [Персонажи](#-персонажи)
- [Сцены](#-сцены)
- [Способности](#-способности)
- [Квесты](#-квесты)
- [Игровые механики](#-игровые-механики)
- [Лидеры](#-лидеры)
- [Достижения](#-достижения)
- [Аналитика](#-аналитика)
- [Данные](#-данные)
- [Администрирование](#-администрирование)

---

## 🔐 Аутентификация

### Регистрация

```http
POST /api/auth/register
Content-Type: application/json
```

**Request:**
```json
{
  "username": "player1",
  "email": "player@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Пользователь зарегистрирован",
  "data": {
    "user_id": "uuid",
    "username": "player1",
    "email": "player@example.com"
  }
}
```

### Вход

```http
POST /api/auth/login
Content-Type: application/json
```

**Request:**
```json
{
  "username": "player1",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Обновление токена

```http
POST /api/auth/refresh
Content-Type: application/json
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ...",
    "expires_in": 1800
  }
}
```

---

## 🎮 Игра

### Начать новую игру

```http
POST /api/game/start
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "game_id": "uuid",
    "chapter": 1,
    "scene_id": "intro_001",
    "player": {
      "name": "Макс Велл",
      "psychic": 10,
      "empathy": 10,
      "biotics": 10,
      "alchemy": 10
    }
  }
}
```

### Получить текущую сцену

```http
GET /api/game/current
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "scene_id": "chapter1_scene2",
    "chapter": 1,
    "title": "Первое задание",
    "text": "Вы стоите на космодроме...",
    "choices": [
      {
        "id": "choice_1",
        "text": "Принять задание",
        "next_scene": "scene_003"
      },
      {
        "id": "choice_2",
        "text": "Отказаться",
        "next_scene": "scene_004"
      }
    ]
  }
}
```

### Сделать выбор

```http
POST /api/game/choose
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "choice_id": "choice_1"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "scene_id": "scene_003",
    "text": "Вы принимаете задание...",
    "choices": [...]
  }
}
```

### Сохранить прогресс

```http
POST /api/game/save
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "save_name": "Перед боем"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Игра сохранена",
  "data": {
    "save_id": "uuid",
    "save_name": "Перед боем",
    "timestamp": "2026-03-15T10:30:00Z"
  }
}
```

### Загрузить сохранение

```http
POST /api/game/load
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "save_id": "uuid"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "scene_id": "scene_003",
    "chapter": 1,
    "player": {...}
  }
}
```

---

## 👥 Персонажи

### Получить всех персонажей

```http
GET /api/characters
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "char_001",
      "name": "Мия",
      "role": "Тактик",
      "relationship": 50,
      "romance_available": true,
      "description": "Опытный тактик..."
    },
    ...
  ]
}
```

### Получить персонажа по ID

```http
GET /api/characters/{character_id}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "char_001",
    "name": "Мия",
    "role": "Тактик",
    "relationship": 50,
    "dialogues": [...],
    "quests": [...]
  }
}
```

### Взаимодействовать с персонажем

```http
POST /api/characters/{character_id}/interact
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "action": "talk",
  "dialogue_id": "dialogue_001"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "relationship_change": 5,
    "new_relationship": 55,
    "dialogue_text": "..."
  }
}
```

---

## 📋 Сцены

### Получить сцену по ID

```http
GET /api/scenes/{scene_id}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "scene_001",
    "chapter": 1,
    "title": "Введение",
    "text": "Добро пожаловать...",
    "choices": [...],
    "requirements": {
      "min_chapter": 1
    }
  }
}
```

### Получить сцены главы

```http
GET /api/scenes/chapter/{chapter_number}
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "scene_001",
      "title": "Введение",
      "order": 1
    },
    ...
  ]
}
```

---

## ⚡ Способности

### Получить все способности

```http
GET /api/abilities
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "psychic": [
      {
        "id": "psychic_001",
        "name": "Телепатия",
        "level": 1,
        "description": "Чтение мыслей...",
        "cost": 10
      }
    ],
    "biotics": [...],
    "alchemy": [...],
    "resonance": [...]
  }
}
```

### Улучшить способность

```http
POST /api/abilities/upgrade
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "ability_id": "psychic_001",
  "ability_type": "psychic"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Способность улучшена",
  "data": {
    "ability_id": "psychic_001",
    "old_level": 1,
    "new_level": 2,
    "new_effect": "..."
  }
}
```

---

## 📜 Квесты

### Получить все квесты

```http
GET /api/quests
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` (optional): active, completed, failed
- `chapter` (optional): номер главы

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "quest_001",
      "title": "Первое задание",
      "description": "Найдите артефакт...",
      "status": "active",
      "chapter": 1,
      "rewards": {
        "credits": 100,
        "exp": 50
      }
    }
  ]
}
```

### Обновить прогресс квеста

```http
POST /api/quests/{quest_id}/progress
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "objective_id": "obj_001",
  "completed": true
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "quest_id": "quest_001",
    "progress": 50,
    "objectives_completed": 1,
    "objectives_total": 2
  }
}
```

### Завершить квест

```http
POST /api/quests/{quest_id}/complete
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Квест завершён!",
  "data": {
    "rewards": {
      "credits": 100,
      "exp": 50,
      "items": [...]
    }
  }
}
```

---

## 🎮 Игровые механики

### Получить состояние игрока

```http
GET /api/game-mechanics/state
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "resonance": {
      "level": 2,
      "experience": 150,
      "bonus": "Расширенный радиус (500)"
    },
    "path": {
      "value": "alliance",
      "progress": 30,
      "bonus": "Флот, ресурсы"
    },
    "mental_state": {
      "health": 85,
      "influence": 15,
      "status": "normal"
    },
    "endings_available": ["exile"]
  }
}
```

### Получить опыт Резонанса

```http
POST /api/game-mechanics/resonance/gain
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "amount": 25
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Получено 25 опыта Резонанса",
  "data": {
    "old_level": 2,
    "new_level": 2,
    "experience": 175,
    "next_level_at": 200
  }
}
```

### Выбрать путь

```http
POST /api/game-mechanics/path/choose
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "path": "alliance"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Выбран путь: Альянс",
  "data": {
    "path": "alliance",
    "bonuses": ["Флот", "Ресурсы", "+5000 кредитов"],
    "allies": ["Маркус Рид", "Флот Альянса"]
  }
}
```

### Проверить доступность финала

```http
POST /api/game-mechanics/ending/check
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "ending_type": "treaty"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "ending_type": "treaty",
    "available": true,
    "requirements": {
      "psychic": {"required": 70, "current": 75},
      "empathy": {"required": 80, "current": 65}
    },
    "met": "psychic"
  }
}
```

---

## 🏆 Лидеры

### Получить таблицу лидеров

```http
GET /api/leaderboard
```

**Query Parameters:**
- `limit` (optional): 10 (default), max 100
- `offset` (optional): 0
- `timeframe` (optional): all_time, week, month

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total": 1000,
    "leaderboard": [
      {
        "rank": 1,
        "player_id": "uuid",
        "username": "ProGamer",
        "score": 15000,
        "chapter": 18,
        "ending": "merge"
      },
      ...
    ]
  }
}
```

### Получить свой ранг

```http
GET /api/leaderboard/me
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "rank": 42,
    "score": 8500,
    "percentile": 95
  }
}
```

---

## 🎖️ Достижения

### Получить все достижения

```http
GET /api/achievements
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total": 22,
    "unlocked": 15,
    "achievements": [
      {
        "id": "ach_001",
        "name": "Первые шаги",
        "description": "Начать игру",
        "unlocked": true,
        "unlocked_at": "2026-03-15T10:00:00Z",
        "category": "story"
      },
      ...
    ]
  }
}
```

---

## 📊 Аналитика

### Получить статистику игрока

```http
GET /api/analytics/player
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_playtime": "15h 30m",
    "chapters_completed": 12,
    "choices_made": 250,
    "endings_unlocked": 1,
    "achievements_unlocked": 15,
    "favorite_path": "alliance",
    "relationship_stats": {...}
  }
}
```

### Отправить событие

```http
POST /api/analytics/event
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "event_type": "choice_made",
  "data": {
    "scene_id": "scene_001",
    "choice_id": "choice_1"
  }
}
```

---

## 📦 Данные

### Экспорт данных

```http
GET /api/data/export
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `format`: json (default), zip

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "download_url": "/api/data/download/uuid",
    "expires_at": "2026-03-15T12:00:00Z",
    "size_bytes": 1024
  }
}
```

### Импорт данных

```http
POST /api/data/import
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**FormData:**
- `file`: JSON файл с данными

**Response (200):**
```json
{
  "status": "success",
  "message": "Данные импортированы",
  "data": {
    "imported_records": 150,
    "skipped_records": 0
  }
}
```

### Удалить аккаунт (GDPR)

```http
DELETE /api/data/account
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Аккаунт и все данные удалены"
}
```

---

## 👑 Администрирование

### Получить статистику сервера

```http
GET /api/admin/stats
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_users": 1000,
    "active_users": 250,
    "total_games": 5000,
    "average_score": 7500
  }
}
```

### Отправить уведомление

```http
POST /api/admin/notify
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request:**
```json
{
  "user_id": "uuid",
  "message": "Новое событие!",
  "type": "info"
}
```

---

## ❌ Обработка ошибок

### Стандартный формат ошибок

```json
{
  "status": "error",
  "message": "Описание ошибки",
  "details": {
    "code": "VALIDATION_ERROR",
    "field": "email",
    "reason": "Invalid email format"
  }
}
```

### Коды ошибок HTTP

| Код | Описание |
|-----|----------|
| 200 | Успех |
| 201 | Создано |
| 400 | Неправильный запрос |
| 401 | Неавторизован |
| 403 | Доступ запрещён |
| 404 | Не найдено |
| 409 | Конфликт |
| 422 | Ошибка валидации |
| 429 | Слишком много запросов |
| 500 | Внутренняя ошибка |

---

## 🔗 Дополнительные ресурсы

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
- [OpenAPI Spec](http://localhost:8000/openapi.json)

---

*Последнее обновление: 15 марта 2026*
