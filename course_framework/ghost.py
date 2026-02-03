from __future__ import annotations
from PySide6.QtCore import QObject, QTimer, Signal

class GhostTyper(QObject):
    """Small, reliable ghost typer for demos."""
    typed_count = Signal(int)
    finished = Signal()

    def __init__(self, wpm: int = 18, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._text = ""
        self._pos = 0
        self.set_wpm(wpm)

    def set_wpm(self, wpm: int):
        interval = int(60000 / max(1, wpm) / 5)
        self._timer.setInterval(max(8, interval))

    def start(self, text: str):
        self.stop()
        self._text = text or ""
        self._pos = 0
        self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    def _tick(self):
        if self._pos >= len(self._text):
            self.stop()
            self.finished.emit()
            return
        self._pos += 1
        self.typed_count.emit(self._pos)

    @property
    def text(self) -> str:
        return self._text
