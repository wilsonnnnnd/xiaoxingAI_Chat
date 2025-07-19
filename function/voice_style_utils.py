import json
import os
from config.config_paths import SPEECH_STYLE_PATH

def load_speech_config(path: str = SPEECH_STYLE_PATH) -> dict:
    if not os.path.exists(path):
        print(f"[语音情绪配置缺失] {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SPEECH_CONFIG_MAP = load_speech_config()

def get_speech_config_by_emotion(emotion: str) -> dict:
    """
    根据情绪返回语音合成的配置，包括 style, voice, rate, volume 等
    """
    emotion = emotion.lower() if emotion else ""
    return SPEECH_CONFIG_MAP.get(emotion, SPEECH_CONFIG_MAP.get("_default", {}))
