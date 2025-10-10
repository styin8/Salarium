<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { useUserStore } from '../store/user'
import * as echarts from 'echarts'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const user = useUserStore()
const year = ref(new Date().getFullYear())
const selectedPersonId = ref(null) // null means all persons - default to show all members
const monthly = ref([])
const yearly = ref([])
const persons = ref([])
const familySummary = ref({})
const loading = ref(false)

// Chart references
const monthlyChartEl = ref(null)
const compositionChartEl = ref(null)
const comparisonChartEl = ref(null)
let monthlyChart, compositionChart, comparisonChart

const api = axios.create({ baseURL: '/api', headers: { Authorization: `Bearer ${user.token}` } })

// Computed properties for statistics
const totalStats = computed(() => {
  if (selectedPersonId.value) {
    // Single person stats
    const personYearly = yearly.value.find(y => y.person_id === selectedPersonId.value)
    return personYearly ? {
      totalGross: personYearly.total_gross,
      totalNet: personYearly.total_net,
      avgNet: personYearly.avg_net,
      totalTax: personYearly.tax_total,
      totalInsurance: personYearly.insurance_total,
      months: personYearly.months
    } : {
      totalGross: 0, totalNet: 0, avgNet: 0, totalTax: 0, totalInsurance: 0, months: 0
    }
  } else {
    // All persons combined stats
    return yearly.value.reduce((acc, curr) => ({
      totalGross: acc.totalGross + curr.total_gross,
      totalNet: acc.totalNet + curr.total_net,
      avgNet: yearly.value.length ? (acc.totalNet + curr.total_net) / yearly.value.length : 0,
      totalTax: acc.totalTax + curr.tax_total,
      totalInsurance: acc.totalInsurance + curr.insurance_total,
      months: Math.max(acc.months, curr.months)
    }), { totalGross: 0, totalNet: 0, avgNet: 0, totalTax: 0, totalInsurance: 0, months: 0 })
  }
})

// Load persons list
async function loadPersons() {
  try {
    const { data } = await api.get('/persons/')
    persons.value = data
  } catch (error) {
    console.error('Failed to load persons:', error)
  }
}

