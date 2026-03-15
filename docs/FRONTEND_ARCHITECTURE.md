# 🎨 StarCourier Web - Frontend Архитектура

Документация по архитектуре frontend приложения StarCourier Web.

---

## 📋 Содержание

- [Обзор архитектуры](#-обзор-архитектуры)
- [Структура проекта](#-структура-проекта)
- [Компоненты](#-компоненты)
- [Управление состоянием](#-управление-состоянием)
- [Стилизация](#-стилизация)
- [Производительность](#-производительность)

---

## 🎯 Обзор архитектуры

### Технологический стек

- **Фреймворк**: Vue.js 3.3+
- **State Management**: Pinia 2.1+
- **Роутинг**: Vue Router 4.2+
- **Сборка**: Vite 5.0+
- **HTTP клиент**: Axios 1.13+
- **Стилизация**: CSS Variables + Scoped CSS

### Архитектурные принципы

1. **Component Composition** - композиция компонентов
2. **Single Responsibility** - один компонент = одна ответственность
3. **Props Down, Events Up** - однонаправленный поток данных
4. **Lazy Loading** - ленивая загрузка компонентов
5. **Reactivity First** - реактивность по умолчанию

---

## 📁 Структура проекта

```
frontend/
├── src/
│   ├── assets/             # Статические ресурсы
│   │   ├── images/
│   │   ├── fonts/
│   │   └── sounds/
│   │
│   ├── components/         # Vue компоненты
│   │   ├── ui/             # UI компоненты общего назначения
│   │   │   ├── Button.vue
│   │   │   ├── Card.vue
│   │   │   ├── ProgressBar.vue
│   │   │   ├── Modal.vue
│   │   │   └── Input.vue
│   │   │
│   │   ├── game/           # Игровые компоненты
│   │   │   ├── GameView.vue
│   │   │   ├── SceneDisplay.vue
│   │   │   ├── ChoiceButton.vue
│   │   │   ├── StatsPanel.vue
│   │   │   └── InventoryPanel.vue
│   │   │
│   │   ├── character/      # Компоненты персонажей
│   │   │   ├── CharacterCard.vue
│   │   │   ├── RelationshipBar.vue
│   │   │   └── DialogueBox.vue
│   │   │
│   │   └── common/         # Общие компоненты
│   │       ├── LoadingIndicator.vue
│   │       ├── ErrorBoundary.vue
│   │       └── Notification.vue
│   │
│   ├── composables/        # Vue Composables (Composition API)
│   │   ├── index.js
│   │   ├── useAudio.js
│   │   ├── useLoading.js
│   │   ├── useModal.js
│   │   └── useNotification.js
│   │
│   ├── views/              # Страницы (Route views)
│   │   ├── HomeView.vue
│   │   ├── GameView.vue
│   │   ├── AboutView.vue
│   │   └── NotFoundView.vue
│   │
│   ├── store/              # Pinia stores
│   │   ├── game.js
│   │   ├── auth.js
│   │   ├── ui.js
│   │   └── achievements.js
│   │
│   ├── services/           # API сервисы
│   │   ├── api.js
│   │   ├── gameService.js
│   │   ├── authService.js
│   │   └── achievementsService.js
│   │
│   ├── styles/             # Глобальные стили
│   │   ├── tokens.css      # Design tokens
│   │   ├── main.css
│   │   ├── animations.css
│   │   ├── components.css
│   │   └── variables.css
│   │
│   ├── router/             # Конфигурация роутера
│   │   └── index.js
│   │
│   ├── plugins/            # Vue плагины
│   │   └── index.js
│   │
│   ├── locales/            # Интернационализация
│   │   ├── en.json
│   │   ├── ru.json
│   │   └── es.json
│   │
│   ├── types/              # JSDoc типы
│   │   └── index.js
│   │
│   ├── utils/              # Утилиты
│   │   ├── helpers.js
│   │   ├── constants.js
│   │   └── validators.js
│   │
│   ├── App.vue             # Корневой компонент
│   └── main.js             # Точка входа
│
├── public/                 # Публичные файлы
│   ├── manifest.json
│   ├── sw.js              # Service Worker
│   └── icons/
│
├── tests/                  # Тесты
│   ├── unit/
│   └── e2e/
│
├── index.html
├── package.json
├── vite.config.js
└── .eslintrc.json
```

---

## 🧩 Компоненты

### Иерархия компонентов

```
App.vue (Root)
│
├── Navbar
│
├── RouterView
│   ├── HomeView
│   │   └── HeroSection
│   │
│   ├── GameView
│   │   ├── GameSidebar
│   │   │   ├── CharacterInfo
│   │   │   ├── StatsGrid
│   │   │   └── RelationshipsPanel
│   │   │
│   │   ├── SceneDisplay
│   │   │   ├── SceneImage
│   │   │   ├── SceneTitle
│   │   │   └── SceneText
│   │   │
│   │   ├── ChoicesPanel
│   │   │   └── ChoiceButton (xN)
│   │   │
│   │   └── QuickActions
│   │       └── Modal (xN)
│   │
│   └── AboutView
│
└── Footer
```

### Типы компонентов

#### 1. UI Components (Базовые)

Переиспользуемые компоненты без бизнес-логики:

```vue
<!-- Button.vue -->
<script setup>
const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  loading: Boolean,
  disabled: Boolean
})

const emit = defineEmits(['click'])
</script>

<template>
  <button :class="['btn', `btn--${variant}`, `btn--${size}`]" @click="emit('click')">
    <slot></slot>
  </button>
</template>
```

#### 2. Feature Components (Бизнес-логика)

Компоненты с бизнес-логикой:

```vue
<!-- StatsPanel.vue -->
<script setup>
import { storeToRefs } from 'pinia'
import { useGameStore } from '@/store/game'
import ProgressBar from '@/components/ui/ProgressBar.vue'

const gameStore = useGameStore()
const { stats } = storeToRefs(gameStore)

const getStatColor = (statName) => {
  const colors = {
    health: 'danger',
    morale: 'warning',
    psychic: 'accent'
  }
  return colors[statName] || 'primary'
}
</script>

<template>
  <div class="stats-panel">
    <div v-for="(value, key) in stats" :key="key" class="stat-item">
      <span class="stat-label">{{ key }}</span>
      <ProgressBar :value="value" :variant="getStatColor(key)" />
    </div>
  </div>
</template>
```

#### 3. Layout Components

Компоненты разметки:

```vue
<!-- GameLayout.vue -->
<template>
  <div class="game-layout">
    <aside class="sidebar">
      <slot name="sidebar"></slot>
    </aside>
    
    <main class="content">
      <slot></slot>
    </main>
  </div>
</template>
```

---

## 🗄️ Управление состоянием

### Pinia Stores

#### Game Store

```javascript
// store/game.js
import { defineStore } from 'pinia'

export const useGameStore = defineStore('game', {
  state: () => ({
    currentSceneId: 'start',
    stats: {
      health: 100,
      morale: 100,
      psychic: 10
    },
    relationships: {},
    inventory: [],
    choicesMade: 0,
    isGameStarted: false
  }),

  getters: {
    currentScene: (state) => {
      return getSceneById(state.currentSceneId)
    },
    
    isGameOver: (state) => {
      return state.stats.health <= 0
    }
  },

  actions: {
    async startGame() {
      this.isGameStarted = true
      // API call
    },

    async makeChoice(choiceId, nextSceneId) {
      this.choicesMade++
      this.currentSceneId = nextSceneId
      // API call
    }
  }
})
```

### Композиция stores

```javascript
// В компоненте
import { useGameStore } from '@/store/game'
import { useUiStore } from '@/store/ui'
import { storeToRefs } from 'pinia'

const gameStore = useGameStore()
const uiStore = useUiStore()

//Refs для реактивности
const { stats, currentScene } = storeToRefs(gameStore)
```

---

## 🎨 Стилизация

### Design Tokens

```css
/* styles/tokens.css */
:root {
  /* Colors */
  --color-primary-500: #3b82f6;
  --color-secondary-500: #f59e0b;
  
  /* Spacing */
  --space-4: 1rem;
  
  /* Typography */
  --font-size-base: 1rem;
  
  /* Shadows */
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

### Scoped CSS

```vue
<template>
  <div class="card">...</div>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}
</style>
```

### CSS Modules (опционально)

```vue
<template>
  <div :class="$styles.card">...</div>
</template>

<style module>
.card {
  padding: 1rem;
}
</style>
```

---

## ⚡ Производительность

### Lazy Loading

```javascript
// Роуты
const routes = [
  {
    path: '/game',
    component: () => import('@/views/GameView.vue')
  }
]

// Компоненты
const AchievementNotification = () => import('@/components/AchievementNotification.vue')
```

### Computed Properties

```javascript
computed: {
  // Кэшируется
  filteredItems() {
    return this.items.filter(item => item.active)
  },
  
  // Не кэшируется (метод)
  calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.value, 0)
  }
}
```

### v-for Keys

```vue
<!-- ✅ Правильно -->
<div v-for="item in items" :key="item.id">{{ item.name }}</div>

<!-- ❌ Неправильно -->
<div v-for="item in items">{{ item.name }}</div>
```

---

## 🧪 Тестирование

### Unit тесты

```javascript
// tests/unit/components/Button.test.js
import { mount } from '@vue/test-utils'
import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  it('renders correctly', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Click me' }
    })
    
    expect(wrapper.text()).toBe('Click me')
  })

  it('emits click event', async () => {
    const wrapper = mount(Button)
    await wrapper.trigger('click')
    
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### Composables тесты

```javascript
// tests/unit/composables/useLoading.test.js
import { useLoading } from '@/composables'

describe('useLoading', () => {
  it('starts and stops loading', () => {
    const { isLoading, startLoading, stopLoading } = useLoading()
    
    expect(isLoading.value).toBe(false)
    
    startLoading()
    expect(isLoading.value).toBe(true)
    
    stopLoading()
    expect(isLoading.value).toBe(false)
  })
})
```

---

## 📚 Дополнительные ресурсы

- [Vue.js Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)

---

*Последнее обновление: 15 марта 2026*
