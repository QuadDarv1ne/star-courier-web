<template>
  <div class="achievements-panel">
    <!-- Header -->
    <div class="panel-header">
      <h2>🎖️ Достижения</h2>
      <div class="progress-summary">
        <div class="progress-ring">
          <svg viewBox="0 0 36 36" class="circular-chart">
            <path class="circle-bg"
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path class="circle"
              :stroke-dasharray="`${progressPercentage}, 100`"
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <span class="progress-text">{{ progressPercentage }}%</span>
        </div>
        <div class="progress-info">
          <span class="unlocked">{{ unlockedCount }}</span>
          <span class="separator">/</span>
          <span class="total">{{ totalCount }}</span>
          <span class="label">открыто</span>
        </div>
        <div class="total-points">
          <span class="points">{{ totalPoints }}</span>
          <span class="label">очков</span>
        </div>
      </div>
    </div>

    <!-- Category Filter -->
    <div class="category-filter">
      <button 
        :class="['filter-btn', { active: selectedCategory === null }]"
        @click="selectedCategory = null"
      >
        Все
      </button>
      <button 
        v-for="cat in categories"
        :key="cat.id"
        :class="['filter-btn', { active: selectedCategory === cat.id }]"
        @click="selectedCategory = cat.id"
      >
        {{ cat.icon }} {{ cat.name }}
      </button>
    </div>

    <!-- Achievements Grid -->
    <div class="achievements-grid">
      <div 
        v-for="achievement in filteredAchievements"
        :key="achievement.id"
        :class="['achievement-card', { unlocked: isUnlocked(achievement.id) }]"
        :style="{ '--rarity-color': achievement.rarity_color }"
      >
        <div class="achievement-icon">
          {{ achievement.icon }}
        </div>
        <div class="achievement-info">
          <h3 class="achievement-name">
            {{ isUnlocked(achievement.id) || !achievement.hidden ? achievement.name : '???' }}
          </h3>
          <p class="achievement-description">
            {{ isUnlocked(achievement.id) || !achievement.hidden ? achievement.description : 'Скрытое достижение' }}
          </p>
          <div class="achievement-meta">
            <span class="points">
              {{ achievement.points }} очков
            </span>
            <span :class="['rarity', achievement.rarity]">
              {{ getRarityName(achievement.rarity) }}
            </span>
          </div>
        </div>
        <div v-if="isUnlocked(achievement.id)" class="unlocked-badge">
          ✓
        </div>
        <div v-else class="progress-bar">
          <div 
            class="progress-fill"
            :style="{ width: `${getProgress(achievement.id)}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Close button -->
    <button class="close-btn" @click="$emit('close')" title="Закрыть">
      ✕
    </button>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { achievementsApi, getRarityName } from '../services/gameStats'
import { useGameStore } from '../store/game'

export default {
  name: 'AchievementsPanel',
  
  emits: ['close'],
  
  setup() {
    const gameStore = useGameStore()
    
    const achievements = ref([])
    const categories = ref([])
    const unlockedAchievements = ref(new Set())
    const progress = ref({})
    const selectedCategory = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    
    // Computed
    const filteredAchievements = computed(() => {
      if (!selectedCategory.value) return achievements.value
      return achievements.value.filter(a => a.category === selectedCategory.value)
    })
    
    const unlockedCount = computed(() => unlockedAchievements.value.size)
    const totalCount = computed(() => achievements.value.length)
    
    const progressPercentage = computed(() => {
      if (totalCount.value === 0) return 0
      return Math.round((unlockedCount.value / totalCount.value) * 100)
    })
    
    const totalPoints = computed(() => {
      return achievements.value
        .filter(a => isUnlocked(a.id))
        .reduce((sum, a) => sum + a.points, 0)
    })
    
    // Methods
    async function loadAchievements() {
      isLoading.value = true
      error.value = null
      
      try {
        // Load achievements definitions
        const data = await achievementsApi.getAll({ includeHidden: false })
        achievements.value = data.achievements
        
        // Load categories
        const catData = await achievementsApi.getCategories()
        categories.value = Object.entries(catData.categories).map(([id, cat]) => ({
          id,
          ...cat
        }))
        
        // Check player achievements
        await checkPlayerAchievements()
      } catch (err) {
        console.error('Failed to load achievements:', err)
        error.value = err.message
      } finally {
        isLoading.value = false
      }
    }
    
    async function checkPlayerAchievements() {
      try {
        const playerData = {
          visited_scenes: Array.from(gameStore.visitedScenes || []),
          choices_made: gameStore.choicesMade || 0,
          decision_patterns: gameStore.decisionPatterns || {},
          stats: gameStore.stats || {},
          relationships: gameStore.relationships || {},
          ending_type: gameStore.endingType || null,
          playtime_minutes: Math.floor((gameStore.playtime || 0) / 60),
          games_completed: gameStore.gamesCompleted || 0
        }
        
        const result = await achievementsApi.checkForPlayer(playerData)
        
        unlockedAchievements.value = new Set(
          result.achievements.map(a => a.id)
        )
        progress.value = result.progress
      } catch (err) {
        console.error('Failed to check achievements:', err)
      }
    }
    
    function isUnlocked(achievementId) {
      return unlockedAchievements.value.has(achievementId)
    }
    
    function getProgress(achievementId) {
      const p = progress.value[achievementId]
      if (!p) return 0
      return Math.round(p.percentage || 0)
    }
    
    // Lifecycle
    onMounted(() => {
      loadAchievements()
    })
    
    return {
      achievements,
      categories,
      selectedCategory,
      isLoading,
      error,
      filteredAchievements,
      unlockedCount,
      totalCount,
      progressPercentage,
      totalPoints,
      isUnlocked,
      getProgress,
      getRarityName
    }
  }
}
</script>

