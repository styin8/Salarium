<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'

const username = ref('')
const password = ref('')
const loading = ref(false)
const router = useRouter()
const user = useUserStore()

async function onSubmit() {
  loading.value = true
  try {
    const { data } = await axios.post('/api/auth/login', { username: username.value, password: password.value })
    user.setToken(data.access_token)
    user.setUsername(username.value)
    router.push('/persons')
  } catch (e) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width:360px;margin:60px auto">
    <el-card>
      <h3 style="margin-bottom:16px">登录</h3>
      <el-form @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" placeholder="请输入密码" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit" style="width:100%">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>