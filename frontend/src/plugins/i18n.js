/**
 * StarCourier Web - i18n Plugin
 * Плагин для интернационализации Vue.js 3
 * 
 * Автор: QuadDarv1ne
 * Версия: 1.0.0
 */

import { ref, computed, watch } from 'vue'

// Поддерживаемые языки
const SUPPORTED_LOCALES = ['ru', 'en']
const DEFAULT_LOCALE = 'ru'

// Загруженные переводы
const translations = {
  ru: () => import('../locales/ru.json'),
  en: () => import('../locales/en.json')
}

// Кэш загруженных сообщений
const loadedMessages = {}

// Текущий язык
const currentLocale = ref(getStoredLocale())

/**
 * Получение сохранённого языка
 */
function getStoredLocale() {
  // Проверка localStorage
  const stored = localStorage.getItem('starcourier_locale')
  if (stored && SUPPORTED_LOCALES.includes(stored)) {
    return stored
  }
  
  // Проверка языка браузера
  const browserLang = navigator.language.split('-')[0]
  if (SUPPORTED_LOCALES.includes(browserLang)) {
    return browserLang
  }
  
  return DEFAULT_LOCALE
}

/**
 * Сохранение языка
 */
function setStoredLocale(locale) {
  localStorage.setItem('starcourier_locale', locale)
}

/**
 * Загрузка сообщений для языка
 */
async function loadMessages(locale) {
  if (loadedMessages[locale]) {
    return loadedMessages[locale]
  }
  
  try {
    const messages = await translations[locale]()
    loadedMessages[locale] = messages.default || messages
    return loadedMessages[locale]
  } catch (error) {
    console.error(`Failed to load messages for ${locale}:`, error)
    return {}
  }
}

/**
 * Получение значения по пути (например, 'app.name')
 */
function getValueByPath(obj, path) {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj)
}

/**
 * Замена плейсхолдеров в строке
 * Пример: "Hello, {name}!" с { name: "World" } => "Hello, World!"
 */
function interpolate(message, params = {}) {
  return message.replace(/\{(\w+)\}/g, (match, key) => {
    return params[key] !== undefined ? params[key] : match
  })
}

/**
 * Функция перевода
 */
function t(key, params = {}) {
  const messages = loadedMessages[currentLocale.value] || {}
  let message = getValueByPath(messages, key)
  
  if (message === undefined) {
    // Fallback на язык по умолчанию
    const defaultMessages = loadedMessages[DEFAULT_LOCALE] || {}
    message = getValueByPath(defaultMessages, key)
    
    if (message === undefined) {
      console.warn(`Translation not found: ${key}`)
      return key
    }
  }
  
  return interpolate(message, params)
}

/**
 * Проверка существования перевода
 */
function te(key) {
  const messages = loadedMessages[currentLocale.value] || {}
  return getValueByPath(messages, key) !== undefined
}

/**
 * Смена языка
 */
async function setLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) {
    console.warn(`Unsupported locale: ${locale}`)
    return
  }
  
  await loadMessages(locale)
  currentLocale.value = locale
  setStoredLocale(locale)
  document.documentElement.setAttribute('lang', locale)
}

/**
 * Плагин i18n для Vue
 */
export default {
  install(app) {
    // Загрузка начального языка
    loadMessages(currentLocale.value).then(() => {
      document.documentElement.setAttribute('lang', currentLocale.value)
    })
    
    // Глобальные свойства
    app.config.globalProperties.$t = t
    app.config.globalProperties.$te = te
    app.config.globalProperties.$i18n = {
      locale: currentLocale,
      setLocale,
      availableLocales: SUPPORTED_LOCALES
    }
    
    // Предоставление через provide/inject
    app.provide('i18n', {
      t,
      te,
      locale: currentLocale,
      setLocale,
      availableLocales: SUPPORTED_LOCALES
    })
  }
}

// Экспорт composables
export function useI18n() {
  return {
    t,
    te,
    locale: computed(() => currentLocale.value),
    setLocale,
    availableLocales: SUPPORTED_LOCALES
  }
}

// Экспорт утилит
export {
  t,
  te,
  setLocale,
  currentLocale,
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE
}
