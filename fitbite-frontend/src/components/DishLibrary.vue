<template>
  <div class="space-y-6">
    <!-- 食材多选筛选区 -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
          <el-icon class="text-emerald-500"><Food /></el-icon> 食材可视化挑选（多选联动）
        </h2>
        <el-button v-if="selectedIds.length > 0" size="small" type="info" text @click="clearSelection">
          重置选择 (已选 {{ selectedIds.length }} 个)
        </el-button>
      </div>

      <!-- 食材分类卡片列表 -->
      <div class="space-y-4">
        <div v-for="(group, categoryKey) in groupedIngredients" :key="categoryKey">
          <span class="text-xs font-semibold text-slate-400 block mb-2">{{ getCategoryName(categoryKey) }}</span>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="item in group"
              :key="item.id"
              @click="toggleIngredient(item.id)"
              :class="[
                'px-3 py-1.5 rounded-lg text-sm transition-all duration-200 flex items-center gap-1.5 border',
                selectedIds.includes(item.id)
                  ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm scale-105'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:border-emerald-300 hover:bg-emerald-50'
              ]"
            >
              <span>{{ item.icon }}</span>
              <span>{{ item.name }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 匹配的菜品展示卡片列表 -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
      <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        <el-icon class="text-blue-500"><List /></el-icon> 匹配菜品列表 ({{ dishes.length }})
      </h2>

      <div v-if="dishes.length === 0" class="text-slate-400 text-center py-12">
        暂无包含选中食材的菜品，尝试切换其他食材组合吧！
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="dish in dishes"
          :key="dish.id"
          class="p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:shadow-md transition-shadow flex flex-col justify-between"
        >
          <div>
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-bold text-slate-800 text-base">{{ dish.name }}</h3>
              <span class="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">
                {{ dish.calories }} kcal
              </span>
            </div>
            <p class="text-xs text-slate-500 mb-3">{{ dish.description }}</p>

            <div class="flex flex-wrap gap-1 mb-3">
              <el-tag
                v-for="name in dish.ingredientNames"
                :key="name"
                size="small"
                type="success"
                effect="plain"
              >
                {{ name }}
              </el-tag>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-200/60 flex justify-between items-center text-xs text-slate-500">
            <span>蛋: {{ dish.protein }}g | 碳: {{ dish.carbs }}g | 脂: {{ dish.fat }}g</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getIngredients, searchDishesByIngredients } from '../api/diet'
import { Food, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Ingredient {
  id: number
  name: string
  category: string
  icon: string
}

interface Dish {
  id: number
  name: string
  calories: number
  protein: number
  carbs: number
  fat: number
  description: string
  ingredientNames: string[]
}

const ingredients = ref<Ingredient[]>([])
const dishes = ref<Dish[]>([])
const selectedIds = ref<number[]>([])

// 按分类分组食材
const groupedIngredients = computed(() => {
  const groups: Record<string, Ingredient[]> = {}
  ingredients.value.forEach(item => {
    if (!groups[item.category]) groups[item.category] = []
    groups[item.category].push(item)
  })
  return groups
})

const getCategoryName = (key: string) => {
  const map: Record<string, string> = { meat: '🥩 肉禽蛋类', veg: '🥦 蔬菜类', carb: '🍚 优质碳水', other: '其他' }
  return map[key] || '其他'
}

// 点击/取消选择食材
const toggleIngredient = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
  fetchDishes()
}

const clearSelection = () => {
  selectedIds.value = []
  fetchDishes()
}

const loadIngredients = async () => {
  try {
    const res = await getIngredients()
    // 兼容 Axios 包装格式及 R/Result 统一响应结构
    const list = res.data?.data || res.data || []
    ingredients.value = Array.isArray(list) ? list : []
  } catch (err) {
    console.error('获取食材库失败:', err)
    ElMessage.error('获取食材库失败')
  }
}

const fetchDishes = async () => {
  try {
    const res = await searchDishesByIngredients(selectedIds.value)
    // 兼容 Axios 包装格式及 R/Result 统一响应结构
    const list = res.data?.data || res.data || []
    dishes.value = Array.isArray(list) ? list : []
  } catch (err) {
    console.error('查询菜品失败:', err)
    ElMessage.error('查询菜品失败')
  }
}

onMounted(() => {
  loadIngredients()
  fetchDishes()
})
</script>