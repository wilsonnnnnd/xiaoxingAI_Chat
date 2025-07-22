
import sqlite3
from config.config import DB_PATH

def load_stopwords(db_path=DB_PATH) -> set:
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT word FROM stopwords")
    words = {row[0] for row in cursor.fetchall()}
    conn.close()
    return words

# 可直接引用
STOP_WORDS = load_stopwords()
