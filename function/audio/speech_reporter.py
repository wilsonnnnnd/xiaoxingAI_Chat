import os
import json
from datetime import datetime
from collections import Counter
import re
import matplotlib.pyplot as plt
from config.config import LOG_SPEECH_PATH, AUDIO_DIR, MARKDOWN_DIR, MAX_AUDIO_FILES
from function.audio.stopwords import STOP_WORDS

os.makedirs(MARKDOWN_DIR, exist_ok=True)

def generate_speech_report():
    if not os.path.exists(LOG_SPEECH_PATH):
        print("❌ 没有找到日志文件，跳过统计。")
        return

    with open(LOG_SPEECH_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    word_counter = Counter()
    date_map = {}

    for line in lines:
        try:
            entry = json.loads(line)
            text = entry.get("text", "")
            timestamp = entry.get("timestamp", "")
            date = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")
            path = entry.get("path", "")
            words = re.findall(r'\w+', text)
            for word in words:
                if word not in STOP_WORDS:
                    word_counter[word] += 1

            if date not in date_map:
                date_map[date] = []
            date_map[date].append(f"- {timestamp.split('T')[1]}：{text}")
        except Exception as e:
            print("❌ 日志格式异常：", e)

    # 关键词柱状图
    top_words = word_counter.most_common(10)
    if top_words:
        words, counts = zip(*top_words)
        plt.figure(figsize=(8, 4))
        plt.bar(words, counts)
        plt.title("语音关键词统计（Top 10）")
        plt.xlabel("关键词")
        plt.ylabel("出现次数")
        plt.tight_layout()
        plt.savefig("memory/speak_keywords_bar.png")
        print("✅ 已生成关键词统计图：memory/speak_keywords_bar.png")

    # 按日期生成 markdown 文件
    for date, items in date_map.items():
        md_path = os.path.join(MARKDOWN_DIR, f"{date}.md")
        with open(md_path, "w", encoding="utf-8") as md:
            md.write(f"# 小星语音记录 - {date}\n\n")
            md.write("\n".join(items))
        print(f"✅ 已生成：{md_path}")

    # 自动清理旧音频
    if os.path.exists(AUDIO_DIR):
        audio_files = sorted(
            [f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")],
            key=lambda f: os.path.getmtime(os.path.join(AUDIO_DIR, f))
        )
        if len(audio_files) > MAX_AUDIO_FILES:
            files_to_delete = audio_files[:-MAX_AUDIO_FILES]
            for f in files_to_delete:
                try:
                    os.remove(os.path.join(AUDIO_DIR, f))
                except Exception as e:
                    print("❌ 删除失败：", f, e)
            print(f"🧹 已清理 {len(files_to_delete)} 个旧音频文件")
