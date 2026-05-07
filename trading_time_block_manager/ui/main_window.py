"""Main dashboard window for the Trading Time Block Manager."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from ..alarm import AlarmManager
from ..models import TradingBlock
from ..resources import app_icon
from ..sample_data import starter_sessions
from ..storage import SessionStorage
from ..timer_manager import TimerManager
from .mini_timer import MiniTimer
from .session_card import SessionCard
from .session_dialog import SessionDialog


class MainWindow(QMainWindow):
    """Dark-mode trading dashboard with persistent session cards."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Trading Time Block Manager")
        self.resize(1050, 760)
        self.storage = SessionStorage()
        self.blocks: list[TradingBlock] = self.storage.load()
        self.cards: dict[str, SessionCard] = {}
        self.timer = TimerManager()
        self.alarms = AlarmManager()
        self.mini_timer = MiniTimer()
        self._last_now = datetime.now()
        self._alarm_popups: list[QMessageBox] = []
        self.tray_icon = QSystemTrayIcon(self) if QSystemTrayIcon.isSystemTrayAvailable() else None
        if self.tray_icon:
            self.tray_icon.setIcon(app_icon())
            self.tray_icon.setToolTip("Trading Time Block Manager")
            self.tray_icon.setVisible(True)
        self._build_ui()
        self._build_actions()
        self._apply_styles()
        self._render_cards()
        self.timer.tick.connect(self._on_tick)
        self.alarms.alarm_triggered.connect(self._show_alarm)
        self.timer.start()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        title = QLabel("Trading Time Block Manager")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Local-time session planning, progress, and alarms for traders")
        subtitle.setObjectName("MutedLabel")
        self.clock_label = QLabel()
        self.clock_label.setObjectName("ClockLabel")

        add_button = QPushButton("+ Add Block")
        add_button.setObjectName("PrimaryButton")
        add_button.clicked.connect(self.add_block)
        starter_button = QPushButton("Load Starter Sessions")
        starter_button.clicked.connect(self.load_starter_sessions)
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_blocks)
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_blocks)
        mini_button = QPushButton("Mini Timer")
        mini_button.clicked.connect(self.toggle_mini_timer)
        always_button = QPushButton("Always on Top")
        always_button.setCheckable(True)
        always_button.toggled.connect(self.set_always_on_top)

        button_row = QHBoxLayout()
        button_row.addWidget(add_button)
        button_row.addWidget(starter_button)
        button_row.addWidget(import_button)
        button_row.addWidget(export_button)
        button_row.addWidget(mini_button)
        button_row.addWidget(always_button)

        top = QHBoxLayout()
        heading = QVBoxLayout()
        heading.addWidget(title)
        heading.addWidget(subtitle)
        top.addLayout(heading, stretch=1)
        top.addWidget(self.clock_label)

        self.empty_label = QLabel("No trading blocks yet. Add a session or load starter sessions to begin.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setObjectName("EmptyState")

        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(14)
        self.card_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(self.card_container)

        root.addLayout(top)
        root.addLayout(button_row)
        root.addWidget(self.empty_label)
        root.addWidget(scroll, stretch=1)
        self.setCentralWidget(central)
        self.statusBar().showMessage(f"Sessions file: {self.storage.path}")

    def _build_actions(self) -> None:
        """Wire up keyboard shortcuts and menu actions."""

        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.add_block)
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self.toggle_mini_timer)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self.export_blocks)

        file_menu = self.menuBar().addMenu("File")
        add_action = QAction("Add Block", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self.add_block)
        file_menu.addAction(add_action)
        file_menu.addAction("Load Starter Sessions", self.load_starter_sessions)
        file_menu.addAction("Import Sessions", self.import_blocks)
        file_menu.addAction("Export Sessions", self.export_blocks)
        file_menu.addSeparator()
        file_menu.addAction("Quit", self.close)

    def _render_cards(self) -> None:
        """Rebuild cards after add/edit/delete/import and keep sorted order."""

        while self.card_layout.count() > 0:
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cards.clear()

        sorted_blocks = sorted(self.blocks, key=lambda block: block.next_sort_key(self._last_now))
        for block in sorted_blocks:
            card = SessionCard(block)
            card.edit_requested.connect(self.edit_block)
            card.delete_requested.connect(self.delete_block)
            self.cards[block.block_id] = card
            self.card_layout.addWidget(card)
        self.card_layout.addStretch()
        self.empty_label.setVisible(not bool(self.blocks))

    def _save_and_refresh(self) -> None:
        self.blocks.sort(key=lambda block: block.next_sort_key(self._last_now))
        self.storage.save(self.blocks)
        self._render_cards()

    def add_block(self) -> None:
        dialog = SessionDialog(parent=self)
        if dialog.exec():
            self.blocks.append(dialog.get_block())
            self._save_and_refresh()

    def edit_block(self, block_id: str) -> None:
        block = self._find_block(block_id)
        if not block:
            return
        dialog = SessionDialog(block, self)
        if dialog.exec():
            updated = dialog.get_block()
            index = self.blocks.index(block)
            self.blocks[index] = updated
            self._save_and_refresh()

    def delete_block(self, block_id: str) -> None:
        block = self._find_block(block_id)
        if not block:
            return
        response = QMessageBox.question(self, "Delete session", f"Delete '{block.name}'?")
        if response == QMessageBox.StandardButton.Yes:
            self.blocks = [item for item in self.blocks if item.block_id != block_id]
            self._save_and_refresh()

    def load_starter_sessions(self) -> None:
        """Load editable example blocks so first-time users see a working app."""

        if self.blocks:
            response = QMessageBox.question(
                self,
                "Replace sessions?",
                "Load starter sessions and replace your current blocks?",
            )
            if response != QMessageBox.StandardButton.Yes:
                return
        self.blocks = starter_sessions()
        self.alarms.reset()
        self._save_and_refresh()

    def import_blocks(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import sessions", str(Path.home()), "JSON files (*.json)")
        if not path:
            return
        try:
            imported = self.storage.import_from(Path(path))
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Import failed", f"Could not import sessions:\n{exc}")
            return
        self.blocks = imported
        self.alarms.reset()
        self._save_and_refresh()

    def export_blocks(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export sessions", str(Path.home() / "trading-sessions.json"), "JSON files (*.json)")
        if not path:
            return
        self.storage.export_to(Path(path), self.blocks)
        QMessageBox.information(self, "Export complete", "Session template exported successfully.")

    def toggle_mini_timer(self) -> None:
        if self.mini_timer.isVisible():
            self.mini_timer.hide()
        else:
            self.mini_timer.show()
            self.mini_timer.update_blocks(self.blocks, self._last_now)

    def set_always_on_top(self, enabled: bool) -> None:
        flags = self.windowFlags()
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _on_tick(self, now: datetime) -> None:
        """Refresh live clock, progress bars, mini timer, and alarm checks."""

        self._last_now = now
        self.clock_label.setText(now.strftime("%A, %d %b %Y  •  %H:%M:%S"))
        for card in self.cards.values():
            card.update_from_time(now)
        self.alarms.evaluate(self.blocks, now)
        if self.mini_timer.isVisible():
            self.mini_timer.update_blocks(self.blocks, now)

    def _show_alarm(self, title: str, message: str) -> None:
        QApplication.beep()
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)
        popup = QMessageBox(self)
        popup.setWindowTitle(title)
        popup.setText(message)
        popup.setIcon(QMessageBox.Icon.Information)
        popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        popup.setModal(False)
        popup.finished.connect(lambda _result, box=popup: self._forget_alarm_popup(box))
        self._alarm_popups.append(popup)
        popup.show()

    def _forget_alarm_popup(self, popup: QMessageBox) -> None:
        """Drop closed alarm popups from the retention list."""

        if popup in self._alarm_popups:
            self._alarm_popups.remove(popup)

    def _find_block(self, block_id: str) -> TradingBlock | None:
        return next((block for block in self.blocks if block.block_id == block_id), None)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override name
        self.timer.stop()
        self.storage.save(self.blocks)
        self.mini_timer.close()
        super().closeEvent(event)

    def _apply_styles(self) -> None:
        """Install a compact dark stylesheet inspired by trading terminals."""

        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #0d1117; color: #e6edf3; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }
            QMenuBar, QMenu { background: #161b22; color: #e6edf3; border: 1px solid #30363d; }
            QMenu::item:selected { background: #21262d; }
            #AppTitle { font-size: 30px; font-weight: 700; letter-spacing: 0.3px; }
            #ClockLabel { color: #7ee787; font-size: 16px; font-weight: 600; }
            #MutedLabel { color: #8b949e; }
            #EmptyState { color: #8b949e; border: 1px dashed #30363d; border-radius: 18px; padding: 26px; }
            QPushButton { background: #21262d; color: #e6edf3; border: 1px solid #30363d; border-radius: 10px; padding: 10px 14px; }
            QPushButton:hover { background: #30363d; }
            QPushButton:checked, #PrimaryButton { background: #238636; border-color: #2ea043; font-weight: 700; }
            #IconButton { border-radius: 14px; padding: 4px 9px; font-size: 20px; }
            #SessionCard { background: #161b22; border: 1px solid #30363d; border-radius: 18px; }
            #SessionCard[status="active"] { border-color: #2ea043; }
            #SessionCard[status="upcoming"] { border-color: #388bfd; }
            #CardTitle { font-size: 19px; font-weight: 700; }
            #RemainingLabel { color: #e6edf3; font-size: 16px; font-weight: 600; }
            #StatusPill { border-radius: 12px; padding: 5px 10px; background: #30363d; color: #c9d1d9; font-weight: 700; }
            #StatusPill[status="active"] { background: #1f6f43; color: #d2ffd9; }
            #StatusPill[status="upcoming"] { background: #1f4f8b; color: #dbeafe; }
            #StatusPill[status="completed"] { background: #373e47; color: #8b949e; }
            #ProgressBar { height: 10px; border-radius: 5px; background: #30363d; }
            #ProgressBar::chunk { border-radius: 5px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2f81f7, stop:1 #7ee787); }
            #NotesPreview { background: #0d1117; color: #8b949e; border: 1px solid #30363d; border-radius: 12px; padding: 8px; }
            QLineEdit, QTextEdit, QTimeEdit, QSpinBox { background: #0d1117; color: #e6edf3; border: 1px solid #30363d; border-radius: 10px; padding: 8px; }
            QScrollArea { background: transparent; }
            #MiniTimer { background: #161b22; border: 1px solid #30363d; }
            #MiniTitle { font-weight: 700; font-size: 16px; }
            #MiniCountdown { color: #7ee787; font-size: 20px; font-weight: 800; }
            """
        )
