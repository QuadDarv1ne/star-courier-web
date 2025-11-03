<template>
  <div class="mini-game-overlay" @click="closeGame">
    <div class="mini-game-container" @click.stop>
      <div class="mini-game-header">
        <h3>🎮 Мини-игра: Взлом системы</h3>
        <button class="close-button" @click="closeGame">×</button>
      </div>
      
      <div class="mini-game-content">
        <!-- Game Instructions -->
        <div v-if="gameState === 'instructions'" class="instructions">
          <p>Вам нужно взломать систему безопасности, соединяя пары одинаковых символов.</p>
          <p>Кликайте на две одинаковые карты, чтобы удалить их. Очистите всё поле, чтобы получить награду!</p>
          <div class="difficulty-selector">
            <label>Сложность:</label>
            <select v-model="difficulty">
              <option value="easy">Лёгкая</option>
              <option value="medium">Средняя</option>
              <option value="hard">Сложная</option>
            </select>
          </div>
          <button class="start-button" @click="startGame">Начать игру</button>
        </div>
        
        <!-- Game Board -->
        <div v-else-if="gameState === 'playing'" class="game-board">
          <div class="game-info">
            <div class="timer">⏱️ {{ formatTime(timeLeft) }}</div>
            <div class="moves">Шаги: {{ moves }}</div>
            <div class="pairs">Пары: {{ foundPairs }}/{{ totalPairs }}</div>
          </div>
          
          <div class="board" :class="difficulty">
            <div 
              v-for="(card, index) in board" 
              :key="index"
              :class="['card', { flipped: card.flipped, matched: card.matched }]"
              @click="flipCard(index)"
            >
              <div class="card-inner">
                <div class="card-front">?</div>
                <div class="card-back">{{ card.symbol }}</div>
              </div>
            </div>
          </div>
          
          <div v-if="gameResult" class="game-result">
            <div :class="['result-message', gameResult]">
              <span v-if="gameResult === 'win'">🎉 Победа! Вы получаете {{ reward }} кредитов!</span>
              <span v-else>💀 Время вышло! Попробуйте ещё раз.</span>
            </div>
            <button class="play-again" @click="resetGame">Играть снова</button>
            <button class="exit-game" @click="closeGame">Выйти</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'MiniGame',
  
  emits: ['close', 'win'],
  
  data() {
    return {
      gameState: 'instructions', // instructions, playing, finished
      difficulty: 'medium',
      timeLeft: 60,
      moves: 0,
      foundPairs: 0,
      totalPairs: 0,
      board: [],
      flippedCards: [],
      timer: null,
      gameResult: null, // win, lose
      symbols: ['🚀', '🛸', '👽', '🤖', '🌌', '⭐', '💥', '⚡', '🔮', '🔒', '🔑', '💻']
    }
  },
  
  computed: {
    reward() {
      const baseReward = 100
      const difficultyMultiplier = {
        easy: 0.5,
        medium: 1,
        hard: 2
      }
      return Math.floor(baseReward * difficultyMultiplier[this.difficulty] * (this.timeLeft / 60))
    }
  },
  
  methods: {
    startGame() {
      this.gameState = 'playing'
      this.setupGame()
      this.startTimer()
    },
    
    setupGame() {
      // Reset game state
      this.moves = 0
      this.foundPairs = 0
      this.flippedCards = []
      this.gameResult = null
      
      // Set time based on difficulty
      const timeSettings = {
        easy: 90,
        medium: 60,
        hard: 45
      }
      this.timeLeft = timeSettings[this.difficulty]
      
      // Create board based on difficulty
      let pairs = 8
      if (this.difficulty === 'easy') pairs = 6
      if (this.difficulty === 'hard') pairs = 10
      
      this.totalPairs = pairs
      
      // Create card pairs
      const selectedSymbols = this.symbols.slice(0, pairs)
      const cardPairs = [...selectedSymbols, ...selectedSymbols]
      
      // Shuffle cards
      const shuffled = this.shuffleArray(cardPairs)
      
      // Create board
      this.board = shuffled.map(symbol => ({
        symbol,
        flipped: false,
        matched: false
      }))
    },
    
    shuffleArray(array) {
      const newArray = [...array]
      for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]]
      }
      return newArray
    },
    
    startTimer() {
      if (this.timer) clearInterval(this.timer)
      
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.endGame('lose')
        }
      }, 1000)
    },
    
    flipCard(index) {
      // Don't flip if card is already flipped or matched
      if (this.board[index].flipped || this.board[index].matched) return
      
      // Don't flip if two cards are already flipped
      if (this.flippedCards.length >= 2) return
      
      // Flip the card
      this.board[index].flipped = true
      this.flippedCards.push(index)
      
      // Check for match when two cards are flipped
      if (this.flippedCards.length === 2) {
        this.moves++
        const [firstIndex, secondIndex] = this.flippedCards
        const firstCard = this.board[firstIndex]
        const secondCard = this.board[secondIndex]
        
        if (firstCard.symbol === secondCard.symbol) {
          // Match found
          firstCard.matched = true
          secondCard.matched = true
          this.foundPairs++
          
          // Play sound effect
          this.$utils.$audio.playSoundEffect('achievementUnlocked')
          
          // Check for win
          if (this.foundPairs === this.totalPairs) {
            this.endGame('win')
          }
        } else {
          // No match, flip cards back after delay
          setTimeout(() => {
            this.board[firstIndex].flipped = false
            this.board[secondIndex].flipped = false
            this.flippedCards = []
          }, 1000)
        }
        
        // Clear flipped cards array
        if (firstCard.symbol === secondCard.symbol) {
          this.flippedCards = []
        }
      }
    },
    
    endGame(result) {
      this.gameResult = result
      clearInterval(this.timer)
      
      if (result === 'win') {
        // Emit win event with reward
        this.$emit('win', this.reward)
        
        // Play win sound
        this.$utils.$audio.playSoundEffect('choiceMade')
      } else {
        // Play lose sound
        this.$utils.$audio.playSoundEffect('gameOver')
      }
    },
    
    resetGame() {
      this.gameState = 'instructions'
      clearInterval(this.timer)
    },
    
    closeGame() {
      clearInterval(this.timer)
      this.$emit('close')
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
  },
  
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  }
})
</script>

