<template>
  <div class="settings-panel">
    <div class="modal-header">
      <h3>⚙️ Настройки</h3>
      <div class="settings-stats" v-if="uiStore">
        <span class="stat-item">FPS: {{ uiPerformance.fps }}</span>
        <span class="stat-item">Ср. время: {{ uiPerformance.averageRenderTime.toFixed(1) }}ms</span>
      </div>
      <button class="modal-close" @click="$emit('close')" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
        ✕
      </button>
    </div>

    <div class="modal-content">
      <!-- Audio Settings -->
      <div class="settings-section">
        <h4>🔊 Аудио</h4>
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="uiStore.soundEnabled"
              @change="toggleSound"
            >
            Звуковые эффекты
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="uiStore.musicEnabled"
              @change="toggleMusic"
            >
            Музыка
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            Громкость:
            <input 
              type="range" 
              min="0" 
              max="100" 
              :value="audioVolume"
              @input="setAudioVolume"
              class="volume-slider"
            >
            <span class="volume-value">{{ audioVolume }}%</span>
          </label>
        </div>
      </div>
      
      <!-- Display Settings -->
      <div class="settings-section">
        <h4>🖥️ Отображение</h4>
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="uiStore.isDarkMode"
              @change="toggleDarkMode"
            >
            Тёмная тема
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            Размер текста:
            <select 
              :value="uiStore.settings.textSize"
              @change="setTextSize"
              class="text-size-select"
            >
              <option value="small">Маленький</option>
              <option value="medium">Средний</option>
              <option value="large">Большой</option>
            </select>
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="uiStore.settings.animationsEnabled"
              @change="toggleAnimations"
            >
            Анимации
          </label>
        </div>
      </div>
      
      <!-- Game Settings -->
      <div class="settings-section">
        <h4>🎮 Игра</h4>
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="uiStore.settings.autoSaveEnabled"
              @change="toggleAutoSave"
            >
            Автосохранение
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            Интервал автосохранения:
            <select 
              :value="uiStore.settings.autoSaveInterval"
              @change="setAutoSaveInterval"
              :disabled="!uiStore.settings.autoSaveEnabled"
              class="interval-select"
            >
              <option value="60000">1 минута</option>
              <option value="120000">2 минуты</option>
              <option value="300000">5 минут</option>
              <option value="600000">10 минут</option>
              <option value="1800000">30 минут</option>
            </select>
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="uiStore.settings.showTutorial"
              @change="toggleTutorial"
            >
            Показывать обучение
          </label>
        </div>
      </div>
      
      <!-- Performance Settings -->
      <div class="settings-section">
        <h4>⚡ Производительность</h4>
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="cacheEnabled"
              @change="toggleCache"
            >
            Кэширование данных
          </label>
        </div>
        
        <div class="setting-row">
          <button 
            class="btn btn-secondary" 
            @click="clearAllCaches"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          >
            Очистить кэш
          </button>
        </div>
        
        <div class="setting-row">
          <button 
            class="btn btn-secondary" 
            @click="clearPerformanceMetrics"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          >
            Сбросить метрики производительности
          </button>
        </div>
      </div>
      
      <!-- Reset Settings -->
      <div class="settings-section">
        <h4>🔄 Сброс</h4>
        <div class="setting-row">
          <button 
            class="btn btn-danger" 
            @click="resetSettings"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          >
            Сбросить все настройки
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useUiStore } from '../store/ui'
import { useGameStore } from '../store/game'

