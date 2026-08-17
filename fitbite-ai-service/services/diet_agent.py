import re
import time
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.config import settings
from schemas.diet import DietGenerateRequest


def normalize_markdown(text: str) -> str:
    """
    后处理 Markdown 输出：补齐章节/列表项的换行，修复 AI 漏写的换行
    关键能力：即使 AI 输出完全没有 \n，也能强制在 ## 标题与 - 列表项前插入换行
    """
    if not text:
        return text

    # ===== 第 0 步：处理完全没有 \n 的情况（最关键的修复）=====
    # 0.1 在 ## 标题前插 \n\n —— 当前面是其他字符时（AI 经常输出 kcal## 直接紧贴）
    text = re.sub(r'([^\n])## ', r'\1\n\n## ', text)
    # 0.2 在 - 列表项前插 \n —— 当前面是其他字符时
    text = re.sub(r'([^\n])- ', r'\1\n- ', text)

    # ===== 第 1 步：补充 \n 后的空行（已有 \n 但缺空行的情况）=====
    # 1.1 确保 ## 标题前有空行（除字符串开头）
    text = re.sub(r'([^\n])\n(## )', r'\1\n\n\2', text)
    # 1.2 确保 ## 标题后有空行（除紧跟 - 列表的情况）
    text = re.sub(r'(## [^\n]+)\n(?!\n|-)', r'\1\n\n', text)

    # ===== 第 2 步：清理 3+ 连续换行 =====
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def to_sse_data(content: str) -> str:
    """
    将多行 content 格式化为合法的 SSE 多行 data 事件
    SSE 协议：每行必须以 "data: " 开头，事件以空行 (\\n\\n) 结尾
    """
    if not content:
        return "data: \n\n"
    lines = content.split('\n')
    return ''.join(f'data: {line}\n' for line in lines) + '\n'


