"""Small runtime-generated resources for the desktop application.

Keeping the icon in Python avoids external asset paths during development and
makes PyInstaller packaging less fragile. A future designer-supplied `.ico` can
replace this helper without touching the rest of the UI.
"""

from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QPixmap


_ICON_CACHE: QIcon | None = None


def app_icon() -> QIcon:
    """Return a reusable trading-themed application icon."""

    global _ICON_CACHE
    if _ICON_CACHE is not None:
        return _ICON_CACHE

    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient = QLinearGradient(0, 0, 256, 256)
    gradient.setColorAt(0.0, QColor("#0d1117"))
    gradient.setColorAt(0.55, QColor("#10233f"))
    gradient.setColorAt(1.0, QColor("#238636"))
    painter.setBrush(gradient)
    painter.setPen(QPen(QColor("#30363d"), 4))
    painter.drawRoundedRect(QRectF(10, 10, 236, 236), 42, 42)

    axis_pen = QPen(QColor("#8b949e"), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(axis_pen)
    painter.drawLine(QPointF(56, 184), QPointF(204, 184))
    painter.drawLine(QPointF(56, 184), QPointF(56, 68))

    chart_pen = QPen(QColor("#7ee787"), 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(chart_pen)
    points = [QPointF(66, 166), QPointF(98, 132), QPointF(126, 146), QPointF(158, 92), QPointF(198, 108)]
    for start, end in zip(points, points[1:], strict=True):
        painter.drawLine(start, end)

    painter.setFont(QFont("Segoe UI", 34, QFont.Weight.Bold))
    painter.setPen(QColor("#e6edf3"))
    painter.drawText(QRectF(0, 190, 256, 44), Qt.AlignmentFlag.AlignCenter, "TTB")
    painter.end()

    _ICON_CACHE = QIcon(pixmap)
    return _ICON_CACHE
