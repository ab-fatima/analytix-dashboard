<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Analytics e-commerce en temps réel</p>
      </div>
      <div class="period-selector">
        <button v-for="p in periods" :key="p.value"
          class="period-btn" :class="{ active: period === p.value }"
          @click="changePeriod(p.value)">{{ p.label }}</button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div v-if="loading" v-for="i in 4" :key="i" class="kpi-card skeleton"></div>
      <template v-else>
        <div class="kpi-card" v-for="(kpi, key) in kpis" :key="key">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value">
            <span v-if="kpi.prefix" class="kpi-prefix">{{ kpi.prefix }} </span>{{ fmt(kpi.value) }}
          </div>
          <div class="kpi-change" :class="kpi.change >= 0 ? 'positive' : 'negative'">
            {{ kpi.change >= 0 ? '▲' : '▼' }} {{ Math.abs(kpi.change) }}% vs période précédente
          </div>
        </div>
      </template>
    </div>

    <!-- Row 1 -->
    <div class="charts-row">
      <div class="chart-card wide">
        <div class="chart-header">
          <h2 class="chart-title">Chiffre d'affaires</h2>
        </div>
        <canvas ref="revenueCanvas" height="100"></canvas>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h2 class="chart-title">Statuts commandes</h2>
        </div>
        <canvas ref="statusCanvas"></canvas>
        <div class="status-legend">
          <div v-for="(item, i) in statusData" :key="i" class="legend-item">
            <span class="legend-dot" :style="{ background: colors[i % colors.length] }"></span>
            <span class="legend-label">{{ item.label }}</span>
            <span class="legend-value">{{ item.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <h2 class="chart-title" style="margin-bottom:16px">Top Produits</h2>
        <canvas ref="productsCanvas" height="200"></canvas>
      </div>
      <div class="chart-card">
        <h2 class="chart-title" style="margin-bottom:16px">Ventes par catégorie</h2>
        <canvas ref="categoryCanvas"></canvas>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="table-card">
      <div class="chart-header">
        <h2 class="chart-title">Dernières commandes</h2>
      </div>
      <div style="overflow-x:auto">
        <table class="data-table">
          <thead>
            <tr><th>Référence</th><th>Client</th><th>Statut</th><th>Total</th><th>Date</th></tr>
          </thead>
          <tbody>
            <tr v-if="!recentOrders.length">
              <td colspan="5" class="empty-row">Chargement...</td>
            </tr>
            <tr v-for="o in recentOrders" :key="o.id">
              <td class="ref">{{ o.reference }}</td>
              <td>{{ o.customer }}</td>
              <td><span class="status-badge" :class="o.status">{{ o.status }}</span></td>
              <td class="amount">MAD {{ fmt(o.total) }}</td>
              <td class="date">{{ o.ordered_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

const token   = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

const kpis         = ref(null)
const statusData   = ref([])
const recentOrders = ref([])
const loading      = ref(true)
const period       = ref(30)

const revenueCanvas  = ref(null)
const statusCanvas   = ref(null)
const productsCanvas = ref(null)
const categoryCanvas = ref(null)

const periods = [{ label: '7J', value: 7 }, { label: '30J', value: 30 }, { label: '90J', value: 90 }]
const colors  = ['#6366f1','#22c55e','#f59e0b','#3b82f6','#ef4444','#8b5cf6']

let charts = {}
function kill(k) { if (charts[k]) { charts[k].destroy(); charts[k] = null } }

function fmt(v) { return Number(v || 0).toLocaleString('fr-MA', { maximumFractionDigits: 0 }) }

async function fetchAll(p) {
  loading.value = true
  try {
    const [k, r, s, t, c, o] = await Promise.all([
      axios.get(`/api/dashboard/kpis?period=${p}`, { headers }),
      axios.get(`/api/dashboard/revenue-chart?period=${p}`, { headers }),
      axios.get('/api/dashboard/orders-by-status', { headers }),
      axios.get('/api/dashboard/top-products', { headers }),
      axios.get('/api/dashboard/sales-by-category', { headers }),
      axios.get('/api/dashboard/recent-orders', { headers }),
    ])
    kpis.value         = k.data
    statusData.value   = s.data
    recentOrders.value = o.data
    loading.value      = false
    await nextTick()
    buildCharts(r.data, s.data, t.data, c.data)
  } catch (e) {
    loading.value = false
    console.error(e)
  }
}

function buildCharts(revenue, status, products, categories) {
  kill('revenue')
  if (revenueCanvas.value && revenue.length) {
    charts.revenue = new Chart(revenueCanvas.value, {
      type: 'line',
      data: {
        labels: revenue.map(d => d.period),
        datasets: [{
          label: 'Revenu (MAD)',
          data: revenue.map(d => d.revenue),
          borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.08)',
          fill: true, tension: 0.4, pointRadius: 3,
        }],
      },
      options: { responsive: true, plugins: { legend: { position: 'top' } } },
    })
  }

  kill('status')
  if (statusCanvas.value && status.length) {
    charts.status = new Chart(statusCanvas.value, {
      type: 'doughnut',
      data: {
        labels: status.map(d => d.label),
        datasets: [{ data: status.map(d => d.count), backgroundColor: colors, borderWidth: 2 }],
      },
      options: { cutout: '65%', plugins: { legend: { display: false } } },
    })
  }

  kill('products')
  if (productsCanvas.value && products.length) {
    charts.products = new Chart(productsCanvas.value, {
      type: 'bar',
      data: {
        labels: products.slice(0, 5).map(p => p.name),
        datasets: [{ label: 'Revenu (MAD)', data: products.slice(0, 5).map(p => p.revenue), backgroundColor: '#6366f1', borderRadius: 6 }],
      },
      options: { indexAxis: 'y', responsive: true },
    })
  }

  kill('category')
  if (categoryCanvas.value && categories.length) {
    charts.category = new Chart(categoryCanvas.value, {
      type: 'polarArea',
      data: {
        labels: categories.map(d => d.category),
        datasets: [{ data: categories.map(d => d.revenue), backgroundColor: colors.map(c => c + 'cc') }],
      },
      options: { plugins: { legend: { position: 'right' } } },
    })
  }
}

async function changePeriod(p) { period.value = p; await fetchAll(p) }
onMounted(() => fetchAll(30))
</script>
