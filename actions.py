import asyncio
from typing import Optional

import win32gui
import winsdk.windows.media.ocr as wocr

import config
from input import post_click_rel, scroll_down


async def do_refresh(hwnd: int) -> None:
    """Click the shop Refresh button then confirm the dialog."""
    post_click_rel(hwnd, *config.COORD_REFRESH)
    await asyncio.sleep(config.DELAY_CLICK)
    post_click_rel(hwnd, *config.COORD_REFRESH_CONFIRM)
    await asyncio.sleep(config.DELAY_AFTER_REFRESH)


async def do_buy(hwnd: int, item_line: wocr.OcrLine) -> None:
    """Click the in-game Buy button for the given item row, then confirm.

    The Buy button sits at a fixed relative X (BUY_BUTTON_RX) but at the same
    relative Y as the item text row. That Y is derived from the OcrLine's
    bounding_rect, which is in pixels relative to the top-left of the OCR
    capture region.

    TODO — Calibrate BUY_BUTTON_RX:
        1. Take a screenshot of the shop with a target item visible.
        2. Note the pixel X of the item's Buy button and the client width.
        3. Set BUY_BUTTON_RX = button_pixel_x / client_width in config.py.
        The current placeholder (0.88) is an estimate; it may need adjustment.

    TODO — OCR region must be full client area (rx1=0, ry1=0, rx2=1, ry2=1):
        bounding_rect coordinates are pixel offsets from the top-left corner of
        the captured image. If the OCR region is the full client area, these
        pixels map directly to client coords, so the division by client_height
        below is valid. If the region is a sub-region, add the region's top-left
        offset before dividing.
    """
    _, _, _, ch = win32gui.GetClientRect(hwnd)

    rect = item_line.bounding_rect
    item_center_y = rect.y + rect.height / 2
    ry = item_center_y / ch

    post_click_rel(hwnd, config.BUY_BUTTON_RX, ry)
    await asyncio.sleep(config.DELAY_CLICK)
    post_click_rel(hwnd, *config.COORD_BUY_CONFIRM)
    await asyncio.sleep(config.DELAY_AFTER_BUY)


async def do_scroll(hwnd: int) -> None:
    """Scroll the shop item list down one page."""
    scroll_down(hwnd)
    await asyncio.sleep(config.DELAY_AFTER_SCROLL)
