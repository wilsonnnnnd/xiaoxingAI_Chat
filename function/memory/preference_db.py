import sqlite3
from config.config import DB_PATH

def load_preference_rules() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT keyword, reply_template, category FROM preference_rules")
    rules = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    conn.close()
    return rules

def load_preference_templates() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT pattern FROM preference_template")
    templates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return templates
