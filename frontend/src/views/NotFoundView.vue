<template>
  <div class="not-found-view">
    <div class="not-found-content">
      <div class="not-found-emoji">🚀</div>
      <h1>404</h1>
      <h2>Страница не найдена</h2>
      <p>Похоже, вы залетели в неизвестный сектор космоса...</p>
      
      <div class="not-found-buttons">
        <router-link to="/" class="btn btn-primary">
          🏠 На главную
        </router-link>
        <router-link to="/game" class="btn btn-secondary">
          🎮 Играть
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>

<style scoped>
.not-found-view {
  min-height: calc(100vh - 300px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
}

.not-found-emoji {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
}

.not-found-content h1 {
  font-size: 4rem;
  color: #fbbf24;
  margin: 0;
  font-weight: bold;
}

.not-found-content h2 {
  font-size: 2rem;
  color: #fcd34d;
  margin: 0.5rem 0;
}

.not-found-content p {
  font-size: 1.1rem;
  color: #d1d5db;
  margin: 1.5rem 0 2rem 0;
}

.not-found-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.875rem 1.75rem;
  border-radius: 0.375rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(217, 119, 6, 0.6);
}

.btn-secondary {
  background: transparent;
  border: 2px solid #fbbf24;
  color: #fbbf24;
}

.btn-secondary:hover {
  background: rgba(251, 191, 36, 0.1);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .not-found-content h1 {
    font-size: 3rem;
  }

  .not-found-content h2 {
    font-size: 1.5rem;
  }

  .not-found-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>