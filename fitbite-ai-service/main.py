import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.config import settings
from routers import diet
from services.diet_agent import init_diet_agent_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：建立本地 SQLite 检查点并构造 Agent 服务单例（持久化多轮记忆）
    await init_diet_agent_service()
    yield


# 创建 FastAPI 实例
app = FastAPI(
    title="FitBite 智膳 —— AI Agent 微服务",
    description="基于 FastAPI + LangChain/DeepSeek 的智能减脂餐与 RAG 膳食管理服务",
    version="1.0.0",
    lifespan=lifespan,
)

# 允许跨域请求 (为后续 Java 后端和 Vue 前端对接做准备)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(diet.router)

@app.get("/", summary="健康检查接口")
async def root():
    return {
        "status": "online",
        "service": "FitBite AI Service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # 启动 Uvicorn 服务器，监听配置中的端口 (8001)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )