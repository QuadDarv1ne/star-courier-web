/**
 * Auth Store for StarCourier Web
 * Управление аутентификацией и авторизацией пользователей
 * 
 * Использует JWT токены для аутентификации
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Ключи для localStorage
const TOKEN_KEY = 'starcourier_access_token'
const REFRESH_TOKEN_KEY = 'starcourier_refresh_token'
const USER_KEY = 'starcourier_user'

// API Base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useAuthStore = defineStore('auth', () => {
  // ============================================================================
  // STATE
  // ============================================================================

  const accessToken = ref(localStorage.getItem(TOKEN_KEY) || null)
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || null)
  const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))
  const isLoading = ref(false)
  const error = ref(null)
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  // ============================================================================
  // HELPERS
  // ============================================================================

  /**
   * Сохранить токены в localStorage
   */
  function saveTokens(tokens) {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    
    localStorage.setItem(TOKEN_KEY, tokens.access_token)
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
  }

  /**
   * Сохранить пользователя в localStorage
   */
  function saveUser(userData) {
    user.value = userData
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
  }

  /**
   * Очистить все данные аутентификации
   */
  function clearAuth() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    error.value = null
    
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  /**
   * Получить заголовки авторизации
   */
  function getAuthHeaders() {
    if (!accessToken.value) return {}
    return {
      'Authorization': `Bearer ${accessToken.value}`
    }
  }

  /**
   * Выполнить API запрос с авторизацией
   */
  async function authFetch(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`
    
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options.headers
    }

    const response = await fetch(url, {
      ...options,
      headers
    })

    // Если токен истёк, пытаемся обновить
    if (response.status === 401 && refreshToken.value) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // Повторяем запрос с новым токеном
        const newHeaders = {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
          ...options.headers
        }
        return fetch(url, {
          ...options,
          headers: newHeaders
        })
      } else {
        // Не удалось обновить - разлогиниваем
        clearAuth()
        throw new Error('Сессия истекла. Пожалуйста, войдите снова.')
      }
    }

    return response
  }

  // ============================================================================
  // ACTIONS
  // ============================================================================

  /**
   * Регистрация нового пользователя
   */
  async function register(userData) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка при регистрации')
      }

      // После успешной регистрации автоматически входим
      await login({
        username: userData.username,
        password: userData.password
      })

      return { success: true, user: data }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Вход в систему
   */
  async function login(credentials) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка при входе')
      }

      // Сохраняем токены
      saveTokens(data)

      // Получаем информацию о пользователе
      await fetchUserProfile()

      console.log('✅ Пользователь вошёл:', user.value?.username)
      return { success: true, tokens: data }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Выход из системы
   */
  async function logout() {
    try {
      // Вызываем API для выхода (если нужно)
      await authFetch('/api/auth/logout', { method: 'POST' })
    } catch (err) {
      console.warn('Logout API call failed:', err)
    } finally {
      clearAuth()
      console.log('👋 Пользователь вышел')
    }
  }

  /**
   * Обновить access токен
   */
  async function refreshAccessToken() {
    if (!refreshToken.value) return false

    try {
      const response = await fetch(`${API_URL}/api/auth/refresh?refresh_token=${refreshToken.value}`, {
        method: 'POST'
      })

      if (!response.ok) {
        return false
      }

      const data = await response.json()
      saveTokens(data)
      return true
    } catch (err) {
      console.error('Failed to refresh token:', err)
      return false
    }
  }

  /**
   * Получить профиль пользователя
   */
  async function fetchUserProfile() {
    if (!accessToken.value) return null

    try {
      const response = await authFetch('/api/auth/me')

      if (!response.ok) {
        throw new Error('Не удалось получить профиль')
      }

      const userData = await response.json()
      saveUser(userData)
      return userData
    } catch (err) {
      console.error('Failed to fetch user profile:', err)
      throw err
    }
  }

  /**
   * Получить статистику пользователя
   */
  async function getUserStats() {
    try {
      const response = await authFetch('/api/auth/me/stats')
      
      if (!response.ok) {
        throw new Error('Не удалось получить статистику')
      }

      return await response.json()
    } catch (err) {
      console.error('Failed to fetch user stats:', err)
      throw err
    }
  }

  /**
   * Удалить аккаунт
   */
  async function deleteAccount() {
    isLoading.value = true

    try {
      const response = await authFetch('/api/auth/account', {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Не удалось удалить аккаунт')
      }

      clearAuth()
      return { success: true }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Проверить валидность токена
   */
  async function validateToken() {
    if (!accessToken.value) return false

    try {
      const response = await authFetch('/api/auth/validate')
      return response.ok
    } catch (err) {
      return false
    }
  }

  /**
   * Инициализация - проверка авторизации при загрузке
   */
  async function initialize() {
    if (accessToken.value) {
      try {
        await fetchUserProfile()
        console.log('✅ Сессия восстановлена:', user.value?.username)
      } catch (err) {
        console.warn('⚠️ Сессия истекла')
        clearAuth()
      }
    }
  }

  // ============================================================================
  // RETURN
  // ============================================================================

  return {
    // State
    accessToken,
    refreshToken,
    user,
    isLoading,
    error,
    isAuthenticated,

    // Actions
    register,
    login,
    logout,
    refreshAccessToken,
    fetchUserProfile,
    getUserStats,
    deleteAccount,
    validateToken,
    initialize,
    clearAuth,

    // Helpers
    getAuthHeaders,
    authFetch
  }
})
