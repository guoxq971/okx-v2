import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import App from './App.vue'
import 'ant-design-vue/dist/reset.css'
import './style.css'
import zhCN from 'ant-design-vue/es/locale/zh_CN';

const app = createApp(App)

app.use(createPinia())
app.use(Antd)

app.mount('#app')
