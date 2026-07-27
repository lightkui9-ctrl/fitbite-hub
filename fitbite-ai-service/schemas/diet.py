from pydantic import BaseModel, Field
from typing import List, Optional


class DietGenerateRequest(BaseModel):
    """
    减脂餐生成接口请求体 Schema (契约定义)
    """
    gender: str = Field(..., description="性别: male 或 female", example="male")
    age: int = Field(..., ge=1, le=120, description="年龄", example=25)
    height: float = Field(..., gt=0, description="身高 (cm)", example=175.0)
    weight: float = Field(..., gt=0, description="当前体重 (kg)", example=75.0)

    activity_level: str = Field(
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
                "dietary_restrictions": ["海鲜"]
            }
        }