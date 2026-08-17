<template>
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
    <!-- 左侧：体征与食材表单 -->
    <div class="lg:col-span-5 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
      <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        <el-icon class="text-emerald-500"><MagicStick /></el-icon> AI 膳食定制参数
      </h2>

      <el-form :model="form" label-position="top">
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="性别">
            <el-select v-model="form.gender">
              <el-option label="男" value="male" />
              <el-option label="女" value="female" />
            </el-select>
          </el-form-item>
          <el-form-item label="年龄">
            <el-input-number v-model="form.age" :min="10" :max="100" class="w-full" />
          </el-form-item>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="身高 (cm)">
            <el-input-number v-model="form.height" :precision="1" class="w-full" />
          </el-form-item>
          <el-form-item label="体重 (kg)">
            <el-input-number v-model="form.weight" :precision="1" class="w-full" />
          </el-form-item>
        </div>

        <el-form-item label="日常活动量">
          <el-select v-model="form.activityLevel" class="w-full">
            <el-option label="久坐不动 (Sedentary)" value="sedentary" />
            <el-option label="轻度活动 (Light)" value="light" />
            <el-option label="中度活动 (Moderate)" value="moderate" />
            <el-option label="积极运动 (Active)" value="active" />
          </el-select>
        </el-form-item>

        <el-form-item label="现有食材 (回车添加)">
          <el-select
            v-model="form.availableIngredients"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="如：鸡胸肉, 西兰花, 鸡蛋"
            class="w-full"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="w-full mt-2"
          :loading="loading"
          @click="handleGenerate"
        >
          {{ loading ? 'AI 正在思考方案中...' : '生成专属减脂食谱' }}
        </el-button>
      </el-form>
    </div>

    <!-- 右侧：打字机流式输出展示区 (支持 Markdown 美化) -->
    <div class="lg:col-span-7 bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
      <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        <el-icon class="text-blue-500"><Document /></el-icon> AI 智能推荐方案
      </h2>

      <div class="flex-1 bg-slate-50 p-6 rounded-lg border border-slate-200 overflow-y-auto max-h-[550px] min-h-[380px]">
        <!-- 初始未生成状态 -->
        <div v-if="!rawAiResult && !loading" class="text-slate-400 text-center py-24">
          👈 在左侧填写参数并点击“生成”，即可查看 AI 流式生成的食谱方案
        </div>

        <!-- 流式生成/渲染状态 -->
        <div v-else class="prose max-w-none font-sans text-slate-700 leading-relaxed">
          <div v-html="parsedMarkdown"></div>
          <!-- 绿色的流式动画光标 -->
          <span v-if="loading" class="inline-block w-2 h-4 bg-emerald-500 animate-pulse ml-1 align-middle"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { generateDietStream } from '../api/diet'
import { ElMessage } from 'element-plus'
import { MagicStick, Document } from '@element-plus/icons-vue'
import { marked } from 'marked'

// 关键：开启 marked 的 breaks 选项，把单个 \n 渲染为 <br>
// 这是后端 normalize_markdown 的最后一道兜底防线——即便 AI 输出没换行，
// normalize 处理后的 \n 也能被前端正确识别为换行
marked.setOptions({
  breaks: true,  // 把 \n 转换为 <br>
  gfm: true,     // 启用 GitHub 风格 Markdown
})

const loading = ref(false)
const rawAiResult = ref('') // 存储清洗后的原始 Markdown 文本

// 响应式计算属性：实时把接收到的 Markdown 文本编译为漂亮的 HTML
const parsedMarkdown = computed(() => {
  return marked.parse(rawAiResult.value)
})

const form = reactive({
  gender: 'male',
  age: 23,
  height: 188,
  weight: 88,
  activityLevel: 'moderate',
  targetWeightLoss: 5,
  availableIngredients: ['鸡胸肉', '西兰花', '鸡蛋'],
  dietaryRestrictions: []
})

const handleGenerate = () => {
  rawAiResult.value = ''
  loading.value = true

  generateDietStream(
    form,
    (textChunk) => {
      // 这里的 textChunk 已经是 API 模块清洗掉 "data:" 后的纯内容
      rawAiResult.value += textChunk
    },
    (err) => {
      ElMessage.error('生成失败，请确认 Java 与 Python 服务均已启动')
      loading.value = false
    },
    () => {
      loading.value = false
      ElMessage.success('方案生成完毕！')
    }
  )
}
</script>

<style scoped>
/* 保证生成的 Markdown 样式层次清晰 */
:deep(.prose h1), :deep(.prose h2), :deep(.prose h3) {
  margin-top: 0.8em;
  margin-bottom: 0.4em;
  font-weight: 700;
  color: #1e293b;
}
:deep(.prose ul), :deep(.prose ol) {
  padding-left: 1.25em;
  margin-top: 0.4em;
  margin-bottom: 0.4em;
}
:deep(.prose li) {
  margin-top: 0.2em;
  margin-bottom: 0.2em;
}
:deep(.prose p) {
  margin-top: 0.4em;
  margin-bottom: 0.4em;
}
</style>