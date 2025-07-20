import threading
import time
import schedule
from function.summary_manager import summarize_and_store

def start_summary_scheduler_thread(shared_history: list):
    """
    启动每日23:00自动总结线程，传入主对话历史对象引用
    """
    def run_daily_summary():
        if len(shared_history) >= 5:
            summary = summarize_and_store(shared_history)
            print("\n🧠【自动总结】小星记录了今天的聊天内容～\n", summary)
        else:
            print("\n🧠【自动总结】今天聊天不多，小星就偷懒一下啦～")

    schedule.every().day.at("23:00").do(run_daily_summary)

    def scheduler_loop():
        print("🕓 小星的每日总结线程已启动（每天23:00）")
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()