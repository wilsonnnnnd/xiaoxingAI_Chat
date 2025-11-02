# 功能文档：聊天主流程（main_chat.py）

概述
-----
`main_chat.py` 实现 CLI 风格的主交互循环，是程序的顶层控制点。主要职责：接收用户输入、按优先级应用记忆检索与规则、调用情绪检测、向 AI 后端请求回复、记录会话、触发语音合成并维护历史与调度线程。

关键函数 / 组件
----------------
- `main()` (async)
  - 输入：用户通过 stdin 输入的文本。
  - 输出：在控制台打印 bot 回复并返回（通过持续循环，不会立即返回）。
  - 依赖：`Memory`, `EmotionTracker`, `log_conversation`, `get_speech_config`, `speak`, `summarize_and_store`, `start_summary_scheduler_thread`, `start_speech_report_scheduler_thread`。
  - 行为要点：
    - 启动摘要与语音报告调度线程（daemon）。
    - 读取并打印上次摘要（`load_latest_summary`）。
    - 循环处理输入：退出关键字检测 -> 摘要命令检测 -> 尝试 `analyze_input`（记忆解析） -> 情绪检测并保存情绪关键词 -> 回忆（`recall_input`） -> 若无则调用 `ask_llama_ai`。
    - 将最终回复记录到 `chat_history` 并保持长度上限（`MAX_HISTORY`）。

- `build_prompt(user_input, system_prompt, history, summary)`
  - 用途：整合系统提示、最近摘要与历史对话，生成发送给模型的 `prompt`。

- `ask_llama_ai(user_input, summary)`
  - 用途：读取 `PROMPT_PATH` 系统提示，调用 `build_prompt`，并通过 `requests.post(API_URL, json=...)` 向模型后端请求回复。
  - 返回：模型返回的文本（或在异常时返回固定提示字符串）。

依赖及副作用
---------------
- 依赖全局配置（`config/config.py`）中的 `PROMPT_PATH`, `API_URL`, token & 历史限制配置。
- 多处写入会触发 SQLite 操作（通过 `ChatLogger`、`Memory` 等），并可能写入音频文件目录。

已知限制
---------
- `ask_llama_ai` 假定 `API_URL` 可用；若不可达会捕获异常并返回固定错误文本。程序没有在启动阶段对模型服务做健康检查。
- 主循环对 IO（stdin/stdout）敏感，适用于命令行运行场景。

注意点
------
- 若需在 GUI 或服务化部署，建议将 `main()` 中的同步 stdin/read loop 替换为事件或 RPC 接口，并将调度线程/播放队列整合到服务生命周期管理。
