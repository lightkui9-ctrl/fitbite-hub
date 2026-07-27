import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    全局配置类，基于 Pydantic-Settings 自动读取环境变量或 .env 文件
    """
    # LLM 相关配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    MODEL_NAME: str = "gpt-4o-mini"

    # 服务运行配置
    PORT: int = 8001
    LOG_LEVEL: str = "INFO"

    # 向量数据库路径
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # 指定配置配置文件来源
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# 实例化全局配置对象，供后续模块导入使用
settings = Settings()