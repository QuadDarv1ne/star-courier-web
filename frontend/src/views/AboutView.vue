<!-- ================================================================ -->
<!-- FILE 1: src/views/AboutView.vue -->
<!-- ================================================================ -->

<template>
  <div class="about-view">
    <!-- Hero Section -->
    <section class="about-hero">
      <h1>О проекте StarCourier Web</h1>
      <p class="subtitle">Интерактивная текстовая RPG в космосе</p>
    </section>

    <!-- Main Content -->
    <section class="about-content">
      <div class="content-container">
        <!-- About Section -->
        <article class="about-section">
          <h2>📖 О проекте</h2>
          <p>
            <strong>StarCourier Web</strong> — это интерактивная текстовая RPG игра в космической тематике, 
            разработанная как демонстрация возможностей современного веб-фреймворка Vue.js и быстрого API на FastAPI.
          </p>
          <p>
            Игроки управляют капитаном Максом Веллом, командиром звездолёта "Элея", и принимают решения, 
            которые влияют на исход истории. Каждый выбор имеет последствия — изменяются статы персонажа 
            и отношения с членами команды.
          </p>
        </article>

        <!-- Game Features -->
        <article class="about-section">
          <h2>🎮 Особенности игры</h2>
          <ul class="features-list">
            <li>🎯 <strong>15+ интерактивных сцен</strong> с разветвлённым сюжетом</li>
            <li>👥 <strong>Система отношений</strong> с тремя персонажами команды</li>
            <li>📊 <strong>Динамическая статистика</strong> — здоровье, мораль, знание, команда и др.</li>
            <li>🏆 <strong>Система достижений</strong> — разблокируйте награды за действия</li>
            <li>💾 <strong>Сохранение игры</strong> — сохраняйте и загружайте прогресс</li>
            <li>🌌 <strong>Атмосфера космоса</strong> — научная фантастика, мистика, древние цивилизации</li>
            <li>🎭 <strong>Несколько концовок</strong> — исход зависит от ваших выборов</li>
          </ul>
        </article>

        <!-- Technology Stack -->
        <article class="about-section">
          <h2>⚙️ Технологический стек</h2>
          <div class="tech-grid">
            <div class="tech-item">
              <h3>Frontend</h3>
              <ul>
                <li>Vue.js 3 — современный фреймворк</li>
                <li>Pinia — управление состоянием</li>
                <li>Vue Router — навигация</li>
                <li>Axios — HTTP клиент</li>
                <li>Vite — сборщик проекта</li>
              </ul>
            </div>
            <div class="tech-item">
              <h3>Backend</h3>
              <ul>
                <li>FastAPI — быстрый фреймворк на Python</li>
                <li>Uvicorn — ASGI сервер</li>
                <li>Pydantic — валидация данных</li>
                <li>SQLAlchemy — ORM для БД</li>
                <li>PostgreSQL/SQLite — базы данных</li>
              </ul>
            </div>
            <div class="tech-item">
              <h3>DevOps</h3>
              <ul>
                <li>Docker — контейнеризация</li>
                <li>Git — контроль версий</li>
                <li>GitHub — хостинг кода</li>
                <li>Vite + Nginx — развёртывание</li>
              </ul>
            </div>
          </div>
        </article>

        <!-- Team & Author -->
        <article class="about-section">
          <h2>👨‍💻 Автор</h2>
          <div class="author-card">
            <div class="author-info">
              <h3>QuadDarv1ne</h3>
              <p class="author-bio">Разработчик и автор проекта StarCourier Web</p>
              <div class="author-links">
                <a href="https://github.com/QuadDarv1ne" target="_blank">GitHub</a>
                <a href="https://orcid.org/0009-0007-7605-539X" target="_blank">ORCID</a>
              </div>
            </div>
          </div>
        </article>

        <!-- License -->
        <article class="about-section">
          <h2>📄 Лицензия</h2>
          <p>
            Этот проект лицензирован под <strong>MIT License</strong> — 
            свободное использование, модификация и распространение с указанием авторства.
          </p>
          <p>
            Исходный код доступен на <a href="https://github.com/QuadDarv1ne/star-courier-web" target="_blank">GitHub</a>.
          </p>
        </article>

        <!-- Contributing -->
        <article class="about-section">
          <h2>🤝 Вклад в проект</h2>
          <p>
            Проект открыт для сотрудничества! Если вы хотите предложить идеи, 
            исправить ошибки или добавить контент, создавайте Pull Request на GitHub.
          </p>
          <div class="contribute-buttons">
            <a href="https://github.com/QuadDarv1ne/star-courier-web/issues" class="contribute-btn">
              Сообщить об ошибке
            </a>
            <a href="https://github.com/QuadDarv1ne/star-courier-web" class="contribute-btn">
              Посмотреть код
            </a>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'AboutView',
  
  mounted() {
    this.$utils.log('info', 'AboutView mounted')
  }
}
</script>

