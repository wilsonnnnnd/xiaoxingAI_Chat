import sqlite3
import os
import pathlib
import sys

# Ensure the repository root is on sys.path so `from config.config import DB_PATH` works
# whether this script is executed from the repo root or from the db/ folder.
repo_root = pathlib.Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from config.config import DB_PATH

# 使用仓库中的 schema_output.sql，且默认 DB 路径从 config 读取，保证一致性
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_output.sql")


def init_db(db_path: str = DB_PATH, schema_path: str = SCHEMA_PATH):
    """安全初始化数据库：
    - 使用 config 中的 DB_PATH（默认）
    - 读取 db/schema_output.sql，按语句逐一执行
    - 已存在的表会被忽略（不会覆盖已有数据）
    """
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if not os.path.exists(schema_path):
        print(f"[❌] schema 文件未找到: {schema_path}")
        return

    conn = sqlite3.connect(db_path)
    created = 0
    skipped = 0

    # 尝试多种编码读取 schema 文件，兼容带 BOM 或本地编码的文件
    sql = None
    last_exc = None
    for enc in ("utf-8-sig", "utf-8", "utf-16", "gbk", "latin-1"):
        try:
            with open(schema_path, "r", encoding=enc) as f:
                sql = f.read()
            break
        except Exception as e:
            last_exc = e
            continue
    if sql is None:
        print(f"[❌] 无法读取 schema 文件 ({schema_path})，尝试的编码均失败")
        raise last_exc

    # 按分号分割语句并逐条执行，已存在的表将被忽略
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        try:
            conn.execute(stmt)
            created += 1
        except sqlite3.OperationalError as e:
            # 常见: table already exists -> 忽略
            skipped += 1
        except Exception as e:
            print(f"[❌] 执行 schema 语句出错: {e}")

    conn.commit()
    conn.close()

    print(f"✅ 数据库初始化完成：{db_path}（已执行语句: {created}，跳过: {skipped}）")


if __name__ == "__main__":
    init_db()
