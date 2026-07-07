import time
import win32api
import win32gui

WM_MOUSEMOVE    = 0x0200
WM_LBUTTONDOWN  = 0x0201
WM_LBUTTONUP    = 0x0202
WM_MOUSEWHEEL   = 0x020A
MK_LBUTTON      = 0x0001

WHEEL_DELTA = 120


def post_click_rel(hwnd: int, rx: float, ry: float) -> None:
    """Click at a position given as fractions of the client area (0.0–1.0).

    Posts WM_MOUSEMOVE first because GLFW ignores lParam coordinates on
    WM_LBUTTONDOWN and uses the last mouse position instead.
    """
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    cx = int(rx * (right - left))
    cy = int(ry * (bottom - top))
    lparam = (cy << 16) | (cx & 0xFFFF)
    win32api.PostMessage(hwnd, WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.025)
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.075)
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, lparam)


def scroll_down(hwnd: int, rx: float = 0.5, ry: float = 0.5, ticks: int = 3) -> None:
    """Scroll the shop list downward using WM_MOUSEWHEEL.

    rx/ry: relative position to aim the wheel event (shop list center).
    ticks: number of WHEEL_DELTA steps; each is one detent of the scroll wheel.

    The wParam high word is the signed delta (negative = scroll down).
    GetClientRect coords are packed into lParam as for a click.
    """
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    cx = int(rx * (right - left))
    cy = int(ry * (bottom - top))
    lparam = (cy << 16) | (cx & 0xFFFF)

    delta = -(WHEEL_DELTA * ticks)
    # wParam: high word = wheel delta, low word = key state (0)
    wparam = (delta & 0xFFFF) << 16
    win32api.PostMessage(hwnd, WM_MOUSEWHEEL, wparam, lparam)
