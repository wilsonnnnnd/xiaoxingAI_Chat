from memory import Memory
from memory_tools import analyze_input, recall_input
from emotion_utils import detect_emotion, get_emotion_summary
from logger import append_to_log
import requests

MEMORY_PATH = "memory/store/memory_store.json"
memory = Memory(MEMORY_PATH)

API_URL = "http://127.0.0.1:8000/v1/completion"
HISTORY_LIMIT = 5  # 限制历史轮数（避免 prompt 太长）

# 多轮上下文历史
chat_history = []

# 构造带上下文的完整 prompt
def build_prompt(user_input: str) -> str:
    try:
        with open("E:/xiaoxing/prompt.txt", encoding="utf-8") as f:
            system_prompt = f.read()
    except:
        system_prompt = "你是一个温柔体贴的女生助手小星。"

    history_text = ""
    for entry in chat_history[-HISTORY_LIMIT:]:
        history_text += f"用户：{entry['user']}\n小星：{entry['bot']}\n"
    history_text += f"用户：{user_input}\n小星："

    return system_prompt.strip() + "\n" + history_text


# 向模型发送请求
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
            "stop": ["用户："]  # 关键停止点
        }, timeout=60)
        return response.json().get("content", "").strip()
    except Exception as e:
        return f"[小星 AI 接口出错]: {e}"


# 主聊天入口
def main():
    print("👧 小星上线啦～ 有什么想聊的吗？\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            break

        append_to_log("你", user_input)

        # 优先尝试关键词记忆
        response = analyze_input(user_input, memory)

        # 情绪分析
        emotion, keyword = detect_emotion(user_input)
        emotion_reply = ""
        if emotion == "positive":
            emotion_reply = f"听到你说“{keyword}”，我好开心呀～💕"
        elif emotion == "negative":
            emotion_reply = f"哎呀，你说“{keyword}”的时候，感觉你有点不高兴呢……要抱抱吗？🤗"
        elif emotion == "neutral":
            emotion_reply = f"嗯嗯，我知道了“{keyword}”，我会记在心里的～"

        # 若无关键词命中，则尝试记忆唤起 or 模型生成
        if not response:
            response = recall_input(user_input, memory)
        if not response:
            response = ask_llama_ai(user_input)
        if not response:
            response = "嘻嘻～我听着呢，还有别的想说的吗？"

        # 输出与记录
        final_reply = response + ("\n" + emotion_reply if emotion_reply else "")
        print("小星：" + final_reply.strip())
        append_to_log("小星", final_reply.strip())

        # 加入历史上下文
        chat_history.append({
            "user": user_input,
            "bot": response.strip()
        })

        # 情绪统计输出
        print("（情绪统计）" + get_emotion_summary())


if __name__ == "__main__":
    main()
