import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
})

let router = null
let userStore = null

export function setupAxiosInterceptors(routerInstance, store) {
  router = routerInstance
  userStore = store

  api.interceptors.request.use(
    (config) => {
      if (userStore?.token) {
        config.headers.Authorization = `Bearer ${userStore.token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  api.interceptors.response.use(
    (response) => {
      return response
    },
    (error) => {
      if (error.response?.status === 401) {
        const currentPath = router.currentRoute.value.fullPath
        const isLoginPage = currentPath === '/login'
        const isAuthEndpoint = error.config?.url?.includes('/auth/login') || 
                              error.config?.url?.includes('/auth/register') ||
                              error.config?.url?.includes('/auth/refresh')

        if (!isAuthEndpoint && !isLoginPage) {
          if (userStore) {
            userStore.logout()
          }
          
          ElMessage.warning('登录已过期，请重新登录')
          
          router.replace({
            path: '/login',
            query: { redirect: currentPath }
          })
        }
      }
      return Promise.reject(error)
    }
  )
}

export default api
