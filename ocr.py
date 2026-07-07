import ctypes
import io
import re
from typing import Optional

import win32gui
import win32ui
import winsdk.windows.graphics.imaging as wgi
import winsdk.windows.media.ocr as wocr
import winsdk.windows.storage.streams as wss
from PIL import Image

import config

# PW_RENDERFULLCONTENT forces the GPU to render into the bitmap, which is
# required for hardware-accelerated (OpenGL/DX) windows and works across
# all monitors regardless of which display the window is on.
_PW_RENDERFULLCONTENT = 0x2


def _capture_window(hwnd: int, rx1: float, ry1: float, rx2: float, ry2: float) -> Image.Image:
    """Capture a client-relative sub-region via PrintWindow(PW_RENDERFULLCONTENT).

    Works for GPU-rendered windows (e.g. GLFW/OpenGL games) on any monitor,
    unlike ImageGrab.grab() which returns black for such windows.
    """
    _, _, cw, ch = win32gui.GetClientRect(hwnd)

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc  = win32ui.CreateDCFromHandle(hwnd_dc)
    mem_dc  = mfc_dc.CreateCompatibleDC()
    bmp     = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfc_dc, cw, ch)
    mem_dc.SelectObject(bmp)

    ctypes.windll.user32.PrintWindow(hwnd, mem_dc.GetSafeHdc(), _PW_RENDERFULLCONTENT)

    bmp_info = bmp.GetInfo()
    bmp_bits = bmp.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGB",
        (bmp_info["bmWidth"], bmp_info["bmHeight"]),
        bmp_bits, "raw", "BGRX", 0, 1,
    )

    win32gui.DeleteObject(bmp.GetHandle())
    mem_dc.DeleteDC()
    # mfc_dc wraps hwnd_dc (a GetWindowDC handle) — must use ReleaseDC, not DeleteDC
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    cx1 = int(rx1 * cw)
    cy1 = int(ry1 * ch)
    cx2 = int(rx2 * cw)
    cy2 = int(ry2 * ch)
    return img.crop((cx1, cy1, cx2, cy2))


_OCR_SCALE = 3  # upscale factor; small crops need this for accurate digit recognition


def _scale_for_ocr(img: Image.Image, scale: int = _OCR_SCALE) -> Image.Image:
    """Upscale image by `scale`× with LANCZOS for better OCR accuracy."""
    if scale <= 1:
        return img
    return img.resize((img.width * scale, img.height * scale), Image.LANCZOS)


async def ocr_region(
    hwnd: int,
    rx1: float, ry1: float,
    rx2: float, ry2: float,
) -> wocr.OcrResult:
    """Capture a client-relative sub-region and run Windows OCR on it.

    Coordinates are fractions of the client area (0.0–1.0).
    Returns a raw OcrResult whose .lines carry .text and .bounding_rect.
    """
    return await _ocr_image(_capture_window(hwnd, rx1, ry1, rx2, ry2))


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


async def _ocr_image(img: Image.Image) -> wocr.OcrResult:
    """Run Windows OCR on an already-prepared PIL Image."""
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


async def read_gold(hwnd: int) -> Optional[int]:
    """OCR the gold counter at the top of the screen and return it as an int.

    The crop is upscaled before OCR for digit accuracy; bounding rects from
    this result are never used for click positioning, so scaling is safe here.

    Returns None if the region yields no recognisable digit sequence, so callers
    can choose to skip the check rather than halt on a transient misread.
    """
    img = _capture_window(
        hwnd,
        config.GOLD_RX1, config.GOLD_RY1,
        config.GOLD_RX2, config.GOLD_RY2,
    )
    result = await _ocr_image(_scale_for_ocr(img))
    normalized = re.sub(r"[,.]", "", result.text)
    digits = "".join(re.findall(r"\d+", normalized))
    return int(digits) if digits else None
