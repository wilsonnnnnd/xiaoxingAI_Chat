from memory import Memory
from memory_tools import analyze_input, recall_input
from emotion_utils import detect_emotion
from logger import append_to_log

memory = Memory("memory/store/memory_store.json")

def main():
    print("👧 小星上线啦～ 有什么想聊的吗？\n")
    while True:
        user_input = input("你：").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            break

        append_to_log("你", user_input)
        response = analyze_input(user_input)
        emotion, keyword = detect_emotion(user_input)

        if emotion == "positive":
            emotion_reply = f"听到你说“{keyword}”，我好开心呀～💕"
        elif emotion == "negative":
            emotion_reply = f"哎呀，你说“{keyword}”的时候，感觉你有点不高兴呢……要抱抱吗？🤗"
        elif emotion == "neutral":
            emotion_reply = f"嗯嗯，我知道了“{keyword}”，我会记在心里的～"
        else:
            emotion_reply = ""

        if not response:
            response = recall_input(user_input) or "嘻嘻～我听着呢，还有别的想说的吗？"

        final_reply = response + "\n" + emotion_reply if emotion_reply else response
        print("小星：" + final_reply.strip())
        append_to_log("小星", final_reply.strip())

if __name__ == "__main__":
    main()
