"""Card widget used to render one trading session."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..models import SessionStatus, TradingBlock, humanize_remaining


class SessionCard(QFrame):
    """Modern rounded card with status, countdown, and progress controls."""

    edit_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, block: TradingBlock) -> None:
        super().__init__()
        self.block = block
        self.setObjectName("SessionCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._build_ui()
        self.update_from_time(datetime.now())

    def _build_ui(self) -> None:
        self.color_strip = QFrame()
        self.color_strip.setFixedWidth(5)
        self.color_strip.setObjectName("ColorStrip")

        self.title = QLabel()
        self.title.setObjectName("CardTitle")
        self.time_range = QLabel()
        self.time_range.setObjectName("MutedLabel")
        self.status = QLabel()
        self.status.setObjectName("StatusPill")
        self.remaining = QLabel()
        self.remaining.setObjectName("RemainingLabel")
        self.percent = QLabel()
        self.percent.setObjectName("MutedLabel")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setObjectName("ProgressBar")

        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setMaximumHeight(64)
        self.notes.setObjectName("NotesPreview")

        self.menu_button = QPushButton("⋯")
        self.menu_button.setObjectName("IconButton")
        self.menu_button.clicked.connect(self._open_menu)

        header = QHBoxLayout()
        title_group = QVBoxLayout()
        title_group.addWidget(self.title)
        title_group.addWidget(self.time_range)
        header.addLayout(title_group, stretch=1)
        header.addWidget(self.status)
        header.addWidget(self.menu_button)

        progress_row = QHBoxLayout()
        progress_row.addWidget(self.remaining)
        progress_row.addStretch()
        progress_row.addWidget(self.percent)

        content = QVBoxLayout()
        content.setContentsMargins(18, 16, 18, 16)
        content.setSpacing(10)
        content.addLayout(header)
        content.addLayout(progress_row)
        content.addWidget(self.progress)
        content.addWidget(self.notes)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.color_strip)
        root.addLayout(content)

    def update_block(self, block: TradingBlock) -> None:
        """Replace the backing model after edits."""

        self.block = block
        self.update_from_time(datetime.now())

    def update_from_time(self, now: datetime) -> None:
        """Refresh labels and progress for the supplied local time."""

        timing = self.block.occurrence_for(now)
        percent = int(round(timing.progress * 100))
        self.title.setText(self.block.name)
        self.time_range.setText(self.block.time_range_label())
        self.status.setText(timing.status.value)
        self.remaining.setText(self._remaining_text(timing.status, timing.remaining))
        self.percent.setText(f"{percent}% complete")
        self.progress.setValue(percent)
        self.notes.setText(self.block.notes or "No notes / strategy added yet.")
        self.color_strip.setStyleSheet(f"background: {self.block.color}; border-top-left-radius: 18px; border-bottom-left-radius: 18px;")
        self.setProperty("status", timing.status.value.lower())
        self.status.setProperty("status", timing.status.value.lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    @staticmethod
    def _remaining_text(status: SessionStatus, remaining) -> str:
        if status == SessionStatus.ACTIVE:
            return humanize_remaining(remaining)
        if status == SessionStatus.UPCOMING:
            return f"Starts in {humanize_remaining(remaining).replace(' remaining', '')}"
        return "Session completed"

    def _open_menu(self) -> None:
        menu = QMenu(self)
        edit_action = menu.addAction("Edit session")
        delete_action = menu.addAction("Delete session")
        action = menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))
        if action == edit_action:
            self.edit_requested.emit(self.block.block_id)
        elif action == delete_action:
            self.delete_requested.emit(self.block.block_id)
