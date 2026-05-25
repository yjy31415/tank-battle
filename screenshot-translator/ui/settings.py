from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QCheckBox, QDialogButtonBox, QKeySequenceEdit,
)

from config import Config


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(420)
        self._config = config

        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        self._hotkey_edit = QKeySequenceEdit()
        self._hotkey_edit.setKeySequence(QKeySequence(config.hotkey))
        form.addRow("截图快捷键:", self._hotkey_edit)

        self._translator_combo = QComboBox()
        self._translator_combo.addItems(["google", "deepl"])
        self._translator_combo.setCurrentText(config.translator)
        form.addRow("翻译服务:", self._translator_combo)

        self._display_combo = QComboBox()
        self._display_combo.addItem("双语对照", "bilingual")
        self._display_combo.addItem("仅译文", "translation_only")
        idx = self._display_combo.findData(config.display_mode)
        if idx >= 0:
            self._display_combo.setCurrentIndex(idx)
        form.addRow("显示方式:", self._display_combo)

        self._google_key = QLineEdit()
        self._google_key.setText(config.google_api_key)
        self._google_key.setEchoMode(QLineEdit.Password)
        self._google_key.setPlaceholderText("可选，用于 Google Cloud Translation API")
        form.addRow("Google API Key:", self._google_key)

        self._deepl_key = QLineEdit()
        self._deepl_key.setText(config.deepl_api_key)
        self._deepl_key.setEchoMode(QLineEdit.Password)
        self._deepl_key.setPlaceholderText("DeepL API Free Key (推荐)")
        form.addRow("DeepL API Key:", self._deepl_key)

        self._auto_start = QCheckBox()
        self._auto_start.setChecked(config.auto_start)
        form.addRow("开机自启:", self._auto_start)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self) -> None:
        self._config.hotkey = self._hotkey_edit.keySequence().toString()
        self._config.translator = self._translator_combo.currentText()
        self._config.display_mode = self._display_combo.currentData()
        self._config.google_api_key = self._google_key.text()
        self._config.deepl_api_key = self._deepl_key.text()
        self._config.auto_start = self._auto_start.isChecked()
        self._config.save()
        self.accept()
