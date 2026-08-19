from pydantic import BaseModel, Field
from typing import List, Optional


class DietGenerateRequest(BaseModel):
    """
    减脂餐生成接口请求体 Schema (契约定义)

    支持两种调用模式：
    1. 首次生成（结构化）：传入 gender/age/height/weight 等体征字段
    2. 多轮追问（自然语言）：传入 message + session_id，复用历史记忆
    """
    # —— 首次生成所需体征字段（多轮追问时可选）——
    gender: Optional[str] = Field(default=None, description="性别: male 或 female", example="male")
    age: Optional[int] = Field(default=None, ge=1, le=120, description="年龄", example=25)
    height: Optional[float] = Field(default=None, gt=0, description="身高 (cm)", example=175.0)
    weight: Optional[float] = Field(default=None, gt=0, description="当前体重 (kg)", example=75.0)

    activity_level: Optional[str] = Field(
        default="moderate",
        description="日常活动量: sedentary(久坐), light(轻度), moderate(中度), active(高强度)",
        example="moderate"
    )

    target_weight_loss: Optional[float] = Field(
        default=5.0,
        description="期望减重目标 (kg)",
        example=5.0
    )

    available_ingredients: List[str] = Field(
        default=[],
        description="家里现有的食材列表",
        example=["鸡胸肉", "西兰花", "紫薯", "鸡蛋"]
    )

    dietary_restrictions: List[str] = Field(
        default=[],
        description="饮食忌口或过敏源",
        example=["海鲜", "辣"]
    )

    # —— 多轮对话 / Agent 字段 ——
    message: Optional[str] = Field(
        default=None,
        description="多轮追问的自然语言消息。传入时直接使用，并复用 session 历史",
        example="把早餐换成更低脂的方案"
    )

    session_id: Optional[str] = Field(
        default="default",
        description="会话 ID，用于多轮记忆隔离。前端每次会话生成唯一值",
        example="sess-abc123"
    )

    # 为 FastAPI /docs 接口文档提供完整请求样例
    class Config:
        json_schema_extra = {
            "example": {
                "gender": "male",
                "age": 25,
                "height": 175.0,
                "weight": 75.0,
                "activity_level": "moderate",
                "target_weight_loss": 5.0,
                "available_ingredients": ["鸡胸肉", "西兰花", "紫薯", "鸡蛋"],
                "dietary_restrictions": ["海鲜"],
                "message": None,
                "session_id": "sess-abc123"
            }
        }
