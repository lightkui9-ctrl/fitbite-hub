<template>
  <!-- 未登录：登录 / 注册 -->
  <AuthView v-if="!userStore.isLoggedIn" />

  <!-- 已登录：主应用 -->
  <div v-else class="min-h-screen bg-slate-100 p-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- 顶部 Header -->
      <header class="bg-white p-4 rounded-xl shadow-sm flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center text-white">
            <el-icon class="text-2xl"><Food /></el-icon>
          </div>
          <div>
            <h1 class="text-xl font-bold text-slate-800">FitBite 智膳</h1>
            <p class="text-xs text-slate-400">基于 AI Agent 的个性化减脂餐与健康管理系统</p>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <span class="text-sm text-slate-600">你好，{{ userStore.user?.username || '用户' }}</span>
          <el-button text :icon="Edit" @click="profileVisible = true">完善档案</el-button>
          <el-button type="primary" plain :icon="SwitchButton" @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <!-- 核心功能导航页签 -->
      <main class="bg-transparent">
        <el-tabs v-model="activeTab" type="border-card" class="rounded-xl shadow-sm overflow-hidden">
          <el-tab-pane label="🤖 AI 减脂餐定制" name="ai">
            <DietGenerator />
          </el-tab-pane>
          <el-tab-pane label="📊 每日热量账本" name="dashboard">
            <DietDashboard />
          </el-tab-pane>
          <el-tab-pane label="🥗 菜品食材检索" name="library">
            <DishLibrary />
          </el-tab-pane>
        </el-tabs>
      </main>

      <!-- 完善个人档案弹窗 -->
      <ProfileDialog v-model="profileVisible" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Food, Edit, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from './stores/user'
import AuthView from './components/AuthView.vue'
import ProfileDialog from './components/ProfileDialog.vue'
import DietGenerator from './components/DietGenerator.vue'
import DietDashboard from './components/DietDashboard.vue'
import DishLibrary from './components/DishLibrary.vue'

const userStore = useUserStore()
const activeTab = ref('ai')
const profileVisible = ref(false)

// 刷新后若仅有 token 而无 user，则拉取一次用户信息
onMounted(async () => {
  if (userStore.isLoggedIn && !userStore.user) {
    try {
      await userStore.fetchMe()
    } catch {
      userStore.logout()
    }
  }
})

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
}
</script>

<style>
/* 优化 Tab 边框样式 */
.el-tabs--border-card {
  border: none !important;
}
</style>
