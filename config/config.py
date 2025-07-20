## json configuration files
KEYWORD_MAP_PATH = "config/keyword_map.json"
TEMPLATE_PATH = "config/templates.json"
EMOTION_WORDS_PATH = "config/emotion_words.json"
SPEECH_STYLE_PATH = "config/speech_styles.json"
PROMPT_PATH = "config/prompt.txt"
SUMMARY_LOG_PATH = "memory/store/summary_log.json"


## file paths for various resources
LOG_SPEECH_PATH = "memory/speak_log.jsonl"
MARKDOWN_DIR = "memory/speak_markdown"
AUDIO_DIR = "memory/audio"
MEMORY_PATH = "memory/store/memory_store.json"
CHART_OUTPUT_DIR = "memory"
DEFAULT_LOG_DIR = "memory/logs"


## API configuration
API_URL = "http://127.0.0.1:8000/v1/completions"

## Constants for various limits and configurations
HISTORY_LIMIT_FOR_SUMMARY = 10  # 至少10轮对话才尝试压缩
MAX_AUDIO_FILES = 100
HISTORY_LIMIT = 5       # 每次构造 prompt 时保留的上下文轮数
MAX_HISTORY = 20        # 总聊天历史保留上限
