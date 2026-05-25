from __future__ import annotations

import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyManager(QObject):
    """Wraps the keyboard library as a QObject that emits Qt signals.

    The keyboard library fires callbacks from its own thread. By emitting
    a Qt signal, we ensure the slot runs on the main thread where Qt
    widgets can be safely manipulated.
    """

    triggered = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._current_hotkey: str | None = None

    def register(self, hotkey: str) -> None:
        """Register a global hotkey. Replaces any previous registration."""
        self.unregister()
        keyboard.add_hotkey(hotkey, lambda: self.triggered.emit())
        self._current_hotkey = hotkey

    def unregister(self) -> None:
        if self._current_hotkey:
            keyboard.remove_hotkey(self._current_hotkey)
            self._current_hotkey = None
