<script setup>
const props = defineProps({
  title: { type: String, default: '' },
  note: { type: String, default: '' },
})
</script>

<template>
  <div class="chart-card">
    <div v-if="$slots.header" class="chart-header">
      <slot name="header" />
    </div>
    <div class="chart-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 320px;
}

/* Header aligned with Salaries table header style */
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
}

/* Plot container: let ECharts control paddings via grid */
.chart-body {
  width: 100%;
  padding: 0;
}
</style>
