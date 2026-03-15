/**
 * StarCourier Web - Button Component
 * Универсальная кнопка с вариантами стилей
 */

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** Тип кнопки */
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'accent', 'success', 'danger', 'warning', 'ghost', 'outline'].includes(value)
  },
  
  /** Размер кнопки */
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  
  /** Загрузка */
  loading: {
    type: Boolean,
    default: false
  },
  
  /** Отключена */
  disabled: {
    type: Boolean,
    default: false
  },
  
  /** Полная ширина */
  fullWidth: {
    type: Boolean,
    default: false
  },
  
  /** Иконка слева */
  leftIcon: {
    type: String,
    default: ''
  },
  
  /** Иконка справа */
  rightIcon: {
    type: String,
    default: ''
  },
  
  /** Тип кнопки */
  type: {
    type: String,
    default: 'button'
  }
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}

const classes = computed(() => ({
  'btn': true,
  [`btn--${props.variant}`]: true,
  [`btn--${props.size}`]: true,
  'btn--loading': props.loading,
  'btn--disabled': props.disabled,
  'btn--full-width': props.fullWidth
}))
</script>

<template>
  <button
    :class="classes"
    :type="type"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <span v-if="loading" class="btn__spinner">
      <svg class="spinner" viewBox="0 0 24 24">
        <circle class="path" cx="12" cy="12" r="10" fill="none" stroke-width="3" />
      </svg>
    </span>

    <!-- Left Icon -->
    <span v-if="leftIcon && !loading" class="btn__icon btn__icon--left">
      {{ leftIcon }}
    </span>

    <!-- Content -->
    <span class="btn__content">
      <slot></slot>
    </span>

    <!-- Right Icon -->
    <span v-if="rightIcon && !loading" class="btn__icon btn__icon--right">
      {{ rightIcon }}
    </span>
  </button>
</template>

<style scoped>
/* ============================================================================
 * BASE STYLES
 * ============================================================================ */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-family-sans);
  font-weight: var(--font-weight-semibold);
  text-align: center;
  white-space: nowrap;
  user-select: none;
  cursor: pointer;
  transition: all var(--duration-200) var(--ease-in-out);
  border: var(--border-width-2) solid transparent;
  border-radius: var(--radius-lg);
  position: relative;
  overflow: hidden;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn:active:not(:disabled) {
  transform: translateY(0);
}

.btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================================================
 * SIZES
 * ============================================================================ */

.btn--sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--font-size-sm);
  min-height: 32px;
}

.btn--md {
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-base);
  min-height: 40px;
}

.btn--lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--font-size-lg);
  min-height: 48px;
}

.btn--xl {
  padding: var(--space-4) var(--space-8);
  font-size: var(--font-size-xl);
  min-height: 56px;
}

/* ============================================================================
 * VARIANTS
 * ============================================================================ */

/* Primary */
.btn--primary {
  background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-700));
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-primary);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

/* Secondary */
.btn--secondary {
  background: linear-gradient(135deg, var(--color-secondary-500), var(--color-secondary-600));
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-secondary);
}

.btn--secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-secondary-400), var(--color-secondary-500));
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5);
}

/* Accent */
.btn--accent {
  background: linear-gradient(135deg, var(--color-accent-500), var(--color-accent-600));
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-accent);
}

.btn--accent:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-accent-400), var(--color-accent-500));
  box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5);
}

/* Success */
.btn--success {
  background: linear-gradient(135deg, var(--color-success-500), var(--color-success-600));
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-success);
}

.btn--success:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-success-400), var(--color-success-500));
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
}

/* Danger */
.btn--danger {
  background: linear-gradient(135deg, var(--color-danger-500), var(--color-danger-600));
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-danger);
}

.btn--danger:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-danger-400), var(--color-danger-500));
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5);
}

/* Warning */
.btn--warning {
  background: linear-gradient(135deg, var(--color-warning-500), var(--color-warning-600));
  color: var(--color-neutral-0);
  box-shadow: var(--shadow-secondary);
}

.btn--warning:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-warning-400), var(--color-warning-500));
}

/* Ghost */
.btn--ghost {
  background: transparent;
  color: var(--color-primary-500);
}

.btn--ghost:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.1);
}

/* Outline */
.btn--outline {
  background: transparent;
  border-color: var(--color-primary-500);
  color: var(--color-primary-500);
}

.btn--outline:hover:not(:disabled) {
  background: var(--color-primary-500);
  color: var(--color-neutral-0);
}

/* ============================================================================
 * STATES
 * ============================================================================ */

.btn--full-width {
  width: 100%;
}

.btn--loading {
  pointer-events: none;
}

.btn--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================================================
 * ICONS
 * ============================================================================ */

.btn__icon {
  display: inline-flex;
  font-size: 1.2em;
}

.btn__icon--left {
  margin-right: var(--space-1);
}

.btn__icon--right {
  margin-left: var(--space-1);
}

/* ============================================================================
 * SPINNER
 * ============================================================================ */

.btn__spinner {
  display: inline-flex;
  animation: spin 1s linear infinite;
}

.spinner {
  width: 1em;
  height: 1em;
}

.path {
  stroke: currentColor;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

/* ============================================================================
 * CONTENT
 * ============================================================================ */

.btn__content {
  position: relative;
  z-index: 1;
}
</style>
