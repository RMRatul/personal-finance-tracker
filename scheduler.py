import schedule
import time
import threading
from datetime import datetime
from typing import Callable
 
 
class ReportScheduler:
    """
    Runs in a background thread.
    Sends monthly report on the 1st of every month at 09:00 AM.
    """
    def __init__(self, send_fn: Callable):
        self._send_fn = send_fn
        self._thread: threading.Thread = None
        self._running = False

    def _check_and_send(self):
        if datetime.now().day == 1:
            self._job()

    def _job(self):
        now = datetime.now()
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
        print(f"\n  📅 Scheduler triggered at {now.strftime('%Y-%m-%d %H:%M')}")
        success, msg = self._send_fn(prev_year, prev_month)
        print(f"  {msg}\n")

    def start(self):
        schedule.every().day.at("09:00").do(self._check_and_send)
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("  ⏰ Scheduler started — report will auto-send on the 1st of each month at 09:00 AM.")

    def _run_loop(self):
        while self._running:
            schedule.run_pending()
            time.sleep(30)

    def stop(self):
        self._running = False
        schedule.clear()
        print("  ⏰ Scheduler stopped.")

    def send_now(self, year: int = None, month: int = None) -> tuple[bool, str]:
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        return self._send_fn(year, month)