import json
import os


class Memory:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {
            "facts": {},
            "emotions": {}
        }
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data["facts"] = loaded.get("facts", {})
                    self.data["emotions"] = loaded.get("emotions", {})
            except Exception as e:
                print("[Memory Load Error]", e)

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("[Memory Save Error]", e)

    def remember(self, key, value):
        self.data["facts"][key] = value
        self.save()

    def recall(self, key):
        return self.data["facts"].get(key, "")

    def save_emotion(self, keyword, emotion):
        self.data["emotions"][keyword] = emotion
        self.save()

    def recall_emotion(self, keyword):
        return self.data["emotions"].get(keyword, "")

    def get_all_memory(self):
        return self.data["facts"]

    def get_all_emotions(self):
        return self.data["emotions"]
