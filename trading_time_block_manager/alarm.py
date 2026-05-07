"""Alarm scheduling helpers for trading blocks."""

from __future__ import annotations

from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, pyqtSignal

from .models import TradingBlock, iso_day


class AlarmManager(QObject):
    """Emits alarm events once when a configured trigger is reached."""

    alarm_triggered = pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._fired: set[str] = set()

    def reset(self) -> None:
        """Clear in-memory alarm state, used after import or full reload."""

        self._fired.clear()

    def evaluate(self, blocks: list[TradingBlock], now: datetime | None = None) -> None:
        """Check every block for alarm triggers without blocking the UI thread."""

        now = now or datetime.now()
        for block in blocks:
            if not block.alarm_enabled:
                continue
            timing = block.occurrence_for(now)
            offset = timedelta(minutes=max(block.alarm_offset_minutes, 0))
            triggers: list[tuple[str, datetime, str]] = []
            if block.alarm_before_start:
                triggers.append(("before-start", timing.start - offset, "starts soon"))
            if block.alarm_at_start:
                triggers.append(("at-start", timing.start, "is starting now"))
            if block.alarm_before_end:
                triggers.append(("before-end", timing.end - offset, "ends soon"))

            for alarm_type, target, phrase in triggers:
                seconds_since_target = (now - target).total_seconds()
                key = f"{block.block_id}:{iso_day(target)}:{alarm_type}"
                # A small five-second window avoids firing old missed alarms
                # while still tolerating timer jitter on busy machines.
                if 0 <= seconds_since_target <= 5 and key not in self._fired:
                    self._fired.add(key)
                    title = f"{block.name} {phrase}"
                    message = f"{block.name} ({block.time_range_label()}) {phrase}."
                    self.alarm_triggered.emit(title, message)
