import re
from function.memory.preference_db import load_preference_rules, load_preference_templates
from difflib import SequenceMatcher
from function.memory.memory import Memory

PREFERENCE_RULES = load_preference_rules()
TEMPLATE_LIST = load_preference_templates()

def fuzzy_match(text: str, keyword: str) -> bool:
    return SequenceMatcher(None, keyword, text).ratio() >= 0.7  # 可从配置表读取

def analyze_input(user_input: str, memory: Memory) -> str:
    for key, (reply_template, _) in PREFERENCE_RULES.items():
        for template in TEMPLATE_LIST:
            try:
                pattern = template.replace("{key}", re.escape(key)).replace("{item}", r"(.+?)")
                match = re.search(pattern, user_input)
                if match and match.lastindex:
                    item = match.group(1).strip()
                    if item:
                        memory.add(chat_log_id=-1, keyword=key, value=item, source="自动提取")
                        return reply_template.format(item=item)
            except re.error as e:
                print(f"[❌ 正则错误] 模板: {template} key: {key} -> {e}")

    for key, (reply_template, _) in PREFERENCE_RULES.items():
        if fuzzy_match(user_input, key):
            memory.add(chat_log_id=-1, keyword=key, value=user_input, source="模糊匹配")
            return reply_template.format(item=user_input)

    return ""

def recall_input(user_input: str, memory: Memory) -> str:
    for key in PREFERENCE_RULES.keys():
        pattern = fr"{re.escape(key)}.*(什么|还记得|记得我|告诉我)"
        if re.search(pattern, user_input):
            fact = memory.recall_latest(key)
            if fact:
                return f"你曾经提到你{key}{fact}～"

    for key in PREFERENCE_RULES.keys():
        if fuzzy_match(user_input, key) and any(x in user_input for x in ["什么", "记得", "告诉我"]):
            fact = memory.recall_latest(key)
            if fact:
                return f"你好像说过你{key}{fact}～"
    return ""
