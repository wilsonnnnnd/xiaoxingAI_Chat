## 简要模块概述

本仓库为“小星”聊天助手（xiaoxing）的 Python 层实现，围绕对话交互、记忆管理、情绪分析、语音合成与每日摘要功能构建。系统以本地 SQLite 作为主要持久化层，并通过一个配置的 HTTP 接口（默认 `http://127.0.0.1:8000/v1/completions`，由 `config/config.py` 中的 `API_URL` 配置）调用模型后端生成回复。

主要已实现模块：

- `main_chat.py`：主入口与对话控制流程。处理用户输入，优先使用记忆检索与规则逻辑，调用情绪检测、AI 接口生成回复、记录会话并触发 TTS。
- `config/config.py`：项目常量与路径配置（包含 DB 路径、PROMPT 路径、TTS 默认参数、历史与 token 限制、每日调度时间等）。
- `function/log/chat_logger.py`：对话日志封装（`ChatLogger` 类、`log_conversation` 辅助函数），写入 `chat_log` 表。
- `function/memory/memory.py`：`Memory` 类，提供对 `memory` 表与 `emotions` 表的增删查接口（`add`, `save_emotion`, `recall`, `recall_latest`, `forget`）。
- `function/memory/memory_parser.py`：从自由文本中抽取偏好/记忆信息的工具（`extract_memory`），依赖 DB 中 `preference_keyword_map` 与 `preference_template` 表。
- `function/audio/speech_utils.py`：基于 `edge_tts` 的 TTS 合成与本地播放队列实现（`speak` 异步函数与后台播放线程）。
- `function/audio/speech_config_db.py` / `function/audio/speech_logger.py`：读取语音配置与写入语音合成日志（`speech_log`）。
- `function/summary/summary_manager.py` / `function/summary/summary_db.py` / `function/summary/summary_reporter.py`：聊天摘要生成（通过 `API_URL` 调用）、摘要持久化与导出/可视化（词云/情绪柱状图）。
- `function/summary/scheduler_manager.py`：使用 `schedule` 启动两个后台守护线程，按配置时间触发每日摘要与每日语音报告。

## 关键函数说明

以下列出仓库中已实现并在主流程中明确被调用或导入的关键函数/类（以源码为准）：

- build_prompt(user_input: str, system_prompt: str = "", history: List[Dict[str,str]] = [], summary: str = "") -> str
  - 作用：拼接系统提示、历史对话与最近摘要为最终发送给模型的 prompt。
  - 输入：用户文本、系统提示、历史对话（user/bot 条目）、摘要文本（可选）。
  - 输出：字符串形式的 prompt。

- ask_llama_ai(user_input: str, summary: str = "") -> str
  - 作用：读取 `PROMPT_PATH`（系统提示），调用 `build_prompt`，向 `API_URL` 发起 POST 请求获取模型回复。
  - 输入：用户文本、摘要（可选）。
  - 输出：模型返回的文本；若网络/解析失败，返回固定错误提示字符串。

- main() (async) in `main_chat.py`
  - 作用：CLI 主循环，按步骤执行：解析/退出判断、优先使用记忆逻辑、情绪检测与记录、回忆逻辑、AI 回应、日志写入、TTS 合成与播放、历史维护与情绪统计展示。
  - 关键依赖：`Memory` 实例、`EmotionTracker`、`log_conversation`、`get_speech_config`、`speak`、`summarize_and_store`、摘要调度函数。

- class Memory (`function/memory/memory.py`)
  - add(chat_log_id, keyword, value, topic=None, tags=None, source=None)
    - 写入 `memory` 表（含 tags JSON、is_deleted 标记），commit 后无返回值。
  - save_emotion(keyword, emotion)
    - 将情绪与关键词写入 `emotions` 表（含 timestamp）。
  - recall(keyword) -> List[dict]
    - 返回匹配且未删除的记忆列表（字段：keyword, value, topic, tags, source, created_at）。
  - recall_latest(keyword) -> Optional[str]
    - 返回最新一条 value，若无返回 None。
  - forget(keyword)
    - 将记忆项标记为已删除（is_deleted=1）。

- extract_memory(text: str, keyword_map_override=None, templates_override=None) -> List[(field, value)] (`function/memory/memory_parser.py`)
  - 作用：基于 DB 中的关键词映射表与模板列表，通过正则匹配从自然语言中抽取结构化偏好（字段名与值对）。

- ChatLogger.log(role, content, topic=None, tags=None, context_version=1, is_deleted=0) -> int
  - 作用：向 `chat_log` 插入一条记录并返回 `chat_log_id`。
  - `log_conversation(user_text, bot_text, extra_fields=None)` 为便捷写入函数，会写入两条记录（user/bot）。

- speak(text, voice=..., style=..., rate=..., volume=..., remove_brackets=True) (异步)
  - 作用：使用 `edge_tts.Communicate` 合成音频为 MP3，保存到 `AUDIO_DIR`，记录至 `speech_log` 并将文件路径放入播放队列，由后台线程执行播放。
  - 异常与退化处理：若生成文件不存在或小于 `MIN_AUDIO_FILE_SIZE` 则视为合成失败并跳过；合成/播放异常会被捕获并打印。

