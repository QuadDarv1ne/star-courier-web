/**
 * Achievements Store for StarCourier Web
 * Manages player achievements and progress tracking
 */

import { defineStore } from 'pinia'

export const useAchievementsStore = defineStore('achievements', {
  state: () => ({
    unlockedAchievements: new Set(),
    achievements: {
      first_choice: {
        id: 'first_choice',
        title: 'Первый выбор',
        description: 'Сделайте свой первый выбор в игре',
        icon: '🎯',
        secret: false
      },
      explorer: {
        id: 'explorer',
        title: 'Исследователь',
        description: 'Посетите 5 различных сцен',
        icon: '🗺️',
        secret: false,
        progress: 0,
        target: 5
      },
      survivor: {
        id: 'survivor',
        title: 'Выживший',
        description: 'Выживите с менее чем 20% здоровья',
        icon: '💪',
        secret: true
      },
      rich_courier: {
        id: 'rich_courier',
        title: 'Богатый курьер',
        description: 'Накопите 5000 кредитов',
        icon: '💰',
        secret: false,
        progress: 0,
        target: 5000
      },
      trusted_friend: {
        id: 'trusted_friend',
        title: 'Надёжный друг',
        description: 'Достигните 100% доверия с любым персонажем',
        icon: '🤝',
        secret: false
      }
    }
  }),

  getters: {
    /**
     * Получить все доступные достижения
     */
    allAchievements: (state) => Object.values(state.achievements),

    /**
     * Получить разблокированные достижения
     */
    unlockedAchievementsList: (state) => (
      Object.values(state.achievements).filter(a => state.unlockedAchievements.has(a.id))
    ),

    /**
     * Получить процент выполнения всех достижений
     */
    completionPercentage: (state) => {
      const total = Object.keys(state.achievements).length
      return Math.round((state.unlockedAchievements.size / total) * 100)
    }
  },

  actions: {
    /**
     * Разблокировать достижение
     */
    unlockAchievement(achievementId) {
      if (!this.unlockedAchievements.has(achievementId)) {
        this.unlockedAchievements.add(achievementId)
        return true
      }
      return false
    },

    /**
     * Обновить прогресс достижения
     */
    updateProgress(achievementId, currentValue) {
      const achievement = this.achievements[achievementId]
      if (achievement && achievement.progress !== undefined) {
        achievement.progress = currentValue
        if (currentValue >= achievement.target) {
          this.unlockAchievement(achievementId)
        }
      }
    },

    /**
     * Проверить условия достижений
     */
    checkAchievements(gameStore) {
      // Проверяем первый выбор
      if (gameStore.choicesMade === 1) {
        this.unlockAchievement('first_choice')
      }

      // Проверяем здоровье для достижения "Выживший"
      if (gameStore.stats.health <= 20 && gameStore.stats.health > 0) {
        this.unlockAchievement('survivor')
      }

      // Обновляем прогресс денег
      this.updateProgress('rich_courier', gameStore.stats.money)

      // Проверяем отношения с персонажами
      Object.values(gameStore.relationships).forEach(value => {
        if (value >= 100) {
          this.unlockAchievement('trusted_friend')
        }
      })

      // Обновляем прогресс исследователя
      const uniqueScenes = new Set(gameStore.visitedScenes)
      this.updateProgress('explorer', uniqueScenes.size)
    }
  }
})