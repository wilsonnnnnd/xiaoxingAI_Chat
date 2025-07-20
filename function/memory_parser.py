import re
from config.config import KEYWORD_MAP_PATH, TEMPLATE_PATH


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
    local_map = keyword_map_override or KEYWORD_MAP_PATH
    local_templates = templates_override or TEMPLATE_PATH

    for key, field in local_map.items():
        for template in local_templates:
            try:
                pattern = template.format(key=re.escape(key))
                match = re.search(pattern, text)
                if match:
                    # 提取所有 group 中最后一个非 None 的组
                    value = next((g for g in reversed(match.groups()) if g), None)
                    if value:
                        results.append((field, value.strip()))
                        break  # 命中一次即跳出
            except re.error as e:
                print(f"❌ 模板解析错误：{template} -> {e}")
    return results
