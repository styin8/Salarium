<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  DollarSign, 
  Calendar, 
  TrendingUp, 
  Award, 
  Shield, 
  Calculator, 
  Trash2, 
  ArrowLeft,
  User,
  FileText,
  Edit,
  Filter
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const user = useUserStore()
const personId = ref(Number(route.params.personId))
const personName = ref('')
const list = ref([])
const filteredList = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

// 筛选条件
const filterYear = ref(null)
const filterMonth = ref(null)

const form = ref({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  base_salary: 0,
  performance_percent: null,
  performance_fixed: null,
  allowances: {},
  bonuses: {},
  ins_pension: 0,
  ins_medical: 0,
  ins_unemployment: 0,
  ins_injury: 0,
  ins_maternity: 0,
  housing_fund: 0,
  tax: 0,
  auto_tax: false,
  note: '',
})

const api = axios.create({ baseURL: '/api', headers: { Authorization: `Bearer ${user.token}` } })

// 计算统计数据 - 基于筛选后的数据
const stats = computed(() => {
  if (filteredList.value.length === 0) return { total: 0, average: 0, latest: 0 }
  
  const total = filteredList.value.reduce((sum, item) => sum + (item.net_income || 0), 0)
  const average = total / filteredList.value.length
  const latest = filteredList.value.length > 0 ? filteredList.value[filteredList.value.length - 1].net_income || 0 : 0
  
  return { total, average, latest }
})

// 获取年份选项
const yearOptions = computed(() => {
  const years = [...new Set(list.value.map(item => item.year))].sort((a, b) => b - a)
  return years
})

// 筛选数据
const filterData = () => {
  let filtered = [...list.value]
  
  if (filterYear.value) {
    filtered = filtered.filter(item => item.year === filterYear.value)
  }
  
  if (filterMonth.value) {
    filtered = filtered.filter(item => item.month === filterMonth.value)
  }
  
  // 按时间排序
  filtered.sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year
    return b.month - a.month
  })
  
  filteredList.value = filtered
}

// 监听筛选条件变化
watch([filterYear, filterMonth], filterData)
watch(list, filterData, { immediate: true })

