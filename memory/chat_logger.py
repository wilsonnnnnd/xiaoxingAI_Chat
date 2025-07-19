import os
import json
from datetime import datetime

LOG_PATH = "E:/xiaoxing/memory/logs/"
os.makedirs(LOG_PATH, exist_ok=True)

def log_conversation(user_input, assistant_reply):
    timestamp = datetime.now().isoformat(timespec="seconds")
    log_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "xiaoxing": assistant_reply
    }

    log_file = os.path.join(LOG_PATH, f"chat_{datetime.today().date()}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
