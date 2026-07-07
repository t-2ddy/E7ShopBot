import asyncio
import sys

import win32gui

from config import WINDOW_CLASS, WINDOW_TITLE
from loop import run_loop


def main() -> None:
    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        sys.exit(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")
    print(f"Found window: hwnd={hwnd}")
    asyncio.run(run_loop(hwnd))


if __name__ == "__main__":
    main()
