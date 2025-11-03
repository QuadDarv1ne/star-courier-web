<!-- Statistics Panel Component -->
<template>
  <div class="statistics-panel">
    <div class="modal-header">
      <h3>📊 Статистика игры</h3>
      <button class="modal-close" @click="$emit('close')" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
        ✕
      </button>
    </div>

    <div class="modal-content">
      <!-- Player Overview -->
      <div class="stats-section">
        <h4>Обзор игрока</h4>
        <div class="player-overview">
          <div class="overview-item">
            <span class="label">Стиль принятия решений:</span>
            <span class="value">{{ gameStore.decisionStyle }}</span>
          </div>
          <div class="overview-item">
            <span class="label">Средний уровень параметров:</span>
            <span class="value">{{ gameStore.averageStats }}%</span>
          </div>
          <div class="overview-item">
            <span class="label">Сильная сторона:</span>
            <span class="value">{{ gameStore.strongestStat }}</span>
          </div>
          <div class="overview-item">
            <span class="label">Сложность игры:</span>
            <span class="value">{{ gameStore.gameDifficulty }}</span>
          </div>
        </div>
      </div>

      <!-- Time Tracking -->
      <div class="stats-section">
        <h4>Время в сценах</h4>
        <div v-if="Object.keys(sceneTimes).length === 0" class="no-data">
          Нет данных
        </div>
        <div v-else class="scene-times">
          <div 
            v-for="(time, sceneId) in sceneTimes" 
            :key="`scene-time-${sceneId}`"
            class="scene-time-item"
          >
            <span class="scene-name">{{ getSceneTitle(sceneId) }}</span>
            <span class="scene-time">{{ formatTime(time) }}</span>
          </div>
        </div>
      </div>

      <!-- Decision Patterns -->
      <div class="stats-section">
        <h4>Стили принятия решений</h4>
        <div class="decision-patterns">
          <div class="pattern-item">
            <div class="pattern-bar">
              <div 
                class="pattern-fill" 
                :style="{ width: `${(gameStore.decisionPatterns.aggressive / maxPattern) * 100}%` }"
              ></div>
            </div>
            <div class="pattern-info">
              <span class="pattern-name">Агрессивный</span>
              <span class="pattern-value">{{ gameStore.decisionPatterns.aggressive }}</span>
            </div>
          </div>
          
          <div class="pattern-item">
            <div class="pattern-bar">
              <div 
                class="pattern-fill" 
                :style="{ width: `${(gameStore.decisionPatterns.diplomatic / maxPattern) * 100}%` }"
              ></div>
            </div>
            <div class="pattern-info">
              <span class="pattern-name">Дипломатичный</span>
              <span class="pattern-value">{{ gameStore.decisionPatterns.diplomatic }}</span>
            </div>
          </div>
          
          <div class="pattern-item">
            <div class="pattern-bar">
              <div 
                class="pattern-fill" 
                :style="{ width: `${(gameStore.decisionPatterns.analytical / maxPattern) * 100}%` }"
              ></div>
            </div>
            <div class="pattern-info">
              <span class="pattern-name">Аналитический</span>
              <span class="pattern-value">{{ gameStore.decisionPatterns.analytical }}</span>
            </div>
          </div>
          
          <div class="pattern-item">
            <div class="pattern-bar">
              <div 
                class="pattern-fill" 
                :style="{ width: `${(gameStore.decisionPatterns.caring / maxPattern) * 100}%` }"
              ></div>
            </div>
            <div class="pattern-info">
              <span class="pattern-name">Заботливый</span>
              <span class="pattern-value">{{ gameStore.decisionPatterns.caring }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stat History -->
      <div class="stats-section">
        <h4>История параметров</h4>
        <div class="stat-history">
          <div 
            v-for="(history, stat) in statHistories" 
            :key="`stat-history-${stat}`"
            class="stat-history-item"
          >
            <div class="stat-header">
              <span class="stat-name">{{ getStatLabel(stat) }}</span>
              <span class="stat-values">{{ history.min }}% → {{ history.max }}%</span>
            </div>
            <div class="stat-range">
              <div class="stat-min">{{ history.min }}%</div>
              <div class="stat-bar">
                <div 
                  class="stat-current" 
                  :style="{ left: `${(gameStore.stats[stat] - history.min) / (history.max - history.min) * 100}%` }"
                ></div>
              </div>
              <div class="stat-max">{{ history.max }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useGameStore } from '../store/game'

export default defineComponent({
  name: 'StatisticsPanel',

  setup() {
    const gameStore = useGameStore()
    return { gameStore }
  },

  computed: {
    sceneTimes() {
      // Sort scenes by time spent (descending)
      const sorted = Object.entries(this.gameStore.sceneTimeTracking || {})
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10) // Show top 10 scenes
      return Object.fromEntries(sorted)
    },
    
    statHistories() {
      // Filter out stats with no history
      const histories = {}
      Object.entries(this.gameStore.statHistory || {}).forEach(([stat, history]) => {
        if (history.min !== history.max) {
          histories[stat] = history
        }
      })
      return histories
    },
    
    maxPattern() {
      const patterns = this.gameStore.decisionPatterns || { aggressive: 0, diplomatic: 0, analytical: 0, caring: 0 }
      return Math.max(
        patterns.aggressive,
        patterns.diplomatic,
        patterns.analytical,
        patterns.caring,
        1 // Ensure we don't divide by zero
      )
    }
  },

  methods: {
    getSceneTitle(sceneId) {
      const sceneTitles = {
        'start': 'Пробуждение на Элее',
        'command_center': 'Центр управления Элеи',
        'mystery_contact': 'Голос в эфире',
        'artifact_vault': 'Хранилище артефакта',
        'sigma_station': 'Станция Сигма-7',
        'li_zheng_secret': 'Тайна Ли Чжэнь',
        'li_alliance': 'Союз навигатора',
        'ancient_awakening': 'Пробуждение Древних',
        'hide_artifact': 'Хранитель секретов',
        'artifact_destruction': 'Жертва',
        'defend_station': 'Боевая победа',
        'artifact_guard': 'Охрана артефакта',
        'crew_meeting': 'Совет экипажа',
        'team_divided': 'Раздор в команде',
        'secret_mission': 'Секретная миссия'
      }
      return sceneTitles[sceneId] || sceneId
    },
    
    getStatLabel(stat) {
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
      return statLabels[stat] || stat
    },
    
    formatTime(milliseconds) {
      const seconds = Math.floor(milliseconds / 1000)
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }
  }
})
</script>

