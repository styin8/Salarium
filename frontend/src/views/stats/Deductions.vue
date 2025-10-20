<script setup>
import { ref, onMounted, watch } from 'vue'
import { useStatsStore } from '../../store/stats'
import DeductionsBreakdown from '../../components/stats/DeductionsBreakdown.vue'

const stats = useStatsStore()
const info = ref({ summary: [], monthly: [] })
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    info.value = await stats.loadDeductionsBreakdown()
  } catch (e) { error.value = e } finally { loading.value = false }
}

onMounted(load)
watch(() => [stats.personId, stats.year, stats.range], () => { stats.invalidateCache(); load() }, { deep: true })
</script>

<template>
  <div>
    <el-card shadow="hover">
      <DeductionsBreakdown :summary="info.summary" :monthly="info.monthly" />
    </el-card>

    <div v-if="!loading && error" class="empty">
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="load">重试</el-button>
    </div>
  </div>
</template>
