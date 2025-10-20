import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const Login = () => import('../views/Login.vue')
const Persons = () => import('../views/Persons.vue')
const Salaries = () => import('../views/Salaries.vue')

// Stats module with tabs/routes
const StatsIndex = () => import('../views/stats/Index.vue')
const StatsNet = () => import('../views/stats/Net.vue')
const StatsComposition = () => import('../views/stats/Composition.vue')
const StatsDeductions = () => import('../views/stats/Deductions.vue')
const StatsCumulative = () => import('../views/stats/Cumulative.vue')
const StatsTable = () => import('../views/stats/Table.vue')

const routes = [
  { path: '/', redirect: '/stats' },
  { path: '/login', component: Login },
  {
    path: '/stats',
    component: StatsIndex,
    redirect: { name: 'stats-net' },
    children: [
      { path: 'net', name: 'stats-net', component: StatsNet },
      { path: 'composition', name: 'stats-composition', component: StatsComposition },
      { path: 'deductions', name: 'stats-deductions', component: StatsDeductions },
      { path: 'cumulative', name: 'stats-cumulative', component: StatsCumulative },
      { path: 'table', name: 'stats-table', component: StatsTable },
    ],
  },
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
