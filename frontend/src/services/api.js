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
// REQUEST INTERCEPTOR
// ============================================================================

apiClient.interceptors.request.use(
  (config) => {
    console.log(`📤 API Request: ${config.method.toUpperCase()} ${config.url}`)
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
// GAME API ENDPOINTS
// ============================================================================

export const gameApi = {
  /**
   * Start a new game
   */
  startGame(playerId) {
    return apiClient.post('/game/start', {
      player_id: playerId
    })
  },

  /**
   * Make a choice in game
   */
  makeChoice(playerId, nextScene, stats = {}) {
    return apiClient.post('/game/choose', {
      player_id: playerId,
      next_scene: nextScene,
      stats
    })
  },

  /**
   * Get scene details
   */
  getScene(sceneId) {
    return apiClient.get(`/game/scene/${sceneId}`)
  },

  /**
   * Get player stats
   */
  getPlayerStats(playerId) {
    return apiClient.get(`/game/stats/${playerId}`)
  }
}

// ============================================================================
// CHARACTER API ENDPOINTS
// ============================================================================

export const characterApi = {
  /**
   * Get all characters
   */
  getAllCharacters() {
    return apiClient.get('/characters')
  },

  /**
   * Get specific character
   */
  getCharacter(characterId) {
    return apiClient.get(`/characters/${characterId}`)
  }
}

// ============================================================================
// SCENE API ENDPOINTS
// ============================================================================

export const sceneApi = {
  /**
   * Get all scenes
   */
  getAllScenes() {
    return apiClient.get('/scenes')
  },

  /**
   * Get specific scene
   */
  getScene(sceneId) {
    return apiClient.get(`/scenes/${sceneId}`)
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
      const response = await apiClient.get('/health')
      return response.data
    } catch (error) {
      console.error('❌ Server health check failed:', error)
      throw error
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
    throw new Error('Server не ответил. Пожалуйста, убедитесь, что backend запущен на http://localhost:8000')
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

// ============================================================================
// EXPORT EVERYTHING
// ============================================================================

export default apiClient