<style scoped>
.statistics-panel {
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #92400e;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #44260e;
}

.modal-header h3 {
  color: #fbbf24;
  margin: 0;
  flex: 1;
}

.modal-close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #ef4444;
}

.modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-section {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.stats-section h4 {
  color: #fbbf24;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.player-overview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.overview-item {
  display: flex;
  flex-direction: column;
}

.label {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.value {
  color: #fbbf24;
  font-weight: 600;
}

.no-data {
  color: #9ca3af;
  text-align: center;
  padding: 1rem;
  font-style: italic;
}

.scene-times {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.scene-time-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #78350f;
  border-radius: 0.25rem;
  transition: all 0.3s;
}

.scene-time-item:hover {
  border-color: #fbbf24;
  background: rgba(30, 41, 59, 0.7);
}

.scene-name {
  color: #d1d5db;
}

.scene-time {
  color: #fbbf24;
  font-weight: 600;
}

.decision-patterns {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pattern-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pattern-bar {
  background: rgba(0, 0, 0, 0.2);
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.pattern-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
  transition: width 0.3s ease;
}

.pattern-info {
  display: flex;
  justify-content: space-between;
}

.pattern-name {
  color: #d1d5db;
}

.pattern-value {
  color: #fbbf24;
  font-weight: 600;
}

.stat-history {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat-history-item {
  padding: 1rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #78350f;
  border-radius: 0.25rem;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.stat-name {
  color: #fbbf24;
  font-weight: 600;
}

.stat-values {
  color: #9ca3af;
  font-size: 0.875rem;
}

.stat-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-min, .stat-max {
  color: #9ca3af;
  font-size: 0.75rem;
  width: 30px;
}

.stat-bar {
  flex: 1;
  height: 6px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
  position: relative;
}

.stat-current {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #fbbf24;
  border-radius: 50%;
  border: 2px solid #0f172a;
}

@media (max-width: 768px) {
  .player-overview {
    grid-template-columns: 1fr;
  }
  
  .stat-range {
    flex-direction: column;
    align-items: stretch;
    gap: 0.25rem;
  }
  
  .stat-min, .stat-max {
    width: auto;
    text-align: center;
  }
}
</style>