import json
import os
from functools import lru_cache
from config.config import STOP_WORDS_PATH

@lru_cache(maxsize=1)
def load_stop_words(path: str = None) -> set:
    """
    加载停用词列表（默认从配置路径）
    """
    actual_path = path or STOP_WORDS_PATH
    if not os.path.exists(actual_path):
        print(f"[⚠️ 停用词文件不存在] {actual_path}")
        return set()
    try:
        with open(actual_path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception as e:
        print(f"[❌ 加载停用词失败] {e}")
        return set()

STOP_WORDS = load_stop_words()
