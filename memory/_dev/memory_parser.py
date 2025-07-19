import re

# 关键词词典，映射到记忆的字段名
KEYWORD_MAP = {
    "喜欢": "喜欢的东西",
    "讨厌": "讨厌的东西",
    "生日": "生日",
    "来自": "家乡",
    "家乡": "家乡",
    "听": "喜欢的歌手",
}

# 通用模板正则（匹配句子结构）
TEMPLATES = [
    r"我\s*{key}\s*([^\s，。！]*)",
    r"我\s*的{key}\s*是\s*([^\s，。！]*)",
    r"我\s*最{key}\s*的是\s*([^\s，。！]*)",
    r"我\s*总是\s*{key}\s*([^\s，。！]*)",
    r"我\s*(不)?太{key}\s*([^\s，。！]*)",
]

def extract_memory(text):
    results = []
    for key, field in KEYWORD_MAP.items():
        for template in TEMPLATES:
            pattern = template.format(key=key)
            match = re.search(pattern, text)
            if match:
                # 提取匹配内容（支持含“我不太喜欢xxx”这种否定的情况）
                value = match.group(2) if match.lastindex >= 2 else match.group(1)
                results.append((field, value.strip()))
                break  # 同一个关键词匹配一次就够
    return results
