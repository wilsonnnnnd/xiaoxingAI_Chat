import re
import json
import os
from config.config_paths import KEYWORD_MAP_PATH, TEMPLATE_PATH


def load_json(path: str) -> dict | list:
    if not os.path.exists(path):
        print(f"[配置缺失] {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 加载配置
keyword_map = load_json(KEYWORD_MAP_PATH)
templates = load_json(TEMPLATE_PATH)

def extract_memory(text: str, keyword_map_override=None, templates_override=None):
    results = []
    local_map = keyword_map_override or keyword_map
    local_templates = templates_override or templates

    for key, field in local_map.items():
        for template in local_templates:
            pattern = template.format(key=re.escape(key))
            match = re.search(pattern, text)
            if match:
                value = match.group(2) if match.lastindex and match.lastindex >= 2 else match.group(1)
                if value:
                    results.append((field, value.strip()))
                    break  # 命中一次即跳出
    return results
