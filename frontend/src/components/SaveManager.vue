<!-- Save Manager Component -->
<template>
  <div class="save-manager">
    <div class="modal-header">
      <h3>💾 Управление сохранениями</h3>
      <button class="modal-close" @click="$emit('close')" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
        ✕
      </button>
    </div>

    <div class="modal-content">
      <!-- Auto-save settings -->
      <div class="save-settings">
        <h4>Настройки автосохранения</h4>
        <div class="setting-row">
          <label class="setting-label">
            <input 
              type="checkbox" 
              :checked="gameStore.autoSaveEnabled"
              @change="toggleAutoSave"
            >
            Включить автосохранение
          </label>
        </div>
        
        <div class="setting-row">
          <label class="setting-label">
            Интервал автосохранения:
            <select 
              :value="gameStore.autoSaveInterval"
              @change="setAutoSaveInterval"
              :disabled="!gameStore.autoSaveEnabled"
            >
              <option value="60000">1 минута</option>
              <option value="120000">2 минуты</option>
              <option value="300000">5 минут</option>
              <option value="600000">10 минут</option>
              <option value="1800000">30 минут</option>
            </select>
          </label>
        </div>
        
        <div class="setting-row" v-if="gameStore.lastAutoSave">
          <span class="last-save">
            Последнее автосохранение: {{ formatLastSaveTime(gameStore.lastAutoSave) }}
          </span>
        </div>
      </div>
      
      <!-- Manual save -->
      <div class="manual-save">
        <h4>Ручное сохранение</h4>
        <div class="save-input">
          <input 
            v-model="saveName"
            type="text" 
            placeholder="Название сохранения"
            class="save-name-input"
          >
          <button 
            class="btn btn-primary" 
            @click="saveGame"
            :disabled="!gameStore.isGameStarted"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          >
            Сохранить
          </button>
        </div>
      </div>
      
      <!-- Saved games list -->
      <div class="saved-games">
        <h4>Сохранённые игры</h4>
        <div v-if="savedGames.length === 0" class="no-saves">
          Нет сохранённых игр
        </div>
        
        <div v-else class="saves-list">
          <div 
            v-for="save in savedGames" 
            :key="save.id"
            class="save-item"
          >
            <div class="save-info">
              <div class="save-name">{{ save.name }}</div>
              <div class="save-meta">
                <span class="save-date">{{ formatDate(save.timestamp) }}</span>
                <span class="save-time">{{ formatPlaytime(save.playtime) }}</span>
                <span class="save-scene">{{ getSceneTitle(save.currentSceneId) }}</span>
              </div>
            </div>
            
            <div class="save-actions">
              <button 
                class="btn btn-small btn-secondary" 
                @click="loadSave(save.id)"
                @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
              >
                Загрузить
              </button>
              <button 
                class="btn btn-small btn-danger" 
                @click="deleteSave(save.id)"
                @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Export/Import -->
      <div class="export-import">
        <h4>Экспорт/Импорт</h4>
        <div class="export-import-buttons">
          <button 
            class="btn btn-secondary" 
            @click="exportGame"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          >
            Экспорт всех сохранений
          </button>
          <button 
            class="btn btn-secondary" 
            @click="triggerImport"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          >
            Импорт сохранений
          </button>
          <input 
            ref="fileInput"
            type="file" 
            accept=".json"
            @change="importGame"
            class="hidden-file-input"
          >
        </div>
      </div>
      
      <!-- Clear all saves -->
      <div class="clear-saves">
        <button 
          class="btn btn-danger" 
          @click="clearAllSaves"
          :disabled="savedGames.length === 0"
          @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
        >
          Удалить все сохранения
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useGameStore } from '../store/game'

