import threading
import time
import schedule
from datetime import datetime
from config.config import SPEECH_REPORT_SCHEDULE_TIME, SUMMARY_SCHEDULE_TIME
from function.summary.summary_manager import summarize_and_store
from function.audio.speech_reporter import generate_speech_report


def start_summary_scheduler_thread(chat_history: list[str]):
    """
    启动每日聊天摘要调度线程（默认每天定时执行一次）
    """
    def run_summary():
        try:
            if len(chat_history) >= 5:
                summary = summarize_and_store(chat_history)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 已完成今日聊天摘要\n{summary}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 今日对话较少，跳过总结")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 总结执行失败: {e}")

    def loop():
        schedule.every().day.at(SUMMARY_SCHEDULE_TIME).do(run_summary)
        print(f"🕓 已启动每日聊天摘要线程（每天 {SUMMARY_SCHEDULE_TIME}）")
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"[总结调度器错误] {e}")
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()


def start_speech_report_scheduler_thread():
    """
    启动每日语音报告调度线程（默认每天定时执行一次）
    """
    def loop():
        schedule.every().day.at(SPEECH_REPORT_SCHEDULE_TIME).do(generate_speech_report)
        print(f"🕓 已启动每日语音报告线程（每天 {SPEECH_REPORT_SCHEDULE_TIME}）")
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"[语音报告调度器错误] {e}")
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()
