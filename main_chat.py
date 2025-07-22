import tiktoken
import asyncio
import requests
import time
from typing import List, Dict

from config.config import (
    API_URL, HISTORY_LIMIT, MAX_HISTORY, MAX_HISTORY_ROUNDS, MAX_SUMMARY_TOKENS, PROMPT_PATH
)
from function.log.chat_logger import log_conversation
from function.emotion.emotion_utils import EmotionTracker, log_emotion_analysis
from function.audio.speech_utils import speak
from function.memory.memory_tools import analyze_input, recall_input
from function.memory.memory import Memory
from function.summary.summary_manager import load_latest_summary, summarize_and_store
from function.audio.speech_config_db import get_speech_config
from function.summary.scheduler_manager import (
    start_summary_scheduler_thread,
    start_speech_report_scheduler_thread
)

# 初始化模块实例
memory = Memory()
emotion_tracker = EmotionTracker()
chat_history = []


def truncate_text_by_tokens(text: str, max_tokens: int) -> str:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens]) + "..."


def build_prompt(
    user_input: str,
    system_prompt: str = "",
    history: List[Dict[str, str]] = [],
    summary: str = ""
) -> str:
    summary_text = ""
    if summary:
        summary = truncate_text_by_tokens(summary, MAX_SUMMARY_TOKENS)
        summary_text = f"\n📝 最近的对话总结（小星偷偷记下来的）～：\n{summary}\n"

    trimmed_history = history[-MAX_HISTORY_ROUNDS:]
    history_text = "".join(
        f"用户：{entry['user']}\n小星：{entry['bot']}\n" for entry in trimmed_history
    )

    return (
        system_prompt.strip()
        + summary_text
        + "\n🌟 下面是我们刚刚的对话记录：\n"
        + history_text
        + f"用户：{user_input}\n小星："
    )


def ask_llama_ai(user_input: str, summary: str = "") -> str:
    try:
        with open(PROMPT_PATH, encoding="utf-8") as f:
            system_prompt = f.read()
    except Exception as e:
        print("[⚠️ 加载系统提示失败]", e)
        system_prompt = ""

    prompt = build_prompt(user_input, system_prompt,
                          chat_history[-HISTORY_LIMIT:], summary)

    try:
        response = requests.post(API_URL, json={
            "prompt": prompt,
            "n_predict": 256,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "stop": ["用户："]
        }, timeout=60)

        result = response.json()
        return result.get("content", result.get("choices", [{}])[0].get("text", "")).strip()

    except Exception as e:
        print("[❌ 小星 AI 接口出错]", e)
        return "我好像没连上大脑…请稍后再试一次。"


async def main():
    start_summary_scheduler_thread(chat_history)
    start_speech_report_scheduler_thread()

    print("\n🌟 小星已启动，开始陪你聊天啦～")
    summary = load_latest_summary()

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("👋 小星下线了，再见～")
            break

        if any(kw in user_input.lower() for kw in ["总结", "概括", "刚刚聊了什么"]):
            summary = summarize_and_store(chat_history)
            print("\n🧠 小星（总结）：", summary)
            continue

        # ✅ 优先尝试记忆逻辑
        response = analyze_input(user_input, memory)

        # ✅ 情绪识别 + 写入关键词情绪 + 情绪日志
        emotion, keyword = emotion_tracker.detect_emotion(user_input)

        if keyword:
            memory.save_emotion(keyword, emotion)

        log_emotion_analysis(user_input, emotion)

        if not emotion:
            emotion = "neutral"

        # ✅ 回忆逻辑
        if not response:
            response = recall_input(user_input, memory)

        # ✅ AI 回应
        if not response:
            start_time = time.time()
            response = ask_llama_ai(user_input, summary)
            end_time = time.time()
            print(f"[⏱️ 回复耗时] {(end_time - start_time):.2f} 秒")

        final_reply = response.strip()
        print("小星：" + final_reply)

        # ✅ 记录对话日志（含情绪）
        log_conversation(user_input, final_reply, extra_fields={
            "emotion": emotion,
            "keyword": keyword or ""
        })

        # ✅ 情绪驱动语音播放
        try:
            speech_config = get_speech_config(emotion)
            await speak(
                final_reply,
                voice=speech_config.get("voice"),
                style=speech_config.get("style"),
                rate=speech_config.get("rate"),
                volume=speech_config.get("volume")
            )
        except Exception as e:
            print("[❌ 语音合成出错]", e)

        # ✅ 更新历史
        chat_history.append({"user": user_input, "bot": final_reply})
        if len(chat_history) > MAX_HISTORY:
            chat_history.pop(0)

        # ✅ 输出当前对话的情绪统计
        print(emotion_tracker.get_summary())


if __name__ == "__main__":
    asyncio.run(main())
