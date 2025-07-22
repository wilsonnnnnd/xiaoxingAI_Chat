# function/emotion/emotion_dict_db.py
import sqlite3
from collections import defaultdict
from config.config import DB_PATH

class EmotionDictionaryDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def load_emotion_words(self) -> dict:
        """
        加载数据库中的情绪词汇，结构为：
        { "positive": [...], "negative": [...], "neutral": [...] }
        """
        cursor = self.conn.execute("SELECT word, category FROM emotion_dictionary")
        result = defaultdict(list)
        for row in cursor:
            result[row["category"]].append(row["word"])
        return dict(result)

    def close(self):
        self.conn.close()
