import sqlite3
from config.config import DB_PATH

def load_preference_rules() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT keyword, reply_template, category FROM preference_rules")
    rules = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    conn.close()
    return rules

def load_keyword_templates(db_path=DB_PATH) -> dict:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT type, keyword FROM preference_template")
    result = cursor.fetchall()
    conn.close()

    keywords = {"preference": [], "negative": [], "recall": []}
    for type_, keyword in result:
        if type_ in keywords:
            keywords[type_].append(keyword)
    return keywords