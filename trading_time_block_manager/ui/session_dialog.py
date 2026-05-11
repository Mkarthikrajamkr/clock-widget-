"""Dialog for adding and editing trading blocks."""

from __future__ import annotations

from PyQt6.QtCore import QTime
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from ..models import TradingBlock


class SessionDialog(QDialog):
    """Collects all editable session fields from the user."""

    def __init__(self, block: TradingBlock | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Trading Session" if block else "Add Trading Session")
        self.block = block
        self.selected_color = block.color if block else "#2f81f7"
        self._build_ui()
        if block:
            self._load_block(block)

    def _build_ui(self) -> None:
        self.name = QLineEdit()
        self.name.setPlaceholderText("London Open, NY AM Scalps, Power Hour...")
        self.start = QTimeEdit()
        self.start.setDisplayFormat("HH:mm")
        self.start.setTime(QTime(9, 30))
        self.end = QTimeEdit()
        self.end.setDisplayFormat("HH:mm")
        self.end.setTime(QTime(16, 0))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Strategy, pairs, risk rules, execution checklist...")

        self.alarm_enabled = QCheckBox("Enable alarms")
        self.before_start = QCheckBox("Before session starts")
        self.at_start = QCheckBox("At session start")
        self.before_end = QCheckBox("Before session ends")
        self.offset = QSpinBox()
        self.offset.setRange(0, 240)
        self.offset.setSuffix(" min")
        self.offset.setValue(5)
        self.recurring = QCheckBox("Repeat daily")
        self.recurring.setChecked(True)

        self.color_preview = QLabel("     ")
        self.color_preview.setObjectName("ColorPreview")
        self._refresh_color_preview()
        color_button = QPushButton("Choose color")
        color_button.clicked.connect(self._choose_color)
        color_row = QHBoxLayout()
        color_row.addWidget(self.color_preview)
        color_row.addWidget(color_button)
        color_row.addStretch()

        form = QFormLayout()
        form.addRow("Block name", self.name)
        form.addRow("Start time", self.start)
        form.addRow("End time", self.end)
        form.addRow("Notes / Strategy", self.notes)
        form.addRow("Alarm", self.alarm_enabled)
        form.addRow("Alarm triggers", self._alarm_options_widget())
        form.addRow("Alarm offset", self.offset)
        form.addRow("Recurrence", self.recurring)
        form.addRow("Card color", color_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)
        self.resize(520, 560)

    def _alarm_options_widget(self):
        container = QVBoxLayout()
        container.addWidget(self.before_start)
        container.addWidget(self.at_start)
        container.addWidget(self.before_end)
        widget = QWidget()
        widget.setLayout(container)
        return widget

    def _load_block(self, block: TradingBlock) -> None:
        self.name.setText(block.name)
        start_time = TradingBlock.parse_time(block.start_time)
        end_time = TradingBlock.parse_time(block.end_time)
        self.start.setTime(QTime(start_time.hour, start_time.minute))
        self.end.setTime(QTime(end_time.hour, end_time.minute))
        self.notes.setText(block.notes)
        self.alarm_enabled.setChecked(block.alarm_enabled)
        self.before_start.setChecked(block.alarm_before_start)
        self.at_start.setChecked(block.alarm_at_start)
        self.before_end.setChecked(block.alarm_before_end)
        self.offset.setValue(block.alarm_offset_minutes)
        self.recurring.setChecked(block.recurring_daily)

    def _choose_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Choose session color")
        if color.isValid():
            self.selected_color = color.name()
            self._refresh_color_preview()

    def _refresh_color_preview(self) -> None:
        self.color_preview.setStyleSheet(f"background: {self.selected_color}; border-radius: 8px; min-height: 24px;")

    def get_block(self) -> TradingBlock:
        """Return a validated model from the form state."""

        name = self.name.text().strip() or "Untitled Session"
        block = TradingBlock(
            name=name,
            start_time=self.start.time().toString("HH:mm"),
            end_time=self.end.time().toString("HH:mm"),
            notes=self.notes.toPlainText().strip(),
            alarm_enabled=self.alarm_enabled.isChecked(),
            alarm_before_start=self.before_start.isChecked(),
            alarm_at_start=self.at_start.isChecked(),
            alarm_before_end=self.before_end.isChecked(),
            alarm_offset_minutes=self.offset.value(),
            recurring_daily=self.recurring.isChecked(),
            color=self.selected_color,
        )
        if self.block:
            block.block_id = self.block.block_id
        return block
