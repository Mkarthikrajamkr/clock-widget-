from datetime import datetime, timedelta

from trading_time_block_manager.models import SessionStatus, TradingBlock, humanize_remaining


def test_regular_session_status_and_progress():
    block = TradingBlock(name="Test", start_time="09:00", end_time="10:00")

    upcoming = block.occurrence_for(datetime(2026, 5, 7, 8, 30))
    assert upcoming.status == SessionStatus.UPCOMING
    assert upcoming.progress == 0

    active = block.occurrence_for(datetime(2026, 5, 7, 9, 30))
    assert active.status == SessionStatus.ACTIVE
    assert active.progress == 0.5
    assert active.remaining == timedelta(minutes=30)

    completed = block.occurrence_for(datetime(2026, 5, 7, 10, 30))
    assert completed.status == SessionStatus.COMPLETED
    assert completed.progress == 1


def test_overnight_session_uses_local_calendar_boundaries():
    block = TradingBlock(name="Overnight", start_time="22:00", end_time="02:00")

    assert block.occurrence_for(datetime(2026, 5, 7, 23, 0)).status == SessionStatus.ACTIVE
    assert block.occurrence_for(datetime(2026, 5, 8, 1, 0)).status == SessionStatus.ACTIVE
    assert block.occurrence_for(datetime(2026, 5, 7, 9, 0)).status == SessionStatus.UPCOMING


def test_humanize_remaining_formats_countdown():
    assert humanize_remaining(timedelta(hours=1, minutes=24, seconds=10)) == "01h 24m remaining"
    assert humanize_remaining(timedelta(minutes=4, seconds=5)) == "04m 05s remaining"
    assert humanize_remaining(timedelta(seconds=9)) == "09s remaining"
