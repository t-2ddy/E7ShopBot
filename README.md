# auto-shop

e7shop2/

├── config.py    — all tunable constants (coords, timing, keywords)

├── input.py     — Win32 click + scroll primitives

├── ocr.py       — screen capture + Windows OCR pipeline

├── actions.py   — do_refresh / do_buy / do_scroll (+ buy button TODO)

├── loop.py      — async state machine following the flowchart

└── main.py      — entry point: find window → asyncio.run(run_loop)

## What is this? (plain-language overview)

This is a little helper app for **Epic Seven** that automatically refreshes and shops the in-game **Secret Shop** for you, so you don't have to sit there clicking Refresh over and over hoping for good items to show up.

### What it does, step by step

1. You open Epic Seven and leave it running in the background.
2. You open the E7 Secret Shop Bot app and type in two numbers:
   - **Skystones to spend** — how many Skystones you're willing to spend on shop refreshes. The app works out how many refreshes that buys you (each refresh costs 3 Skystones) and shows it as "Total refreshes."
   - **Starting gold** — how much gold you currently have. The app keeps its own running tally of your gold as it spends, so it knows when to stop.
3. You hit **Start**. From there the app takes over:
   - It clicks the shop's Refresh button for you.
   - It "looks" at the shop screen (using text recognition, the same way your phone can scan a receipt) to check if either **Mystic Medal** or **Covenant Bookmark** is currently in stock.
   - If it finds one, it clicks Buy and confirms the purchase automatically.
   - It scrolls down to check the rest of the shop too, then goes back to step 1 and refreshes again.
4. It keeps repeating this refresh-and-check cycle until one of two things happens:
   - You've used up all the refreshes you paid for with your Skystones, or
   - Your tracked gold drops below 300,000 (so you don't accidentally spend yourself broke). You can turn this safety net off with the **Gold limiter** checkbox if you don't want it.
5. While it's running, the app shows you live stats: how many refreshes it's done, and how many of each item it's bought. When it stops, it tells you why (ran out of refreshes, hit the gold limit, or you pressed Stop yourself).

### Good to know

- The gold amount isn't read off your screen — you tell the app how much gold you're starting with, and it subtracts the known cost of each item as it buys them (Mystic Medal costs 280,000 gold, Covenant Bookmark costs 184,000 gold). So make sure the "Starting gold" number you type in is accurate before you hit Start, otherwise the stopping point won't be accurate either.
- The app needs the Epic Seven window to be open (it doesn't matter if it's minimized or on another monitor) — if it can't find the game, it'll tell you instead of doing anything.
- You can stop the bot at any time by pressing the **Stop** button (it changes from "Start" once running).
- **It doesn't take over your mouse.** Instead of physically moving your cursor and clicking like a person would, it sends the clicks and scrolls directly to the game window behind the scenes. That means your actual mouse pointer never moves, and you're free to keep using your computer for other things (browsing, other apps, etc.) while it runs in the background.