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
        <el-form class="toolbar-filters" :inline="true" size="small">
          <el-form-item class="toolbar-field">
            <el-select
              v-model="personFilter"
              placeholder="请选择用户"
              class="filter-control"
              size="small"
              clearable
              filterable
              :loading="stats.loadingPersons"
            >
              <el-option
                v-for="p in stats.persons"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item class="toolbar-field">
            <el-input-number
              v-model="stats.year"
              class="filter-control"
              size="small"
              :min="2000"
              :max="2100"
              controls-position="right"
            />
          </el-form-item>

          <el-form-item class="toolbar-field">
            <el-select
              v-model="monthFilter"
              placeholder="月"
              class="filter-control"
              size="small"
              clearable
            >
              <el-option
                v-for="m in 12"
                :key="m"
                :label="m + '月'"
                :value="m"
              />
            </el-select>
          </el-form-item>

          <el-button
            size="small"
            type="primary"
            plain
            aria-label="刷新"
            class="toolbar-refresh"
            :loading="stats.isRefreshing"
            @click="stats.refreshAll()"
          >
            <el-icon>
              <Refresh />
            </el-icon>
            <span class="btn-text">刷新</span>
          </el-button>
        </el-form>
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

.toolbar-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
}

.toolbar-field {
  margin: 0;
}

.toolbar-field :deep(.el-select),
.toolbar-field :deep(.el-input-number) {
  min-width: 160px;
  max-width: 240px;
  width: 100%;
}

.toolbar-field :deep(.el-input-number) {
  display: flex;
}

.toolbar-field :deep(.el-input-number .el-input__inner) {
  text-align: left;
}

/* Toolbar refresh button styling */
.toolbar-refresh {
  height: 32px !important;
  min-height: 32px !important;
  width: auto !important;
  padding: 0 12px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
}

/* Input number controls styling */
.toolbar-filters :deep(.el-input-number__increase),
.toolbar-filters :deep(.el-input-number__decrease) {
  height: 16px !important;
  line-height: 16px !important;
  width: 20px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* Month selector width adjustment */
.toolbar-filters :deep(.el-select) {
  min-width: 80px !important;
}

.toolbar-filters :deep(.el-select__wrapper) {
  min-width: 80px !important;
}

.toolbar-filters :deep(.el-input-number__increase) {
  border-bottom: 1px solid var(--primary-color) !important;
}

.toolbar-filters :deep(.el-input-number__decrease) {
  border-top: 1px solid var(--primary-color) !important;
}

.toolbar-refresh :deep(.el-icon) {
  font-size: 16px;
}

/* Remove focus outline from filter controls */
.toolbar-filters :deep(.el-select:focus),
.toolbar-filters :deep(.el-select:focus-visible),
.toolbar-filters :deep(.el-select.is-focus),
.toolbar-filters :deep(.el-select.is-active),
.toolbar-filters :deep(.el-input-number:focus),
.toolbar-filters :deep(.el-input-number:focus-visible),
.toolbar-filters :deep(.el-input-number.is-focus),
.toolbar-filters :deep(.el-input-number.is-active),
.toolbar-filters :deep(.el-date-picker:focus),
.toolbar-filters :deep(.el-date-picker:focus-visible),
.toolbar-filters :deep(.el-date-picker.is-focus),
.toolbar-filters :deep(.el-date-picker.is-active) {
  outline: none !important;
}

.toolbar-filters :deep(.el-select.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-select.is-active .el-input__wrapper),
.toolbar-filters :deep(.el-select:focus .el-input__wrapper),
.toolbar-filters :deep(.el-select:focus-visible .el-input__wrapper),
.toolbar-filters :deep(.el-input-number.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-input-number.is-active .el-input__wrapper),
.toolbar-filters :deep(.el-input-number:focus .el-input__wrapper),
.toolbar-filters :deep(.el-input-number:focus-visible .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker.is-focus .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker.is-active .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker:focus .el-input__wrapper),
.toolbar-filters :deep(.el-date-picker:focus-visible .el-input__wrapper) {
  box-shadow: none !important;
}

/* Button-like style for filter controls to match toolbar button */
.toolbar-filters :deep(.el-select__wrapper),
.toolbar-filters :deep(.el-input__wrapper),
.toolbar-filters :deep(.el-date-editor .el-input__wrapper) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0 12px;
  height: 32px;
  min-width: 80px;
  border: 1px solid var(--primary-color) !important;
  border-radius: 6px;
  background-color: #fff;
  color: var(--text-primary);
  box-shadow: none !important;
}

.toolbar-filters :deep(.el-select__wrapper:hover),
.toolbar-filters :deep(.el-input__wrapper:hover),
.toolbar-filters :deep(.el-date-editor .el-input__wrapper:hover) {
  border-color: var(--primary-hover) !important;
  background-color: #f0f7ff;
}

.toolbar-filters :deep(.el-select__wrapper.is-focus),
.toolbar-filters :deep(.el-input__wrapper.is-focus),
.toolbar-filters :deep(.el-date-editor.is-focus .el-input__wrapper) {
  border-color: var(--primary-color) !important;
  box-shadow: none !important;
}

.toolbar-filters :deep(.el-select__suffix .el-select__icon),
.toolbar-filters :deep(.el-select__suffix .el-select__caret) {
  color: var(--primary-color);
}

.toolbar-filters :deep(.el-input__inner) {
  font-size: 14px;
  height: 30px;
  line-height: 30px;
}

.toolbar-filters :deep(.el-select__selected-item .el-select__placeholder),
.toolbar-filters :deep(.el-select__placeholder) {
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .toolbar-field :deep(.el-select),
  .toolbar-field :deep(.el-input-number) {
    max-width: 100%;
    flex: 1 1 auto;
  }
}

@media (max-width: 520px) {
  .toolbar-refresh .btn-text {
    display: none;
  }

  .toolbar-refresh {
    justify-content: center;
    min-width: 36px;
    padding: 0 10px;
  }
}
</style>
