import win32gui


def cb(hwnd, _):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if "Epic Seven" in title:
            cls = win32gui.GetClassName(hwnd)
            print(f"hwnd=0x{hwnd:08X}  title={title!r}  class={cls!r}")


win32gui.EnumWindows(cb, None)
