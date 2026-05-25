from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


def _make_tray_icon() -> QIcon:
    """Generate a programmatic tray icon - rounded square with '译' character."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(78, 205, 196))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 7, 7)
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Microsoft YaHei", 14, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "译")
    painter.end()
    return QIcon(pixmap)


class SystemTray(QSystemTrayIcon):
    screenshot_requested = Signal()
    settings_requested = Signal()

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app

        self.setIcon(_make_tray_icon())
        self.setToolTip("截图翻译工具")

        menu = QMenu()

        screenshot_act = QAction("截图翻译", menu)
        screenshot_act.triggered.connect(self.screenshot_requested.emit)
        menu.addAction(screenshot_act)

        settings_act = QAction("设置", menu)
        settings_act.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_act)

        menu.addSeparator()

        quit_act = QAction("退出", menu)
        quit_act.triggered.connect(app.quit)
        menu.addAction(quit_act)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self.screenshot_requested.emit()
