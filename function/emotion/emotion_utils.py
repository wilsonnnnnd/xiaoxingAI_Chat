from function.emotion.emotion_dict_db import EmotionDictionaryDB

class EmotionTracker:
    def __init__(self):
        self.emotion_count = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        self.latest_keyword = None

        db = EmotionDictionaryDB()
        self.emotion_words = db.load_emotion_words()
        db.close()

    def detect_emotion(self, text: str):
        found_keywords = {"positive": [], "negative": [], "neutral": []}

        for category, words in self.emotion_words.items():
            for word in words:
                if word in text:
                    found_keywords[category].append(word)

        for category in found_keywords:
            self.emotion_count[category] += len(found_keywords[category])

        dominant = max(found_keywords.items(), key=lambda x: len(x[1]))
        dominant_emotion = dominant[0] if dominant[1] else "neutral"
        self.latest_keyword = dominant[1][0] if dominant[1] else None
        return dominant_emotion, self.latest_keyword

    def get_summary(self) -> str:
        return (
            f"🧠 情绪统计 ｜ 正面：{self.emotion_count['positive']} ｜ "
            f"负面：{self.emotion_count['negative']} ｜ 中性：{self.emotion_count['neutral']}"
        )

    def reset(self):
        self.emotion_count = {"positive": 0, "negative": 0, "neutral": 0}
        self.latest_keyword = None
