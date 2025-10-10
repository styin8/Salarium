import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const Login = () => import('../views/Login.vue')
const Persons = () => import('../views/Persons.vue')
const Salaries = () => import('../views/Salaries.vue')
const Stats = () => import('../views/Stats.vue')

const routes = [
  { path: '/', redirect: '/stats' },
  { path: '/login', component: Login },
  { path: '/stats', component: Stats },
  { path: '/persons', component: Persons },
  { path: '/salaries/:personId?', component: Salaries },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const user = useUserStore()
  const publicPaths = ['/login']
  if (!user.token && !publicPaths.includes(to.path)) {
    return '/login'
  }
})

export default router