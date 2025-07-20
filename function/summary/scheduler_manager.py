import threading
import time
import schedule
from function.summary.summary_manager import summarize_and_store
from function.audio.speech_reporter import generate_speech_report


def start_summary_scheduler_thread(chat_history):
    """
    启动每日聊天摘要调度线程（每天23:00自动执行）
    """
    def loop():
        schedule.every().day.at("23:00").do(lambda: summarize_and_store(chat_history))
        print("🕓 已启动每日聊天摘要线程（每天23:00）")
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"[总结日志调度器错误] {e}")
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()


def start_speech_report_scheduler_thread():
    """
    启动每日语音报告调度线程（每天23:30自动执行）
    """
    def loop():
        schedule.every().day.at("23:30").do(generate_speech_report)
        print("🕓 已启动每日语音报告线程（每天23:30）")
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"[语音报告调度器错误] {e}")
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()
