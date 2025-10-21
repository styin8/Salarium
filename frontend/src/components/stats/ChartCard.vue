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
    <div v-if="title || note" class="chart-footer">
      <div class="chart-title" :title="title">{{ title }}</div>
      <div v-if="note" class="chart-note">{{ note }}</div>
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  display: flex;
  flex-direction: column;
  width: 100%;
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
.chart-header.sticky {
  position: sticky;
  top: 0;
  z-index: 7;
  background: #fff;
}

/* Plot container padding aligns with header left/right */
.chart-body {
  width: 100%;
  padding: 12px 16px;
}

/* Footer title placed below chart, single line, aligned with header paddings */
.chart-footer {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 16px 12px;
  color: #475569;
  flex-wrap: nowrap;
}
.chart-title {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.chart-note { font-size: 12px; color: #94a3b8; white-space: nowrap; }
</style>
