import re
import sqlite3
from config.config import DB_PATH

def load_keyword_map() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT keyword, field FROM preference_keyword_map")
    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return result

def load_templates() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT pattern FROM preference_template")
    templates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return templates

def extract_memory(text: str, keyword_map_override=None, templates_override=None):
    """
    从用户输入中提取结构化偏好信息
    参数：
        text: 用户输入文本
        keyword_map_override: 可选的关键词映射（用于测试或临时注入）
        templates_override: 可选的匹配模板列表
    返回：
        List[Tuple[field_name, value]]
    """
    results = []
    local_map = keyword_map_override or load_keyword_map()
    local_templates = templates_override or load_templates()

    for key, field in local_map.items():
        for template in local_templates:
            try:
                pattern = template.format(key=re.escape(key))
                match = re.search(pattern, text, flags=re.IGNORECASE)  # 忽略大小写匹配
                if match:
                    # 提取所有 group 中最后一个非 None 的组
                    value = next((g for g in reversed(match.groups()) if g), None)
                    if value:
                        results.append((field, value.strip()))
                        break  # 命中一次即跳出
            except re.error as e:
                print(f"❌ 模板解析错误：{template} -> {e}")
    return results