<style scoped>
/* ======================== GENERAL ======================== */

.about-view {
  width: 100%;
}

/* ======================== HERO ======================== */

.about-hero {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, rgba(217, 119, 6, 0.1) 0%, rgba(234, 88, 12, 0.1) 100%);
  border-bottom: 2px solid #d97706;
  margin-bottom: 3rem;
}

.about-hero h1 {
  font-size: 2.5rem;
  color: #fbbf24;
  margin-bottom: 0.5rem;
}

.about-hero .subtitle {
  font-size: 1.25rem;
  color: #fcd34d;
}

/* ======================== CONTENT ======================== */

.about-content {
  padding: 0 2rem;
}

.content-container {
  max-width: 900px;
  margin: 0 auto;
}

/* Sections */

.about-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #92400e;
  border-radius: 0.5rem;
}

.about-section h2 {
  font-size: 2rem;
  color: #fbbf24;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #92400e;
  padding-bottom: 1rem;
}

.about-section p {
  font-size: 1rem;
  color: #d1d5db;
  line-height: 1.8;
  margin-bottom: 1rem;
}

.about-section a {
  color: #fbbf24;
  text-decoration: none;
  transition: all 0.3s;
}

.about-section a:hover {
  text-decoration: underline;
  color: #fcd34d;
}

/* Features List */

.features-list {
  list-style: none;
  padding: 0;
}

.features-list li {
  padding: 0.75rem 0;
  color: #e0e7ff;
  border-bottom: 1px solid rgba(147, 64, 14, 0.3);
}

.features-list li:last-child {
  border-bottom: none;
}

/* Tech Grid */

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.tech-item {
  background: rgba(17, 24, 39, 0.7);
  border: 1px solid #78350f;
  border-radius: 0.375rem;
  padding: 1.5rem;
}

.tech-item h3 {
  color: #fbbf24;
  margin-bottom: 1rem;
}

.tech-item ul {
  list-style: none;
  padding: 0;
}

.tech-item li {
  color: #d1d5db;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(147, 64, 14, 0.2);
}

.tech-item li:last-child {
  border-bottom: none;
}

/* Author Card */

.author-card {
  background: rgba(17, 24, 39, 0.7);
  border: 2px solid #fbbf24;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
}

.author-info h3 {
  color: #fbbf24;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.author-bio {
  color: #d1d5db;
  margin-bottom: 1.5rem;
}

.author-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.author-links a {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: all 0.3s;
}

.author-links a:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
}

/* Contribute Buttons */

.contribute-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.contribute-btn {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  padding: 0.875rem 1.75rem;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: all 0.3s;
  display: inline-block;
}

.contribute-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(217, 119, 6, 0.6);
}

/* ======================== RESPONSIVE ======================== */

@media (max-width: 768px) {
  .about-hero {
    padding: 2rem 1rem;
  }

  .about-hero h1 {
    font-size: 2rem;
  }

  .about-section {
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .about-section h2 {
    font-size: 1.5rem;
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }

  .contribute-buttons {
    flex-direction: column;
  }

  .contribute-btn {
    width: 100%;
    text-align: center;
  }
}
</style>