import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { installElement } from './plugins/element'
import './styles/index.scss'

const app = createApp(App)

installElement(app)
app.use(createPinia()).use(router).mount('#app')
