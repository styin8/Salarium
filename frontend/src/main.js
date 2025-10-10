import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
import i18n from './i18n.js'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.use(createPinia())
app.use(i18n)
app.mount('#app')
