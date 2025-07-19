from emotion_words import EMOTION_WORDS
from datetime import datetime

# 全局情绪累积计分器（可扩展为数据库存储）
EMOTION_SCORE = {
    "positive": 0,
    "negative": 0,
    "neutral": 0
}

def detect_emotion(text):
    for category, words in EMOTION_WORDS.items():
        for word in words:
            if word in text:
                EMOTION_SCORE[category] += 1
                return category, word
    return None, None

def get_emotion_summary():
    return f"当前情绪累积：😊正向 {EMOTION_SCORE['positive']}，😟负向 {EMOTION_SCORE['negative']}，😐中性 {EMOTION_SCORE['neutral']}"

