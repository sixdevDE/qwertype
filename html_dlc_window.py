# html_dlc_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Signal

# Try relative then absolute import; if missing, provide a safe stub so the app doesn't crash.
try:
    from .scholar_engine import ScholarEngine
except Exception:
    try:
        from scholar_engine import ScholarEngine
    except Exception:
        # Fallback stub to avoid crashing when module is missing.
        from PySide6.QtWidgets import QLabel
        class ScholarEngine(QWidget):
            badge_awarded = Signal(int)
            request_close = Signal()

            def __init__(self, *args, dlc_data=None, standalone=False, **kwargs):
                super().__init__(*args, **kwargs)
                layout = QVBoxLayout(self)
                layout.setContentsMargins(16, 16, 16, 16)
                label = QLabel("ScholarEngine module missing. HTML DLC disabled.", self)
                layout.addWidget(label)

            def shutdown(self):
                pass

class HtmlDlcWindow(QMainWindow):
    closed = Signal()

    def __init__(self, app, dlc_data):
        super().__init__()
        self.app = app
        self.dlc_data = dlc_data

        self.setWindowTitle("QwerType – HTML DLC")
        self.resize(1280, 800)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(root)

        self.scholar = ScholarEngine(
            dlc_data=self.dlc_data,
            standalone=True
        )

        layout.addWidget(self.scholar)

        self.scholar.badge_awarded.connect(self._on_badge)
        self.scholar.request_close.connect(self.close)

    def _on_badge(self, tier):
        self.app.awardBadge("html", tier)

    def closeEvent(self, event):
        self.scholar.shutdown()
        self.closed.emit()
        event.accept()
