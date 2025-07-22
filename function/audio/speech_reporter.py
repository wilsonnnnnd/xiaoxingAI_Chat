# function/audio/speech_reporter.py
import os
import sqlite3
from collections import Counter
from datetime import datetime
import re
import matplotlib.pyplot as plt
from config.config import DB_PATH, MARKDOWN_DIR, CHART_OUTPUT_DIR
from function.audio.stopwords_db import STOP_WORDS

def generate_speech_report():
    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT text, timestamp FROM speech_log ORDER BY timestamp ASC")
    word_counter = Counter()
    date_map = {}

    for row in cursor.fetchall():
        text = row[0]
        timestamp = row[1]
        date = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")
        words = re.findall(r'\w+', text)
        for word in words:
            if word not in STOP_WORDS:
                word_counter[word] += 1
        date_map.setdefault(date, []).append(f"- {timestamp.split('T')[1]}：{text}")

    conn.close()

    # 关键词柱状图
    if word_counter:
        top_words = word_counter.most_common(10)
        words, counts = zip(*top_words)
        plt.figure(figsize=(8, 4))
        plt.bar(words, counts)
        plt.title("语音关键词统计（Top 10）")
        plt.xlabel("关键词")
        plt.ylabel("出现次数")
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_OUTPUT_DIR, "speech_keyword_bar.png"))
        print("✅ 已生成关键词柱状图")

    # Markdown 语音日志
    for date, items in date_map.items():
        md_path = os.path.join(MARKDOWN_DIR, f"{date}.md")
        with open(md_path, "w", encoding="utf-8") as md:
            md.write(f"# 小星语音记录 - {date}\n\n" + "\n".join(items))
        print(f"✅ 已生成语音日志：{md_path}")
