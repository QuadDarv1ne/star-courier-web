/**
 * StarCourier Web - Frontend Tests
 * Tests for game store and utilities
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useGameStore } from '../src/store/game'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString() },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} }
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock import.meta.env
vi.mock('import.meta', () => ({
  env: {
    VITE_API_URL: 'http://localhost:8000'
  }
}))

describe('Game Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useGameStore()
      
      expect(store.isGameStarted).toBe(false)
      expect(store.isLoading).toBe(false)
      expect(store.playerId).toBe(null)
      expect(store.currentSceneId).toBe('start')
      expect(store.choicesMade).toBe(0)
    })

    it('should have correct initial stats', () => {
      const store = useGameStore()
      
      expect(store.stats.health).toBe(100)
      expect(store.stats.morale).toBe(75)
      expect(store.stats.knowledge).toBe(30)
      expect(store.stats.money).toBe(1000)
    })

    it('should have correct initial relationships', () => {
      const store = useGameStore()
      
      expect(store.relationships.sara_nova).toBe(50)
      expect(store.relationships.grisha_romanov).toBe(60)
      expect(store.relationships.li_zheng).toBe(45)
    })
  })

  describe('Getters', () => {
    it('should calculate game over correctly', () => {
      const store = useGameStore()
      
      expect(store.isGameOver).toBe(false)
      
      store.stats.health = 0
      expect(store.isGameOver).toBe(true)
      
      store.stats.health = 50
      store.stats.morale = 0
      expect(store.isGameOver).toBe(true)
    })

    it('should calculate game progress correctly', () => {
      const store = useGameStore()
      
      store.choicesMade = 0
      expect(store.gameProgress).toBe(0)
      
      store.choicesMade = 7
      expect(store.gameProgress).toBe(47)
      
      store.choicesMade = 15
      expect(store.gameProgress).toBe(100)
    })

    it('should determine game difficulty correctly', () => {
      const store = useGameStore()
      
      store.stats.danger = 10
      expect(store.gameDifficulty).toBe('Лёгкая')
      
      store.stats.danger = 30
      expect(store.gameDifficulty).toBe('Низкая')
      
      store.stats.danger = 50
      expect(store.gameDifficulty).toBe('Средняя')
      
      store.stats.danger = 70
      expect(store.gameDifficulty).toBe('Высокая')
      
      store.stats.danger = 90
      expect(store.gameDifficulty).toBe('Экстремальная')
    })

    it('should determine decision style correctly', () => {
      const store = useGameStore()
      
      expect(store.decisionStyle).toBe('Сбалансированный')
      
      store.decisionPatterns.aggressive = 10
      expect(store.decisionStyle).toBe('Агрессивный')
      
      store.decisionPatterns.diplomatic = 15
      expect(store.decisionStyle).toBe('Дипломатичный')
      
      store.decisionPatterns.analytical = 20
      expect(store.decisionStyle).toBe('Аналитический')
      
      store.decisionPatterns.caring = 25
      expect(store.decisionStyle).toBe('Заботливый')
    })

    it('should find favorite character correctly', () => {
      const store = useGameStore()
      
      let favorite = store.favoriteCharacter
      expect(favorite.name).toBe('Гриша Романов') // 60 is highest
      
      store.relationships.sara_nova = 80
      favorite = store.favoriteCharacter
      expect(favorite.name).toBe('Сара Нова')
      expect(favorite.relationship).toBe(80)
    })
  })

  describe('Actions', () => {
    it('should generate unique player ID', () => {
      const store = useGameStore()
      const id1 = store.generatePlayerId()
      const id2 = store.generatePlayerId()
      
      expect(id1).toMatch(/^player_[a-z0-9]+$/)
      expect(id2).toMatch(/^player_[a-z0-9]+$/)
      expect(id1).not.toBe(id2)
    })

    it('should reset game correctly', () => {
      const store = useGameStore()
      
      // Simulate a started game
      store.isGameStarted = true
      store.playerId = 'test_player'
      store.currentSceneId = 'scene_2'
      store.choicesMade = 5
      store.stats.health = 50
      store.stats.morale = 30
      
      store.resetGame()
      
      expect(store.isGameStarted).toBe(false)
      expect(store.playerId).toBe(null)
      expect(store.currentSceneId).toBe('start')
      expect(store.choicesMade).toBe(0)
      expect(store.stats.health).toBe(100)
      expect(store.stats.morale).toBe(75)
    })

    it('should save game to localStorage', () => {
      const store = useGameStore()
      
      store.isGameStarted = true
      store.playerId = 'test_player'
      store.currentSceneId = 'scene_2'
      store.choicesMade = 3
      
      const saveData = store.saveGame('Test Save')
      
      expect(saveData.name).toBe('Test Save')
      expect(saveData.playerId).toBe('test_player')
      expect(saveData.currentSceneId).toBe('scene_2')
      expect(saveData.choicesMade).toBe(3)
      
      const saved = JSON.parse(localStorage.getItem('starCourierSavedGames'))
      expect(saved.length).toBe(1)
      expect(saved[0].name).toBe('Test Save')
    })

    it('should load saved games from localStorage', () => {
      const store = useGameStore()
      
      // Add a saved game
      const saves = [{
        id: '123',
        name: 'Test Save',
        playerId: 'player_123',
        currentSceneId: 'scene_3',
        stats: { health: 80, morale: 70 },
        timestamp: new Date().toISOString()
      }]
      localStorage.setItem('starCourierSavedGames', JSON.stringify(saves))
      
      const loaded = store.loadAllSavedGames()
      
      expect(loaded.length).toBe(1)
      expect(loaded[0].name).toBe('Test Save')
      expect(store.savedGames.length).toBe(1)
    })

    it('should delete saved game', () => {
      const store = useGameStore()
      
      // Add saved games
      const saves = [
        { id: '1', name: 'Save 1' },
        { id: '2', name: 'Save 2' }
      ]
      localStorage.setItem('starCourierSavedGames', JSON.stringify(saves))
      store.loadAllSavedGames()
      
      store.deleteSave('1')
      
      const remaining = JSON.parse(localStorage.getItem('starCourierSavedGames'))
      expect(remaining.length).toBe(1)
      expect(remaining[0].id).toBe('2')
    })

    it('should clear all caches', () => {
      const store = useGameStore()
      
      // Add some cache data
      store.sceneCache.set('scene_1', { title: 'Test Scene' })
      store.characterCache.set('char_1', { name: 'Test Character' })
      
      expect(store.sceneCache.size).toBe(1)
      expect(store.characterCache.size).toBe(1)
      
      store.clearCaches()
      
      expect(store.sceneCache.size).toBe(0)
      expect(store.characterCache.size).toBe(0)
    })

    it('should get cache stats', () => {
      const store = useGameStore()
      
      store.sceneCache.set('scene_1', {})
      store.sceneCache.set('scene_2', {})
      store.characterCache.set('char_1', {})
      
      const stats = store.getCacheStats()
      
      expect(stats.scenes).toBe(2)
      expect(stats.characters).toBe(1)
    })
  })

  describe('Game State Validation', () => {
    it('should track visited scenes', () => {
      const store = useGameStore()
      
      expect(store.visitedScenes.has('start')).toBe(true)
      
      store.visitedScenes.add('scene_2')
      store.visitedScenes.add('scene_3')
      
      expect(store.visitedScenes.size).toBe(3)
    })

    it('should track decision patterns', () => {
      const store = useGameStore()
      
      store.updateDecisionPatterns('danger', 10)
      expect(store.decisionPatterns.aggressive).toBe(1)
      
      store.updateDecisionPatterns('trust', 10)
      expect(store.decisionPatterns.diplomatic).toBe(1)
      
      store.updateDecisionPatterns('knowledge', 10)
      expect(store.decisionPatterns.analytical).toBe(1)
      
      store.updateDecisionPatterns('team', 10)
      expect(store.decisionPatterns.caring).toBe(1)
    })

    it('should track stat history', () => {
      const store = useGameStore()
      
      expect(store.statHistory.health.min).toBe(100)
      expect(store.statHistory.health.max).toBe(100)
      
      // Simulate stat change
      store.stats.health = 80
      store.statHistory.health.min = Math.min(store.statHistory.health.min, 80)
      store.statHistory.health.max = Math.max(store.statHistory.health.max, 100)
      
      expect(store.statHistory.health.min).toBe(80)
      expect(store.statHistory.health.max).toBe(100)
    })
  })
})

describe('Utility Functions', () => {
  it('should format time correctly', () => {
    const formatTime = (totalSeconds) => {
      const hours = Math.floor(totalSeconds / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)
      const seconds = totalSeconds % 60
      
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    }
    
    expect(formatTime(0)).toBe('00:00:00')
    expect(formatTime(61)).toBe('00:01:01')
    expect(formatTime(3661)).toBe('01:01:01')
  })

  it('should clamp values correctly', () => {
    const clamp = (value, min, max) => Math.min(max, Math.max(min, value))
    
    expect(clamp(50, 0, 100)).toBe(50)
    expect(clamp(-10, 0, 100)).toBe(0)
    expect(clamp(150, 0, 100)).toBe(100)
  })
})
