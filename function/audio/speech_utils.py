import os
import platform
import time
import queue
import threading
import re
import html
from datetime import datetime
import subprocess
from edge_tts import Communicate
from config.config import DEFAULT_RATE, DEFAULT_STYLE, DEFAULT_VOICE, DEFAULT_VOLUME, AUDIO_DIR, MIN_AUDIO_FILE_SIZE
from function.audio.speech_logger import log_speech_to_db

speak_queue = queue.Queue()

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
            except Exception as e:
                print(f"[❌ 播放出错] {e}")
            speak_queue.task_done()
    threading.Thread(target=worker, daemon=True).start()

_start_speak_worker()

def build_ssml(text, voice, style, rate, volume):
    return f"""
        <speak version='1.0' xml:lang='zh-CN'>
        <voice name='{voice}' style='{style}'>
            <prosody rate='{rate}' volume='{volume}'>{text}</prosody>
        </voice>
        </speak>
        """

async def speak(text: str, voice=DEFAULT_VOICE, style=DEFAULT_STYLE, rate=DEFAULT_RATE, volume=DEFAULT_VOLUME, remove_brackets=True):
    original_text = text.strip()
    if remove_brackets:
        cleaned_text = re.sub(r"[{}]", "", original_text)
    else:
        cleaned_text = original_text

    safe_text = html.escape(cleaned_text)
    print(f"[🗣️ 合成语音] {cleaned_text}")

    try:
        ssml_text = build_ssml(safe_text, voice, style, rate, volume)
        os.makedirs(AUDIO_DIR, exist_ok=True)
        filename = f"output_{int(time.time() * 1000)}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

        communicate = Communicate(cleaned_text, voice=voice)
        await communicate.save(output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) < MIN_AUDIO_FILE_SIZE:
            print("⚠️ 合成失败或音频过小，自动跳过")
            return

        log_speech_to_db(cleaned_text, output_path)
        speak_queue.put(output_path)
        print(f"[✅ 合成完成] 入队播放：{output_path}")

    except Exception as e:
        print("[❌ 语音合成出错]", e)
