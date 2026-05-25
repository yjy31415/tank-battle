from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from config import Config
from screenshot.hotkey import HotkeyManager
from screenshot.capture import capture_region
from screenshot.overlay import ScreenshotOverlay
from ocr.engine import OCREngine
from translator.factory import create_translator
from ui.tray import SystemTray
from ui.result_window import ResultWindow
from ui.settings import SettingsDialog


class App:
    def __init__(self) -> None:
        self.config = Config.load()

        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)

        self._ocr: OCREngine | None = None
        self._translator = None
        self._overlay: ScreenshotOverlay | None = None

        self.hotkey = HotkeyManager()
        self.hotkey.triggered.connect(self._start_screenshot)
        self.hotkey.register(self.config.hotkey)

        self.tray = SystemTray(self.qt_app)
        self.tray.screenshot_requested.connect(self._start_screenshot)
        self.tray.settings_requested.connect(self._show_settings)
        self.tray.show()

    def _start_screenshot(self) -> None:
        self._overlay = ScreenshotOverlay()
        self._overlay.region_selected.connect(self._on_region_captured)
        self._overlay.cancelled.connect(self._on_overlay_cancelled)
        self._overlay.show()

    def _on_region_captured(self, rect) -> None:
        img = capture_region(rect.x(), rect.y(), rect.width(), rect.height())

        ocr = self._get_ocr()
        text_blocks = ocr.recognize(img)

        if not text_blocks:
            self._cleanup_overlay()
            return

        translator = self._get_translator()
        texts = [b["text"] for b in text_blocks]
        translations = translator.translate(texts)

        for i, item in enumerate(translations):
            item["bbox"] = text_blocks[i]["bbox"]

        window = ResultWindow(img, translations, self.config.display_mode)
        window.show()

        self._cleanup_overlay()

    def _on_overlay_cancelled(self) -> None:
        self._cleanup_overlay()

    def _cleanup_overlay(self) -> None:
        if self._overlay:
            self._overlay.deleteLater()
            self._overlay = None

    def _get_ocr(self) -> OCREngine:
        if self._ocr is None:
            self._ocr = OCREngine(lang=self.config.ocr_lang)
        return self._ocr

    def _get_translator(self):
        if self._translator is None:
            kwargs = {}
            if self.config.translator == "deepl":
                kwargs["api_key"] = self.config.deepl_api_key
            self._translator = create_translator(
                self.config.translator, **kwargs
            )
        return self._translator

    def _show_settings(self) -> None:
        dialog = SettingsDialog(self.config)
        if dialog.exec():
            self.hotkey.register(self.config.hotkey)
            self._translator = None

    def run(self) -> None:
        sys.exit(self.qt_app.exec())


if __name__ == "__main__":
    App().run()
