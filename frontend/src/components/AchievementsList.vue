<!-- Achievement list component -->
<template>
  <div class="achievements-modal">
    <div class="modal-header">
      <h3>🏆 Достижения</h3>
      <div class="progress-info">
        {{ achievementsStore.completionPercentage }}% выполнено
        <span class="achievement-count">
          ({{ unlockedCount }}/{{ totalAchievements }})
        </span>
      </div>
      <button class="modal-close" @click="$emit('close')" @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')">
        ✕
      </button>
    </div>

    <div class="modal-content">
      <div class="achievements-tabs">
        <button 
          :class="['tab', { active: activeTab === 'all' }]"
          @click="activeTab = 'all'"
        >
          Все
        </button>
        <button 
          :class="['tab', { active: activeTab === 'unlocked' }]"
          @click="activeTab = 'unlocked'"
        >
          Разблокированные
        </button>
        <button 
          :class="['tab', { active: activeTab === 'locked' }]"
          @click="activeTab = 'locked'"
        >
          Неразблокированные
        </button>
        <button 
          :class="['tab', { active: activeTab === 'categories' }]"
          @click="activeTab = 'categories'"
        >
          Категории
        </button>
      </div>
      
      <!-- Category View -->
      <div v-if="activeTab === 'categories'" class="categories-view">
        <div 
          v-for="(achievements, category) in achievementsByCategory" 
          :key="`category-${category}`"
          class="category-section"
        >
          <h4 class="category-title">
            {{ getCategoryName(category) }}
            <span class="category-progress">
              ({{ getUnlockedInCategory(achievements) }}/{{ achievements.length }})
            </span>
          </h4>
          <div class="category-achievements">
            <div 
              v-for="achievement in achievements" 
              :key="`achievement-${achievement.id}`"
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
                <h5>{{ isUnlocked(achievement.id) || !achievement.secret ? achievement.title : '???' }}</h5>
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
      
      <!-- Standard Views -->
      <div v-else class="achievements-grid">
        <div 
          v-for="achievement in filteredAchievements" 
          :key="`achievement-${achievement.id}`"
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
            
            <div v-if="!isUnlocked(achievement.id) && achievement.progress === undefined" class="achievement-hint">
              <span v-if="!achievement.secret">Подсказка: {{ getHint(achievement.id) }}</span>
              <span v-else>???</span>
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
  
  data() {
    return {
      activeTab: 'all'
    }
  },
  
  computed: {
    filteredAchievements() {
      const all = this.achievementsStore.allAchievements
      
      switch (this.activeTab) {
        case 'unlocked':
          return all.filter(a => this.isUnlocked(a.id))
        case 'locked':
          return all.filter(a => !this.isUnlocked(a.id))
        default:
          return all
      }
    },
    
    achievementsByCategory() {
      return this.achievementsStore.achievementsByCategory || {}
    },
    
    unlockedCount() {
      return this.achievementsStore.unlockedAchievements.size
    },
    
    totalAchievements() {
      return this.achievementsStore.allAchievements.length
    }
  },

  methods: {
    isUnlocked(achievementId) {
      return this.achievementsStore.unlockedAchievements.has(achievementId)
    },
    
    getHint(achievementId) {
      const hints = {
        first_choice: 'Сделайте первый выбор в игре',
        explorer: 'Посетите разные сцены',
        survivor: 'Выживите с низким здоровьем',
        rich_courier: 'Заработайте больше денег',
        trusted_friend: 'Повышайте доверие с персонажами',
        knowledge_seeker: 'Повышайте уровень знаний',
        team_player: 'Работайте с командой',
        fuel_efficient: 'Экономьте топливо',
        peace_maker: 'Сохраняйте высокую мораль',
        danger_zone: 'Попадите в опасные ситуации',
        psychic_power: 'Развивайте психические способности',
        security_expert: 'Повышайте уровень безопасности',
        master_negotiator: 'Выбирайте дипломатичные решения',
        time_traveler: 'Достигните всех концовок',
        collector: 'Соберите предметы'
      }
      return hints[achievementId] || 'Продолжайте играть'
    },
    
    getCategoryName(category) {
      const names = {
        exploration: 'Исследование',
        survival: 'Выживание',
        social: 'Социальные',
        resources: 'Ресурсы',
        skills: 'Навыки',
        teamwork: 'Командная работа',
        challenge: 'Вызовы'
      }
      return names[category] || category
    },
    
    getUnlockedInCategory(achievements) {
      return achievements.filter(a => this.isUnlocked(a.id)).length
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.achievement-count {
  font-size: 0.9rem;
  color: #fbbf24;
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

.achievements-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #44260e;
  padding-bottom: 1rem;
  flex-wrap: wrap;
}

.tab {
  background: transparent;
  border: 1px solid #78350f;
  color: #9ca3af;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.tab:hover {
  background: rgba(251, 191, 36, 0.1);
  border-color: #fbbf24;
  color: #fbbf24;
}

.tab.active {
  background: rgba(251, 191, 36, 0.2);
  border-color: #fbbf24;
  color: #fbbf24;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.category-section {
  margin-bottom: 2rem;
}

.category-title {
  color: #fbbf24;
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-progress {
  font-size: 0.9rem;
  color: #9ca3af;
}

.category-achievements {
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
  position: relative;
  overflow: hidden;
}

.achievement-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.achievement-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.achievement-card:hover::before {
  left: 100%;
}

.achievement-unlocked {
  border-color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
}

.achievement-unlocked .achievement-icon {
  animation: pulse 2s infinite;
}

.achievement-secret .achievement-details h4,
.achievement-secret .achievement-details h5,
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

.achievement-details h4,
.achievement-details h5 {
  color: #fbbf24;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.achievement-details p {
  color: #9ca3af;
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  line-height: 1.4;
}

.achievement-progress {
  margin-top: 0.5rem;
}

.progress-bar {
  background: rgba(0, 0, 0, 0.2);
  height: 6px;
  border-radius: 3px;
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

.achievement-hint {
  color: #78350f;
  font-size: 0.75rem;
  font-style: italic;
  border-top: 1px dashed #78350f;
  padding-top: 0.5rem;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.4);
  }
  70% {
    box-shadow: 0 0 0 5px rgba(251, 191, 36, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0);
  }
}

@media (max-width: 768px) {
  .achievements-grid,
  .category-achievements {
    grid-template-columns: 1fr;
  }
  
  .achievements-tabs {
    flex-direction: column;
  }
  
  .tab {
    width: 100%;
    text-align: center;
  }
}
</style>