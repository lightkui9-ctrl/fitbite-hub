"""
本地对话存储（持久化）

把每一轮「用户提问」与「AI 回答」落盘到本地 JSON 文件：
- 路径：data/sessions/{session_id}.json
- 结构：{"turns": [{"role": "user"|"assistant", "content": "...", "ts": "..."}]}

用途：
1. 前端刷新/重开后能恢复完整聊天记录（用户提问 + AI 回答都展示）
2. 作为本地持久化存储，满足「用户提问和模型回答都应保存」的需求
3. 与 Agent 的 LangGraph 检查点（SQLite）互相独立，互不干扰
"""
import os
import re
import json
import threading
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

_lock = threading.Lock()


def _ensure_dir():
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def _safe_name(session_id: str) -> str:
    # 防止路径穿越 / 非法文件名
    return re.sub(r'[^A-Za-z0-9_\-]', '_', str(session_id))[:120]


def _path(session_id: str) -> str:
    return os.path.join(SESSIONS_DIR, f"{_safe_name(session_id)}.json")


def append_turn(session_id: str, role: str, content: str) -> None:
    """追加一条对话（user 或 assistant）到本地存储"""
    _ensure_dir()
    p = _path(session_id)
    with _lock:
        data = {"turns": []}
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {"turns": []}
        data.setdefault("turns", []).append({
            "role": role,
            "content": content,
            "ts": datetime.now().isoformat(timespec="seconds"),
        })
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_history(session_id: str) -> list:
    """读取某会话的完整对话历史，供前端恢复展示"""
    p = _path(session_id)
    if not os.path.exists(p):
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("turns", [])
    except Exception:
        return []


def clear(session_id: str) -> None:
    """删除某会话的本地对话文件"""
    p = _path(session_id)
    with _lock:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
