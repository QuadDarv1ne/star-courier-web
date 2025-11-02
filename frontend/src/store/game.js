/**
 * Game Store for StarCourier Web
 * Manages game state, player progress, and game logic
 * 
 * Uses Pinia for state management
 */

import { defineStore } from 'pinia'
import { apiClient } from '../services/api'

export const useGameStore = defineStore('game', {
  state: () => ({
    // ========================
    // GAME STATE
    // ========================
    
    isGameStarted: false,
    isLoading: false,
    playerId: null,
    currentSceneId: 'start',
    choicesMade: 0,
    visitedScenes: new Set(['start']),
    error: null,
    
    // ========================
    // PLAYER STATS
    // ========================
    
    stats: {
      health: 100,
      morale: 75,
      knowledge: 30,
      team: 50,
      danger: 0,
      security: 20,
      fuel: 100,
      money: 1000,
      psychic: 0,
      trust: 50
    },
    
    // ========================
    // CHARACTER RELATIONSHIPS
    // ========================
    
    relationships: {
      sara_nova: 50,
      grisha_romanov: 60,
      li_zheng: 45
    },
    
    // ========================
    // INVENTORY & GAME DATA
    // ========================
    
    inventory: ['Брекер кодов', 'Боевой нож'],
    currentScene: null,
    
    // ========================
    // GAME TIMING
    // ========================
    
    startTime: null,
    sessionDuration: 0,
    
    // ========================
    // SAVE MANAGEMENT
    // ========================
    
    savedGames: [],
    autoSaveEnabled: false
  }),

  getters: {
    /**
     * Check if game is over
     */
    isGameOver: (state) => {
      return state.stats.health <= 0 || state.stats.morale <= 0
    },

    /**
     * Get game progress percentage
     */
    gameProgress: (state) => {
      return Math.round((state.choicesMade / 15) * 100) // 15 сцен в игре
    },

    /**
     * Get total playtime in seconds
     */
    playtime: (state) => {
      if (!state.startTime) return 0
      return Math.floor((Date.now() - state.startTime) / 1000)
    },

    /**
     * Format playtime as HH:MM:SS
     */
    playtimeFormatted: (state) => {
      const totalSeconds = Math.floor((Date.now() - (state.startTime || Date.now())) / 1000)
      const hours = Math.floor(totalSeconds / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)
      const seconds = totalSeconds % 60
      
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    },

    /**
     * Get game summary
     */
    gameSummary: (state) => {
      return {
        playerId: state.playerId,
        currentScene: state.currentSceneId,
        choicesMade: state.choicesMade,
        stats: state.stats,
        relationships: state.relationships,
        visitedScenes: Array.from(state.visitedScenes),
        inventory: state.inventory
      }
    }
  },

  actions: {
    /**
     * Initialize a new game
     * Connects to backend API to start game session
     */
    async initializeGame() {
      this.isLoading = true
      this.error = null

      try {
        // Generate unique player ID
        this.playerId = this.generatePlayerId()
        
        console.log('🎮 Инициализация игры для игрока:', this.playerId)

        // Call backend API to start game
        const response = await apiClient.post('/game/start', {
          player_id: this.playerId
        })

        // Update state from API response
        this.currentSceneId = response.data.scene.id
        this.currentScene = response.data.scene
        this.stats = response.data.stats
        this.relationships = response.data.relationships

        // Initialize game
        this.isGameStarted = true
        this.startTime = Date.now()
        this.choicesMade = 0
        this.visitedScenes = new Set(['start'])

        console.log('✅ Игра инициализирована успешно')
        
        return {
          status: 'success',
          scene: response.data.scene,
          stats: response.data.stats,
          relationships: response.data.relationships
        }
      } catch (err) {
        this.error = err.message || 'Ошибка при инициализации игры'
        console.error('❌ Ошибка при инициализации:', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Make a choice and move to next scene
     * @param {string} nextSceneId - ID of the next scene
     * @param {Object} statChanges - Changes to apply to stats
     */
    async makeChoice(nextSceneId, statChanges = {}) {
      this.isLoading = true
      this.error = null

      try {
        console.log(`📍 Переход на сцену: ${nextSceneId}`)

        // Call backend API
        const response = await apiClient.post('/game/choose', {
          player_id: this.playerId,
          next_scene: nextSceneId,
          stats: statChanges
        })

        // Handle game over
        if (response.data.status === 'game_over') {
          console.log('💀 Игра окончена:', response.data.reason)
          return {
            status: 'game_over',
            reason: response.data.reason,
            choices_made: response.data.choices_made
          }
        }

        // Update state
        this.currentSceneId = response.data.scene.id
        this.currentScene = response.data.scene
        this.stats = response.data.stats
        this.relationships = response.data.relationships
        this.choicesMade = response.data.choices_made

        // Track visited scenes
        this.visitedScenes.add(nextSceneId)

        console.log('✅ Выбор обработан')

        return {
          status: 'success',
          scene: response.data.scene,
          stats: response.data.stats,
          relationships: response.data.relationships,
          choices_made: response.data.choices_made
        }
      } catch (err) {
        this.error = err.message || 'Ошибка при обработке выбора'
        console.error('❌ Ошибка при выборе:', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    /**
     * Get player statistics
     */
    async getPlayerStats() {
      try {
        const response = await apiClient.get(`/game/stats/${this.playerId}`)
        
        this.stats = response.data.stats
        this.relationships = response.data.relationships
        this.inventory = response.data.inventory
        this.choicesMade = response.data.choices_made

        return response.data
      } catch (err) {
        console.error('❌ Ошибка при получении статистики:', err)
        throw err
      }
    },

    /**
     * Fetch scene data from backend
     * @param {string} sceneId - Scene ID to fetch
     */
    async fetchScene(sceneId) {
      try {
        const response = await apiClient.get(`/game/scene/${sceneId}`)
        this.currentScene = response.data
        return response.data
      } catch (err) {
        console.error(`❌ Ошибка при загрузке сцены ${sceneId}:`, err)
        throw err
      }
    },

    /**
     * Generate a unique player ID
     */
    generatePlayerId() {
      return 'player_' + Math.random().toString(36).substr(2, 9)
    },

    /**
     * Reset game state
     */
    resetGame() {
      console.log('🔄 Сброс игры')
      
      this.isGameStarted = false
      this.playerId = null
      this.currentSceneId = 'start'
      this.currentScene = null
      this.choicesMade = 0
      this.startTime = null
      this.sessionDuration = 0
      this.error = null
      this.visitedScenes = new Set(['start'])

      // Reset stats to defaults
      this.stats = {
        health: 100,
        morale: 75,
        knowledge: 30,
        team: 50,
        danger: 0,
        security: 20,
        fuel: 100,
        money: 1000,
        psychic: 0,
        trust: 50
      }

      // Reset relationships
      this.relationships = {
        sara_nova: 50,
        grisha_romanov: 60,
        li_zheng: 45
      }

      // Reset inventory
      this.inventory = ['Брекер кодов', 'Боевой нож']

      console.log('✅ Игра сброшена')
    },

    /**
     * Save current game state to localStorage
     * @param {string} saveName - Optional name for the save
     */
    saveGame(saveName = null) {
      console.log('💾 Сохранение игры...')

      try {
        const saveData = {
          id: Date.now().toString(),
          name: saveName || `Сохранение #${this.savedGames.length + 1}`,
          timestamp: new Date().toISOString(),
          playerId: this.playerId,
          currentSceneId: this.currentSceneId,
          choicesMade: this.choicesMade,
          stats: { ...this.stats },
          relationships: { ...this.relationships },
          inventory: [...this.inventory],
          startTime: this.startTime,
          playtime: this.playtime
        }

        // Load existing saves
        const existingSaves = this.loadAllSavedGames()
        existingSaves.push(saveData)

        // Save to localStorage
        localStorage.setItem('starCourierSavedGames', JSON.stringify(existingSaves))
        this.savedGames = existingSaves

        console.log('✅ Игра сохранена:', saveData.name)
        return saveData
      } catch (error) {
        console.error('❌ Ошибка при сохранении:', error)
        this.error = 'Не удалось сохранить игру'
        throw error
      }
    },

    /**
     * Load a saved game
     * @param {string} saveId - ID of the save to load
     */
    loadGame(saveId) {
      console.log('📂 Загрузка сохранения:', saveId)

      try {
        const saves = this.loadAllSavedGames()
        const saveData = saves.find(save => save.id === saveId)

        if (!saveData) {
          throw new Error('Сохранение не найдено')
        }

        // Restore game state
        this.playerId = saveData.playerId
        this.currentSceneId = saveData.currentSceneId
        this.choicesMade = saveData.choicesMade
        this.stats = { ...saveData.stats }
        this.relationships = { ...saveData.relationships }
        this.inventory = [...saveData.inventory]
        this.startTime = saveData.startTime
        this.isGameStarted = true

        console.log('✅ Сохранение загружено:', saveData.name)
        return saveData
      } catch (error) {
        console.error('❌ Ошибка при загрузке:', error)
        this.error = 'Не удалось загрузить игру'
        throw error
      }
    },

    /**
     * Delete a saved game
     * @param {string} saveId - ID of the save to delete
     */
    deleteSave(saveId) {
      console.log('🗑️ Удаление сохранения:', saveId)

      try {
        const saves = this.loadAllSavedGames()
        const filteredSaves = saves.filter(save => save.id !== saveId)
        localStorage.setItem('starCourierSavedGames', JSON.stringify(filteredSaves))
        this.savedGames = filteredSaves

        console.log('✅ Сохранение удалено')
      } catch (error) {
        console.error('❌ Ошибка при удалении:', error)
        this.error = 'Не удалось удалить сохранение'
        throw error
      }
    },

    /**
     * Load all saved games from localStorage
     */
    loadAllSavedGames() {
      try {
        const saves = JSON.parse(localStorage.getItem('starCourierSavedGames') || '[]')
        this.savedGames = saves
        return saves
      } catch (error) {
        console.error('❌ Ошибка при загрузке сохранений:', error)
        this.savedGames = []
        return []
      }
    },

    /**
     * Clear all saved games
     */
    clearAllSaves() {
      console.log('🗑️ Удаление всех сохранений')

      try {
        localStorage.removeItem('starCourierSavedGames')
        this.savedGames = []
        console.log('✅ Все сохранения удалены')
      } catch (error) {
        console.error('❌ Ошибка при очистке:', error)
        this.error = 'Не удалось очистить сохранения'
        throw error
      }
    },

    /**
     * Export game progress as JSON
     */
    exportGameData() {
      const data = {
        version: '1.0.0',
        exportDate: new Date().toISOString(),
        currentGame: this.gameSummary,
        savedGames: this.savedGames
      }

      return JSON.stringify(data, null, 2)
    },

    /**
     * Import game progress from JSON
     */
    importGameData(jsonData) {
      try {
        const data = JSON.parse(jsonData)
        
        if (!data.version) {
          throw new Error('Неверный формат файла')
        }

        // Restore saved games
        this.savedGames = data.savedGames || []
        localStorage.setItem('starCourierSavedGames', JSON.stringify(this.savedGames))

        console.log('✅ Данные импортированы')
        return data
      } catch (error) {
        console.error('❌ Ошибка при импорте:', error)
        this.error = 'Не удалось импортировать данные'
        throw error
      }
    }
  }
})