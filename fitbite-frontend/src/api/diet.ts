import axios from 'axios'

// 1. 创建通用 Axios 实例（用于传统 CRUD 请求，连接 Java 后端）
export const api = axios.create({
  baseURL: 'http://localhost:8080/api/v1',
  timeout: 10000
})

// 2. 封装 SSE 流式请求（用于接收 DeepSeek 生成减脂餐的打字机流，并清洗 "data:" 前缀）
export function generateDietStream(
  data: any,
  onMessage: (text: string) => void,
  onError: (err: any) => void,
  onComplete: () => void
) {
  fetch('http://localhost:8080/api/v1/ai/diet/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(async (response) => {
      if (!response.ok) throw new Error('网络请求失败')
      const reader = response.body?.getReader()
      const decoder = new TextDecoder('utf-8')

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })

        // 按行切分，清洗掉 SSE 协议的 "data:" 前缀
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const content = line.replace(/^data:/, '')
            onMessage(content)
          } else if (line.trim() !== '') {
            onMessage(line)
          }
        }
      }
      onComplete()
    })
    .catch((err) => {
      onError(err)
    })
}

// 3. 添加一笔饮食打卡记录（Java 后端接口）
export function addDietRecord(data: {
  userId: number
  recordDate?: string
  mealType: string
  foodName: string
  calories: number
  protein?: number
  carbs?: number
  fat?: number
  aiAdvice?: string
}) {
  return api.post('/diet/record/add', data)
}

// 4. 获取指定日期的热量账本汇总及明细（Java 后端接口）
export function getDailySummary(userId: number, date?: string) {
  return api.get('/diet/record/summary', {
    params: { userId, date }
  })
}