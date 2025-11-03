/**
 * UI Store for StarCourier Web
 * Manages UI state, notifications, and user interface settings
 * 
 * Uses Pinia for state management
 */

import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
  state: () => ({
    // ========================
    // NOTIFICATIONS
    // ========================
    
    notifications: [],
    
    // ========================
    // MODALS
    // ========================
    
    modals: {
      inventory: false,
      settings: false,
      achievements: false,
      saves: false,
      help: false
    },
    
    // ========================
    // UI STATE
    // ========================
    
    isDarkMode: true,
    sidebarOpen: true,
    soundEnabled: true,
    musicEnabled: true,
    
    // ========================
    // LOADING & ERRORS
    // ========================
    
    isLoading: false,
    loadingMessage: '',
    error: null,
    
    // ========================
    // SETTINGS
    // ========================
    
    settings: {
      textSize: 'medium', // small, medium, large
      animationsEnabled: true,
      autoSaveEnabled: true,
      autoSaveInterval: 300000, // 5 minutes
      showTutorial: true,
      language: 'ru'
    },
    
    // ========================
    // PERFORMANCE
    // ========================
    
    // Track UI performance metrics
    performanceMetrics: {
      lastRenderTime: 0,
      averageRenderTime: 0,
      renderCount: 0
    },
    
    // Debounce timers for performance
    debounceTimers: new Map()
  }),

  getters: {
    /**
     * Get active notifications
     */
    activeNotifications: (state) => {
      return state.notifications.filter(n => n.active)
    },

    /**
     * Check if any modal is open
     */
    isModalOpen: (state) => {
      return Object.values(state.modals).some(value => value === true)
    },

    /**
     * Get current text size class
     */
    textSizeClass: (state) => {
      return `text-${state.settings.textSize}`
    },
    
    /**
     * Get UI performance metrics
     */
    uiPerformance: (state) => {
      return state.performanceMetrics
    }
  },

  actions: {
    /**
     * Add notification
     * @param {Object} notification - Notification object
     * @param {string} notification.message - Message text
     * @param {string} notification.type - Type: info, success, warning, error
     * @param {number} notification.duration - Duration in ms (0 = infinite)
     */
    addNotification(notification) {
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
      const notif = {
        id,
        message: notification.message,
        type: notification.type || 'info',
        active: true,
        timestamp: Date.now()
      }

      this.notifications.push(notif)

      // Auto-remove notification
      if (notification.duration !== 0) {
        const duration = notification.duration || 3000
        setTimeout(() => {
          this.removeNotification(id)
        }, duration)
      }

      console.log(`📢 Уведомление (${notif.type}):`, notif.message)
      return id
    },

    /**
     * Remove notification by ID
     */
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications[index].active = false
        setTimeout(() => {
          this.notifications.splice(index, 1)
        }, 300) // Animation delay
      }
    },

    /**
     * Clear all notifications
     */
    clearNotifications() {
      this.notifications = []
    },

    /**
     * Show info notification
     */
    showInfo(message, duration = 3000) {
      return this.addNotification({
        message,
        type: 'info',
        duration
      })
    },

    /**
     * Show success notification
     */
    showSuccess(message, duration = 3000) {
      return this.addNotification({
        message,
        type: 'success',
        duration
      })
    },

    /**
     * Show warning notification
     */
    showWarning(message, duration = 5000) {
      return this.addNotification({
        message,
        type: 'warning',
        duration
      })
    },

    /**
     * Show error notification
     */
    showError(message, duration = 0) {
      return this.addNotification({
        message,
        type: 'error',
        duration
      })
    },
    
    /**
     * Show network error notification
     */
    showNetworkError(message, duration = 0) {
      return this.addNotification({
        message: `📡 ${message}`,
        type: 'error',
        duration
      })
    },
    
    /**
     * Show success notification with icon
     */
    showSuccessWithIcon(message, duration = 3000) {
      return this.addNotification({
        message: `✅ ${message}`,
        type: 'success',
        duration
      })
    },
    
    /**
     * Show warning notification with icon
     */
    showWarningWithIcon(message, duration = 5000) {
      return this.addNotification({
        message: `⚠️ ${message}`,
        type: 'warning',
        duration
      })
    },
    
    /**
     * Show info notification with icon
     */
    showInfoWithIcon(message, duration = 3000) {
      return this.addNotification({
        message: `ℹ️ ${message}`,
        type: 'info',
        duration
      })
    },
    
    /**
     * Show loading notification
     */
    showLoading(message, duration = 0) {
      return this.addNotification({
        message: `⏳ ${message}`,
        type: 'info',
        duration
      })
    },
    
    /**
     * Show achievement notification
     */
    showAchievement(title, description, duration = 5000) {
      return this.addNotification({
        message: `🏆 ${title}: ${description}`,
        type: 'success',
        duration
      })
    },

    /**
     * Open modal
     */
    openModal(modalName) {
      if (this.modals.hasOwnProperty(modalName)) {
        this.modals[modalName] = true
        console.log(`🔓 Открыто окно: ${modalName}`)
      }
    },

    /**
     * Close modal
     */
    closeModal(modalName) {
      if (this.modals.hasOwnProperty(modalName)) {
        this.modals[modalName] = false
        console.log(`🔒 Закрыто окно: ${modalName}`)
      }
    },

    /**
     * Toggle modal
     */
    toggleModal(modalName) {
      if (this.modals.hasOwnProperty(modalName)) {
        this.modals[modalName] = !this.modals[modalName]
      }
    },

    /**
     * Close all modals
     */
    closeAllModals() {
      Object.keys(this.modals).forEach(key => {
        this.modals[key] = false
      })
    },

    /**
     * Set loading state
     */
    setLoading(isLoading, message = '') {
      this.isLoading = isLoading
      this.loadingMessage = message
    },

    /**
     * Set error
     */
    setError(error) {
      this.error = error
      if (error) {
        this.showError(error)
      }
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null
    },

    /**
     * Toggle dark mode
     */
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode
      this.saveUiSettings()
    },

    /**
     * Toggle sidebar
     */
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
      this.saveUiSettings()
    },

    /**
     * Toggle sound
     */
    toggleSound() {
      this.soundEnabled = !this.soundEnabled
      this.saveUiSettings()
    },

    /**
     * Toggle music
     */
    toggleMusic() {
      this.musicEnabled = !this.musicEnabled
      this.saveUiSettings()
    },

    /**
     * Update settings
     */
    updateSettings(newSettings) {
      this.settings = {
        ...this.settings,
        ...newSettings
      }
      this.saveUiSettings()
    },

    /**
     * Set text size
     */
    setTextSize(size) {
      if (['small', 'medium', 'large'].includes(size)) {
        this.settings.textSize = size
        this.saveUiSettings()
      }
    },
    
    /**
     * Set auto-save settings
     */
    setAutoSaveSettings(enabled, interval) {
      this.settings.autoSaveEnabled = enabled
      if (interval) {
        this.settings.autoSaveInterval = interval
      }
      this.saveUiSettings()
    },

    /**
     * Save UI settings to localStorage
     */
    saveUiSettings() {
      try {
        const settings = {
          isDarkMode: this.isDarkMode,
          sidebarOpen: this.sidebarOpen,
          soundEnabled: this.soundEnabled,
          musicEnabled: this.musicEnabled,
          settings: this.settings
        }
        localStorage.setItem('starCourierUiSettings', JSON.stringify(settings))
        console.log('✅ Настройки UI сохранены')
      } catch (error) {
        console.error('❌ Ошибка при сохранении настроек:', error)
      }
    },

    /**
     * Load UI settings from localStorage
     */
    loadUiSettings() {
      try {
        const saved = localStorage.getItem('starCourierUiSettings')
        if (saved) {
          const settings = JSON.parse(saved)
          this.isDarkMode = settings.isDarkMode ?? this.isDarkMode
          this.sidebarOpen = settings.sidebarOpen ?? this.sidebarOpen
          this.soundEnabled = settings.soundEnabled ?? this.soundEnabled
          this.musicEnabled = settings.musicEnabled ?? this.musicEnabled
          this.settings = { ...this.settings, ...settings.settings }
          console.log('✅ Настройки UI загружены')
        }
      } catch (error) {
        console.error('❌ Ошибка при загрузке настроек:', error)
      }
    },

    /**
     * Reset UI settings to defaults
     */
    resetUiSettings() {
      this.isDarkMode = true
      this.sidebarOpen = true
      this.soundEnabled = true
      this.musicEnabled = true
      this.settings = {
        textSize: 'medium',
        animationsEnabled: true,
        autoSaveEnabled: true,
        autoSaveInterval: 300000, // 5 minutes
        showTutorial: true,
        language: 'ru'
      }
      this.saveUiSettings()
      console.log('🔄 Настройки UI сброшены')
    },
    
    /**
     * Debounce function for performance optimization
     * @param {string} key - Unique key for the debounce timer
     * @param {Function} func - Function to execute
     * @param {number} delay - Delay in milliseconds
     */
    debounce(key, func, delay = 300) {
      // Clear existing timer
      if (this.debounceTimers.has(key)) {
        clearTimeout(this.debounceTimers.get(key))
      }
      
      // Set new timer
      const timer = setTimeout(() => {
        func()
        this.debounceTimers.delete(key)
      }, delay)
      
      // Store timer
      this.debounceTimers.set(key, timer)
    },
    
    /**
     * Track UI render performance
     * @param {number} renderTime - Time taken to render in milliseconds
     */
    trackRenderPerformance(renderTime) {
      this.performanceMetrics.lastRenderTime = renderTime
      this.performanceMetrics.renderCount++
      
      // Calculate average render time
      const totalRenderTime = this.performanceMetrics.averageRenderTime * (this.performanceMetrics.renderCount - 1) + renderTime
      this.performanceMetrics.averageRenderTime = totalRenderTime / this.performanceMetrics.renderCount
    },
    
    /**
     * Get performance report
     */
    getPerformanceReport() {
      return {
        ...this.performanceMetrics,
        fps: this.performanceMetrics.averageRenderTime > 0 ? 
          Math.round(1000 / this.performanceMetrics.averageRenderTime) : 0
      }
    },
    
    /**
     * Clear performance metrics
     */
    clearPerformanceMetrics() {
      this.performanceMetrics = {
        lastRenderTime: 0,
        averageRenderTime: 0,
        renderCount: 0
      }
    }
  }
})