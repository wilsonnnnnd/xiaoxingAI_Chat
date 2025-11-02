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
import shutil
import importlib
import ctypes

speak_queue = queue.Queue()
active_players = []


def _ensure_vlc_loaded(candidate_paths=None):
    try:
        import vlc
        return vlc
    except Exception:
        pass

    if candidate_paths is None:
        candidate_paths = []
    env_vlc = os.environ.get('VLC_PATH')
    if env_vlc:
        candidate_paths.append(env_vlc)
    pf = os.environ.get('ProgramFiles')
    pf86 = os.environ.get('ProgramFiles(x86)')
    if pf:
        candidate_paths.append(os.path.join(pf, 'VideoLAN', 'VLC'))
    if pf86:
        candidate_paths.append(os.path.join(pf86, 'VideoLAN', 'VLC'))
    candidate_paths.append(r'E:\Program Files (x86)\VideoLAN\VLC')

    for cand in candidate_paths:
        try:
            if not cand or not os.path.isdir(cand):
                continue
            try:
                if hasattr(os, 'add_dll_directory'):
                    os.add_dll_directory(cand)
            except Exception:
                pass
            try:
                import vlc
                return vlc
            except Exception:
                dll_path = os.path.join(cand, 'libvlc.dll')
                if os.path.exists(dll_path):
                    try:
                        ctypes.CDLL(dll_path)
                        import vlc
                        return vlc
                    except Exception:
                        pass
        except Exception:
            pass
    raise ImportError('python-vlc / libvlc not found')


def _player_cleaner():
    while True:
        try:
            for p in list(active_players):
                try:
                    if hasattr(p, 'get_state'):
                        try:
                            import vlc as _vlc
                            state = p.get_state()
                            if state in (_vlc.State.Ended, _vlc.State.Error, _vlc.State.Stopped):
                                active_players.remove(p)
                                continue
                        except Exception:
                            pass
                    if hasattr(p, 'is_playing'):
                        try:
                            if not p.is_playing():
                                active_players.remove(p)
                                continue
                        except Exception:
                            try:
                                active_players.remove(p)
                            except ValueError:
                                pass
                except Exception:
                    try:
                        active_players.remove(p)
                    except ValueError:
                        pass
            time.sleep(2)
        except Exception:
            time.sleep(2)


def _start_speak_worker():
    def worker():
        while True:
            audio_path = speak_queue.get()
            if not audio_path:
                continue
            try:
                system = platform.system()
                if system == 'Windows':
                    # 1) python-vlc
                    try:
                        vlc = _ensure_vlc_loaded()
                        instance = vlc.Instance('--intf', 'dummy', '--no-video')
                        media = instance.media_new(audio_path)
                        player = instance.media_player_new()
                        player.set_media(media)
                        player.play()
                        active_players.append(player)
                        continue
                    except Exception as e_vlc:
                            pass

                    # 2) pydub + simpleaudio
                    try:
                        from pydub import AudioSegment
                        import simpleaudio as sa
                        seg = AudioSegment.from_file(audio_path)
                        play_obj = sa.play_buffer(seg.raw_data, seg.channels, seg.sample_width, seg.frame_rate)
                        active_players.append(play_obj)
                        continue
                    except Exception as e_pa:
                            pass

                    # 3) ffplay / mpv
                    try:
                        ffplay = shutil.which('ffplay')
                        mpv = shutil.which('mpv')
                        if ffplay:
                            subprocess.Popen([ffplay, '-nodisp', '-autoexit', '-loglevel', 'quiet', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            continue
                        elif mpv:
                            subprocess.Popen([mpv, '--no-terminal', '--really-quiet', '--idle=no', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            continue
                    except Exception as e_ff:
                            pass

                    # fallback: os.startfile
                    try:
                        os.startfile(audio_path)
                    except Exception:
                        subprocess.Popen(f'start "" "{audio_path}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                elif system == 'Darwin':
                    subprocess.Popen(['afplay', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    try:
                        subprocess.Popen(['mpg123', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except FileNotFoundError:
                        ffplay = shutil.which('ffplay')
                        mpv = shutil.which('mpv')
                        if ffplay:
                            subprocess.Popen([ffplay, '-nodisp', '-autoexit', '-loglevel', 'quiet', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif mpv:
                            subprocess.Popen([mpv, '--no-terminal', '--really-quiet', '--idle=no', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            subprocess.Popen(['xdg-open', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                    pass
            finally:
                speak_queue.task_done()

    threading.Thread(target=_player_cleaner, daemon=True).start()
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
