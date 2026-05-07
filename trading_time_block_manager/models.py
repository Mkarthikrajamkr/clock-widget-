"""Domain models and time calculations for trading sessions.

The application intentionally uses ``datetime.now()`` without injecting a fixed
zone. That makes all calculations follow the operating system's local timezone,
which is the right behavior for traders in different regions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4


class SessionStatus(str, Enum):
    """Human-readable lifecycle state for a session occurrence."""

    UPCOMING = "Upcoming"
    ACTIVE = "Active"
    COMPLETED = "Completed"


@dataclass(slots=True)
class SessionTiming:
    """Calculated timing information for one trading block occurrence."""

    start: datetime
    end: datetime
    status: SessionStatus
    progress: float
    remaining: timedelta


@dataclass(slots=True)
class TradingBlock:
    """Persistent trading block configuration."""

    name: str
    start_time: str
    end_time: str
    notes: str = ""
    alarm_enabled: bool = False
    alarm_before_start: bool = False
    alarm_at_start: bool = False
    alarm_before_end: bool = False
    alarm_offset_minutes: int = 5
    recurring_daily: bool = True
    color: str = "#2f81f7"
    block_id: str = field(default_factory=lambda: str(uuid4()))

    @staticmethod
    def parse_time(value: str) -> time:
        """Parse a 24-hour HH:MM value into a ``time`` object."""

        return datetime.strptime(value, "%H:%M").time()

    def time_range_label(self) -> str:
        """Return the display label used on cards and dialogs."""

        return f"{self.start_time} - {self.end_time}"

    def occurrence_for(self, now: datetime | None = None) -> SessionTiming:
        """Calculate status, progress, and remaining time for local ``now``.

        Overnight sessions are supported by moving the end time to the next day
        when the configured end clock time is less than or equal to the start.
        """

        now = now or datetime.now()
        start_clock = self.parse_time(self.start_time)
        end_clock = self.parse_time(self.end_time)
        start = datetime.combine(now.date(), start_clock)
        end = datetime.combine(now.date(), end_clock)

        if end <= start:
            # Session crosses midnight. If the current clock time is before the
            # end time, the session began yesterday; otherwise it ends tomorrow.
            end += timedelta(days=1)
            if now.time() < end_clock:
                start -= timedelta(days=1)
                end -= timedelta(days=1)

        if now < start:
            status = SessionStatus.UPCOMING
            progress = 0.0
            remaining = start - now
        elif start <= now <= end:
            status = SessionStatus.ACTIVE
            total_seconds = max((end - start).total_seconds(), 1)
            progress = min(max((now - start).total_seconds() / total_seconds, 0.0), 1.0)
            remaining = end - now
        else:
            status = SessionStatus.COMPLETED
            progress = 1.0
            remaining = timedelta(0)

        return SessionTiming(start=start, end=end, status=status, progress=progress, remaining=remaining)

    def next_sort_key(self, now: datetime | None = None) -> tuple[int, datetime, str]:
        """Return a stable key that places active and upcoming blocks first."""

        now = now or datetime.now()
        timing = self.occurrence_for(now)
        if timing.status == SessionStatus.ACTIVE:
            return (0, timing.end, self.name.lower())
        if timing.status == SessionStatus.UPCOMING:
            return (1, timing.start, self.name.lower())

        # Completed daily sessions sort after active/upcoming, by tomorrow's
        # occurrence when recurrence is enabled.
        tomorrow = now + timedelta(days=1)
        next_timing = self.occurrence_for(tomorrow) if self.recurring_daily else timing
        return (2, next_timing.start, self.name.lower())

    def to_dict(self) -> dict[str, Any]:
        """Serialize the block to JSON-compatible data."""

        return {
            "block_id": self.block_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "notes": self.notes,
            "alarm_enabled": self.alarm_enabled,
            "alarm_before_start": self.alarm_before_start,
            "alarm_at_start": self.alarm_at_start,
            "alarm_before_end": self.alarm_before_end,
            "alarm_offset_minutes": self.alarm_offset_minutes,
            "recurring_daily": self.recurring_daily,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradingBlock":
        """Create a block from saved JSON data with safe defaults."""

        return cls(
            block_id=data.get("block_id") or str(uuid4()),
            name=data.get("name", "Untitled Session"),
            start_time=data.get("start_time", "09:30"),
            end_time=data.get("end_time", "16:00"),
            notes=data.get("notes", ""),
            alarm_enabled=bool(data.get("alarm_enabled", False)),
            alarm_before_start=bool(data.get("alarm_before_start", False)),
            alarm_at_start=bool(data.get("alarm_at_start", False)),
            alarm_before_end=bool(data.get("alarm_before_end", False)),
            alarm_offset_minutes=int(data.get("alarm_offset_minutes", 5)),
            recurring_daily=bool(data.get("recurring_daily", True)),
            color=data.get("color", "#2f81f7"),
        )


def humanize_remaining(delta: timedelta) -> str:
    """Format a positive timedelta as a compact trading-dashboard label."""

    seconds = max(int(delta.total_seconds()), 0)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}h {minutes:02d}m remaining"
    if minutes:
        return f"{minutes:02d}m {secs:02d}s remaining"
    return f"{secs:02d}s remaining"


def iso_day(value: datetime) -> str:
    """Return the date key used to prevent duplicate alarm notifications."""

    return date(value.year, value.month, value.day).isoformat()
