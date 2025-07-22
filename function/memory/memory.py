# memory/memory.py
from datetime import datetime
import sqlite3
import json
from typing import List, Optional

from pydantic_core import to_json
from config.config import DB_PATH

class Memory:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def add(self, chat_log_id: int, keyword: str, value: str,
            topic: Optional[str] = None,
            tags: Optional[List[str]] = None,
            source: Optional[str] = None):
        print(f"[DEBUG] memory.add() 参数: {chat_log_id=}, {keyword=}, {value=}, {topic=}, {source=}")
        tags_json = to_json(tags) if tags else None
        try:
            self.conn.execute("""
                INSERT INTO memory (chat_log_id, keyword, value, topic, tags, source, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (chat_log_id, keyword, value, topic, tags_json, source))
            self.conn.commit()
            print(f"[🧠 记忆] 写入成功：{keyword} = {value}")
        except Exception as e:
            print("[❌ memory.insert 出错]", e)



    def save_emotion(self, keyword: str, emotion: str):
        """
        将情绪关键词和对应情绪保存到 emotions 表。
        """
        try:
            self.conn.execute('''
                INSERT INTO emotions (keyword, emotion, timestamp)
                VALUES (?, ?, ?)
            ''', (keyword, emotion, datetime.now().isoformat()))
            self.conn.commit()
            print(f"[🧠 记忆] 已保存关键词情绪：'{keyword}' -> {emotion}")
        except Exception as e:
            print("[❌ 记忆错误] 无法保存情绪信息：", e)


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
