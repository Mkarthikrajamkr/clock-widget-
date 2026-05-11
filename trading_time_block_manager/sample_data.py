"""Starter templates users can load to see the app working immediately."""

from __future__ import annotations

from .models import TradingBlock


def starter_sessions() -> list[TradingBlock]:
    """Return timezone-neutral demo sessions using common market labels.

    Times are plain local clock times. They are not tied to any country or
    exchange timezone and can be edited immediately by the user.
    """

    return [
        TradingBlock(
            name="Pre-Market Prep",
            start_time="08:45",
            end_time="09:25",
            notes="Review overnight news, mark levels, confirm risk limits, and prepare watchlist.",
            alarm_enabled=True,
            alarm_before_start=True,
            alarm_at_start=True,
            alarm_offset_minutes=10,
            color="#f0883e",
        ),
        TradingBlock(
            name="Opening Range",
            start_time="09:30",
            end_time="10:30",
            notes="Focus on high-liquidity setups only. Wait for confirmation before entry.",
            alarm_enabled=True,
            alarm_at_start=True,
            alarm_before_end=True,
            alarm_offset_minutes=5,
            color="#2f81f7",
        ),
        TradingBlock(
            name="Power Hour Review",
            start_time="15:00",
            end_time="16:00",
            notes="Manage open risk, avoid revenge trades, and journal execution quality.",
            alarm_enabled=False,
            color="#a371f7",
        ),
    ]
