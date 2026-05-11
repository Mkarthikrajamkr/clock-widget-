"""Optional floating mini timer widget for the nearest active/upcoming block."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..models import SessionStatus, TradingBlock, humanize_remaining


class MiniTimer(QWidget):
    """Small always-on-top window that summarizes the most important session."""

    def __init__(self) -> None:
        super().__init__(flags=Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Trading Timer")
        self.setObjectName("MiniTimer")
        self.title = QLabel("No sessions")
        self.title.setObjectName("MiniTitle")
        self.timer = QLabel("--:--")
        self.timer.setObjectName("MiniCountdown")
        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.timer)
        self.resize(260, 110)

    def update_blocks(self, blocks: list[TradingBlock], now: datetime) -> None:
        """Show the active block first, otherwise the next upcoming block."""

        if not blocks:
            self.title.setText("No sessions")
            self.timer.setText("Add a block")
            return
        block = sorted(blocks, key=lambda item: item.next_sort_key(now))[0]
        timing = block.occurrence_for(now)
        self.title.setText(block.name)
        if timing.status == SessionStatus.ACTIVE:
            self.timer.setText(humanize_remaining(timing.remaining))
        elif timing.status == SessionStatus.UPCOMING:
            self.timer.setText("Starts in " + humanize_remaining(timing.remaining).replace(" remaining", ""))
        else:
            self.timer.setText("Completed")
