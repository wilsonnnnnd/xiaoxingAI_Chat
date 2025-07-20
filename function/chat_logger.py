import os
import json
from datetime import datetime

from config.config import DEFAULT_LOG_DIR


def ensure_log_dir(log_dir: str = DEFAULT_LOG_DIR) -> str:
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def get_log_file_path(log_dir: str = DEFAULT_LOG_DIR) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"chat_{date_str}.jsonl")

def log_conversation(user_input: str, assistant_reply: str, log_dir: str = DEFAULT_LOG_DIR, extra_fields: dict = None) -> str:
    ensure_log_dir(log_dir)
    timestamp = datetime.now().isoformat(timespec="seconds")

    log_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "xiaoxing": assistant_reply
    }

    if extra_fields:
        log_entry.update(extra_fields)

    log_path = get_log_file_path(log_dir)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    return log_path  # 可选返回路径
