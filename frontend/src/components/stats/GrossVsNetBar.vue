<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, monthsToLabels, axisCurrencyFormatter, gradient, palette } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const el = ref(null)
let chart

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const points = props.data || []
  const labels = monthsToLabels(points)
  const gross = points.map(p => p.gross_income)
  const net = points.map(p => p.net_income)

  chart.setOption({
    title: { text: '毛收入 vs 净收入', left: 'center' },
    tooltip: { trigger: 'axis', valueFormatter: (v) => `¥${Number(v).toLocaleString()}` },
    legend: { data: ['毛收入', '净收入'], top: 28 },
    grid: baseGrid(),
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      {
        name: '毛收入',
        type: 'bar',
        stack: 'income',
        data: gross,
        itemStyle: { color: gradient('#409EFF', '#66b1ff') },
        barWidth: '40%',
      },
      {
        name: '净收入',
        type: 'bar',
        stack: 'income',
        data: net,
        itemStyle: { color: gradient('#67C23A', '#A3E09E') },
        barWidth: '40%',
      },
    ],
  })
}

onMounted(render)
watch(() => props.data, render)

onBeforeUnmount(() => { chart && chart.dispose && chart.dispose() })
</script>

<template>
  <div class="chart" ref="el" style="height: 360px; width: 100%"></div>
</template>
