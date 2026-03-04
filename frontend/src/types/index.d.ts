/**
 * StarCourier Web - TypeScript Definitions
 * JSDoc типы для JavaScript файлов
 *
 * @typedef {Object} Scene
 * @property {string} id - ID сцены
 * @property {string} title - Название сцены
 * @property {string} text - Текст сцены
 * @property {string} image - Эмодзи сцены
 * @property {string} character - Персонаж сцены
 * @property {Choice[]} choices - Доступные выборы
 */

/**
 * @typedef {Object} Choice
 * @property {string} text - Текст выбора
 * @property {string} next - ID следующей сцены
 * @property {Object.<string, number>} [stats] - Изменения статистики
 * @property {string} [difficulty] - Сложность выбора
 */

/**
 * @typedef {Object} PlayerStats
 * @property {number} health - Здоровье (0-100)
 * @property {number} morale - Мораль (0-100)
 * @property {number} knowledge - Знание (0-100)
 * @property {number} team - Команда (0-100)
 * @property {number} danger - Опасность (0-100)
 * @property {number} security - Безопасность (0-100)
 * @property {number} fuel - Топливо (0-100)
 * @property {number} money - Деньги (0-∞)
 * @property {number} psychic - Психика (0-100)
 * @property {number} trust - Доверие (0-100)
 */

/**
 * @typedef {Object} Character
 * @property {string} id - ID персонажа
 * @property {string} name - Имя персонажа
 * @property {string} role - Роль персонажа
 * @property {string} description - Описание персонажа
 * @property {number} relationship - Уровень отношений (0-100)
 * @property {string} [avatar] - Эмодзи аватар
 * @property {string[]} [traits] - Черты характера
 */

/**
 * @typedef {Object} SaveData
 * @property {string} id - ID сохранения
 * @property {string} name - Название сохранения
 * @property {string} timestamp - Время сохранения (ISO)
 * @property {string} playerId - ID игрока
 * @property {string} currentSceneId - ID текущей сцены
 * @property {number} choicesMade - Количество сделанных выборов
 * @property {PlayerStats} stats - Статистика игрока
 * @property {Object.<string, number>} relationships - Отношения с персонажами
 * @property {string[]} inventory - Инвентарь
 * @property {number} startTime - Время начала игры (timestamp)
 * @property {number} playtime - Время игры в секундах
 * @property {string[]} visitedScenes - Посещённые сцены
 * @property {Object} choiceHistory - История выборов
 * @property {Object} statHistory - История статистики
 */

/**
 * @typedef {Object} GameState
 * @property {boolean} isGameStarted - Игра начата
 * @property {boolean} isLoading - Загрузка
 * @property {string|null} playerId - ID игрока
 * @property {string} currentSceneId - ID текущей сцены
 * @property {number} choicesMade - Сделано выборов
 * @property {Set<string>} visitedScenes - Посещённые сцены
 * @property {string|null} error - Ошибка
 * @property {PlayerStats} stats - Статистика
 * @property {Object.<string, number>} relationships - Отношения
 * @property {string[]} inventory - Инвентарь
 * @property {Scene|null} currentScene - Текущая сцена
 */

/**
 * @typedef {Object} ApiError
 * @property {string} status - Статус ошибки
 * @property {string} message - Сообщение об ошибке
 * @property {string} [code] - Код ошибки
 * @property {Object} [details] - Детали ошибки
 */

/**
 * @typedef {'aggressive'|'diplomatic'|'analytical'|'caring'|'balanced'} DecisionStyle
 */

/**
 * @typedef {Object} DecisionPatterns
 * @property {number} aggressive - Агрессивные выборы
 * @property {number} diplomatic - Дипломатичные выборы
 * @property {number} analytical - Аналитические выборы
 * @property {number} caring - Заботливые выборы
 */

/**
 * @typedef {Object} GameSummary
 * @property {string} playerId - ID игрока
 * @property {string} currentScene - Текущая сцена
 * @property {number} choicesMade - Сделано выборов
 * @property {PlayerStats} stats - Статистика
 * @property {Object.<string, number>} relationships - Отношения
 * @property {string[]} visitedScenes - Посещённые сцены
 * @property {string[]} inventory - Инвентарь
 * @property {number} playtime - Время игры
 * @property {Object} statHistory - История статистики
 * @property {Object} choiceHistory - История выборов
 * @property {Object} sceneTimeTracking - Время в сценах
 * @property {Object} statChangeHistory - История изменений статистики
 * @property {DecisionPatterns} decisionPatterns - Паттерны решений
 */

export default {}
