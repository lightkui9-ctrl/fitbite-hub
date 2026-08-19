import os
import re
import json
import time
import asyncio
from typing import AsyncGenerator, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    BaseMessage,
)
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
from config.config import settings
from schemas.diet import DietGenerateRequest
from services.tools import ALL_TOOLS
from services.conversation_store import append_turn, get_history, clear as clear_store

# 持久化检查点数据库（LangGraph 多轮记忆落盘，重启不丢）
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "agent_checkpoints.db",
)


def normalize_markdown(text: str) -> str:
    """
    后处理 Markdown 输出：补齐章节/列表项的换行，修复 AI 漏写的换行
    关键能力：即使 AI 输出完全没有 \n，也能强制在 ## 标题与 - 列表项前插入换行
    """
    if not text:
        return text

    # ===== 第 0 步：确保 '##' 后紧跟空格（Markdown 规范要求，
    #           否则 '##标题' 不会被渲染成标题，只会显示成普通文字）=====
    text = re.sub(r'##(?=[^\s\n#])', r'## ', text)

    # ===== 第 1 步：处理完全没有 \n 的情况（最关键的修复）=====
    text = re.sub(r'([^\n])## ', r'\1\n\n## ', text)
    text = re.sub(r'([^\n])- ', r'\1\n- ', text)

    # ===== 第 1 步：补充 \n 后的空行 =====
    text = re.sub(r'([^\n])\n(## )', r'\1\n\n\2', text)
    text = re.sub(r'(## [^\n]+)\n(?!\n|-)', r'\1\n\n', text)

    # ===== 第 2 步：清理 3+ 连续换行 =====
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def to_sse_data(content: str) -> str:
    """将多行 content 格式化为合法的 SSE 多行 data 事件"""
    if not content:
        return "data: \n\n"
    lines = content.split('\n')
    return ''.join(f'data: {line}\n' for line in lines) + '\n'


def to_sse_comment(comment: str) -> str:
    """
    生成 SSE 注释行 (以 ':' 开头)。
    前端 SSE 解析器只处理以 'data:' 开头的行，注释行会被自动忽略，
    因此可用它向客户端透传「工具调用状态」而不污染最终 Markdown 正文。
    """
    return f": {comment}\n\n"


# ============================================================
# Agent 的系统 Prompt —— 之前这坨代码没传给 create_react_agent，
# 导致 Agent 一直在用默认 prompt，多轮后必然跑偏。现在真正生效。
# ============================================================
SYSTEM_PROMPT = (
    "你是「FitBite 智膳」的专业营养师 AI Agent，负责为用户生成与调整减脂餐方案，"
    "并回答膳食相关的提问。\n\n"
    "【你拥有的工具】\n"
    "- calculate_bmr_tdee：根据性别/年龄/身高/体重/活动量计算 BMR、TDEE 与减脂目标摄入\n"
    "- get_food_calorie：查询指定食物每 100g 的热量与三大营养素\n"
    "- suggest_ingredient_swap：给出某食材的低卡 / 健康替代建议\n\n"
    "【铁律 · 必须严格遵守】\n"
    "1. 禁止输出任何解释、寒暄、推理过程，或『让我查询』之类的话。\n"
    "2. 禁止 Markdown 表格（不要用 | 和 ---），所有数据一律用 - 列表项。\n"
    "3. 调用工具时只输出工具调用，不得附带任何文字说明。\n\n"
    "【生成 / 调整食谱时】必须输出完整 Markdown 食谱，且正文第一个标题必须是 "
    "'## 👤 用户'，其前不得有任何文字。结构严格如下：\n"
    "## 👤 用户\n"
    "- 性别: <性别>\n- 年龄: <年龄> 岁\n- 身高: <身高> cm\n"
    "- 体重: <体重> kg\n- 活动: <活动>\n- BMR: <BMR> kcal\n"
    "- TDEE: <TDEE> kcal\n- 目标: <目标> kcal\n"
    "## 🍳 早餐（约 <X> kcal）\n- 菜名: ...\n- 食材: ...\n- 贴士: ...\n"
    "## 🥗 午餐（约 <X> kcal）\n- 菜名: ...\n- 食材: ...\n- 贴士: ...\n"
    "## 🍲 晚餐（约 <X> kcal）\n- 菜名: ...\n- 食材: ...\n- 贴士: ...\n"
    "## 📊 总计\n- 蛋白: ... g\n- 碳水: ... g\n- 脂肪: ... g\n"
    "格式规则：\n"
    "- 每个 ## 标题独占一行，前后以空行分隔\n"
    "- 每个 - 列表项独占一行\n"
    "- 单行 ≤ 30 字\n"
    "- 工具返回的真实数据必须被使用，不得编造数字\n"
    "- 当用户要求『修改某餐 / 替换食材 / 换个方案』时，必须输出【完整】的更新后食谱"
    "（含全部餐次），而非仅被修改的部分\n\n"
    "【纯问答时】当用户只是提问（如『鸡胸肉热量多少』『为什么选糙米』），"
    "用简洁中文直接回答，可附简短 Markdown 列表，无需完整食谱框架。"
)


