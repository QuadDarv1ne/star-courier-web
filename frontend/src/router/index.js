/**
 * Vue Router Configuration for StarCourier Web
 * Manages application routing and navigation
 * 
 * frontend\src\router\index.js
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useGameStore } from '../store/game'

// ============================================================================
// LAZY LOAD COMPONENTS
// ============================================================================

const HomeView = () => import('../views/HomeView.vue')
const GameView = () => import('../views/GameView.vue')
const AboutView = () => import('../views/AboutView.vue')
const NotFoundView = () => import('../views/NotFoundView.vue')

// ============================================================================
// ROUTES
// ============================================================================

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      title: 'StarCourier Web - Главная',
      description: 'Интерактивная текстовая RPG в космосе'
    }
  },

  {
    path: '/game',
    name: 'Game',
    component: GameView,
    meta: {
      title: 'StarCourier Web - Игра',
      description: 'Играйте в интерактивную новеллу',
      requiresGame: true // Требует начало игры
    },
    beforeEnter: (to, from, next) => {
      const gameStore = useGameStore()
      if (!gameStore.isGameStarted) {
        console.warn('⚠️ Игра не начата. Перенаправляем на главную.')
        next('/')
      } else {
        next()
      }
    }
  },

  {
    path: '/about',
    name: 'About',
    component: AboutView,
    meta: {
      title: 'StarCourier Web - О проекте',
      description: 'Информация о проекте StarCourier Web'
    }
  },

  // Catch-all для 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: {
      title: 'Страница не найдена',
      description: '404 - Страница не найдена'
    }
  }
]

// ============================================================================
// CREATE ROUTER INSTANCE
// ============================================================================

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // Плавная прокрутка вверх при переходе
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// ============================================================================
// GLOBAL GUARDS
// ============================================================================

/**
 * Before Each Guard - Выполняется ДО каждой навигации
 */
router.beforeEach((to, from, next) => {
  // Обновляем title страницы
  const title = to.meta.title || 'StarCourier Web'
  document.title = title

  console.log(`📍 Навигация: ${from.name || 'Start'} → ${to.name}`)

  // Логируем мета информацию
  if (to.meta.requiresGame) {
    console.log('🎮 Требуется активная игра')
  }

  next()
})

/**
 * After Each Guard - Выполняется ПОСЛЕ каждой навигации
 */
router.afterEach((to, from) => {
  // Отправляем событие (например, для аналитики)
  if (window.gtag) {
    window.gtag('config', 'GA_ID', {
      page_path: to.path,
      page_title: to.meta.title
    })
  }

  console.log(`✅ Загружена страница: ${to.name}`)
})

/**
 * On Error Guard - Обработчик ошибок навигации
 */
router.onError((error) => {
  console.error('❌ Router Error:', error)
})

// ============================================================================
// ROUTE HELPER FUNCTIONS
// ============================================================================

/**
 * Перейти на главную
 */
export function goHome() {
  router.push('/')
}

/**
 * Перейти в игру
 */
export function goGame() {
  router.push('/game')
}

/**
 * Перейти к информации
 */
export function goAbout() {
  router.push('/about')
}

/**
 * Перейти на 404
 */
export function goNotFound() {
  router.push('/404')
}

/**
 * Вернуться назад
 */
export function goBack() {
  router.back()
}

/**
 * Перейти на путь
 */
export function navigateTo(path) {
  router.push(path)
}

// ============================================================================
// EXPORT
// ============================================================================

export default router