from memory_parser import extract_memory
from datetime import datetime

def analyze_input(user_input: str, memory) -> str | None:
    extracted = extract_memory(user_input)
    if extracted:
        responses = []
        for key, value in extracted:
            memory.remember(key, value)  # 内部已记录时间戳
            responses.append(f"嗯嗯～我记住了，你的「{key}」是「{value}」噢～")
        return "\n".join(responses)
    return None

def recall_input(user_input: str, memory) -> str | None:
    for key in memory.data.keys():
        if key in user_input:
            value = memory.recall(key)
            return f"当然记得呀～你告诉我你的「{key}」是「{value}」噢～"
    return None
