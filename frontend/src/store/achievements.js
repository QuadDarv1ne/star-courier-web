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
      },
      // New achievements
      knowledge_seeker: {
        id: 'knowledge_seeker',
        title: 'Искатель знаний',
        description: 'Достигните 80% знания',
        icon: '📚',
        secret: false
      },
      team_player: {
        id: 'team_player',
        title: 'Командный игрок',
        description: 'Достигните 90% командного духа',
        icon: '👥',
        secret: false
      },
      fuel_efficient: {
        id: 'fuel_efficient',
        title: 'Экономный пилот',
        description: 'Завершите игру с более чем 50% топлива',
        icon: '⛽',
        secret: false
      },
      peace_maker: {
        id: 'peace_maker',
        title: 'Миротворец',
        description: 'Завершите игру без снижения морали ниже 50%',
        icon: '🕊️',
        secret: false
      },
      danger_zone: {
        id: 'danger_zone',
        title: 'Зона опасности',
        description: 'Достигните 90% уровня опасности',
        icon: '⚠️',
        secret: true
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
    },
    
    /**
     * Получить секретные достижения
     */
    secretAchievements: (state) => (
      Object.values(state.achievements).filter(a => a.secret)
    ),
    
    /**
     * Получить обычные достижения
     */
    regularAchievements: (state) => (
      Object.values(state.achievements).filter(a => !a.secret)
    )
  },

  actions: {
    /**
     * Разблокировать достижение
     */
    unlockAchievement(achievementId) {
      if (!this.unlockedAchievements.has(achievementId)) {
        this.unlockedAchievements.add(achievementId)
        // Return the achievement object for notification
        return this.achievements[achievementId] || null
      }
      return null
    },

    /**
     * Обновить прогресс достижения
     */
    updateProgress(achievementId, currentValue) {
      const achievement = this.achievements[achievementId]
      if (achievement && achievement.progress !== undefined) {
        achievement.progress = currentValue
        if (currentValue >= achievement.target) {
          return this.unlockAchievement(achievementId)
        }
      }
      return null
    },

    /**
     * Проверить условия достижений
     */
    checkAchievements(gameStore) {
      const unlocked = []
      
      // Проверяем первый выбор
      if (gameStore.choicesMade >= 1) {
        const achievement = this.unlockAchievement('first_choice')
        if (achievement) unlocked.push(achievement)
      }

      // Проверяем здоровье для достижения "Выживший"
      if (gameStore.stats.health <= 20 && gameStore.stats.health > 0) {
        const achievement = this.unlockAchievement('survivor')
        if (achievement) unlocked.push(achievement)
      }

      // Обновляем прогресс денег
      const richCourier = this.updateProgress('rich_courier', gameStore.stats.money)
      if (richCourier) unlocked.push(richCourier)

      // Проверяем отношения с персонажами
      Object.values(gameStore.relationships).forEach(value => {
        if (value >= 100) {
          const achievement = this.unlockAchievement('trusted_friend')
          if (achievement) unlocked.push(achievement)
        }
      })

      // Обновляем прогресс исследователя
      const uniqueScenes = new Set(gameStore.visitedScenes)
      const explorer = this.updateProgress('explorer', uniqueScenes.size)
      if (explorer) unlocked.push(explorer)
      
      // Новые проверки
      // Искатель знаний
      if (gameStore.stats.knowledge >= 80) {
        const achievement = this.unlockAchievement('knowledge_seeker')
        if (achievement) unlocked.push(achievement)
      }
      
      // Командный игрок
      if (gameStore.stats.team >= 90) {
        const achievement = this.unlockAchievement('team_player')
        if (achievement) unlocked.push(achievement)
      }
      
      // Зона опасности
      if (gameStore.stats.danger >= 90) {
        const achievement = this.unlockAchievement('danger_zone')
        if (achievement) unlocked.push(achievement)
      }
      
      return unlocked
    },
    
    /**
     * Проверить достижения в конце игры
     */
    checkEndGameAchievements(gameStore) {
      const unlocked = []
      
      // Экономный пилот
      if (gameStore.stats.fuel > 50) {
        const achievement = this.unlockAchievement('fuel_efficient')
        if (achievement) unlocked.push(achievement)
      }
      
      // Миротворец (проверяем, что мораль никогда не опускалась ниже 50)
      // This would require tracking min morale throughout the game
      // For now, we'll just check the final value
      if (gameStore.stats.morale >= 50) {
        const achievement = this.unlockAchievement('peace_maker')
        if (achievement) unlocked.push(achievement)
      }
      
      return unlocked
    },
    
    /**
     * Сбросить прогресс достижений
     */
    resetAchievements() {
      this.unlockedAchievements.clear()
      // Reset progress for achievements with progress tracking
      Object.values(this.achievements).forEach(achievement => {
        if (achievement.progress !== undefined) {
          achievement.progress = 0
        }
      })
    },
    
    /**
     * Проверить, разблокировано ли достижение
     */
    isUnlocked(achievementId) {
      return this.unlockedAchievements.has(achievementId)
    },
    
    /**
     * Получить прогресс достижения
     */
    getAchievementProgress(achievementId) {
      const achievement = this.achievements[achievementId]
      if (!achievement) return 0
      if (achievement.progress === undefined) return this.isUnlocked(achievementId) ? 100 : 0
      return Math.round((achievement.progress / achievement.target) * 100)
    }
  }
})