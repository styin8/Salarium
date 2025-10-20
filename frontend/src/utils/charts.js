import * as echarts from 'echarts'

export function initChart(el) {
  if (!el) return null
  return echarts.init(el)
}

export function baseGrid() {
  return { left: '3%', right: '3%', bottom: '8%', top: '12%', containLabel: true }
}

export function currencyFormatter(val) {
  if (val == null || isNaN(val)) return '¥0'
  return '¥' + Number(val).toLocaleString()
}

export function axisCurrencyFormatter(value) {
  return `¥${value}`
}

export function monthsToLabels(points) {
  return points.map(p => `${p.month}月`)
}

export function responsiveResize(instance) {
  if (!instance) return () => {}
  const handler = () => instance.resize()
  window.addEventListener('resize', handler)
  return () => window.removeEventListener('resize', handler)
}

export const palette = {
  primary: '#409EFF',
  success: '#67C23A',
  warning: '#E6A23C',
  danger: '#F56C6C',
  info: '#909399',
  blue: '#409EFF',
  green: '#67C23A',
  orange: '#E6A23C',
  purple: '#8e44ad',
  teal: '#1abc9c',
}

export function gradient(color1, color2) {
  return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: color1 },
    { offset: 1, color: color2 },
  ])
}
