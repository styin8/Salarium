<script setup>
import { ref, onMounted, watch } from 'vue'
import { useStatsStore } from '../../store/stats'
import CumulativeContribChart from '../../components/stats/CumulativeContribChart.vue'

const stats = useStatsStore()
const data = ref(null)
const loading = ref(false)
const error = ref(null)

async function load() {
  if (!stats.personId) return
  loading.value = true
  error.value = null
  try { data.value = await stats.loadContributionsCumulative() } catch (e) { error.value = e } finally { loading.value = false }
}

onMounted(load)
watch(() => [stats.personId, stats.year, stats.range], () => { stats.invalidateCache(); load() }, { deep: true })
</script>

<template>
  <div>
    <el-alert v-if="!stats.personId" title="请选择人员以查看累计曲线" type="info" show-icon />

    <el-card v-else shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ data?.person_name }} 累计曲线</span>
        </div>
      </template>
      <CumulativeContribChart :points="data?.points || []" />
    </el-card>

    <div v-if="!loading && error" class="empty">
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="load">重试</el-button>
    </div>
  </div>
</template>
