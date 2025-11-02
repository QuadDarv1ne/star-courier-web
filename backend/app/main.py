"""
StarCourier Web - FastAPI Backend
Главная точка входа приложения с интеграцией config.py

Автор: QuadDarv1ne
Версия: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Импорт конфигурации
from config import settings

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

# Настройка логирования
logging.basicConfig(
    level=settings.get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC МОДЕЛИ
# ============================================================================

class StatUpdate(BaseModel):
    """Модель обновления статистики"""
    health: Optional[int] = 0
    morale: Optional[int] = 0
    knowledge: Optional[int] = 0
    team: Optional[int] = 0
    danger: Optional[int] = 0
    security: Optional[int] = 0
    fuel: Optional[int] = 0
    money: Optional[int] = 0
    psychic: Optional[int] = 0
    trust: Optional[int] = 0


class Choice(BaseModel):
    """Модель выбора"""
    text: str = Field(..., description="Текст выбора")
    next: str = Field(..., description="ID следующей сцены")
    stats: Optional[Dict[str, int]] = Field(None, description="Изменение статистики")
    difficulty: Optional[str] = Field(None, description="Сложность выбора")


class SceneResponse(BaseModel):
    """Модель ответа со сценой"""
    id: str = Field(..., description="ID сцены")
    title: str = Field(..., description="Название сцены")
    text: str = Field(..., description="Текст сцены")
    image: str = Field(..., description="Эмодзи сцены")
    character: str = Field(..., description="Персонаж, говорящий в сцене")
    choices: List[Choice] = Field(..., description="Доступные выборы")


class GameStartRequest(BaseModel):
    """Модель запроса начала игры"""
    player_id: str = Field(..., description="Уникальный ID игрока")


class GameStartResponse(BaseModel):
    """Модель ответа начала игры"""
    status: str = "success"
    scene: SceneResponse
    stats: Dict[str, int]
    relationships: Dict[str, int]


class GameChoiceRequest(BaseModel):
    """Модель запроса выбора"""
    player_id: str = Field(..., description="ID игрока")
    next_scene: str = Field(..., description="ID следующей сцены")
    stats: Optional[Dict[str, int]] = Field(None, description="Изменение статистики")


class GameChoiceResponse(BaseModel):
    """Модель ответа на выбор"""
    status: str
    scene: Optional[SceneResponse] = None
    stats: Optional[Dict[str, int]] = None
    relationships: Optional[Dict[str, int]] = None
    choices_made: int = 0
    reason: Optional[str] = None


class PlayerStatsResponse(BaseModel):
    """Модель ответа с статистикой игрока"""
    current_scene: str
    stats: Dict[str, int]
    relationships: Dict[str, int]
    inventory: List[str]
    choices_made: int


class CharacterInfo(BaseModel):
    """Информация о персонаже"""
    id: str
    name: str
    role: str
    relationship: int
    description: str


class HealthCheckResponse(BaseModel):
    """Модель health check"""
    status: str
    version: str
    environment: str
    timestamp: str


# ============================================================================
# ДАННЫЕ ИГ
# ============================================================================

# Сцены игры
SCENES: Dict[str, dict] = {
    "start": {
        "title": "Пробуждение на Элее",
        "text": "Вы — капитан Макс Велл. Просыпаетесь в каюте звездолёта 'Элея'. На консоли мигает красная лампочка. Это сообщение от таинственного контактера на станции Сигма. Он говорит о древнем артефакте, способном изменить судьбу человечества.\n\nВаша команда уже ждёт приказов в центре управления.",
        "image": "🚀",
        "character": "Сара Нова",
        "choices": [
            {"text": "Спешить в центр управления", "next": "command_center", "stats": {"health": -5, "morale": 10}},
            {"text": "Включить связь и узнать больше", "next": "mystery_contact", "stats": {"knowledge": 15, "morale": -5}},
            {"text": "Проверить состояние артефакта в хранилище", "next": "artifact_vault", "stats": {"knowledge": 20}}
        ]
    },
    "command_center": {
        "title": "Центр управления Элеи",
        "text": "В центре управления вас встречают:\n\n• САРА НОВА — главный научный офицер (холодная, расчётливая)\n• ГРИША РОМАНОВ — боевой офицер (верный, опытный)\n• ЛИ ЧЖЭНЬ — навигатор (загадочная, с тайнами)\n\nСара докладывает: 'Артефакт находится в безопасности, но станция Сигма отправляет срочный сигнал. Что вы приказываете?'",
        "image": "🎮",
        "character": "Сара Нова",
        "choices": [
            {"text": "Отправиться на станцию Сигма", "next": "sigma_station", "stats": {"fuel": -30, "morale": 20}},
            {"text": "Усилить охрану артефакта", "next": "artifact_guard", "stats": {"security": 25, "morale": 5}},
            {"text": "Созвать совет экипажа", "next": "crew_meeting", "stats": {"team": 15}}
        ]
    },
    "mystery_contact": {
        "title": "Голос в эфире",
        "text": "Вы включаете приватный канал. Голос, скрытый фильтром:\n\n'Капитан Велл, времени мало. Артефакт, который вы везёте — это ключ к портам между мирами. Они хотят его украсть. Доверяйте только себе... и может быть, Ли Чжэнь.'\n\nСвязь прерывается. На экране координаты неизвестной системы.",
        "image": "📡",
        "character": "Неизвестный",
        "choices": [
            {"text": "Рассказать о звонке Саре и Грише", "next": "team_divided", "stats": {"trust": -20, "morale": -10}},
            {"text": "Поговорить наедине с Ли Чжэнь", "next": "li_zheng_secret", "stats": {"knowledge": 25, "morale": 15}},
            {"text": "Молча отправиться по координатам", "next": "secret_mission", "stats": {"danger": 30}}
        ]
    },
    "artifact_vault": {
        "title": "Хранилище артефакта",
        "text": "Подземное хранилище Элеи. Артефакт светится голубым светом в магнитном поле.\n\nЭто кристаллическая структура, невозможно определить её происхождение. На поверхности кристалла — странные символы, которые светятся в такт вашему пульсу.\n\nНеожиданно вы слышите шум. Кто-то пробирается в хранилище!",
        "image": "💎",
        "character": "Артефакт",
        "choices": [
            {"text": "Активировать боевую блокировку", "next": "lockdown_intruder", "stats": {"security": 30, "danger": 20}},
            {"text": "Коснуться артефакта и ощутить его силу", "next": "artifact_touch", "stats": {"knowledge": 40, "psychic": 20}},
            {"text": "Вызвать охрану и подняться в центр управления", "next": "command_center", "stats": {"team": 10}}
        ]
    },
    "sigma_station": {
        "title": "Станция Сигма-7",
        "text": "Станция в полусогнутом состоянии. На портале висят рваные провода и обломки панелей. Немного персонала остаётся.\n\nВас встречает КОМАНДИР КЕЙН — человек с шрамом на лице:\n\n'Велл, спасибо что приехали. У нас проблема. Пираты из клана 'Чёрный Ворон' хотят артефакт. Они прибывают через 6 часов. Нам нужна помощь.'",
        "image": "🛸",
        "character": "Командир Кейн",
        "choices": [
            {"text": "Защитить станцию всеми силами", "next": "defend_station", "stats": {"team": 20, "danger": 40}},
            {"text": "Заключить сделку с пиратами", "next": "pirate_deal", "stats": {"money": 50, "morale": -30, "trust": -25}},
            {"text": "Эвакуировать и уйти", "next": "evacuate", "stats": {"morale": -20, "fuel": -40}}
        ]
    },
    "li_zheng_secret": {
        "title": "Тайна Ли Чжэнь",
        "text": "Вы находите Ли в её каюте, покрытой древними картами и символами, похожими на те, что на артефакте.\n\nЛи оборачивается: 'Я знала, что вы позвоните, Макс. Мне нужно рассказать вам истину. Я не просто навигатор. Я — последняя хранительница древнего ордена. Артефакт — это часть чего-то гораздо большего.'",
        "image": "🧭",
        "character": "Ли Чжэнь",
        "choices": [
            {"text": "Полностью доверить ей", "next": "li_alliance", "stats": {"trust": 40, "knowledge": 30, "morale": 20}},
            {"text": "Требовать полную правду", "next": "li_confrontation", "stats": {"knowledge": 25, "trust": -15}},
            {"text": "Уйти и доложить команде", "next": "team_divided", "stats": {"trust": -30}}
        ]
    },
    "li_alliance": {
        "title": "Союз навигатора",
        "text": "Ли показывает вам древние записи. Артефакт — это ключ к галактике Древних, могущественной цивилизации, исчезнувшей 10000 лет назад.\n\n'Макс, они вернутся. И когда это произойдёт, будут две стороны — те, кто хочет спасти человечество, и те, кто хочет завоевать. Выбор за вами.'",
        "image": "✨",
        "character": "Ли Чжэнь",
        "choices": [
            {"text": "Начать подготовку к возвращению Древних", "next": "ancient_awakening", "stats": {"knowledge": 50, "danger": 50}},
            {"text": "Скрыть артефакт в безопасном месте", "next": "hide_artifact", "stats": {"morale": -10, "security": 40}},
            {"text": "Уничтожить артефакт", "next": "artifact_destruction", "stats": {"morale": -40, "knowledge": -30}}
        ]
    },
    "ancient_awakening": {
        "title": "🌠 КОНЕЦ: Пробуждение Древних",
        "text": "Вы активируете артефакт. Голубой свет наполняет космос.\n\nЗвездолёт Элея трансформируется. Стены светятся символами, включаются древние технологии. Ваша команда смотрит в восхищении.\n\nЛи произносит древние слова, и в небе появляется огромная структура — мегаструктура Древних, пробуждающаяся после тысячелетий.\n\nВы — не просто капитан. Вы — тот, кто привёл человечество в новую эру.",
        "image": "👑",
        "character": "Судьба",
        "choices": [
            {"text": "Начать заново", "next": "start"}
        ]
    },
    "hide_artifact": {
        "title": "🔒 КОНЕЦ: Хранитель секретов",
        "text": "Вы находите древнюю планету, жизни на ней нет. Вы оставляете артефакт в подземелье, защищённый кодами, которые знает только Ли.\n\nСера, Гриша и остальная команда верят вам. Артефакт в безопасности.\n\nВы — хранитель величайшей тайны Вселенной.",
        "image": "🗝️",
        "character": "Секрет",
        "choices": [
            {"text": "Начать заново", "next": "start"}
        ]
    },
    "artifact_destruction": {
        "title": "💥 КОНЕЦ: Жертва",
        "text": "Артефакт разрушается в ослепительной вспышке.\n\nВселенная содрогается. Древние не пробуждаются.\n\nНо Ли падает на колени: 'Вы уничтожили бессмертие человечества...'\n\nВы спасили мир от неизвестного, но потеряли бесценный артефакт.",
        "image": "⚡",
        "character": "Жертва",
        "choices": [
            {"text": "Начать заново", "next": "start"}
        ]
    },
    "defend_station": {
        "title": "⚔️ КОНЕЦ: Боевая победа",
        "text": "Ваша стратегия работает идеально. Пираты отступают в панике.\n\nГриша пожимает вам руку: 'Блестящая тактика, капитан. Мы победили.'\n\nКомандир Кейн: 'Вы спасили станцию и артефакт. Человечество вам благодарно.'",
        "image": "🏆",
        "character": "Герой",
        "choices": [
            {"text": "Начать заново", "next": "start"}
        ]
    }
}

# Персонажи
CHARACTERS: Dict[str, dict] = {
    "sara_nova": {
        "name": "Сара Нова",
        "role": "Главный научный офицер",
        "relationship": 50,
        "description": "Холодная, расчётливая, но с добрым сердцем"
    },
    "grisha_romanov": {
        "name": "Гриша Романов",
        "role": "Боевой офицер",
        "relationship": 60,
        "description": "Верный боец, опытный воин"
    },
    "li_zheng": {
        "name": "Ли Чжэнь",
        "role": "Навигатор",
        "relationship": 45,
        "description": "Загадочная, хранительница древних тайн"
    }
}

# Сохранение прогресса игроков в памяти
game_progress: Dict[str, dict] = {}

# ============================================================================
# LIFESPAN - ИНИЦИАЛИЗАЦИЯ И ЗАВЕРШЕНИЕ
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация
    logger.info("=" * 80)
    logger.info(f"🚀 {settings.app_name} Backend запущен")
    logger.info("=" * 80)
    logger.info(f"🌍 Окружение: {settings.environment}")
    logger.info(f"🐛 Debug: {settings.debug}")
    logger.info(f"📊 Загружено сцен: {len(SCENES)}")
    logger.info(f"👥 Загружено персонажей: {len(CHARACTERS)}")
    logger.info(f"💾 База данных: {settings.database_type}")
    logger.info(f"⚡ Кэш: {settings.cache_type} (включен: {settings.cache_enabled})")
    logger.info(f"🔐 Auth: {settings.auth_enabled}")
    logger.info(f"📡 CORS origins: {len(settings.cors_origins_list)} источников")
    logger.info(f"📚 API документация: {settings.docs_url if settings.docs_enabled else 'отключена'}")
    logger.info("=" * 80)
    
    yield
    
    # Завершение
    logger.info("🛑 Завершение работы приложения...")
    logger.info(f"📊 Активных сессий: {len(game_progress)}")


# ============================================================================
# СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description="Интерактивная текстовая RPG в космической тематике",
    version=settings.app_version,
    docs_url=settings.docs_url if settings.docs_enabled else None,
    redoc_url=settings.redoc_url if settings.redoc_enabled else None,
    openapi_url=settings.openapi_url if settings.docs_enabled else None,
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE - CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"✅ CORS настроен для {len(settings.cors_origins_list)} источников")

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработчик HTTP исключений"""
    logger.error(f"❌ HTTP Exception ({exc.status_code}): {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработчик общих исключений"""
    logger.error(f"❌ Необработанное исключение: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# ============================================================================
# ENDPOINTS
# ============================================================================

# -------- Health Check --------


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Проверка здоровья приложения и состояния сервера
    """
    logger.debug("Health check запрос получен")
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now().isoformat()
    }

# -------- Game Endpoints --------


@app.post("/api/game/start", response_model=GameStartResponse, tags=["Game"])
async def start_game(request: GameStartRequest):
    """
    Начать новую игру
    
    Инициализирует игровую сессию для игрока с начальными параметрами
    """
    try:
        player_id = request.player_id
        
        logger.info(f"🎮 Попытка начать игру для игрока: {player_id}")
        
        # Проверка существования игроков
        if len(game_progress) >= settings.max_active_games:
            logger.warning(f"⚠️ Максимум активных игр достигнут: {settings.max_active_games}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Максимум активных игр достигнут"
            )
        
        # Инициализация прогресса игрока
        game_progress[player_id] = {
            'current_scene': 'start',
            'stats': {
                'health': 100,
                'morale': 75,
                'knowledge': 30,
                'team': 50,
                'danger': 0,
                'security': 20,
                'fuel': 100,
                'money': 1000,
                'psychic': 0,
                'trust': 50
            },
            'relationships': {char: CHARACTERS[char]['relationship'] for char in CHARACTERS},
            'inventory': ['Брекер кодов', 'Боевой нож'],
            'choices_made': 0,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Игра начата для игрока: {player_id}")
        logger.debug(f"📊 Активных сессий: {len(game_progress)}/{settings.max_active_games}")
        
        return {
            "status": "success",
            "scene": get_scene_data('start'),
            "stats": game_progress[player_id]['stats'],
            "relationships": game_progress[player_id]['relationships']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при начале игры: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при начале игры"
        )


@app.get("/api/game/scene/{scene_id}", response_model=SceneResponse, tags=["Game"])
async def get_scene(scene_id: str):
    """
    Получить информацию о сцене
    
    Возвращает детали конкретной сцены по ID
    """
    logger.debug(f"Запрос сцены: {scene_id}")
    
    if scene_id not in SCENES:
        logger.warning(f"⚠️ Сцена не найдена: {scene_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сцена '{scene_id}' не найдена"
        )
    
    return get_scene_data(scene_id)


@app.post("/api/game/choose", response_model=GameChoiceResponse, tags=["Game"])
async def make_choice(request: GameChoiceRequest):
    """
    Сделать выбор в игре
    
    Обрабатывает выбор игрока и переходит на следующую сцену
    """
    try:
        player_id = request.player_id
        next_scene = request.next_scene
        stats_changes = request.stats or {}
        
        logger.debug(f"Выбор от игрока {player_id}: переход на сцену {next_scene}")
        
        # Проверка что игра началась
        if player_id not in game_progress:
            logger.warning(f"⚠️ Игра не началась для игрока: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Игра не начата"
            )
        
        # Обновление статистики
        for key, value in stats_changes.items():
            if key in game_progress[player_id]['stats']:
                old_value = game_progress[player_id]['stats'][key]
                game_progress[player_id]['stats'][key] = max(0, min(100, old_value + value))
                logger.debug(f"  {key}: {old_value} → {game_progress[player_id]['stats'][key]}")
        
        # Обновление текущей сцены
        game_progress[player_id]['current_scene'] = next_scene
        game_progress[player_id]['choices_made'] += 1
        
        logger.info(f"✅ Игрок {player_id}: выбор #{game_progress[player_id]['choices_made']} → {next_scene}")
        
        # Проверка условий поражения
        stats = game_progress[player_id]['stats']
        if stats['morale'] <= 0 or stats['health'] <= 0:
            logger.warning(f"❌ Игрок {player_id} проиграл (morale: {stats['morale']}, health: {stats['health']})")
            return {
                "status": "game_over",
                "reason": "Вы не выжили в космосе",
                "choices_made": game_progress[player_id]['choices_made']
            }
        
        return {
            "status": "success",
            "scene": get_scene_data(next_scene),
            "stats": game_progress[player_id]['stats'],
            "relationships": game_progress[player_id]['relationships'],
            "choices_made": game_progress[player_id]['choices_made']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при выборе: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке выбора"
        )


@app.get("/api/game/stats/{player_id}", response_model=PlayerStatsResponse, tags=["Game"])
async def get_player_stats(player_id: str):
    """
    Получить статистику игрока
    
    Возвращает полную информацию о прогрессе игрока
    """
    logger.debug(f"Запрос статистики для игрока: {player_id}")
    
    if player_id not in game_progress:
        logger.warning(f"⚠️ Игрок не найден: {player_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Игрок не найден"
        )
    
    progress = game_progress[player_id]
    return {
        "current_scene": progress['current_scene'],
        "stats": progress['stats'],
        "relationships": progress['relationships'],
        "inventory": progress['inventory'],
        "choices_made": progress['choices_made']
    }

# -------- Character Endpoints --------


@app.get("/api/characters", tags=["Characters"])
async def get_all_characters():
    """
    Получить всех персонажей
    
    Возвращает информацию о всех персонажах игры
    """
    logger.debug(f"Запрос списка персонажей: {len(CHARACTERS)} персонажей")
    
    return {char_id: {**char_data, "id": char_id} 
            for char_id, char_data in CHARACTERS.items()}


@app.get("/api/characters/{character_id}", response_model=CharacterInfo, tags=["Characters"])
async def get_character(character_id: str):
    """
    Получить информацию о персонаже
    
    Возвращает детали конкретного персонажа по ID
    """
    logger.debug(f"Запрос персонажа: {character_id}")
    
    if character_id not in CHARACTERS:
        logger.warning(f"⚠️ Персонаж не найден: {character_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Персонаж '{character_id}' не найден"
        )
    
    char = CHARACTERS[character_id]
    return {
        "id": character_id,
        "name": char['name'],
        "role": char['role'],
        "relationship": char['relationship'],
        "description": char['description']
    }

# -------- Scene Endpoints --------


@app.get("/api/scenes", tags=["Scenes"])
async def list_scenes():
    """
    Получить список всех сцен
    
    Возвращает информацию о всех доступных сценах (для отладки)
    """
    logger.debug(f"Запрос списка всех сцен: {len(SCENES)} сцен")
    
    return {scene_id: scene['title'] for scene_id, scene in SCENES.items()}


# -------- Admin Endpoints --------

@app.get("/api/admin/stats", tags=["Admin"])
async def admin_stats():
    """
    Получить статистику сервера (только для отладки)
    
    Возвращает информацию об активных сессиях и конфигурации
    """
    logger.debug("Admin stats запрос")
    
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin endpoints доступны только в debug режиме"
        )
    
    return {
        "active_sessions": len(game_progress),
        "max_sessions": settings.max_active_games,
        "environment": settings.environment,
        "debug": settings.debug,
        "cache_enabled": settings.cache_enabled,
        "auth_enabled": settings.auth_enabled,
        "total_scenes": len(SCENES),
        "total_characters": len(CHARACTERS),
        "uptime_info": "см. в логах"
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["Root"])
async def root():
    """Главная страница API"""
    logger.debug("Root endpoint запрос")
    
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Интерактивная текстовая RPG в космической тематике",
        "environment": settings.environment,
        "docs": settings.docs_url if settings.docs_enabled else None,
        "redoc": settings.redoc_url if settings.redoc_enabled else None,
        "health": "/health",
        "api": {
            "game": "/api/game/start",
            "characters": "/api/characters",
            "scenes": "/api/scenes"
        }
    }

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def get_scene_data(scene_id: str) -> SceneResponse:
    """
    Получить данные сцены в формате SceneResponse
    
    Args:
        scene_id: ID сцены
        
    Returns:
        SceneResponse: Данные сцены
    """
    scene = SCENES.get(scene_id, SCENES['start'])
    return SceneResponse(
        id=scene_id,
        title=scene['title'],
        text=scene['text'],
        image=scene['image'],
        character=scene.get('character', 'Неизвестный'),
        choices=[Choice(**choice) for choice in scene['choices']]
    )

# ============================================================================
# ЗАПУСК
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("🚀 Запуск StarCourier Web Backend")
    logger.info("=" * 80)
    logger.info(f"📍 Адрес: http://{settings.server_host}:{settings.server_port}")
    logger.info(f"📚 API Docs: http://{settings.server_host}:{settings.server_port}{settings.docs_url}")
    logger.info(f"🌍 Environment: {settings.environment}")
    logger.info(f"🐛 Debug: {settings.debug}")
    logger.info("=" * 80)
    
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )