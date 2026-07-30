import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './style.css' // 引入包含 Tailwind CSS 的样式
import App from './App.vue'

// 1. 创建 Vue 应用实例
const app = createApp(App)

// 2. 全局注册 Element Plus 的所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 3. 挂载 Pinia (状态管理) 与 Element Plus (UI组件库)
app.use(createPinia())
app.use(ElementPlus)

// 4. 将 Vue 应用挂载到 index.html 的 #app 节点上
app.mount('#app')