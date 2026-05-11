from datetime import datetime

import pytest

from trading_time_block_manager.models import TradingBlock
from trading_time_block_manager.sample_data import starter_sessions
from trading_time_block_manager.storage import SessionStorage


def test_storage_round_trip(tmp_path):
    storage = SessionStorage(tmp_path / "sessions.json")
    blocks = starter_sessions()

    storage.save(blocks)
    loaded = storage.load()

    assert [block.name for block in loaded] == [block.name for block in blocks]
    assert loaded[0].alarm_before_start is True
    assert loaded[1].color == "#2f81f7"


def test_alarm_manager_emits_once():
    pytest.importorskip("PyQt6")
    from trading_time_block_manager.alarm import AlarmManager

    block = TradingBlock(
        name="Open",
        start_time="09:30",
        end_time="10:00",
        alarm_enabled=True,
        alarm_at_start=True,
    )
    manager = AlarmManager()
    triggered: list[tuple[str, str]] = []
    manager.alarm_triggered.connect(lambda title, message: triggered.append((title, message)))

    manager.evaluate([block], datetime(2026, 5, 7, 9, 30, 1))
    manager.evaluate([block], datetime(2026, 5, 7, 9, 30, 2))

    assert len(triggered) == 1
    assert triggered[0][0] == "Open is starting now"
