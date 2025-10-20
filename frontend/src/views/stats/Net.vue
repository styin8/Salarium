<script setup>
import { ref, onMounted, watch } from 'vue'
import { useStatsStore } from '../../store/stats'
import NetIncomeChart from '../../components/stats/NetIncomeChart.vue'
import GrossVsNetBar from '../../components/stats/GrossVsNetBar.vue'
import WaterfallChart from '../../components/stats/WaterfallChart.vue'

const stats = useStatsStore()
const net = ref([])
const gvn = ref([])
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    net.value = await stats.loadMonthlyNetIncome()
    gvn.value = await stats.loadGrossVsNetMonthly()
  } catch (e) {
    error.value = e
  } finally { loading.value = false }
}

onMounted(() => { load() })
watch(() => [stats.personId, stats.year, stats.range], () => { stats.invalidateCache(); load() }, { deep: true })
</script>

<template>
  <div class="grid" style="display:grid; grid-template-columns: 1fr; gap: 16px;">
    <el-card shadow="hover">
      <NetIncomeChart :data="net" />
    </el-card>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px;">
      <el-card shadow="hover"><GrossVsNetBar :data="gvn" /></el-card>
      <el-card shadow="hover"><WaterfallChart :data="gvn" /></el-card>
    </div>

    <div v-if="!loading && error" class="empty">
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="load">重试</el-button>
    </div>
  </div>
</template>
