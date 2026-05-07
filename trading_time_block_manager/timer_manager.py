"""Central one-second timer for live clock, cards, progress, and alarms."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TimerManager(QObject):
    """Low-overhead Qt timer that keeps the interface updated every second."""

    tick = pyqtSignal(datetime)

    def __init__(self, interval_ms: int = 1000) -> None:
        super().__init__()
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._emit_tick)

    def start(self) -> None:
        """Start ticking and emit immediately so the UI is populated at launch."""

        self._emit_tick()
        self._timer.start()

    def stop(self) -> None:
        """Stop the timer cleanly during application shutdown."""

        self._timer.stop()

    def _emit_tick(self) -> None:
        self.tick.emit(datetime.now())
