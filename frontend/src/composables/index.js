/**
 * StarCourier Web - Vue Composables
 * Переиспользуемая логика для Vue компонентов
 */

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// ============================================================================
// AUDIO COMPOSABLE
// ============================================================================

/**
 * Composable для управления аудио
 */
export function useAudio() {
  const isMuted = ref(false)
  const volume = ref(0.5)
  const isPlaying = ref(false)

  const playSound = (soundUrl) => {
    if (isMuted.value) return
    
    const audio = new Audio(soundUrl)
    audio.volume = volume.value
    audio.play().catch(console.error)
  }

  const toggleMute = () => {
    isMuted.value = !isMuted.value
  }

  const setVolume = (newVolume) => {
    volume.value = Math.max(0, Math.min(1, newVolume))
  }

  return {
    isMuted,
    volume,
    isPlaying,
    playSound,
    toggleMute,
    setVolume
  }
}

// ============================================================================
// LOADING COMPOSABLE
// ============================================================================

/**
 * Composable для управления состоянием загрузки
 */
export function useLoading(initialState = false) {
  const isLoading = ref(initialState)
  const loadingMessage = ref('')

  const startLoading = (message = 'Загрузка...') => {
    loadingMessage.value = message
    isLoading.value = true
  }

  const stopLoading = () => {
    loadingMessage.value = ''
    isLoading.value = false
  }

  const withLoading = async (callback, message) => {
    startLoading(message)
    try {
      return await callback()
    } finally {
      stopLoading()
    }
  }

  return {
    isLoading,
    loadingMessage,
    startLoading,
    stopLoading,
    withLoading
  }
}

// ============================================================================
// MODAL COMPOSABLE
// ============================================================================

/**
 * Composable для управления модальными окнами
 */
export function useModal(initialState = false) {
  const isOpen = ref(initialState)

  const open = () => {
    isOpen.value = true
    document.body.style.overflow = 'hidden'
  }

  const close = () => {
    isOpen.value = false
    document.body.style.overflow = ''
  }

  const toggle = () => {
    if (isOpen.value) {
      close()
    } else {
      open()
    }
  }

  const handleEscape = (event) => {
    if (event.key === 'Escape' && isOpen.value) {
      close()
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleEscape)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
    document.body.style.overflow = ''
  })

  return {
    isOpen,
    open,
    close,
    toggle
  }
}

// ============================================================================
// NOTIFICATION COMPOSABLE
// ============================================================================

/**
 * Composable для уведомлений
 */
export function useNotification() {
  const notifications = ref([])

  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = Date.now()
    notifications.value.push({ id, message, type, duration })

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const success = (message, duration) => addNotification(message, 'success', duration)
  const error = (message, duration) => addNotification(message, 'error', duration)
  const warning = (message, duration) => addNotification(message, 'warning', duration)
  const info = (message, duration) => addNotification(message, 'info', duration)

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info
  }
}

// ============================================================================
// FORM COMPOSABLE
// ============================================================================

/**
 * Composable для управления формами
 */
export function useForm(initialValues = {}, validators = {}) {
  const values = ref({ ...initialValues })
  const errors = ref({})
  const isSubmitting = ref(false)
  const isDirty = ref(false)

  const validateField = (field, value) => {
    const validator = validators[field]
    if (!validator) return true

    const error = validator(value)
    if (error) {
      errors.value[field] = error
      return false
    } else {
      delete errors.value[field]
      return true
    }
  }

  const validateAll = () => {
    const newErrors = {}
    
    Object.keys(validators).forEach(field => {
      const error = validators[field](values.value[field])
      if (error) {
        newErrors[field] = error
      }
    })

    errors.value = newErrors
    return Object.keys(newErrors).length === 0
  }

  const updateField = (field, value) => {
    values.value[field] = value
    isDirty.value = true
    validateField(field, value)
  }

  const reset = () => {
    values.value = { ...initialValues }
    errors.value = {}
    isDirty.value = false
    isSubmitting.value = false
  }

  const withSubmit = async (callback) => {
    if (!validateAll()) return

    isSubmitting.value = true
    try {
      await callback()
      reset()
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    values,
    errors,
    isSubmitting,
    isDirty,
    updateField,
    validateField,
    validateAll,
    reset,
    withSubmit
  }
}

// ============================================================================
// LOCAL STORAGE COMPOSABLE
// ============================================================================

/**
 * Composable для работы с localStorage
 */
export function useLocalStorage(key, initialValue) {
  const storedValue = ref(() => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  })

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue.value) : value
      storedValue.value = valueToStore
      localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  const removeValue = () => {
    try {
      localStorage.removeItem(key)
      storedValue.value = initialValue
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error)
    }
  }

  return {
    value: storedValue,
    setValue,
    removeValue
  }
}

// ============================================================================
// RESPONSIVE COMPOSABLE
// ============================================================================

/**
 * Composable для отслеживания размера экрана
 */
export function useResponsive() {
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)

  const updateSize = () => {
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  onMounted(() => {
    window.addEventListener('resize', updateSize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateSize)
  })

  const isMobile = computed(() => width.value < 768)
  const isTablet = computed(() => width.value >= 768 && width.value < 1024)
  const isDesktop = computed(() => width.value >= 1024)

  const breakpoint = computed(() => {
    if (width.value < 768) return 'sm'
    if (width.value < 1024) return 'md'
    if (width.value < 1280) return 'lg'
    return 'xl'
  })

  return {
    width,
    height,
    isMobile,
    isTablet,
    isDesktop,
    breakpoint
  }
}

// ============================================================================
// KEYBOARD COMPOSABLE
// ============================================================================

/**
 * Composable для отслеживания нажатий клавиш
 */
export function useKeyboard(shortcuts = {}) {
  const handleKeydown = (event) => {
    const key = event.key.toLowerCase()
    const shortcut = shortcuts[key]
    
    if (shortcut) {
      event.preventDefault()
      shortcut()
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return {
    handleKeydown
  }
}

// ============================================================================
// EXPORT
// ============================================================================

export default {
  useAudio,
  useLoading,
  useModal,
  useNotification,
  useForm,
  useLocalStorage,
  useResponsive,
  useKeyboard
}
