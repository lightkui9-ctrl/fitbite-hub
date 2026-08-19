from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from schemas.diet import DietGenerateRequest
from services import diet_agent
from services.conversation_store import get_history

router = APIRouter(
    prefix="/api/v1/diet",
    tags=["减脂餐 AI 智能体"]
)


@router.post("/generate", summary="流式生成 / 多轮追问 个性化减脂餐 (SSE)")
async def generate_diet_plan(request: DietGenerateRequest):
    """
    根据用户输入的体征数据、食材和忌口，调用 DeepSeek / LangGraph Agent
    流式推送定制化的减脂餐食谱。

    - 首次：传 gender/age/height/weight 等体征字段
    - 追问：传 message + session_id，Agent 自动复用历史记忆（持久化）
    - Agent 会按需调用工具（食物热量查询/热量计算/食材替换）
    - 每轮「用户提问」与「AI 回答」都会落盘到本地存储，供前端展示与重载
    """
    svc = diet_agent.diet_agent_service
    user_display = svc._build_user_display(
        request if request.message is None else None,
        request.message,
    )
    return StreamingResponse(
        svc.generate_diet_plan_stream(
            req=request if request.message is None else None,
            message=request.message,
            session_id=request.session_id or "default",
            user_display=user_display,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 防止 Nginx 缓存流式数据
        }
    )


@router.get("/session/history", summary="获取会话历史（用户提问 + AI 回答）")
async def session_history(session_id: str = "default"):
    """
    返回某会话的完整对话历史，供前端刷新/重开后恢复聊天记录。
    返回结构：{"session_id": "...", "turns": [{"role": "user"|"assistant", "content": "...", "ts": "..."}]}
    """
    return {
        "session_id": session_id,
        "turns": get_history(session_id),
    }


@router.post("/session/clear", summary="清空指定会话的记忆与本地存储")
async def clear_session(session_id: str = "default"):
    """
    清空指定 session_id 的 Agent 记忆（持久化检查点）+ 本地对话文件，
    用于「重新开始」按钮。
    """
    await diet_agent.diet_agent_service.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}
