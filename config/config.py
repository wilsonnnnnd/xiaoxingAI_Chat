import os

# 获取项目根路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
STORE_DIR = os.path.join(MEMORY_DIR, "store")
AUDIO_DIR = os.path.join(MEMORY_DIR, "audio")
LOG_DIR = os.path.join(MEMORY_DIR, "logs")
SPEAK_LOG_DIR = os.path.join(MEMORY_DIR, "speak")
REPORT_DIR = os.path.join(MEMORY_DIR, "report")

# json configuration files
KEYWORD_MAP_PATH = os.path.join(CONFIG_DIR, "keyword_map.json")
TEMPLATE_PATH = os.path.join(CONFIG_DIR, "templates.json")
EMOTION_WORDS_PATH = os.path.join(CONFIG_DIR, "emotion_words.json")
SPEECH_STYLE_PATH = os.path.join(CONFIG_DIR, "speech_styles.json")
STOP_WORDS_PATH = os.path.join(CONFIG_DIR, "stop_words.json")
PROMPT_PATH = os.path.join(CONFIG_DIR, "prompt.txt")
PREFERENCE_RULES_PATH = os.path.join(CONFIG_DIR, "preference_rules.json")
# storage and logs
MEMORY_PATH = os.path.join(STORE_DIR, "memory_store.json")
SUMMARY_LOG_PATH = os.path.join(STORE_DIR, "summary_log.json")
LOG_SPEECH_PATH = os.path.join(SPEAK_LOG_DIR, "speak_log.jsonl")
MARKDOWN_DIR = os.path.join(SPEAK_LOG_DIR, "speak_markdown")
CHART_OUTPUT_DIR = REPORT_DIR
DEFAULT_LOG_DIR = LOG_DIR

# API
URL="http://127.0.0.1:8000"
API_URL = URL + "/v1/completions"

# chat configuration
HISTORY_LIMIT = 5
MAX_HISTORY = 20
HISTORY_LIMIT_FOR_SUMMARY = 10
MAX_AUDIO_FILES = 100

# audio settings
MIN_AUDIO_FILE_SIZE = 1024  # bytes

# TTS config
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_STYLE = "friendly"
DEFAULT_RATE = "0%"
DEFAULT_VOLUME = "0dB"

# word cloud settings
WORD_CLOUD_WIDTH = 800
WORD_CLOUD_HEIGHT = 400
WORD_CLOUD_COLOR = "white"
WORD_FONT_PATH = "simhei.ttf" # 中文字体路径

# emotion tracking
FUZZY_THRESHOLD = 0.75  # 模糊匹配相似度阈值