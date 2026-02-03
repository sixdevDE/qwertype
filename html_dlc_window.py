from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QLabel, QPushButton, QPlainTextEdit, QTextBrowser
)

from course_framework import CourseEngine, flatten_course_steps, GhostTyper
from course_framework.validators import validate_step
from course_framework.progress import badge_for_ratio


class HtmlDlcWindow(QMainWindow):
    """Standalone OS window for HTML DLC course.

    IMPORTANT:
    - Uses internal course_framework (engine + validators + ghost)
    - Does NOT touch main UI
    - Gated Continue for interactive steps (now_you/quiz/fix_the_code)
    """

    def __init__(self, main_window, theme, i18n, spec_data: Dict[str, Any], data_dir: str):
        super().__init__(None)
        self.main = main_window
        self.theme = theme
        self.i18n = i18n
        self.data_dir = data_dir

        self.spec = spec_data or {}
        self.steps = flatten_course_steps(self.spec)
        self.engine = CourseEngine(self.steps)

        self.ghost = GhostTyper(wpm=120, parent=self)
        self.ghost.typed_count.connect(self._on_ghost_typed)
        self.ghost.finished.connect(self._on_ghost_finished)
        self._ghost_full_text = ""

        self._last_badge: Optional[str] = None

        self.setWindowTitle("QwerType – HTML DLC")
        self.resize(1280, 820)

        self._build_ui()
        self._apply_theme()
        self._apply_step()

    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # Left: lesson
        self.lesson_panel = QFrame()
        self.lesson_panel.setObjectName("Panel")
        lp = QVBoxLayout(self.lesson_panel)
        lp.setSpacing(10)

        self.lbl_title = QLabel("")
        self.lbl_title.setStyleSheet("font-size:18px;font-weight:800;")
        lp.addWidget(self.lbl_title)

        self.lbl_meta = QLabel("")
        self.lbl_meta.setStyleSheet("opacity:0.8;")
        lp.addWidget(self.lbl_meta)

        self.txt_content = QTextBrowser()
        self.txt_content.setOpenExternalLinks(True)
        lp.addWidget(self.txt_content, 1)

        nav = QHBoxLayout()
        self.btn_back = QPushButton("◀ Back")
        self.btn_continue = QPushButton("Continue ▶")
        nav.addWidget(self.btn_back)
        nav.addStretch(1)
        nav.addWidget(self.btn_continue)
        lp.addLayout(nav)

        # Right: workspace
        self.work_panel = QFrame()
        self.work_panel.setObjectName("Panel")
        wp = QVBoxLayout(self.work_panel)
        wp.setSpacing(10)

        hdr = QHBoxLayout()
        self.lbl_workspace = QLabel("Workspace")
        self.lbl_workspace.setStyleSheet("font-size:14px;font-weight:700;")
        hdr.addWidget(self.lbl_workspace)
        hdr.addStretch(1)

        self.lbl_progress = QLabel("0%")
        self.lbl_progress.setStyleSheet("font-weight:700;")
        hdr.addWidget(self.lbl_progress)
        wp.addLayout(hdr)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Your code …")
        wp.addWidget(self.editor, 3)

        self.preview = QTextBrowser()
        self.preview.setFrameShape(QFrame.NoFrame)
        wp.addWidget(self.preview, 2)

        actions = QHBoxLayout()
        self.btn_check = QPushButton("Check")
        self.btn_run_demo = QPushButton("Run Demo")
        actions.addWidget(self.btn_check)
        actions.addStretch(1)
        actions.addWidget(self.btn_run_demo)
        wp.addLayout(actions)

        root.addWidget(self.lesson_panel, 3)
        root.addWidget(self.work_panel, 4)

        # connect
        self.btn_back.clicked.connect(self._on_back)
        self.btn_continue.clicked.connect(self._on_continue)
        self.btn_check.clicked.connect(self._on_check)
        self.btn_run_demo.clicked.connect(self._on_run_demo)
        self.editor.textChanged.connect(self._on_editor_changed)

    def _apply_theme(self):
        # Apply app-wide stylesheet if available
        try:
            if hasattr(self.theme, "app_stylesheet"):
                self.setStyleSheet(self.theme.app_stylesheet())
        except Exception:
            pass

        is_dark = True
        try:
            is_dark = bool(getattr(self.theme, "is_dark", True))
        except Exception:
            pass

        if is_dark:
            content_bg = "#0d1117"
            content_text = "#e8eaf0"
            border = "#232a3a"
            editor_bg = "#0d1117"
            editor_text = "#e6edf3"
        else:
            content_bg = "#ffffff"
            content_text = "#1a1f2a"
            border = "#d9dfeb"
            editor_bg = "#ffffff"
            editor_text = "#0d1117"

        self.txt_content.setStyleSheet(
            f"background:{content_bg}; color:{content_text}; border:1px solid {border}; "
            "border-radius:12px; padding:8px;"
        )
        self.editor.setStyleSheet(
            f"background:{editor_bg}; color:{editor_text}; border:2px solid {border}; "
            "border-radius:12px; padding:10px; font-family: Consolas, monospace;"
        )
        self.preview.setStyleSheet(
            "background:#ffffff; color:#000000; border:1px solid #d9dfeb; border-radius:12px; padding:8px;"
        )

    def _apply_step(self):
        step = self.engine.current()
        stype = self.engine.current_type()

        self.lbl_title.setText(step.get("title", "") or "")
        self.lbl_meta.setText(f"{step.get('_chapter_title','')} • Step {self.engine.index+1}/{len(self.engine.steps)} • {stype}")

        content = step.get("content", [])
        if isinstance(content, str):
            html = content
        else:
            html = "<br>".join([str(x) for x in content])
        self.txt_content.setHtml(html)

        # defaults
        self._stop_ghost()
        self.btn_check.setVisible(False)
        self.btn_run_demo.setVisible(False)
        self.editor.blockSignals(True)
        self.editor.setPlainText("")
        self.editor.blockSignals(False)
        self.preview.setHtml("")
        self.editor.setReadOnly(True)
        self.btn_continue.setEnabled(True)

        if stype == "ghost_demo":
            self.btn_run_demo.setVisible(True)
            self.lbl_workspace.setText("Ghost Demo")
        elif stype == "now_you":
            self.btn_check.setVisible(True)
            self.editor.setReadOnly(False)
            starter = step.get("starter_code", "") or step.get("starter", "")
            if starter:
                self.editor.blockSignals(True)
                self.editor.setPlainText(starter)
                self.editor.blockSignals(False)
            self._update_preview()
            self.btn_continue.setEnabled(self.engine.get_state().completed)
            self.lbl_workspace.setText("Now you")
        else:
            self.lbl_workspace.setText("Reading")

        self._update_progress_ui()

    def _update_progress_ui(self):
        ratio = self.engine.progress_ratio()
        self.lbl_progress.setText(f"{int(ratio*100)}%")
        badge = badge_for_ratio(ratio)
        if badge and badge != self._last_badge:
            self._last_badge = badge
            self._toast(f"🏅 Badge unlocked: {badge}")

    def _on_back(self):
        if self.engine.back():
            self._apply_step()

    def _on_continue(self):
        if not self.engine.can_continue():
            self._toast("Solve the task first (Check).")
            return
        if self.engine.next():
            self._apply_step()
        else:
            self.close()

    def _on_check(self):
        step = self.engine.current()
        if self.engine.current_type() != "now_you":
            self._toast("Nothing to check on this step.")
            return
        code = self.editor.toPlainText()
        ok, msg = validate_step(step, code)
        self.engine.mark_attempt(ok=ok)
        if ok:
            self._toast(msg)
            self.btn_continue.setEnabled(True)
            self.editor.setReadOnly(True)
        else:
            self._toast("❌ " + msg)
            self.btn_continue.setEnabled(False)
        self._update_progress_ui()

    def _on_run_demo(self):
        step = self.engine.current()
        ghost = step.get("ghost", {}) or {}
        code = (ghost.get("final_code") or ghost.get("code") or "")
        if not code:
            self._toast("No demo code in this step.")
            return
        self._ghost_full_text = code
        self.editor.setReadOnly(True)
        self.editor.blockSignals(True)
        self.editor.setPlainText("")
        self.editor.blockSignals(False)
        self.preview.setHtml("")
        self.ghost.start(code)

    def _stop_ghost(self):
        try:
            self.ghost.stop()
        except Exception:
            pass

    def _on_ghost_typed(self, count: int):
        part = self._ghost_full_text[:count]
        self.editor.blockSignals(True)
        self.editor.setPlainText(part)
        self.editor.blockSignals(False)
        self.preview.setHtml(part)

    def _on_ghost_finished(self):
        self.preview.setHtml(self._ghost_full_text)
        self._toast("✅ Demo finished.")

    def _on_editor_changed(self):
        if not self.editor.isReadOnly():
            self._update_preview()

    def _update_preview(self):
        self.preview.setHtml(self.editor.toPlainText())

    def _toast(self, msg: str):
        try:
            self.main.toast.show_msg(msg, 2000)
        except Exception:
            try:
                self.statusBar().showMessage(msg, 2000)
            except Exception:
                print(msg)

    def closeEvent(self, event):
        self._stop_ghost()
        super().closeEvent(event)
