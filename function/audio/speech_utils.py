
import re
import html
import os
import platform
import time
import queue
import threading
import json
from datetime import datetime
from edge_tts import Communicate
from config.config import DEFAULT_RATE, DEFAULT_STYLE, DEFAULT_VOICE, DEFAULT_VOLUME, LOG_SPEECH_PATH, AUDIO_DIR, MIN_AUDIO_FILE_SIZE
import subprocess

# 音频播放队列（用于防止多段语音重叠）
speak_queue = queue.Queue()

# 启动独立线程用于串行播放语音
def _start_speak_worker():
    def worker():
        while True:
            audio_path = speak_queue.get()
            if not audio_path:
                continue
            try:
                if platform.system() == "Windows":
                    subprocess.run(["start", "", audio_path], shell=True)
                elif platform.system() == "Darwin":
                    subprocess.run(["afplay", audio_path])
                else:
                    subprocess.run(["mpg123", audio_path])
                print(f"[🔊 播放完成] {audio_path}")
            except Exception as e:
                print(f"[❌ 播放出错] {e}")
            speak_queue.task_done()

    threading.Thread(target=worker, daemon=True).start()


# 启动线程
_start_speak_worker()

def build_ssml(text, voice, style, rate, volume):
    """
    构建标准 SSML 字符串
    """
    return f"""
<speak version='1.0' xml:lang='zh-CN'>
  <voice name='{voice}' style='{style}'>
    <prosody rate='{rate}' volume='{volume}'>{text}</prosody>
  </voice>
</speak>
"""

def log_speech_playback(text: str, audio_path: str):
    """
    写入语音播放日志到 JSONL 文件
    """
    entry = {
        "text": text,
        "path": audio_path,
        "timestamp": datetime.now().isoformat()
    }
    with open(LOG_SPEECH_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

async def speak(
    text: str,
    voice: str = DEFAULT_VOICE,
    style: str = DEFAULT_STYLE,
    rate: str = DEFAULT_RATE,
    volume: str = DEFAULT_VOLUME,
    remove_brackets: bool = True
):
    """
    使用 edge-tts 合成语音并排入播放队列
    """
    original_text = text.strip()

    # 可选去除括号内容（如 {你好吗} -> 你好吗）
    if remove_brackets:
        cleaned_text = re.sub(r"[{}]", "", original_text)
    else:
        cleaned_text = original_text

    # HTML 转义，防止非法字符影响 SSML
    safe_text = html.escape(cleaned_text)

    print("\n[🗣️ 合成语音（SSML 模式）]")
    print(f"Voice  : {voice}")
    print(f"Style  : {style}")
    print(f"Rate   : {rate}")
    print(f"Volume : {volume}")
    print(f"Text   : {cleaned_text}")
    print("-" * 40)

    try:
        ssml_text = build_ssml(safe_text, voice, style, rate, volume)
        os.makedirs(AUDIO_DIR, exist_ok=True)
        filename = f"output_{int(time.time() * 1000)}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

        communicate = Communicate(ssml_text, voice=voice)
        await communicate.save(output_path)

        if not os.path.exists(output_path):
            print("❌ 合成失败：音频文件未生成")
            return

        file_size = os.path.getsize(output_path)
        if file_size < MIN_AUDIO_FILE_SIZE:
            print(f"⚠️ 检测到音频文件异常（仅 {file_size} 字节），自动删除：{output_path}")
            os.remove(output_path)
            return

        print(f"[✅ 合成完成] 文件大小：{file_size} 字节 -> 入队播放：{output_path}")
        log_speech_playback(cleaned_text, output_path)
        speak_queue.put(output_path)

    except Exception as e:
        print("[❌ 语音合成出错]", e)