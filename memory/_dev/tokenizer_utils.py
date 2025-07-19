import tiktoken  # 使用 OpenAI 兼容 tokenizer，可替换为自定义 tokenizer

ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")  # 可根据模型修改

def count_tokens(text: str) -> int:
    return len(ENCODER.encode(text))

def trim_conversation_history(history: list[str], max_tokens: int) -> list[str]:
    total_tokens = 0
    trimmed = []

    for message in reversed(history):
        token_count = count_tokens(message)
        if total_tokens + token_count > max_tokens:
            break
        trimmed.insert(0, message)
        total_tokens += token_count

    return trimmed
