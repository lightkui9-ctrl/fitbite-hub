# FitBite 智膳 —— 基于 AI Agent 的个性化减脂餐与健康管理系统

## 📖 项目简介
FitBite 智膳是一款结合 Java 传统业务管理与 Python AI 智能体（Agent）微服务的健康饮食管理平台。系统解决传统减肥人群"算热量繁琐、食谱不接地气、缺乏动态追踪"的痛点，提供基于个人体征与现有食材的智能减脂餐定制、基于 MySQL 多对多关系的菜品食材检索库以及每日热量账本管理。

---

## 🏗️ 系统架构

项目采用前后端分离与异构微服务架构：

- **前端 (Vue 3 + Element Plus + Tailwind CSS)**：负责 UI 交互、SSE 打字机打字效果、热量账本数据展示。
- **业务主后端 (Java Spring Boot 3.0.2)**：负责用户档案、每日热量打卡持久化（MySQL/Redis）、`WebClient` 以 DataBuffer 原始字节流式透传 Python AI 响应及 Knife4j 接口文档。
- **AI 微服务 (Python FastAPI)**：负责 LangGraph Agent 推理、RAG 知识库检索、流式（SSE）响应输出。

## 🏗️ 全栈工程目录结构 (Architecture & Directory Tree)

系统采用单仓库多服务 (Monorepo) 架构，包含三大独立运行的子工程：

```text
fitbite-hub/                           # 【主项目根目录】
├── fitbite-ai-service/                # 1. Python AI 微服务 (FastAPI)
│   ├── config/                        # 系统配置 (读取 .env、日志等)
│   │   └── config.py
│   ├── routers/                       # API 路由层 (定义 REST/SSE 接口)
│   │   └── diet.py
│   ├── schemas/                       # 数据契约层 (Pydantic 请求/响应模型)
│   │   └── diet.py
│   ├── services/                      # 核心 AI & Agent 业务逻辑层 (LangGraph/RAG)
│   │   └── diet_agent.py
│   ├── main.py                        # FastAPI 启动入口
│   ├── requirements.txt               # Python 依赖清单
│   ├── .env.example                   # 环境变量模板
│   └── .env                           # 环境变量 (需自行配置)
│
├── fitbite-backend-service/           # 2. Java 业务主后端 (Spring Boot 3.0.2)
│   ├── src/
│   │   └── main/
│   │       ├── java/com/fitbite/
│   │       │   ├── config/            # 配置类 (Redis, WebClient, Knife4j)
│   │       │   ├── controller/        # 业务路由层 (透传 AI 服务, 菜品食材检索, 打卡账本)
│   │       │   ├── domain/            # 数据模型层
│   │       │   │   ├── dto/           # 数据传输对象 (DietGenerateDTO, DietRecordDTO, UserSaveDTO)
│   │       │   │   ├── entity/        # 数据库实体 (SysUser, DietRecord, Dish, Ingredient)
│   │       │   │   └── vo/            # 视图对象 (DailyCalorieSummaryVO)
│   │       │   ├── mapper/            # DAO 层 (MyBatis-Plus 动态 SQL / 多对多 JOIN)
│   │       │   └── service/           # 业务逻辑层 (用户档案, 热量打卡账本, AI 透传)
│   │       └── resources/             # 配置文件 (application.yml)
│   ├── pom.xml                        # Maven 依赖管理
│   └── README.md
│
├── fitbite-frontend/                  # 3. Web 前端项目 (Vue 3 + Vite + TS)
│   ├── src/
│   │   ├── api/                       # HTTP / SSE 请求封装 (diet.ts)
│   │   ├── assets/                    # 静态资源 (图片、样式)
│   │   ├── components/                # 业务组件 (DietGenerator, DietDashboard, DishLibrary)
│   │   ├── App.vue                    # 主框架与 Tab 导航页签
│   │   ├── main.ts                    # 前端入口
│   │   └── style.css                  # 全局样式
│   ├── package.json                   # 前端依赖配置
│   └── README.md
│
├── package.json                       # 根项目依赖
├── package-lock.json                  # npm 锁定文件
└── README.md                          # 全栈项目总说明文档
```

## 🛠️ 技术选型与基线版本

- **Frontend**: Vue 3.5.39, Vite 8.1.1, TypeScript 6.0.2, Element Plus 2.14.3, Tailwind CSS 4.3.3, Pinia 4.0.2, Axios 1.19.0, Marked 18.0.9

- **Backend (Java)**: JDK 17, Spring Boot 3.0.2, MyBatis-Plus 3.5.5, WebClient (Spring WebFlux), MySQL 8.0+, Redis 7.0+, Knife4j 4.1.0, Lombok

- **AI Service (Python)**: Python 3.11+, FastAPI 0.110~0.112, Uvicorn, Pydantic 2.6+, LangChain 0.3+, LangGraph 0.2+, ChromaDB 0.4.24+, DeepSeek-V3/R1

---

## 🚀 本地启动指南

### 前置条件

- JDK 17+, Maven 3.8+
- Python 3.11+, pip
- Node.js 20+, npm
- MySQL 8.0, Redis 7.0

### 启动步骤

**1. AI 微服务（端口 8001）**

```bash
cd fitbite-ai-service
cp .env.example .env          # 编辑 .env，填入 OPENAI_API_KEY 等
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**2. 业务后端（端口 8080）**

```bash
cd fitbite-backend-service
mvn spring-boot:run
```

**3. Web 前端（端口 5173）**

```bash
cd fitbite-frontend
npm install && npm run dev
```

### 关键环境变量（.env）

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI / 兼容 API 密钥 | `sk-xxx` |
| `OPENAI_BASE_URL` | API 端点地址 | `https://api.deepseek.com/v1` |
| `MODEL_NAME` | LLM 模型名称 | `deepseek-v4-pro` |
| `PORT` | AI 服务监听端口 | `8001` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `CHROMA_PERSIST_DIR` | ChromaDB 向量库持久化路径 | `./chroma_data` |
