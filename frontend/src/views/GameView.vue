<template>
  <div class="game-view">
    <!-- Animated Background -->
    <div class="space-background">
      <div class="star" v-for="i in 100" :key="`space-star-${i}`" :style="getStarStyle(i)"></div>
    </div>
    
    <!-- Loading State -->
    <LoadingIndicator 
      v-if="loading" 
      :message="loadingMessage" 
      :overlay="true"
    />

    <!-- Game Over Screen -->
    <div v-else-if="isGameOver" class="game-over-screen">
      <div class="game-over-content">
        <div class="game-over-emoji">💀</div>
        <h2>Игра окончена</h2>
        <p class="game-over-reason">{{ gameOverReason }}</p>
        <div class="game-stats">
          <div class="stat-item">
            <span class="stat-label">Сцен пройдено:</span>
            <span class="stat-value">{{ gameStore.choicesMade }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Время игры:</span>
            <span class="stat-value">{{ formatGameTime() }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Стиль игры:</span>
            <span class="stat-value">{{ gameStore.decisionStyle }}</span>
          </div>
        </div>
        <button class="btn btn-primary" @click="goHome">
          🏠 Вернуться на главную
        </button>
      </div>
    </div>

    <!-- Mini Game -->
    <div v-else-if="showMiniGame" class="mini-game-wrapper">
      <MiniGame 
        @close="closeMiniGame" 
        @win="handleMiniGameWin"
      />
    </div>

    <!-- Main Game Screen -->
    <div v-else class="game-container">
      <!-- Left Sidebar - Stats -->
      <aside class="game-sidebar">
        <!-- Character Info -->
        <div class="character-info">
          <h3>Капитан Макс Велл</h3>
          <p class="ship-name">Звездолёт «Элея»</p>
          <div class="divider"></div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <div 
            v-for="(stat, key) in displayStats" 
            :key="`stat-${key}`"
            class="stat-card"
          >
            <div class="stat-header">
              <span class="stat-emoji">{{ getStatEmoji(key) }}</span>
              <span class="stat-name">{{ getStatLabel(key) }}</span>
            </div>
            <div class="stat-bar">
              <div 
                class="stat-fill" 
                :style="{ 
                  width: `${stat}%`,
                  backgroundColor: getStatColor(stat)
                }"
              ></div>
            </div>
            <div class="stat-value">{{ Math.round(stat) }}</div>
          </div>
        </div>

        <!-- Divider -->
        <div class="divider"></div>

        <!-- Relationships -->
        <div class="relationships">
          <h4 class="relationships-title">💕 Отношения</h4>
          <div 
            v-for="(relationship, charId) in gameStore.relationships" 
            :key="`relationship-${charId}`"
            class="relationship-item"
          >
            <span class="char-name">{{ getCharacterName(charId) }}</span>
            <div class="relationship-bar">
              <div 
                class="relationship-fill"
                :style="{ width: `${relationship}%` }"
              ></div>
            </div>
            <span class="relationship-value">{{ Math.round(relationship) }}</span>
          </div>
        </div>

        <!-- Info -->
        <div class="divider"></div>
        <div class="game-info">
          <p class="info-item">
            <span class="label">Выборов:</span>
            <span class="value">{{ gameStore.choicesMade }}</span>
          </p>
          <p class="info-item">
            <span class="label">Сцена:</span>
            <span class="value">{{ gameStore.currentSceneId }}</span>
          </p>
          <p class="info-item">
            <span class="label">Сложность:</span>
            <span class="value">{{ gameStore.gameDifficulty }}</span>
          </p>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="game-main">
        <!-- Scene -->
        <section class="scene">
          <div class="scene-emoji">{{ currentScene.image }}</div>
          
          <div class="scene-character">
            ► {{ currentScene.character }}
          </div>
          
          <h2 class="scene-title">{{ currentScene.title }}</h2>
          
          <p class="scene-text">{{ currentScene.text }}</p>
          
          <!-- Game Stats Summary -->
          <div class="game-stats-summary">
            <div class="stat-summary-item">
              <span class="stat-label">Сложность:</span>
              <span class="stat-value">{{ gameStore.gameDifficulty }}</span>
            </div>
            <div class="stat-summary-item">
              <span class="stat-label">Любимый персонаж:</span>
              <span class="stat-value">{{ gameStore.favoriteCharacter?.name || 'Нет' }}</span>
            </div>
            <div class="stat-summary-item">
              <span class="stat-label">Время игры:</span>
              <span class="stat-value">{{ gameStore.playtimeFormatted }}</span>
            </div>
            <div class="stat-summary-item">
              <span class="stat-label">Стиль игры:</span>
              <span class="stat-value">{{ gameStore.decisionStyle }}</span>
            </div>
          </div>
        </section>

        <!-- Choices -->
        <section class="choices">
          <div class="choices-label">Выберите действие:</div>
          
          <div class="choices-grid">
            <button 
              v-for="(choice, idx) in currentScene.choices"
              :key="`choice-${idx}`"
              class="choice-button"
              @click="makeChoice(choice)"
              @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
              :disabled="loading"
            >
              <span class="choice-arrow">▶</span>
              <span class="choice-text">{{ choice.text }}</span>
              <span v-if="choice.difficulty" class="choice-difficulty">
                {{ choice.difficulty }}
              </span>
            </button>
          </div>
        </section>

        <!-- Quick Actions -->
        <section class="quick-actions">
          <button 
            class="action-btn"
            @click="showInventory = !showInventory"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
            title="Инвентарь"
          >
            🎒 Инвентарь
          </button>
          <button 
            class="action-btn"
            @click="showAchievements = true"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
            title="Достижения"
          >
            🏆 Достижения
          </button>
          <button 
            class="action-btn"
            @click="showSaveManager = true"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
            title="Сохранения"
          >
            💾 Сохранения
          </button>

          <button 
            class="action-btn"
            @click="showStatistics = true"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
            title="Статистика"
          >
            📊 Статистика
          </button>

          <button 
            class="action-btn"
            @click="confirmExitGame"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
            title="Выход"
          >
            🚪 Выход
          </button>
        </section>

        <!-- Achievements Modal -->
        <div v-if="showAchievements" class="modal-overlay" @click="showAchievements = false">
          <div class="modal achievements-container" @click.stop>
            <component 
              :is="AchievementsList" 
              @close="showAchievements = false" 
            />
          </div>
        </div>

        <!-- Save Manager Modal -->
        <div v-if="showSaveManager" class="modal-overlay" @click="showSaveManager = false">
          <div class="modal" @click.stop>
            <component 
              :is="SaveManager" 
              @close="showSaveManager = false" 
            />
          </div>
        </div>

        <!-- Inventory Modal -->
        <div v-if="showInventory" class="modal-overlay" @click="showInventory = false">
          <div class="modal" @click.stop>
            <div class="modal-header">
              <h3>🎒 Инвентарь</h3>
              <button class="modal-close" @click="showInventory = false" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">✕</button>
            </div>
            <div class="modal-content">
              <div v-if="gameStore.inventory.length > 0" class="inventory-list">
                <div v-for="(item, idx) in gameStore.inventory" :key="`inventory-${idx}`" class="inventory-item">
                  {{ item }}
                </div>
              </div>
              <div v-else class="empty-inventory">
                Инвентарь пуст
              </div>
            </div>
          </div>
        </div>

        <!-- Statistics Panel Modal -->
        <div v-if="showStatistics" class="modal-overlay" @click="showStatistics = false">
          <div class="modal" @click.stop>
            <component 
              :is="StatisticsPanel" 
              @close="showStatistics = false" 
            />
          </div>
        </div>

        <!-- Exit Confirmation Modal -->
        <div v-if="showExitConfirm" class="modal-overlay">
          <div class="modal">
            <div class="modal-header">
              <h3>⚠️ Выход из игры</h3>
            </div>
            <div class="modal-content">
              <p>Вы уверены? Прогресс не сохранится.</p>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showExitConfirm = false" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
                Отмена
              </button>
              <button class="btn btn-primary" @click="exitGame" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
                Выход
              </button>
            </div>
          </div>
        </div>
        <!-- Achievement Notification -->
        <component 
          :is="AchievementNotification"
          v-if="recentAchievement"
          :achievement="recentAchievement"
          :show="showAchievementNotification"
          @dismiss="dismissAchievement"
        />
      </main>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../store/game'
import { useUiStore } from '../store/ui'
import { useAchievementsStore } from '../store/achievements'

// Lazy load components that are not always visible
const AchievementNotification = () => import('../components/AchievementNotification.vue')
const AchievementsList = () => import('../components/AchievementsList.vue')
const SaveManager = () => import('../components/SaveManager.vue')
const MiniGame = () => import('../components/MiniGame.vue')

export default defineComponent({
  name: 'GameView',

  components: {
    AchievementNotification,
    AchievementsList,
    SaveManager,
    StatisticsPanel: () => import('../components/StatisticsPanel.vue'),
    LoadingIndicator: () => import('../components/LoadingIndicator.vue'),
    MiniGame
  },

  setup() {
    const router = useRouter()
    const gameStore = useGameStore()
    const uiStore = useUiStore()
    const achievementsStore = useAchievementsStore()

    return {
      router,
      gameStore,
      uiStore,
      achievementsStore
    }
  },

  data() {
    return {
      loading: false,
      loadingMessage: 'Инициализация игры...',
      showInventory: false,
      showExitConfirm: false,
      showAchievements: false,
      showSaveManager: false,
      showStatistics: false,
      showMiniGame: false,
      isGameOver: false,
      gameOverReason: '',
      startTime: null,
      recentAchievement: null,
      showAchievementNotification: false,
      // Pre-generate star styles to reduce computations
      starStyles: this.generateStarStyles(100),
      statEmojis: {
        health: '❤️',
        morale: '💪',
        knowledge: '🧠',
        team: '👥',
        danger: '⚠️',
        security: '🔒',
        fuel: '⛽',
        money: '💰',
        psychic: '✨',
        trust: '🤝'
      },
      statLabels: {
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
      },
      characterNames: {
        sara_nova: 'Сара Нова',
        grisha_romanov: 'Гриша Романов',
        li_zheng: 'Ли Чжэнь'
      }
    }
  },

  computed: {
    /**
     * Get current scene data with fallback
     */
    currentScene() {
      return this.gameStore.currentScene || {
        id: 'start',
        title: 'Пробуждение на Элее',
        text: 'Загрузка...',
        image: '🚀',
        character: 'Система',
        choices: []
      }
    },
    
    /**
     * Get display stats for UI
     */
    displayStats() {
      // Return a sorted version of stats for consistent UI
      const sortedStats = {}
      const statOrder = [
        'health', 'morale', 'knowledge', 'team', 
        'danger', 'security', 'fuel', 'money', 
        'psychic', 'trust'
      ]
      
      statOrder.forEach(stat => {
        if (this.gameStore.stats.hasOwnProperty(stat)) {
          sortedStats[stat] = this.gameStore.stats[stat]
        }
      })
      
      return sortedStats
    }
  },

  methods: {
    /**
     * Pre-generate star styles to reduce computations
     */
    generateStarStyles(count) {
      const styles = []
      for (let i = 0; i < count; i++) {
        const size = Math.random() * 3 + 1
        const top = Math.random() * 100
        const left = Math.random() * 100
        const opacity = Math.random() * 0.8 + 0.2
        const animationDelay = Math.random() * 5
        
        styles.push({
          width: `${size}px`,
          height: `${size}px`,
          top: `${top}%`,
          left: `${left}%`,
          opacity: opacity,
          animationDelay: `${animationDelay}s`
        })
      }
      return styles
    },
    
    /**
     * Генерировать стиль для звезды (fallback method)
     */
    getStarStyle(index) {
      return this.starStyles[index] || {}
    },
    
    /**
     * Initialize audio system for the game view
     */
    async initializeAudio() {
      if (!this.$utils || !this.$utils.$audio) {
        console.warn('[GameView] Audio utilities are not available')
        return
      }

      try {
        await this.$utils.$audio.createUserContext()

        if (this.$utils.$audio.soundEffects.size === 0) {
          await this.$utils.$audio.preloadGameAudio()
        }

        await this.$utils.$audio.playBackgroundMusic()
        this.$utils.log('info', 'Audio system initialized')
      } catch (error) {
        this.$utils.log('warning', 'Failed to initialize audio system', error)
      }
    },
    
    /**
     * Сделать выбор
     */
    async makeChoice(choice) {
      // Special handling for mini-game scene
      if (this.gameStore.currentSceneId === 'start_hack') {
        this.showMiniGame = true
        return
      }
      
      // Play sound effect
      this.$utils.$audio.playSoundEffect('choiceMade')
      
      this.loading = true
      this.loadingMessage = 'Загрузка следующей сцены...'

      try {
        // Проверяем достижения после выбора
        const unlocked = this.achievementsStore.checkAchievements(this.gameStore)
        this.$utils.log('info', 'Выбор сделан', choice.text)
        
        // Проверяем, является ли выбор дипломатичным
        if (choice.text.includes('договор') || choice.text.includes('мир') || 
            choice.text.includes('переговор') || choice.text.includes('довер')) {
          this.achievementsStore.recordDiplomaticChoice()
        }
        
        // Показываем уведомления о новых достижениях
        unlocked.forEach(achievement => {
          if (achievement) {
            this.showAchievement(achievement)
          }
        })
        
        // Отправляем выбор в store
        const response = await this.gameStore.makeChoice(
          choice.next,
          choice.stats || {}
        )

        // Проверяем game over
        if (response.status === 'game_over') {
          this.isGameOver = true
          this.gameOverReason = response.reason
          this.$root.showNotification('Игра окончена: ' + response.reason, 'warning')
          this.$utils.$audio.playSoundEffect('gameOver')
          
          // Проверяем достижения в конце игры
          const endGameAchievements = this.achievementsStore.checkEndGameAchievements(this.gameStore)
          endGameAchievements.forEach(achievement => {
            if (achievement) {
              this.showAchievement(achievement)
            }
          })
        } else {
          // Play scene change sound
          this.$utils.$audio.playSoundEffect('sceneChange')
        }

        this.$utils.log('success', 'Сцена загружена')
      } catch (error) {
        this.$utils.log('error', 'Ошибка при выборе', error)
        this.$root.showNotification('Ошибка при загрузке сцены: ' + error.message, 'error')
        
        // Play error sound
        this.$utils.$audio.playSoundEffect('gameOver')
      } finally {
        this.loading = false
      }
    },

    /**
     * Получить эмодзи статистики
     */
    getStatEmoji(key) {
      return this.statEmojis[key] || '📊'
    },

    /**
     * Получить название статистики
     */
    getStatLabel(key) {
      return this.statLabels[key] || key
    },

    /**
     * Получить цвет статистики
     */
    getStatColor(value) {
      return this.$utils.getStatColor(value)
    },

    /**
     * Получить имя персонажа
     */
    getCharacterName(charId) {
      return this.characterNames[charId] || charId
    },

    /**
     * Подтверждение выхода
     */
    confirmExitGame() {
      this.showExitConfirm = true
    },

    /**
     * Выход из игры
     */
    async exitGame() {
      this.showExitConfirm = false
      this.$utils.log('info', 'Выход из игры')
      
      // Сбрасываем store
      this.gameStore.resetGame()
      
      // Переходим на главную
      await this.$router.push('/')
    },

    /**
     * Возврат на главную
     */
    async goHome() {
      this.gameStore.resetGame()
      await this.$router.push('/')
    },

    /**
     * Форматирование времени игры
     */
    formatGameTime() {
      if (!this.startTime) return '0:00'
      
      const elapsed = Math.floor((Date.now() - this.startTime) / 1000)
      const minutes = Math.floor(elapsed / 60)
      const seconds = elapsed % 60
      
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    },

    /**
     * Показать уведомление о достижении
     */
    showAchievement(achievement) {
      this.recentAchievement = achievement
      this.showAchievementNotification = true
      this.$utils.$audio.playSoundEffect('achievementUnlocked')
      
      // Автоматически скрыть через 5 секунд
      setTimeout(() => {
        this.dismissAchievement()
      }, 5000)
    },

    /**
     * Скрыть уведомление о достижении
     */
    dismissAchievement() {
      this.showAchievementNotification = false
      setTimeout(() => {
        this.recentAchievement = null
      }, 300)
    },

    /**
     * Проверить достижения
     */
    checkAchievements() {
      const previouslyUnlocked = new Set(this.achievementsStore.unlockedAchievements)
      this.achievementsStore.checkAchievements(this.gameStore)
      
      // Показать уведомления о новых достижениях
      this.achievementsStore.unlockedAchievementsList.forEach(achievement => {
        if (!previouslyUnlocked.has(achievement.id)) {
          this.showAchievement(achievement)
        }
      })
    },
    
    /**
     * Handle mini-game win
     */
    handleMiniGameWin(reward) {
      this.showMiniGame = false
      // Add reward to player's money
      this.gameStore.stats.money += reward
      // Show notification
      this.$root.showNotification(`Поздравляем! Вы получили ${reward} кредитов за успешный взлом.`, 'success')
      // Play win sound
      this.$utils.$audio.playSoundEffect('achievementUnlocked')
      // Continue to success scene
      this.makeChoice({ next: 'hack_success', stats: { money: reward } })
    },
    
    /**
     * Close mini-game
     */
    closeMiniGame() {
      this.showMiniGame = false
      // Continue to failure scene
      this.makeChoice({ next: 'hack_failure', stats: { security: -20, danger: 15 } })
    }
  },

  async mounted() {
    this.$utils.log('info', 'GameView mounted')

    await this.initializeAudio()
    
    this.startTime = Date.now()

    // Проверяем, начата ли игра
    if (!this.gameStore.isGameStarted) {
      this.$utils.log('warning', 'Игра не начата, перенаправляем на главную')
      await this.$router.push('/')
      return
    }

    this.$utils.log('success', 'Игра готова', {
      playerId: this.gameStore.playerId,
      scene: this.gameStore.currentSceneId
    })
  },

  beforeUnmount() {
    this.$utils.log('info', 'GameView unmounted')
  }
})
</script>

<style scoped>
/* ======================== GENERAL ======================== */

.game-view {
  width: 100%;
  height: calc(100vh - 200px);
  background: linear-gradient(135deg, #0f172a 0%, #44260e 50%, #0f172a 100%);
  color: #e0e7ff;
  position: relative;
  overflow: hidden;
}

/* ======================== SPACE BACKGROUND ======================== */

.space-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;
}

.star {
  position: absolute;
  background-color: #fff;
  border-radius: 50%;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

/* ======================== LOADING SCREEN ======================== */

.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #44260e 50%, #0f172a 100%);
  position: relative;
  overflow: hidden;
}

.loading-content {
  text-align: center;
  background: rgba(30, 41, 59, 0.8);
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  border: 2px solid #fbbf24;
  position: relative;
  z-index: 2;
}

.loading-spinner {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: float 2s ease-in-out infinite, spin 3s linear infinite;
}

.loading-content h2 {
  color: #fbbf24;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
}

.loading-content p {
  color: #d1d5db;
  font-size: 1.1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ======================== GAME OVER SCREEN ======================== */

.game-over-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: radial-gradient(ellipse at center, rgba(15, 23, 42, 0.8) 0%, rgba(68, 38, 14, 0.9) 100%);
}

.game-over-content {
  background: rgba(30, 41, 59, 0.9);
  border: 2px solid #ef4444;
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  max-width: 500px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.5s ease-out;
}

.game-over-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #ef4444, #fbbf24, #ef4444);
}

