# html_dlc_window.py
# QwerType – HTML DLC Window (Standalone Course Framework)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QPlainTextEdit, QTextBrowser, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
import re


# -----------------------------
# Ghost Typer (self-contained)
# -----------------------------
class GhostTyper(QTimer):
    char_typed = Signal(int)
    finished = Signal()

    def __init__(self, wpm=18):
        super().__init__()
        self.setInterval(int(60000 / (wpm * 5)))
        self._text = ""
        self._pos = 0
        self.timeout.connect(self._tick)

    def type_text(self, text: str):
        self.stop()
        self._text = text or ""
        self._pos = 0
        self.start()

    def _tick(self):
        if self._pos >= len(self._text):
            self.stop()
            self.finished.emit()
            return
        self._pos += 1
        self.char_typed.emit(self._pos)


# -----------------------------
# HTML DLC Window
# -----------------------------
class HtmlDlcWindow(QMainWindow):
    def __init__(self, main_window, theme, i18n, spec_data: dict):
        super().__init__(None)
        self.main = main_window
        self.theme = theme
        self.i18n = i18n
        self.spec = spec_data

        self.setWindowTitle("QwerType – HTML Kurs")
        self.resize(1300, 850)

        # ----- course state -----
        self.steps = self._collect_steps()
        self.step_index = 0
        self.step_completed = False
        self.active_step = None

        # ----- ghost -----
        self.ghost = GhostTyper()
        self.ghost.char_typed.connect(self._on_ghost_char)
        self.ghost.finished.connect(self._on_ghost_finished)
        self._ghost_text = ""

        # ----- UI -----
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        # LEFT: Lesson
        self.lesson_panel = QFrame()
        self.lesson_panel.setObjectName("Panel")
        lp = QVBoxLayout(self.lesson_panel)
        lp.setSpacing(10)

        self.lbl_title = QLabel("")
        self.lbl_title.setStyleSheet("font-size:18px;font-weight:700;")
        lp.addWidget(self.lbl_title)

        self.txt_content = QTextBrowser()
        self.txt_content.setOpenExternalLinks(True)
        lp.addWidget(self.txt_content, 1)

        nav = QHBoxLayout()
        self.btn_back = QPushButton("◀ Zurück")
        self.btn_continue = QPushButton("Weiter ▶")
        nav.addWidget(self.btn_back)
        nav.addStretch(1)
        nav.addWidget(self.btn_continue)
        lp.addLayout(nav)

        # RIGHT: Workspace
        self.work_panel = QFrame()
        self.work_panel.setObjectName("Panel")
        wp = QVBoxLayout(self.work_panel)
        wp.setSpacing(8)

        self.lbl_workspace = QLabel("HTML Workspace")
        self.lbl_workspace.setStyleSheet("font-size:14px;font-weight:600;")
        wp.addWidget(self.lbl_workspace)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Code erscheint hier …")
        wp.addWidget(self.editor, 3)

        self.preview = QTextBrowser()
        self.preview.setFrameShape(QFrame.NoFrame)
        wp.addWidget(self.preview, 2)

        act = QHBoxLayout()
        self.btn_check = QPushButton("Check")
        self.btn_run = QPushButton("Run Demo")
        act.addWidget(self.btn_check)
        act.addStretch(1)
        act.addWidget(self.btn_run)
        wp.addLayout(act)

        layout.addWidget(self.lesson_panel, 3)
        layout.addWidget(self.work_panel, 4)

        # ----- connections -----
        self.btn_back.clicked.connect(self._on_back)
        self.btn_continue.clicked.connect(self._on_continue)
        self.btn_check.clicked.connect(self._on_check)
        self.btn_run.clicked.connect(self._on_run_demo)
        self.editor.textChanged.connect(self._on_editor_changed)

        # ----- init -----
        self._load_step(0)

    # -----------------------------
    # Step handling
    # -----------------------------
    def _collect_steps(self):
        steps = []
        for ch in self.spec.get("course", {}).get("chapters", []):
            for st in ch.get("steps", []):
                steps.append(st)
        return steps

    def _load_step(self, index: int):
        self.ghost.stop()
        self.step_index = max(0, min(index, len(self.steps) - 1))
        self.active_step = self.steps[self.step_index]
        self.step_completed = False

        step = self.active_step
        stype = step.get("type", "text")

        self.lbl_title.setText(step.get("title", ""))
        self.txt_content.setHtml("<p>" + "<br>".join(step.get("content", [])) + "</p>")

        # defaults
        self.editor.setReadOnly(True)
        self.editor.clear()
        self.preview.clear()
        self.btn_check.setVisible(False)
        self.btn_run.setVisible(False)
        self.btn_continue.setEnabled(True)

        # ---- routing ----
        if stype in ("intro", "lesson", "text"):
            self.step_completed = True

        elif stype == "ghost_demo":
            self.btn_run.setVisible(True)
            self.step_completed = True

        elif stype == "now_you":
            self.editor.setReadOnly(False)
            self.btn_check.setVisible(True)
            self.btn_continue.setEnabled(False)
            starter = step.get("starter_code", "")
            if starter:
                self.editor.setPlainText(starter)
            self._update_preview()

        else:
            self.step_completed = True

    # -----------------------------
    # Navigation
    # -----------------------------
    def _on_back(self):
        if self.step_index > 0:
            self._load_step(self.step_index - 1)

    def _on_continue(self):
        stype = self.active_step.get("type", "text")
        if stype in ("now_you", "quiz") and not self.step_completed:
            self._toast("Bitte Aufgabe lösen, bevor du weitergehst.")
            return
        if self.step_index < len(self.steps) - 1:
            self._load_step(self.step_index + 1)
        else:
            self.close()

    # -----------------------------
    # Ghost demo
    # -----------------------------
    def _on_run_demo(self):
        ghost = self.active_step.get("ghost", {})
        code = ghost.get("final_code", "")
        if not code:
            self._toast("Kein Demo-Code vorhanden.")
            return

        self.editor.setReadOnly(True)
        self.editor.clear()
        self.preview.clear()
        self._ghost_text = code
        self.ghost.type_text(code)

    def _on_ghost_char(self, pos: int):
        part = self._ghost_text[:pos]
        self.editor.setPlainText(part)
        self.preview.setHtml(part)

    def _on_ghost_finished(self):
        self.preview.setHtml(self._ghost_text)

    # -----------------------------
    # Now-you validation
    # -----------------------------
    def _on_check(self):
        checks = self.active_step.get("validation_checks", [])
        code = self.editor.toPlainText()

        for c in checks:
            t = c.get("type")
            if t == "element_exists":
                tag = c.get("target", "")
                if f"<{tag}" not in code.lower():
                    self._toast(f"<{tag}> fehlt.")
                    return
            elif t == "attribute_exists_or_matches_pattern":
                pat = c.get("pattern", "")
                if pat and not re.search(pat, code, re.IGNORECASE):
                    self._toast("Attribut stimmt nicht.")
                    return

        self.step_completed = True
        self.btn_continue.setEnabled(True)
        self.editor.setReadOnly(True)
        self._toast("✅ Korrekt!")

    # -----------------------------
    # Preview
    # -----------------------------
    def _on_editor_changed(self):
        if not self.editor.isReadOnly():
            self._update_preview()

    def _update_preview(self):
        self.preview.setHtml(self.editor.toPlainText())

    # -----------------------------
    # Utils
    # -----------------------------
    def _toast(self, msg: str):
        try:
            self.main.toast.show_msg(msg, 2000)
        except Exception:
            self.statusBar().showMessage(msg, 2000)
