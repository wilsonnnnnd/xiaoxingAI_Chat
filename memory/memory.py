import os
import json
from datetime import datetime


class Memory:
    EMOTION_KEY = "emotion_memory"

    DEFAULT_NOT_FOUND = "（未找到相关记忆）"
    DEFAULT_FORGOT = "（该记忆已删除）"
    DEFAULT_EMPTY = "（没有符合条件的旧记忆）"

    def __init__(self, path: str):
        self.path = path
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _format_time(self, iso_str: str) -> str:
        try:
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime("%Y年%m月%d日 %H:%M:%S")
        except Exception:
            return iso_str  # fallback

    def remember(self, key: str, value: str):
        self.data[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def recall(self, key: str) -> str:
        return self.data.get(key, {}).get("value", self.DEFAULT_NOT_FOUND)

    def recall_with_time(self, key: str) -> str:
        if key in self.data:
            value = self.data[key]["value"]
            time_str = self._format_time(self.data[key]["timestamp"])
            return f"{key}：{value}（记录时间：{time_str}）"
        return self.DEFAULT_NOT_FOUND

    def forget(self, key: str) -> str:
        if key in self.data:
            del self.data[key]
            self._save()
            return self.DEFAULT_FORGOT
        return self.DEFAULT_NOT_FOUND

    def forget_older_than(self, days: int) -> str:
        threshold = datetime.now().timestamp() - days * 86400
        forgotten = []
        for key in list(self.data.keys()):
            ts = datetime.fromisoformat(
                self.data[key]["timestamp"]).timestamp()
            if ts < threshold:
                del self.data[key]
                forgotten.append(key)
        if forgotten:
            self._save()
            return f"已清除 {days} 天前的记忆：{', '.join(forgotten)}"
        return self.DEFAULT_EMPTY

    def save_emotion(self, keyword: str, emotion: str):
        if self.EMOTION_KEY not in self.data:
            self.data[self.EMOTION_KEY] = {}
        self.data[self.EMOTION_KEY][keyword] = {
            "emotion": emotion,
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def recall_emotion(self, keyword: str) -> str:
        if self.EMOTION_KEY in self.data and keyword in self.data[self.EMOTION_KEY]:
            return self.data[self.EMOTION_KEY][keyword]["emotion"]
        return ""

    @property
    def memory_items(self):
        return self.data
