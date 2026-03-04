<template>
  <div class="auth-modal">
    <!-- Tabs -->
    <div class="auth-tabs">
      <button 
        :class="['tab-btn', { active: mode === 'login' }]"
        @click="mode = 'login'"
      >
        Вход
      </button>
      <button 
        :class="['tab-btn', { active: mode === 'register' }]"
        @click="mode = 'register'"
      >
        Регистрация
      </button>
    </div>

    <!-- Login Form -->
    <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="auth-form">
      <div class="form-group">
        <label for="login-username">Username</label>
        <input 
          id="login-username"
          v-model="loginForm.username"
          type="text"
          placeholder="Введите username"
          required
          autocomplete="username"
        />
      </div>

      <div class="form-group">
        <label for="login-password">Пароль</label>
        <input 
          id="login-password"
          v-model="loginForm.password"
          type="password"
          placeholder="Введите пароль"
          required
          autocomplete="current-password"
        />
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" class="submit-btn" :disabled="isLoading">
        {{ isLoading ? 'Вход...' : 'Войти' }}
      </button>
    </form>

    <!-- Register Form -->
    <form v-else @submit.prevent="handleRegister" class="auth-form">
      <div class="form-group">
        <label for="reg-username">Username</label>
        <input 
          id="reg-username"
          v-model="registerForm.username"
          type="text"
          placeholder="Придумайте username"
          required
          pattern="[a-zA-Z0-9_]+"
          title="Только буквы, цифры и подчёркивание"
        />
        <small class="hint">Только буквы, цифры и _</small>
      </div>

      <div class="form-group">
        <label for="reg-email">Email</label>
        <input 
          id="reg-email"
          v-model="registerForm.email"
          type="email"
          placeholder="Ваш email"
          required
        />
      </div>

      <div class="form-group">
        <label for="reg-password">Пароль</label>
        <input 
          id="reg-password"
          v-model="registerForm.password"
          type="password"
          placeholder="Минимум 8 символов"
          required
          minlength="8"
        />
        <div class="password-requirements">
          <span :class="{ met: hasUpperCase }">A-Z</span>
          <span :class="{ met: hasLowerCase }">a-z</span>
          <span :class="{ met: hasNumber }">0-9</span>
          <span :class="{ met: hasMinLength }">8+</span>
        </div>
      </div>

      <div class="form-group">
        <label for="reg-confirm">Подтвердите пароль</label>
        <input 
          id="reg-confirm"
          v-model="registerForm.confirmPassword"
          type="password"
          placeholder="Повторите пароль"
          required
        />
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" class="submit-btn" :disabled="isLoading || !isPasswordValid">
        {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
    </form>

    <!-- Close button -->
    <button class="close-btn" @click="$emit('close')" title="Закрыть">
      ✕
    </button>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useAuthStore } from '../store/auth'

export default {
  name: 'AuthModal',
  
  emits: ['close', 'success'],
  
  setup(props, { emit }) {
    const authStore = useAuthStore()
    
    const mode = ref('login')
    const isLoading = computed(() => authStore.isLoading)
    const error = ref(null)
    
    const loginForm = ref({
      username: '',
      password: ''
    })
    
    const registerForm = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    // Password validation
    const hasUpperCase = computed(() => /[A-Z]/.test(registerForm.value.password))
    const hasLowerCase = computed(() => /[a-z]/.test(registerForm.value.password))
    const hasNumber = computed(() => /\d/.test(registerForm.value.password))
    const hasMinLength = computed(() => registerForm.value.password.length >= 8)
    
    const isPasswordValid = computed(() => 
      hasUpperCase.value && hasLowerCase.value && hasNumber.value && hasMinLength.value
    )
    
    async function handleLogin() {
      error.value = null
      
      try {
        await authStore.login(loginForm.value)
        emit('success')
        emit('close')
      } catch (err) {
        error.value = err.message
      }
    }
    
    async function handleRegister() {
      error.value = null
      
      // Validate passwords match
      if (registerForm.value.password !== registerForm.value.confirmPassword) {
        error.value = 'Пароли не совпадают'
        return
      }
      
      try {
        await authStore.register({
          username: registerForm.value.username,
          email: registerForm.value.email,
          password: registerForm.value.password
        })
        emit('success')
        emit('close')
      } catch (err) {
        error.value = err.message
      }
    }
    
    return {
      mode,
      loginForm,
      registerForm,
      isLoading,
      error,
      hasUpperCase,
      hasLowerCase,
      hasNumber,
      hasMinLength,
      isPasswordValid,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.auth-modal {
  background: rgba(30, 41, 59, 0.95);
  border: 2px solid #fbbf24;
  border-radius: 1rem;
  padding: 2rem;
  min-width: 400px;
  max-width: 450px;
  position: relative;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.auth-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: 1px solid #78350f;
  color: #d1d5db;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.3s;
  font-weight: 600;
}

.tab-btn:hover {
  background: rgba(251, 191, 36, 0.1);
}

.tab-btn.active {
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  color: white;
  border-color: #fbbf24;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #fbbf24;
  font-weight: 600;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.75rem 1rem;
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid #78350f;
  border-radius: 0.5rem;
  color: #e5e7eb;
  font-size: 1rem;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #fbbf24;
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.2);
}

.form-group input::placeholder {
  color: #6b7280;
}

.hint {
  color: #9ca3af;
  font-size: 0.8rem;
}

.password-requirements {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.password-requirements span {
  padding: 0.25rem 0.5rem;
  background: rgba(17, 24, 39, 0.5);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
  transition: all 0.3s;
}

.password-requirements span.met {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
}

.submit-btn {
  padding: 1rem;
  background: linear-gradient(135deg, #d97706 0%, #ea580c 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #fbbf24;
}

@media (max-width: 480px) {
  .auth-modal {
    min-width: unset;
    width: 100%;
    padding: 1.5rem;
  }
}
</style>
