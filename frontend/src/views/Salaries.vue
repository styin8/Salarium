<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import { useUserStore } from '../store/user'

const route = useRoute()
const user = useUserStore()
const personId = ref(Number(route.params.personId))
const list = ref([])
const dialogVisible = ref(false)
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

async function load() {
  if (!personId.value) return
  const { data } = await api.get('/salaries/', { params: { person_id: personId.value } })
  list.value = data
}

function openCreate() {
  dialogVisible.value = true
}

async function submit() {
  const { data } = await api.post(`/salaries/${personId.value}`, form.value)
  list.value.push(data)
  dialogVisible.value = false
}

async function remove(id) {
  await api.delete(`/salaries/${id}`)
  list.value = list.value.filter(i => i.id !== id)
}

watch(() => route.params.personId, (v) => { personId.value = Number(v); load() })

onMounted(load)
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px">
      <h3>工资记录（人员ID：{{ personId }}）</h3>
      <el-button type="primary" @click="openCreate" :disabled="!personId">新增记录</el-button>
    </div>

    <el-table :data="list" style="width:100%">
      <el-table-column prop="year" label="年份" width="80" />
      <el-table-column prop="month" label="月份" width="80" />
      <el-table-column prop="base_salary" label="基础工资" />
      <el-table-column prop="performance" label="绩效" />
      <el-table-column prop="allowances_total" label="补贴" />
      <el-table-column prop="bonuses_total" label="奖金福利" />
      <el-table-column prop="insurance_total" label="五险一金" />
      <el-table-column prop="tax" label="个税" />
      <el-table-column prop="net_income" label="到手" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新增工资记录" width="700px">
      <el-form label-width="120px">
        <el-form-item label="年份"><el-input-number v-model="form.year" :min="2000" :max="2100" /></el-form-item>
        <el-form-item label="月份"><el-input-number v-model="form.month" :min="1" :max="12" /></el-form-item>
        <el-form-item label="基础工资"><el-input-number v-model="form.base_salary" :min="0" /></el-form-item>
        <el-form-item label="绩效比例"><el-input-number v-model="form.performance_percent" :step="0.01" :min="0" /></el-form-item>
        <el-form-item label="绩效固定"><el-input-number v-model="form.performance_fixed" :min="0" /></el-form-item>
        <el-form-item label="补贴(示例)"><el-input v-model="form.allowances['交通']" placeholder="交通" /></el-form-item>
        <el-form-item label="奖金(示例)"><el-input v-model="form.bonuses['年终奖']" placeholder="年终奖" /></el-form-item>
        <el-form-item label="养老"><el-input-number v-model="form.ins_pension" :min="0" /></el-form-item>
        <el-form-item label="医疗"><el-input-number v-model="form.ins_medical" :min="0" /></el-form-item>
        <el-form-item label="失业"><el-input-number v-model="form.ins_unemployment" :min="0" /></el-form-item>
        <el-form-item label="工伤"><el-input-number v-model="form.ins_injury" :min="0" /></el-form-item>
        <el-form-item label="生育"><el-input-number v-model="form.ins_maternity" :min="0" /></el-form-item>
        <el-form-item label="公积金"><el-input-number v-model="form.housing_fund" :min="0" /></el-form-item>
        <el-form-item label="个税"><el-input-number v-model="form.tax" :min="0" /></el-form-item>
        <el-form-item label="是否自动个税"><el-switch v-model="form.auto_tax" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>