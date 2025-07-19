from typing import List
import hashlib

class SimpleSummarizer:
    def __init__(self):
        self.cache = {}

    def summarize(self, messages: List[str]) -> str:
        key = hashlib.md5("".join(messages).encode("utf-8")).hexdigest()
        if key in self.cache:
            return self.cache[key]

        # TODO: 可替换为真正的 summarization 模型
        summary = "总结了以下内容：" + "；".join([msg[:20] + "…" for msg in messages])
        self.cache[key] = summary
        return summary
