<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '../store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Users, DollarSign, Trash2, Edit, User, TrendingUp, Calendar, Award } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const user = useUserStore()
const list = ref([])
const dialogVisible = ref(false)
const form = ref({ name: '', note: '' })
const loading = ref(false)

const api = axios.create({
  baseURL: '/api',
  headers: { Authorization: `Bearer ${user.token}` },
})

// Load persons data
async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/persons/')
    list.value = data
  } catch (error) {
    ElMessage.error(t('persons.loadError'))
  } finally {
    loading.value = false
  }
}

// Open create person dialog
function openCreate() {
  form.value = { name: '', note: '' }
  dialogVisible.value = true
}

// Submit new person
async function submit() {
  if (!form.value.name.trim()) {
    ElMessage.warning(t('persons.enterName'))
    return
  }
  
  try {
    const { data } = await api.post('/persons/', form.value)
    list.value.push(data)
    dialogVisible.value = false
    ElMessage.success(t('persons.addSuccess'))
  } catch (error) {
    ElMessage.error(t('persons.addError'))
  }
}

// Remove person
async function remove(id, name) {
  try {
    await ElMessageBox.confirm(
      t('persons.deleteConfirm', { name }),
      t('persons.confirmDelete'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      }
    )
    
    await api.delete(`/persons/${id}`)
    list.value = list.value.filter(i => i.id !== id)
    ElMessage.success(t('persons.deleteSuccess'))
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('persons.deleteError'))
    }
  }
}

onMounted(load)
</script>

<template>
  <div class="persons-container">
    <!-- Header Section -->
    <div class="persons-header">
      <div class="header-left">
        <h2 class="page-title">{{ t('persons.title') }}</h2>
        <p class="page-subtitle">{{ t('persons.subtitle') }}</p>
      </div>
      <div class="header-controls">
        <el-button type="primary" @click="openCreate" class="add-button">
          <Plus class="button-icon" />
          {{ t('persons.addPerson') }}
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards" v-loading="loading">
      <div class="stat-card gradient-blue">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ list.length }}</div>
          <div class="stat-label">{{ t('persons.totalCount') }}</div>
        </div>
      </div>
      <div class="stat-card gradient-green">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ list.length > 0 ? '100%' : '0%' }}</div>
          <div class="stat-label">{{ t('persons.activeRate') }}</div>
        </div>
      </div>
      <div class="stat-card gradient-orange">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-value">{{ new Date().getFullYear() }}</div>
          <div class="stat-label">{{ t('persons.currentYear') }}</div>
        </div>
      </div>
      <div class="stat-card gradient-purple">
        <div class="stat-icon">🏆</div>
        <div class="stat-content">
          <div class="stat-value">{{ list.length }}</div>
          <div class="stat-label">{{ t('persons.managedPersons') }}</div>
        </div>
      </div>
    </div>

    <!-- Persons List Section -->
    <el-card class="persons-list-card" shadow="hover" v-if="list.length > 0">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ t('persons.list') }}</span>
          <el-button @click="load" size="small" type="default">
            {{ t('common.refresh') }}
          </el-button>
        </div>
      </template>
      
      <div class="persons-grid">
        <div 
          v-for="person in list" 
          :key="person.id" 
          class="person-card"
        >
          <div class="person-avatar">
            <div class="avatar-icon">👤</div>
          </div>
          <div class="person-info">
            <h3 class="person-name">{{ person.name }}</h3>
            <p class="person-note" v-if="person.note">{{ person.note }}</p>
            <p class="person-note" v-else>{{ t('persons.noNote') }}</p>
          </div>
          <div class="person-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="$router.push(`/salaries/${person.id}`)"
              :icon="DollarSign"
            >
              {{ t('persons.salary') }}
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="remove(person.id, person.name)"
              :icon="Trash2"
            >
              {{ t('common.delete') }}
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Empty State -->
    <el-card class="empty-state-card" shadow="hover" v-if="list.length === 0 && !loading">
      <div class="empty-state">
        <div class="empty-icon">👥</div>
        <h3 class="empty-title">{{ t('persons.noPersons') }}</h3>
        <p class="empty-description">{{ t('persons.clickAddFirst') }}</p>
        <el-button type="primary" @click="openCreate" class="empty-action">
          <Plus class="button-icon" />
          {{ t('persons.addPerson') }}
        </el-button>
      </div>
    </el-card>

    <!-- Add Person Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="t('persons.addPerson')" 
      width="500px"
      class="person-dialog"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item :label="t('common.name')" required>
          <el-input 
            v-model="form.name" 
            :placeholder="t('persons.enterName')"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item :label="t('common.note')">
          <el-input 
            v-model="form.note" 
            type="textarea" 
            :placeholder="t('persons.enterNote')"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submit">{{ t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.persons-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 60px);
}

.persons-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  padding: 0 4px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.add-button {
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
}

.button-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.gradient-blue {
  --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-green {
  --gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-orange {
  --gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-purple {
  --gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon {
  font-size: 32px;
  margin-right: 16px;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.persons-list-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.persons-list-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.persons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.person-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.person-card:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.person-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 24px;
  color: white;
}

.person-info {
  flex: 1;
  min-width: 0;
}

.person-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.person-note {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.person-actions {
  flex-shrink: 0;
}

.empty-state-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.empty-description {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0 0 24px 0;
}

.empty-action {
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
}

.person-dialog {
  border-radius: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .persons-container {
    padding: 16px;
  }
  
  .persons-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .persons-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .person-card {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .persons-container {
    padding: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-icon {
    font-size: 28px;
    margin-right: 12px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .person-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .person-info {
    text-align: center;
  }
}
</style>