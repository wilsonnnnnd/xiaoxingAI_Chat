import os
import json
import re
from datetime import datetime
from memory.memory_parser import extract_memory
from memory.emotion_words import EMOTION_WORDS

# 文件路径设置
MEMORY_FILE = "E:/xiaoxing/memory/store/memory_store.json"
LOG_FILE = "E:/xiaoxing/memory/logs/chat_history.log"

# 确保目录存在
os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# 初始化记忆文件
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# 记忆模块类
class Memory:
    def __init__(self, path):
        self.path = path
        self.data = self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def remember(self, key, value):
        self.data[key] = value
        self.save()

    def recall(self, key):
        return self.data.get(key, "我还没有记住这个呢～")

    def forget(self, key):
        if key in self.data:
            del self.data[key]
            self.save()
            return "好的，这个我已经忘掉啦～"
        return "我本来就没有记住这个呢～"

# 写入日志函数
def append_to_log(role, content):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {role}：{content}\n")

# 创建记忆实例
memory = Memory(MEMORY_FILE)

# 自动提取并记忆
def analyze_input(user_input: str):
    extracted = extract_memory(user_input)
    if extracted:
        responses = []
        for key, value in extracted:
            memory.remember(key, value)
            responses.append(f"嗯嗯～我记住了，你的「{key}」是「{value}」噢～")
        return "\n".join(responses)
    return None

# 记忆回忆
def recall_input(user_input: str):
    for key in memory.data.keys():
        if key in user_input:
            value = memory.recall(key)
            return f"当然记得呀～你告诉我你的「{key}」是「{value}」噢～"
    return None

# 情绪识别
def detect_emotion(text):
    for word in EMOTION_WORDS["positive"]:
        if word in text:
            return "positive", word
    for word in EMOTION_WORDS["negative"]:
        if word in text:
            return "negative", word
    for word in EMOTION_WORDS["neutral"]:
        if word in text:
            return "neutral", word
    return None, None

# 主聊天流程
def main_chat():
    print("👧 小星上线啦～ 有什么想聊的吗？\n")
    chat_history = []

    while True:
        user_input = input("你：").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            break

        append_to_log("你", user_input)
        chat_history.append({"role": "user", "content": user_input})

        # 自动记忆和情绪
        response = analyze_input(user_input)
        emotion, keyword = detect_emotion(user_input)
        ai_reply = ""

        if emotion == "positive":
            ai_reply = f"听到你说“{keyword}”，我好开心呀～💕"
        elif emotion == "negative":
            ai_reply = f"哎呀，你说“{keyword}”的时候，感觉你有点不高兴呢……要抱抱吗？🤗"
        elif emotion == "neutral":
            ai_reply = f"嗯嗯，我知道了“{keyword}”，我会记在心里的～"
        elif response:
            ai_reply = response
        else:
            recall = recall_input(user_input)
            ai_reply = recall if recall else "嘻嘻～我听着呢，还有别的想说的吗？"

        print("小星：" + ai_reply)
        append_to_log("小星", ai_reply)
        chat_history.append({"role": "assistant", "content": ai_reply})

if __name__ == "__main__":
    main_chat()