class DietAgentService:
    """
    减脂餐智能体服务层
    处理体征计算、Prompt 组装以及大模型流式推理
    """

    def __init__(self):
        # 初始化大模型客户端
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.MODEL_NAME,
            streaming=True,
            temperature=0.3,  # 调低温度，让 AI 输出格式更稳定
            max_tokens=1500,  # 限制最大生成长度
        )

    @staticmethod
    def calculate_energy_needs(req: DietGenerateRequest) -> dict:
        """
        基于 Mifflin-St Jeor 公式计算 BMR 与 TDEE
        """
        # 1. 计算 BMR (基础代谢率)
        if req.gender.lower() == "male":
            bmr = 10 * req.weight + 6.25 * req.height - 5 * req.age + 5
        else:
            bmr = 10 * req.weight + 6.25 * req.height - 5 * req.age - 161

        # 2. 根据活动量计算 TDEE (每日总热量消耗)
        activity_multipliers = {
            "sedentary": 1.2,  # 久坐
            "light": 1.375,  # 轻度活动
            "moderate": 1.55,  # 中度活动
            "active": 1.725  # 高强度运动
        }
        multiplier = activity_multipliers.get(req.activity_level.lower(), 1.55)
        tdee = bmr * multiplier

        # 3. 计算减脂期每日建议摄入热量 (产生 300~500 kcal 热量赤字)
        target_calories = max(bmr, tdee - 400)

        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "target_calories": round(target_calories, 1)
        }

    async def generate_diet_plan_stream(self, req: DietGenerateRequest) -> AsyncGenerator[str, None]:
        """
        流式生成减脂餐食谱 (SSE 格式输出)

        核心优化：
        1. 跳过 LCEL 链路，直接调用 llm.astream()
        2. 行缓冲累积 + 流式 normalize
        3. 强制 flush 阈值 (80 字符)，避免一次性刷出整段
        4. normalize_markdown 兼容无 \\n 输出
        """
        t_start = time.time()
        # 1. 计算热量基线
        energy = self.calculate_energy_needs(req)

        # 2. 严格 Markdown 模板 System Prompt
        # 关键：用 \n 显式标注换行（prompt 里看不太清），并强调每个标签独立成行
        system_prompt = (
            "你是专业营养师。基于用户数据生成单日减脂餐食谱。\n"
            "\n"
            "【硬性格式规则 · 必须严格遵守】\n"
            "1. 每个 ## 标题必须独占一行，前面必须有【空行】\n"
            "2. 每个 - 列表项必须独占一行\n"
            "3. 单行字数 ≤ 30 字\n"
            "4. 总字数 ≤ 500 字\n"
            "\n"
            "【输出结构】\n"
            "## 👤 用户\n"
            "- 性别: <性别>\n"
            "- 年龄: <年龄> 岁\n"
            "- 身高: <身高> cm\n"
            "- 体重: <体重> kg\n"
            "- 活动: <活动>\n"
            "- BMR: <BMR> kcal\n"
            "- TDEE: <TDEE> kcal\n"
            "- 目标: <目标> kcal\n"
            "\n"
            "## 🍳 早餐（约 <X> kcal）\n"
            "- 菜名: ...\n"
            "- 食材: ...\n"
            "- 贴士: ...\n"
            "\n"
            "## 🥗 午餐（约 <X> kcal）\n"
            "- 菜名: ...\n"
            "- 食材: ...\n"
            "- 贴士: ...\n"
            "\n"
            "## 🍲 晚餐（约 <X> kcal）\n"
            "- 菜名: ...\n"
            "- 食材: ...\n"
            "- 贴士: ...\n"
            "\n"
            "## 📊 总计\n"
            "- 蛋白: ... g\n"
            "- 碳水: ... g\n"
            "- 脂肪: ... g\n"
            "\n"
            "【烹饪规则】\n"
            "- 早:午:晚 = 30% : 40% : 30%\n"
            "- 优先利用现有食材\n"
            "- 严格避开忌口\n"
        )

        ingredients_str = ", ".join(req.available_ingredients) if req.available_ingredients else "无限制"
        restrictions_str = ", ".join(req.dietary_restrictions) if req.dietary_restrictions else "无"

        human_prompt = (
            f"性别: {'男' if req.gender == 'male' else '女'} | "
            f"年龄: {req.age}岁 | 身高: {req.height}cm | 体重: {req.weight}kg | 活动: {req.activity_level}\n"
            f"目标减重: {req.target_weight_loss} kg\n"
            f"BMR: {energy['bmr']} | TDEE: {energy['tdee']} | 今日目标: {energy['target_calories']} kcal\n"
            f"现有食材: {ingredients_str}\n"
            f"忌口: {restrictions_str}"
        )

        # 3. 直接构造消息列表，跳过 LCEL 链路
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

        # 4. 立即推送空事件，确认 SSE 连接
        yield to_sse_data("")
        t_connected = time.time()
        print(f"[Timing] SSE握手完成耗时: {t_connected - t_start:.2f}s", flush=True)

        # 5. 异步流式调用 + 行缓冲 + 流式 normalize
        chunk_count = 0
        line_buffer = ''
        emitted_lines = ''  # 已发出内容（用于 normalize delta 计算）
        FLUSH_THRESHOLD = 80  # buffer 长度超过此值时强制 flush（避免一次性吐出整段）

        try:
            first_token = True
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    chunk_count += 1
                    if first_token:
                        t_first_token = time.time()
                        print(f"[Timing] DeepSeek TTFT (首token): {t_first_token - t_connected:.2f}s", flush=True)
                        first_token = False

                    line_buffer += chunk.content

                    # 触发 flush：出现 \n 或 buffer 长度超阈值
                    should_flush = '\n' in line_buffer or len(line_buffer) >= FLUSH_THRESHOLD
                    if should_flush:
                        if '\n' in line_buffer:
                            # 切分完整行，保留最后一段
                            parts = line_buffer.split('\n')
                            line_buffer = parts[-1]
                            flush_text = '\n'.join(parts[:-1]) + '\n'
                        else:
                            # 无 \n 但 buffer 过长，强制切一刀（保证流式体感）
                            flush_text = line_buffer
                            line_buffer = ''

                        # 后处理 + emit
                        combined = emitted_lines + flush_text
                        normalized = normalize_markdown(combined)
                        delta = normalized[len(emitted_lines):]
                        if delta:
                            yield to_sse_data(delta)
                        emitted_lines = normalized

            # 6. 流结束 flush 剩余 buffer
            if line_buffer:
                combined = emitted_lines + line_buffer
                normalized = normalize_markdown(combined)
                # 清理连续空行
                normalized = re.sub(r'\n{3,}', '\n\n', normalized)
                delta = normalized[len(emitted_lines):]
                if delta:
                    yield to_sse_data(delta)
                emitted_lines = normalized

            t_done = time.time()
            print(f"[Timing] 流式生成总耗时: {t_done - t_start:.2f}s, 总chunks: {chunk_count}", flush=True)
        except Exception as e:
            print(f"[Error] DeepSeek 调用异常: {repr(e)}", flush=True)
            yield to_sse_data(f"[Error: 生成食谱时发生异常: {str(e)}]")


# 实例化 Service 单例
diet_agent_service = DietAgentService()
