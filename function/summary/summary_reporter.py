import os
import json
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from config.config import SUMMARY_LOG_PATH, CHART_OUTPUT_DIR, MARKDOWN_DIR, WORD_CLOUD_COLOR, WORD_CLOUD_HEIGHT, WORD_CLOUD_WIDTH, WORD_FONT_PATH

def export_summaries_to_markdown():
    if not os.path.exists(SUMMARY_LOG_PATH):
        print("⚠️ 没有找到 summary_log.json，请先运行一次对话总结。")
        return

    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    with open(SUMMARY_LOG_PATH, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    for entry in summaries:
        date = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d")
        md_path = os.path.join(MARKDOWN_DIR, f"{date}.md")
        with open(md_path, "w", encoding="utf-8") as md:
            md.write(f"# 小星的聊天总结 - {date}\n\n")
            md.write(f"**情绪倾向：** {entry.get('emotion', '未知')}\n\n")
            md.write(f"**摘要内容：**\n{entry['summary']}\n")

    print(f"✅ 已导出 {len(summaries)} 个 markdown 文件")

def generate_summary_charts():
    if not os.path.exists(SUMMARY_LOG_PATH):
        print("⚠️ 无法生成图表：summary_log.json 不存在")
        return

    with open(SUMMARY_LOG_PATH, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    # 情绪柱状图
    emotions = [entry["emotion"] for entry in summaries if entry["emotion"]]
    counter = Counter(emotions)

    plt.figure(figsize=(8, 4))
    plt.bar(counter.keys(), counter.values())
    plt.title("聊天情绪统计 - 小星")
    plt.xlabel("情绪类别")
    plt.ylabel("出现次数")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_OUTPUT_DIR, "emotion_bar_chart.png"))

    # 摘要词云图
    all_text = " ".join(entry["summary"] for entry in summaries)
    wordcloud = WordCloud(
        width=WORD_CLOUD_WIDTH,
        height=WORD_CLOUD_HEIGHT,
        background_color=WORD_CLOUD_COLOR,
        font_path=WORD_FONT_PATH  # 指定中文字体
    ).generate(all_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("小星的聊天关键词云")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_OUTPUT_DIR, "summary_wordcloud.png"))

    print("✅ 情绪柱状图 & 摘要词云图已生成")
