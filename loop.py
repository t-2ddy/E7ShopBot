import asyncio

import config
from actions import do_buy, do_refresh, do_scroll
from ocr import find_items, ocr_region


async def _check_and_buy(hwnd: int) -> bool:
    """Run OCR on the shop, buy any found items, and return whether anything was bought."""
    result = await ocr_region(
        hwnd,
        config.OCR_RX1, config.OCR_RY1,
        config.OCR_RX2, config.OCR_RY2,
    )
    found = find_items(result, config.ITEM_KEYWORDS)

    matched = {k: v for k, v in found.items() if v is not None}
    if not matched:
        return False

    # Buy in keyword priority order (mystic medal before covenant bookmark)
    for keyword in config.ITEM_KEYWORDS:
        if keyword in matched:
            print(f"[loop] buying: {keyword}")
            await do_buy(hwnd, matched[keyword])

    return True


async def run_loop(hwnd: int) -> None:
    """Main shop refresh loop.

    Flow:
      1. Refresh the shop.
      2. OCR check — if item(s) found, buy them, then re-check (step 2).
      3. If none found, scroll down and OCR check again.
      4. If still none after scroll, go back to step 1 (refresh).

    Press Ctrl+C to stop.
    """
    print("[loop] starting — press Ctrl+C to stop")
    try:
        while True:
            print("[loop] refreshing shop")
            await do_refresh(hwnd)

            # First check (top of shop list)
            bought = await _check_and_buy(hwnd)
            if bought:
                # Re-check top of list; items may have shifted after a purchase
                continue

            # Scroll and check bottom of list
            print("[loop] nothing found at top — scrolling")
            await do_scroll(hwnd)

            bought = await _check_and_buy(hwnd)
            if bought:
                continue

            # Nothing in entire shop — loop back to refresh
            print("[loop] nothing found — refreshing")

    except asyncio.CancelledError:
        print("[loop] cancelled")
    except KeyboardInterrupt:
        print("[loop] stopped by user")