<style scoped>
.mini-game-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.mini-game-container {
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #92400e;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
}

.mini-game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(17, 24, 39, 0.7);
  border-bottom: 1px solid #44260e;
}

.mini-game-header h3 {
  color: #fbbf24;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.2s;
}

.close-button:hover {
  color: #ef4444;
}

.mini-game-content {
  padding: 1.5rem;
}

.instructions p {
  color: #d1d5db;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.difficulty-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}

.difficulty-selector label {
  color: #fbbf24;
  font-weight: 600;
}

.difficulty-selector select {
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid #78350f;
  color: #d1d5db;
  padding: 0.5rem;
  border-radius: 0.25rem;
}

.start-button {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s;
  width: 100%;
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
}

.game-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.timer, .moves, .pairs {
  background: rgba(17, 24, 39, 0.7);
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  border: 1px solid #78350f;
  color: #fbbf24;
  font-weight: 600;
}

.board {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.board.easy {
  grid-template-columns: repeat(4, 1fr);
}

.board.medium {
  grid-template-columns: repeat(4, 1fr);
}

.board.hard {
  grid-template-columns: repeat(5, 1fr);
}

.card {
  aspect-ratio: 1;
  perspective: 1000px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.card.flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  font-size: 1.5rem;
}

.card-front {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
}

.card-back {
  background: rgba(30, 41, 59, 0.9);
  border: 2px solid #fbbf24;
  transform: rotateY(180deg);
}

.card.matched .card-back {
  background: rgba(34, 197, 94, 0.2);
  border-color: #22c55e;
}

.game-result {
  text-align: center;
}

.result-message {
  padding: 1rem;
  border-radius: 0.25rem;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.result-message.win {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border: 1px solid #22c55e;
}

.result-message.lose {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid #ef4444;
}

.play-again, .exit-game {
  background: transparent;
  border: 1px solid #fbbf24;
  color: #fbbf24;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 600;
  margin: 0 0.5rem;
  transition: all 0.3s;
}

.play-again:hover, .exit-game:hover {
  background: rgba(251, 191, 36, 0.1);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .board.easy, .board.medium {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .board.hard {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .game-info {
    flex-direction: column;
    align-items: center;
  }
  
  .timer, .moves, .pairs {
    width: 100%;
    text-align: center;
  }
}
</style>