<!-- Achievement notification component -->
<template>
  <Transition name="achievement">
    <div v-if="show && achievement" class="achievement-notification" @click="dismiss">
      <div class="achievement-icon">{{ achievement.icon }}</div>
      <div class="achievement-info">
        <h4>{{ achievement.title }}</h4>
        <p>{{ achievement.description }}</p>
      </div>
      <div class="achievement-dismiss">✕</div>
    </div>
  </Transition>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'AchievementNotification',

  props: {
    achievement: {
      type: Object,
      default: null
    },
    show: {
      type: Boolean,
      default: false
    }
  },

  emits: ['dismiss'],

  methods: {
    dismiss() {
      this.$emit('dismiss')
    }
  },
  
  watch: {
    show(newVal) {
      if (newVal && this.achievement) {
        console.log('🏆 Разблокировано достижение:', this.achievement.title)
      }
    }
  }
})
</script>

<style scoped>
.achievement-notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #fbbf24;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  min-width: 300px;
  transform-origin: bottom right;
}

.achievement-icon {
  font-size: 2rem;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(251, 191, 36, 0.1);
  border-radius: 0.375rem;
  animation: pulse 1s infinite;
}

.achievement-info {
  flex: 1;
}

.achievement-info h4 {
  color: #fbbf24;
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.achievement-info p {
  color: #e5e7eb;
  margin: 0;
  font-size: 0.875rem;
}

.achievement-dismiss {
  color: #9ca3af;
  font-size: 1.25rem;
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.achievement-dismiss:hover {
  color: #ef4444;
}

/* Анимации */
.achievement-enter-active {
  animation: achievement-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.achievement-leave-active {
  animation: achievement-out 0.3s ease-in;
}

@keyframes achievement-in {
  from {
    transform: scale(0.5);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes achievement-out {
  from {
    transform: scale(1);
    opacity: 1;
  }
  to {
    transform: scale(0.5);
    opacity: 0;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(251, 191, 36, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(251, 191, 36, 0);
  }
}
</style>