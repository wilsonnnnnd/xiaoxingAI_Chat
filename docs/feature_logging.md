# 功能文档：对话日志（function/log/chat_logger.py）

概述
-----
`function/log/chat_logger.py` 封装了对话日志写入逻辑，使用 SQLite 将用户与 bot 的文本记录到 `chat_log` 表。提供类接口与便捷的模块级函数以供主流程调用。

类与函数
---------
- `class ChatLogger`（`__init__(db_path=DB_PATH)`）
  - `log(role: str, content: str, topic: Optional[str]=None, tags: Optional[List[str]]=None, context_version: int = 1, is_deleted: int = 0) -> int`
    - 向 `chat_log` 表插入一条记录并返回 `chat_log_id`（通过 `last_insert_rowid()`）。
  - `close()`：关闭 DB 连接。

- `log_conversation(user_text: str, bot_text: str, extra_fields: dict = None)`
  - 便捷函数：先写入用户消息再写入机器人回复，将 `extra_fields`（如 emotion, keyword）转换为 tags 并保存到每条记录的 tags 字段中。

数据库依赖
-----------
- 使用 `config/config.DB_PATH` 的 SQLite 数据库；预期存在 `chat_log` 表，字段与 INSERT 语句一致（role, content, topic, tags, context_version, is_deleted, created_at 等）。

错误处理
---------
- 本模块在写入过程中若发生 sqlite 异常，调用方可能会看到异常输出；主流程在 `log_conversation` 调用之后没有对异常进行额外处理。

注意事项
---------
- `tags` 使用 JSON 编码（`json.dumps`）保存，读取时需要相应解析。
- 推荐在生产部署前检查并确保 `chat_log` 表结构与代码一致；可将 `db/init_db.py` 用作参考或迁移脚本。
