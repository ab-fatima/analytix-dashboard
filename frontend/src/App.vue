<template>
  <div v-if="isPublic"><router-view /></div>
  <div v-else class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span>📊</span>
        <span class="logo-text">AnalytiX</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item">🏠 Dashboard</router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ initial }}</div>
          <div>
            <div class="user-name">{{ user?.name }}</div>
            <div class="user-email">{{ user?.email }}</div>
          </div>
        </div>
        <button class="logout-btn" @click="logout">↩ Logout</button>
      </div>
    </aside>
    <main class="main-content"><router-view /></main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route    = useRoute()
const router   = useRouter()
const isPublic = computed(() => route.meta.public)
const user     = computed(() => JSON.parse(localStorage.getItem('user') || 'null'))
const initial  = computed(() => user.value?.name?.[0]?.toUpperCase() || 'A')

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
