<template>
  <div class="min-h-screen bg-slate-100 p-6">
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
          <!-- 新增：菜品食材检索选项卡 -->
          <el-tab-pane label="🥗 菜品食材检索" name="library">
            <DishLibrary />
          </el-tab-pane>
        </el-tabs>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Food } from '@element-plus/icons-vue'
import DietGenerator from './components/DietGenerator.vue'
import DietDashboard from './components/DietDashboard.vue'
import DishLibrary from './components/DishLibrary.vue' // 👈 1. 引入新组件

const activeTab = ref('ai')
</script>

<style>
/* 优化 Tab 边框样式 */
.el-tabs--border-card {
  border: none !important;
}
</style>