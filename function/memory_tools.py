import re
from function.memory import Memory
from config.config import TEMPLATES_PATH

# 偏好关键词规则定义：关键词 -> [回复模板, 情绪标签（可选）]
PREFERENCE_RULES = {
    "喜欢": ["你喜欢{item}，我记住啦～", "joy"],
    "名字": ["你好，{item}～我记住你的名字了！", "friendly"],
    "生日": ["你的生日是{item}，我已经记下来了 🎂", "joy"],
    "讨厌": ["原来你不喜欢{item}，我会避开它～", "disgust"],
    "住在": ["你住在{item}呀～听起来不错！", "neutral"]
    # 可继续扩展...
}

def analyze_input(user_input: str, memory: Memory) -> str:
    """
    根据用户输入分析偏好关键词，自动提取并记忆
    """
    for key, (reply_template, _) in PREFERENCE_RULES.items():
        for template in TEMPLATES_PATH:
            pattern = template.replace("{key}", key)
            match = re.search(pattern, user_input)
            if match:
                item = match.group(1).strip()
                if item:
                    memory.remember(key, item)
                    return reply_template.format(item=item)
    return ""

def recall_input(user_input: str, memory: Memory) -> str:
    """
    当用户提问如“我喜欢什么？”时，从记忆中搜索关键词
    """
    for key in PREFERENCE_RULES.keys():
        if key in user_input and any(kw in user_input for kw in ["什么", "还记得", "记得我"]):
            fact = memory.recall(key)
            if fact:
                return fact
    return ""
