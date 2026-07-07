import msvcrt
import sys
import time

import win32gui

sys.path.insert(0, "..")
from config import WINDOW_CLASS, WINDOW_TITLE
from input import scroll_down


if __name__ == "__main__":
    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        print(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")
        sys.exit(1)

    print("Scrolling down every 3 seconds. Press Q to stop.")

    while True:
        scroll_down(hwnd)
        print("scroll_down sent")

        for _ in range(30):
            time.sleep(0.1)
            if msvcrt.kbhit() and msvcrt.getwch().lower() == "q":
                print("Stopped.")
                sys.exit(0)
