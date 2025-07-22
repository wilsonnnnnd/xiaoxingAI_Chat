import sqlite3
from datetime import datetime
from config.config import DB_PATH

def log_speech_to_db(text: str, path: str, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO speech_log (text, path, timestamp)
        VALUES (?, ?, ?)
    """, (text, path, datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()