async function load() {
  if (!personId.value) return
  loading.value = true
  try {
    const { data } = await api.get('/salaries/', { params: { person_id: personId.value } })
    list.value = data
    
    // 获取人员姓名
    const { data: persons } = await api.get('/persons/')
    const person = persons.find(p => p.id === personId.value)
    personName.value = person ? person.name : `人员 ${personId.value}`
  } catch (error) {
    ElMessage.error('加载工资记录失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    base_salary: 0,
    performance_percent: null,
    performance_fixed: null,
    allowances: {},
    bonuses: {},
    ins_pension: 0,
    ins_medical: 0,
    ins_unemployment: 0,
    ins_injury: 0,
    ins_maternity: 0,
    housing_fund: 0,
    tax: 0,
    auto_tax: false,
    note: '',
  }
  dialogVisible.value = true
}

function openEdit(salary) {
  isEditing.value = true
  editingId.value = salary.id
  form.value = {
    year: salary.year,
    month: salary.month,
    base_salary: salary.base_salary,
    performance_percent: salary.performance_percent,
    performance_fixed: salary.performance_fixed,
    allowances: salary.allowances || {},
    bonuses: salary.bonuses || {},
    ins_pension: salary.ins_pension,
    ins_medical: salary.ins_medical,
    ins_unemployment: salary.ins_unemployment,
    ins_injury: salary.ins_injury,
    ins_maternity: salary.ins_maternity,
    housing_fund: salary.housing_fund,
    tax: salary.tax,
    auto_tax: salary.auto_tax,
    note: salary.note || '',
  }
  dialogVisible.value = true
}

async function submit() {
  if (form.value.base_salary < 0) {
    ElMessage.warning('基础工资不能为负数')
    return
  }
  
  try {
    if (isEditing.value) {
      // 更新记录
      const { data } = await api.put(`/salaries/${editingId.value}`, form.value)
      const index = list.value.findIndex(item => item.id === editingId.value)
      if (index !== -1) {
        list.value[index] = data
      }
      ElMessage.success('工资记录更新成功')
    } else {
      // 新增记录
      const { data } = await api.post(`/salaries/${personId.value}`, form.value)
      list.value.push(data)
      ElMessage.success('工资记录添加成功')
    }
    dialogVisible.value = false
  } catch (error) {
    console.error('操作工资记录失败:', error)
    if (error.response) {
      ElMessage.error(`操作失败: ${error.response.data.detail || '服务器错误'}`)
    } else {
      ElMessage.error('操作工资记录失败，请检查网络连接')
    }
  }
}

async function remove(id, yearMonth) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${yearMonth} 的工资记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await api.delete(`/salaries/${id}`)
    list.value = list.value.filter(i => i.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(amount || 0)
}

function goBack() {
  router.push('/persons')
}

function clearFilters() {
  filterYear.value = null
  filterMonth.value = null
}

watch(() => route.params.personId, (v) => { 
  personId.value = Number(v)
  load() 
})

onMounted(load)
</script>

<template>
  <div class="salaries-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-nav">
          <button class="back-btn" @click="goBack">
            <ArrowLeft class="back-icon" />
            返回人员列表
          </button>
        </div>
        <div class="header-title">
          <DollarSign class="title-icon" />
          <div>
            <h1>{{ personName }} 的工资记录</h1>
            <p class="header-subtitle">管理和查看工资详情</p>
          </div>
        </div>
      </div>
      <button class="btn btn-primary" @click="openCreate" :disabled="!personId">
        <Plus class="btn-icon" />
        新增记录
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-primary">
          <Calculator />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ formatCurrency(stats.latest) }}</div>
          <div class="stat-label">最新工资</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon stat-icon-success">
          <TrendingUp />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ formatCurrency(stats.average) }}</div>
          <div class="stat-label">平均工资</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon stat-icon-info">
          <Award />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ filteredList.length }}</div>
          <div class="stat-label">筛选记录数</div>
        </div>
      </div>
    </div>

    <!-- 工资记录列表 -->
    <div class="content-card">
      <div class="card-header">
        <h2 class="card-title">工资记录</h2>
      </div>
      
      <!-- 筛选器  -->
      <div class="filter-section">
        <div class="filter-controls">
          <div class="filter-group">
            <label class="filter-label">年份：</label>
            <select v-model="filterYear" class="filter-select">
              <option :value="null">全部年份</option>
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">月份：</label>
            <select v-model="filterMonth" class="filter-select">
              <option :value="null">全部月份</option>
              <option v-for="month in 12" :key="month" :value="month">{{ month }}月</option>
            </select>
          </div>
          <button class="btn btn-clear" @click="clearFilters">
            清除筛选
          </button>
        </div>
      </div>

      <div class="table-container" v-loading="loading">
        <div v-if="filteredList.length === 0 && !loading" class="empty-state">
          <DollarSign class="empty-icon" />
          <h3>{{ list.length === 0 ? '暂无工资记录' : '没有符合条件的记录' }}</h3>
          <p>{{ list.length === 0 ? '点击上方按钮添加第一条工资记录' : '请调整筛选条件或清除筛选' }}</p>
        </div>
        
        <div v-else class="table-wrapper">
          <table class="salary-table">
            <thead>
              <tr>
                <th class="col-date">时间</th>
                <th class="col-currency">基础工资</th>
                <th class="col-currency">绩效</th>
                <th class="col-currency">补贴</th>
                <th class="col-currency">奖金福利</th>
                <th class="col-currency">五险一金</th>
                <th class="col-currency">个税</th>
                <th class="col-currency">实发工资</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="salary in filteredList" :key="salary.id" class="table-row">
                <td class="col-date">
                  <div class="date-cell">
                    <Calendar class="date-icon" />
                    <span>{{ salary.year }}/{{ salary.month.toString().padStart(2, '0') }}</span>
                  </div>
                </td>
                <td class="col-currency">{{ formatCurrency(salary.base_salary) }}</td>
                <td class="col-currency">{{ formatCurrency(salary.performance) }}</td>
                <td class="col-currency">{{ formatCurrency(salary.allowances_total) }}</td>
                <td class="col-currency">{{ formatCurrency(salary.bonuses_total) }}</td>
                <td class="col-currency text-danger">-{{ formatCurrency(salary.insurance_total) }}</td>
                <td class="col-currency text-danger">-{{ formatCurrency(salary.tax) }}</td>
                <td class="col-currency net-income">{{ formatCurrency(salary.net_income) }}</td>
                <td class="col-actions">
                  <div class="action-buttons">
                    <button 
                      class="action-btn btn-edit"
                      @click="openEdit(salary)"
                      title="编辑记录"
                    >
                      <Edit class="action-icon" />
                    </button>
                    <button 
                      class="action-btn btn-delete"
                      @click="remove(salary.id, `${salary.year}年${salary.month}月`)"
                      title="删除记录"
                    >
                      <Trash2 class="action-icon" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 新增/编辑工资记录对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditing ? '编辑工资记录' : '新增工资记录'" 
      width="800px"
      :close-on-click-modal="false"
    >
      <form @submit.prevent="submit" class="salary-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <Calendar class="section-icon" />
            基本信息
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">年份 <span class="required">*</span></label>
              <input 
                v-model.number="form.year" 
                type="number" 
                class="form-control" 
                :min="2000" 
                :max="2100"
              />
            </div>
            <div class="form-group">
              <label class="form-label">月份 <span class="required">*</span></label>
              <input 
                v-model.number="form.month" 
                type="number" 
                class="form-control" 
                :min="1" 
                :max="12"
              />
            </div>
          </div>
        </div>

        <!-- 工资构成 -->
        <div class="form-section">
          <h3 class="section-title">
            <DollarSign class="section-icon" />
            工资构成
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">基础工资 <span class="required">*</span></label>
              <input 
                v-model.number="form.base_salary" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
            <div class="form-group">
              <label class="form-label">绩效比例</label>
              <input 
                v-model.number="form.performance_percent" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
                placeholder="如 0.2 表示 20%"
              />
            </div>
            <div class="form-group">
              <label class="form-label">绩效固定</label>
              <input 
                v-model.number="form.performance_fixed" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
          </div>
        </div>

        <!-- 五险一金 -->
        <div class="form-section">
          <h3 class="section-title">
            <Shield class="section-icon" />
            五险一金
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">养老保险</label>
              <input 
                v-model.number="form.ins_pension" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
            <div class="form-group">
              <label class="form-label">医疗保险</label>
              <input 
                v-model.number="form.ins_medical" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
            <div class="form-group">
              <label class="form-label">失业保险</label>
              <input 
                v-model.number="form.ins_unemployment" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">工伤保险</label>
              <input 
                v-model.number="form.ins_injury" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
            <div class="form-group">
              <label class="form-label">生育保险</label>
              <input 
                v-model.number="form.ins_maternity" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
            <div class="form-group">
              <label class="form-label">住房公积金</label>
              <input 
                v-model.number="form.housing_fund" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
          </div>
        </div>

        <!-- 其他信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <FileText class="section-icon" />
            其他信息
          </h3>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">个人所得税</label>
              <input 
                v-model.number="form.tax" 
                type="number" 
                class="form-control" 
                :min="0"
                step="0.01"
              />
            </div>
            <div class="form-group">
              <label class="form-label">自动计税</label>
              <div class="switch-container">
                <input 
                  v-model="form.auto_tax" 
                  type="checkbox" 
                  class="form-switch"
                />
                <span class="switch-text">{{ form.auto_tax ? '开启' : '关闭' }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea 
              v-model="form.note" 
              class="form-control textarea" 
              placeholder="请输入备注信息（可选）"
              rows="3"
              maxlength="200"
            ></textarea>
          </div>
        </div>
      </form>
      
      <template #footer>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="dialogVisible = false">
            取消
          </button>
          <button class="btn btn-primary" @click="submit">
            保存记录
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.salaries-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 1rem;
}

