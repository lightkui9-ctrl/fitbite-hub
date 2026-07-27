from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from schemas.diet import DietGenerateRequest
from services.diet_agent import diet_agent_service

router = APIRouter(
    prefix="/api/v1/diet",
    tags=["减脂餐 AI 智能体"]
)

@router.post("/generate", summary="流式生成个性化减脂餐食谱 (SSE)")
async def generate_diet_plan(request: DietGenerateRequest):
    """
    根据用户输入的体征数据、食材和忌口，
    调用 DeepSeek / LangChain 流式推送定制化的减脂餐食谱。
    """
    return StreamingResponse(
        diet_agent_service.generate_diet_plan_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 防止 Nginx 缓存流式数据
        }
    )