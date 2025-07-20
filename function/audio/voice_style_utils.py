import json
import os
from functools import lru_cache
from config.config import SPEECH_STYLE_PATH

@lru_cache(maxsize=1)
def load_speech_config(path: str = SPEECH_STYLE_PATH) -> dict:
    if not os.path.exists(path):
        print(f"[语音情绪配置缺失] {path}")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                raise ValueError("配置文件内容应为 dict")
            return config
    except Exception as e:
        print(f"[❌ 加载语音配置失败] {e}")
        return {}

SPEECH_CONFIG_MAP = load_speech_config()

def get_speech_config_by_emotion(emotion: str) -> dict:
    """
    根据情绪返回语音合成的配置，包括 style, voice, rate, volume 等。
    若未匹配情绪或配置缺失，回退使用 '_default'。
    """
    if not emotion:
        emotion = ""
    emotion_key = emotion.strip().lower()
    config = SPEECH_CONFIG_MAP.get(emotion_key) or SPEECH_CONFIG_MAP.get("_default", {})

    if not config:
        print(f"[⚠️ 找不到语音配置] 情绪: '{emotion}'，请检查配置文件")

    return config