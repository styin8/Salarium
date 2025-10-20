<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter } from '../../utils/charts'

const props = defineProps({
  summary: { type: Array, default: () => [] }, // DeductionsBreakdownItem[]
  monthly: { type: Array, default: () => [] }, // DeductionsMonthly[]
})

const pieEl = ref(null)
const stackEl = ref(null)
let pieChart, stackChart

function renderPie() {
  if (!pieEl.value) return
  if (!pieChart) pieChart = initChart(pieEl.value)
  pieChart.setOption({
    title: { text: '扣除项占比', left: 'center' },
    tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ¥${Number(p.value).toLocaleString()} (${p.percent}%)` },
    series: [
      { type: 'pie', radius: ['40%', '70%'], data: props.summary.map(s => ({ name: s.category, value: s.amount })) },
    ],
  })
}

function renderStack() {
  if (!stackEl.value) return
  if (!stackChart) stackChart = initChart(stackEl.value)
  const labels = props.monthly.map(m => `${m.month}月`)
  stackChart.setOption({
    title: { text: '扣除项月度趋势', left: 'center' },
    tooltip: { trigger: 'axis', valueFormatter: (v) => `¥${Number(v).toLocaleString()}` },
    legend: { top: 28 },
    grid: baseGrid(),
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      { name: '养老保险', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.pension_insurance) },
      { name: '医疗保险', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.medical_insurance) },
      { name: '失业保险', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.unemployment_insurance) },
      { name: '大病互助保险', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.critical_illness_insurance) },
      { name: '企业年金', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.enterprise_annuity) },
      { name: '住房公积金', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.housing_fund) },
      { name: '其他扣除', type: 'line', stack: 'ded', areaStyle: {}, data: props.monthly.map(m => m.other_deductions) },
    ],
  })
}

onMounted(() => { renderPie(); renderStack() })
watch(() => props.summary, renderPie)
watch(() => props.monthly, renderStack)

onBeforeUnmount(() => {
  pieChart && pieChart.dispose && pieChart.dispose()
  stackChart && stackChart.dispose && stackChart.dispose()
})
</script>

<template>
  <div class="grid" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
    <div ref="pieEl" style="height:320px;width:100%"></div>
    <div ref="stackEl" style="height:320px;width:100%"></div>
  </div>
</template>
