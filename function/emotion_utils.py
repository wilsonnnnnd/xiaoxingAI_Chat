import re
from function.emotion_words import load_emotion_words

class EmotionTracker:
    def __init__(self):
        self.emotion_count = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        self.latest_keyword = None
        self.emotion_words = load_emotion_words()  # 使用缓存加载词典

    def detect_emotion(self, text: str):
        """
        根据情绪词判断文本情绪类别
        返回 (emotion, keyword)，若无匹配则为 ("neutral", None)
        """
        for category, words in self.emotion_words.items():
            for word in words:
                if word in text:
                    self.emotion_count[category] += 1
                    self.latest_keyword = word
                    return category, word
        self.emotion_count["neutral"] += 1
        return "neutral", None

    def get_summary(self) -> str:
        """
        返回实时情绪统计摘要字符串
        """
        return (
            f"🧠 情绪统计 ｜ 正面：{self.emotion_count['positive']} ｜ "
            f"负面：{self.emotion_count['negative']} ｜ 中性：{self.emotion_count['neutral']}"
        )

    def reset(self):
        """
        重置统计计数
        """
        self.emotion_count = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        self.latest_keyword = None
