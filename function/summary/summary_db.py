import sqlite3
from datetime import datetime
from typing import Optional, List
from config.config import DB_PATH

class SummaryDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def save(self, summary: str, emotion: str = "", emotion_chart: str = "", wordcloud_keywords: str = "", tags: str = ""):
        date = datetime.now().strftime("%Y-%m-%d")
        self.conn.execute("""
            INSERT OR REPLACE INTO daily_summary (date, summary, emotion_chart, wordcloud_keywords, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (date, summary, emotion_chart, wordcloud_keywords, tags))
        self.conn.commit()

    def load_all(self) -> List[dict]:
        cursor = self.conn.execute("SELECT * FROM daily_summary ORDER BY date DESC")
        return [dict(row) for row in cursor.fetchall()]

    def load_latest(self) -> Optional[str]:
        cursor = self.conn.execute("SELECT summary FROM daily_summary ORDER BY date DESC LIMIT 1")
        row = cursor.fetchone()
        return row["summary"] if row else None

    def close(self):
        self.conn.close()
