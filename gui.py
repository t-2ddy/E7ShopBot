import asyncio
import threading

import customtkinter as ctk
import win32gui

import config
from loop import run_loop

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_FONT         = ("Segoe UI", 13)
_FONT_BOLD    = ("Segoe UI", 13, "bold")
_FONT_TITLE   = ("Segoe UI", 18, "bold")
_FONT_SMALL   = ("Segoe UI", 11)
_FONT_STATUS  = ("Segoe UI", 14, "bold")

SKYSTONES_PER_REFRESH = 3


class BotStats:
    """Shared mutable state between the GUI thread and the bot's asyncio thread."""

    def __init__(self) -> None:
        self.refresh_count = 0
        self.refresh_limit = 0  # 0 = unlimited
        self.purchases: dict[str, int] = {k: 0 for k in config.ITEM_KEYWORDS}
        self.gold_limiter_enabled = True
        self.running = False
        self.stop_reason = ""


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("E7 Secret Shop Bot")
        self.geometry("360x460")
        self.minsize(320, 400)
        self.resizable(True, True)

        self.stats = BotStats()
        self._bot_thread: threading.Thread | None = None
        self._loop_task: asyncio.Task | None = None
        self._async_loop: asyncio.AbstractEventLoop | None = None

        self._build_widgets()
        self.after(500, self._refresh_ui)

    def _build_widgets(self) -> None:
        pad = {"padx": 16, "pady": (8, 0)}

        title = ctk.CTkLabel(self, text="E7 Secret Shop Bot", font=_FONT_TITLE)
        title.pack(pady=(16, 8))

        status_frame = ctk.CTkFrame(self)
        status_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.status_label = ctk.CTkLabel(
            status_frame, text="\u25cf Idle", font=_FONT_STATUS
        )
        self.status_label.pack(side="left", padx=12, pady=8)

        self.start_button = ctk.CTkButton(status_frame, text="Start", font=_FONT_BOLD, command=self._on_start_stop)
        self.start_button.pack(side="right", padx=12, pady=8)

        stones_frame = ctk.CTkFrame(self)
        stones_frame.pack(fill="x", padx=16, pady=(0, 8))

        stones_row = ctk.CTkFrame(stones_frame, fg_color="transparent")
        stones_row.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(stones_row, text="Skystones to spend", font=_FONT).pack(side="left")
        self.skystones_var = ctk.StringVar(value="300")
        self.skystones_var.trace_add("write", self._on_skystones_change)
        self.skystones_entry = ctk.CTkEntry(stones_row, width=90, textvariable=self.skystones_var, font=_FONT)
        self.skystones_entry.pack(side="right")

        allowed_row = ctk.CTkFrame(stones_frame, fg_color="transparent")
        allowed_row.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(allowed_row, text="Refreshes allowed", font=_FONT).pack(side="left")
        self.refreshes_allowed_label = ctk.CTkLabel(allowed_row, text="0", font=_FONT)
        self.refreshes_allowed_label.pack(side="right")
        self._on_skystones_change()

        done_row = ctk.CTkFrame(stones_frame, fg_color="transparent")
        done_row.pack(fill="x", padx=12, pady=(2, 10))
        ctk.CTkLabel(done_row, text="Refreshes done", font=_FONT).pack(side="left")
        self.refreshes_done_label = ctk.CTkLabel(done_row, text="0", font=_FONT)
        self.refreshes_done_label.pack(side="right")

        purchases_frame = ctk.CTkFrame(self)
        purchases_frame.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            purchases_frame, text="Purchases", font=_FONT_BOLD
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.purchase_labels: dict[str, ctk.CTkLabel] = {}
        for keyword in config.ITEM_KEYWORDS:
            row = ctk.CTkFrame(purchases_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(row, text=keyword.title(), font=_FONT).pack(side="left")
            count_label = ctk.CTkLabel(row, text="0", font=_FONT)
            count_label.pack(side="right")
            self.purchase_labels[keyword] = count_label

        ctk.CTkFrame(purchases_frame, fg_color="transparent", height=6).pack()

        limiter_frame = ctk.CTkFrame(self)
        limiter_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.gold_limiter_var = ctk.BooleanVar(value=True)
        gold_check = ctk.CTkCheckBox(
            limiter_frame,
            text="Gold limiter",
            font=_FONT,
            variable=self.gold_limiter_var,
            command=self._on_gold_limiter_toggle,
        )
        gold_check.pack(anchor="w", padx=12, pady=(10, 0))

        ctk.CTkLabel(
            limiter_frame,
            text=f"Stops at {config.GOLD_MIN:,} gold",
            font=_FONT_SMALL,
            text_color="gray60",
        ).pack(anchor="w", padx=36, pady=(0, 10))

    def _on_skystones_change(self, *_args) -> None:
        raw = self.skystones_var.get().strip()
        try:
            skystones = int(raw) if raw else 0
        except ValueError:
            skystones = 0
        self.stats.refresh_limit = skystones // SKYSTONES_PER_REFRESH
        self.refreshes_allowed_label.configure(text=str(self.stats.refresh_limit))

    def _on_gold_limiter_toggle(self) -> None:
        self.stats.gold_limiter_enabled = self.gold_limiter_var.get()

    def _on_start_stop(self) -> None:
        if self.stats.running:
            self._stop_bot()
        else:
            self._start_bot()

    def _start_bot(self) -> None:
        hwnd = win32gui.FindWindow(config.WINDOW_CLASS, config.WINDOW_TITLE)
        if not hwnd:
            self.status_label.configure(
                text="\u25cf Window not found", text_color="red"
            )
            return

        self.stats.refresh_count = 0
        self.stats.purchases = {k: 0 for k in config.ITEM_KEYWORDS}
        self.stats.stop_reason = ""
        self.stats.running = True

        self._bot_thread = threading.Thread(
            target=self._run_bot_thread, args=(hwnd,), daemon=True
        )
        self._bot_thread.start()

        self.start_button.configure(text="Stop")
        self.status_label.configure(text="\u25cf Running", text_color="#2ecc71")

    def _run_bot_thread(self, hwnd: int) -> None:
        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)
        try:
            self._loop_task = self._async_loop.create_task(run_loop(hwnd, self.stats))
            self._async_loop.run_until_complete(self._loop_task)
        finally:
            self.stats.running = False
            self._async_loop.close()

    def _stop_bot(self) -> None:
        if self._async_loop is not None and self._loop_task is not None:
            self._async_loop.call_soon_threadsafe(self._loop_task.cancel)
        self.stats.stop_reason = self.stats.stop_reason or "user"

    def _refresh_ui(self) -> None:
        self.refreshes_done_label.configure(text=str(self.stats.refresh_count))
        for keyword, label in self.purchase_labels.items():
            label.configure(text=str(self.stats.purchases.get(keyword, 0)))

        if not self.stats.running and self.start_button.cget("text") == "Stop":
            self.start_button.configure(text="Start")
            if self.stats.stop_reason == "gold limit":
                self.status_label.configure(text="\u25cf Stopped (gold limit)", text_color="red")
            elif self.stats.stop_reason == "refresh limit":
                self.status_label.configure(text="\u25cf Stopped (refresh limit)", text_color="orange")
            else:
                self.status_label.configure(text="\u25cf Idle", text_color="gray60")

        self.after(500, self._refresh_ui)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
