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
    capture region. Coordinates calibrated via test_buy.py.
    """
    _, _, _, ch = win32gui.GetClientRect(hwnd)

    rect = item_line.words[0].bounding_rect
    item_center_y = rect.y + rect.height / 2
    ry = item_center_y / ch - 0.01

    post_click_rel(hwnd, config.BUY_BUTTON_RX, ry)
    await asyncio.sleep(config.DELAY_CLICK)
    post_click_rel(hwnd, *config.COORD_BUY_CONFIRM)
    await asyncio.sleep(config.DELAY_AFTER_BUY)


async def do_scroll(hwnd: int) -> None:
    """Scroll the shop item list down two pages."""
    scroll_down(hwnd)
    scroll_down(hwnd)
    await asyncio.sleep(config.DELAY_AFTER_SCROLL)
