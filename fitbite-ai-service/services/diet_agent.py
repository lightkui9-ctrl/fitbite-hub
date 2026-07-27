import asyncio
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config.config import settings
from schemas.diet import DietGenerateRequest


class DietAgentService:
    """
    减脂餐智能体服务层
    处理体征计算、Prompt 组装以及大模型流式推理
    """

    def __init__(self):
        # 初始化大模型客户端 (读取 config 中配置的 DeepSeek 密钥和端点)
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.MODEL_NAME,
            streaming=True,  # 开启流式输出
            temperature=0.7,
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
        """
        # 1. 计算热量基线
        energy = self.calculate_energy_needs(req)

        # 2. 组装 Prompt 模板
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """你是一名极其专业的注册营养师与减脂餐主厨。
你的任务是根据用户的体征数据、目标摄入热量、现有食材以及忌口要求，为用户量身定制一套科学、美味、接地气的单日减脂餐食谱。

请严格遵守以下定制规则：
1. 明确列出该用户的 BMR、TDEE 和【今日建议摄入总热量】。
2. 按照 早餐(30%) / 晚餐(30%) / 午餐(40%) 分配三大营养素（碳水化合物、蛋白质、脂肪）。
3. **优先且充分利用**用户现有的食材：{available_ingredients}。
4. **严格避开**用户的忌口/过敏源：{dietary_restrictions}。
5. 给出每餐的具体菜名、食材克数及预估热量，并附带一句简短的烹饪小贴士。
6. 排版要清晰漂亮，多用 Emoji，适合手机端阅读。"""),
            ("human", """请为我定制今天的减脂餐：
- 基本信息：{gender}, {age}岁, 身高{height}cm, 体重{weight}kg
- 活动强度：{activity_level}
- 减脂目标：减重 {target_weight_loss} kg
- 计算出的每日目标热量：{target_calories} kcal (BMR: {bmr} kcal, TDEE: {tdee} kcal)
- 现有食材：{available_ingredients}
- 忌口要求：{dietary_restrictions}
""")
        ])

        # 3. 填充 Prompt 参数
        prompt_input = {
            "gender": "男" if req.gender == "male" else "女",
            "age": req.age,
            "height": req.height,
            "weight": req.weight,
            "activity_level": req.activity_level,
            "target_weight_loss": req.target_weight_loss,
            "bmr": energy["bmr"],
            "tdee": energy["tdee"],
            "target_calories": energy["target_calories"],
            "available_ingredients": ", ".join(req.available_ingredients) if req.available_ingredients else "无限制",
            "dietary_restrictions": ", ".join(req.dietary_restrictions) if req.dietary_restrictions else "无"
        }

        chain = prompt_template | self.llm

        # 4. 异步流式调用大模型并按 SSE 格式 yield 输出
        try:
            async for chunk in chain.astream(prompt_input):
                if chunk.content:
                    # SSE 规范要求格式：data: <内容>\n\n
                    yield f"data: {chunk.content}\n\n"
                    await asyncio.sleep(0.01)  # 平滑打字机效果
        except Exception as e:
            yield f"data: [Error: 生成食谱时发生异常: {str(e)}]\n\n"


# 实例化 Service 单例
diet_agent_service = DietAgentService()