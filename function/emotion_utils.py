from function.emotion_words import EMOTION_WORDS
from datetime import datetime

class EmotionTracker:
    def __init__(self):
        self.score = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }

    def detect_emotion(self, text: str) -> tuple[str | None, str | None]:
        for category, words in EMOTION_WORDS.items():
            for word in words:
                if word in text:
                    self.score[category] += 1
                    return category, word
        self.score["neutral"] += 1
        return "neutral", None

    def get_summary(self, use_emoji: bool = True) -> str:
        if use_emoji:
            return (
                f"当前情绪累积：😊正向 {self.score['positive']}，"
                f"😟负向 {self.score['negative']}，😐中性 {self.score['neutral']}"
            )
        else:
            return f"Emotion summary - Positive: {self.score['positive']}, Negative: {self.score['negative']}, Neutral: {self.score['neutral']}"

    def reset(self):
        for key in self.score:
            self.score[key] = 0
