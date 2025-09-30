<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from './store/user'

const router = useRouter()
const user = useUserStore()

function handleLogout() {
  user.logout()
  router.push('/login')
}
</script>

<template>
  <el-container style="min-height:100vh">
    <el-header>
      <div style="display:flex;align-items:center;justify-content:space-between">
        <div>
          <el-menu mode="horizontal" :default-active="$route.path" router>
            <el-menu-item index="/persons">人员</el-menu-item>
            <el-menu-item index="/stats">统计</el-menu-item>
          </el-menu>
        </div>
        <div>
          <el-button v-if="!user.token" type="primary" @click="router.push('/login')">登录</el-button>
          <el-dropdown v-else>
            <span class="el-dropdown-link">{{ user.username || '已登录' }}</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
  
  <el-backtop :right="20" :bottom="40" />
</template>

<style scoped>
.el-header { background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
</style>
