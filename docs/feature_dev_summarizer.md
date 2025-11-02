# 功能文档（开发用）：简易摘要占位器（memory/_dev/summarizer.py）

概述
-----
该模块位于 `memory/_dev/`，提供一个非常轻量的本地 `SimpleSummarizer` 实现，用于在开发或测试阶段生成占位摘要。该实现使用字符串拼接并在内部维护简单缓存（基于消息列表的 MD5）。

关键内容
--------
- `class SimpleSummarizer`
  - `summarize(messages: List[str]) -> str`：将传入消息列表拼接并返回一个简短的占位摘要（使用每条消息的前 20 个字符）。
  - 内部使用 `hashlib.md5` 对消息合并字符串建 key 并缓存结果以避免重复计算。

当前状态（TODO）
----------------
- 源码中标记："# TODO: 可替换为真正的 summarization 模型"。说明这是占位实现，主流程并未直接依赖该文件（主流程使用 `function/summary/summary_manager.py` 调用外部 HTTP 接口）。

适用场景
--------
- 本模块适合离线测试或在无模型服务时提供非常基础的摘要占位输出；不建议在生产环境作为最终摘要方案使用。
