import sqlite3
from config.config import DB_PATH


class SpeechConfigDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_config_by_emotion(self, emotion: str) -> dict:
        cursor = self.conn.execute("""
            SELECT * FROM speech_config
            WHERE emotion = ? OR emotion = '_default'
            ORDER BY CASE WHEN emotion = ? THEN 0 ELSE 1 END
            LIMIT 1
        """, (emotion, '_default'))
        row = cursor.fetchone()
        return dict(row) if row else {}

    def close(self):
        self.conn.close()


# ✅ 推荐使用的导出函数，供主程序使用
def get_speech_config(emotion: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT style, voice, rate, volume
        FROM speech_config
        WHERE emotion = ? OR emotion = '_default'
        ORDER BY CASE WHEN emotion = ? THEN 0 ELSE 1 END
        LIMIT 1
    """, (emotion, emotion))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}
