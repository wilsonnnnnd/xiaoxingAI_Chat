import re
from difflib import SequenceMatcher
from function.memory.memory import Memory
from function.memory.preference_db import load_preference_rules, load_keyword_templates

PREFERENCE_RULES = load_preference_rules()
KEYWORDS = load_keyword_templates()

PREFERENCE_HINT_WORDS = KEYWORDS["preference"]
NEGATIVE_WORDS = KEYWORDS["negative"]
RECALL_HINT_WORDS = KEYWORDS["recall"]

def fuzzy_match(text: str, keyword: str) -> bool:
    return SequenceMatcher(None, keyword, text).ratio() >= 0.7

def analyze_input(user_input: str, memory: Memory) -> str:
    print(f"[🔍 分析输入] 用户输入: {user_input}")
    
    for key in PREFERENCE_RULES:
        if key in user_input:
            # 否定处理（只对正向关键词适用）
            if key == "喜欢" and any(neg in user_input for neg in NEGATIVE_WORDS):
                print(f"[⚠️ 否定表达] 跳过关键词 key='{key}' 匹配")
                continue
            
            # 提取关键词后的内容
            match = re.search(rf"{key}\s*(.+)", user_input)
            if match:
                item = match.group(1).strip()
                if item:
                    reply_template, topic = PREFERENCE_RULES[key]
                    print(f"[🧠 提取偏好] 命中关键词：key='{key}' → item='{item}'")
                    memory.add(chat_log_id=-1, keyword=key, value=item, topic=topic, source="关键词提取")
                    return reply_template.format(item=item)

    print("[ℹ️ 无关键词提取]")
    return ""

def recall_input(user_input: str, memory: Memory) -> str:
    print(f"[🔍 回忆触发] 用户输入: {user_input}")

    for key in PREFERENCE_RULES:
        if key in user_input and any(hint in user_input for hint in RECALL_HINT_WORDS):
            fact = memory.recall_latest(key)
            if fact:
                print(f"[🧠 精确命中] key='{key}' → 记忆值='{fact}'")
                return f"你曾经提到你{key}{fact}～"

    for key in PREFERENCE_RULES:
        if fuzzy_match(user_input, key) and any(hint in user_input for hint in RECALL_HINT_WORDS):
            fact = memory.recall_latest(key)
            if fact:
                print(f"[🧠 模糊命中] key='{key}' → 记忆值='{fact}'")
                return f"你好像说过你{key}{fact}～"

    print("[ℹ️ 无法触发回忆]")
    return ""