.game-over-emoji {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
}

.game-over-content h2 {
  color: #fbbf24;
  font-size: 2rem;
  margin-bottom: 1rem;
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
}

.game-over-reason {
  color: #d1d5db;
  font-size: 1.1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.game-stats {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #44260e;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #9ca3af;
}

.stat-value {
  color: #fbbf24;
  font-weight: bold;
  font-size: 1.1rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ======================== GAME CONTAINER ======================== */

.game-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  padding: 2rem;
  height: 100%;
  overflow: hidden;
}

/* ======================== SIDEBAR ======================== */

.game-sidebar {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid #92400e;
  border-radius: 0.5rem;
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

.character-info {
  margin-bottom: 1.5rem;
}

.character-info h3 {
  color: #fbbf24;
  font-size: 1.25rem;
  margin: 0 0 0.5rem 0;
}

.ship-name {
  color: #fcd34d;
  font-size: 0.9rem;
  margin: 0;
}

.divider {
  height: 1px;
  background: #44260e;
  margin: 1.5rem 0;
}

/* Stats Grid */

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.375rem;
  padding: 0.75rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.stat-card:hover {
  transform: translateY(-3px);
  border-color: #fbbf24;
  box-shadow: 0 5px 15px rgba(251, 191, 36, 0.2);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.stat-emoji {
  font-size: 1.25rem;
  animation: pulse 2s infinite;
}

.stat-name {
  color: #d1d5db;
  font-weight: 600;
  flex: 1;
}

.stat-bar {
  width: 100%;
  height: 0.375rem;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 0.2rem;
  overflow: hidden;
  margin-bottom: 0.25rem;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
}

.stat-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 0.2rem;
}

.stat-value {
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: right;
  font-weight: 600;
}

/* Relationships */

.relationships {
  margin-bottom: 1.5rem;
}

.relationships-title {
  color: #fbbf24;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.relationship-item {
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
  background: rgba(17, 24, 39, 0.5);
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

.relationship-item:hover {
  background: rgba(17, 24, 39, 0.7);
  transform: translateX(3px);
}

.char-name {
  color: #fcd34d;
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 600;
}

.relationship-bar {
  width: 100%;
  height: 0.25rem;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 0.15rem;
  overflow: hidden;
  margin-bottom: 0.2rem;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
}

.relationship-fill {
  height: 100%;
  background: linear-gradient(90deg, #ec4899 0%, #f43f5e 100%);
  transition: width 0.3s ease;
  border-radius: 0.15rem;
}

.relationship-value {
  color: #9ca3af;
  float: right;
  font-weight: 600;
}

/* Game Info */

.game-info {
  font-size: 0.85rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.label {
  color: #9ca3af;
}

.value {
  color: #fbbf24;
  font-weight: 600;
}

/* ======================== MAIN GAME AREA ======================== */

.game-main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

/* Scene */

.scene {
  background: rgba(30, 41, 59, 0.8);
  border: 2px solid #fbbf24;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.scene:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(251, 191, 36, 0.3);
}

.scene-emoji {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
}

.scene-character {
  color: #fbbf24;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.scene-title {
  color: #fbbf24;
  font-size: 1.75rem;
  margin: 0 0 1rem 0;
  font-weight: bold;
  text-align: center;
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
  position: relative;
  padding-bottom: 0.5rem;
}

.scene-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #fbbf24, transparent);
}

.scene-text {
  color: #e5e7eb;
  font-size: 1.05rem;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  text-align: justify;
  font-family: 'Georgia', serif;
  padding: 1rem 0;
}

/* Game Stats Summary */
.game-stats-summary {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #44260e;
  flex-wrap: wrap;
}

.stat-summary-item {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}

.stat-label {
  color: #9ca3af;
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
}

.stat-value {
  color: #fbbf24;
  font-weight: 600;
  font-size: 0.875rem;
}

/* Choices */

.choices {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid #92400e;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.choices-label {
  color: #fbbf24;
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.choices-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.choice-button {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.choice-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: 0.5s;
}

.choice-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #c65d00 0%, #d84315 100%);
  transform: translateX(5px);
  box-shadow: 0 0 20px rgba(217, 119, 6, 0.4);
}

.choice-button:hover:not(:disabled)::before {
  left: 100%;
}

.choice-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.choice-arrow {
  font-size: 1rem;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.choice-button:hover:not(:disabled) .choice-arrow {
  transform: translateX(3px);
}

.choice-text {
  flex: 1;
}

.choice-difficulty {
  font-size: 0.75rem;
  opacity: 0.8;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

/* Quick Actions */

.quick-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  background: transparent;
  border: 1px solid #92400e;
  color: #fbbf24;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  flex: 1;
  min-width: 120px;
}

.action-btn:hover {
  background: rgba(251, 191, 36, 0.1);
  border-color: #fbbf24;
}

/* ======================== BUTTONS ======================== */

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
}

.btn-secondary {
  background: transparent;
  border: 1px solid #fbbf24;
  color: #fbbf24;
}

.btn-secondary:hover {
  background: rgba(251, 191, 36, 0.1);
}

/* ======================== MODALS ======================== */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #92400e;
  border-radius: 0.5rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #44260e;
}

.modal-header h3 {
  color: #fbbf24;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: #fbbf24;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.modal-close:hover {
  color: #ef4444;
}

.modal-content {
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.inventory-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.inventory-item {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  padding: 1rem;
  border-radius: 0.375rem;
  text-align: center;
  color: #fbbf24;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.inventory-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.inventory-item:hover {
  transform: translateY(-5px);
  border-color: #fbbf24;
  box-shadow: 0 10px 20px rgba(251, 191, 36, 0.3);
}

.inventory-item:hover::before {
  left: 100%;
}

.empty-inventory {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
  font-style: italic;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #44260e;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

/* ======================== RESPONSIVE ======================== */

@media (max-width: 1024px) {
  .game-container {
    grid-template-columns: 1fr;
  }

  .game-sidebar {
    max-height: 300px;
  }

  .game-main {
    max-height: calc(100vh - 500px);
  }
}

@media (max-width: 768px) {
  .game-view {
    height: auto;
  }

  .game-container {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }

  .game-sidebar {
    max-height: none;
  }

  .game-main {
    max-height: none;
    gap: 1rem;
  }

  .scene {
    padding: 1.5rem;
  }

  .scene-emoji {
    font-size: 2.5rem;
  }

  .scene-title {
    font-size: 1.5rem;
  }

  .choices {
    padding: 1rem;
  }

  .choice-button {
    padding: 0.75rem;
  }

  .quick-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }

  .game-stats-summary {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stat-summary-item {
    width: 100%;
  }
}
</style>