# ============================================================
# 第二阶段「格式化 LLM」的系统提示：把 Agent 收集/生成的方案
# 整理为干净 Markdown 食谱（修复模型偶发的格式瑕疵，如缺 '- ' 前缀、
# 标题缺空格等）。仅对「食谱类」回答（含 ##）启用；纯问答不套用。
# ============================================================
FORMATTER_SYSTEM = (
    "你是减脂餐排版助手。下面是一份由营养师 Agent 生成的减脂餐方案"
    "（可能夹杂少量寒暄或解释文字，或 Markdown 格式略有瑕疵）。\n"
    "请将其【严格整理】为干净的 Markdown 食谱并输出，要求：\n"
    "1. 第一个标题必须是 '## 👤 用户'，其后列出：性别 / 年龄 / 身高 / 体重 / 活动 / BMR / TDEE / 目标\n"
    "2. 之后依次：'## 🍳 早餐'、'## 🥗 午餐'、'## 🍲 晚餐'、'## 📊 总计'，每餐含 菜名 / 食材 / 贴士\n"
    "3. 禁止任何寒暄、解释、推理过程，直接输出食谱正文\n"
    "4. 禁止 Markdown 表格，所有数据一律用 - 列表项（每个列表项以 '- ' 开头，独占一行）\n"
    "5. 每个 ## 标题独占一行，其后必须紧跟换行\n"
    "6. 若用户只是提问（草稿本身不是食谱），则直接整理为简洁回答，无需强行套用食谱框架\n"
)


