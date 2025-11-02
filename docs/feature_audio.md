# 功能文档：语音合成与播放（function/audio）

概述
-----
语音相关实现分布在 `function/audio/` 目录，主要职责包括：从数据库读取情绪匹配的 TTS 配置、使用 `edge_tts` 合成音频文件、记录合成日志并异步播放。

主要模块与函数
----------------
- `speech_utils.py`
  - `_start_speak_worker()`：启动后台播放线程，监听 `speak_queue` 并调用平台命令播放音频文件（Windows 使用 `start`、macOS 使用 `afplay`、Linux 使用 `mpg123`）。
  - `build_ssml(text, voice, style, rate, volume)`：根据参数构造 SSML 字符串。
  - `async speak(text, voice=..., style=..., rate=..., volume=..., remove_brackets=True)`：合成音频并入队播放流程。
    - 行为：清洗文本 -> 构建 SSML -> 使用 `edge_tts.Communicate` 生成 MP3 到 `AUDIO_DIR` -> 验证音频文件大小 -> 写入 `speech_log` -> 将路径放入播放队列。

- `speech_config_db.py`
  - `get_speech_config(emotion: str) -> dict`：返回与指定情绪最匹配（或 `_default`）的一行配置（包含 style, voice, rate, volume）。

- `speech_logger.py`
  - `log_speech_to_db(text: str, path: str)`：将合成文本与输出路径写入 `speech_log` 表。

依赖
----
- Python 包：`edge_tts`（合成），`subprocess` 用于调用系统播放器，`python-vlc`（可选，用于在进程内播放以避免弹出外部播放器窗口）。
- 配置：`config/config.py` 提供 `AUDIO_DIR`, `MIN_AUDIO_FILE_SIZE` 与默认 TTS 参数。
- 数据库：写入 `speech_log` 表，需要 `DB_PATH` 可用并包含对应表。

系统级要求
 脚本现在会按顺序尝试：`python-vlc`（进程内）→ `pydub+simpleaudio`（进程内）→ `ffplay` / `mpv`（无窗口外部播放器）→ `os.startfile`（最后回退，会弹出播放器窗口）。为了在不弹窗的环境中获得最佳兼容性，请尽量安装 `ffmpeg`（提供 `ffplay`）或 `mpv`。
 安装示例（Windows）：
  - 安装 VLC：从 https://www.videolan.org/ 下载并安装；然后在虚拟环境中运行 `pip install python-vlc`。
  - 安装 ffmpeg（包含 ffplay）：建议使用 https://www.gyan.dev/ffmpeg/builds/ 或 choco：
    - choco 安装（需要 Chocolatey）：
      - choco install ffmpeg -y
    - 或手动下载并将 ffmpeg/bin 添加到 PATH。
  - 安装 mpv（可选）：下载 Windows 发行版并将可执行文件放入 PATH，或使用包管理器安装。

已知限制
---------
- 播放依赖具体平台命令，若目标环境缺少这些命令（例如 Linux 没有 mpg123）或无法在无头环境下播放，播放将失败。合成成功但播放失败时，`speak` 仅打印错误。
- `edge_tts` 的参数使用较直接，未实现复杂的 retry 或长文本分片策略（长文本可能需要按段合成）。

安全/兼容性注意
------------------
- 生成的文件保存在磁盘，建议定期清理 `AUDIO_DIR`（配合 `MAX_AUDIO_FILES` 与文件大小阈值的策略）。
