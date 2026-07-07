import asyncio
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import win32gui
import winsdk.windows.graphics.imaging as wgi
import winsdk.windows.media.ocr as wocr
import winsdk.windows.storage.streams as wss

from ocr import _capture_window

WINDOW_CLASS = "GLFW30"
WINDOW_TITLE = "Epic Seven"

# Crop region covering the gold number at the top center.
# rx2 is set to cut off before the blue gem icon to the right.
# Tune these after inspecting capture_gold.png:
#   - lower rx2 if the gem number leaks in
#   - lower rx1 if the gold number is clipped on the left
RX1, RY1, RX2, RY2 = 0.50, 0.05, 0.70, 0.13


async def main() -> None:
    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        sys.exit(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")

    img = _capture_window(hwnd, RX1, RY1, RX2, RY2)
    img.save("capture_gold.png")
    print("Screenshot saved to capture_gold.png")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = bytearray(buf.getvalue())

    stream = wss.InMemoryRandomAccessStream()
    writer = wss.DataWriter(stream.get_output_stream_at(0))
    writer.write_bytes(png_bytes)
    await writer.store_async()
    stream.seek(0)

    decoder = await wgi.BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    if bitmap.bitmap_pixel_format != wgi.BitmapPixelFormat.BGRA8:
        bitmap = wgi.SoftwareBitmap.convert(bitmap, wgi.BitmapPixelFormat.BGRA8)

    engine = wocr.OcrEngine.try_create_from_user_profile_languages()
    result = await engine.recognize_async(bitmap)

    raw = result.text.strip()
    print(f"OCR raw: {raw!r}")

    # Strip thousands separators and grab the first digit run
    normalized = re.sub(r"[,.]", "", raw)
    match = re.search(r"\d+", normalized)
    if match:
        print(f"Gold: {int(match.group())}")
    else:
        print("Gold: not found")


asyncio.run(main())
