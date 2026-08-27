# E7 Secret Shop Bot

Windows helper for **Epic Seven** that refreshes the in-game **Secret Shop** and buys **Mystic Medal** / **Covenant Bookmark** when they appear. Clicks and scrolls are posted to the game window, so the real mouse never moves.

[Download the prebuilt](https://drive.google.com/file/d/1bpG2I4HBYqQMVKjS-PAUq3GkNtGKlNnp/view?usp=sharing) `.exe`

## Demo (old version demo, features are still the same)

<img width="426" height="240" alt="490850390-c1134679-fed4-495e-ab40-450e05b199a9" src="https://github.com/user-attachments/assets/3234db06-2272-4a28-9a5a-b52b084e96a2" />


## Quick Start
1) Open epic seven and move to secret shop
2) Open app **AS ADMIN** (because stove opens the game with higher permissions)
3) Set the skystones (and gold) and run the bot

## Important To Note
- **Do not minimize the game** It should be open and the text in the shop should be a "readable" size (about 1/4 or 1/5 screen size is good)
- E7 can be behind other windows or games and run fine
- Try not to run an auto farm in the background, e7 sends large data objects to its servers from your client(game) and on run completions stutters which can interupt the bot


## Requirements

- Windows 10/11 (Win32 messages + Windows OCR)
- Epic Seven running (window title `Epic Seven`, class `GLFW30`)
- Python 3.10+ if running from source

## Setup

```powershell
cd E7ShopBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install customtkinter pywin32 winsdk Pillow
```

There is no `requirements.txt` in the repo; those four packages are the runtime deps (`gui.py` plus OCR/input).

## Run

Leave Epic Seven open (NOT minimized, but on another monitor is fine and behind other windows is okay). Then either launch the downloaded `E7ShopBot.exe`, or:

```powershell
python gui.py
```

1. Set **Skystones to spend**. The app divides by 3 (cost per refresh) and shows **Total refreshes**.
2. If you want the gold safety net, leave **Gold limiter** on and enter **Starting gold**.
3. Hit **Start**. The bot refreshes, OCRs the shop, buys matches, scrolls, and repeats.
4. Hit **Stop** (or close the window) to cancel.

Live stats: refreshes done, purchase counts per item, and a stop reason (refresh limit, gold limit, or user).

CLI (no GUI, no gold/refresh limits; press `Q` to stop):

```powershell
python main.py
```

If the game window is not found, the GUI shows "Window not found" and the CLI exits. Run `python find_window.py` to print visible Epic Seven hwnd / title / class.

### Build the exe

```powershell
pip install pyinstaller
pyinstaller E7ShopBot.spec
```

Output: `dist/E7ShopBot.exe` (windowed, icons from `LuaShakeicon.ico` / `LuaShakeicon.png`).

## How it works

```text
Find Epic Seven hwnd
→ refresh (click + confirm)
→ PrintWindow capture → Windows OCR → keyword match
→ buy (row Y from OCR, confirm) if Mystic Medal / Covenant Bookmark
→ scroll shop list
→ OCR + buy again
→ repeat until refresh limit, gold floor, or Stop
```

- **Clicks/scrolls** (`input.py`): `PostMessage` `WM_MOUSEMOVE` + `WM_LBUTTONDOWN/UP` / `WM_MOUSEWHEEL` to the game hwnd. GLFW uses the last posted mouse position, so the physical cursor is left alone.
- **Capture** (`ocr.py`): `PrintWindow(PW_RENDERFULLCONTENT)` so GPU/OpenGL windows work on any monitor (plain screen grab is black).
- **Buy** (`actions.py`): Buy button X is a fixed relative coord (`BUY_BUTTON_RX`); Y comes from the matched OCR line.
- **Gold** is not read from the screen. You enter a starting amount; each buy subtracts a hardcoded cost. Without the GUI `stats` object (CLI), the gold limiter does nothing.


| Item              | Gold cost |
| ----------------- | --------- |
| Mystic Medal      | 280,000   |
| Covenant Bookmark | 184,000   |


Gold limiter default floor: **300,000**. Toggle it off in the GUI if you don't want that stop.

Tunable coords, delays, keywords, and costs live in `config.py` (all click positions are 0.0–1.0 of the client area).

## Harness scripts

Scripts under `ut/` talk to a live Epic Seven window. Run them from the repo root (`python ut/test_buy.py`).


| Script              | Purpose                                      |
| ------------------- | -------------------------------------------- |
| `find_window.py`    | List visible Epic Seven hwnd / title / class |
| `ut/test_click.py`  | Calibrate relative clicks                    |
| `ut/test_scroll.py` | Repeat `scroll_down` until `Q`               |
| `ut/test_text.py`   | Capture + OCR the right half of the client   |
| `ut/test_buy.py`    | OCR a target row and click its Buy button    |
| `ut/test_gold.py`   | Experiment: crop/OCR the gold readout        |




## Known limitations

- **Windows only** — depends on Win32, Windows OCR, and the GLFW game window.
- **Layout-sensitive** — relative coords assume the Secret Shop UI; unusual resolutions or UI scale may miss buttons.
- **Gold is a local tally** — if Starting gold is wrong, the limiter stop point is wrong too.
- **OCR language** — Windows OCR uses the user profile languages; English shop text is what the keywords expect.
- **Exclusive fullscreen** — the window must be findable as `Epic Seven` / `GLFW30`; use windowed or borderless if FindWindow fails.



## Project layout

```text
gui.py           # CustomTkinter app (primary entry)
main.py          # CLI entry: find window → run_loop, Q to stop
loop.py          # refresh → OCR/buy → scroll → OCR/buy
actions.py       # do_refresh / do_buy / do_scroll
ocr.py           # PrintWindow capture + Windows OCR
input.py         # Win32 click + scroll primitives
config.py        # coords, timing, keywords, item costs
find_window.py   # list Epic Seven windows
ut/              # live-window calibration harnesses
E7ShopBot.spec   # PyInstaller build
```

