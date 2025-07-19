import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json

def load_logs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def show_log_ui(filepath):
    logs = load_logs(filepath)

    root = tk.Tk()
    root.title("小星聊天日志")

    text_area = ScrolledText(root, width=100, height=30, font=("Microsoft YaHei", 12))
    text_area.pack()

    for entry in logs:
        text_area.insert(tk.END, f"[{entry['timestamp']}]\n你：{entry['user']}\n小星：{entry['xiaoxing']}\n\n")

    root.mainloop()
