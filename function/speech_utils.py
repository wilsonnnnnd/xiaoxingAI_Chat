import re
import html
import os
import platform
import time
from edge_tts import Communicate

def build_ssml(text, voice, style, rate, volume):
    return f"""
<speak version='1.0' xml:lang='zh-CN'>
  <voice name='{voice}' style='{style}'>
    <prosody rate='{rate}' volume='{volume}'>{text}</prosody>
  </voice>
</speak>
"""

async def speak(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    style: str = "friendly",
    rate: str = "0%",
    volume: str = "0dB",
    remove_brackets: bool = True
):
    original_text = text.strip()
    if remove_brackets:
        cleaned_text = re.sub(r"[{}]", "", original_text)
    else:
        cleaned_text = original_text

    safe_text = html.escape(cleaned_text)

    print("\n[🗣️ 合成语音（SSML 模式）]")
    print(f"Voice  : {voice}")
    print(f"Style  : {style}")
    print(f"Rate   : {rate}")
    print(f"Volume : {volume}")
    print(f"Text   : {cleaned_text}")
    print("-" * 40)

    try:
        # 构建 SSML 文本
        ssml_text = build_ssml(safe_text, voice, style, rate, volume)

        # 自动生成唯一音频文件名
        output_dir = "memory/audio"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"output_{int(time.time() * 1000)}.mp3"
        output_path = os.path.join(output_dir, filename)

        # 使用 SSML 合成（不需要 ssml=True）
        communicate = Communicate(ssml_text, voice=voice)
        await communicate.save(output_path)

        # 播放语音
        if platform.system() == "Windows":
            os.system(f'start {output_path}')
        elif platform.system() == "Darwin":
            os.system(f'afplay {output_path}')
        else:
            os.system(f'mpg123 {output_path}')
    except Exception as e:
        print("[语音合成出错]", e)
