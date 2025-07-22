# memory/memory.py
import sqlite3
import json
from typing import List, Optional
from config.config import DB_PATH

class Memory:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def add(self, chat_log_id: int, keyword: str, value: str,
            topic: Optional[str] = None,
            tags: Optional[List[str]] = None,
            source: Optional[str] = None):
        tags_json = json.dumps(tags) if tags else None
        self.conn.execute("""
            INSERT OR IGNORE INTO memory (chat_log_id, keyword, value, topic, tags, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_log_id, keyword, value, topic, tags_json, source))
        self.conn.commit()

    def recall(self, keyword: str) -> List[dict]:
        cursor = self.conn.execute("""
            SELECT keyword, value, topic, tags, source, created_at
            FROM memory
            WHERE keyword = ? AND is_deleted = 0
            ORDER BY created_at DESC
        """, (keyword,))
        return [dict(row) for row in cursor.fetchall()]

    def recall_latest(self, keyword: str) -> Optional[str]:
        facts = self.recall(keyword)
        if facts:
            return facts[0]["value"]
        return None

    def forget(self, keyword: str):
        self.conn.execute("""
            UPDATE memory SET is_deleted = 1 WHERE keyword = ?
        """, (keyword,))
        self.conn.commit()

    def close(self):
        self.conn.close()
