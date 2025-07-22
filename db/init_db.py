import sqlite3
import os

# 路径定义
DB_PATH = "memory/store/xiaoxing_memory.db"
SCHEMA_PATH = "memory/memory_schema.sql"

def init_db(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
        conn.executescript(schema)

    conn.commit()
    conn.close()
    print(f"✅ 数据库已成功创建：{db_path}")

if __name__ == "__main__":
    init_db()
