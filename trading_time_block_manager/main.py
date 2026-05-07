"""Application entry point."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .resources import app_icon
from .ui.main_window import MainWindow


def main() -> int:
    """Create the Qt application and start the event loop."""

    app = QApplication(sys.argv)
    app.setApplicationName("Trading Time Block Manager")
    app.setWindowIcon(app_icon())
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
