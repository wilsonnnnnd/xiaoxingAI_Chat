# 功能文档：记忆存取层（function/memory/memory.py）

概述
-----
`function/memory/memory.py` 提供基于 SQLite 的记忆管理封装，包含写入结构化记忆、保存关键词情绪、检索（回忆）与删除（忘记）等基本操作。

类与方法
---------
- `class Memory`（构造器：`Memory(db_path=DB_PATH)`）
  - `add(chat_log_id: int, keyword: str, value: str, topic: Optional[str]=None, tags: Optional[List[str]]=None, source: Optional[str]=None)`
    - 写入 `memory` 表（字段包含 chat_log_id, keyword, value, topic, tags（JSON）, source, is_deleted），commit 后无返回值。
  - `save_emotion(keyword: str, emotion: str)`
    - 写入 `emotions` 表（带 timestamp）。
  - `recall(keyword: str) -> List[dict]`
    - 返回 keyword 匹配且未删除的记忆条目列表（包含 `keyword, value, topic, tags, source, created_at` 等字段）。
  - `recall_latest(keyword: str) -> Optional[str]`
    - 返回最新一条匹配的 value 或 None。
  - `forget(keyword: str)`
    - 将匹配项的 `is_deleted` 标记为 1。
  - `close()`
    - 关闭 DB 连接。

数据库依赖
-----------
- 默认 DB 路径通过 `config/config.py` 的 `DB_PATH` 提供。该类直接使用 sqlite3 执行 SQL 语句，假定存在 `memory` 与 `emotions` 等相关表。

错误处理
---------
- `add` 与 `save_emotion` 均在捕获异常后打印错误信息，但不会向调用方抛出。调用者应注意确认写入成功或检查日志以判断异常。

已知限制/注意事项
-----------------
- 表结构必须与代码中的列名一致（`memory` 表至少要包含 `chat_log_id, keyword, value, topic, tags, source, is_deleted, created_at` 等列）。`db/init_db.py` 应创建相应表。
- 对高并发写入场景没有显式的事务或锁策略（使用 sqlite 的单连接提交），在并发情境下可能需要改造为连接池或外部数据库。
