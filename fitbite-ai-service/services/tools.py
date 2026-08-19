"""
减脂餐 Agent 的工具集 (Function Calling / Tool Use)

这些工具会被 LangGraph Agent 在推理过程中自主调用：
- 查食物热量：从本地营养知识库检索某食材的热量与宏量营养素
- 计算 BMR/TDEE：基于用户体征计算基础代谢与每日总消耗
- 推荐替代食材：给出更低热量的健康替代方案

注意：工具数据均为本地内置字典，无需外部 API，保证 demo 可独立运行。
"""

from langchain_core.tools import tool


# ===== 内置营养知识库（常见食材，每 100g 数据）=====
# 字段: 热量(kcal), 蛋白质(g), 碳水(g), 脂肪(g)
FOOD_NUTRITION_DB = {
    "鸡胸肉": (133, 19.4, 2.5, 5.0),
    "西兰花": (34, 2.8, 7.0, 0.4),
    "鸡蛋": (144, 13.3, 2.8, 8.8),
    "牛肉": (250, 26.0, 0.0, 15.0),
    "三文鱼": (208, 20.0, 0.0, 13.0),
    "米饭": (116, 2.6, 25.9, 0.3),
    "糙米": (112, 2.6, 23.0, 0.9),
    "全麦面包": (247, 13.0, 41.0, 3.4),
    "紫薯": (82, 1.6, 20.0, 0.1),
    "红薯": (99, 1.1, 24.0, 0.2),
    "土豆": (77, 2.0, 17.0, 0.1),
    "燕麦": (338, 15.0, 66.0, 7.0),
    "牛奶": (54, 3.4, 5.0, 3.2),
    "酸奶": (72, 2.5, 9.3, 2.7),
    "豆腐": (81, 8.1, 4.2, 3.7),
    "虾": (99, 24.0, 0.2, 0.3),
    "金枪鱼": (132, 28.0, 0.0, 1.0),
    "菠菜": (23, 2.9, 3.6, 0.4),
    "胡萝卜": (39, 0.9, 9.6, 0.2),
    "番茄": (18, 0.9, 3.9, 0.2),
    "牛油果": (160, 2.0, 9.0, 15.0),
    "杏仁": (579, 21.0, 22.0, 50.0),
    "香蕉": (89, 1.1, 23.0, 0.3),
    "苹果": (52, 0.3, 14.0, 0.2),
}


@tool
def get_food_calorie(food_name: str) -> str:
    """
    查询某种食材每 100g 的热量与宏量营养素（蛋白质/碳水/脂肪）。
    当用户询问某食物热量、营养，或 Agent 需要精确计算某道菜热量时使用。
    参数 food_name 为食材中文名，如 '鸡胸肉'、'米饭'。
    """
    data = FOOD_NUTRITION_DB.get(food_name.strip())
    if not data:
        # 返回未收录提示，让 Agent 自行估算
        return f"知识库暂未收录「{food_name}」的精确热量数据，请基于常识估算，并明确标注为估算值。"
    kcal, protein, carbs, fat = data
    return (
        f"{food_name} (每100g): 热量 {kcal} kcal | "
        f"蛋白质 {protein}g | 碳水 {carbs}g | 脂肪 {fat}g"
    )


@tool
def calculate_bmr_tdee(
    gender: str, age: int, height: float, weight: float, activity_level: str = "moderate"
) -> str:
    """
    基于 Mifflin-St Jeor 公式计算用户的基础代谢率(BMR)与每日总消耗(TDEE)，
    并给出减脂期每日建议摄入热量(目标热量)。
    当用户提供了体征数据并需要精确热量基线时调用。
    参数:
      gender: 'male' 或 'female'
      age: 年龄(岁)
      height: 身高(cm)
      weight: 体重(kg)
      activity_level: sedentary/light/moderate/active
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
    }
    multiplier = multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier
    target = max(bmr, tdee - 400)

    return (
        f"BMR={round(bmr,1)} kcal | TDEE={round(tdee,1)} kcal | "
        f"减脂目标摄入={round(target,1)} kcal"
    )


@tool
def suggest_ingredient_swap(ingredient: str, goal: str = "low_calorie") -> str:
    """
    为某食材推荐更健康/更低热量的替代方案。
    当用户希望替换高热量食材、或需要对现有食材做健康升级时调用。
    参数:
      ingredient: 需要被替换的食材名，如 '米饭'
      goal: 替换目标，默认 'low_calorie'(低热量)
    """
    swaps = {
        "米饭": "糙米 / 藜麦 / 花椰菜米（热量更低且升糖更慢）",
        "面条": "魔芋面 / 荞麦面 / 全麦意面",
        "牛肉": "鸡胸肉 / 火鸡胸 / 鱼类（脂肪含量更低）",
        "猪肉": "鸡胸肉 / 虾仁（低脂高蛋白）",
        "全脂牛奶": "脱脂牛奶 / 无糖豆浆",
        "黄油": "橄榄油（少量）/ 牛油果泥",
        "薯条": "烤红薯 / 烤土豆块（无油烘烤）",
        "白糖": "赤藓糖醇 / 少量蜂蜜",
        "面包": "全麦面包 / 黑麦面包",
    }
    suggestion = swaps.get(ingredient.strip())
    if not suggestion:
        return f"暂未预设「{ingredient}」的替代方案，建议选择同类型中热量更低、加工程度更低的天然食材。"
    return f"「{ingredient}」的{goal}替代建议: {suggestion}"


# 工具列表，供 Agent 绑定
ALL_TOOLS = [get_food_calorie, calculate_bmr_tdee, suggest_ingredient_swap]
