/**
 * StarCourier Web - Card Component
 * Универсальная карточка с вариантами
 */

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** Вариант карточки */
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'elevated', 'outlined', 'interactive'].includes(value)
  },
  
  /** Размер */
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  
  /** С hover эффектом */
  hoverable: {
    type: Boolean,
    default: false
  },
  
  /** С кликом */
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (props.clickable) {
    emit('click', event)
  }
}

const classes = computed(() => ({
  'card': true,
  [`card--${props.variant}`]: true,
  [`card--${props.size}`]: true,
  'card--hoverable': props.hoverable,
  'card--clickable': props.clickable
}))
</script>

<template>
  <div
    :class="classes"
    @click="handleClick"
  >
    <slot></slot>
  </div>
</template>

<style scoped>
/* ============================================================================
 * BASE STYLES
 * ============================================================================ */

.card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  transition: all var(--duration-300) var(--ease-in-out);
  overflow: hidden;
}

/* ============================================================================
 * VARIANTS
 * ============================================================================ */

/* Default */
.card--default {
  background: rgba(30, 41, 59, 0.5);
  border: var(--border-width-1) solid rgba(148, 163, 184, 0.1);
  box-shadow: var(--shadow-default);
}

/* Elevated */
.card--elevated {
  background: var(--color-surface);
  box-shadow: var(--shadow-xl);
}

/* Outlined */
.card--outlined {
  background: transparent;
  border: var(--border-width-2) solid var(--color-neutral-700);
}

/* Interactive */
.card--interactive {
  background: rgba(30, 41, 59, 0.5);
  border: var(--border-width-1) solid rgba(148, 163, 184, 0.1);
  cursor: pointer;
}

.card--interactive:hover {
  background: rgba(30, 41, 59, 0.7);
  border-color: var(--color-primary-500);
  transform: translateY(-4px);
  box-shadow: var(--shadow-primary);
}

/* ============================================================================
 * SIZES
 * ============================================================================ */

.card--sm {
  padding: var(--space-4);
}

.card--md {
  padding: var(--space-6);
}

.card--lg {
  padding: var(--space-8);
}

/* ============================================================================
 * HOVERABLE
 * ============================================================================ */

.card--hoverable:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

/* ============================================================================
 * CLICKABLE
 * ============================================================================ */

.card--clickable {
  cursor: pointer;
  user-select: none;
}

.card--clickable:active {
  transform: translateY(-2px);
}
</style>
