import requests
from config.config import API_URL, HISTORY_LIMIT_FOR_SUMMARY
from function.summary.summary_db import SummaryDB
from datetime import datetime

try:
    from emotion_utils import detect_emotion
except ImportError:
    detect_emotion = None

def summarize_chat_history(chat_history: list[str], api_url: str = API_URL) -> str:
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
        try:
            return response.json().get("content", "").strip()
        except Exception as e:
            print("[解析失败]", e, response.text)
            return ""
    else:
        print("❌ 总结失败：", response.status_code, response.text)
        return ""

def summarize_and_store(chat_history: list[str]) -> str:
    summary = summarize_chat_history(chat_history)
    if not summary:
        return ""

    emotion = detect_emotion(summary) if detect_emotion else ""

    db = SummaryDB()
    db.save(summary=summary, emotion=emotion)
    db.close()

    return summary

def load_latest_summary() -> str:
    db = SummaryDB()
    latest = db.load_latest() or ""
    db.close()
    return latest
