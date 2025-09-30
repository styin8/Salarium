<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '../store/user'
import * as echarts from 'echarts'

const user = useUserStore()
const year = ref(new Date().getFullYear())
const monthly = ref([])
const yearly = ref([])
const chartEl = ref(null)
let chart

const api = axios.create({ baseURL: '/api', headers: { Authorization: `Bearer ${user.token}` } })

async function load() {
  const { data: yData } = await api.get('/stats/yearly', { params: { year: year.value } })
  yearly.value = yData
  const { data: mData } = await api.get('/stats/monthly', { params: { year: year.value } })
  monthly.value = mData
  renderChart()
}

function renderChart() {
  if (!chart) chart = echarts.init(chartEl.value)
  const months = [...new Set(monthly.value.map(i => i.month))].sort((a,b)=>a-b)
  const netByMonth = months.map(m => monthly.value.filter(i => i.month===m).reduce((s,i)=>s+i.net_income,0))
  chart.setOption({
    title: { text: `月度到手收入 - ${year.value}` },
    tooltip: {},
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: netByMonth }]
  })
}

onMounted(load)
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px">
      <h3>统计分析</h3>
      <el-input-number v-model="year" :min="2000" :max="2100" @change="load" />
    </div>
    <el-card>
      <div ref="chartEl" style="height:360px"></div>
    </el-card>
  </div>
</template>