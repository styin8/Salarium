<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { initChart, baseGrid, axisCurrencyFormatter, gradient } from '../../utils/charts'

const props = defineProps({
  data: { type: Array, default: () => [] }, // expects GrossVsNetMonthly
})

const el = ref(null)
let chart

const totals = computed(() => {
  const gross = props.data.reduce((s, p) => s + (p.gross_income || 0), 0)
  const net = props.data.reduce((s, p) => s + (p.net_income || 0), 0)
  const ded = Math.max(gross - net, 0)
  return { gross, net, ded }
})

function render() {
  if (!el.value) return
  if (!chart) chart = initChart(el.value)
  const { gross, net, ded } = totals.value
  const data = [gross, -ded, net]

  chart.setOption({
    title: { text: '瀑布图：毛 -> 扣除 -> 净', left: 'center' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: ['毛收入', '扣除', '净收入'] },
    yAxis: { type: 'value', axisLabel: { formatter: axisCurrencyFormatter } },
    series: [
      {
        type: 'bar',
        data,
        itemStyle: {
          color: (params) => {
            if (params.dataIndex === 1) return '#F56C6C'
            if (params.dataIndex === 2) return '#67C23A'
            return '#409EFF'
          },
        },
        label: {
          show: true,
          position: 'top',
          formatter: (p) => `¥${Math.abs(p.value).toLocaleString()}`,
        },
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
  <div class="chart" ref="el" style="height: 320px; width: 100%"></div>
</template>
