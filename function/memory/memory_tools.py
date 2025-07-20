import re
import json
from config.config import FUZZY_THRESHOLD, TEMPLATE_PATH, PREFERENCE_RULES_PATH
from function.memory.memory import Memory
from difflib import SequenceMatcher

# 加载偏好关键词规则
with open(PREFERENCE_RULES_PATH, encoding="utf-8") as f:
    PREFERENCE_RULES = json.load(f)

# ✅ 加载模板内容（而不是路径字符串）
with open(TEMPLATE_PATH, encoding="utf-8") as f:
    TEMPLATE_LIST = json.load(f)

def fuzzy_match(text: str, keyword: str) -> bool:
    return SequenceMatcher(None, keyword, text).ratio() >= FUZZY_THRESHOLD

def analyze_input(user_input: str, memory: Memory) -> str:
    """
    根据用户输入分析偏好关键词，自动提取并记忆，支持模糊关键词匹配
    """

    for key, value in PREFERENCE_RULES.items():
        reply_template, _ = value
        for template in TEMPLATE_LIST:
            try:
                if template.startswith("\\"):
                    raise re.error("模板非法转义，必须以非\\字符开头")

                pattern = template.replace("{key}", re.escape(key))
                pattern = pattern.replace("{item}", r"(.+?)")  # 非贪婪匹配
                match = re.search(pattern, user_input)
                if match and match.lastindex:
                    item = match.group(1).strip()
                    if item:
                        memory.remember(key, item)
                        return reply_template.format(item=item)
            except re.error as e:
                print(f"[❌ 正则错误] 模板: {template} key: {key} -> {e}")

    for key, value in PREFERENCE_RULES.items():
        reply_template, _ = value
        if fuzzy_match(user_input, key):
            memory.remember(key, user_input)
            return reply_template.format(item=user_input)

    return ""

def recall_input(user_input: str, memory: Memory) -> str:
    """
    当用户提问如“我喜欢什么？”时，从记忆中搜索关键词
    """
    for key in PREFERENCE_RULES.keys():
        pattern = fr"{re.escape(key)}.*(什么|还记得|记得我|告诉我)"
        if re.search(pattern, user_input):
            fact = memory.recall(key)
            if fact:
                return f"你曾经提到你{key}{fact}～"

    for key in PREFERENCE_RULES.keys():
        if fuzzy_match(user_input, key) and any(x in user_input for x in ["什么", "记得", "告诉我"]):
            fact = memory.recall(key)
            if fact:
                return f"你好像说过你{key}{fact}～"
    return ""