<style scoped>
.achievements-panel {
  background: rgba(17, 24, 39, 0.95);
  border: 2px solid #fbbf24;
  border-radius: 1rem;
  padding: 2rem;
  min-width: 600px;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #44260e;
}

.panel-header h2 {
  color: #fbbf24;
  margin: 0;
  font-size: 1.5rem;
}

.progress-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.progress-ring {
  position: relative;
  width: 60px;
  height: 60px;
}

.circular-chart {
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: #44260e;
  stroke-width: 3;
}

.circle {
  fill: none;
  stroke: #fbbf24;
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fbbf24;
  font-weight: bold;
  font-size: 0.9rem;
}

.progress-info {
  text-align: center;
}

.progress-info .unlocked {
  color: #fbbf24;
  font-size: 1.5rem;
  font-weight: bold;
}

.progress-info .separator {
  color: #6b7280;
  margin: 0 0.25rem;
}

.progress-info .total {
  color: #9ca3af;
  font-size: 1.25rem;
}

.progress-info .label {
  display: block;
  color: #6b7280;
  font-size: 0.8rem;
}

.total-points {
  text-align: center;
  padding-left: 1rem;
  border-left: 1px solid #44260e;
}

.total-points .points {
  display: block;
  color: #fbbf24;
  font-size: 1.5rem;
  font-weight: bold;
}

.total-points .label {
  color: #6b7280;
  font-size: 0.8rem;
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: rgba(17, 24, 39, 0.5);
  border: 1px solid #78350f;
  color: #d1d5db;
  border-radius: 2rem;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.filter-btn:hover {
  background: rgba(251, 191, 36, 0.1);
  border-color: #fbbf24;
}

.filter-btn.active {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  border-color: #fbbf24;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.achievement-card {
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid #44260e;
  border-radius: 0.75rem;
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
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--rarity-color, #6b7280);
}

.achievement-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.achievement-card.unlocked {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.05);
}

.achievement-card.unlocked::before {
  background: #22c55e;
}

.achievement-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
}

.achievement-card.unlocked .achievement-icon {
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% { filter: drop-shadow(0 0 5px rgba(34, 197, 94, 0.5)); }
  50% { filter: drop-shadow(0 0 15px rgba(34, 197, 94, 0.8)); }
}

.achievement-info {
  flex: 1;
  min-width: 0;
}

.achievement-name {
  color: #fbbf24;
  font-size: 1rem;
  margin: 0 0 0.25rem 0;
}

.achievement-description {
  color: #9ca3af;
  font-size: 0.85rem;
  margin: 0 0 0.5rem 0;
}

.achievement-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}

.achievement-meta .points {
  color: #fbbf24;
}

.achievement-meta .rarity {
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  text-transform: uppercase;
  font-weight: 600;
}

.rarity.common { background: rgba(156, 163, 175, 0.2); color: #9ca3af; }
.rarity.uncommon { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.rarity.rare { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.rarity.epic { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
.rarity.legendary { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }

.unlocked-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  background: #22c55e;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #1f2937;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #d97706, #ea580c);
  transition: width 0.5s ease;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #fbbf24;
}

@media (max-width: 640px) {
  .achievements-panel {
    min-width: unset;
    width: 100%;
    padding: 1.5rem;
  }
  
  .progress-summary {
    flex-wrap: wrap;
  }
}
</style>
