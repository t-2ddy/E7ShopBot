import asyncio

import config
from actions import do_buy, do_refresh, do_scroll
from ocr import find_items, ocr_region


async def _check_and_buy(hwnd: int, already_bought: set[str]) -> None:
    """Run OCR on the shop and buy any found items not already purchased this cycle.

    already_bought is mutated in-place: each keyword bought here is added so it
    won't be attempted again in a subsequent check within the same refresh cycle.
    """
    result = await ocr_region(
        hwnd,
        config.OCR_RX1, config.OCR_RY1,
        config.OCR_RX2, config.OCR_RY2,
    )
    found = find_items(result, config.ITEM_KEYWORDS)

    matched = {k: v for k, v in found.items() if v is not None}
    if not matched:
        return

    # Buy in keyword priority order; skip anything already bought this cycle
    for keyword in config.ITEM_KEYWORDS:
        if keyword in matched and keyword not in already_bought:
            print(f"[loop] buying: {keyword}")
            await do_buy(hwnd, matched[keyword])
            already_bought.add(keyword)


async def run_loop(hwnd: int) -> None:
    """Main shop refresh loop.

    Flow every cycle:
      1. Refresh the shop.
      2. OCR check top half — buy any found items.
      3. Scroll down.
      4. OCR check bottom half — buy any found items.
      5. Go back to step 1.

    Press Q or Ctrl+C to stop.
    """
    print("[loop] starting")
    try:
        while True:
            print("[loop] refreshing shop")
            await do_refresh(hwnd)
            bought_this_cycle: set[str] = set()

            await _check_and_buy(hwnd, bought_this_cycle)

            print("[loop] scrolling to check bottom")
            await do_scroll(hwnd)

            await _check_and_buy(hwnd, bought_this_cycle)

    except asyncio.CancelledError:
        print("[loop] cancelled")
    except KeyboardInterrupt:
        print("[loop] stopped by user")
