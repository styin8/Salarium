<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStatsStore } from '../../store/stats'
import { useUserStore } from '../../store/user'

const tabs = [
  { name: 'stats-net', label: '净收入', path: '/stats/net' },
  { name: 'stats-composition', label: '构成', path: '/stats/composition' },
  { name: 'stats-deductions', label: '扣除', path: '/stats/deductions' },
  { name: 'stats-cumulative', label: '累计', path: '/stats/cumulative' },
  { name: 'stats-table', label: '表格', path: '/stats/table' },
]

const route = useRoute()
const router = useRouter()
const stats = useStatsStore()
const user = useUserStore()

const activeTab = ref('stats-net')

onMounted(async () => {
  await stats.ensurePersons()
  if (route.name) activeTab.value = route.name
})

watch(() => route.name, (n) => { if (n) activeTab.value = n })

function onTabClick(tab) {
  const t = tabs.find(t => t.name === tab.paneName)
  if (t) router.push(t.path)
}
</script>

<template>
  <div class="stats-page">
    <div class="header">
      <div>
        <h2 class="title">统计分析</h2>
        <p class="sub">多维图表与数据表格</p>
      </div>
      <div class="filters">
        <el-select v-model="stats.personId" clearable placeholder="选择人员" style="width: 200px">
          <el-option :label="'所有人员'" :value="null" />
          <el-option v-for="p in stats.persons" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-input-number v-model="stats.year" :min="2000" :max="2100" controls-position="right" style="width: 160px" />
        <el-input v-model="stats.range" placeholder="自定义区间，如 2024-01..2024-12" style="width: 260px" />
        <el-button @click="stats.invalidateCache()">刷新数据</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" @tab-click="onTabClick">
      <el-tab-pane v-for="t in tabs" :key="t.name" :label="t.label" :name="t.name" />
    </el-tabs>

    <router-view />
  </div>
</template>

<style scoped>
.stats-page { padding: 24px; }
.header { display:flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; }
.title { margin: 0; font-size: 24px; }
.sub { margin: 4px 0 0; color: #6b7280 }
.filters { display: flex; gap: 12px; align-items: center; }
</style>
