import requests
import json
import os
from datetime import datetime
from config.config import SUMMARY_LOG_PATH,API_URL,HISTORY_LIMIT_FOR_SUMMARY


def summarize_chat_history(chat_history: list[str], api_url: str = API_URL) -> str:
    """
    使用本地模型压缩聊天历史为摘要
    """
    if len(chat_history) < HISTORY_LIMIT_FOR_SUMMARY:
        return ""

    prompt = (
        "请总结以下用户与AI的对话，提炼出关键的情绪变化、兴趣偏好、重要事件或人际关系信息。\n\n"
        + "\n".join(chat_history)
        + "\n\n总结："
    )

    response = requests.post(api_url, json={
        "prompt": prompt,
        "n_predict": 256,
        "temperature": 0.6,
        "top_k": 40,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "stop": ["用户："]
    })

    if response.status_code == 200:
        content = response.json().get("content", "").strip()
        return content
    else:
        print("❌ 总结失败：", response.status_code, response.text)
        return ""

def save_summary_to_log(summary: str, emotion: str = ""):
    """
    将总结写入 summary_log.json，并附带时间戳与情绪标签
    """
    if not summary:
        return

    entry = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "emotion": emotion or ""
    }

    if os.path.exists(SUMMARY_LOG_PATH):
        with open(SUMMARY_LOG_PATH, "r", encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = []

    log.append(entry)

    with open(SUMMARY_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def load_latest_summary() -> str:
    """
    读取最新一条摘要，用于嵌入系统提示
    """
    if not os.path.exists(SUMMARY_LOG_PATH):
        return ""
    with open(SUMMARY_LOG_PATH, "r", encoding="utf-8") as f:
        log = json.load(f)
    if not log:
        return ""
    return log[-1]["summary"]

# 可选：集成情绪检测模块（如果已存在）
try:
    from emotion_utils import detect_emotion
except ImportError:
    detect_emotion = None

def summarize_and_store(chat_history: list[str]):
    """
    主调用入口：总结并保存摘要和情绪
    """
    summary = summarize_chat_history(chat_history)
    if not summary:
        return ""

    emotion = ""
    if detect_emotion:
        emotion = detect_emotion(summary)

    save_summary_to_log(summary, emotion)
    return summary