export default defineComponent({
  name: 'SaveManager',

  setup() {
    const gameStore = useGameStore()
    return { gameStore }
  },

  data() {
    return {
      saveName: '',
      savedGames: []
    }
  },

  mounted() {
    this.loadSavedGames()
  },

  methods: {
    loadSavedGames() {
      this.savedGames = this.gameStore.loadAllSavedGames()
    },
    
    toggleAutoSave(event) {
      const enabled = event.target.checked
      this.gameStore.autoSaveEnabled = enabled
      if (enabled) {
        this.gameStore.startAutoSave()
      } else {
        this.gameStore.stopAutoSave()
      }
    },
    
    setAutoSaveInterval(event) {
      const interval = parseInt(event.target.value)
      this.gameStore.setAutoSaveInterval(interval)
    },
    
    saveGame() {
      try {
        const saveData = this.gameStore.saveGame(this.saveName || null)
        this.saveName = ''
        this.loadSavedGames()
        this.$root.showNotification('Игра сохранена: ' + saveData.name, 'success')
      } catch (error) {
        this.$root.showNotification('Ошибка сохранения: ' + error.message, 'error')
      }
    },
    
    loadSave(saveId) {
      try {
        this.gameStore.loadGame(saveId)
        this.$root.showNotification('Игра загружена', 'success')
        this.$emit('close')
        // Navigate to game view
        this.$router.push('/game')
      } catch (error) {
        this.$root.showNotification('Ошибка загрузки: ' + error.message, 'error')
      }
    },
    
    deleteSave(saveId) {
      if (confirm('Вы уверены, что хотите удалить это сохранение?')) {
        try {
          this.gameStore.deleteSave(saveId)
          this.loadSavedGames()
          this.$root.showNotification('Сохранение удалено', 'success')
        } catch (error) {
          this.$root.showNotification('Ошибка удаления: ' + error.message, 'error')
        }
      }
    },
    
    clearAllSaves() {
      if (confirm('Вы уверены, что хотите удалить ВСЕ сохранения? Это действие нельзя отменить.')) {
        try {
          this.gameStore.clearAllSaves()
          this.loadSavedGames()
          this.$root.showNotification('Все сохранения удалены', 'success')
        } catch (error) {
          this.$root.showNotification('Ошибка очистки: ' + error.message, 'error')
        }
      }
    },
    
    exportGame() {
      try {
        const jsonData = this.gameStore.exportGameData()
        const blob = new Blob([jsonData], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `star-courier-saves-${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        this.$root.showNotification('Сохранения экспортированы', 'success')
      } catch (error) {
        this.$root.showNotification('Ошибка экспорта: ' + error.message, 'error')
      }
    },
    
    triggerImport() {
      this.$refs.fileInput.click()
    },
    
    importGame(event) {
      const file = event.target.files[0]
      if (!file) return
      
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const jsonData = e.target.result
          this.gameStore.importGameData(jsonData)
          this.loadSavedGames()
          this.$root.showNotification('Сохранения импортированы', 'success')
        } catch (error) {
          this.$root.showNotification('Ошибка импорта: ' + error.message, 'error')
        }
      }
      reader.readAsText(file)
      // Reset file input
      event.target.value = ''
    },
    
    formatLastSaveTime(timestamp) {
      const now = Date.now()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'меньше минуты назад'
      if (minutes < 60) return `${minutes} минут${this.getPlural(minutes, 'у', 'ы', '')} назад`
      
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours} час${this.getPlural(hours, '', 'а', 'ов')} назад`
      
      const days = Math.floor(hours / 24)
      return `${days} день${this.getPlural(days, '', 'я', 'ей')} назад`
    },
    
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString('ru-RU')
    },
    
    formatPlaytime(seconds) {
      if (!seconds) return '0:00'
      
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (hours > 0) {
        return `${hours}ч ${minutes}м`
      }
      return `${minutes}м`
    },
    
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
    
    getPlural(number, one, two, five) {
      let n = Math.abs(number)
      n %= 100
      if (n >= 5 && n <= 20) return five
      n %= 10
      if (n === 1) return one
      if (n >= 2 && n <= 4) return two
      return five
    }
  }
})
</script>

<style scoped>
.save-manager {
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #92400e;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 700px;
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

.save-settings,
.manual-save,
.saved-games,
.export-import,
.clear-saves {
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
}

.setting-label input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
}

.setting-label select {
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid #78350f;
  color: #d1d5db;
  padding: 0.5rem;
  border-radius: 0.25rem;
  margin-left: 0.5rem;
}

.last-save {
  color: #9ca3af;
  font-size: 0.875rem;
  font-style: italic;
}

.save-input {
  display: flex;
  gap: 1rem;
}

.save-name-input {
  flex: 1;
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid #78350f;
  color: #d1d5db;
  padding: 0.75rem;
  border-radius: 0.25rem;
}

.save-name-input:focus {
  outline: none;
  border-color: #fbbf24;
}

.no-saves {
  color: #9ca3af;
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

.saves-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.save-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #78350f;
  border-radius: 0.375rem;
  transition: all 0.3s;
}

.save-item:hover {
  border-color: #fbbf24;
  background: rgba(30, 41, 59, 0.7);
}

.save-info {
  flex: 1;
}

.save-name {
  color: #fbbf24;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.save-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
}

.save-meta span {
  color: #9ca3af;
}

.save-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
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

.btn-small {
  padding: 0.25rem 0.75rem;
  font-size: 0.8125rem;
}

.export-import-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.hidden-file-input {
  display: none;
}

.clear-saves {
  text-align: center;
}

.clear-saves .btn-danger {
  background: rgba(239, 68, 68, 0.1);
  padding: 0.75rem 1.5rem;
}

.clear-saves .btn-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

@media (max-width: 768px) {
  .save-input {
    flex-direction: column;
  }
  
  .save-actions {
    flex-direction: column;
  }
  
  .export-import-buttons {
    flex-direction: column;
  }
  
  .save-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>