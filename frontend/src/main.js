/**
 * StarCourier Web - Frontend
 * Главная точка входа Vue.js приложения
 * 
 * Автор: QuadDarv1ne
 * Версия: 1.0.0
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Импорт стилей
import './styles/main.css'
import './styles/variables.css'
import './styles/components.css'
import './styles/animations.css'

// ============================================================================
// КОНФИГУРАЦИЯ
// ============================================================================

// API URL из переменных окружения
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================================
// СОЗДАНИЕ ПРИЛОЖЕНИЯ
// ============================================================================

const app = createApp(App)

// ============================================================================
// ПЛАГИНЫ
// ============================================================================

// Pinia для state management
const pinia = createPinia()
app.use(pinia)

// Router для навигации
app.use(router)

// ============================================================================
// ГЛОБАЛЬНЫЕ СВОЙСТВА
// ============================================================================

// API URL
app.config.globalProperties.$api = API_URL

// Глобальные утилиты
app.config.globalProperties.$utils = {
  /**
   * Форматирование числа со статистикой
   */
  formatStat(value, max = 100) {
    return Math.min(max, Math.max(0, value))
  },

  /**
   * Получение цвета для статистики
   */
  getStatColor(value) {
    if (value >= 70) return '#22c55e' // Зелёный
    if (value >= 40) return '#eab308' // Жёлтый
    if (value >= 20) return '#f97316' // Оранжевый
    return '#ef4444' // Красный
  },

  /**
   * Форматирование даты
   */
  formatDate(date) {
    const d = new Date(date)
    return d.toLocaleString('ru-RU')
  },

  /**
   * Генерация ID игрока
   */
  generatePlayerId() {
    return 'player_' + Math.random().toString(36).substr(2, 9)
  },

  /**
   * Логирование с типом
   */
  log(type, message, data = null) {
    const timestamp = new Date().toLocaleTimeString('ru-RU')
    const prefix = `[${timestamp}]`
    
    switch (type) {
      case 'info':
        console.log(`${prefix} ℹ️ ${message}`, data || '')
        break
      case 'success':
        console.log(`${prefix} ✅ ${message}`, data || '')
        break
      case 'warning':
        console.warn(`${prefix} ⚠️ ${message}`, data || '')
        break
      case 'error':
        console.error(`${prefix} ❌ ${message}`, data || '')
        break
      case 'debug':
        console.debug(`${prefix} 🐛 ${message}`, data || '')
        break
      default:
        console.log(`${prefix} ${message}`, data || '')
    }
  }
}

// ============================================================================
// ОБРАБОТЧИК ОШИБОК
// ============================================================================

app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', instance?.$options.name)
  console.error('Info:', info)
}

// ============================================================================
// ОБРАБОТЧИК ПРЕДУПРЕЖДЕНИЙ
// ============================================================================

app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Vue Warning:', msg)
  console.warn('Trace:', trace)
}

// ============================================================================
// МОНТИРОВАНИЕ ПРИЛОЖЕНИЯ
// ============================================================================

app.mount('#app')

// ============================================================================
// ЛОГИРОВАНИЕ ЗАПУСКА
// ============================================================================

console.log('%c🚀 StarCourier Web Frontend', 'font-size: 20px; font-weight: bold; color: #fbbf24;')
console.log('%cОкружение: ' + import.meta.env.MODE, 'color: #60a5fa;')
console.log('%cAPI URL: ' + API_URL, 'color: #34d399;')
console.log('%cВерсия: 1.0.0', 'color: #a78bfa;')