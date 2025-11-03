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
      
      // Проверяем, начата ли игра
      if (gameStore.isGameStarted) {
        next()
      } else {
        // Если игра не начата, перенаправляем на главную
        next('/')
      }
    }
  },

  {
    path: '/about',
    name: 'About',
    component: AboutView,
    meta: {
      title: 'StarCourier Web - О проекте',
      description: 'Информация о проекте, технологиях и авторе'
    }
  },

  // 404 страница (всегда последняя)
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: {
      title: 'StarCourier Web - Страница не найдена',
      description: 'Запрашиваемая страница не найдена'
    }
  }
]

// ============================================================================
// ROUTER INSTANCE
// ============================================================================

const router = createRouter({
  history: createWebHistory(),
  routes,
  
  // Scroll behavior
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// ============================================================================
// GLOBAL NAVIGATION GUARDS
// ============================================================================

// Before each route change
router.beforeEach((to, from, next) => {
  // Update document title and meta tags
  document.title = to.meta.title || 'StarCourier Web'
  
  // Update meta description
  const metaDescription = document.querySelector('meta[name="description"]')
  if (metaDescription) {
    metaDescription.setAttribute('content', to.meta.description || 'Интерактивная текстовая RPG в космосе')
  }
  
  // Clear notifications when navigating
  const app = document.getElementById('app')
  if (app && app.__vue_app__) {
    const appInstance = app.__vue_app__
    // This is a simplified approach - in a real app you might want to use a global event bus
  }
  
  next()
})

// After each route change
router.afterEach((to, from) => {
  // Log page views for analytics (if implemented)
  console.log(`📍 Navigated to: ${to.path}`)
  
  // Clear cache when navigating away from game
  if (from.name === 'Game' && to.name !== 'Game') {
    const gameStore = useGameStore()
    if (gameStore) {
      gameStore.clearCaches()
    }
  }
})

export default router