<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { useStatsStore } from '../../store/stats'
import { useUserStore } from '../../store/user'
import PageContainer from '../../components/PageContainer.vue'
import PageHeader from '../../components/PageHeader.vue'

const tabs = [
  { name: 'stats-net', label: '实际到手金额', path: '/stats/net' },
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

const personFilter = computed({
  get: () => stats.personId,
  set: (value) => stats.setPerson(value ?? null),
})

const monthFilter = computed({
  get: () => stats.month,
  set: (value) => stats.setMonth(value ?? null),
})

// Auto-refresh with debounce when filters change
let _debounceTimer = null
watch([personFilter, () => stats.year, monthFilter], () => {
  if (_debounceTimer) clearTimeout(_debounceTimer)
  _debounceTimer = setTimeout(() => {
    stats.refreshAll()
  }, 250)
}, { deep: true })

let _removeInvalidateListener = null
onMounted(async () => {
  await stats.ensurePersons()
  if (route.name) activeTab.value = route.name
  const handler = () => stats.refreshAll()
  window.addEventListener('stats:invalidate', handler)
  _removeInvalidateListener = () => window.removeEventListener('stats:invalidate', handler)
})

onBeforeUnmount(() => {
  if (_removeInvalidateListener) _removeInvalidateListener()
  if (_debounceTimer) clearTimeout(_debounceTimer)
})

watch(() => route.name, (n) => { if (n) { activeTab.value = n; setTimeout(() => window.dispatchEvent(new Event('resize')), 0) } })

function onTabClick(tab) {
  const t = tabs.find(t => t.name === tab.paneName)
  if (t) {
    router.push(t.path)
    setTimeout(() => window.dispatchEvent(new Event('resize')), 0)
  }
}
</script>

<template>
  <PageContainer>
    <PageHeader title="统计分析" subtitle="数据统计分析">
      <template #controls>
        <div class="toolbar-filters">
          <div class="filter-controls">
            <el-select
              v-model="personFilter"
              placeholder="选择人员"
              class="filter-control filter-person"
              size="small"
              clearable
              filterable
              :loading="stats.loadingPersons"
              aria-label="选择人员筛选"
            >
              <el-option
                v-for="p in stats.persons"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              />
            </el-select>

            <el-input-number
              v-model="stats.year"
              class="filter-control filter-year"
              size="small"
              :min="2000"
              :max="2100"
              controls-position="right"
              placeholder="年份"
              aria-label="选择年份"
            />

            <el-select
              v-model="monthFilter"
              placeholder="选择月份"
              class="filter-control filter-month"
              size="small"
              clearable
              aria-label="选择月份筛选"
            >
              <el-option
                v-for="m in 12"
                :key="m"
                :label="m + '月'"
                :value="m"
              />
            </el-select>
          </div>

          <el-button
            size="small"
            type="primary"
            plain
            aria-label="刷新数据"
            class="toolbar-refresh"
            :loading="stats.isRefreshing"
            @click="stats.refreshAll()"
          >
            <el-icon>
              <Refresh />
            </el-icon>
            <span class="btn-text">刷新</span>
          </el-button>
        </div>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" @tab-click="onTabClick" class="stats-tabs">
      <el-tab-pane v-for="t in tabs" :key="t.name" :label="t.label" :name="t.name" />
    </el-tabs>

    <div class="stats-content">
      <router-view />
    </div>
  </PageContainer>
</template>

<style scoped>
.stats-tabs {
  margin-bottom: 16px;
}

.stats-content {
  min-height: 400px;
}

/* Toolbar container - space between filters and button */
.toolbar-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
}

/* Filter controls group */
.filter-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* Filter control styling with specific max widths */
.filter-control {
  height: 32px;
}

.filter-person {
  width: 240px;
  max-width: 240px;
}

.filter-year {
  width: 160px;
  max-width: 160px;
}

.filter-month {
  width: 180px;
  max-width: 180px;
}

.filter-control :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

/* Input number specific styling */
.filter-year :deep(.el-input-number__decrease),
.filter-year :deep(.el-input-number__increase) {
  width: 28px;
}

.filter-year :deep(.el-input__inner) {
  text-align: left;
}

/* Refresh button */
.toolbar-refresh {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

.toolbar-refresh :deep(.el-icon) {
  font-size: 16px;
}

/* Focus styles - subtle border color change for accessibility */
.toolbar-filters :deep(.el-select:focus),
.toolbar-filters :deep(.el-select:focus-visible),
.toolbar-filters :deep(.el-input-number:focus),
.toolbar-filters :deep(.el-input-number:focus-visible) {
  outline: none;
}

/* Subtle focus indication via border color */
.toolbar-filters :deep(.el-select.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-input-number.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 1px #94a3b8 inset !important;
}

/* Keyboard navigation focus - more visible for accessibility */
.toolbar-filters :deep(.el-select:focus-visible .el-input__wrapper),
.toolbar-filters :deep(.el-input-number:focus-visible .el-input__wrapper) {
  box-shadow: 0 0 0 2px #94a3b8 inset !important;
}

/* Hover state */
.toolbar-filters :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1 inset;
}

/* Dropdown alignment */
.filter-control :deep(.el-select-dropdown) {
  margin-top: 4px;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .filter-person {
    width: 200px;
    max-width: 200px;
  }

  .filter-year {
    width: 140px;
    max-width: 140px;
  }

  .filter-month {
    width: 160px;
    max-width: 160px;
  }
}

@media (max-width: 768px) {
  .toolbar-filters {
    gap: 8px;
  }

  .filter-controls {
    gap: 8px;
    width: 100%;
  }

  .filter-person,
  .filter-year,
  .filter-month {
    flex: 1 1 auto;
    min-width: 140px;
    max-width: 100%;
  }

  .toolbar-refresh {
    margin-left: 0;
  }
}

@media (max-width: 520px) {
  .filter-controls {
    width: 100%;
  }

  .filter-person,
  .filter-year,
  .filter-month {
    width: 100%;
    max-width: 100%;
  }

  .toolbar-refresh {
    width: 100%;
    justify-content: center;
  }

  .toolbar-refresh .btn-text {
    display: none;
  }

  .toolbar-refresh {
    min-width: 100%;
    padding: 0 12px;
  }
}

/* Prevent layout shift during zoom (80%-125%) */
@media (min-resolution: 1.2dppx) {
  .filter-controls {
    gap: 8px;
  }
}

@media (min-resolution: 0.8dppx) {
  .filter-controls {
    gap: 12px;
  }
}
</style>
