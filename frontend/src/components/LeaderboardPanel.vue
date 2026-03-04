<template>
  <div class="leaderboard-panel">
    <!-- Header -->
    <div class="panel-header">
      <h2>🏆 Таблица лидеров</h2>
      
      <!-- Sort Options -->
      <div class="sort-options">
        <button 
          v-for="opt in sortOptions"
          :key="opt.value"
          :class="['sort-btn', { active: sortBy === opt.value }]"
          @click="changeSort(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Stats Summary -->
    <div v-if="stats" class="stats-summary">
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_players }}</span>
        <span class="stat-label">Игроков</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ formatScore(stats.top_score) }}</span>
        <span class="stat-label">Топ счёт</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ formatPlaytime(stats.average_playtime) }}</span>
        <span class="stat-label">Среднее время</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка лидеров...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadLeaderboard">Повторить</button>
    </div>

    <!-- Leaderboard Table -->
    <div v-else class="leaderboard-table">
      <div class="table-header">
        <span class="col-rank">#</span>
        <span class="col-player">Игрок</span>
        <span class="col-score">Очки</span>
        <span class="col-achievements">🎖️</span>
        <span class="col-time">⏱️</span>
      </div>
      
      <TransitionGroup name="list" tag="div" class="table-body">
        <div 
          v-for="(entry, index) in entries"
          :key="entry.username"
          :class="['leaderboard-row', { 'current-user': isCurrentUser(entry.username) }]"
        >
          <span class="col-rank">
            <span v-if="entry.rank <= 3" :class="['medal', `medal-${entry.rank}`]">
              {{ getMedal(entry.rank) }}
            </span>
            <span v-else class="rank-number">{{ entry.rank }}</span>
          </span>
          <span class="col-player">
            <span class="player-avatar">{{ getPlayerAvatar(entry.username) }}</span>
            <span class="player-name">{{ entry.username }}</span>
          </span>
          <span class="col-score">
            <span class="score-value">{{ formatScore(entry.score) }}</span>
          </span>
          <span class="col-achievements">
            <span class="achievements-badge">{{ entry.achievements }}</span>
          </span>
          <span class="col-time">
            {{ formatPlaytime(entry.playtime) }}
          </span>
        </div>
      </TransitionGroup>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button 
        class="page-btn"
        :disabled="offset === 0"
        @click="prevPage"
      >
        ← Назад
      </button>
      <span class="page-info">
        Страница {{ currentPage }} из {{ totalPages }}
      </span>
      <button 
        class="page-btn"
        :disabled="offset + limit >= totalEntries"
        @click="nextPage"
      >
        Вперёд →
      </button>
    </div>

    <!-- Close button -->
    <button class="close-btn" @click="$emit('close')" title="Закрыть">
      ✕
    </button>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { leaderboardApi, formatScore, formatPlaytime } from '../services/gameStats'
import { useAuthStore } from '../store/auth'

export default {
  name: 'LeaderboardPanel',
  
  emits: ['close'],
  
  setup() {
    const authStore = useAuthStore()
    
    const entries = ref([])
    const stats = ref(null)
    const totalEntries = ref(0)
    const isLoading = ref(true)
    const error = ref(null)
    
    const sortBy = ref('score')
    const limit = 10
    const offset = ref(0)
    
    const sortOptions = [
      { value: 'score', label: 'По очкам' },
      { value: 'playtime', label: 'По времени' },
      { value: 'achievements', label: 'По достижениям' }
    ]
    
    // Computed
    const currentPage = computed(() => Math.floor(offset.value / limit) + 1)
    const totalPages = computed(() => Math.ceil(totalEntries.value / limit))
    
    // Methods
    async function loadLeaderboard() {
      isLoading.value = true
      error.value = null
      
      try {
        // Load leaderboard entries
        const data = await leaderboardApi.getLeaderboard({
          limit,
          offset: offset.value,
          sortBy: sortBy.value
        })
        
        entries.value = data
        totalEntries.value = data.length < limit && offset.value === 0 
          ? data.length 
          : (data.length === limit ? (currentPage.value + 1) * limit : totalEntries.value)
        
        // Load stats
        const statsData = await leaderboardApi.getStats()
        stats.value = statsData
      } catch (err) {
        console.error('Failed to load leaderboard:', err)
        error.value = err.message
      } finally {
        isLoading.value = false
      }
    }
    
    function changeSort(newSort) {
      sortBy.value = newSort
      offset.value = 0
      loadLeaderboard()
    }
    
    function prevPage() {
      if (offset.value >= limit) {
        offset.value -= limit
        loadLeaderboard()
      }
    }
    
    function nextPage() {
      offset.value += limit
      loadLeaderboard()
    }
    
    function getMedal(rank) {
      const medals = ['🥇', '🥈', '🥉']
      return medals[rank - 1] || ''
    }
    
    function getPlayerAvatar(username) {
      if (!username) return '👤'
      const firstChar = username.charAt(0).toUpperCase()
      const avatars = ['🚀', '⭐', '🌟', '💫', '✨', '🎯', '🛸', '🌌']
      return avatars[firstChar.charCodeAt(0) % avatars.length]
    }
    
    function isCurrentUser(username) {
      return authStore.user?.username?.toLowerCase() === username?.toLowerCase()
    }
    
    // Lifecycle
    onMounted(() => {
      loadLeaderboard()
    })
    
    return {
      entries,
      stats,
      isLoading,
      error,
      sortBy,
      sortOptions,
      limit,
      offset,
      currentPage,
      totalPages,
      totalEntries,
      loadLeaderboard,
      changeSort,
      prevPage,
      nextPage,
      getMedal,
      getPlayerAvatar,
      isCurrentUser,
      formatScore,
      formatPlaytime
    }
  }
}
</script>

