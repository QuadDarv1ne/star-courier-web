# GitHub Environments Configuration
# Настройки окружений для деплоя

# ============================================================================
# STAGING ОКРУЖЕНИЕ
# ============================================================================
# URL: https://staging.starcourier.com
# Ветка: develop
# Требует approval: Нет
#
# Переменные окружения (Secrets):
# - DEPLOY_KEY
# - DATABASE_URL
# - API_KEY
#
# Environment protection rules:
# - Required reviewers: 0
# - Wait timer: 0 минут
# - Branches: develop
# ============================================================================

# ============================================================================
# PRODUCTION ОКРУЖЕНИЕ
# ============================================================================
# URL: https://starcourier.com
# Ветка: main (только теги v*)
# Требует approval: Да (1 человек)
#
# Переменные окружения (Secrets):
# - DEPLOY_KEY
# - DATABASE_URL
# - API_KEY
# - SENTRY_DSN
#
# Environment protection rules:
# - Required reviewers: 1
# - Wait timer: 5 минут
# - Branches: main (только теги v*)
# ============================================================================

# ============================================================================
# ИНСТРУКЦИЯ ПО НАСТРОЙКЕ
# ============================================================================
#
# 1. Перейдите в Settings → Environments
# 2. Нажмите "New environment"
# 3. Введите имя (staging или production)
# 4. Настройте правила:
#    - Required reviewers (для production)
#    - Wait timer (для production)
#    - Deployment branches (только определенные ветки)
# 5. Добавьте Secrets:
#    - DEPLOY_KEY: ключ для деплоя
#    - DATABASE_URL: строка подключения к БД
#    - API_KEY: ключ для внешних API
#
# ============================================================================
# SECRETS (НЕ КОММИТЬТЕ В РЕПОЗИТОРИЙ!)
# ============================================================================
#
# Для настройки secrets используйте GitHub UI:
# Settings → Secrets and variables → Actions → New repository secret
#
# Required secrets:
# - DOCKER_USERNAME: Docker Hub username
# - DOCKER_PASSWORD: Docker Hub password/token
# - DEPLOY_KEY: SSH key для деплоя
# - DATABASE_URL: PostgreSQL connection string
# - SENTRY_DSN: Sentry DSN для мониторинга ошибок
#
# ============================================================================
