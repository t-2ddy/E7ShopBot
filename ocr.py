import io
from typing import Optional

import win32gui
from PIL import ImageGrab
import winsdk.windows.graphics.imaging as wgi
import winsdk.windows.media.ocr as wocr
import winsdk.windows.storage.streams as wss


async def ocr_region(
    hwnd: int,
    rx1: float, ry1: float,
    rx2: float, ry2: float,
) -> wocr.OcrResult:
    """Capture a client-relative sub-region and run Windows OCR on it.

    Coordinates are fractions of the client area (0.0–1.0).
    Returns a raw OcrResult whose .lines carry .text and .bounding_rect.
    """
    cl, ct = win32gui.ClientToScreen(hwnd, (0, 0))
    _, _, cw, ch = win32gui.GetClientRect(hwnd)

    x1 = cl + int(rx1 * cw)
    y1 = ct + int(ry1 * ch)
    x2 = cl + int(rx2 * cw)
    y2 = ct + int(ry2 * ch)

    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

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
    return await engine.recognize_async(bitmap)


def find_items(
    result: wocr.OcrResult,
    keywords: list[str],
) -> dict[str, Optional[wocr.OcrLine]]:
    """Scan OCR result lines for each keyword (case-insensitive).

    Returns a dict mapping each keyword to its matching OcrLine, or None if not
    found. The OcrLine carries a .bounding_rect used to locate the Buy button.
    """
    found: dict[str, Optional[wocr.OcrLine]] = {k: None for k in keywords}
    for line in result.lines:
        text_lower = line.text.lower()
        for keyword in keywords:
            if found[keyword] is None and keyword in text_lower:
                found[keyword] = line
    return found
