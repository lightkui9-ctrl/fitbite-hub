<template>
  <div class="space-y-6">
    <!-- 顶部数据概览卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium text-slate-400">今日总摄入</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">{{ summary.totalCalories }} <span class="text-sm font-normal text-slate-500">kcal</span></h3>
        </div>
        <div class="w-12 h-12 bg-amber-50 rounded-xl flex items-center justify-center text-amber-500">
          <el-icon class="text-2xl"><Orange /></el-icon>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium text-slate-400">蛋白质</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">{{ summary.totalProtein }} <span class="text-sm font-normal text-slate-500">g</span></h3>
        </div>
        <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-500">
          <el-icon class="text-2xl"><Bowl /></el-icon>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium text-slate-400">碳水化合物</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">{{ summary.totalCarbs }} <span class="text-sm font-normal text-slate-500">g</span></h3>
        </div>
        <div class="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center text-emerald-500">
          <el-icon class="text-2xl"><Apple /></el-icon>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div>
          <p class="text-xs font-medium text-slate-400">脂肪</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">{{ summary.totalFat }} <span class="text-sm font-normal text-slate-500">g</span></h3>
        </div>
        <div class="w-12 h-12 bg-rose-50 rounded-xl flex items-center justify-center text-rose-500">
          <el-icon class="text-2xl"><Dish /></el-icon>
        </div>
      </div>
    </div>

    <!-- 主体区域：左侧打卡表单，右侧当日明细表格 -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- 快速打卡表单 -->
      <div class="lg:col-span-4 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
        <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <el-icon class="text-emerald-500"><Plus /></el-icon> 记一笔饮食
        </h2>

        <el-form :model="recordForm" label-position="top">
          <el-form-item label="餐次">
            <el-radio-group v-model="recordForm.mealType" size="large" class="w-full">
              <el-radio-button label="breakfast">早餐</el-radio-button>
              <el-radio-button label="lunch">午餐</el-radio-button>
              <el-radio-button label="dinner">晚餐</el-radio-button>
              <el-radio-button label="snack">加餐</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="食物名称">
            <el-input v-model="recordForm.foodName" placeholder="例如：香煎鸡胸肉配沙拉" />
          </el-form-item>

          <el-form-item label="热量 (kcal)">
            <el-input-number v-model="recordForm.calories" :min="0" :step="10" class="w-full" />
          </el-form-item>

          <div class="grid grid-cols-3 gap-2">
            <el-form-item label="蛋白质(g)">
              <el-input-number v-model="recordForm.protein" :min="0" :controls="false" class="w-full" />
            </el-form-item>
            <el-form-item label="碳水(g)">
              <el-input-number v-model="recordForm.carbs" :min="0" :controls="false" class="w-full" />
            </el-form-item>
            <el-form-item label="脂肪(g)">
              <el-input-number v-model="recordForm.fat" :min="0" :controls="false" class="w-full" />
            </el-form-item>
          </div>

          <el-button type="primary" size="large" class="w-full mt-2" :loading="submitLoading" @click="handleSubmitRecord">
            提交打卡
          </el-button>
        </el-form>
      </div>

      <!-- 当日饮食记录列表 -->
      <div class="lg:col-span-8 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
            <el-icon class="text-blue-500"><List /></el-icon> 今日饮食明细
          </h2>
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            @change="fetchSummary"
          />
        </div>

        <el-table :data="summary.records" style="width: 100%" stripe empty-text="暂无打卡记录，快去左侧记一笔吧！">
          <el-table-column prop="mealType" label="餐次" width="100">
            <template #default="scope">
              <el-tag :type="getMealTagType(scope.row.mealType)">
                {{ getMealName(scope.row.mealType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="foodName" label="食物名称" min-width="140" />
          <el-table-column prop="calories" label="热量(kcal)" width="110" />
          <el-table-column label="营养素 (蛋/碳/脂)" min-width="150">
            <template #default="scope">
              <span class="text-xs text-slate-500">
                {{ scope.row.protein || 0 }}g / {{ scope.row.carbs || 0 }}g / {{ scope.row.fat || 0 }}g
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { addDietRecord, getDailySummary } from '../api/diet'
import { ElMessage } from 'element-plus'
import { Orange, Bowl, Apple, Dish, Plus, List } from '@element-plus/icons-vue'

const userId = 1 // 模拟当前登录用户 ID
const selectedDate = ref(new Date().toISOString().split('T')[0])
const submitLoading = ref(false)

const summary = reactive({
  totalCalories: 0,
  totalProtein: 0,
  totalCarbs: 0,
  totalFat: 0,
  records: []
})

const recordForm = reactive({
  userId: userId,
  mealType: 'lunch',
  foodName: '',
  calories: 350,
  protein: 25,
  carbs: 30,
  fat: 8
})

const fetchSummary = async () => {
  try {
    const res = await getDailySummary(userId, selectedDate.value)
    if (res.data) {
      summary.totalCalories = res.data.totalCalories || 0
      summary.totalProtein = res.data.totalProtein || 0
      summary.totalCarbs = res.data.totalCarbs || 0
      summary.totalFat = res.data.totalFat || 0
      summary.records = res.data.records || []
    }
  } catch (error) {
    ElMessage.error('获取打卡数据失败')
  }
}

const handleSubmitRecord = async () => {
  if (!recordForm.foodName) {
    ElMessage.warning('请输入食物名称')
    return
  }
  submitLoading.value = true
  try {
    await addDietRecord({ ...recordForm, recordDate: selectedDate.value })
    ElMessage.success('打卡成功！')
    recordForm.foodName = ''
    fetchSummary() // 重新刷新数据
  } catch (error) {
    ElMessage.error('打卡提交失败')
  } finally {
    submitLoading.value = false
  }
}

const getMealName = (type: string) => {
  const map: Record<string, string> = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐' }
  return map[type] || '未知'
}

const getMealTagType = (type: string) => {
  const map: Record<string, string> = { breakfast: 'warning', lunch: 'success', dinner: 'primary', snack: 'info' }
  return map[type] || ''
}

onMounted(() => {
  fetchSummary()
})
</script>