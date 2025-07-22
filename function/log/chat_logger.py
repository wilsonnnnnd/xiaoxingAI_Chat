import sqlite3
import json
from datetime import datetime
from typing import Optional, List
from config.config import DB_PATH

class ChatLogger:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def log(self, role: str, content: str,
            topic: Optional[str] = None,
            tags: Optional[List[str]] = None,
            context_version: int = 1,
            is_deleted: int = 0) -> int:
        """
        记录一条对话到 chat_log 表，并返回其 chat_log_id
        """
        tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
        self.conn.execute("""
            INSERT INTO chat_log (role, content, topic, tags, context_version, is_deleted, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            role,
            content,
            topic,
            tags_json,
            context_version,
            is_deleted,
            datetime.now().isoformat(timespec="seconds")
        ))
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def close(self):
        self.conn.close()



# 添加全局函数，便于主流程调用
def log_conversation(user_text: str, bot_text: str, extra_fields: dict = None):
    logger = ChatLogger()
    tags = [f"{extra_fields.get('emotion')}", f"{extra_fields.get('keyword')}"] if extra_fields else None
    logger.log(
        role="user", content=user_text, tags=tags, topic="Chat"
    )
    logger.log(
        role="bot", content=bot_text, tags=tags, topic="Chat"
    )
    logger.close()
