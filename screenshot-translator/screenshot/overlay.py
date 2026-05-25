from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget, QApplication


class ScreenshotOverlay(QWidget):
    """Full-screen semi-transparent overlay for selecting a capture region.

    Usage:
        overlay = ScreenshotOverlay()
        overlay.region_selected.connect(handle_region)
        overlay.cancelled.connect(handle_cancel)
        overlay.show()
    """

    region_selected = Signal(QRect)
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        screen_geo = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geo)

        self._origin = QPoint()
        self._dragging = False
        self._selection = QRect()

        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        if self._selection.isValid():
            rect = self._selection.normalized()
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawRect(rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            handle_size = 8
            painter.setBrush(QColor(78, 205, 196))
            painter.setPen(Qt.NoPen)
            for cx, cy in [
                (rect.left(), rect.top()),
                (rect.right(), rect.top()),
                (rect.left(), rect.bottom()),
                (rect.right(), rect.bottom()),
            ]:
                painter.drawRect(
                    int(cx - handle_size / 2), int(cy - handle_size / 2),
                    handle_size, handle_size,
                )

            pen = QPen(QColor(78, 205, 196), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._origin = event.pos()
            self._dragging = True
            self._selection = QRect()

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self._selection = QRect(self._origin, event.pos())
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            rect = self._selection.normalized()
            if rect.width() >= 20 and rect.height() >= 20:
                self.hide()
                self.region_selected.emit(rect)
            else:
                self._selection = QRect()
                self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.hide()
            self.cancelled.emit()
