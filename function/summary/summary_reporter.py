import os
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from config.config import CHART_OUTPUT_DIR, MARKDOWN_DIR, WORD_CLOUD_COLOR, WORD_CLOUD_HEIGHT, WORD_CLOUD_WIDTH, WORD_FONT_PATH
from function.summary.summary_db import SummaryDB

def export_summaries_to_markdown():
    db = SummaryDB()
    summaries = db.load_all()
    db.close()

    os.makedirs(MARKDOWN_DIR, exist_ok=True)
    for entry in summaries:
        date = entry["date"]
        md_path = os.path.join(MARKDOWN_DIR, f"{date}.md")
        with open(md_path, "w", encoding="utf-8") as md:
            md.write(f"# 小星的聊天总结 - {date}\n\n")
            md.write(f"**情绪倾向：** {entry.get('emotion', '未知')}\n\n")
            md.write(f"**摘要内容：**\n{entry['summary']}\n")

    print(f"✅ 已导出 {len(summaries)} 个 markdown 文件")

def generate_summary_charts():
    db = SummaryDB()
    summaries = db.load_all()
    db.close()

    emotions = [entry["emotion"] for entry in summaries if entry["emotion"]]
    counter = Counter(emotions)

    plt.figure(figsize=(8, 4))
    plt.bar(counter.keys(), counter.values())
    plt.title("聊天情绪统计 - 小星")
    plt.xlabel("情绪类别")
    plt.ylabel("出现次数")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_OUTPUT_DIR, "emotion_bar_chart.png"))

    all_text = " ".join(entry["summary"] for entry in summaries)
    wordcloud = WordCloud(
        width=WORD_CLOUD_WIDTH,
        height=WORD_CLOUD_HEIGHT,
        background_color=WORD_CLOUD_COLOR,
        font_path=WORD_FONT_PATH
    ).generate(all_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("小星的聊天关键词云")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_OUTPUT_DIR, "summary_wordcloud.png"))

    print("✅ 情绪柱状图 & 摘要词云图已生成")
