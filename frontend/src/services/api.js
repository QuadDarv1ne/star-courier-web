/**
 * API Client for StarCourier Web
 * Handles all backend API requests
 * 
 * Uses Axios for HTTP requests
 */

import axios from 'axios'

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ============================================================================
// ENHANCED CACHE WITH LRU EVICTION
// ============================================================================

class LRUCache {
  constructor(maxSize = 100, ttl = 5 * 60 * 1000) {
    this.maxSize = maxSize
    this.ttl = ttl
    this.cache = new Map()
  }

  get(key) {
    const item = this.cache.get(key)
    
    // Check if item exists and is not expired
    if (item && Date.now() - item.timestamp < this.ttl) {
      // Move to end (most recently used)
      this.cache.delete(key)
      this.cache.set(key, item)
      return item.value
    }
    
    // Remove expired item
    if (item) {
      this.cache.delete(key)
    }
    
    return null
  }

  set(key, value) {
    // Remove oldest items if cache is at max size
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    
    // Add new item
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    })
  }

  clear() {
    this.cache.clear()
  }

  size() {
    return this.cache.size
  }
}

const apiCache = new LRUCache(100, 5 * 60 * 1000) // 100 items, 5 minutes TTL

// ============================================================================
// REQUEST INTERCEPTOR
// ============================================================================

