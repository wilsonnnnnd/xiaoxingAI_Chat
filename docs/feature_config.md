# 功能文档：配置（config/config.py）

概述
-----
`config/config.py` 提供项目运行所需的全局常量和路径定义。模块被仓库中多个功能模块直接导入以获取配置值（文件路径、DB 路径、TTS 默认参数、限制阈值及调度时间等）。

关键常量
---------
- `BASE_DIR`、`CONFIG_DIR`、`MEMORY_DIR`、`AUDIO_DIR`、`REPORT_DIR`：项目中各类文件的基础目录路径。大多数模块依赖这些路径进行文件读写。
- `DB_PATH`：SQLite 数据库文件路径（默认为 `db/xiaoxing_memory.db`），是所有持久化模块的统一数据源。
- `PROMPT_PATH`：系统提示文本文件路径（`config/prompt.txt`），被 `main_chat.ask_llama_ai` 读取以构建 prompt。
- API 相关：`URL`, `API_URL`（默认为 `http://127.0.0.1:8000/v1/completions`），被摘要与主对话调用用于与模型后端交互。
- token 与历史限制：`MAX_SUMMARY_TOKENS`, `MAX_HISTORY_ROUNDS`, `HISTORY_LIMIT`, `MAX_HISTORY` 等，用于控制 prompt 大小、历史回溯和摘要触发条件。
- TTS 默认参数：`DEFAULT_VOICE`, `DEFAULT_STYLE`, `DEFAULT_RATE`, `DEFAULT_VOLUME`。
- 调度时间：`SUMMARY_SCHEDULE_TIME`, `SPEECH_REPORT_SCHEDULE_TIME`（用于 `schedule` 调度器）。

用途与依赖
-----------
- 所有需要路径或常量的模块应从此文件导入配置，而不是硬编码字符串或路径。
- 若要变更持久化位置或外部服务地址，仅需修改此文件或通过环境/部署化的替换。

已知限制
---------
- 本配置文件是静态的 Python 模块；生产中可能希望通过环境变量或外部配置文件（YAML/JSON）进行覆盖或注入。
