<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <span style="font-size:42px;display:block">📊</span>
        <h1>AnalytiX</h1>
        <p>E-commerce Dashboard</p>
      </div>
      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="admin@demo.com" />
      </div>
      <div class="form-group">
        <label>Mot de passe</label>
        <input v-model="password" type="password" placeholder="••••••••" @keyup.enter="login" />
      </div>
      <div v-if="error" class="alert-error">{{ error }}</div>
      <button class="btn-primary" :disabled="loading" @click="login">
        {{ loading ? 'Connexion...' : 'Se connecter →' }}
      </button>
      <p class="demo-hint">Demo : admin@demo.com / password</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router   = useRouter()
const email    = ref('admin@demo.com')
const password = ref('password')
const loading  = ref(false)
const error    = ref('')

async function login() {
  loading.value = true
  error.value   = ''
  try {
    const { data } = await axios.post('/api/login', { email: email.value, password: password.value })
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    router.push('/')
  } catch {
    error.value = 'Email ou mot de passe incorrect'
  } finally {
    loading.value = false
  }
}
</script>
