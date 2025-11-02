<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero">
      <!-- Animated Background -->
      <div class="hero-background">
        <div class="star" v-for="i in 50" :key="i" :style="getStarStyle(i)"></div>
      </div>
      
      <div class="hero-content">
        <div class="hero-emoji">🚀</div>
        <h1 class="hero-title">STAR COURIER</h1>
        <p class="hero-subtitle">Интерактивная текстовая RPG в космической тематике</p>
        <p class="hero-description">
          Вы — капитан Макс Велл. Управляйте звездолётом «Элея», раскрывайте тайны 
          древних артефактов, развивайте отношения с командой и определяйте судьбу человечества.
        </p>
        
        <div class="hero-buttons">
          <button 
            class="btn btn-primary" 
            @click="handleStartGame"
            @mouseenter="() => $utils.$audio.playSoundEffect('buttonClick')"
            :disabled="loading"
          >
            {{ loading ? '⏳ Загрузка...' : '🎮 Начать приключение' }}
          </button>
          <button class="btn btn-secondary" @click="scrollToInfo">
            📖 О проекте
          </button>
        </div>

        <div v-if="error" class="error-message">
          <span class="error-icon">❌</span>
          <span class="error-text">{{ error }}</span>
        </div>
      </div>

      <div class="hero-background">
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features" ref="infoSection">
      <div class="features-container">
        <h2 class="section-title">✨ Особенности игры</h2>
        
        <div class="features-grid">
          <!-- Feature 1 -->
          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Интерактивный сюжет</h3>
            <p>15+ сцен с множественными развилками. Ваши выборы определяют исход истории.</p>
          </div>

          <!-- Feature 2 -->
          <div class="feature-card">
            <div class="feature-icon">👥</div>
            <h3>Система отношений</h3>
            <p>Развивайте отношения с членами команды: Сара Нова, Гриша Романов, Ли Чжэнь.</p>
          </div>

          <!-- Feature 3 -->
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Динамическая статистика</h3>
            <p>Здоровье, мораль, знание, команда, опасность и другие параметры.</p>
          </div>

          <!-- Feature 4 -->
          <div class="feature-card">
            <div class="feature-icon">🌌</div>
            <h3>Атмосфера космоса</h3>
            <p>Научная фантастика, мистика, алхимия и древние цивилизации.</p>
          </div>

          <!-- Feature 5 -->
          <div class="feature-card">
            <div class="feature-icon">🎭</div>
            <h3>Несколько концовок</h3>
            <p>5+ разных финалов в зависимости от ваших решений.</p>
          </div>

          <!-- Feature 6 -->
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Быстрая игра</h3>
            <p>Средняя продолжительность 30-45 минут. Можно пройти несколько раз.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Characters Section -->
    <section class="characters">
      <div class="characters-container">
        <h2 class="section-title">👥 Ваша команда</h2>
        
        <div class="characters-grid">
          <!-- Character 1 -->
          <div class="character-card">
            <div class="character-avatar">👩‍🔬</div>
            <h3>Сара Нова</h3>
            <p class="character-role">Главный научный офицер</p>
            <p class="character-description">Холодная, расчётливая, но с добрым сердцем. Разбирается в артефактах и древних технологиях.</p>
          </div>

          <!-- Character 2 -->
          <div class="character-card">
            <div class="character-avatar">🎖️</div>
            <h3>Гриша Романов</h3>
            <p class="character-role">Боевой офицер</p>
            <p class="character-description">Верный боец, опытный воин. Готов защищать команду от любых опасностей.</p>
          </div>

          <!-- Character 3 -->
          <div class="character-card">
            <div class="character-avatar">🧭</div>
            <h3>Ли Чжэнь</h3>
            <p class="character-role">Навигатор</p>
            <p class="character-description">Загадочная, хранительница древних тайн. Знает больше, чем кажется на первый взгляд.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-preview">
      <div class="stats-container">
        <h2 class="section-title">📊 Система статистики</h2>
        
        <div class="stats-grid">
          <div class="stat-preview-item">
            <span class="stat-emoji">❤️</span>
            <span class="stat-name">Здоровье</span>
            <span class="stat-desc">Физическое состояние</span>
          </div>

          <div class="stat-preview-item">
            <span class="stat-emoji">💪</span>
            <span class="stat-name">Мораль</span>
            <span class="stat-desc">Психическое состояние</span>
          </div>

          <div class="stat-preview-item">
            <span class="stat-emoji">🧠</span>
            <span class="stat-name">Знание</span>
            <span class="stat-desc">Понимание ситуации</span>
          </div>

          <div class="stat-preview-item">
            <span class="stat-emoji">👥</span>
            <span class="stat-name">Команда</span>
            <span class="stat-desc">Боевой дух</span>
          </div>

          <div class="stat-preview-item">
            <span class="stat-emoji">⚠️</span>
            <span class="stat-name">Опасность</span>
            <span class="stat-desc">Уровень угрозы</span>
          </div>

          <div class="stat-preview-item">
            <span class="stat-emoji">⛽</span>
            <span class="stat-name">Топливо</span>
            <span class="stat-desc">Запас ресурсов</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2>🚀 Готовы начать одиссею?</h2>
        <p>Отправляйтесь в космический полёт и раскройте тайны вселенной!</p>
        <button 
          class="btn btn-large" 
          @click="handleStartGame"
          :disabled="loading"
        >
          {{ loading ? '⏳ Загрузка...' : '🎮 Начать игру прямо сейчас' }}
        </button>
      </div>
    </section>

    <!-- Info Section -->
    <section class="info-section">
      <div class="info-container">
        <h2 class="section-title">ℹ️ Информация о проекте</h2>
        
        <div class="info-content">
          <div class="info-item">
            <h3>🛠️ Технологии</h3>
            <p>
              Frontend: Vue.js 3, Pinia, Vite<br>
              Backend: FastAPI, Python<br>
              Database: SQLite (разработка), PostgreSQL (продакшен)
            </p>
          </div>

          <div class="info-item">
            <h3>📄 Лицензия</h3>
            <p>MIT License - свободное использование и модификация</p>
          </div>

          <div class="info-item">
            <h3>👨‍💻 Автор</h3>
            <p>
              QuadDarv1ne<br>
              <a href="https://orcid.org/0009-0007-7605-539X" target="_blank">ORCID</a> |
              <a href="https://github.com/QuadDarv1ne" target="_blank">GitHub</a>
            </p>
          </div>

          <div class="info-item">
            <h3>🌐 Исходный код</h3>
            <p>
              <a href="https://github.com/QuadDarv1ne/star-courier-web" target="_blank">
                github.com/QuadDarv1ne/star-courier-web
              </a>
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../store/game'

