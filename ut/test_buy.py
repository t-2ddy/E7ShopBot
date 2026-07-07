import asyncio
import sys

import win32gui

from config import WINDOW_CLASS, WINDOW_TITLE, OCR_RX1, OCR_RY1, OCR_RX2, OCR_RY2
from ocr import _capture_window, ocr_region, find_items
from input import post_click_rel

TARGET = "friendship points"
BUY_RX = 0.9


async def main() -> None:
    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        sys.exit(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")

    img = _capture_window(hwnd, OCR_RX1, OCR_RY1, OCR_RX2, OCR_RY2)
    img.save("capture.png")
    print("Screenshot saved to capture.png")

    print("Running OCR scan...")
    result = await ocr_region(hwnd, OCR_RX1, OCR_RY1, OCR_RX2, OCR_RY2)
    found = find_items(result, [TARGET])
    item_line = found[TARGET]

    if item_line is None:
        print(f"'{TARGET}' not found.")
        return

    print(f"Found '{TARGET}': {item_line.text!r}")
    _, _, _, ch = win32gui.GetClientRect(hwnd)
    rect = item_line.words[0].bounding_rect
    ry = (rect.y + rect.height / 2) / ch - 0.01

    print(f"Clicking at rx={BUY_RX}, ry={ry:.4f}")
    post_click_rel(hwnd, BUY_RX, ry)


asyncio.run(main())