// Load statistics data
async function loadStats() {
  loading.value = true
  try {
    const params = { year: year.value }
    if (selectedPersonId.value) {
      params.person_id = selectedPersonId.value
    }
    
    const [yearlyRes, monthlyRes, familyRes] = await Promise.all([
      api.get('/stats/yearly', { params }),
      api.get('/stats/monthly', { params }),
      api.get('/stats/family', { params: { year: year.value } })
    ])
    
    yearly.value = yearlyRes.data
    monthly.value = monthlyRes.data
    familySummary.value = familyRes.data
    
    renderCharts()
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

// Render monthly income chart
function renderMonthlyChart() {
  if (!monthlyChartEl.value) return
  if (!monthlyChart) {
    monthlyChart = echarts.init(monthlyChartEl.value)
  }
  
  const months = [...new Set(monthly.value.map(i => i.month))].sort((a,b)=>a-b)
  const netByMonth = months.map(m => 
    monthly.value.filter(i => i.month === m).reduce((s,i) => s + i.net_income, 0)
  )
  const grossByMonth = months.map(m => 
    monthly.value.filter(i => i.month === m).reduce((s,i) => s + i.gross_income, 0)
  )
  
  monthlyChart.setOption({
    title: { 
      text: `${t('stats.monthlyIncome')} - ${year.value}`,
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ¥${param.value.toLocaleString()}<br/>`
        })
        return result
      }
    },
    legend: {
      data: [t('stats.grossIncome'), t('stats.netIncome')]
    },
    grid: { left: '3%', right: '4%', bottom: '8%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: months.map(m => `${m}月`),
      axisLabel: { 
        rotate: 0,
        fontSize: 12,
        color: '#666',
        margin: 8,
        interval: 0
      },
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      axisTick: {
        alignWithLabel: true,
        lineStyle: {
          color: '#e0e0e0'
        }
      }
    },
    yAxis: { 
      type: 'value',
      axisLabel: { 
        formatter: '¥{value}',
        fontSize: 12,
        color: '#666'
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: t('stats.grossIncome'),
        type: 'bar',
        data: grossByMonth,
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#66b1ff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '35%'
      },
      {
        name: t('stats.netIncome'),
        type: 'bar',
        data: netByMonth,
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67C23A' },
            { offset: 1, color: '#85ce61' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '35%'
      }
    ]
  })
}

// Render income composition pie chart
function renderCompositionChart() {
  if (!compositionChartEl.value || !totalStats.value.totalGross) return
  if (!compositionChart) {
    compositionChart = echarts.init(compositionChartEl.value)
  }
  
  const stats = totalStats.value
  const data = [
    { value: stats.totalNet, name: t('stats.netIncome'), itemStyle: { color: '#67C23A' } },
    { value: stats.totalTax, name: t('stats.totalTax'), itemStyle: { color: '#E6A23C' } },
    { value: stats.totalInsurance, name: t('stats.totalInsurance'), itemStyle: { color: '#409EFF' } }
  ]
  
  // Calculate other/custom deductions
  const otherAmount = stats.totalGross - (stats.totalNet + stats.totalTax + stats.totalInsurance)
  if (otherAmount > 0) {
    data.push({ 
      value: otherAmount, 
      name: t('stats.otherDeductions') || '其他扣除', 
      itemStyle: { color: '#909399' } 
    })
  }
  
  compositionChart.setOption({
    title: {
      text: t('stats.incomeComposition'),
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 'bold', color: '#333' }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)',
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        fontSize: 12,
        color: '#666'
      }
    },
    series: [
      {
        name: t('stats.incomeComposition'),
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          formatter: '{b}\n¥{c}',
          fontSize: 11,
          color: '#666'
        },
        labelLine: {
          show: true,
          length: 15,
          length2: 10
        }
      }
    ]
  })
}

// Render person comparison chart
function renderComparisonChart() {
  if (!comparisonChartEl.value || selectedPersonId.value) return
  if (!comparisonChart) {
    comparisonChart = echarts.init(comparisonChartEl.value)
  }
  
  const personNames = yearly.value.map(y => {
    const person = persons.value.find(p => p.id === y.person_id)
    return person ? person.name : `Person ${y.person_id}`
  })
  const netIncomes = yearly.value.map(y => y.total_net)
  
  comparisonChart.setOption({
    title: {
      text: t('stats.yearlyStats'),
      textStyle: { fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        return `${params[0].axisValue}<br/>净收入: ¥${params[0].value.toLocaleString()}`
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: personNames,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '¥{value}' }
    },
    series: [
      {
        type: 'bar',
        data: netIncomes,
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  })
}

// Render all charts
function renderCharts() {
  setTimeout(() => {
    renderMonthlyChart()
    renderCompositionChart()
    renderComparisonChart()
  }, 100)
}

// Handle person selection change
function handlePersonChange() {
  loadStats()
}

// Handle year change
function handleYearChange() {
  loadStats()
}

// Resize charts on window resize
function handleResize() {
  monthlyChart?.resize()
  compositionChart?.resize()
  comparisonChart?.resize()
}

// Watch for reactive changes
watch(() => selectedPersonId.value, handlePersonChange)
watch(() => year.value, handleYearChange)

// Lifecycle hooks
onMounted(async () => {
  await loadPersons()
  // Ensure default selection is "All Persons" (null value)
  selectedPersonId.value = null
  await loadStats()
  window.addEventListener('resize', handleResize)
})
</script>

<template>
  <div class="stats-container">
    <!-- Header Section -->
    <div class="stats-header">
      <div class="header-left">
        <h2 class="page-title">{{ t('stats.title') }}</h2>
        <p class="page-subtitle">{{ t('stats.overview') }}</p>
      </div>
      <div class="header-controls">
        <el-select 
          v-model="selectedPersonId" 
          :placeholder="t('stats.selectPerson')"
          clearable
          style="width: 200px; margin-right: 12px"
        >
          <el-option :label="t('stats.allPersons')" :value="null" />
          <el-option 
            v-for="person in persons" 
            :key="person.id" 
            :label="person.name" 
            :value="person.id" 
          />
        </el-select>
        <el-input-number 
          v-model="year" 
          :min="2000" 
          :max="2100" 
          :placeholder="t('stats.selectYear')"
        />
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards" v-loading="loading">
      <div class="stat-card gradient-blue">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ totalStats.totalGross.toLocaleString() }}</div>
          <div class="stat-label">{{ t('stats.grossIncome') }}</div>
        </div>
      </div>
      <div class="stat-card gradient-green">
        <div class="stat-icon">💵</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ totalStats.totalNet.toLocaleString() }}</div>
          <div class="stat-label">{{ t('stats.netIncome') }}</div>
        </div>
      </div>
      <div class="stat-card gradient-orange">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">¥{{ Math.round(totalStats.avgNet).toLocaleString() }}</div>
          <div class="stat-label">{{ t('stats.avgSalary') }}</div>
        </div>
      </div>
      <div class="stat-card gradient-purple">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalStats.months }}</div>
          <div class="stat-label">{{ t('stats.monthlyStats') }}</div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <!-- Monthly Income Chart -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">{{ t('stats.monthlyTrend') }}</span>
          </div>
        </template>
        <div ref="monthlyChartEl" class="chart-container"></div>
      </el-card>

      <!-- Income Composition Chart -->
      <el-card class="chart-card" shadow="hover" v-if="totalStats.totalGross > 0">
        <template #header>
          <div class="card-header">
            <span class="card-title">{{ t('stats.incomeComposition') }}</span>
          </div>
        </template>
        <div ref="compositionChartEl" class="chart-container"></div>
      </el-card>

      <!-- Person Comparison Chart (only when all persons selected) -->
      <el-card class="chart-card full-width" shadow="hover" v-if="!selectedPersonId && yearly.length > 1">
        <template #header>
          <div class="card-header">
            <span class="card-title">{{ t('stats.yearlyStats') }}</span>
          </div>
        </template>
        <div ref="comparisonChartEl" class="chart-container"></div>
      </el-card>
    </div>

    <!-- Data Table -->
    <el-card class="data-table-card" shadow="hover" v-if="yearly.length > 0">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ t('stats.dataTable') }}</span>
        </div>
      </template>
      <el-table :data="yearly" stripe>
        <el-table-column :label="t('common.name')" width="120">
          <template #default="{ row }">
            {{ persons.find(p => p.id === row.person_id)?.name || `Person ${row.person_id}` }}
          </template>
        </el-table-column>
        <el-table-column prop="year" :label="t('common.date')" width="80" />
        <el-table-column prop="months" label="月数" width="80" />
        <el-table-column prop="total_gross" :label="t('stats.grossIncome')" width="120">
          <template #default="{ row }">¥{{ row.total_gross.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="total_net" :label="t('stats.netIncome')" width="120">
          <template #default="{ row }">¥{{ row.total_net.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="avg_net" :label="t('stats.avgSalary')" width="120">
          <template #default="{ row }">¥{{ Math.round(row.avg_net).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="tax_total" :label="t('stats.totalTax')" width="120">
          <template #default="{ row }">¥{{ row.tax_total.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="insurance_total" :label="t('stats.totalInsurance')" width="120">
          <template #default="{ row }">¥{{ row.insurance_total.toLocaleString() }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Empty State -->
    <el-empty 
      v-if="!loading && yearly.length === 0" 
      :description="selectedPersonId ? t('stats.noDataForPerson') : t('common.noData')"
      :image-size="200"
    />
  </div>
</template>

<style scoped>
.stats-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 60px);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  padding: 0 4px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.gradient-blue {
  --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-green {
  --gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-orange {
  --gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-purple {
  --gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon {
  font-size: 32px;
  margin-right: 16px;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.data-table-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .stats-container {
    padding: 16px;
  }
  
  .stats-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-controls {
    width: 100%;
    justify-content: flex-end;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 24px;
  }
}

/* Loading Animation */
.el-loading-mask {
  border-radius: 16px;
}

/* Table Styling */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: #f8f9fa;
  color: #2c3e50;
  font-weight: 600;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #fafbfc;
}
</style>