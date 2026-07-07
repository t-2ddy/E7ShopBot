import asyncio
import io
import re
import sys
import win32gui
from PIL import ImageGrab
import winsdk.windows.media.ocr as wocr
import winsdk.windows.graphics.imaging as wgi
import winsdk.windows.storage.streams as wss

WINDOW_TITLE = "Epic Seven"
WINDOW_CLASS = "GLFW30"


async def main():
    hwnd = win32gui.FindWindow(WINDOW_CLASS, WINDOW_TITLE)
    if not hwnd:
        print(f"ERROR: window not found (class={WINDOW_CLASS!r}, title={WINDOW_TITLE!r})")
        sys.exit(1)

    cl, ct = win32gui.ClientToScreen(hwnd, (0, 0))
    _, _, cw, ch = win32gui.GetClientRect(hwnd)
    mid_x = cl + cw // 2

    img = ImageGrab.grab(bbox=(mid_x, ct, cl + cw, ct + ch))
    img.save("capture.png")
    print("Screenshot saved to capture.png")

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

    text = re.sub(r'[0-9]', '', result.text)
    text = re.sub(r'\s+', ' ', text).strip()
    print(text)


asyncio.run(main())
