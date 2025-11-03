<!-- Loading Indicator Component -->
<template>
  <div class="loading-indicator" :class="{ 'loading-overlay': overlay }">
    <div class="loading-content">
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
      <div v-if="message" class="loading-message">{{ message }}</div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LoadingIndicator',

  props: {
    message: {
      type: String,
      default: ''
    },
    overlay: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<style scoped>
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  text-align: center;
  background: rgba(30, 41, 59, 0.9);
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  border: 2px solid #fbbf24;
}

.loading-spinner {
  margin-bottom: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(251, 191, 36, 0.3);
  border-top: 5px solid #fbbf24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-message {
  color: #fbbf24;
  font-size: 1.1rem;
  font-weight: 600;
}
</style>