export default defineComponent({
  name: 'HomeView',

  setup() {
    const router = useRouter()
    const gameStore = useGameStore()

    return {
      router,
      gameStore
    }
  },

  data() {
    return {
      loading: false,
      error: null
    }
  },

  methods: {
    /**
     * Генерировать стиль для звезды
     */
    getStarStyle(index) {
      const size = Math.random() * 3 + 1
      const top = Math.random() * 100
      const left = Math.random() * 100
      const opacity = Math.random() * 0.8 + 0.2
      const animationDelay = Math.random() * 5
      
      return {
        width: `${size}px`,
        height: `${size}px`,
        top: `${top}%`,
        left: `${left}%`,
        opacity: opacity,
        animationDelay: `${animationDelay}s`
      }
    },
    
    /**
     * Обработчик начала игры
     */
    async handleStartGame() {
      this.loading = true
      this.error = null

      try {
        this.$utils.log('info', 'Начало игры...')
        
        // Инициализируем игру через store
        await this.gameStore.initializeGame()

        this.$utils.log('success', 'Игра инициализирована')
        
        // Переходим на игровой экран
        await this.$router.push('/game')
      } catch (err) {
        this.$utils.log('error', 'Ошибка при начале игры', err)
        this.error = 'Ошибка подключения к серверу. Убедитесь, что backend запущен.'
        
        // Показываем уведомление
        this.$root.showNotification(
          'Ошибка при подключении к серверу',
          'error'
        )
      } finally {
        this.loading = false
      }
    },

    /**
     * Прокрутка к секции информации
     */
    scrollToInfo() {
      this.$refs.infoSection?.scrollIntoView({ behavior: 'smooth' })
    }
  },

  mounted() {
    this.$utils.log('info', 'HomeView mounted')
  }
})
</script>

<style scoped>
/* ======================== GENERAL ======================== */

.home-view {
  width: 100%;
  overflow-x: hidden;
}

.section-title {
  font-size: 2.5rem;
  color: #fbbf24;
  text-align: center;
  margin-bottom: 3rem;
  font-weight: bold;
  text-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
}

/* ======================== HERO SECTION ======================== */

