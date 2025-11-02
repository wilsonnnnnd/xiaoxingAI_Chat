import pyautogui
import time
import random

while True:
    # 随机生成水平和垂直方向的移动量（-50 到 50 像素）
    dx = random.randint(-50, 50)
    dy = random.randint(-50, 50)

    pyautogui.move(dx, dy, duration=0.2)  # 0.2 秒内移动到新位置
    print(f"Moved mouse by ({dx}, {dy})")

    # 随机等待 1 到 10 秒之间的时间
    sleep_time = random.randint(1, 10)
    time.sleep(sleep_time)