<style scoped>
.leaderboard-panel {
  background: rgba(17, 24, 39, 0.95);
  border: 2px solid #fbbf24;
  border-radius: 1rem;
  padding: 2rem;
  min-width: 600px;
  max-width: 700px;
  position: relative;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.panel-header h2 {
  color: #fbbf24;
  margin: 0;
}

.sort-options {
  display: flex;
  gap: 0.5rem;
}

.sort-btn {
  padding: 0.5rem 1rem;
  background: rgba(17, 24, 39, 0.5);
  border: 1px solid #78350f;
  color: #9ca3af;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.85rem;
}

.sort-btn:hover {
  border-color: #fbbf24;
  color: #fbbf24;
}

.sort-btn.active {
  background: linear-gradient(135deg, #d97706, #ea580c);
  color: white;
  border-color: #fbbf24;
}

.stats-summary {
  display: flex;
  justify-content: space-around;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  color: #fbbf24;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  color: #6b7280;
  font-size: 0.8rem;
}

.leaderboard-table {
  margin-bottom: 1rem;
}

.table-header {
  display: grid;
  grid-template-columns: 60px 1fr 100px 60px 80px;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  color: #9ca3af;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.table-body {
  max-height: 400px;
  overflow-y: auto;
}

.leaderboard-row {
  display: grid;
  grid-template-columns: 60px 1fr 100px 60px 80px;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #1f2937;
  align-items: center;
  transition: all 0.3s;
}

.leaderboard-row:hover {
  background: rgba(251, 191, 36, 0.05);
}

.leaderboard-row.current-user {
  background: rgba(34, 197, 94, 0.1);
  border-left: 3px solid #22c55e;
}

.col-rank {
  text-align: center;
}

.medal {
  font-size: 1.5rem;
}

.medal-1 { animation: shine 2s infinite; }
.medal-2 { animation: shine 3s infinite; }
.medal-3 { animation: shine 4s infinite; }

@keyframes shine {
  0%, 100% { filter: drop-shadow(0 0 3px rgba(251, 191, 36, 0.5)); }
  50% { filter: drop-shadow(0 0 10px rgba(251, 191, 36, 1)); }
}

.rank-number {
  color: #9ca3af;
  font-weight: bold;
}

.col-player {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.player-avatar {
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.player-name {
  color: #e5e7eb;
  font-weight: 500;
}

.current-user .player-name {
  color: #22c55e;
}

.col-score {
  text-align: right;
}

.score-value {
  color: #fbbf24;
  font-weight: bold;
}

.col-achievements {
  text-align: center;
}

.achievements-badge {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.col-time {
  color: #9ca3af;
  font-size: 0.9rem;
  text-align: center;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #1f2937;
}

.page-btn {
  padding: 0.5rem 1rem;
  background: rgba(17, 24, 39, 0.5);
  border: 1px solid #78350f;
  color: #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  border-color: #fbbf24;
  color: #fbbf24;
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 0.9rem;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #9ca3af;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #1f2937;
  border-top-color: #fbbf24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #ef4444;
  border: none;
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
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

/* List transition animations */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

@media (max-width: 640px) {
  .leaderboard-panel {
    min-width: unset;
    width: 100%;
    padding: 1.5rem;
  }
  
  .table-header,
  .leaderboard-row {
    grid-template-columns: 40px 1fr 70px 40px;
  }
  
  .col-time {
    display: none;
  }
}
</style>
