# 功能文档：记忆解析器（function/memory/memory_parser.py）

概述
-----
`memory_parser.py` 提供从自然语言文本中抽取结构化偏好/记忆信息的工具函数，适用于在对话中将显式或隐含的偏好转换为可写入记忆表的字段与值对。

主要函数
---------
- `load_keyword_map() -> dict`
  - 从 DB 表 `preference_keyword_map` 读取关键字到字段名的映射（返回 {keyword: field}）。
- `load_templates() -> list`
  - 从 DB 表 `preference_template` 读取模板 pattern 列表（返回 regex 风格的模板字符串列表）。
- `extract_memory(text: str, keyword_map_override=None, templates_override=None) -> List[(field, value)]`
  - 工作流程：加载关键词映射与模板（或使用 override），对每个关键词与模板组合构造 regex（`template.format(key=re.escape(key))`），执行忽略大小写的匹配并提取匹配组中最后一个非空的捕获组作为值。
  - 返回值：列表，每项为 (field_name, value) 的二元组。

错误与容错
-----------------
- 模板解析使用 `re`，若模板本身非法会打印错误并跳过该模板。
- 匹配策略中若没有匹配结果，函数会继续尝试其它模板或关键词，不会抛出异常。

依赖
----
- 依赖 `config.config.DB_PATH` 指向的数据库，预期存在 `preference_keyword_map` 与 `preference_template` 表。

注意事项
---------
- 正则模板需由 DB 维护并确保安全性与正确性（错误模板会被捕获并打印）。
- 提取结果为原始字符串，调用方需根据上下文决定是否写入 `memory` 表或进一步规范化（如标准化时间、地点格式等）。
