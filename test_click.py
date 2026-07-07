import time
import sys
import win32gui
import win32api

WM_MOUSEMOVE    = 0x0200
WM_LBUTTONDOWN  = 0x0201
WM_LBUTTONUP    = 0x0202
WM_LBUTTONDBLCLK = 0x0203
MK_LBUTTON      = 0x0001

# TODO: fill in the exact title and class name from find_window.py output
WINDOW_TITLE = "Epic Seven"
WINDOW_CLASS = "GLFW30"


def post_click(hwnd, sx, sy):
    cx, cy = win32gui.ScreenToClient(hwnd, (sx, sy))
    lparam = (cy << 16) | (cx & 0xFFFF)
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.075)
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, lparam)
    print(f"post_click: WM_LBUTTONDOWN + WM_LBUTTONUP sent to client ({cx}, {cy})")


def post_click_rel(hwnd, rx, ry):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    cx = int(rx * (right - left))
    cy = int(ry * (bottom - top))
    lparam = (cy << 16) | (cx & 0xFFFF)
    win32api.PostMessage(hwnd, WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.025)
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.075)
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, lparam)
    print(f"post_click_rel({rx}, {ry}): sent to client ({cx}, {cy})")


def post_click_extended(hwnd, sx, sy):
    cx, cy = win32gui.ScreenToClient(hwnd, (sx, sy))
    lparam = (cy << 16) | (cx & 0xFFFF)
    win32api.PostMessage(hwnd, WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.025)
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.075)
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, lparam)
    time.sleep(0.075)
    win32api.PostMessage(hwnd, WM_LBUTTONDBLCLK, MK_LBUTTON, lparam)
    time.sleep(0.075)
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, lparam)
    print(f"post_click_extended: WM_MOUSEMOVE + DOWN + UP + DBLCLK + UP sent to client ({cx}, {cy})")


if __name__ == "__main__":
    import msvcrt

    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        print(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")
        sys.exit(1)

    print("Looping clicks every 4 seconds. Press Q to stop.")

    while True:
        post_click_rel(hwnd, 0.2, 0.9)
        #.6, .65 - refresh confirm
        #.6, .7 - buy
        #.2, .9 - refresh

        for _ in range(40):
            time.sleep(0.1)
            if msvcrt.kbhit() and msvcrt.getwch().lower() == "q":
                print("Stopped.")
                sys.exit(0)
