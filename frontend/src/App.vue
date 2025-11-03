<template>
  <div id="app" class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-logo">
          <span class="logo-icon">🚀</span>
          <div class="logo-text">
            <h1>STAR COURIER</h1>
            <p>Звездолёт «Элея»</p>
          </div>
        </div>
        
        <nav class="header-nav">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/game" v-if="gameStore.isGameStarted" class="nav-link">Игра</router-link>
          <router-link to="/about" class="nav-link">О проекте</router-link>
        </nav>
        
        <!-- Settings Button -->
        <button 
          class="settings-button"
          @click="uiStore.openModal('settings')"
          @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
          title="Настройки"
        >
          ⚙️
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="footer-content">
        <p>&copy; 2024 StarCourier Web - Интерактивная текстовая RPG</p>
        <div class="footer-links">
          <a href="https://github.com/QuadDarv1ne/star-courier-web" target="_blank" rel="noopener">
            GitHub
          </a>
          <a href="https://orcid.org/0009-0007-7605-539X" target="_blank" rel="noopener">
            ORCID
          </a>
        </div>
      </div>
    </footer>

    <!-- Notification -->
    <transition name="slide-up">
      <div v-if="notification.show" :class="['notification', `notification-${notification.type}`]">
        <span class="notification-icon">{{ getNotificationIcon(notification.type) }}</span>
        <span class="notification-text">{{ notification.message }}</span>
        <button class="notification-close" @click="hideNotification">✕</button>
      </div>
    </transition>
    
    <!-- Settings Modal -->
    <transition name="fade">
      <div v-if="uiStore.modals.settings" class="modal-overlay" @click="uiStore.closeModal('settings')">
        <div class="modal-container" @click.stop>
          <SettingsPanel @close="uiStore.closeModal('settings')" />
        </div>
      </div>
    </transition>
    
    <!-- Cache Stats (Development only) -->
    <div v-if="showCacheStats" class="cache-stats">
      <div>Cache Stats:</div>
      <div>Scenes: {{ cacheStats.scenes }}</div>
      <div>Characters: {{ cacheStats.characters }}</div>
      <button @click="clearAllCaches">Clear Cache</button>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useGameStore } from './store/game'
import { useUiStore } from './store/ui'
import SettingsPanel from './components/SettingsPanel.vue'

export default defineComponent({
  name: 'App',
  
  components: {
    SettingsPanel
  },
  
  setup() {
    const gameStore = useGameStore()
    const uiStore = useUiStore()
    
    return {
      gameStore,
      uiStore
    }
  },

  data() {
    return {
      notification: {
        show: false,
        message: '',
        type: 'info' // info, success, warning, error
      }
    }
  },

  computed: {
    apiUrl() {
      return this.$api
    },
    
    // Show cache stats in development
    showCacheStats() {
      return import.meta.env.MODE === 'development'
    },
    
    cacheStats() {
      if (this.gameStore) {
        return this.gameStore.getCacheStats()
      }
      return { scenes: 0, characters: 0, timestamps: 0 }
    }
  },

  methods: {
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
      this.notification = {
        show: true,
        message,
        type
      }
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        this.hideNotification()
      }, 5000)
    },
    
    /**
     * Hide notification
     */
    hideNotification() {
      this.notification.show = false
    },
    
    /**
     * Get notification icon based on type
     */
    getNotificationIcon(type) {
      const icons = {
        info: 'ℹ️',
        success: '✅',
        warning: '⚠️',
        error: '❌'
      }
      return icons[type] || 'ℹ️'
    },
    
    /**
     * Clear all caches
     */
    clearAllCaches() {
      this.gameStore.clearCaches()
      this.$api.clearApiCache()
      this.showNotification('Все кэши очищены', 'success')
    }
  },
  
  mounted() {
    // Make showNotification globally available
    this.$root.showNotification = this.showNotification
    
    // Log startup info
    console.log('🚀 StarCourier Web mounted')
    console.log('🎮 Game Store:', this.gameStore ? 'Ready' : 'Not Ready')
    console.log('🎨 UI Store:', this.uiStore ? 'Ready' : 'Not Ready')
  }
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #44260e 50%, #0f172a 100%);
  color: #e0e7ff;
}

/* ======================== HEADER ======================== */

.app-header {
  background: rgba(17, 24, 39, 0.9);
  border-bottom: 2px solid #92400e;
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: transform 0.3s;
}

.header-logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 2rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.logo-text h1 {
  font-size: 1.5rem;
  color: #fbbf24;
  margin: 0;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);
}

.logo-text p {
  font-size: 0.75rem;
  color: #fcd34d;
  margin: 0;
}

/* Settings Button */
.settings-button {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid #fbbf24;
  color: #fbbf24;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.25rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-button:hover {
  background: rgba(251, 191, 36, 0.2);
  transform: rotate(90deg);
}

/* Navigation */

.header-nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #d1d5db;
  text-decoration: none;
  transition: all 0.3s;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
}

.nav-link:hover {
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
}

.nav-link.router-link-active {
  color: #fbbf24;
  border-bottom: 2px solid #fbbf24;
}

/* ======================== MAIN ======================== */

.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* ======================== FOOTER ======================== */

.app-footer {
  background: rgba(17, 24, 39, 0.9);
  border-top: 2px solid #92400e;
  padding: 2rem 1.5rem;
  margin-top: 2rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-content p {
  color: #9ca3af;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.footer-links a {
  color: #fbbf24;
  text-decoration: none;
  transition: all 0.3s;
  font-size: 0.875rem;
}

.footer-links a:hover {
  text-decoration: underline;
  transform: translateY(-2px);
}

/* ======================== NOTIFICATION ======================== */

.notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  z-index: 9999;
  min-width: 300px;
  max-width: 500px;
}

.notification-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
  color: white;
  font-size: 0.95rem;
}

.notification-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.notification-close:hover {
  opacity: 1;
}

/* Notification Types */

.notification-info {
  background: rgba(59, 130, 246, 0.9);
  border-left: 4px solid #3b82f6;
}

.notification-success {
  background: rgba(34, 197, 94, 0.9);
  border-left: 4px solid #22c55e;
}

.notification-warning {
  background: rgba(245, 158, 11, 0.9);
  border-left: 4px solid #f59e0b;
}

.notification-error {
  background: rgba(239, 68, 68, 0.9);
  border-left: 4px solid #ef4444;
}

/* ======================== MODAL ======================== */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-container {
  max-height: 90vh;
  overflow-y: auto;
}

/* ======================== ANIMATIONS ======================== */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(100px);
  opacity: 0;
}

/* ======================== RESPONSIVE ======================== */

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .header-nav {
    gap: 1rem;
  }

  .nav-link {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
  }

  .app-main {
    padding: 1rem;
  }

  .notification {
    right: 1rem;
    left: 1rem;
    bottom: 1rem;
    min-width: unset;
  }

  .footer-links {
    gap: 1rem;
  }
}

/* Cache Stats (Development only) */
.cache-stats {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.8);
  color: #fbbf24;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.cache-stats button {
  background: #fbbf24;
  color: #0f172a;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  margin-top: 0.25rem;
}

.cache-stats button:hover {
  background: #f59e0b;
}
</style>