export default defineComponent({
  name: 'SettingsPanel',

  emits: ['close'],

  setup() {
    const uiStore = useUiStore()
    const gameStore = useGameStore()
    
    return {
      uiStore,
      gameStore
    }
  },

  data() {
    return {
      audioVolume: 80
    }
  },

  computed: {
    cacheEnabled() {
      return true // Always enabled in this implementation
    },
    
    uiPerformance() {
      return this.uiStore.uiPerformance || {
        fps: 0,
        averageRenderTime: 0
      }
    }
  },

  methods: {
    toggleSound(event) {
      const enabled = event.target.checked
      this.uiStore.soundEnabled = enabled
      this.uiStore.saveUiSettings()
    },
    
    toggleMusic(event) {
      const enabled = event.target.checked
      this.uiStore.musicEnabled = enabled
      this.uiStore.saveUiSettings()
    },
    
    setAudioVolume(event) {
      this.audioVolume = parseInt(event.target.value)
      // In a real implementation, this would control actual audio volume
    },
    
    toggleDarkMode(event) {
      const enabled = event.target.checked
      this.uiStore.isDarkMode = enabled
      this.uiStore.saveUiSettings()
    },
    
    setTextSize(event) {
      const size = event.target.value
      this.uiStore.setTextSize(size)
    },
    
    toggleAnimations(event) {
      const enabled = event.target.checked
      this.uiStore.settings.animationsEnabled = enabled
      this.uiStore.saveUiSettings()
    },
    
    toggleAutoSave(event) {
      const enabled = event.target.checked
      this.uiStore.settings.autoSaveEnabled = enabled
      this.uiStore.saveUiSettings()
      
      // Update game store as well
      if (this.gameStore) {
        this.gameStore.autoSaveEnabled = enabled
        if (enabled) {
          this.gameStore.startAutoSave()
        } else {
          this.gameStore.stopAutoSave()
        }
      }
    },
    
    setAutoSaveInterval(event) {
      const interval = parseInt(event.target.value)
      this.uiStore.settings.autoSaveInterval = interval
      this.uiStore.saveUiSettings()
      
      // Update game store as well
      if (this.gameStore) {
        this.gameStore.setAutoSaveInterval(interval)
      }
    },
    
    toggleTutorial(event) {
      const enabled = event.target.checked
      this.uiStore.settings.showTutorial = enabled
      this.uiStore.saveUiSettings()
    },
    
    toggleCache(event) {
      // Cache is always enabled in this implementation
      // In a real implementation, this would control caching behavior
    },
    
    clearAllCaches() {
      if (confirm('Вы уверены, что хотите очистить весь кэш?')) {
        this.gameStore.clearCaches()
        this.$api.clearApiCache()
        this.$root.showNotification('Все кэши очищены', 'success')
      }
    },
    
    clearPerformanceMetrics() {
      this.uiStore.clearPerformanceMetrics()
      this.$root.showNotification('Метрики производительности сброшены', 'success')
    },
    
    resetSettings() {
      if (confirm('Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?')) {
        this.uiStore.resetUiSettings()
        this.audioVolume = 80
        this.$root.showNotification('Настройки сброшены', 'success')
      }
    }
  }
})
</script>

<style scoped>
.settings-panel {
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #92400e;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 600px;
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

.settings-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #9ca3af;
}

.stat-item {
  background: rgba(17, 24, 39, 0.7);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
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

.settings-section {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.modal-content h4 {
  color: #fbbf24;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.setting-row {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.setting-row:last-child {
  margin-bottom: 0;
}

.setting-label {
  color: #d1d5db;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  width: 100%;
}

.setting-label input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
}

.setting-label select,
.setting-label input[type="range"] {
  margin-left: auto;
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid #78350f;
  color: #d1d5db;
  padding: 0.5rem;
  border-radius: 0.25rem;
}

.volume-slider {
  width: 100px;
}

.volume-value {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-left: 0.5rem;
  min-width: 3rem;
  text-align: right;
}

.text-size-select,
.interval-select {
  margin-left: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  font-size: 0.875rem;
  width: 100%;
  margin-top: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  border: 1px solid #fbbf24;
  color: #fbbf24;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(251, 191, 36, 0.1);
  transform: translateY(-2px);
}

.btn-danger {
  background: transparent;
  border: 1px solid #ef4444;
  color: #ef4444;
}

.btn-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .setting-label {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .setting-label select,
  .setting-label input[type="range"] {
    margin-left: 0;
    width: 100%;
  }
  
  .volume-value {
    margin-left: 0;
    text-align: left;
  }
  
  .settings-stats {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>