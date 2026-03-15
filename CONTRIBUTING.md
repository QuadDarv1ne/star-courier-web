# 🤝 Вклад в проект StarCourier Web

Спасибо за интерес к проекту StarCourier Web! Этот документ поможет вам начать вносить свой вклад.

---

## 📋 Содержание

- [Кодекс поведения](#-кодекс-поведения)
- [С чего начать](#-с-чего-начать)
- [Настройка окружения](#-настройка-окружения)
- [Процесс разработки](#-процесс-разработки)
- [Стандарты кода](#-стандарты-кода)
- [Тестирование](#-тестирование)
- [Pull Request гайд](#-pull-request-гайд)
- [Коммиты](#-коммиты)

---

## 🎯 Кодекс поведения

### Наши обязательства

- **Уважение**: Приветствуем участников независимо от опыта, возраста, пола, ориентации
- **Конструктивность**: Критика должна быть конструктивной и полезной
- **Помощь**: Помогаем новичкам и отвечаем на вопросы
- **Терпимость**: Уважаем разные мнения и подходы

### Недопустимое поведение

- Оскорбления и унижения
- Троллинг и провокации
- Распространение дезинформации
- Спам и реклама

---

## 🚀 С чего начать

### 1. Найдите задачу

- Посмотрите [TODO.md](TODO.md) для дорожной карты
- Проверьте [Issues](https://github.com/QuadDarv1ne/star-courier-web/issues) с меткой `good first issue`
- Предложите свою идею через Discussion

### 2. Обсудите

Перед началом работы:
- Проверьте, нет ли уже открытого PR по этой задаче
- Обсудите подход в Issue или Discussion
- Убедитесь, что задача актуальна

### 3. Форкните и работайте

```bash
# Форк репозитория
git clone https://github.com/YOUR_USERNAME/star-courier-web.git
cd star-courier-web

# Создайте ветку
git checkout -b feature/your-feature-name
```

---

## ⚙️ Настройка окружения

### Backend (Python)

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt  # dev зависимости

# Запуск
uvicorn app.main:app --reload
```

### Frontend (Node.js)

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev

# Линтинг
npm run lint

# Форматирование
npm run format
```

### Docker (опционально)

```bash
# Запуск всего стека
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

---

## 📝 Процесс разработки

### Ветка

```bash
# Название веток
feature/add-inventory-system    # Новая фича
bugfix/fix-auth-error           # Исправление бага
docs/update-readme              # Документация
refactor/game-service           # Рефакторинг
test/add-game-tests             # Тесты
```

### Работа

1. Создайте ветку от `main`
2. Делайте небольшие коммиты
3. Пишите тесты для нового функционала
4. Обновляйте документацию при необходимости

### Перед отправкой

```bash
# Backend
cd backend
pytest tests/ -v --cov=app
black app/ tests/
flake8 app/ tests/
mypy app/

# Frontend
cd frontend
npm run test
npm run lint
npm run build
```

---

## 📐 Стандарты кода

### Python

```python
# ✅ Хорошо
from typing import Optional, List
from fastapi import APIRouter, HTTPException

router = APIRouter()

async def get_user(user_id: int) -> Optional[dict]:
    """Получить пользователя по ID"""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    return {"id": user_id}

# ❌ Плохо
def get_user(id):
    if id <= 0:
        raise Exception("Bad ID")
    return {"id": id}
```

**Правила:**
- Используйте Type Hints
- Документируйте функции (docstring)
- Следуйте PEP 8
- Используйте async/await для I/O операций
- Обрабатывайте ошибки явно

### Vue.js

```vue
<!-- ✅ Хорошо -->
<script setup>
import { ref, computed } from 'vue'
import { useGameStore } from '@/store/game'

const gameStore = useGameStore()
const isLoading = ref(false)

const playerName = computed(() => gameStore.player?.name)

async function startGame() {
  isLoading.value = true
  try {
    await gameStore.start()
  } catch (error) {
    console.error('Failed to start:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="game-container">
    <button 
      @click="startGame" 
      :disabled="isLoading"
      class="btn btn-primary"
    >
      {{ isLoading ? 'Загрузка...' : 'Начать игру' }}
    </button>
  </div>
</template>

<style scoped>
.game-container {
  padding: 2rem;
}
</style>
```

**Правила:**
- Используйте Composition API (`<script setup>`)
- Компоненты должны быть переиспользуемыми
- Стили должны быть scoped
- Обрабатывайте состояния загрузки и ошибок

---

## 🧪 Тестирование

### Backend тесты

```bash
cd backend

# Все тесты
pytest tests/ -v

# С покрытием
pytest tests/ -v --cov=app --cov-report=html

# Конкретный тест
pytest tests/test_api.py::test_health_check -v
```

### Frontend тесты

```bash
cd frontend

# Все тесты
npm run test

# С покрытием
npm run test:coverage

# Watch режим
npm run test:watch
```

### Покрытие

Цель: **>80%** для критического кода

```python
# Пример теста
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## 🔀 Pull Request гайд

### Перед созданием PR

- [ ] Код следует стандартам
- [ ] Тесты проходят
- [ ] Документация обновлена
- [ ] Нет конфликтов с main
- [ ] Коммиты переписаны чисто

### Шаблон PR

```markdown
## Описание
Краткое описание изменений

## Тип изменений
- [ ] 🐛 Багфикс
- [ ] ✨ Новая фича
- [ ] 📝 Документация
- [ ] ♻️ Рефакторинг
- [ ] 🧪 Тесты

## Тестирование
Опишите, как тестировали изменения

## Чеклист
- [ ] Код следует гайдлайнам
- [ ] Тесты добавлены/обновлены
- [ ] Документация обновлена
- [ ] Нет warning'ов
```

### Ревью

- Минимум 1 аппрув от мейнтейнера
- Все комментарии должны быть разрешены
- CI/CD пайплайн должен проходить

---

## 📝 Коммиты

### Формат

Следуем [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Типы

- `feat`: Новая фича
- `fix`: Исправление бага
- `docs`: Документация
- `style`: Форматирование
- `refactor`: Рефакторинг
- `test`: Тесты
- `chore`: Инфраструктура

### Примеры

```bash
# ✅ Хорошо
feat(game): добавить систему инвентаря
fix(auth): исправить валидацию токена
docs(readme): обновить секцию установки
refactor(api): упростить обработку ошибок

# ❌ Плохо
added stuff
fixed bug
update
```

---

## 🏷️ Issues

### Метки

- `bug`: Ошибка в коде
- `enhancement`: Улучшение
- `documentation`: Документация
- `good first issue`: Для новичков
- `help wanted`: Нужна помощь
- `question`: Вопрос
- `wontfix`: Не будет исправлено

### Создание Issue

Используйте шаблоны:
- **Bug Report**: шаги воспроизведения, ожидаемый/фактический результат
- **Feature Request**: описание, обоснование, примеры
- **Question**: чёткий вопрос

---

## 📞 Связь

- **GitHub Issues**: Для багов и фич
- **GitHub Discussions**: Для вопросов и идей
- **Email**: [ваш-email@example.com]

---

## 🙏 Благодарности

Спасибо всем контрибьюторам! Ваш вклад делает проект лучше.

[Список контрибьюторов](https://github.com/QuadDarv1ne/star-courier-web/graphs/contributors)

---

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)
