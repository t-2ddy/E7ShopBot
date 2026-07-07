WINDOW_CLASS = "GLFW30"
WINDOW_TITLE = "Epic Seven"

# Click coordinates (relative, 0.0–1.0 of client area)
COORD_REFRESH         = (0.2,  0.9)
COORD_REFRESH_CONFIRM = (0.6,  0.65)
COORD_BUY_CONFIRM     = (0.6,  0.7)

# X position of the in-game Buy button to the right of each item row.
# TODO: calibrate from a live screenshot — see actions.py do_buy() for details.
BUY_BUTTON_RX = 0.88

# OCR scan region (relative to client area)
OCR_RX1, OCR_RY1 = 0.0, 0.0
OCR_RX2, OCR_RY2 = 1.0, 1.0

# Target item keywords (lowercase); order determines buy priority when both present
ITEM_KEYWORDS = ["mystic medal", "covenant bookmark"]

# Timing (seconds)
DELAY_AFTER_REFRESH = 2.0
DELAY_AFTER_BUY     = 1.0
DELAY_AFTER_SCROLL  = 0.8
DELAY_CLICK         = 0.5
