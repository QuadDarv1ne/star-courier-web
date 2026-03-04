/**
 * Game Stats API Service
 * API клиент для статистики, достижений и лидерборда
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================================
// LEADERBOARD API
// ============================================================================

export const leaderboardApi = {
  async getLeaderboard(options = {}) {
    const { limit = 10, offset = 0, sortBy = 'score' } = options
    
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      sort_by: sortBy
    })

    const response = await fetch(`${API_URL}/api/leaderboard?${params}`)
    
    if (!response.ok) {
      throw new Error('Не удалось загрузить таблицу лидеров')
    }

    return response.json()
  },

  async getStats() {
    const response = await fetch(`${API_URL}/api/leaderboard/stats`)
    
    if (!response.ok) {
      throw new Error('Не удалось загрузить статистику')
    }

    return response.json()
  },

  async getPlayerPosition(username) {
    const response = await fetch(`${API_URL}/api/leaderboard/user/${encodeURIComponent(username)}`)
    
    if (!response.ok) {
      throw new Error('Не удалось найти игрока')
    }

    return response.json()
  },

  async getPlayersAround(username, rangeSize = 5) {
    const response = await fetch(
      `${API_URL}/api/leaderboard/around/${encodeURIComponent(username)}?range_size=${rangeSize}`
    )
    
    if (!response.ok) {
      throw new Error('Не удалось загрузить данные')
    }

    return response.json()
  }
}

// ============================================================================
// ACHIEVEMENTS API
// ============================================================================

export const achievementsApi = {
  async getAll(options = {}) {
    const { category = null, includeHidden = false } = options
    
    const params = new URLSearchParams()
    if (category) params.append('category', category)
    if (includeHidden) params.append('include_hidden', 'true')

    const response = await fetch(`${API_URL}/api/achievements?${params}`)
    
    if (!response.ok) {
      throw new Error('Не удалось загрузить достижения')
    }

    return response.json()
  },

  async getCategories() {
    const response = await fetch(`${API_URL}/api/achievements/categories`)
    
    if (!response.ok) {
      throw new Error('Не удалось загрузить категории')
    }

    return response.json()
  },

  async getById(achievementId) {
    const response = await fetch(`${API_URL}/api/achievements/${achievementId}`)
    
    if (!response.ok) {
      throw new Error('Достижение не найдено')
    }

    return response.json()
  },

  async checkForPlayer(playerData) {
    const response = await fetch(`${API_URL}/api/achievements/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(playerData)
    })
    
    if (!response.ok) {
      throw new Error('Не удалось проверить достижения')
    }

    return response.json()
  },

  async getStats() {
    const response = await fetch(`${API_URL}/api/achievements/stats/summary`)
    
    if (!response.ok) {
      throw new Error('Не удалось загрузить статистику')
    }

    return response.json()
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function calculateOverallProgress(unlockedCount, totalCount) {
  if (totalCount === 0) return 0
  return Math.round((unlockedCount / totalCount) * 100)
}

export function getRarityColor(rarity) {
  const colors = {
    common: '#9ca3af',
    uncommon: '#22c55e',
    rare: '#3b82f6',
    epic: '#a855f7',
    legendary: '#f59e0b'
  }
  return colors[rarity] || colors.common
}

export function getRarityName(rarity) {
  const names = {
    common: 'Обычное',
    uncommon: 'Необычное',
    rare: 'Редкое',
    epic: 'Эпическое',
    legendary: 'Легендарное'
  }
  return names[rarity] || rarity
}

export function getCategoryName(category) {
  const names = {
    story: 'История',
    exploration: 'Исследование',
    gameplay: 'Геймплей',
    stats: 'Статистика',
    relationships: 'Отношения',
    endings: 'Концовки',
    challenges: 'Испытания',
    meta: 'Мета'
  }
  return names[category] || category
}

export function formatPlaytime(seconds) {
  if (!seconds || seconds < 0) return '0м'
  if (seconds < 60) return `${Math.round(seconds)}с`
  if (seconds < 3600) return `${Math.round(seconds / 60)}м`
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.round((seconds % 3600) / 60)
  return `${hours}ч ${minutes}м`
}

export function formatScore(score) {
  if (!score) return '0'
  if (score >= 1000000) {
    return `${(score / 1000000).toFixed(1)}M`
  }
  if (score >= 1000) {
    return `${(score / 1000).toFixed(1)}K`
  }
  return Math.round(score).toString()
}

export function formatDate(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// ============================================================================
// WEBSOCKET FOR REAL-TIME UPDATES
// ============================================================================

export class GameStatsWebSocket {
  constructor(playerId) {
    this.playerId = playerId
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.listeners = new Map()
  }

  connect() {
    const wsUrl = `${API_URL.replace('http', 'ws')}/ws/${this.playerId}`
    
    this.ws = new WebSocket(wsUrl)
    
    this.ws.onopen = () => {
      console.log('🔌 WebSocket connected')
      this.reconnectAttempts = 0
      this.emit('connected')
    }
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emit(data.type, data)
      } catch (err) {
        console.error('WebSocket message error:', err)
      }
    }
    
    this.ws.onclose = () => {
      console.log('🔌 WebSocket disconnected')
      this.emit('disconnected')
      this.attemptReconnect()
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
      console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
      setTimeout(() => this.connect(), delay)
    }
  }

  send(type, data = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }))
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data))
    }
  }

  // Convenience methods
  joinGame(gameId) {
    this.send('join_game', { game_id: gameId })
  }

  leaveGame(gameId) {
    this.send('leave_game', { game_id: gameId })
  }

  sendChatMessage(gameId, text) {
    this.send('chat_message', { game_id: gameId, text })
  }

  gameAction(gameId, action, data = {}) {
    this.send('game_action', { game_id: gameId, action, data })
  }
}

export default {
  leaderboardApi,
  achievementsApi,
  GameStatsWebSocket,
  calculateOverallProgress,
  getRarityColor,
  getRarityName,
  getCategoryName,
  formatPlaytime,
  formatScore,
  formatDate
}