class DietAgentService:
    """
    减脂餐智能体服务层

    核心能力：
    1. LangGraph ReAct Agent —— 自主决定调用工具（食物热量/热量计算/食材替换）
    2. AsyncSqliteSaver 持久化多轮记忆 —— 同一 session_id 下可连续追问，
       且记忆落盘到本地 SQLite，Python 服务重启后依然保留
    3. SSE 流式输出 —— 工具状态以注释实时推送，最终回答以打字机效果逐字输出
    """

    def __init__(self, checkpointer, conn):
        self.checkpointer = checkpointer
        self._conn = conn

        # 初始化大模型客户端（绑定 tools，开启流式）—— 供 Agent 使用
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.MODEL_NAME,
            streaming=True,
            temperature=0.3,
            max_tokens=2048,
        ).bind_tools(ALL_TOOLS)

        # 格式化专用 LLM（不绑定 tools）：仅做 Markdown 整理，
        # 避免模型在整理时误触发工具调用导致输出为空
        self.formatter_llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.MODEL_NAME,
            streaming=True,
            temperature=0.2,
            max_tokens=1500,
        )

        # 构建 LangGraph ReAct Agent（system_prompt 真正传入，带持久化检查点）
        self.agent = create_react_agent(
            model=self.llm,
            tools=ALL_TOOLS,
            prompt=SYSTEM_PROMPT,
            checkpointer=self.checkpointer,
        )

    @classmethod
    async def create(cls, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = await aiosqlite.connect(db_path)
        checkpointer = AsyncSqliteSaver(conn)
        return cls(checkpointer, conn)

    async def close(self):
        try:
            await self._conn.close()
        except Exception:
            pass

    @staticmethod
    def calculate_energy_needs(req: DietGenerateRequest) -> dict:
        if req.gender.lower() == "male":
            bmr = 10 * req.weight + 6.25 * req.height - 5 * req.age + 5
        else:
            bmr = 10 * req.weight + 6.25 * req.height - 5 * req.age - 161
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
        }
        multiplier = activity_multipliers.get(req.activity_level.lower(), 1.55)
        tdee = bmr * multiplier
        target_calories = max(bmr, tdee - 400)
        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "target_calories": round(target_calories, 1),
        }

    def _build_human_prompt(self, req: DietGenerateRequest) -> str:
        """首次生成：把结构化体征拼成自然语言指令"""
        energy = self.calculate_energy_needs(req)
        ingredients_str = ", ".join(req.available_ingredients) if req.available_ingredients else "无限制"
        restrictions_str = ", ".join(req.dietary_restrictions) if req.dietary_restrictions else "无"
        return (
            f"请为我定制一日减脂餐。\n"
            f"性别: {'男' if req.gender == 'male' else '女'} | 年龄: {req.age}岁 | "
            f"身高: {req.height}cm | 体重: {req.weight}kg | 活动: {req.activity_level}\n"
            f"目标减重: {req.target_weight_loss} kg\n"
            f"BMR: {energy['bmr']} | TDEE: {energy['tdee']} | 今日目标: {energy['target_calories']} kcal\n"
            f"现有食材: {ingredients_str}\n"
            f"忌口: {restrictions_str}"
        )

    def _build_user_display(self, req: Optional[DietGenerateRequest], message: Optional[str]) -> str:
        """构造一个可读的「用户提问」文本，存入本地对话记录用于 UI 展示"""
        if message:
            return message
        if req:
            return (
                f"生成减脂餐方案（"
                f"{'男' if req.gender == 'male' else '女'} / {req.age}岁 / "
                f"{req.height}cm / {req.weight}kg / 活动:{req.activity_level}）"
            )
        return "（空请求）"

    async def _stream_answer(self, text: str) -> AsyncGenerator[str, None]:
        """
        把最终回答以打字机效果逐字推送给前端：
        - 按小块累加，每累加一次就重新 normalize 整段并只发送增量（delta）
        - 这样既保留正确换行，又避免把上一轮的 chitchat 带出来
        """
        emitted = ""
        full = ""
        chars = list(text)
        i = 0
        step = 4  # 每块约 4 个字符，模拟流式
        while i < len(chars):
            full += "".join(chars[i:i + step])
            i += step
            norm = normalize_markdown(full)
            norm = re.sub(r'\n{3,}', '\n\n', norm)
            delta = norm[len(emitted):]
            emitted = norm
            if delta:
                yield to_sse_data(delta)
            await asyncio.sleep(0.012)

    async def generate_diet_plan_stream(
        self,
        req: Optional[DietGenerateRequest] = None,
        message: Optional[str] = None,
        session_id: str = "default",
        user_display: str = "",
    ) -> AsyncGenerator[str, None]:
        """
        流式生成减脂餐 / 多轮追问 (SSE 格式)。

        流程：
        1. 运行 LangGraph Agent（带持久化记忆）：工具调用过程以 SSE 注释实时推送
        2. 取 Agent 最终回答，以打字机效果逐字推送
        3. 把「用户提问」与「AI 回答」落盘到本地对话存储（供 UI 展示与重载）
        """
        t_start = time.time()

        # 1. 确定本轮用户输入
        if message:
            user_input = message
        elif req:
            user_input = self._build_human_prompt(req)
        else:
            yield to_sse_data("[Error: 缺少请求参数]")
            return

        # 2. 立即推送空事件，确认 SSE 连接
        yield to_sse_data("")
        t_connected = time.time()
        print(f"[Timing] SSE握手完成耗时: {t_connected - t_start:.2f}s", flush=True)

        config = {"configurable": {"thread_id": session_id}}
        is_first_gen = bool(req) and not message

        try:
            # ===== 阶段一：运行 Agent，实时展示工具调用（注释推送）=====
            async for event in self.agent.astream_events(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                version="v2",
            ):
                kind = event.get("event")

                if kind == "on_tool_start":
                    tool_name = event["name"]
                    args = event.get("data", {}).get("input", {})
                    arg_str = json.dumps(args, ensure_ascii=False)[:80]
                    yield to_sse_comment(f"🔧 正在调用工具 {tool_name} {arg_str}")

                elif kind == "on_tool_end":
                    output = str(event.get("data", {}).get("output", ""))[:120]
                    yield to_sse_comment(f"✅ 工具返回: {output}")

            # 阶段一结束后，从持久化检查点取出 Agent 的最终回答
            # 注意：检查点是 AsyncSqliteSaver（异步），必须用 aget_state，
            # 否则会报 "Synchronous calls to AsyncSqliteSaver are only allowed from a different thread"
            state = await self.agent.aget_state(config)
            messages = state.values.get("messages", []) if state and state.values else []
            final_ai = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
            answer = ""
            if final_ai:
                c = final_ai.content
                answer = c if isinstance(c, str) else " ".join(str(x) for x in c)

            if not answer.strip():
                answer = "（未能生成有效回答，请重试或调整提问）"

            print(f"[Timing] Agent 阶段完成，最终回答长度={len(answer)}", flush=True)

            # ===== 阶段二：整理并推送最终回答 =====
            # 食谱类回答（含 ##）：用 formatter 二次整理为干净 Markdown，
            #   首轮额外带上 Python 算好的热量基线，保证数据完整、格式严谨；
            #   追问若也是食谱（如"换个低脂早餐"），同样整理为完整更新后食谱。
            # 纯问答（无 ##）：直接把 Agent 回答打字机式推送，避免强行套食谱框架。
            final_text = ""
            if "##" in answer:
                if is_first_gen and req:
                    energy = self.calculate_energy_needs(req)
                    fmt_input = (
                        f"用户体征：性别{'男' if req.gender == 'male' else '女'}，"
                        f"年龄{req.age}岁，身高{req.height}cm，体重{req.weight}kg，"
                        f"活动水平{req.activity_level}\n"
                        f"计算所得：BMR={energy['bmr']} kcal，TDEE={energy['tdee']} kcal，"
                        f"减脂目标摄入={energy['target_calories']} kcal\n"
                        f"现有食材：{', '.join(req.available_ingredients) or '无限制'}\n"
                        f"忌口：{', '.join(req.dietary_restrictions) or '无'}\n\n"
                        f"以下为 Agent 生成的方案草稿，请严格整理为食谱：\n{answer.strip()}"
                    )
                else:
                    fmt_input = answer.strip()

                buffer = ""
                started = False
                async for chunk in self.formatter_llm.astream([
                    SystemMessage(content=FORMATTER_SYSTEM),
                    HumanMessage(content=fmt_input),
                ]):
                    c = getattr(chunk, "content", None)
                    if not c:
                        continue
                    buffer += c
                    if not started:
                        idx = buffer.find("##")
                        if idx == -1:
                            # 首轮：等首个 ## 标题出现再推送（丢弃极短前言）
                            continue
                        started = True
                        text_from = buffer[idx:]
                        norm = re.sub(r'\n{3,}', '\n\n', normalize_markdown(text_from))
                        final_text = norm
                        yield to_sse_data(norm)
                    else:
                        norm = re.sub(r'\n{3,}', '\n\n', normalize_markdown(buffer))
                        delta = norm[len(final_text):]
                        final_text = norm
                        if delta:
                            yield to_sse_data(delta)
            else:
                # 纯问答：直接打字机式推送 Agent 回答
                final_text = answer
                async for sse in self._stream_answer(answer):
                    yield sse

            # ===== 阶段三：落盘对话（用户提问 + AI 回答）=====
            append_turn(session_id, "user", user_display or user_input)
            append_turn(session_id, "assistant", final_text)

            t_done = time.time()
            print(f"[Timing] 流式生成总耗时: {t_done - t_start:.2f}s", flush=True)

        except Exception as e:
            print(f"[Error] Agent 调用异常: {repr(e)}", flush=True)
            yield to_sse_data(f"[Error: 生成食谱时发生异常: {str(e)}]")

    # —— 记忆管理（供接口调用）——
    async def clear_session(self, session_id: str):
        """清空某 session 的 Agent 记忆（检查点）+ 本地对话文件"""
        try:
            await self.checkpointer.delete_thread(session_id)
        except Exception:
            pass
        clear_store(session_id)


# 单例（在应用启动时通过 init_diet_agent_service 异步创建）
diet_agent_service = None


async def init_diet_agent_service():
    """应用启动时调用：建立本地 SQLite 检查点并构造 Agent 服务单例"""
    global diet_agent_service
    diet_agent_service = await DietAgentService.create()
    return diet_agent_service
