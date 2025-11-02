# 功能文档：摘要与报告（function/summary）

概述
-----
摘要模块负责：在对话达到一定量时使用外部模型（通过 `API_URL`）生成对话摘要，将摘要持久化到 `daily_summary` 表，并提供导出/可视化（词云、情绪柱状图）与每日调度执行。

模块概览
----------
- `summary_manager.py`
  - `summarize_chat_history(chat_history: list[str], api_url: str = API_URL) -> str`：若 `chat_history` 长度低于 `HISTORY_LIMIT_FOR_SUMMARY` 则返回空；否则构建摘要 prompt 并 POST 到 `API_URL` 获取摘要文本。
  - `summarize_and_store(chat_history: list[str]) -> str`：调用摘要接口并将结果写入 `SummaryDB`。（可能尝试调用 `detect_emotion` 来为摘要加上情绪标签，如果可用）。
  - `load_latest_summary() -> str`：读取最近一条摘要记录。

- `summary_db.py`
  - `SummaryDB.save(summary, emotion, ...)`：将摘要写入 `daily_summary`（按日期 `INSERT OR REPLACE`）。
  - `load_all`, `load_latest`, `close` 等简单 CRUD。

- `summary_reporter.py`
  - 提供将摘要导出为 Markdown (`export_summaries_to_markdown`) 与生成情绪柱状图和摘要词云（依赖 `matplotlib` 与 `wordcloud`）的方法。

- `scheduler_manager.py`
  - `start_summary_scheduler_thread(chat_history)`：使用 `schedule` 在每日配置时间触发 `summarize_and_store`（仅在对话量 >= 5 时执行）。
  - `start_speech_report_scheduler_thread()`：按计划触发 `generate_speech_report`。

依赖
----
- 外部模型服务：通过 `API_URL` 调用（配置在 `config/config.py`）。
- Python 包：`requests`, `schedule`, `matplotlib`, `wordcloud`。
- 数据库：`daily_summary` 表，用于持久化摘要内容与情绪标签。

已知限制
---------
- 摘要生成依赖外部 HTTP 接口，可用性直接影响此模块输出；当接口失败或返回不可解析的结果时，模块会打印错误并返回空摘要。
- 词云生成依赖字体文件（`WORD_FONT_PATH`），若缺失可能导致生成失败。
