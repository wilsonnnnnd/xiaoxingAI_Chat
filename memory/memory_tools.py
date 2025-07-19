from memory.memory_parser import extract_memory
from datetime import datetime

# 可根据需要设置多语言模板
RESPONSE_TEMPLATES = {
    "remember": "我已经记住了：{key} = {value}",
    "recall": "你之前告诉我，{key} 是 {value}"
}

def analyze_input(user_input: str, memory) -> str | None:
    extracted = extract_memory(user_input)
    if extracted:
        responses = []
        for key, value in extracted:
            memory.remember(key, value)
            responses.append(RESPONSE_TEMPLATES["remember"].format(key=key, value=value))
        return "\n".join(responses)
    return None

def recall_input(user_input: str, memory) -> str | None:
    for key in memory.data.keys():
        if key in user_input:
            value = memory.recall(key)
            return RESPONSE_TEMPLATES["recall"].format(key=key, value=value)
    return None
