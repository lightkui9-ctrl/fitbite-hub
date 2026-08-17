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

      // 累积 buffer，按 SSE 事件边界 (\n\n) 切分，避免吞掉 AI 输出内的换行
      let buffer = ''

      const flushEvents = (buf: string): { rest: string; events: string[] } => {
        const events: string[] = []
        let endIdx = buf.indexOf('\n\n')
        while (endIdx !== -1) {
          events.push(buf.slice(0, endIdx))
          buf = buf.slice(endIdx + 2)
          endIdx = buf.indexOf('\n\n')
        }
        return { rest: buf, events }
      }

      const extractData = (event: string): string => {
        // SSE 事件可能跨多行 data:，按 \n 切分后拼接 data 部分
        // 关键修复：每行 data 后必须补回 \n，否则多行内容会被前端连成单行
        // （后端 to_sse_data() 用 f'data: {line}\n' 编码，前端解析时必须还原 \n）
        const lines = event.split('\n')
        const dataLines: string[] = []
        for (const line of lines) {
          if (line.startsWith('data:')) {
            // 去掉 "data:" 前缀，保留后续内容
            dataLines.push(line.replace(/^data:\s?/, ''))
          }
        }
        // 用 \n 拼接所有 data 行，正确还原 SSE 多行 data 中的换行
        return dataLines.join('\n')
      }

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const { rest, events } = flushEvents(buffer)
          buffer = rest
          for (const ev of events) {
            const content = extractData(ev)
            if (content) onMessage(content)
          }
        }
        // 流结束时处理剩余 buffer
        if (buffer.trim()) {
          const content = extractData(buffer)
          if (content) onMessage(content)
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

// 获取食材分类列表
export function getIngredients() {
  return api.get('/dish/ingredients')
}

// 根据食材多选搜索菜品
export function searchDishesByIngredients(ingredientIds: number[]) {
  return api.post('/dish/search', ingredientIds)
}