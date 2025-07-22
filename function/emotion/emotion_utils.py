import sqlite3
from datetime import datetime
from collections import Counter

DB_PATH = "xiaoxing_memory.db"  # 可全局配置或从 config 导入

# 情绪分析工具类


class EmotionTracker:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.summary = []

    def detect_emotion(self, text: str) -> tuple[str, str]:
        """
        从 text 中找出第一个命中的情绪词，并返回 (emotion, keyword)
        如果没有命中，则返回 ("neutral", "")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT word, emotion FROM emotion_dictionary")
            rows = cursor.fetchall()
            conn.close()

            for word, emotion in rows:
                if word in text:
                    self.summary.append(emotion)
                    print(f"[💡 情绪识别] '{word}' → {emotion}")
                    return emotion, word

        except Exception as e:
            print("[❌ 情绪识别错误]", e)

        self.summary.append("neutral")
        return "neutral", ""

    def get_summary(self) -> dict:
        """
        获取当前对话的情绪分布统计
        """
        return dict(Counter(self.summary))


# 保存关键词情绪到 emotions 表（偏好记忆）
def save_emotion_keyword(keyword: str, emotion: str, db_path: str = DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emotions (keyword, emotion, timestamp)
            VALUES (?, ?, ?)
        ''', (keyword, emotion, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"[🧠 记忆] 已保存关键词情绪：'{keyword}' -> {emotion}")
    except Exception as e:
        print("[❌ 记忆错误] 无法保存情绪信息：", e)


# 写入整句情绪分析日志（emotion_log 表）
def log_emotion_analysis(content: str, emotion: str, db_path: str = DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emotion_log (content, emotion, timestamp)
            VALUES (?, ?, ?)
        ''', (content, emotion, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"[📥 情绪日志] 已记录：'{content}' → {emotion}")
    except Exception as e:
        print("[❌ 日志错误] emotion_log 写入失败：", e)