apiClient.interceptors.request.use(
  (config) => {
    console.log(`📤 API Request: ${config.method.toUpperCase()} ${config.url}`)
    
    // Check if we should use cache
    if (config.method === 'get' && config.cache !== false) {
      const cacheKey = `${config.method}:${config.url}`
      const cached = apiCache.get(cacheKey)
      
      if (cached) {
        console.log(`📥 API Response (cached): ${config.url}`)
        return Promise.resolve(cached)
      }
    }
    
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// ============================================================================
// RESPONSE INTERCEPTOR
// ============================================================================

apiClient.interceptors.response.use(
  (response) => {
    console.log(`📥 API Response: ${response.status}`, response.data)
    
    // Cache GET responses
    if (response.config.method === 'get' && response.config.cache !== false) {
      const cacheKey = `${response.config.method}:${response.config.url}`
      apiCache.set(cacheKey, response)
    }
    
    return response
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error(`❌ Response Error (${error.response.status}):`, error.response.data)
      
      const message = error.response.data?.error || error.response.data?.detail || 'Ошибка сервера'
      throw new Error(message)
    } else if (error.request) {
      // Request made but no response
      console.error('❌ Network Error: No response from server')
      throw new Error('Ошибка подключения к серверу. Убедитесь, что backend запущен.')
    } else {
      // Error in request setup
      console.error('❌ Error:', error.message)
      throw new Error(error.message)
    }
  }
)

// ============================================================================
// RETRY MECHANISM
// ============================================================================

/**
 * Retry a function with exponential backoff
 * @param {Function} fn - Function to retry
 * @param {number} retries - Number of retries
 * @param {number} delay - Initial delay in ms
 */
async function retryWithBackoff(fn, retries = 3, delay = 1000) {
  try {
    return await fn()
  } catch (error) {
    if (retries === 0) {
      throw error
    }
    
    // Wait for delay
    await new Promise(resolve => setTimeout(resolve, delay))
    
    // Retry with exponential backoff
    return retryWithBackoff(fn, retries - 1, delay * 2)
  }
}

// ============================================================================
// INPUT VALIDATION
// ============================================================================

/**
 * Validate player ID
 * @param {string} playerId - Player ID to validate
 */
function validatePlayerId(playerId) {
  if (!playerId || typeof playerId !== 'string' || playerId.length < 5) {
    throw new Error('Неверный ID игрока')
  }
}

/**
 * Validate scene ID
 * @param {string} sceneId - Scene ID to validate
 */
function validateSceneId(sceneId) {
  if (!sceneId || typeof sceneId !== 'string' || sceneId.length < 1) {
    throw new Error('Неверный ID сцены')
  }
}

/**
 * Validate stats object
 * @param {Object} stats - Stats object to validate
 */
function validateStats(stats) {
  if (!stats || typeof stats !== 'object') {
    throw new Error('Неверный объект статистики')
  }
  
  // Validate each stat value
  for (const [key, value] of Object.entries(stats)) {
    if (typeof value !== 'number' || isNaN(value)) {
      throw new Error(`Неверное значение статистики для ${key}: ${value}`)
    }
    
    // Ensure values are within reasonable bounds
    if (value < -1000 || value > 1000) {
      throw new Error(`Значение статистики ${key} вне допустимого диапазона: ${value}`)
    }
  }
}

// ============================================================================
// GAME API ENDPOINTS
// ============================================================================

export const gameApi = {
  /**
   * Start a new game
   */
  async startGame(playerId) {
    try {
      validatePlayerId(playerId)
      
      // Clear cache when starting new game
      apiCache.clear()
      
      const response = await retryWithBackoff(() => 
        apiClient.post('/game/start', {
          player_id: playerId
        })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to start game:', error)
      throw new Error(`Не удалось начать игру: ${error.message}`)
    }
  },

  /**
   * Make a choice in game
   */
  async makeChoice(playerId, nextScene, stats = {}) {
    try {
      validatePlayerId(playerId)
      validateSceneId(nextScene)
      validateStats(stats)
      
      // Clear cache when making choices (game state changes)
      apiCache.clear()
      
      const response = await retryWithBackoff(() => 
        apiClient.post('/game/choose', {
          player_id: playerId,
          next_scene: nextScene,
          stats
        })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to make choice:', error)
      throw new Error(`Не удалось выполнить выбор: ${error.message}`)
    }
  },

  /**
   * Get scene details (cached)
   */
  async getScene(sceneId) {
    try {
      validateSceneId(sceneId)
      
      const response = await retryWithBackoff(() => 
        apiClient.get(`/game/scene/${sceneId}`, { cache: true })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get scene:', error)
      throw new Error(`Не удалось загрузить сцену: ${error.message}`)
    }
  },

  /**
   * Get player stats
   */
  async getPlayerStats(playerId) {
    try {
      validatePlayerId(playerId)
      
      const response = await retryWithBackoff(() => 
        apiClient.get(`/game/stats/${playerId}`)
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get player stats:', error)
      throw new Error(`Не удалось получить статистику игрока: ${error.message}`)
    }
  }
}

// ============================================================================
// CHARACTER API ENDPOINTS
// ============================================================================

export const characterApi = {
  /**
   * Get all characters (cached)
   */
  async getAllCharacters() {
    try {
      const response = await retryWithBackoff(() => 
        apiClient.get('/characters', { cache: true })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get characters:', error)
      throw new Error(`Не удалось загрузить персонажей: ${error.message}`)
    }
  },

  /**
   * Get specific character (cached)
   */
  async getCharacter(characterId) {
    try {
      if (!characterId || typeof characterId !== 'string') {
        throw new Error('Неверный ID персонажа')
      }
      
      const response = await retryWithBackoff(() => 
        apiClient.get(`/characters/${characterId}`, { cache: true })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get character:', error)
      throw new Error(`Не удалось загрузить персонажа: ${error.message}`)
    }
  },

  /**
   * Get multiple characters in a single request (batch)
   */
  async getCharactersBatch(characterIds) {
    try {
      if (!Array.isArray(characterIds) || characterIds.length === 0) {
        throw new Error('Неверный список ID персонажей')
      }
      
      // Validate each character ID
      characterIds.forEach(id => {
        if (!id || typeof id !== 'string') {
          throw new Error('Неверный ID персонажа в списке')
        }
      })
      
      const response = await retryWithBackoff(() => 
        apiClient.get(`/characters/batch?character_ids=${characterIds.join(',')}`)
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get characters batch:', error)
      throw new Error(`Не удалось загрузить персонажей: ${error.message}`)
    }
  }
}

// ============================================================================
// SCENE API ENDPOINTS
// ============================================================================

export const sceneApi = {
  /**
   * Get all scenes (cached)
   */
  async getAllScenes() {
    try {
      const response = await retryWithBackoff(() => 
        apiClient.get('/scenes', { cache: true })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get scenes:', error)
      throw new Error(`Не удалось загрузить сцены: ${error.message}`)
    }
  },

  /**
   * Get specific scene (cached)
   */
  async getScene(sceneId) {
    try {
      validateSceneId(sceneId)
      
      const response = await retryWithBackoff(() => 
        apiClient.get(`/scenes/${sceneId}`, { cache: true })
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get scene:', error)
      throw new Error(`Не удалось загрузить сцену: ${error.message}`)
    }
  },

  /**
   * Get multiple scenes in a single request (batch)
   */
  async getScenesBatch(sceneIds) {
    try {
      if (!Array.isArray(sceneIds) || sceneIds.length === 0) {
        throw new Error('Неверный список ID сцен')
      }
      
      // Validate each scene ID
      sceneIds.forEach(id => {
        if (!id || typeof id !== 'string') {
          throw new Error('Неверный ID сцены в списке')
        }
      })
      
      const response = await retryWithBackoff(() => 
        apiClient.get(`/scenes/batch?scene_ids=${sceneIds.join(',')}`)
      )
      
      return response
    } catch (error) {
      console.error('❌ Failed to get scenes batch:', error)
      throw new Error(`Не удалось загрузить сцены: ${error.message}`)
    }
  }
}

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthApi = {
  /**
   * Check server health
   */
  async checkHealth() {
    try {
      const response = await retryWithBackoff(() => 
        apiClient.get('/health')
      )
      
      return response.data
    } catch (error) {
      console.error('❌ Server health check failed:', error)
      throw new Error(`Проверка состояния сервера не удалась: ${error.message}`)
    }
  },

  /**
   * Wait for server to be available
   */
  async waitForServer(maxAttempts = 5, delay = 1000) {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        await this.checkHealth()
        console.log('✅ Server is available')
        return true
      } catch (error) {
        console.log(`⏳ Waiting for server... (${i + 1}/${maxAttempts})`)
        if (i < maxAttempts - 1) {
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }
    throw new Error('Сервер не ответил. Пожалуйста, убедитесь, что backend запущен на http://localhost:8000')
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Set API base URL dynamically
 */
export function setApiBaseUrl(url) {
  apiClient.defaults.baseURL = url
  console.log(`📍 API Base URL изменен на: ${url}`)
}

/**
 * Get current API base URL
 */
export function getApiBaseUrl() {
  return apiClient.defaults.baseURL
}

/**
 * Check if API is available
 */
export async function isApiAvailable() {
  try {
    await healthApi.checkHealth()
    return true
  } catch {
    return false
  }
}

/**
 * Format error message
 */
export function formatErrorMessage(error) {
  if (typeof error === 'string') {
    return error
  }
  
  if (error.response?.data?.error) {
    return error.response.data.error
  }
  
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  
  if (error.message) {
    return error.message
  }
  
  return 'Неизвестная ошибка'
}

/**
 * Get detailed error information
 */
export function getErrorDetails(error) {
  const details = {
    message: formatErrorMessage(error),
    status: error.response?.status || null,
    statusText: error.response?.statusText || null,
    url: error.config?.url || null,
    method: error.config?.method || null,
    timestamp: new Date().toISOString()
  }
  
  // Add network error information
  if (error.code) {
    details.code = error.code
  }
  
  if (error.isAxiosError) {
    details.isNetworkError = error.isAxiosError
  }
  
  return details
}

/**
 * Create user-friendly error message
 */
export function createUserFriendlyError(error, context = '') {
  const details = getErrorDetails(error)
  
  // Handle specific error cases
  if (details.status === 404) {
    return `Ресурс не найден${context ? ` (${context})` : ''}. Пожалуйста, проверьте подключение к серверу.`
  }
  
  if (details.status === 500) {
    return `Внутренняя ошибка сервера${context ? ` (${context})` : ''}. Пожалуйста, попробуйте позже.`
  }
  
  if (details.status === 429) {
    return `Слишком много запросов${context ? ` (${context})` : ''}. Пожалуйста, подождите немного.`
  }
  
  if (details.isNetworkError) {
    return `Ошибка подключения к серверу${context ? ` (${context})` : ''}. Пожалуйста, проверьте ваше интернет-соединение.`
  }
  
  // Default message
  return `${details.message}${context ? ` (${context})` : ''}`
}

/**
 * Clear API cache
 */
export function clearApiCache() {
  apiCache.clear()
  console.log('✅ API cache cleared')
}

/**
 * Get cache size
 */
export function getCacheSize() {
  return apiCache.size()
}

// Add a more robust error handler for API calls
export async function handleApiCall(apiCall, context = '') {
  try {
    const response = await apiCall()
    return response.data
  } catch (error) {
    const userFriendlyError = createUserFriendlyError(error, context)
    console.error('API Error:', getErrorDetails(error))
    throw new Error(userFriendlyError)
  }
}

// ============================================================================
// EXPORT EVERYTHING
// ============================================================================

export default apiClient