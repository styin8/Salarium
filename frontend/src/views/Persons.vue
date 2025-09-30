<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '../store/user'

const user = useUserStore()
const list = ref([])
const dialogVisible = ref(false)
const form = ref({ name: '', note: '' })

const api = axios.create({
  baseURL: '/api',
  headers: { Authorization: `Bearer ${user.token}` },
})

async function load() {
  const { data } = await api.get('/persons/')
  list.value = data
}

function openCreate() {
  form.value = { name: '', note: '' }
  dialogVisible.value = true
}

async function submit() {
  const { data } = await api.post('/persons/', form.value)
  list.value.push(data)
  dialogVisible.value = false
}

async function remove(id) {
  await api.delete(`/persons/${id}`)
  list.value = list.value.filter(i => i.id !== id)
}

onMounted(load)
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px">
      <h3>人员管理</h3>
      <el-button type="primary" @click="openCreate">新增人员</el-button>
    </div>
    <el-table :data="list" style="width:100%">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="note" label="备注" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/salaries/${row.id}`)">工资</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新增人员" width="400px">
      <el-form label-width="80px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>