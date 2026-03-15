/**
 * Game Store for StarCourier Web
 * Manages game state, player progress, and game logic
 * 
 * Uses Pinia for state management
 */

import { defineStore } from 'pinia'
import { apiClient, handleApiCall, formatErrorMessage, sceneApi, characterApi } from '../services/api'

// WebSocket connection
let websocket = null
let websocketReconnectAttempts = 0
const MAX_RECONNECT_ATTEMPTS = 5

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
    visitedScenes: ['start'], // Используем массив вместо Set для реактивности
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
    autoSaveEnabled: true,
    autoSaveInterval: 300000, // 5 minutes
    lastAutoSave: null,
    autoSaveTimer: null,
    
    // Cloud save management
    cloudSaves: [],
    isCloudSyncEnabled: false,
    lastCloudSync: null,
    
    // ========================
    // ENHANCED STATISTICS
    // ========================
    
    // Track min/max stats throughout the game
    statHistory: {
      health: { min: 100, max: 100 },
      morale: { min: 75, max: 75 },
      knowledge: { min: 30, max: 30 },
      team: { min: 50, max: 50 },
      danger: { min: 0, max: 0 },
      security: { min: 20, max: 20 },
      fuel: { min: 100, max: 100 },
      money: { min: 1000, max: 1000 },
      psychic: { min: 0, max: 0 },
      trust: { min: 50, max: 50 }
    },
    
    // Track choices made
    choiceHistory: [],
    
    // Track achievements progress
    achievementsProgress: {},
    
    // Track time spent in each scene
    sceneTimeTracking: {},
    
    // Track stat changes over time
    statChangeHistory: [],
    
    // Track decision patterns
    decisionPatterns: {
      aggressive: 0,  // combat/force choices
      diplomatic: 0,  // negotiation/peace choices
      analytical: 0,  // knowledge/research choices
      caring: 0       // team/relationship choices
    },
    
    // Add cache for scenes and characters with timestamps
    sceneCache: new Map(),
    characterCache: new Map(),
    cacheTimestamps: new Map(),
    
    // Cache expiration time (10 minutes)
    cacheExpiration: 10 * 60 * 1000,
    
    // WebSocket connection status
    websocketConnected: false,
    websocketReconnectAttempts: 0
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
        inventory: state.inventory,
        playtime: state.playtime,
        statHistory: state.statHistory,
        choiceHistory: state.choiceHistory,
        sceneTimeTracking: state.sceneTimeTracking,
        statChangeHistory: state.statChangeHistory,
        decisionPatterns: state.decisionPatterns
      }
    },
    
    /**
     * Get favorite character based on relationships
     */
    favoriteCharacter: (state) => {
      const entries = Object.entries(state.relationships)
      if (entries.length === 0) return null
      
      const max = entries.reduce((max, entry) => entry[1] > max[1] ? entry : max)
      return {
        id: max[0],
        name: max[0] === 'sara_nova' ? 'Сара Нова' : 
              max[0] === 'grisha_romanov' ? 'Гриша Романов' : 
              max[0] === 'li_zheng' ? 'Ли Чжэнь' : max[0],
        relationship: max[1]
      }
    },
    
    /**
     * Get game difficulty based on danger level
     */
    gameDifficulty: (state) => {
      if (state.stats.danger >= 80) return 'Экстремальная'
      if (state.stats.danger >= 60) return 'Высокая'
      if (state.stats.danger >= 40) return 'Средняя'
      if (state.stats.danger >= 20) return 'Низкая'
      return 'Лёгкая'
    },
    
    /**
     * Get player decision style based on patterns
     */
    decisionStyle: (state) => {
      const patterns = state.decisionPatterns
      const maxPattern = Math.max(patterns.aggressive, patterns.diplomatic, patterns.analytical, patterns.caring)
      
      if (maxPattern === 0) return 'Сбалансированный'
      
      if (patterns.aggressive === maxPattern) return 'Агрессивный'
      if (patterns.diplomatic === maxPattern) return 'Дипломатичный'
      if (patterns.analytical === maxPattern) return 'Аналитический'
      if (patterns.caring === maxPattern) return 'Заботливый'
      
      return 'Сбалансированный'
    },
    
    /**
     * Get average stats
     */
    averageStats: (state) => {
      const stats = state.stats
      const total = Object.values(stats).reduce((sum, val) => sum + val, 0)
      return Math.round(total / Object.keys(stats).length)
    },
    
    /**
     * Get strongest stat
     */
    strongestStat: (state) => {
      const stats = state.stats
      let maxStat = ''
      let maxValue = -1
      
      Object.entries(stats).forEach(([key, value]) => {
        if (value > maxValue) {
          maxValue = value
          maxStat = key
        }
      })
      
      const statLabels = {
        health: 'Здоровье',
        morale: 'Мораль',
        knowledge: 'Знание',
        team: 'Команда',
        danger: 'Опасность',
        security: 'Безопасность',
        fuel: 'Топливо',
        money: 'Деньги',
        psychic: 'Психика',
        trust: 'Доверие'
      }
      
      return statLabels[maxStat] || maxStat
    },
    
    /**
     * Get cached scene with expiration check
     */
    getCachedScene: (state) => (sceneId) => {
      const cached = state.sceneCache.get(sceneId)
      if (cached) {
        const timestamp = state.cacheTimestamps.get(`scene-${sceneId}`)
        // Check if cache is still valid
        if (timestamp && Date.now() - timestamp < state.cacheExpiration) {
          return cached
        } else {
          // Remove expired cache
          state.sceneCache.delete(sceneId)
          state.cacheTimestamps.delete(`scene-${sceneId}`)
        }
      }
      return null
    },
    
    /**
     * Get cached character with expiration check
     */
    getCachedCharacter: (state) => (charId) => {
      const cached = state.characterCache.get(charId)
      if (cached) {
        const timestamp = state.cacheTimestamps.get(`character-${charId}`)
        // Check if cache is still valid
        if (timestamp && Date.now() - timestamp < state.cacheExpiration) {
          return cached
        } else {
          // Remove expired cache
          state.characterCache.delete(charId)
          state.cacheTimestamps.delete(`character-${charId}`)
        }
      }
      return null
    }
  },

  actions: {
    /**
     * Initialize a new game
     * Connects to backend API to start game session
     */
    async initializeGame() {
      this.isLoading = true;
      this.error = null;

      try {
        // Generate unique player ID
        this.playerId = this.generatePlayerId();
        
        console.log('🎮 Инициализация игры для игрока:', this.playerId);

        // Call backend API to start game
        const response = await handleApiCall(
          () => apiClient.post('/game/start', {
            player_id: this.playerId
          }),
          'начало игры'
        );

        // Validate API response before updating state
        const sceneErrors = this.validateScene(response.scene);
        this.handleValidationErrors(sceneErrors, 'scene data');
        
        // Update state from API response
        this.currentSceneId = response.scene.id;
        this.currentScene = response.scene;
        this.stats = response.stats;
        this.relationships = response.relationships;

        // Validate game state after update
        const validationErrors = this.validateGameState();
        this.handleValidationErrors(validationErrors, 'initial game state');

        // Initialize game
        this.isGameStarted = true;
        this.startTime = Date.now();
        this.sceneEntryTime = Date.now();
        this.choicesMade = 0;
        this.visitedScenes = ['start'];
        this.choiceHistory = [];
        
        // Initialize stat history
        Object.keys(this.stats).forEach(stat => {
          this.statHistory[stat] = {
            min: this.stats[stat],
            max: this.stats[stat]
          };
        });
        
        // Start auto-save timer if enabled
        if (this.autoSaveEnabled) {
          this.startAutoSave();
        }

        // Connect to WebSocket for real-time updates
        this.connectWebSocket();

        console.log('✅ Игра инициализирована успешно');
        
        return {
          status: 'success',
          scene: response.scene,
          stats: response.stats,
          relationships: response.relationships
        };
      } catch (err) {
        this.error = formatErrorMessage(err) || 'Ошибка при инициализации игры';
        console.error('❌ Ошибка при инициализации:', err);
        
        // Show user-friendly error notification
        if (this.$uiStore) {
          this.$uiStore.showNetworkError('Не удалось начать игру. Проверьте подключение к серверу.');
        }
        
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Make a choice and move to next scene
     * @param {string} nextSceneId - ID of the next scene
     * @param {Object} statChanges - Changes to apply to stats
     */
    async makeChoice(nextSceneId, statChanges = {}) {
      this.isLoading = true;
      this.error = null;

      try {
        console.log(`📍 Переход на сцену: ${nextSceneId}`);

        // Record choice in history
        this.choiceHistory.push({
          sceneId: this.currentSceneId,
          nextSceneId,
          statChanges,
          timestamp: Date.now()
        });

        // Track time spent in current scene
        if (this.sceneEntryTime) {
          const timeSpent = Date.now() - this.sceneEntryTime;
          if (!this.sceneTimeTracking[this.currentSceneId]) {
            this.sceneTimeTracking[this.currentSceneId] = 0;
          }
          this.sceneTimeTracking[this.currentSceneId] += timeSpent;
        }
        this.sceneEntryTime = Date.now();

        // Call backend API
        const response = await handleApiCall(
          () => apiClient.post('/game/choose', {
            player_id: this.playerId,
            next_scene: nextSceneId,
            stats: statChanges
          }),
          'выполнение выбора'
        );

        // Handle game over
        if (response.status === 'game_over') {
          console.log('💀 Игра окончена:', response.reason);
          // Stop auto-save when game ends
          this.stopAutoSave();
          return {
            status: 'game_over',
            reason: response.reason,
            choices_made: response.choices_made
          };
        }

        // Validate response scene
        const sceneErrors = this.validateScene(response.scene);
        this.handleValidationErrors(sceneErrors, 'scene data');
        
        // Update state
        this.currentSceneId = response.scene.id;
        this.currentScene = response.scene;
        this.choicesMade = response.choices_made;

        // Track visited scenes
        if (!this.visitedScenes.includes(nextSceneId)) {
          this.visitedScenes.push(nextSceneId);
        }

        // Update stats and track history
        Object.keys(statChanges).forEach(stat => {
          if (this.stats.hasOwnProperty(stat)) {
            const oldValue = this.stats[stat];
            const change = statChanges[stat];
            const newValue = Math.max(0, Math.min(100, oldValue + change));
            
            this.stats[stat] = newValue;
            
            // Track stat changes over time
            this.statChangeHistory.push({
              stat,
              oldValue,
              newValue,
              change,
              timestamp: Date.now()
            });
            
            // Update stat history
            if (!this.statHistory[stat]) {
              this.statHistory[stat] = { min: newValue, max: newValue };
            } else {
              this.statHistory[stat].min = Math.min(this.statHistory[stat].min, newValue);
              this.statHistory[stat].max = Math.max(this.statHistory[stat].max, newValue);
            }
            
            // Update decision patterns based on stat changes
            this.updateDecisionPatterns(stat, change);
          }
        });

        // Update relationships if provided
        if (response.relationships) {
          this.relationships = response.relationships;
        }
        
        // Validate game state after update
        const validationErrors = this.validateGameState();
        this.handleValidationErrors(validationErrors, 'game state after choice');
        
        // Auto-save after each choice if enabled
        if (this.autoSaveEnabled) {
          await this.autoSave();
        }

        console.log('✅ Выбор обработан');

        return {
          status: 'success',
          scene: response.scene,
          stats: this.stats,
          relationships: this.relationships,
          choices_made: response.choices_made
        };
      } catch (err) {
        this.error = formatErrorMessage(err) || 'Ошибка при обработке выбора';
        console.error('❌ Ошибка при выборе:', err);
        
        // Show user-friendly error notification
        if (this.$uiStore) {
          this.$uiStore.showNetworkError('Не удалось выполнить выбор. Проверьте подключение к серверу.');
        }
        
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Get player statistics
     */
    async getPlayerStats() {
      try {
        const response = await handleApiCall(
          () => apiClient.get(`/game/stats/${this.playerId}`),
          'получение статистики игрока'
        );
        
        this.stats = response.stats;
        this.relationships = response.relationships;
        this.inventory = response.inventory;
        this.choicesMade = response.choices_made;

        return response;
      } catch (err) {
        console.error('❌ Ошибка при получении статистики:', err);
        this.error = formatErrorMessage(err) || 'Ошибка при получении статистики';
        
        // Show user-friendly error notification
        if (this.$uiStore) {
          this.$uiStore.showNetworkError('Не удалось получить статистику игрока. Проверьте подключение к серверу.');
        }
        
        throw err;
      }
    },

    /**
     * Fetch scene data from backend with caching
     * @param {string} sceneId - Scene ID to fetch
     */
    async fetchScene(sceneId) {
      try {
        // Validate input
        if (!sceneId || typeof sceneId !== 'string') {
          throw new Error('Неверный ID сцены');
        }
        
        // Check cache first
        const cachedScene = this.getCachedScene(sceneId);
        if (cachedScene) {
          console.log(`📥 Scene loaded from cache: ${sceneId}`);
          this.currentScene = cachedScene;
          return cachedScene;
        }

        const response = await handleApiCall(
          () => apiClient.get(`/game/scene/${sceneId}`),
          'загрузка сцены'
        );
        
        // Cache the scene
        this.sceneCache.set(sceneId, response);
        this.cacheTimestamps.set(`scene-${sceneId}`, Date.now());
        
        this.currentScene = response;
        return response;
      } catch (err) {
        console.error(`❌ Ошибка при загрузке сцены ${sceneId}:`, err);
        this.error = formatErrorMessage(err) || `Ошибка при загрузке сцены ${sceneId}`;
        
        // Show user-friendly error notification
        if (this.$uiStore) {
          this.$uiStore.showNetworkError(`Не удалось загрузить сцену "${sceneId}". Проверьте подключение к серверу.`);
        }
        
        throw err;
      }
    },

    /**
     * Generate a unique player ID
     */
    generatePlayerId() {
      return 'player_' + Math.random().toString(36).substr(2, 9)
    },
    
    /**
     * Update decision patterns based on stat changes
     * @param {string} stat - The stat that changed
     * @param {number} change - The amount of change
     */
    updateDecisionPatterns(stat, change) {
      // Only track significant changes
      if (Math.abs(change) < 5) return;
      
      // Map stats to decision patterns
      const statToPattern = {
        // Aggressive choices affect these stats
        danger: 'aggressive',
        security: 'aggressive',
        
        // Diplomatic choices affect these stats
        trust: 'diplomatic',
        morale: 'diplomatic',
        team: 'diplomatic',
        
        // Analytical choices affect these stats
        knowledge: 'analytical',
        psychic: 'analytical',
        
        // Caring choices affect these stats
        health: 'caring',
        morale: 'caring',
        team: 'caring'
      };
      
      const pattern = statToPattern[stat];
      if (pattern) {
        // Increase pattern score for positive changes, decrease for negative
        this.decisionPatterns[pattern] += change > 0 ? 1 : -1;
        // Ensure pattern scores don't go negative
        this.decisionPatterns[pattern] = Math.max(0, this.decisionPatterns[pattern]);
      }
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
      this.visitedScenes = ['start']

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
      
      // Reset enhanced statistics
      this.sceneTimeTracking = {};
      this.statChangeHistory = [];
      this.decisionPatterns = {
        aggressive: 0,
        diplomatic: 0,
        analytical: 0,
        caring: 0
      };
      this.sceneEntryTime = null;

      // Disconnect WebSocket
      this.disconnectWebSocket();

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
          playtime: this.playtime,
          visitedScenes: Array.from(this.visitedScenes),
          choiceHistory: [...this.choiceHistory],
          statHistory: { ...this.statHistory },
          sceneTimeTracking: { ...this.sceneTimeTracking },
          statChangeHistory: [...this.statChangeHistory],
          decisionPatterns: { ...this.decisionPatterns }
        }

        // Load existing saves
        const existingSaves = this.loadAllSavedGames()
        existingSaves.push(saveData)

        // Save to localStorage
        localStorage.setItem('starCourierSavedGames', JSON.stringify(existingSaves))
        this.savedGames = existingSaves

        // Save to cloud if enabled
        if (this.isCloudSyncEnabled && this.playerId) {
          this.saveToCloud(saveData)
        }

        console.log('✅ Игра сохранена:', saveData.name)
        return saveData
      } catch (error) {
        console.error('❌ Ошибка при сохранении:', error)
        this.error = 'Не удалось сохранить игру'
        throw error
      }
    },
    
    /**
     * Save game to cloud storage
     * @param {Object} saveData - Save data to upload
     */
    async saveToCloud(saveData) {
      if (!this.playerId) {
        console.warn('⚠️ Невозможно сохранить в облако: отсутствует ID игрока')
        return
      }

      try {
        console.log('☁️ Сохранение в облако...')
        
        const response = await handleApiCall(
          () => apiClient.post('/game/save/cloud', {
            player_id: this.playerId,
            save_data: saveData
          }),
          'сохранение в облако'
        )

        this.lastCloudSync = Date.now()
        console.log('✅ Игра сохранена в облако:', response.save_id)
        
        // Refresh cloud saves list
        await this.loadCloudSaves()
        
        return response
      } catch (error) {
        console.error('❌ Ошибка при сохранении в облако:', error)
        this.error = 'Не удалось сохранить в облако: ' + (error.message || 'ошибка соединения')
        throw error
      }
    },
    
    /**
     * Load game from cloud storage
     * @param {string} saveId - ID of the cloud save to load
     */
    async loadFromCloud(saveId) {
      if (!this.playerId) {
        throw new Error('Невозможно загрузить из облака: отсутствует ID игрока')
      }

      try {
        console.log('☁️ Загрузка из облака:', saveId)
        
        const response = await handleApiCall(
          () => apiClient.post('/game/load/cloud', {
            player_id: this.playerId,
            save_id: saveId
          }),
          'загрузка из облака'
        )
        
        // Find the save data in our cloud saves
        const cloudSave = this.cloudSaves.find(save => save.id === saveId)
        if (!cloudSave) {
          throw new Error('Сохранение не найдено в облаке')
        }
        
        // Restore game state
        const saveData = cloudSave.data
        this.playerId = saveData.playerId
        this.currentSceneId = saveData.currentSceneId
        this.choicesMade = saveData.choicesMade
        this.stats = { ...saveData.stats }
        this.relationships = { ...saveData.relationships }
        this.inventory = [...saveData.inventory]
        this.startTime = saveData.startTime
        this.isGameStarted = true
        
        // Restore enhanced data
        this.visitedScenes = Array.isArray(saveData.visitedScenes) ? saveData.visitedScenes : ['start']
        this.choiceHistory = [...(saveData.choiceHistory || [])]
        this.statHistory = { ...(saveData.statHistory || {}) }
        this.sceneTimeTracking = { ...(saveData.sceneTimeTracking || {}) }
        this.statChangeHistory = [...(saveData.statChangeHistory || [])]
        this.decisionPatterns = { ...(saveData.decisionPatterns || { aggressive: 0, diplomatic: 0, analytical: 0, caring: 0 }) }

        console.log('✅ Сохранение загружено из облака:', saveData.name)
        return saveData
      } catch (error) {
        console.error('❌ Ошибка при загрузке из облака:', error)
        this.error = 'Не удалось загрузить из облака: ' + (error.message || 'ошибка соединения')
        throw error
      }
    },
    
    /**
     * Load all cloud saves for current player
     */
    async loadCloudSaves() {
      if (!this.playerId) {
        this.cloudSaves = []
        return []
      }

      try {
        console.log('☁️ Загрузка списка облачных сохранений...')
        
        const response = await handleApiCall(
          () => apiClient.get(`/game/saves/cloud/${this.playerId}`),
          'загрузка списка сохранений'
        )
        
        this.cloudSaves = response.saves || []
        console.log('✅ Загружено облачных сохранений:', this.cloudSaves.length)
        
        return this.cloudSaves
      } catch (error) {
        console.error('❌ Ошибка при загрузке облачных сохранений:', error)
        this.error = 'Не удалось загрузить облачные сохранения: ' + (error.message || 'ошибка соединения')
        this.cloudSaves = []
        return []
      }
    },
    
    /**
     * Delete a cloud save
     * @param {string} saveId - ID of the cloud save to delete
     */
    async deleteCloudSave(saveId) {
      if (!this.playerId) {
        throw new Error('Невозможно удалить из облака: отсутствует ID игрока')
      }

      try {
        console.log('☁️ Удаление облачного сохранения:', saveId)
        
        await handleApiCall(
          () => apiClient.delete(`/game/save/cloud/${this.playerId}/${saveId}`),
          'удаление сохранения из облака'
        )
        
        // Remove from local cache
        this.cloudSaves = this.cloudSaves.filter(save => save.id !== saveId)
        
        console.log('✅ Облачное сохранение удалено:', saveId)
        return true
      } catch (error) {
        console.error('❌ Ошибка при удалении облачного сохранения:', error)
        this.error = 'Не удалось удалить облачное сохранение: ' + (error.message || 'ошибка соединения')
        throw error
      }
    },
    
    /**
     * Toggle cloud sync
     */
    toggleCloudSync() {
      this.isCloudSyncEnabled = !this.isCloudSyncEnabled
      console.log('☁️ Синхронизация с облаком:', this.isCloudSyncEnabled ? 'включена' : 'выключена')
      
      // If enabling, load cloud saves
      if (this.isCloudSyncEnabled && this.playerId) {
        this.loadCloudSaves()
      }
      
      return this.isCloudSyncEnabled
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
        
        // Restore enhanced data
        this.visitedScenes = Array.isArray(saveData.visitedScenes) ? saveData.visitedScenes : ['start']
        this.choiceHistory = [...(saveData.choiceHistory || [])]
        this.statHistory = { ...(saveData.statHistory || {}) }
        this.sceneTimeTracking = { ...(saveData.sceneTimeTracking || {}) }
        this.statChangeHistory = [...(saveData.statChangeHistory || [])]
        this.decisionPatterns = { ...(saveData.decisionPatterns || { aggressive: 0, diplomatic: 0, analytical: 0, caring: 0 }) }

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
     * Start auto-save timer
     */
    startAutoSave() {
      if (this.autoSaveTimer) {
        clearInterval(this.autoSaveTimer);
      }
      
      this.autoSaveTimer = setInterval(() => {
        if (this.isGameStarted) {
          this.autoSave();
        }
      }, this.autoSaveInterval);
      
      console.log('⏱️ Автосохранение включено (каждые ' + (this.autoSaveInterval / 1000 / 60) + ' минут)');
    },
    
    /**
     * Stop auto-save timer
     */
    stopAutoSave() {
      if (this.autoSaveTimer) {
        clearInterval(this.autoSaveTimer);
        this.autoSaveTimer = null;
        console.log('⏹️ Автосохранение отключено');
      }
    },
    
    /**
     * Perform auto-save
     */
    async autoSave() {
      if (!this.isGameStarted) return;
      
      try {
        const saveData = this.saveGame('Автосохранение');
        this.lastAutoSave = Date.now();
        console.log('💾 Автосохранение выполнено:', saveData.name);
        return saveData;
      } catch (error) {
        console.error('❌ Ошибка автосохранения:', error);
        this.error = 'Ошибка автосохранения: ' + error.message;
      }
    },
    
    /**
     * Set auto-save interval
     * @param {number} interval - Interval in milliseconds
     */
    setAutoSaveInterval(interval) {
      this.autoSaveInterval = interval;
      if (this.autoSaveEnabled && this.isGameStarted) {
        this.startAutoSave();
      }
    },
    
    /**
     * Toggle auto-save
     */
    toggleAutoSave() {
      this.autoSaveEnabled = !this.autoSaveEnabled;
      
      if (this.autoSaveEnabled && this.isGameStarted) {
        this.startAutoSave();
      } else {
        this.stopAutoSave();
      }
      
      return this.autoSaveEnabled;
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
    },
    
    /**
     * Load scene with caching
     */
    async loadScene(sceneId) {
      // Validate input
      if (!sceneId || typeof sceneId !== 'string') {
        throw new Error('Неверный ID сцены');
      }
      
      // Check cache first
      const cachedScene = this.getCachedScene(sceneId)
      if (cachedScene) {
        console.log(`📥 Scene loaded from cache: ${sceneId}`)
        this.currentScene = cachedScene
        return cachedScene
      }
      
      try {
        // Load from API if not in cache
        const response = await sceneApi.getScene(sceneId)
        const scene = response.data
        
        // Cache the scene
        this.sceneCache.set(sceneId, scene)
        this.cacheTimestamps.set(`scene-${sceneId}`, Date.now())
        
        this.currentScene = scene
        return scene
      } catch (error) {
        console.error('Failed to load scene:', error)
        throw error
      }
    },
    
    /**
     * Load character with caching
     */
    async loadCharacter(characterId) {
      // Validate input
      if (!characterId || typeof characterId !== 'string') {
        throw new Error('Неверный ID персонажа');
      }
      
      // Check cache first
      const cachedCharacter = this.getCachedCharacter(characterId)
      if (cachedCharacter) {
        console.log(`📥 Character loaded from cache: ${characterId}`)
        return cachedCharacter
      }
      
      try {
        // Load from API if not in cache
        const response = await characterApi.getCharacter(characterId)
        const character = response.data
        
        // Cache the character
        this.characterCache.set(characterId, character)
        this.cacheTimestamps.set(`character-${characterId}`, Date.now())
        
        return character
      } catch (error) {
        console.error('Failed to load character:', error)
        throw error
      }
    },
    
    /**
     * Clear all caches
     */
    clearCaches() {
      this.sceneCache.clear()
      this.characterCache.clear()
      this.cacheTimestamps.clear()
      console.log('✅ All caches cleared')
    },
    
    /**
     * Get cache statistics
     */
    getCacheStats() {
      return {
        scenes: this.sceneCache.size,
        characters: this.characterCache.size,
        timestamps: this.cacheTimestamps.size
      }
    },
    
    /**
     * Batch load scenes for better performance
     */
    async batchLoadScenes(sceneIds) {
      // Validate input
      if (!Array.isArray(sceneIds)) {
        throw new Error('Неверный формат списка сцен');
      }
      
      const results = {}
      const toLoad = []
      
      // Check cache first
      sceneIds.forEach(id => {
        // Validate each scene ID
        if (!id || typeof id !== 'string') {
          console.warn('Неверный ID сцены в списке:', id)
          return
        }
        
        const cached = this.getCachedScene(id)
        if (cached) {
          results[id] = cached
        } else {
          toLoad.push(id)
        }
      })
      
      // Load uncached scenes using batch endpoint
      if (toLoad.length > 0) {
        try {
          // Use batch endpoint for better performance
          const response = await sceneApi.getScenesBatch(toLoad)
          const scenes = response.data.scenes
          
          // Process each scene
          Object.entries(scenes).forEach(([id, scene]) => {
            // Cache the scene
            this.sceneCache.set(id, scene)
            this.cacheTimestamps.set(`scene-${id}`, Date.now())
            results[id] = scene
          })
          
          // Handle not found scenes
          if (response.data.not_found && response.data.not_found.length > 0) {
            console.warn('Сцены не найдены:', response.data.not_found)
          }
        } catch (error) {
          console.error('Failed to batch load scenes:', error)
          throw error
        }
      }
      
      return results
    },
    
    /**
     * Validate game state
     */
    validateGameState() {
      const errors = []
      
      // Validate player ID
      if (!this.playerId || typeof this.playerId !== 'string') {
        errors.push('Неверный ID игрока')
      }
      
      // Validate current scene ID
      if (!this.currentSceneId || typeof this.currentSceneId !== 'string') {
        errors.push('Неверный ID текущей сцены')
      }
      
      // Validate stats
      const validStats = ['health', 'morale', 'knowledge', 'team', 'danger', 'security', 'fuel', 'money', 'psychic', 'trust']
      const statsWithMax100 = ['health', 'morale', 'knowledge', 'team', 'danger', 'security', 'fuel', 'psychic', 'trust']
      Object.entries(this.stats).forEach(([key, value]) => {
        if (!validStats.includes(key)) {
          errors.push(`Неизвестная статистика: ${key}`)
        }
        if (typeof value !== 'number' || isNaN(value) || value < 0) {
          errors.push(`Неверное значение статистики: ${key} = ${value}`)
        }
        // Only check max value for stats that should be <= 100
        if (statsWithMax100.includes(key) && value > 100) {
          errors.push(`Неверное значение статистики: ${key} = ${value} (максимум 100)`)
        }
      })
      
      // Validate relationships (warning only, not error - characters can be added dynamically)
      // Relationships can range from -100 to 100 (negative = hostile, positive = friendly)
      Object.entries(this.relationships).forEach(([key, value]) => {
        if (typeof value !== 'number' || isNaN(value) || value < -100 || value > 100) {
          errors.push(`Неверное значение отношения: ${key} = ${value}`)
        }
      })
      
      // Validate inventory
      if (!Array.isArray(this.inventory)) {
        errors.push('Неверный формат инвентаря')
      } else {
        this.inventory.forEach((item, index) => {
          if (typeof item !== 'string') {
            errors.push(`Неверный предмет в инвентаре на позиции ${index}`)
          }
        })
      }
      
      // Validate choices made
      if (typeof this.choicesMade !== 'number' || isNaN(this.choicesMade) || this.choicesMade < 0) {
        errors.push('Неверное количество сделанных выборов')
      }
      
      // Validate visited scenes
      if (!Array.isArray(this.visitedScenes)) {
        errors.push('Неверный формат посещенных сцен')
      }
      
      return errors
    },
    
    /**
     * Validate scene data
     */
    validateScene(scene) {
      const errors = []
      
      if (!scene) {
        errors.push('Сцена не существует')
        return errors
      }
      
      // Validate scene ID
      if (!scene.id || typeof scene.id !== 'string') {
        errors.push('Неверный ID сцены')
      }
      
      // Validate scene title
      if (!scene.title || typeof scene.title !== 'string') {
        errors.push('Неверное название сцены')
      }
      
      // Validate scene text
      if (!scene.text || typeof scene.text !== 'string') {
        errors.push('Неверный текст сцены')
      }
      
      // Validate scene image
      if (!scene.image || typeof scene.image !== 'string') {
        errors.push('Неверное изображение сцены')
      }
      
      // Validate scene character
      if (!scene.character || typeof scene.character !== 'string') {
        errors.push('Неверный персонаж сцены')
      }
      
      // Validate scene choices
      if (!Array.isArray(scene.choices)) {
        errors.push('Неверный формат выборов сцены')
      } else {
        scene.choices.forEach((choice, index) => {
          if (!choice.text || typeof choice.text !== 'string') {
            errors.push(`Неверный текст выбора ${index + 1}`)
          }
          if (!choice.next || typeof choice.next !== 'string') {
            errors.push(`Неверный следующий ID сцены для выбора ${index + 1}`)
          }
          if (choice.stats && typeof choice.stats !== 'object') {
            errors.push(`Неверный формат статистики для выбора ${index + 1}`)
          }
        })
      }
      
      return errors
    },
    
    /**
     * Handle validation errors
     */
    handleValidationErrors(errors, context = 'game state') {
      if (errors.length > 0) {
        console.error(`❌ Validation errors in ${context}:`, errors)
        
        // Show user-friendly error notification
        if (this.$uiStore) {
          const errorMessage = `Обнаружены ошибки в ${context}: ${errors.join(', ')}`
          this.$uiStore.showError(errorMessage)
        }
        
        // Throw error for critical validation failures
        throw new Error(`Validation failed for ${context}: ${errors.join(', ')}`)
      }
    },
    
    /**
     * Connect to WebSocket for real-time updates
     */
    connectWebSocket() {
      if (!this.playerId) {
        console.warn('Cannot connect WebSocket: No player ID')
        return
      }
      
      // Close existing connection if any
      if (websocket) {
        websocket.close()
      }
      
      // Create WebSocket connection
      const wsUrl = `${apiClient.defaults.baseURL.replace('http', 'ws')}/ws/game/${this.playerId}`
      console.log(`🔌 Connecting to WebSocket: ${wsUrl}`)
      
      websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        console.log('✅ WebSocket connected')
        this.websocketConnected = true
        websocketReconnectAttempts = 0
        
        // Send ping every 30 seconds to keep connection alive
        setInterval(() => {
          if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send('ping')
          }
        }, 30000)
      }
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('📥 WebSocket message:', data)
          
          // Handle different types of updates
          if (data.type === 'stats_update') {
            this.stats = { ...this.stats, ...data.stats }
          } else if (data.type === 'scene_update') {
            this.currentScene = data.scene
            this.currentSceneId = data.scene.id
          } else if (data.type === 'relationship_update') {
            this.relationships = { ...this.relationships, ...data.relationships }
          }
        } catch (error) {
          console.error('❌ Error processing WebSocket message:', error)
        }
      }
      
      websocket.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        this.websocketConnected = false
        
        // Attempt to reconnect if needed
        if (websocketReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          websocketReconnectAttempts++
          console.log(`⏳ Attempting to reconnect (${websocketReconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`)
          setTimeout(() => {
            this.connectWebSocket()
          }, 1000 * websocketReconnectAttempts) // Exponential backoff
        }
      }
      
      websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        this.websocketConnected = false
      }
    },
    
    /**
     * Disconnect WebSocket
     */
    disconnectWebSocket() {
      if (websocket) {
        websocket.close()
        websocket = null
      }
      this.websocketConnected = false
    },
    
    /**
     * Send update through WebSocket
     */
    sendWebSocketUpdate(update) {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(update))
      }
    }
  }
})