.hero {
  position: relative;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #44260e 50%, #0f172a 100%);
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.star {
  position: absolute;
  background: #fbbf24;
  border-radius: 50%;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 600px;
  background: rgba(17, 24, 39, 0.7);
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  border: 2px solid #92400e;
}

.hero-emoji {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
  text-shadow: 0 0 20px rgba(251, 191, 36, 0.8);
}

.hero-title {
  font-size: 3.5rem;
  color: #fbbf24;
  margin-bottom: 0.5rem;
  font-weight: bold;
  text-shadow: 0 0 30px rgba(251, 191, 36, 0.5);
  letter-spacing: 2px;
  position: relative;
  padding-bottom: 1rem;
}

.hero-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 3px;
  background: linear-gradient(90deg, transparent, #fbbf24, transparent);
}

.hero-subtitle {
  font-size: 1.5rem;
  color: #fcd34d;
  margin-bottom: 1.5rem;
  font-style: italic;
}

.hero-description {
  font-size: 1.1rem;
  color: #d1d5db;
  line-height: 1.8;
  margin-bottom: 2rem;
  text-align: justify;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

/* ======================== BUTTONS ======================== */

.btn {
  padding: 1rem 2rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(217, 119, 6, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(217, 119, 6, 0.6);
}

.btn-secondary {
  background: transparent;
  color: #fbbf24;
  border: 2px solid #fbbf24;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(251, 191, 36, 0.1);
  transform: translateY(-2px);
}

.btn-large {
  padding: 1.25rem 2.5rem;
  font-size: 1.125rem;
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(217, 119, 6, 0.4);
}

.btn-large:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(217, 119, 6, 0.6);
}

/* Error Message */

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(127, 29, 29, 0.5);
  border: 1px solid #dc2626;
  padding: 1rem;
  border-radius: 0.5rem;
  color: #fca5a5;
}

.error-icon {
  font-size: 1.25rem;
}

.error-text {
  flex: 1;
}

/* ======================== FEATURES SECTION ======================== */

.features {
  padding: 4rem 2rem;
  background: rgba(30, 41, 59, 0.5);
}

.features-container {
  max-width: 1200px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #92400e;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.feature-card:hover {
  transform: translateY(-5px);
  border-color: #fbbf24;
  box-shadow: 0 10px 30px rgba(251, 191, 36, 0.2);
}

.feature-card:hover::before {
  left: 100%;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
}

.feature-card h3 {
  color: #fbbf24;
  margin-bottom: 0.75rem;
  font-size: 1.25rem;
  text-shadow: 0 0 5px rgba(251, 191, 36, 0.3);
}

.feature-card p {
  color: #d1d5db;
  line-height: 1.6;
}

/* ======================== CHARACTERS SECTION ======================== */

.characters {
  padding: 4rem 2rem;
}

.characters-container {
  max-width: 1200px;
  margin: 0 auto;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.character-card {
  background: rgba(30, 41, 59, 0.7);
  border: 2px solid #92400e;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.character-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.character-card:hover {
  border-color: #fbbf24;
  box-shadow: 0 10px 30px rgba(251, 191, 36, 0.2);
  transform: translateY(-5px);
}

.character-card:hover::before {
  left: 100%;
}

.character-avatar {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
}

.character-card h3 {
  color: #fbbf24;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  text-shadow: 0 0 5px rgba(251, 191, 36, 0.3);
}

.character-role {
  color: #fcd34d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.character-description {
  color: #d1d5db;
  line-height: 1.6;
  font-size: 0.95rem;
  text-align: justify;
}

/* ======================== STATS PREVIEW SECTION ======================== */

.stats-preview {
  padding: 4rem 2rem;
  background: rgba(30, 41, 59, 0.5);
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-preview-item {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.5rem;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.3s;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.stat-preview-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: 0.5s;
}

.stat-preview-item:hover {
  border-color: #fbbf24;
  background: rgba(17, 24, 39, 0.9);
  transform: translateY(-5px);
}

.stat-preview-item:hover::before {
  left: 100%;
}

.stat-emoji {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
  animation: pulse 2s infinite;
}

.stat-name {
  display: block;
  color: #fbbf24;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 5px rgba(251, 191, 36, 0.3);
}

.stat-desc {
  display: block;
  color: #9ca3af;
  font-size: 0.875rem;
}

/* ======================== CTA SECTION ======================== */

.cta-section {
  padding: 4rem 2rem;
  background: linear-gradient(135deg, rgba(217, 119, 6, 0.2) 0%, rgba(234, 88, 12, 0.2) 100%);
  text-align: center;
  border: 2px solid #d97706;
  border-radius: 1rem;
  margin: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.cta-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, transparent, #fbbf24, transparent);
}

.cta-content h2 {
  font-size: 2.5rem;
  color: #fbbf24;
  margin-bottom: 1rem;
  text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
}

.cta-content p {
  font-size: 1.1rem;
  color: #d1d5db;
  margin-bottom: 2rem;
  text-align: center;
}

/* ======================== INFO SECTION ======================== */

.info-section {
  padding: 4rem 2rem;
}

.info-container {
  max-width: 1200px;
  margin: 0 auto;
}

.info-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.info-item {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid #92400e;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.info-item h3 {
  color: #fbbf24;
  margin-bottom: 1rem;
}

.info-item p {
  color: #d1d5db;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.info-item a {
  color: #fbbf24;
  text-decoration: none;
  transition: all 0.3s;
}

.info-item a:hover {
  text-decoration: underline;
}

/* ======================== RESPONSIVE ======================== */

@media (max-width: 768px) {
  .hero {
    min-height: 400px;
    padding: 2rem 1rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.125rem;
  }

  .hero-buttons {
    flex-direction: column;
  }

  .btn, .btn-large {
    width: 100%;
  }

  .section-title {
    font-size: 2rem;
  }

  .features-grid,
  .characters-grid,
  .stats-grid,
  .info-content {
    grid-template-columns: 1fr;
  }

  .cta-section {
    margin: 1rem;
  }

  .cta-content h2 {
    font-size: 1.75rem;
  }
}
</style>
