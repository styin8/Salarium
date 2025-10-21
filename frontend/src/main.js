import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
// Element Plus visual alignment overrides (align tables with Salaries page)
import './assets/element-plus-overrides.css'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.use(createPinia())
app.mount('#app')
