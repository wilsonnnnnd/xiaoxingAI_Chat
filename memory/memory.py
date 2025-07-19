import os
import json
from datetime import datetime

class Memory:
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

    def remember(self, key: str, value: str):
        self.data[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def recall(self, key: str) -> str:
        if key in self.data:
            return self.data[key]["value"]
        return "我还没有记住这个呢～"

    def recall_with_time(self, key: str) -> str:
        if key in self.data:
            value = self.data[key]["value"]
            iso_time = self.data[key]["timestamp"]
            try:
                dt = datetime.fromisoformat(iso_time)
                formatted_time = dt.strftime("%Y年%-m月%-d日 %H:%M:%S")
            except Exception:
                formatted_time = iso_time  # fallback
            return f"你的「{key}」是「{value}」，我是 {formatted_time} 记住的～"
        return "我还没有记住这个呢～"

    def forget(self, key: str) -> str:
        if key in self.data:
            del self.data[key]
            self._save()
            return "这个我已经忘记啦～"
        return "我本来就没有记住这个呢～"

    def forget_older_than(self, days: int) -> str:
        threshold = datetime.now().timestamp() - days * 86400
        forgotten = []
        for key in list(self.data.keys()):
            ts = datetime.fromisoformat(self.data[key]["timestamp"]).timestamp()
            if ts < threshold:
                del self.data[key]
                forgotten.append(key)
        if forgotten:
            self._save()
            return f"我忘记了这些{days}天前的记忆：{', '.join(forgotten)}"
        return f"{days}天内没有旧记忆需要忘记～"


    @property
    def memory_items(self):
        return self.data
