import os
import json
import logging
from functools import lru_cache
from config.config import EMOTION_WORDS_PATH

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@lru_cache(maxsize=1)
def load_emotion_words(path: str = None) -> dict:
    """
    加载情绪词汇字典（带缓存，默认使用配置路径）
    
    参数:
        path: 指定加载路径，可选。如果不传，则使用默认路径。
    
    返回:
        dict: 情绪分类词汇，如 {"positive": ["开心", "愉快"], "negative": ["生气", "难过"]}
    """
    actual_path = path or EMOTION_WORDS_PATH

    if not os.path.exists(actual_path):
        logger.warning(f"[情绪词配置文件不存在] {actual_path}")
        return {}

    try:
        with open(actual_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[读取情绪词配置失败] {actual_path} -> {e}")
        return {}

# 模块级默认变量（供其他模块引用）
EMOTION_WORDS = load_emotion_words()
