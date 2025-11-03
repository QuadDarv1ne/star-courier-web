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
        secret: false,
        progress: 0,
        target: 1
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
        secret: true,
        progress: 0,
        target: 1
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
        secret: false,
        progress: 0,
        target: 100
      },
      // New achievements
      knowledge_seeker: {
        id: 'knowledge_seeker',
        title: 'Искатель знаний',
        description: 'Достигните 80% знания',
        icon: '📚',
        secret: false,
        progress: 0,
        target: 80
      },
      team_player: {
        id: 'team_player',
        title: 'Командный игрок',
        description: 'Достигните 90% командного духа',
        icon: '👥',
        secret: false,
        progress: 0,
        target: 90
      },
      fuel_efficient: {
        id: 'fuel_efficient',
        title: 'Экономный пилот',
        description: 'Завершите игру с более чем 50% топлива',
        icon: '⛽',
        secret: false,
        progress: 0,
        target: 50
      },
      peace_maker: {
        id: 'peace_maker',
        title: 'Миротворец',
        description: 'Завершите игру без снижения морали ниже 50%',
        icon: '🕊️',
        secret: false,
        progress: 0,
        target: 50
      },
      danger_zone: {
        id: 'danger_zone',
        title: 'Зона опасности',
        description: 'Достигните 90% уровня опасности',
        icon: '⚠️',
        secret: true,
        progress: 0,
        target: 90
      },
      // New achievements for version 2
      psychic_power: {
        id: 'psychic_power',
        title: 'Психическая сила',
        description: 'Развивайте психические способности до 75%',
        icon: '🔮',
        secret: false,
        progress: 0,
        target: 75
      },
      security_expert: {
        id: 'security_expert',
        title: 'Эксперт по безопасности',
        description: 'Достигните 95% уровня безопасности',
        icon: '🛡️',
        secret: false,
        progress: 0,
        target: 95
      },
      master_negotiator: {
        id: 'master_negotiator',
        title: 'Мастер переговоров',
        description: 'Пройдите 3 диалога, выбирая дипломатичные решения',
        icon: '🤝',
        secret: false,
        progress: 0,
        target: 3
      },
      time_traveler: {
        id: 'time_traveler',
        title: 'Путешественник во времени',
        description: 'Посетите все концовки игры',
        icon: '⏳',
        secret: true,
        progress: 0,
        target: 5 // Number of different endings
      },
      collector: {
        id: 'collector',
        title: 'Коллекционер',
        description: 'Соберите 10 предметов',
        icon: '🎒',
        secret: false,
        progress: 0,
        target: 10
      }
    },
    
    // Track special game events for achievements
    gameEvents: {
      diplomaticChoices: 0,
      endingsReached: new Set(),
      itemsCollected: 0
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
    ),
    
    /**
     * Получить достижения по категориям
     */
    achievementsByCategory: (state) => {
      const categories = {
        exploration: ['explorer', 'time_traveler'],
        survival: ['survivor', 'peace_maker'],
        social: ['trusted_friend', 'master_negotiator'],
        resources: ['rich_courier', 'fuel_efficient', 'collector'],
        skills: ['knowledge_seeker', 'psychic_power', 'security_expert'],
        teamwork: ['team_player'],
        challenge: ['danger_zone']
      }
      
      const result = {}
      Object.keys(categories).forEach(category => {
        result[category] = categories[category].map(id => state.achievements[id]).filter(Boolean)
      })
      
      return result
    }
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
      const firstChoice = this.updateProgress('first_choice', gameStore.choicesMade)
      if (firstChoice) unlocked.push(firstChoice)

      // Проверяем здоровье для достижения "Выживший"
      if (gameStore.stats.health <= 20 && gameStore.stats.health > 0) {
        const achievement = this.updateProgress('survivor', 1)
        if (achievement) unlocked.push(achievement)
      }

      // Обновляем прогресс денег
      const richCourier = this.updateProgress('rich_courier', gameStore.stats.money)
      if (richCourier) unlocked.push(richCourier)

      // Проверяем отношения с персонажами
      const maxRelationship = Math.max(...Object.values(gameStore.relationships))
      const trustedFriend = this.updateProgress('trusted_friend', maxRelationship)
      if (trustedFriend) unlocked.push(trustedFriend)

      // Обновляем прогресс исследователя
      const uniqueScenes = new Set(gameStore.visitedScenes)
      const explorer = this.updateProgress('explorer', uniqueScenes.size)
      if (explorer) unlocked.push(explorer)
      
      // Новые проверки
      // Искатель знаний
      const knowledgeSeeker = this.updateProgress('knowledge_seeker', gameStore.stats.knowledge)
      if (knowledgeSeeker) unlocked.push(knowledgeSeeker)
      
      // Командный игрок
      const teamPlayer = this.updateProgress('team_player', gameStore.stats.team)
      if (teamPlayer) unlocked.push(teamPlayer)
      
      // Зона опасности
      const dangerZone = this.updateProgress('danger_zone', gameStore.stats.danger)
      if (dangerZone) unlocked.push(dangerZone)
      
      // Психическая сила
      const psychicPower = this.updateProgress('psychic_power', gameStore.stats.psychic)
      if (psychicPower) unlocked.push(psychicPower)
      
      // Эксперт по безопасности
      const securityExpert = this.updateProgress('security_expert', gameStore.stats.security)
      if (securityExpert) unlocked.push(securityExpert)
      
      // Мастер переговоров
      const masterNegotiator = this.updateProgress('master_negotiator', this.gameEvents.diplomaticChoices)
      if (masterNegotiator) unlocked.push(masterNegotiator)
      
      // Коллекционер
      const collector = this.updateProgress('collector', this.gameEvents.itemsCollected)
      if (collector) unlocked.push(collector)
      
      return unlocked
    },
    
    /**
     * Проверить достижения в конце игры
     */
    checkEndGameAchievements(gameStore) {
      const unlocked = []
      
      // Экономный пилот
      const fuelEfficient = this.updateProgress('fuel_efficient', gameStore.stats.fuel)
      if (fuelEfficient) unlocked.push(fuelEfficient)
      
      // Миротворец (проверяем, что мораль никогда не опускалась ниже 50)
      // This would require tracking min morale throughout the game
      // For now, we'll just check the final value
      const peaceMaker = this.updateProgress('peace_maker', gameStore.stats.morale)
      if (peaceMaker) unlocked.push(peaceMaker)
      
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
      
      // Reset game events
      this.gameEvents = {
        diplomaticChoices: 0,
        endingsReached: new Set(),
        itemsCollected: 0
      }
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
    },
    
    /**
     * Record a diplomatic choice for achievements
     */
    recordDiplomaticChoice() {
      this.gameEvents.diplomaticChoices++
    },
    
    /**
     * Record an item collection for achievements
     */
    recordItemCollection() {
      this.gameEvents.itemsCollected++
    },
    
    /**
     * Record reaching an ending for achievements
     * @param {string} endingId - Identifier for the ending reached
     */
    recordEnding(endingId) {
      this.gameEvents.endingsReached.add(endingId)
      this.updateProgress('time_traveler', this.gameEvents.endingsReached.size)
    },
    
    /**
     * Add an item to inventory and track for achievements
     * @param {string} item - Item name to add
     */
    addItem(item) {
      this.recordItemCollection()
    },
    
    /**
     * Get achievement statistics
     */
    getAchievementStats() {
      const total = Object.keys(this.achievements).length
      const unlocked = this.unlockedAchievements.size
      const secret = Object.values(this.achievements).filter(a => a.secret).length
      const unlockedSecret = Object.values(this.achievements).filter(a => a.secret && this.unlockedAchievements.has(a.id)).length
      
      return {
        total,
        unlocked,
        locked: total - unlocked,
        percentage: Math.round((unlocked / total) * 100),
        secretTotal: secret,
        secretUnlocked: unlockedSecret
      }
    }
  }
})