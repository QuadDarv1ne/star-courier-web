<!-- Achievement list component -->
<template>
  <div class="achievements-modal">
    <div class="modal-header">
      <h3>🏆 Достижения</h3>
      <div class="progress-info">
        {{ achievementsStore.completionPercentage }}% выполнено
      </div>
      <button class="modal-close" @click="$emit('close')" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
        ✕
      </button>
    </div>

    <div class="modal-content">
      <div class="achievements-grid">
        <div 
          v-for="achievement in achievementsStore.allAchievements" 
          :key="achievement.id"
          :class="[
            'achievement-card',
            {
              'achievement-unlocked': isUnlocked(achievement.id),
              'achievement-secret': achievement.secret && !isUnlocked(achievement.id)
            }
          ]"
        >
          <div class="achievement-icon">{{ achievement.icon }}</div>
          <div class="achievement-details">
            <h4>{{ isUnlocked(achievement.id) || !achievement.secret ? achievement.title : '???' }}</h4>
            <p>{{ isUnlocked(achievement.id) || !achievement.secret ? achievement.description : 'Секретное достижение' }}</p>
            
            <div v-if="achievement.progress !== undefined" class="achievement-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: `${(achievement.progress / achievement.target) * 100}%` }"
                ></div>
              </div>
              <span class="progress-text">
                {{ achievement.progress }} / {{ achievement.target }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useAchievementsStore } from '../store/achievements'

export default defineComponent({
  name: 'AchievementsList',

  setup() {
    const achievementsStore = useAchievementsStore()
    return { achievementsStore }
  },

  methods: {
    isUnlocked(achievementId) {
      return this.achievementsStore.unlockedAchievements.has(achievementId)
    }
  }
})
</script>

<style scoped>
.achievements-modal {
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

.progress-info {
  color: #9ca3af;
  margin-right: 1rem;
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
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.achievement-card {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.375rem;
  padding: 1rem;
  display: flex;
  gap: 1rem;
  transition: all 0.3s;
}

.achievement-unlocked {
  border-color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
}

.achievement-secret .achievement-details h4,
.achievement-secret .achievement-details p {
  filter: blur(3px);
}

.achievement-icon {
  font-size: 2rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(251, 191, 36, 0.1);
  border-radius: 0.375rem;
  flex-shrink: 0;
}

.achievement-details {
  flex: 1;
}

.achievement-details h4 {
  color: #fbbf24;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.achievement-details p {
  color: #9ca3af;
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.4;
}

.achievement-progress {
  margin-top: 0.75rem;
}

.progress-bar {
  background: rgba(0, 0, 0, 0.2);
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
  transition: width 0.3s ease;
}

.progress-text {
  color: #9ca3af;
  font-size: 0.75rem;
}
</style>