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
          :disabled="hasGenerated && loading"
          @click="handleGenerate"
        >
          {{ loading ? 'AI 正在思考方案中...' : (hasGenerated ? '重新生成食谱' : '生成专属减脂食谱') }}
        </el-button>

        <el-button
          v-if="hasGenerated"
          size="large"
          class="w-full mt-2"
          :disabled="loading"
          @click="handleReset"
        >
          重新开始会话
        </el-button>
      </el-form>
    </div>

    <!-- 右侧：聊天式展示区（用户/AI 左右气泡，支持 Markdown 与流式打字机） -->
    <div class="lg:col-span-7 bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
      <h2 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        <el-icon class="text-blue-500"><Document /></el-icon> AI 智能推荐方案
      </h2>

      <div
        ref="chatContainer"
        class="flex-1 bg-slate-50 p-4 rounded-lg border border-slate-200 overflow-y-auto max-h-[520px] min-h-[320px] space-y-4"
      >
        <!-- 初始未生成状态 -->
        <div v-if="messages.length === 0 && !loading" class="text-slate-400 text-center py-24">
          👈 在左侧填写参数并点击"生成"，即可查看 AI 流式生成的食谱方案
        </div>

        <!-- 消息气泡 -->
        <div
          v-for="(m, idx) in messages"
          :key="idx"
          class="flex"
          :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <!-- 用户气泡（右） -->
          <div
            v-if="m.role === 'user'"
            class="max-w-[80%] bg-emerald-500 text-white rounded-2xl rounded-tr-sm px-4 py-2 text-sm leading-relaxed whitespace-pre-wrap shadow-sm"
          >
            {{ m.content }}
          </div>

          <!-- AI 气泡（左） -->
          <div
            v-else
            class="max-w-[90%] bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm"
          >
            <div
              v-if="m.content"
              class="prose max-w-none font-sans text-slate-700 leading-relaxed text-sm"
              v-html="renderMarkdown(m.content)"
            ></div>
            <!-- 流式动画光标（仅最后一条 AI 且正在加载时） -->
            <span
              v-if="loading && idx === messages.length - 1 && !m.content"
              class="text-slate-400 text-sm"
            >AI 正在思考方案中...</span>
            <span
              v-if="loading && idx === messages.length - 1 && m.content"
              class="inline-block w-2 h-4 bg-emerald-500 animate-pulse ml-1 align-middle"
            ></span>
          </div>
        </div>
      </div>

      <!-- 多轮追问输入框：首次生成完成后出现 -->
      <div v-if="hasGenerated" class="mt-4 flex gap-2">
        <el-input
          v-model="followUpMsg"
          placeholder="继续追问，例如：把早餐换成更低脂的方案 / 午餐用到的鸡胸肉热量是多少？"
          :disabled="loading"
          @keyup.enter="handleFollowUp"
        />
        <el-button
          type="primary"
          :loading="loading"
          @click="handleFollowUp"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { generateDietStream, getDietHistory, clearDietSession } from '../api/diet'
import { ElMessage } from 'element-plus'
import { MagicStick, Document } from '@element-plus/icons-vue'
import { marked } from 'marked'

// 关键：开启 marked 的 breaks 选项，把单个 \n 渲染为 <br>
marked.setOptions({
  breaks: true,  // 把 \n 转换为 <br>
  gfm: true,     // 启用 GitHub 风格 Markdown
})

interface ChatMsg {
  role: 'user' | 'assistant'
  content: string
}

const loading = ref(false)
const hasGenerated = ref(false)
const followUpMsg = ref('')
const messages = ref<ChatMsg[]>([])
const chatContainer = ref<HTMLElement | null>(null)

// sessionId 持久化到 localStorage：刷新/重开后仍能恢复同一会话的历史与记忆
const SESSION_KEY = 'fitbite_session_id'
const stored = typeof localStorage !== 'undefined' ? localStorage.getItem(SESSION_KEY) : null
const sessionId = ref(
  stored || `sess-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
)
if (!stored && typeof localStorage !== 'undefined') {
  localStorage.setItem(SESSION_KEY, sessionId.value)
}

const renderMarkdown = (content: string): string => {
  if (!content) return ''
  return marked.parse(content) as string
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

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

// 首轮生成：把体征拼成一句可读的「用户提问」展示在气泡里
const buildUserText = () => {
  const genderTxt = form.gender === 'male' ? '男' : '女'
  return `生成减脂餐方案（${genderTxt} / ${form.age}岁 / ${form.height}cm / ${form.weight}kg / 活动:${form.activityLevel}）`
}

const streamInto = (
  aiIdx: number,
  payload: any,
  onDone: () => void
) => {
  generateDietStream(
    payload,
    (textChunk: string) => {
      messages.value[aiIdx].content += textChunk
      scrollToBottom()
    },
    () => {
      ElMessage.error('请求失败，请确认 Java 与 Python 服务均已启动')
      loading.value = false
    },
    () => {
      loading.value = false
      hasGenerated.value = true
      onDone()
    }
  )
}

const handleGenerate = () => {
  if (loading.value) return
  loading.value = true
  messages.value.push({ role: 'user', content: buildUserText() })
  messages.value.push({ role: 'assistant', content: '' })
  const aiIdx = messages.value.length - 1
  scrollToBottom()
  streamInto(aiIdx, { ...form, sessionId: sessionId.value }, () => {
    ElMessage.success('方案生成完毕！可继续在下方追问')
  })
}

// 多轮追问：只传 sessionId + message
const handleFollowUp = () => {
  const msg = followUpMsg.value.trim()
  if (!msg || loading.value) return
  followUpMsg.value = ''
  loading.value = true
  messages.value.push({ role: 'user', content: msg })
  messages.value.push({ role: 'assistant', content: '' })
  const aiIdx = messages.value.length - 1
  scrollToBottom()
  streamInto(aiIdx, { sessionId: sessionId.value, message: msg }, () => {
    ElMessage.success('已更新方案')
  })
}

// 重新开始：清空后端记忆 + 本地存储，开新会话
const handleReset = async () => {
  try {
    await clearDietSession(sessionId.value)
  } catch (e) {
    // 后端未启动时忽略，前端至少清空展示
  }
  sessionId.value = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(SESSION_KEY, sessionId.value)
  }
  messages.value = []
  hasGenerated.value = false
  followUpMsg.value = ''
  ElMessage.info('已开启新会话')
}

// 页面加载时恢复历史（用户提问 + AI 回答）
onMounted(async () => {
  try {
    const res = await getDietHistory(sessionId.value)
    const turns = res?.data?.turns || []
    if (turns.length) {
      messages.value = turns.map((t: any) => ({
        role: t.role === 'user' ? 'user' : 'assistant',
        content: t.content || ''
      }))
      hasGenerated.value = true
      await scrollToBottom()
    }
  } catch (e) {
    // 历史接口不可用（如后端未启动）时忽略，正常空白开始
  }
})
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