- summarize_chat_history / summarize_and_store / load_latest_summary (`function/summary/summary_manager.py`)
  - 作用：当对话记录数达到阈值时，构造 prompt 调用 `API_URL` 获取摘要，通过 `SummaryDB.save` 持久化；`load_latest_summary` 用于读取最近摘要。

## 依赖与调用关系（高层次）

- 配置：`config/config.py` 提供全局常量（路径、DB、API_URL、TTS 默认值、时间配置等），多数模块直接导入使用。
- 主流程：`main_chat.py` 调用记忆解析 (`function/memory/memory_tools`)、情绪检测 (`function/emotion/emotion_utils`)、日志 (`function/log/chat_logger`)、摘要 (`function/summary/summary_manager`) 与 TTS (`function/audio/speech_utils`)。
- 数据层：所有持久化均基于 SQLite（路径由 `DB_PATH` 指定），涉及表有但不限于：`chat_log`, `memory`, `emotions`, `daily_summary`, `speech_log`, `speech_config`, `preference_keyword_map`, `preference_template`。这些表的创建由 `db/init_db.py` 或外部初始化过程负责。
- 外部服务：模型后端依赖 HTTP 接口（`API_URL`）。TTS 合成依赖第三方包 `edge_tts`，播放依赖系统平台命令（Windows 使用 `start`、macOS 使用 `afplay`、Linux 使用 `mpg123` 等）。

## 当前限制与已知问题（源码中明确的限制/TODO/FIXME）

- 外部服务依赖性：
  - 模型生成依赖 `API_URL` 指向的服务，若不可达 `ask_llama_ai` 返回错误提示字符串。仓库未包含模型服务的启动脚本（仅在 `llama.cpp` 子项目中存在大量工具，但主流程仅通过 HTTP 请求交互）。

- 数据库结构假定：
  - 多模块直接读写特定表；若 `db` 未初始化或缺少表，运行时会出现 sqlite 错误。请确保运行 `db/init_db.py` 或已经创建所需表。

- 摘要/情绪模块：
  - `function/summary/summary_manager.py` 通过 HTTP 请求外部接口完成摘要；当对话数量不足或接口返回失败时会跳过或返回空字符串。情绪识别依赖 `function/emotion` 模块（其导入在代码中有 try/except 保护，可能在某些环境下不可用）。

- 语音合成/播放兼容性：
  - 使用 `edge_tts` 合成并依赖各平台播放命令，若环境缺少相应播放命令或 `edge_tts` 安装异常，会导致合成或播放失败。`speak` 会在合成失败时打印并跳过，但不会对上层做复杂回退。

- 占位/未完成实现（源码中显式标注）：
  - `memory/_dev/summarizer.py` 含 TODO 注释：当前为简易占位摘要实现（字符串截断与缓存），注释提示可替换为真正的 summarization 模型。该 `_dev` 模块并非主流程默认使用（主流程使用 `function/summary` 通过 HTTP 的实现）。
  - 仓库中 `llama.cpp` 子项目包含大量 TODO/FIXME（工具脚本、模型转换、测试），属于该子项目的未完成项，不属于 Python 主流程直接逻辑但影响模型相关工具链。

- 错误处理与鲁棒性：
  - 多处对 SQLite 操作、网络请求、外部进程调用仅打印异常并继续，缺乏统一的错误上报/重试策略；在生产化场景建议增强异常传播、重试与告警。

## 建议（基于当前实现的事实性建议）

- 在仓库文档中明确列出所需 DB 表结构或将 `db/init_db.py` 的创建 SQL 片段纳入 docs，使开发者/部署方可以快速初始化。 (我可以根据代码中 INSERT/SELECT 的列名自动生成一个初始 schema 草案，若需要请告知)。
- 增加对 `API_URL`（模型服务）和 TTS 引擎的启动前健康检查与可选退化策略（例如本地占位回复或禁用语音输出），以提升可用性。 
- 为关键 DB 操作与网络交互添加重试与更明确的异常处理，减少 silent-fail（仅打印日志但主流程继续）的风险。

---

附：本文件基于仓库中以下已读取源码生成（截取于 生成时刻）：

- `main_chat.py`
- `config/config.py`
- `function/memory/memory.py`
- `function/memory/memory_parser.py`
- `function/log/chat_logger.py`
- `function/audio/speech_utils.py`
- `function/audio/speech_config_db.py`
- `function/audio/speech_logger.py`
- `function/summary/summary_manager.py`
- `function/summary/summary_db.py`
- `function/summary/summary_reporter.py`
- `function/summary/scheduler_manager.py`
- `memory/_dev/summarizer.py` (标注 TODO)

若需我将该文档合并到 README 或生成对应的 `db/schema.md`（基于当前 SQL 使用字段推断），我可以继续执行。 

----
 文件生成时间：2025-11-02
