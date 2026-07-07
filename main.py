import asyncio
import msvcrt
import sys
import time

import win32gui

from config import WINDOW_CLASS, WINDOW_TITLE
from loop import run_loop


def _wait_for_q() -> None:
    """Block in a thread until Q is pressed."""
    while True:
        if msvcrt.kbhit() and msvcrt.getwch().lower() == "q":
            return
        time.sleep(0.05)


async def _run(hwnd: int) -> None:
    loop_task = asyncio.create_task(run_loop(hwnd))
    quit_future = asyncio.get_event_loop().run_in_executor(None, _wait_for_q)

    done, pending = await asyncio.wait(
        [loop_task, quit_future],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    if quit_future in done:
        print("[main] Q pressed — stopping")


def main() -> None:
    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        sys.exit(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")
    print(f"Found window: hwnd={hwnd}")
    print("Press Q to stop.")
    asyncio.run(_run(hwnd))


if __name__ == "__main__":
    main()
