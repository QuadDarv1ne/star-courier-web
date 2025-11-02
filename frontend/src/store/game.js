/**
 * Game Store for StarCourier Web
 * Manages game state, player progress, and game logic
 */

import { defineStore } from 'pinia'

export const useGameStore = defineStore('game', {
  state: () => ({
    // Game state
    isGameStarted: false,
    playerId: null,
    currentSceneId: 'start',
    choicesMade: 0,
    visitedScenes: new Set(['start']),
    
    // Player stats
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
    
    // Character relationships
    relationships: {
      sara_nova: 50,
      grisha_romanov: 60,
      li_zheng: 45
    },
    
    // Inventory
    inventory: ['Брекер кодов', 'Боевой нож'],
    
    // Game start time
    startTime: null,
    
    // Saved games
    savedGames: []
  }),
  
  getters: {
    /**
     * Get current scene data from backend
     */
    currentScene: (state) => {
      // This would normally fetch from backend
      // For now, we'll return a placeholder
      return {
        id: state.currentSceneId,
        title: 'Scene Title',
        text: 'Scene text content...',
        image: '🚀',
        character: 'Character Name',
        choices: []
      }
    },
    
    /**
     * Check if game is over
     */
    isGameOver: (state) => {
      return state.stats.health <= 0 || state.stats.morale <= 0
    }
  },
  
  actions: {
    /**
     * Initialize a new game
     */
    async initializeGame() {
      this.playerId = this.generatePlayerId()
      this.isGameStarted = true
      this.startTime = new Date()
      this.choicesMade = 0
      
      // Reset stats
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
      
      // Set initial scene
      this.currentSceneId = 'start'
      
      console.log('Game initialized for player:', this.playerId)
    },
    
        /**
     * Make a choice in the game
     * @param {string} nextSceneId - ID of the next scene
     * @param {Object} statChanges - Changes to apply to stats
     */
    async makeChoice(nextSceneId, statChanges = {}) {
      // Увеличиваем счетчик выборов
      this.choicesMade++

      // Обновляем текущую сцену
      this.currentSceneId = nextSceneId
      this.visitedScenes.add(nextSceneId)

      // Применяем изменения статов
      if (statChanges) {
        Object.entries(statChanges).forEach(([stat, change]) => {
          if (this.stats[stat] !== undefined) {
            this.stats[stat] = Math.max(0, Math.min(100, this.stats[stat] + change))
          }
        })
      }
    }
    async makeChoice(nextSceneId, statChanges = {}) {
      // Update stats
      for (const [key, value] of Object.entries(statChanges)) {
        if (this.stats.hasOwnProperty(key)) {
          this.stats[key] = Math.max(0, Math.min(100, this.stats[key] + value))
        }
      }
      
      // Update current scene
      this.currentSceneId = nextSceneId
      this.choicesMade++
      
      // Check for game over
      if (this.isGameOver) {
        return {
          status: 'game_over',
          reason: 'Вы не выжили в космосе'
        }
      }
      
      return {
        status: 'success',
        scene: {
          id: nextSceneId,
          title: 'Next Scene Title',
          text: 'Next scene content...',
          image: '🎮',
          character: 'Next Character',
          choices: []
        }
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
      this.isGameStarted = false
      this.playerId = null
      this.currentSceneId = 'start'
      this.choicesMade = 0
      this.startTime = null
    },
    
    /**
     * Save current game state
     */
    saveGame(saveName = null) {
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
        startTime: this.startTime
      }
      
      // Save to localStorage
      try {
        const savedGames = JSON.parse(localStorage.getItem('starCourierSavedGames') || '[]')
        savedGames.push(saveData)
        localStorage.setItem('starCourierSavedGames', JSON.stringify(savedGames))
        
        // Update store
        this.savedGames = savedGames
        
        console.log('Game saved:', saveData.name)
        return saveData
      } catch (error) {
        console.error('Failed to save game:', error)
        throw new Error('Не удалось сохранить игру')
      }
    },
    
    /**
     * Load a saved game
     * @param {string} saveId - ID of the save to load
     */
    loadGame(saveId) {
      try {
        const savedGames = JSON.parse(localStorage.getItem('starCourierSavedGames') || '[]')
        const saveData = savedGames.find(save => save.id === saveId)
        
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
        this.startTime = new Date(saveData.startTime)
        this.isGameStarted = true
        
        console.log('Game loaded:', saveData.name)
        return saveData
      } catch (error) {
        console.error('Failed to load game:', error)
        throw new Error('Не удалось загрузить игру')
      }
    },
    
    /**
     * Delete a saved game
     * @param {string} saveId - ID of the save to delete
     */
    deleteSave(saveId) {
      try {
        const savedGames = JSON.parse(localStorage.getItem('starCourierSavedGames') || '[]')
        const filteredGames = savedGames.filter(save => save.id !== saveId)
        localStorage.setItem('starCourierSavedGames', JSON.stringify(filteredGames))
        
        // Update store
        this.savedGames = filteredGames
        
        console.log('Save deleted:', saveId)
      } catch (error) {
        console.error('Failed to delete save:', error)
        throw new Error('Не удалось удалить сохранение')
      }
    },
    
    /**
     * Load all saved games
     */
    loadSavedGames() {
      try {
        const savedGames = JSON.parse(localStorage.getItem('starCourierSavedGames') || '[]')
        this.savedGames = savedGames
        return savedGames
      } catch (error) {
        console.error('Failed to load saved games:', error)
        this.savedGames = []
        return []
      }
    }
  }
})