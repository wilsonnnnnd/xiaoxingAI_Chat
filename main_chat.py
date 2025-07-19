import asyncio
import requests
from config.config_paths import PROMPT_PATH
from function.chat_logger import log_conversation
from function.emotion_utils import EmotionTracker
from function.speech_utils import speak
from memory.memory_tools import analyze_input, recall_input
from memory.memory import Memory
from function.voice_style_utils import get_speech_config_by_emotion


MEMORY_PATH = "memory/store/memory_store.json"
API_URL = "http://127.0.0.1:8000/v1/completions"
HISTORY_LIMIT = 5  # 限制上下文轮数

memory = Memory(MEMORY_PATH)
emotion_tracker = EmotionTracker()
chat_history = []


def build_prompt(user_input: str) -> str:
    try:
        with open(PROMPT_PATH, encoding="utf-8") as f:
            system_prompt = f.read()
    except:
        system_prompt = ""

    history_text = "".join(
        f"用户：{entry['user']}\n小星：{entry['bot']}\n" for entry in chat_history[-HISTORY_LIMIT:]
    )
    return system_prompt.strip() + "\n" + history_text + f"用户：{user_input}\n小星："


def ask_llama_ai(user_input: str) -> str:
    prompt = build_prompt(user_input)
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
        print("[小星 AI 接口出错]", e)
        return ""


async def main():
    print("小星已启动。")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            break

        response = analyze_input(user_input, memory)

        # 情绪识别与记忆
        emotion, keyword = emotion_tracker.detect_emotion(user_input)
        if keyword:
            memory.save_emotion(keyword, emotion)

        if not emotion:
            emotion = "neutral"

        if not response:
            response = recall_input(user_input, memory)
        if not response:
            response = ask_llama_ai(user_input)

        final_reply = response
        print("小星：" + final_reply.strip())

        # 日志记录
        log_conversation(user_input, final_reply.strip(), extra_fields={
            "emotion": emotion,
            "keyword": keyword or ""
        })

        # 情绪驱动语音配置
        speech_config = get_speech_config_by_emotion(emotion)
        try:
            await speak(
                final_reply.strip(),
                voice=speech_config["voice"],
                style=speech_config["style"],
                rate=speech_config["rate"],
                volume=speech_config["volume"]
            )
        except Exception as e:
            print("[语音合成出错]", e)

        # 更新上下文历史
        chat_history.append({
            "user": user_input,
            "bot": response.strip()
        })

        # 打印情绪统计
        print(emotion_tracker.get_summary())


if __name__ == "__main__":
    asyncio.run(main())