.header-content {
  flex: 1;
}

.header-nav {
  margin-bottom: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #f9fafb;
  color: #374151;
}

.back-icon {
  width: 16px;
  height: 16px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  width: 32px;
  height: 32px;
  color: #3b82f6;
}

.header-title h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.header-subtitle {
  color: #6b7280;
  font-size: 1rem;
  margin: 0.25rem 0 0 0;
}

/* 筛选器样式 */
.filter-section {
  background: white;
  border-radius: 12px;
  margin: 1.5rem;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.filter-icon {
  width: 20px;
  height: 20px;
  color: #3b82f6;
}

.filter-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
  white-space: nowrap;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  min-width: 120px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-clear {
  background: #f3f4f6;
  color: #6b7280;
  border-color: #d1d5db;
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

.btn-clear:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
  color: #374151;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-primary {
  background: #3b82f6;
}

.stat-icon-success {
  background: #10b981;
}

.stat-icon-info {
  background: #6366f1;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.content-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.table-container {
  padding: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.25rem;
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

/* 表格样式优化 */
.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.salary-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  background: white;
}

.salary-table th {
  background: #f8fafc;
  color: #374151;
  font-weight: 600;
  padding: 1rem 0.75rem;
  text-align: left;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.salary-table td {
  padding: 1rem 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.table-row:hover {
  background: #f9fafb;
}

/* 列宽定义 */
.col-date {
  width: 120px;
  min-width: 120px;
}

.col-currency {
  width: 110px;
  min-width: 110px;
  text-align: right;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-weight: 500;
}

.col-actions {
  width: 120px;
  min-width: 120px;
  text-align: center;
}

.date-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.date-icon {
  width: 16px;
  height: 16px;
  color: #6b7280;
  flex-shrink: 0;
}

.net-income {
  color: #10b981;
  font-weight: 600;
}

.text-danger {
  color: #ef4444;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  border: 1px solid;
  cursor: pointer;
  background: transparent;
}

.action-icon {
  width: 16px;
  height: 16px;
}

.btn-edit {
  color: #3b82f6;
  border-color: #3b82f6;
}

.btn-edit:hover {
  background: #3b82f6;
  color: white;
}

.btn-delete {
  color: #ef4444;
  border-color: #ef4444;
}

.btn-delete:hover {
  background: #ef4444;
  color: white;
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid;
  text-decoration: none;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  border-color: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  border-color: #6b7280;
}

.btn-secondary:hover {
  background: #4b5563;
  border-color: #4b5563;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 表单样式 */
.salary-form {
  max-height: 60vh;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #3b82f6;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #111827;
  font-size: 0.875rem;
}

.required {
  color: #ef4444;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.textarea {
  resize: vertical;
  min-height: 80px;
}

.switch-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-switch {
  width: 20px;
  height: 20px;
}

.switch-text {
  font-size: 0.875rem;
  color: #6b7280;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .salaries-container {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    min-width: auto;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .table-wrapper {
    overflow-x: scroll;
  }
  
  .salary-table {
    min-width: 800px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .header-title h1 {
    font-size: 1.5rem;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .stat-number {
    font-size: 1.25rem;
  }
}
</style>