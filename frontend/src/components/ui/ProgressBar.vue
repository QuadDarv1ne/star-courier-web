/**
 * StarCourier Web - Progress Bar Component
 * Анимированный прогресс бар с вариантами
 */

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** Значение прогресса (0-100) */
  value: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100
  },
  
  /** Вариант цвета */
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger', 'accent', 'gradient'].includes(value)
  },
  
  /** Размер */
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  
  /** Показывать текст */
  showText: {
    type: Boolean,
    default: false
  },
  
  /** Анимировать */
  animated: {
    type: Boolean,
    default: true
  },
  
  /** Показывать полоски */
  striped: {
    type: Boolean,
    default: false
  }
})

const normalizedValue = computed(() => {
  return Math.max(0, Math.min(100, props.value))
})

const classes = computed(() => ({
  'progress': true,
  [`progress--${props.variant}`]: true,
  [`progress--${props.size}`]: true,
  'progress--animated': props.animated,
  'progress--striped': props.striped
}))

const style = computed(() => ({
  '--progress-value': `${normalizedValue.value}%`
}))
</script>

<template>
  <div class="progress" :class="classes" :style="style">
    <!-- Background -->
    <div class="progress__track">
      <!-- Fill -->
      <div
        class="progress__fill"
        :style="{ width: `${normalizedValue}%` }"
      >
        <!-- Striped Pattern -->
        <div v-if="striped" class="progress__stripes"></div>
        
        <!-- Animated Shine -->
        <div v-if="animated" class="progress__shine"></div>
      </div>
    </div>
    
    <!-- Text Label -->
    <div v-if="showText" class="progress__label">
      {{ Math.round(normalizedValue) }}%
    </div>
  </div>
</template>

<style scoped>
/* ============================================================================
 * BASE STYLES
 * ============================================================================ */

.progress {
  position: relative;
  width: 100%;
}

.progress__track {
  width: 100%;
  height: 100%;
  background: rgba(148, 163, 184, 0.2);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-500) var(--ease-in-out);
  position: relative;
  overflow: hidden;
}

/* ============================================================================
 * SIZES
 * ============================================================================ */

.progress--sm {
  height: 4px;
}

.progress--md {
  height: 8px;
}

.progress--lg {
  height: 12px;
}

/* ============================================================================
 * VARIANTS
 * ============================================================================ */

/* Primary */
.progress--primary .progress__fill {
  background: linear-gradient(
    90deg,
    var(--color-primary-600),
    var(--color-primary-500)
  );
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

/* Success */
.progress--success .progress__fill {
  background: linear-gradient(
    90deg,
    var(--color-success-600),
    var(--color-success-500)
  );
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

/* Warning */
.progress--warning .progress__fill {
  background: linear-gradient(
    90deg,
    var(--color-warning-600),
    var(--color-warning-500)
  );
  box-shadow: 0 0 10px rgba(249, 115, 22, 0.5);
}

/* Danger */
.progress--danger .progress__fill {
  background: linear-gradient(
    90deg,
    var(--color-danger-600),
    var(--color-danger-500)
  );
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

/* Accent */
.progress--accent .progress__fill {
  background: linear-gradient(
    90deg,
    var(--color-accent-600),
    var(--color-accent-500)
  );
  box-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
}

/* Gradient */
.progress--gradient .progress__fill {
  background: linear-gradient(
    90deg,
    var(--color-primary-500),
    var(--color-accent-500),
    var(--color-secondary-500)
  );
  box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
}

/* ============================================================================
 * STRIPED
 * ============================================================================ */

.progress__stripes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
}

/* ============================================================================
 * ANIMATED
 * ============================================================================ */

.progress--animated .progress__shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shine 2s infinite;
}

@keyframes shine {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

/* ============================================================================
 * LABEL
 * ============================================================================ */

.progress__label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: var(--color-neutral-0);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  z-index: 1;
}
</style>
