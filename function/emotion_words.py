import os
import json
from config.config_paths import EMOTION_WORDS_PATH

def load_emotion_words(path: str = EMOTION_WORDS_PATH) -> dict:
    if not os.path.exists(path):
        print(f"[情绪词配置文件不存在] {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

EMOTION_WORDS = load_emotion_words()
