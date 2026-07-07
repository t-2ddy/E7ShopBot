# auto-shop

e7shop2/

├── config.py    — all tunable constants (coords, timing, keywords)

├── input.py     — Win32 click + scroll primitives

├── ocr.py       — screen capture + Windows OCR pipeline

├── actions.py   — do_refresh / do_buy / do_scroll (+ buy button TODO)

├── loop.py      — async state machine following the flowchart

└── main.py      — entry point: find window → asyncio.run(run_loop)
