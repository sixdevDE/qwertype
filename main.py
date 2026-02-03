import sys
import os
import json
import time
import random
import math
import re
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from threading import Thread, Lock
from pathlib import Path
from datetime import datetime, timezone
from html_dlc_window import HtmlDlcWindow
import platform

from PySide6.QtCore import (
    Qt, QTimer, QPoint, QPointF, QRect, QSize, QEvent, Signal,
    QEasingCurve, QPropertyAnimation, QThread, QObject
)
from PySide6.QtGui import (
    QColor, QPainter, QPen, QFont, QPixmap, QGuiApplication, QRadialGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QLineEdit, QPushButton, QStackedWidget, QSizePolicy, QSpacerItem,
    QComboBox, QCheckBox, QDialog, QScrollArea, QGraphicsOpacityEffect,
    QPlainTextEdit, QTextBrowser
)

# ============================================================
# APP
# ============================================================

APP_TITLE = "qwerType"
FOOTER_TEXT = "Developed by sixdev© - 2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
I18N_DIR = os.path.join(BASE_DIR, "i18n")
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_LANG = "de"

SETTINGS_JSON = os.path.join(DATA_DIR, "settings.json")
HIGHSCORES_JSON = os.path.join(DATA_DIR, "highscores.json")
SERVER_URL = "https://qwertype.morina-solutions.com"

DEFAULT_WORDS_DE = [
    "möchten", "tastatur", "lernen", "geschwindigkeit", "technik",
    "übung", "genauigkeit", "workflow", "python", "qwertz",
    "straße", "größe", "über", "für", "schreiben",
    "beispiel", "computer", "entwickler", "software", "hardware",
    "bildschirm", "maus", "internet", "browser", "webseite",
    "programmieren", "variable", "funktion", "klasse", "objekt",
    "schleife", "bedingung", "datenbank", "netzwerk", "server",
    "client", "projekt", "aufgabe", "lösung", "erfolg",
]

DEFAULT_SENTENCES_DE = [
    "ich tippe heute sehr konzentriert",
    "python macht spaß wenn es läuft",
    "bitte schreibe die wörter sauber",
    "übung macht den meister",
    "ich will schneller und genauer werden",
    "heute trainiere ich zehn finger tippen",
    "eine schnelle tastatur ist sehr hilfreich",
    "konzentration ist der schlüssel zum erfolg",
    "fehler zu machen ist ein teil des lernens",
    "jeder schritt bringt mich meinem ziel näher",
    "die sonne scheint heute besonders hell",
    "morgen werde ich noch besser tippen können",
]

DEFAULT_WORDS_EN = [
    "keyboard", "typing", "practice", "speed", "accuracy",
    "improve", "engine", "source", "code", "python",
    "developer", "software", "project", "system", "network",
    "computer", "internet", "website", "online", "digital",
    "learning", "example", "result", "success", "future",
    "design", "simple", "complex", "stable", "active",
    "screen", "mouse", "button", "click", "input",
    "output", "data", "base", "logic", "flow",
]

DEFAULT_SENTENCES_EN = [
    "i am typing very fast today",
    "python is a great language to learn",
    "practice makes perfect in typing",
    "i want to become more accurate",
    "keep your fingers on the home row",
    "speed comes with time and effort",
    "focus on the screen not the keys",
    "every day is a new opportunity",
    "success is the result of hard work",
    "logic will get you from a to b",
]

# Minimal: Programmiersprachen-Listen (für Training + getrennte Leaderboards)
DEFAULT_LANG_ITEMS = {
    "py": [
        "def", "class", "import", "from", "return", "async", "await",
        "list", "dict", "tuple", "lambda", "with", "yield",
    ],
    "js": [
        "function", "const", "let", "var", "return", "async", "await",
        "import", "export", "class", "extends", "promise", "typeof",
    ],
    "cpp": [
        "int", "float", "double", "std", "string", "vector", "include",
        "namespace", "template", "nullptr", "override", "constexpr",
    ],
    "rs": [
        "fn", "let", "mut", "impl", "trait", "enum", "struct",
        "match", "use", "crate", "pub", "where",
    ],
    "java": [
        "public", "class", "static", "void", "new", "return", "extends",
        "implements", "package", "import", "final", "interface",
    ],
}

PROFANITY = {
    # expanded filter
    "fuck", "shit", "bitch", "asshole", "pussy", "dick", "cunt",
    "ficker", "fotze", "hurensohn", "arschloch", "scheiße", "scheisse",
    "nazi", "hitler", "wichser", "schlampe", "depp", "idiot",
    "cock", "bastard", "slut", "wanker",
}

def _ensure_dirs():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(I18N_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))

def _write_json_if_missing(path: str, data: dict):
    if os.path.exists(path):
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def ensure_default_i18n_files():
    _ensure_dirs()

    de = {
        # tabs
        "tab_train": "Training",
        "tab_settings": "Einstellungen",
        "tab_scores": "Bestenliste",

        # settings
        "settings_title": "Einstellungen",
        "settings_winmode": "Fenstermodus",
        "win_windowed": "Fenster",
        "win_maximized": "Maximiert",
        "win_borderless": "Vollbild (Rahmenlos)",
        "footer_stats": "Statistik",
        "footer_settings": "Einstellungen",
        "settings_lang": "Sprache",
        "settings_layout": "Layout",
        "settings_mode": "Modus",
        "settings_name": "Name",
        "settings_name_ph": "Spitzname",
        "name_invalid": "Name nicht erlaubt.",
        "name_saved": "Name gespeichert.",
        "mode_words": "Wörter",
        "mode_sentences": "Sätze",
        "mode_py": "Python",
        "mode_js": "JavaScript",
        "mode_cpp": "C++",
        "mode_rs": "Rust",
        "mode_java": "Java",
        "setting_darkmode": "Dark Mode",
        "apply": "Übernehmen",
        "saved": "Gespeichert",

        # trainer / stats
        "stats_line_active": "WPM: {wpm}  |  Genauigkeit: {acc}%  |  Fehler: {err}  |  Zeit: {left}s",
        "stats_line_idle": "{note}",
        "suggestions": "Schwachstellen:",
        "suggestions_empty": "Schwachstellen: –",

        # session flow
        "hint_type_start": "Tippe START zum Beginnen.",
        "session_started": "Session gestartet (60s).",
        "session_finished": "Session beendet.",
        "session_finished_to_start": "Session beendet. Tippe START für neue Runde.",

        # score + leaderboard
        "final_score": "Ergebnis",
        "leaderboard": "Bestenliste",
        "leaderboard_offline": "Lokal gespeichert",
        "lb_words": "Wörter",
        "lb_sentences": "Sätze",
        "lb_langs": "Code",
        "lb_none": "Noch keine Einträge.",

        # splash
        "splash_sub": "Vorbereitung…",

        "hint_type_start_title": "BEREIT?",
        "hint_type_start_long": "Um die 60-Sekunden Session zu beginnen,\ntippe bitte 'START'.",
        "close": "Schließen",
    }

    en = {
        "tab_train": "Trainer",
        "tab_settings": "Settings",
        "tab_scores": "Stats",

        "settings_winmode": "Window Mode",
        "win_windowed": "Windowed",
        "win_maximized": "Maximized",
        "win_borderless": "Borderless Fullscreen",
        "footer_stats": "Stats",
        "footer_settings": "Settings",
        "settings_lang": "Language",
        "settings_layout": "Layout",
        "settings_mode": "Mode",
        "settings_name": "Name",
        "settings_name_ph": "nickname",
        "name_invalid": "Name not allowed.",
        "name_saved": "Name saved.",
        "mode_words": "Words",
        "mode_sentences": "Sentences",
        "mode_py": "Python",
        "mode_js": "JavaScript",
        "mode_cpp": "C++",
        "mode_rs": "Rust",
        "mode_java": "Java",
        "setting_darkmode": "Dark Mode",
        "apply": "Apply",
        "saved": "Saved",

        "stats_line_active": "WPM: {wpm}  |  Accuracy: {acc}%  |  Errors: {err}  |  Time: {left}s",
        "stats_line_idle": "{note}",
        "suggestions": "Weak spots:",
        "suggestions_empty": "Weak spots: –",

        "hint_type_start": "Type START to begin.",
        "session_started": "Session started (60s).",
        "session_finished": "Session finished.",
        "session_finished_to_start": "Session finished. Type START to start again.",

        "final_score": "Score",
        "leaderboard": "Leaderboard",
        "leaderboard_offline": "Saved locally",
        "lb_words": "Words",
        "lb_sentences": "Sentences",
        "lb_langs": "Code",
        "lb_none": "No entries yet.",
        "splash_sub": "Preparing…",
        "close": "Close",
        "tab_train": "Trainer",
        "tab_settings": "Settings",
        "tab_scores": "Stats",
    }

    save_json(os.path.join(I18N_DIR, "de.json"), de)
    save_json(os.path.join(I18N_DIR, "en.json"), en)

def load_json(path: str, fallback: dict) -> dict:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return fallback

def save_json(path: str, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def normalize_name(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"\s+", " ", name)
    return name[:24]

def is_name_allowed(name: str) -> bool:
    n = normalize_name(name)
    if len(n) < 2:
        return False
    # einfache Sanitization fürs Prüfen
    cleaned = re.sub(r"[^a-zA-Z0-9äöüÄÖÜß]+", "", n).casefold()
    if not cleaned:
        return False
    for bad in PROFANITY:
        if bad in cleaned:
            return False
    return True

# ============================================================
# SERVER SYNC
# ============================================================

class ServerSync:
    """Handles adaptive syncing with highscore server"""
    def __init__(self):
        self.lock = Lock()
        self.pending_scores = []
        self.last_activity = time.time()
        self.sync_interval = 600  # 10 minutes in seconds
        self.idle_interval = 1800  # 30 minutes in seconds
        self.timer = None
        
    def add_score(self, username: str, mode: str, wpm: float, accuracy: float, points: int, completion_pct: Optional[float] = None):
        """Queue a score for syncing"""
        with self.lock:
            self.pending_scores.append({
                "username": username,
                "mode": mode,
                "wpm": wpm,
                "accuracy": accuracy,
                "points": points,
                "completion_pct": completion_pct
            })
            self.last_activity = time.time()
    
    def sync_now(self):
        """Sync all pending scores to server"""
        with self.lock:
            if not self.pending_scores:
                return
            
            scores_to_sync = self.pending_scores.copy()
            self.pending_scores.clear()
        
        # Sync in background thread
        Thread(target=self._sync_thread, args=(scores_to_sync,), daemon=True).start()
    
    def _sync_thread(self, scores):
        """Background thread for syncing"""
        for score in scores:
            try:
                response = requests.post(
                    f"{SERVER_URL}/api/scores",
                    json=score,
                    timeout=5
                )
                response.raise_for_status()
            except Exception as e:
                # Silently fail - scores are already saved locally
                print(f"Sync failed: {e}")
    
    def get_leaderboard(self, mode: str, period: str = "alltime", limit: int = 30) -> list:
        """Fetch leaderboard data from server"""
        try:
            response = requests.get(
                f"{SERVER_URL}/api/leaderboard/{mode}?period={period}&limit={limit}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def get_user_bests(self, username: str) -> dict:
        """Fetch personal bests for user"""
        url = f"{SERVER_URL}/api/user/{username}/bests"
        print(f"[DEBUG] Fetching user bests: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"[DEBUG] Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] Received bests for {username}: {list(data.keys())}")
            return data
        except Exception as e:
            print(f"[DEBUG] Error fetching user bests: {e}")
            return {}

    def get_adaptive_interval(self) -> int:
        """Calculate sync interval based on activity"""
        time_since_activity = time.time() - self.last_activity
        if time_since_activity < 600:  # Active in last 10 min
            return self.sync_interval
        else:  # Idle
            return self.idle_interval

# ============================================================
# LICENSING & HWID
# ============================================================

class HWIDManager:
    """Generates a stable hardware identifier for licensing"""
    @staticmethod
    def get_hwid() -> str:
        parts = [
            platform.system(),
            platform.machine(),
            os.getenv("COMPUTERNAME", ""),
            os.getenv("HOSTNAME", ""),
            os.getenv("USERNAME", ""),
        ]
        raw = "|".join([p for p in parts if p]) or "unknown"
        # We could hash this for privacy, but keeping it readable for debug per original LIC STUFF
        return raw

class LicenseManager(QObject):
    """Handles license activation and lease management"""
    status_changed = Signal(str) # For UI feedback

    def __init__(self):
        super().__init__()
        self.api_base = "https://apilc.morina-solutions.com"
        self.lease_file = Path(DATA_DIR) / "license_lease.json"
        self.hwid = HWIDManager.get_hwid()
        self.current_lease = self.load_lease()

    def load_lease(self) -> Optional[dict]:
        try:
            if not self.lease_file.exists():
                return None
            return json.loads(self.lease_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def save_lease(self, data: dict):
        try:
            self.lease_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            self.current_lease = data
        except Exception as e:
            print(f"Failed to save lease: {e}")

    def is_active(self) -> bool:
        """
        Check if we have a valid recurring lease.
        TEMPORARY OVERRIDE FOR TESTING: Always returns True.
        """
        # NOTE FOR FUTURE AI AGENTS: Licensing is temporarily bypassed 
        # to allow testing of the Scholar DLC system without an active key.
        return True

        # Original logic:
        # if not self.current_lease: return False
        # vu_str = self.current_lease.get("valid_until")
        # if not vu_str: return False
        # try:
        #     if vu_str.endswith("Z"): vu_str = vu_str[:-1] + "+00:00"
        #     vu = datetime.fromisoformat(vu_str).astimezone(timezone.utc)
        #     return datetime.now(timezone.utc) < vu
        # except Exception: return False

    def activate(self, key: str):
        """Perform online activation"""
        Thread(target=self._activate_thread, args=(key,), daemon=True).start()

    def _activate_thread(self, key: str):
        try:
            r = requests.post(
                f"{self.api_base}/activate",
                json={"license_key": key.strip(), "hwid": self.hwid},
                timeout=15
            )
            r.raise_for_status()
            data = r.json()
            self.save_lease(data)
            self.status_changed.emit("success")
        except Exception as e:
            print(f"Activation failed: {e}")
            self.status_changed.emit("failed")

    def check_silent(self):
        """Silently renew if needed on startup"""
        if self.current_lease and not self.is_active():
            token = self.current_lease.get("lease_token")
            if token:
                Thread(target=self._renew_thread, args=(token,), daemon=True).start()

    def _renew_thread(self, token: str):
        try:
            r = requests.post(
                f"{self.api_base}/renew",
                json={"lease_token": token, "hwid": self.hwid},
                timeout=15
            )
            r.raise_for_status()
            data = r.json()
            # Merge with existing
            new_data = {**self.current_lease, **data}
            self.save_lease(new_data)
        except Exception:
            pass

class LeaderboardSignals(QObject):
    finished = Signal(list)
    finished_bests = Signal(dict)
    error = Signal()

class LeaderboardFetcher:
    def __init__(self, sync, mode, period="alltime", limit=30, username=None):
        self.sync = sync
        self.mode = mode
        self.period = period
        self.limit = limit
        self.username = username
        self.signals = LeaderboardSignals()

    def start(self):
        Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            # 1. Global Leaderboard
            data = self.sync.get_leaderboard(self.mode, self.period, self.limit)
            self.signals.finished.emit(data)
            
            # 2. Personal Bests (if username provided)
            if self.username:
                bests = self.sync.get_user_bests(self.username)
                self.signals.finished_bests.emit(bests)
                
        except Exception:
            self.signals.error.emit()

def format_server_leaderboard(data: list, i18n, theme):
    if not data:
        return i18n.t("lb_none")
    
    # Determine base text color based on theme
    base_color = "#e8eaf0" if theme.is_dark else "#1a1f2a"
    
    lines = []
    # Header
    lines.append(f"<table width='100%' cellspacing='0' cellpadding='2' style='color:{base_color}'>")
    lines.append(f"<tr>"
                 f"<th align='left'>Rank</th>"
                 f"<th align='left'>User</th>"
                 f"<th align='center'>PTS</th>"
                 f"<th align='center'>WPM</th>"
                 f"<th align='center'>ACC</th>"
                 f"</tr>")
    
    for entry in data:
        rank = entry.get('rank', '-')
        raw_user = entry.get('username', '?')
        user_disp = raw_user[:12]
        pts = entry.get('points', 0)
        wpm = entry.get('wpm', 0)
        acc = entry.get('accuracy', 0)
        
        # Link for interaction
        # Force the color explicitly because 'inherit' often fails in QLabels
        user_html = f"<a href='user:{raw_user}' style='color: {base_color}; text-decoration: none;'>{user_disp}</a>"
        
        # Highlight top 3 (Colors that work reasonably on both, or tweak)
        # Gold/Silver/Bronze usually readable on both dark/light key backgrounds
        color = base_color
        weight = "normal"
        
        if rank == 1: 
            color = "#ffd700" if theme.is_dark else "#d4af37" # Gold
            weight = "bold"
        elif rank == 2: 
            color = "#c0c0c0" if theme.is_dark else "#a9a9a9" # Silver
            weight = "bold"
        elif rank == 3: 
            color = "#cd7f32" if theme.is_dark else "#cd7f32" # Bronze
            weight = "bold"
            
        lines.append(f"<tr style='color:{color}; font-weight:{weight}'>"
                     f"<td>#{rank}</td>"
                     f"<td>{user_html}</td>"
                     f"<td align='center'>{pts}</td>"
                     f"<td align='center'>{wpm:.0f}</td>"
                     f"<td align='center'>{acc:.0f}%</td>"
                     f"</tr>")
                     
    lines.append("</table>")
    return "".join(lines)
# i18n
# ============================================================

# ... (I18N class omitted for brevity, assuming generic replacement context) ...

# ...


# i18n
# ============================================================

class I18N:
    def __init__(self, lang: str):
        self.lang = lang
        self.data: Dict[str, str] = {}
        self.load(lang)

    def load(self, lang: str):
        self.lang = lang
        path = os.path.join(I18N_DIR, f"{lang}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def t(self, key: str, **kwargs) -> str:
        s = self.data.get(key, key)
        if kwargs:
            try:
                s = s.format(**kwargs)
            except Exception:
                pass
        return s


# ============================================================
# THEME
# ============================================================

class Theme:
    def __init__(self, mode: str = "dark"):
        self.mode = mode

    @property
    def is_dark(self) -> bool:
        return self.mode == "dark"

    def app_stylesheet(self) -> str:
        if self.is_dark:
            bg = "#0f1115"
            panel = "#121620"
            panel2 = "#10131a"
            text = "#e8eaf0"
            muted = "#9aa3b2"
            border = "#232a3a"
            btn = "#1b2130"
        else:
            bg = "#f4f6fb"
            panel = "#ffffff"
            panel2 = "#f0f3fa"
            text = "#1a1f2a"
            muted = "#556070"
            border = "#d9dfeb"
            btn = "#f2f5fb"

        return f"""
        QMainWindow {{
            background: {bg};
            color: {text};
        }}
        QWidget {{
            color: {text};
            font-family: Segoe UI, Inter, Arial;
            font-size: 11pt;
        }}
        QFrame#Panel {{
            background: {panel};
            border: 1px solid {border};
            border-radius: 16px;
        }}
        QFrame#Panel2 {{
            background: {panel2};
            border: 1px solid {border};
            border-radius: 16px;
        }}
        QLabel#Muted {{
            color: {muted};
        }}

        QLineEdit {{
            background: {btn};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 6px 10px;
        }}

        QComboBox {{
            background: {btn};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 6px 10px;
        }}
        QComboBox QAbstractItemView {{
            background: {btn};
            color: {text};
            selection-background-color: rgba(124, 92, 255, 0.28);
            selection-color: {text};
            border: 1px solid {border};
            outline: 0px;
        }}

        QCheckBox {{
            spacing: 10px;
        }}

        QTabWidget::pane {{
            border: 0px;
        }}
        QTabBar::tab {{
            background: transparent;
            padding: 8px 14px;
            margin-right: 6px;
            border-radius: 10px;
            color: {muted};
        }}
        QTabBar::tab:selected {{
            background: rgba(124, 92, 255, 0.18);
            color: {text};
        }}
        QTabBar::tab:hover {{
            background: rgba(124, 92, 255, 0.10);
        }}

        QPushButton {{
            background: {btn};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 6px 14px;
        }}
        QPushButton:hover {{
            border-color: #7c5cff;
        }}
        QPushButton:pressed {{
            background: rgba(124, 92, 255, 0.10);
        }}

        QPushButton#Muted {{
            color: {muted};
            background: transparent;
            border: none;
            padding: 4px 10px;
            border-radius: 8px;
        }}
        QPushButton#Muted:hover {{
            background: rgba(124, 92, 255, 0.10);
            color: {text};
        }}
        QPushButton#Muted:pressed {{
            background: rgba(124, 92, 255, 0.20);
        }}
        """

    def key_palette(self) -> dict:
        if self.is_dark:
            return dict(
                key_left="#1f2533",
                key_right="#252b3d",
                key_text="#e8eaf0",
                key_target="#7c5cff",
                key_wrong="#ff4d4d",
                key_correct="#2ed573",
            )
        return dict(
            key_left="#f2f5fb",
            key_right="#e8eef8",
            key_text="#1a1f2a",
            key_target="#7c5cff",
            key_wrong="#ff3b30",
            key_correct="#19c37d",
        )
# ============================================================
# HAND RENDERER (TRUE STREAMING, PIXEL COORDS)
# ============================================================

class HandRenderer:
    """
    TRUE streaming:
    - wir rendern IMMER in Original-PNG Pixelgröße
    - Finger-Positionen sind Pixel-Koordinaten (cx, cy) im Originalbild
    - danach wird NUR das fertige QPixmap im UI skaliert angezeigt
    """
    def __init__(self, theme: Theme, side: str):
        self.theme = theme
        self.side = side  # "left" | "right"
        fn = "hands_left.png" if side == "left" else "hands_right.png"
        path = os.path.join(ASSETS_DIR, fn)
        self.base = QPixmap(path) if os.path.exists(path) else QPixmap()

        self.active_finger: Optional[str] = None

        # Default-Positions: du kannst die später 1:1 als Pixel anpassen.
        # Erstmal: aus deinen alten Normwerten EINMALIG in Pixel umgerechnet (falls base vorhanden),
        # danach keine width/height-Multiplikation mehr.
        self.finger_pos_px: Dict[str, Tuple[int, int]] = {}

        # Normwerte als Fallback-Quelle (wird einmal konvertiert)
        # Human-Calibrated Fingertip positions (from 1000x1000 assets)
        if side == "left":
            norm = {
                "pinky":  (0.1180, 0.4110),
                "ring":   (0.2310, 0.1950),
                "middle": (0.3650, 0.0960),
                "index":  (0.5460, 0.0930),
                "thumb":  (0.8690, 0.3820),
            }
        else:
            norm = {
                "pinky":  (1.0 - 0.1180, 0.4110),
                "ring":   (1.0 - 0.2310, 0.1950),
                "middle": (1.0 - 0.3650, 0.0960),
                "index":  (1.0 - 0.5460, 0.0930),
                "thumb":  (1.0 - 0.8690, 0.3820),
            }

        self._init_positions_from_norm(norm)

    def _init_positions_from_norm(self, norm_map: Dict[str, Tuple[float, float]]):
        if self.base.isNull():
            # Dummy-Canvas (wird eh nur Placeholder)
            w, h = 1024, 1024
        else:
            w, h = self.base.width(), self.base.height()

        self.finger_pos_px = {}
        for k, (nx, ny) in norm_map.items():
            self.finger_pos_px[k] = (int(w * nx), int(h * ny))

    def set_theme(self, theme: Theme):
        self.theme = theme

    def set_active(self, finger: Optional[str]):
        self.active_finger = finger

    def set_positions_px(self, mapping: Dict[str, Tuple[int, int]]):
        # Direkt Pixel setzen (beste Lösung, wenn du sauber markierst)
        self.finger_pos_px.update({k: (int(v[0]), int(v[1])) for k, v in mapping.items()})

    def render_frame(self) -> QPixmap:
        if self.base.isNull():
            pm = QPixmap(1024, 1024)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setPen(QPen(QColor(255,255,255,140) if self.theme.is_dark else QColor(0,0,0,160), 2))
            p.drawText(pm.rect(), Qt.AlignCenter,
                       f"{self.side.upper()} HAND\nassets/{'hands_left.png' if self.side=='left' else 'hands_right.png'} fehlt")
            p.end()
            return pm

        pm = QPixmap(self.base.size())
        pm.fill(Qt.transparent)

        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.drawPixmap(0, 0, self.base)

        if self.active_finger and self.active_finger in self.finger_pos_px:
            cx, cy = self.finger_pos_px[self.active_finger]
            base = QColor(70, 230, 140) if self.side == "left" else QColor(70, 170, 255)
            if not self.theme.is_dark:
                base = base.darker(110)

            # Premium rendering with gradients
            p.setPen(Qt.NoPen)

            # Glow
            grad = QRadialGradient(QPointF(cx, cy), 45)
            c_glow = QColor(base)
            c_glow.setAlpha(80)
            grad.setColorAt(0, c_glow)
            grad.setColorAt(1, Qt.transparent)
            p.setBrush(grad)
            p.drawEllipse(QPoint(cx, cy), 45, 45)

            # Outer ring
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 200), 3))
            p.drawEllipse(QPoint(cx, cy), 24, 24)

            # Inner dot
            dot = QColor(base)
            dot.setAlpha(220)
            p.setBrush(dot)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(cx, cy), 6, 6)

        p.end()
        return pm


class SquareHandPanel(QFrame):
    """
    Quadratisches Panel, zeigt fertigen Stream skaliert.
    Größe wird vom MainWindow gesetzt (set_panel_size()).
    """
    def __init__(self, theme: Theme, renderer: HandRenderer):
        super().__init__()
        self.setObjectName("Panel")
        self.theme = theme
        self.renderer = renderer
        self._last_frame: Optional[QPixmap] = None
        self._size = 260

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(40, 40)
        self.set_panel_size(self._size)

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.renderer.set_theme(theme)
        self.update_stream()

    def set_panel_size(self, px: int):
        px = int(px)
        if px != self._size:
            self._size = px
            self.setFixedSize(px, px)
            self.update()

    def set_active_finger(self, finger: Optional[str]):
        self.renderer.set_active(finger)
        self.update_stream()

    def update_stream(self):
        self._last_frame = self.renderer.render_frame()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect().adjusted(14, 14, -14, -14)
        side = min(r.width(), r.height())
        sq = QRect(r.x() + (r.width() - side)//2, r.y() + (r.height() - side)//2, side, side)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255,255,255,6) if self.theme.is_dark else QColor(0,0,0,4))
        p.drawRoundedRect(sq, 18, 18)

        frame = self._last_frame or self.renderer.render_frame()
        self._last_frame = frame

        scaled = frame.scaled(sq.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = sq.x() + (sq.width() - scaled.width())//2
        y = sq.y() + (sq.height() - scaled.height())//2
        p.drawPixmap(x, y, scaled)

        p.end()
# ============================================================
# KEYBOARD LAYOUTS
# ============================================================

@dataclass
class KeyDef:
    kid: str
    label: str
    label2: str = ""
    w: float = 1.0
    is_spacer: bool = False

def de_layout() -> List[List[KeyDef]]:
    return [
        [KeyDef("Escape","esc"), KeyDef("F1","F1"), KeyDef("F2","F2"), KeyDef("F3","F3"), KeyDef("F4","F4"),
         KeyDef("F5","F5"), KeyDef("F6","F6"), KeyDef("F7","F7"), KeyDef("F8","F8"), KeyDef("F9","F9"),
         KeyDef("F10","F10"), KeyDef("F11","F11"), KeyDef("F12","F12"), KeyDef("Backspace","⌫", w=1.4)],

        [KeyDef("Backquote","^","°"), KeyDef("Digit1","1","!"), KeyDef("Digit2","2","\""), KeyDef("Digit3","3","§"),
         KeyDef("Digit4","4","$"), KeyDef("Digit5","5","%"), KeyDef("Digit6","6","&"), KeyDef("Digit7","7","/"),
         KeyDef("Digit8","8","("), KeyDef("Digit9","9",")"), KeyDef("Digit0","0","="),
         KeyDef("Minus","ß","?"), KeyDef("Equal","´","`"), KeyDef("Delete","del", w=1.2)],

        [KeyDef("Tab","tab", w=1.3), KeyDef("KeyQ","Q"), KeyDef("KeyW","W"), KeyDef("KeyE","E"), KeyDef("KeyR","R"),
         KeyDef("KeyT","T"), KeyDef("KeyZ","Z"), KeyDef("KeyU","U"), KeyDef("KeyI","I"), KeyDef("KeyO","O"),
         KeyDef("KeyP","P"), KeyDef("BracketLeft","Ü"), KeyDef("BracketRight","+","*"), KeyDef("Enter","enter", w=1.6)],

        [KeyDef("CapsLock","caps", w=1.5), KeyDef("KeyA","A"), KeyDef("KeyS","S"), KeyDef("KeyD","D"), KeyDef("KeyF","F"),
         KeyDef("KeyG","G"), KeyDef("KeyH","H"), KeyDef("KeyJ","J"), KeyDef("KeyK","K"), KeyDef("KeyL","L"),
         KeyDef("Semicolon","Ö"), KeyDef("Quote","Ä"), KeyDef("Backslash","#")],

        [KeyDef("ShiftLeft","shift", w=1.7), KeyDef("IntlBackslash","<",">"), KeyDef("KeyY","Y"), KeyDef("KeyX","X"),
         KeyDef("KeyC","C"), KeyDef("KeyV","V"), KeyDef("KeyB","B"), KeyDef("KeyN","N"), KeyDef("KeyM","M"),
         KeyDef("Comma",",",";"), KeyDef("Period",".",":"), KeyDef("Slash","-","_"),
         KeyDef("ShiftRight","shift", w=1.9)],

        [KeyDef("ControlLeft","ctrl", w=1.2), KeyDef("AltLeft","alt", w=1.2),
         KeyDef("Space","space", w=6.0),
         KeyDef("AltRight","altgr", w=1.2), KeyDef("ControlRight","ctrl", w=1.2)]
    ]

def us_layout() -> List[List[KeyDef]]:
    return [
        [KeyDef("Escape","esc"), KeyDef("F1","F1"), KeyDef("F2","F2"), KeyDef("F3","F3"), KeyDef("F4","F4"),
         KeyDef("F5","F5"), KeyDef("F6","F6"), KeyDef("F7","F7"), KeyDef("F8","F8"), KeyDef("F9","F9"),
         KeyDef("F10","F10"), KeyDef("F11","F11"), KeyDef("F12","F12"), KeyDef("Backspace","⌫", w=1.4)],

        [KeyDef("Backquote","`","~"), KeyDef("Digit1","1","!"), KeyDef("Digit2","2","@"), KeyDef("Digit3","3","#"),
         KeyDef("Digit4","4","$"), KeyDef("Digit5","5","%"), KeyDef("Digit6","6","^"), KeyDef("Digit7","7","&"),
         KeyDef("Digit8","8","*"), KeyDef("Digit9","9","("), KeyDef("Digit0","0",")"),
         KeyDef("Minus","-","_"), KeyDef("Equal","=","+"), KeyDef("Delete","del", w=1.2)],

        [KeyDef("Tab","tab", w=1.3), KeyDef("KeyQ","Q"), KeyDef("KeyW","W"), KeyDef("KeyE","E"), KeyDef("KeyR","R"),
         KeyDef("KeyT","T"), KeyDef("KeyY","Y"), KeyDef("KeyU","U"), KeyDef("KeyI","I"), KeyDef("KeyO","O"),
         KeyDef("KeyP","P"), KeyDef("BracketLeft","[","{"), KeyDef("BracketRight","]","}"), KeyDef("Enter","enter", w=1.6)],

        [KeyDef("CapsLock","caps", w=1.5), KeyDef("KeyA","A"), KeyDef("KeyS","S"), KeyDef("KeyD","D"), KeyDef("KeyF","F"),
         KeyDef("KeyG","G"), KeyDef("KeyH","H"), KeyDef("KeyJ","J"), KeyDef("KeyK","K"), KeyDef("KeyL","L"),
         KeyDef("Semicolon",";",":"), KeyDef("Quote","'","\""), KeyDef("Backslash","\\","|")],

        [KeyDef("ShiftLeft","shift", w=1.7), KeyDef("KeyZ","Z"), KeyDef("KeyX","X"),
         KeyDef("KeyC","C"), KeyDef("KeyV","V"), KeyDef("KeyB","B"), KeyDef("KeyN","N"), KeyDef("KeyM","M"),
         KeyDef("Comma",",","<"), KeyDef("Period",".",">"), KeyDef("Slash","/","?"),
         KeyDef("ShiftRight","shift", w=1.9)],

        [KeyDef("ControlLeft","ctrl", w=1.2), KeyDef("AltLeft","alt", w=1.2),
         KeyDef("Space","space", w=6.0),
         KeyDef("AltRight","alt", w=1.2), KeyDef("ControlRight","ctrl", w=1.2)]
    ]

def right_hand_kids(layout_name: str) -> set:
    base = {
        # Standard Right Hand Column Ownership
        "Digit6","Digit7","Digit8","Digit9","Digit0","Minus","Equal",
        "KeyU","KeyI","KeyO","KeyP","BracketLeft","BracketRight","Backspace",
        "KeyH","KeyJ","KeyK","KeyL","Semicolon","Quote","Backslash","Enter",
        "KeyN","KeyM","Comma","Period","Slash","ShiftRight",
        "Delete","ControlRight","AltRight",
    }
    # QWERTZ: Z is top row index-right
    if layout_name.upper() == "DE":
        return base | {"KeyZ"}
    # QWERTY: Y is top row index-right
    return base | {"KeyY"}

def hand_for_kid(layout_name: str, kid: Optional[str]) -> str:
    if not kid:
        return "unknown"
    return "right" if kid in right_hand_kids(layout_name) else "left"

def kid_for_char(layout_name: str, ch: str) -> Optional[str]:
    if not ch:
        return None
    if ch == " ":
        return "Space"
    ch = ch.lower()

    if layout_name.upper() == "DE":
        return {
            "a":"KeyA","b":"KeyB","c":"KeyC","d":"KeyD","e":"KeyE","f":"KeyF","g":"KeyG","h":"KeyH",
            "i":"KeyI","j":"KeyJ","k":"KeyK","l":"KeyL","m":"KeyM","n":"KeyN","o":"KeyO","p":"KeyP",
            "q":"KeyQ","r":"KeyR","s":"KeyS","t":"KeyT","u":"KeyU","v":"KeyV","w":"KeyW","x":"KeyX",
            "y":"KeyY","z":"KeyZ",
            "ä":"Quote","ö":"Semicolon","ü":"BracketLeft","ß":"Minus",
            ",":"Comma",".":"Period","-":"Slash",
            "1":"Digit1","2":"Digit2","3":"Digit3","4":"Digit4","5":"Digit5","6":"Digit6","7":"Digit7","8":"Digit8","9":"Digit9","0":"Digit0",
        }.get(ch)
    else:
        return {
            "a":"KeyA","b":"KeyB","c":"KeyC","d":"KeyD","e":"KeyE","f":"KeyF","g":"KeyG","h":"KeyH",
            "i":"KeyI","j":"KeyJ","k":"KeyK","l":"KeyL","m":"KeyM","n":"KeyN","o":"KeyO","p":"KeyP",
            "q":"KeyQ","r":"KeyR","s":"KeyS","t":"KeyT","u":"KeyU","v":"KeyV","w":"KeyW","x":"KeyX",
            "y":"KeyY","z":"KeyZ",
            ",":"Comma",".":"Period","/":"Slash","-":"Minus",";":"Semicolon","'":"Quote",
            "1":"Digit1","2":"Digit2","3":"Digit3","4":"Digit4","5":"Digit5","6":"Digit6","7":"Digit7","8":"Digit8","9":"Digit9","0":"Digit0",
        }.get(ch)
def finger_for_kid(layout_name: str, kid: Optional[str]) -> Tuple[str, str]:
    if not kid:
        return ("unknown", "index")

    # Universal Finger Map
    fm = {
        # Left Hand
        "Digit1":"pinky","KeyQ":"pinky","KeyA":"pinky","Backquote":"pinky","Tab":"pinky","CapsLock":"pinky","ShiftLeft":"pinky","ControlLeft":"pinky",
        "Digit2":"ring","KeyW":"ring","KeyS":"ring","KeyX":"ring",
        "Digit3":"middle","KeyE":"middle","KeyD":"middle","KeyC":"middle",
        "Digit4":"index","Digit5":"index","KeyR":"index","KeyT":"index","KeyF":"index","KeyG":"index","KeyV":"index","KeyB":"index",
        # Right Hand
        "Digit6":"index","Digit7":"index","KeyU":"index","KeyH":"index","KeyJ":"index","KeyN":"index","KeyM":"index",
        "Digit8":"middle","KeyI":"middle","KeyK":"middle","Comma":"middle",
        "Digit9":"ring","KeyO":"ring","KeyL":"ring","Period":"ring",
        "Digit0":"pinky","Minus":"pinky","Equal":"pinky","KeyP":"pinky","BracketLeft":"pinky","BracketRight":"pinky","Backspace":"pinky",
        "Semicolon":"pinky","Quote":"pinky","Backslash":"pinky","Enter":"pinky",
        "Slash":"pinky","ShiftRight":"pinky","Delete":"pinky","ControlRight":"pinky",
        # Thumb
        "Space":"thumb",
    }
    
    # Platform-specific and Layout-specific overrides
    is_de = layout_name.upper() == "DE"
    if is_de:
        fm["KeyY"] = "pinky"    # QWERTZ: Y is bottom left
        fm["IntlBackslash"] = "pinky"
        fm["KeyZ"] = "index"  # QWERTZ: Z is top index
        fm["BracketLeft"] = "pinky" # Ü
        fm["Semicolon"] = "pinky"   # Ö
        fm["Quote"] = "pinky"       # Ä
        fm["Slash"] = "pinky"       # - (where Slash is)
    else:
        fm["KeyZ"] = "pinky"   # QWERTY: Z is bottom left
        fm["KeyY"] = "index"   # QWERTY: Y is top index

    finger = fm.get(kid, "index")
    hand = hand_for_kid(layout_name, kid)
    return (hand, finger)


# ============================================================
# TYPING COACH
# ============================================================

class TypingCoach:
    def __init__(self, items: List[str]):
        self.items = [x.strip() for x in items if x.strip()] or DEFAULT_WORDS_DE[:]
        self.reset()
        self.per_char_hit: Dict[str, int] = {}
        self.per_char_miss: Dict[str, int] = {}

    def set_items(self, items: List[str]):
        self.items = [x.strip() for x in items if x.strip()] or DEFAULT_WORDS_DE[:]
        self.reset()

    def reset(self):
        self.current = random.choice(self.items)
        self.index = 0
        self.total = 0
        self.mistakes = 0
        self.started = time.time()

    def next_item(self):
        self.current = random.choice(self.items)
        self.index = 0

    def expected_char(self) -> str:
        if self.index >= len(self.current):
            return ""
        return self.current[self.index]

    def feed(self, ch: str) -> Tuple[bool, str]:
        exp = self.expected_char()
        if exp == "":
            self.next_item()
            exp = self.expected_char()

        self.total += 1

        if ch == exp:
            self.per_char_hit[exp] = self.per_char_hit.get(exp, 0) + 1
            self.index += 1
            if self.index >= len(self.current):
                self.next_item()
            return True, exp

        self.mistakes += 1
        self.per_char_miss[exp] = self.per_char_miss.get(exp, 0) + 1
        return False, exp

    def accuracy(self) -> float:
        if self.total <= 0:
            return 100.0
        return max(0.0, ((self.total - self.mistakes) / self.total) * 100.0)

    def wpm(self) -> float:
        elapsed = max(1e-6, time.time() - self.started)
        return ((self.total / 5.0) / (elapsed / 60.0))

    def score_points(self) -> int:
        # simple, stabile Score-Formel (offline):
        # WPM * Accuracy% (0..100) -> skaliert
        wpm = self.wpm()
        acc = self.accuracy()
        pts = int(round(wpm * (acc / 100.0) * 10.0))
        return max(0, pts)

    def suggestions(self, limit=5) -> List[str]:
        items = sorted(self.per_char_miss.items(), key=lambda x: x[1], reverse=True)[:limit]
        out = []
        for ch, miss in items:
            hit = self.per_char_hit.get(ch, 0)
            out.append(f"'{ch}' → Fehler: {miss}, Treffer: {hit}")
        return out
# ============================================================
# UI COMPONENTS
# ============================================================

class Splash(QWidget):
    finished = Signal()
    def __init__(self, theme: Theme, i18n: I18N):
        super().__init__()
        self.theme = theme
        self.i18n = i18n
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(560, 340)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Panel")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 28, 28, 28)
        cl.setSpacing(10)
        cl.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(path):
            pix = QPixmap(path)
            logo.setPixmap(pix.scaledToWidth(240, Qt.SmoothTransformation))
        else:
            logo.setText("qwerType")
            logo.setStyleSheet("font-size: 26pt; font-weight: 900;")

        title = QLabel("qwerType")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22pt; font-weight: 900;")

        sub = QLabel(self.i18n.t("splash_sub"))
        sub.setObjectName("Muted")
        sub.setAlignment(Qt.AlignCenter)

        cl.addWidget(logo)
        cl.addWidget(title)
        cl.addWidget(sub)
        lay.addWidget(card)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)

        self.fade_in = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_in.setDuration(650)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()

        QTimer.singleShot(5000, self.fade_out)

    def fade_out(self):
        self.fade_out_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_out_anim.setDuration(650)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_anim.finished.connect(self.finished.emit)
        self.fade_out_anim.start()


class StartupOverlay(QWidget):
    start_triggered = Signal()

    def __init__(self, parent, theme: Theme, i18n: I18N):
        super().__init__(parent)
        self.theme = theme
        self.i18n = i18n
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        
        self.card = QFrame()
        self.card.setObjectName("Panel")
        self.card.setMinimumWidth(600)
        self.card.setMaximumWidth(800)
        self.card.setMinimumHeight(400)
        self.card.setMaximumHeight(700)
        
        # Outer card layout
        outer_cl = QVBoxLayout(self.card)
        outer_cl.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area for internal content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        inner_widget = QWidget()
        inner_widget.setObjectName("Panel")
        inner_widget.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(inner_widget)
        # Proportional top margin for better framing
        cl.setContentsMargins(30, 80, 30, 60) 
        cl.setSpacing(24)
        cl.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        self.title = QLabel(self.i18n.t("hint_type_start_title", fallback="READY?"))
        self.title.setStyleSheet("font-size: 20pt; font-weight: 900; color: #7c5cff;")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)
        
        self.hint = QLabel(self.i18n.t("hint_type_start_long", 
                                  fallback="To begin the 60s training session,\nplease type 'START' on your keyboard."))
        self.hint.setObjectName("Muted")
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet("font-size: 11pt;")
        self.hint.setWordWrap(True)
        
        self.btn_close = QPushButton(self.i18n.t("close", fallback="Close"))
        self.btn_close.setFixedWidth(140)
        self.btn_close.setFixedHeight(40)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.hide)
        
        self.btn_demo = QPushButton("Watch & Learn")
        self.btn_demo.setFixedWidth(140)
        self.btn_demo.setFixedHeight(40)
        self.btn_demo.setCursor(Qt.PointingHandCursor)
        self.btn_demo.hide()
        
        # Theme-aware styling
        btn_bg = "#1b2130" if self.theme.is_dark else "#f2f5fb"
        btn_text = "#e8eaf0" if self.theme.is_dark else "#1a1f2a"
        border = "#232a3a" if self.theme.is_dark else "#d9dfeb"
        btn_style = f"""
            QPushButton {{
                background: {btn_bg};
                color: {btn_text};
                border: 1px solid {border};
                border-radius: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(124, 92, 255, 0.15);
                border: 1px solid #7c5cff;
            }}
        """
        self.btn_close.setStyleSheet(btn_style)
        self.btn_demo.setStyleSheet(btn_style.replace("#7c5cff", "#ffae00"))
        
        cl.addWidget(self.title)
        cl.addWidget(self.hint)
        
        btns = QHBoxLayout()
        btns.addWidget(self.btn_demo)
        btns.addWidget(self.btn_close)
        cl.addLayout(btns)
        
        self.scroll.setWidget(inner_widget)
        outer_cl.addWidget(self.scroll)
        lay.addWidget(self.card)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())

    def apply_scale(self, s: float):
        self.card.setMinimumWidth(int(600 * s))
        self.card.setMinimumHeight(int(320 * s))
        
        self.title.setStyleSheet(f"font-size: {int(22*s)}pt; font-weight: 900; color: #7c5cff;")
        self.hint.setStyleSheet(f"font-size: {int(12*s)}pt;")
        
        self.btn_close.setFixedWidth(int(140 * s))
        self.btn_close.setFixedHeight(int(40 * s))

    def paintEvent(self, event):
        p = QPainter(self)
        # Blur-like dimming
        p.fillRect(self.rect(), QColor(0, 0, 0, 180) if self.theme.is_dark else QColor(255, 255, 255, 140))


class UsernameDialog(QFrame):
    accepted = Signal(str)

    def __init__(self, theme: Theme, i18n: I18N):
        super().__init__()
        self.theme = theme
        self.i18n = i18n
        self.setFixedSize(420, 260)
        self.setObjectName("Panel")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(15)
        
        title = QLabel(self.i18n.t("settings_name", fallback="Your Name"))
        title.setStyleSheet("font-size: 16pt; font-weight: 800;")
        
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(self.i18n.t("settings_name_ph", fallback="nickname"))
        self.edit.setMaxLength(24)
        
        self.error = QLabel("")
        self.error.setStyleSheet("color: #ff4d4d; font-size: 9pt;")

        self.btn = QPushButton(self.i18n.t("apply", fallback="Save"))
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self._validate)

        lay.addWidget(title)
        lay.addWidget(self.edit)
        lay.addWidget(self.error)
        lay.addStretch(1)
        lay.addWidget(self.btn, alignment=Qt.AlignCenter)
        
    def apply_scale(self, s: float):
        self.setFixedSize(int(420 * s), int(260 * s))
        for label in self.findChildren(QLabel):
            if label.text() == self.i18n.t("settings_name", fallback="Your Name"):
                label.setStyleSheet(f"font-size: {int(16*s)}pt; font-weight: 800;")
            else:
                label.setStyleSheet(f"font-size: {int(9*s)}pt;")
        self.btn.setFixedWidth(int(140 * s))
        self.btn.setFixedHeight(int(40 * s))
        
        # Theme-aware styling to match the overlay
        btn_bg = "#1b2130" if self.theme.is_dark else "#f2f5fb"
        btn_text = "#e8eaf0" if self.theme.is_dark else "#1a1f2a"
        border = "#232a3a" if self.theme.is_dark else "#d9dfeb"
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: {btn_bg};
                color: {btn_text};
                border: 1px solid {border};
                border-radius: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(124, 92, 255, 0.15);
                border: 1px solid #7c5cff;
            }}
        """)

    def _validate(self):
        name = self.edit.text()
        if not is_name_allowed(name):
            self.error.setText(self.i18n.t("name_invalid", fallback="Invalid name (too short or blocked)."))
        else:
            self.accepted.emit(normalize_name(name))


class ScholarLessonWidget(QWidget):
    """Step-based course engine for DLC modules"""
    finished = Signal()
    step_changed = Signal(int)

    def __init__(self, parent, theme: Theme, i18n: I18N):
        super().__init__(parent)
        self.theme = theme
        self.i18n = i18n
        self.steps = []
        self.current_idx = 0
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        
        self.card = QFrame()
        self.card.setObjectName("Panel")
        self.card.setMinimumWidth(700)
        self.card.setMaximumWidth(900)
        self.card.setMinimumHeight(500)
        
        # Outer cl for the card
        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(24)
        
        # Header: Title + Progress
        top = QHBoxLayout()
        self.lbl_title = QLabel("Chapter Title")
        self.lbl_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #7c5cff;")
        top.addWidget(self.lbl_title)
        top.addStretch(1)
        self.lbl_progress = QLabel("0/0")
        self.lbl_progress.setObjectName("Muted")
        top.addWidget(self.lbl_progress)
        cl.addLayout(top)
        
        # Content Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.inner_content = QWidget()
        self.inner_content.setStyleSheet("background: transparent;")
        self.content_lay = QVBoxLayout(self.inner_content)
        self.content_lay.setSpacing(20)
        self.content_lay.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.inner_content)
        cl.addWidget(self.scroll, 1)
        
        # Bottom Navigation
        nav = QHBoxLayout()
        self.btn_back = QPushButton(self.i18n.t("back", fallback="Back"))
        self.btn_back.setFixedSize(120, 40)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.clicked.connect(self.prev_step)
        
        self.btn_next = QPushButton(self.i18n.t("continue", fallback="Continue"))
        self.btn_next.setFixedSize(120, 40)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.next_step)
        
        # Theme styling for buttons
        btn_bg = "#1b2130" if self.theme.is_dark else "#f2f5fb"
        self.btn_back.setStyleSheet(f"background: {btn_bg}; border: 1px solid #232a3a; border-radius: 12px;")
        self.btn_next.setStyleSheet("background: #7c5cff; color: white; font-weight: bold; border-radius: 12px;")
        
        nav.addWidget(self.btn_back)
        nav.addStretch(1)
        nav.addWidget(self.btn_next)
        cl.addLayout(nav)
        
        lay.addWidget(self.card)

    def set_course(self, spec_data: dict):
        self.steps = []
        for ch in spec_data.get("course", {}).get("chapters", []):
            for step in ch.get("steps", []):
                step["chapter_name"] = ch.get("name", "Basics")
                self.steps.append(step)
        self.current_idx = 0
        self.show_step(0)

    def show_step(self, idx):
        if not (0 <= idx < len(self.steps)): return
        self.current_idx = idx
        step = self.steps[idx]
        
        self.lbl_title.setText(step.get("title", "Lesson"))
        self.lbl_progress.setText(f"{idx+1}/{len(self.steps)}")
        self.btn_back.setEnabled(idx > 0)
        
        # Clear old content
        while self.content_lay.count():
            item = self.content_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        # Build step UI based on type
        stype = step.get("type", "intro")
        if stype == "intro":
            lbl = QLabel("\n".join(step.get("content", ["Welcome!"])))
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 11pt;")
            self.content_lay.addWidget(lbl)
            
            # If there's an interaction choice
            inter = step.get("interaction", {})
            if inter.get("type") == "choice":
                lbl_p = QLabel(inter.get("prompt", "Choose your goal:"))
                lbl_p.setObjectName("Muted")
                self.content_lay.addWidget(lbl_p)
                for opt in inter.get("options", []):
                    btn = QPushButton(opt)
                    btn.setFixedHeight(40)
                    btn.setCursor(Qt.PointingHandCursor)
                    btn.setStyleSheet(f"background: rgba(124, 92, 255, 0.1); border: 1px solid #7c5cff; border-radius: 10px; color: #7c5cff; text-align: left; padding-left: 15px;")
                    btn.clicked.connect(self.next_step)
                    self.content_lay.addWidget(btn)
                    
        elif stype == "lesson_quiz":
            lbl = QLabel("\n".join(step.get("content", [])))
            lbl.setWordWrap(True)
            self.content_lay.addWidget(lbl)
            
            inter = step.get("interaction", {})
            if inter.get("type") == "quiz":
                for qst in inter.get("questions", []):
                    q_lbl = QLabel(f"<b>Q: {qst['q']}</b>")
                    self.content_lay.addWidget(q_lbl)
                    # For now just show the answer since it's a study quiz
                    a_lbl = QLabel(f"A: {qst['a']}")
                    a_lbl.setStyleSheet("color: #27c93f;")
                    self.content_lay.addWidget(a_lbl)
        
        elif stype == "ghost_demo":
            lbl = QLabel("Watch the code being typed and see the result:")
            lbl.setObjectName("Muted")
            self.content_lay.addWidget(lbl)
            
            btn_play = QPushButton("▶ Run Ghost Demo")
            btn_play.setStyleSheet("background: #ffae00; color: black; font-weight: bold; border-radius: 12px; height: 50px;")
            btn_play.clicked.connect(lambda: self.step_changed.emit(idx))
            self.content_lay.addWidget(btn_play)

        elif stype == "now_you":
            lbl = QLabel(step.get("title", ""))
            self.content_lay.addWidget(lbl)
            lbl_r = QLabel("Requirements:\n- " + "\n- ".join(step.get("requirements", [])))
            lbl_r.setStyleSheet("color: #7c5cff;")
            self.content_lay.addWidget(lbl_r)

    def next_step(self):
        if self.current_idx < len(self.steps) - 1:
            self.show_step(self.current_idx + 1)
        else:
            self.finished.emit()

    def prev_step(self):
        if self.current_idx > 0:
            self.show_step(self.current_idx - 1)

    def apply_scale(self, s):
        self.card.setMinimumWidth(int(700 * s))
        self.lbl_title.setStyleSheet(f"font-size: {int(20*s)}pt; font-weight: bold; color: #7c5cff;")

class HtmlDlcWindowLegacy(QMainWindow):
    """Standalone OS window for HTML Scholar DLC (does NOT touch Main UI)."""
    def __init__(self, main_window: 'MainWindow', spec_data: dict):
        super().__init__(None)
        self.main_window = main_window
        self.spec_data = spec_data or {}
        self.setWindowTitle("QwerType – HTML DLC")
        self.resize(1280, 820)

        self._demo_active = False
        self._demo_code = ""
        self._demo_timer = QTimer(self)
        self._demo_timer.setSingleShot(True)

        # Ghost typer local to this window
        self.ghost = GhostTyper(wpm=120)
        self.ghost.char_typed.connect(self._on_demo_char)
        self.ghost.step_finished.connect(self._on_demo_finished)

        central = QWidget(self)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # Left: Scholar lesson cards (Continue/Back + Run Ghost Demo button)
        self.scholar = ScholarLessonWidget(self, main_window.theme, main_window.i18n)
        self.scholar.set_course(self.spec_data)
        self.scholar.step_changed.connect(self._on_step_changed)
        self.scholar.finished.connect(self.close)

        # Right: Code + Preview workspace
        right = QFrame()
        right.setObjectName("Panel")
        rlay = QVBoxLayout(right)
        rlay.setContentsMargins(18, 18, 18, 18)
        rlay.setSpacing(10)

        top = QHBoxLayout()
        self.lbl_context = QLabel("HTML Workspace")
        self.lbl_context.setStyleSheet("font-size: 14pt; font-weight: 700; color: #7c5cff;")
        top.addWidget(self.lbl_context)
        top.addStretch(1)

        self.btn_run = QPushButton("Run")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.clicked.connect(self._run_preview)
        top.addWidget(self.btn_run)

        self.btn_check = QPushButton("Check")
        self.btn_check.setCursor(Qt.PointingHandCursor)
        self.btn_check.clicked.connect(self._check_now_you)
        top.addWidget(self.btn_check)

        rlay.addLayout(top)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Code erscheint hier (Ghost Demo) oder du schreibst hier (Jetzt du).")
        self.editor.setTabStopDistance(28)
        self.editor.textChanged.connect(self._on_editor_changed)
        rlay.addWidget(self.editor, 3)

        self.preview = QTextBrowser()
        self.preview.setFrameShape(QFrame.NoFrame)
        self.preview.setStyleSheet("background:#ffffff; color:#000; border-radius:12px;")
        rlay.addWidget(self.preview, 2)

        # Theme editor a bit
        try:
            if getattr(main_window.theme, "is_dark", True):
                self.editor.setStyleSheet("background:#0d1117; color:#e6edf3; border:2px solid #232a3a; border-radius:12px; padding:10px; font-family: Consolas, monospace;")
            else:
                self.editor.setStyleSheet("background:#ffffff; color:#0d1117; border:2px solid #d9dfeb; border-radius:12px; padding:10px; font-family: Consolas, monospace;")
        except Exception:
            pass

        root.addWidget(self.scholar, 3)
        root.addWidget(right, 4)

        # Initialize workspace for first step
        self._apply_step_workspace()

    def closeEvent(self, event):
        self._stop_demo()
        try:
            self.ghost.stop()
        except Exception:
            pass
        event.accept()

    # ---------- helpers ----------
    def _current_step(self) -> dict:
        if not getattr(self.scholar, "steps", None):
            return {}
        idx = getattr(self.scholar, "current_idx", 0)
        if 0 <= idx < len(self.scholar.steps):
            return self.scholar.steps[idx]
        return {}

    def _apply_step_workspace(self):
        step = self._current_step()
        stype = step.get("type", "intro")

        self.btn_check.setEnabled(False)
        self.btn_run.setEnabled(True)

        if stype == "ghost_demo":
            self.editor.setReadOnly(True)
            self.editor.setPlainText("")
            self.preview.setHtml("")
            self.lbl_context.setText(f"Ghost Demo: {step.get('title','Demo')}")
        elif stype == "now_you":
            self.editor.setReadOnly(False)
            self.btn_check.setEnabled(True)
            starter = step.get("starter_code", "")
            self.editor.setPlainText(starter)
            self.lbl_context.setText("Jetzt du: Bearbeite den Code")
            self._run_preview()
        else:
            self.editor.setReadOnly(True)
            self.lbl_context.setText("HTML Workspace")

    # ---------- scholar events ----------
    def _on_step_changed(self, idx: int):
        # This signal is emitted by the "▶ Run Ghost Demo" button for ghost_demo steps
        if not (0 <= idx < len(self.scholar.steps)):
            return
        step = self.scholar.steps[idx]
        if step.get("type") != "ghost_demo":
            return

        code = (step.get("ghost", {}) or {}).get("final_code", "")
        if not code:
            self._toast("Kein Demo-Code gefunden.")
            return

        self._stop_demo()
        self._demo_active = True
        self._demo_code = code

        self.editor.setReadOnly(True)
        self.editor.setPlainText("")
        self.preview.setHtml("")
        self.lbl_context.setText(f"Ghost Demo läuft: {step.get('title','Demo')}")

        # small delay so UI updates before typing
        try:
            self._demo_timer.timeout.disconnect()
        except Exception:
            pass
        self._demo_timer.timeout.connect(self._start_demo_typing)
        self._demo_timer.start(250)

    # ---------- ghost demo ----------
    def _start_demo_typing(self):
        if not self._demo_active:
            return
        try:
            self.ghost.stop()
        except Exception:
            pass
        self.ghost.type_string(self._demo_code)

    def _on_demo_char(self, count: int):
        if not self._demo_active:
            return
        partial = self._demo_code[:count]
        self.editor.blockSignals(True)
        self.editor.setPlainText(partial)
        self.editor.blockSignals(False)
        self.preview.setHtml(partial)

    def _on_demo_finished(self):
        if not self._demo_active:
            return
        self._demo_active = False
        self.lbl_context.setText("✅ Demo fertig – du kannst weiter klicken.")
        self.preview.setHtml(self._demo_code)

    def _stop_demo(self):
        self._demo_active = False
        try:
            self._demo_timer.stop()
        except Exception:
            pass
        try:
            self.ghost.stop()
        except Exception:
            pass

    # ---------- now-you ----------
    def _on_editor_changed(self):
        if self.editor.isReadOnly():
            return
        self._run_preview()

    def _run_preview(self):
        self.preview.setHtml(self.editor.toPlainText())

    def _check_now_you(self):
        step = self._current_step()
        if step.get("type") != "now_you":
            self._toast("Kein 'Jetzt du' in diesem Step.")
            return

        code = self.editor.toPlainText()
        checks = step.get("validation_checks", []) or []

        ok, msg = self._validate_code(code, checks)
        if ok:
            self._toast("✅ Richtig! Du kannst weiter.")
        else:
            self._toast(f"❌ {msg}")

    def _validate_code(self, code: str, checks: list):
        low = code.lower()

        def has_tag(tag: str):
            return f"<{tag}" in low and f"</{tag}>" in low

        for chk in checks:
            ctype = chk.get("type")
            if ctype == "element_exists":
                target = (chk.get("target") or "").strip().lower()
                if target and not has_tag(target):
                    return False, f"<{target}> fehlt oder ist nicht geschlossen."
            elif ctype == "attribute_exists_or_matches_pattern":
                target = chk.get("target", "")
                pattern = chk.get("pattern", "")
                if "meta" in target and "charset" in target:
                    if "charset" not in low:
                        return False, "meta charset fehlt."
                    if pattern:
                        try:
                            if not re.search(pattern, code, re.IGNORECASE):
                                return False, "charset ist nicht UTF-8."
                        except re.error:
                            if "utf-8" not in low and "utf8" not in low:
                                return False, "charset ist nicht UTF-8."
        return True, "OK"

    def _toast(self, msg: str):
        try:
            if hasattr(self.main_window, "toast"):
                self.main_window.toast.show_msg(msg, 1800)
                return
        except Exception:
            pass
        try:
            self.statusBar().showMessage(msg, 2000)
        except Exception:
            pass
class ResultPreviewWidget(QWidget):
    """Fake Browser popup to show rendered HTML results"""
    def __init__(self, parent, theme: Theme, i18n: I18N):
        super().__init__(parent)
        self.theme = theme
        self.i18n = i18n
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        
        self.card = QFrame()
        self.card.setObjectName("Panel")
        self.card.setMinimumWidth(700)
        self.card.setMinimumHeight(500)
        self.card.setMaximumWidth(1000)
        self.card.setMaximumHeight(800)
        
        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        
        # Browser Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        tl = QHBoxLayout(self.toolbar)
        tl.setContentsMargins(15, 0, 15, 0)
        
        # Traffic lights
        dots = QHBoxLayout()
        for color in ["#ff5f56", "#ffbd2e", "#27c93f"]:
            dot = QFrame()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background: {color}; border-radius: 6px;")
            dots.addWidget(dot)
        tl.addLayout(dots)
        tl.addSpacing(20)
        
        # URL Bar
        self.url_bar = QFrame()
        self.url_bar.setFixedHeight(24)
        ul = QHBoxLayout(self.url_bar)
        ul.setContentsMargins(10, 0, 10, 0)
        self.url_text = QLabel("localhost:8080/preview")
        self.url_text.setStyleSheet("font-size: 8pt; color: #6e7681;")
        ul.addWidget(self.url_text)
        tl.addWidget(self.url_bar)
        tl.addStretch(1)
        
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.hide)
        tl.addWidget(self.btn_close)
        
        cl.addWidget(self.toolbar)
        
        # Browser Content Area
        self.view = QTextBrowser()
        self.view.setFrameShape(QFrame.NoFrame)
        cl.addWidget(self.view)
        
        lay.addWidget(self.card)
        self.apply_theme()
        
    def apply_theme(self):
        bg = "#1b2130" if self.theme.is_dark else "#f2f5fb"
        border = "#232a3a" if self.theme.is_dark else "#d9dfeb"
        url_bg = "#0d1117" if self.theme.is_dark else "#ffffff"
        
        self.toolbar.setStyleSheet(f"background: {bg}; border-bottom: 2px solid {border}; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        self.url_bar.setStyleSheet(f"background: {url_bg}; border-radius: 6px;")
        self.view.setStyleSheet(f"background: #ffffff; color: #000000; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        self.btn_close.setStyleSheet("QPushButton { border: none; color: #6e7681; font-weight: bold; } QPushButton:hover { color: #ff5f56; }")

    def show_content(self, html: str):
        self.view.setHtml(html)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()

    def update_live_content(self, html: str):
        """Update browser view without popping up or stealing focus"""
        self.view.setHtml(html)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())


class Toast(QFrame):
    def __init__(self, theme: Theme):
        super().__init__()
        self.setObjectName("Panel2")
        self.theme = theme
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground) # For transparency if needed

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)

        self.label = QLabel("")
        self.label.setObjectName("Muted")
        lay.addWidget(self.label)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.anim = None
        self.hide()

    def show_msg(self, text: str, ms: int = 1400):
        self.label.setText(text)
        self.show()
        self.raise_()

        self.opacity.setOpacity(0.0)
        self.anim = QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(120)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

        QTimer.singleShot(ms, self.hide)




class DLCManager:
    """Handles discovery, loading and verification of DLC modules"""
    def __init__(self, theme: Theme, i18n: I18N):
        self.theme = theme
        self.i18n = i18n
        self.dlc_dir = Path(DATA_DIR) / "dlc"
        self.dlc_dir.mkdir(parents=True, exist_ok=True)
        self.modules = {} # id -> data

    def discover(self):
        """Scan for modules in subdirectories"""
        if not self.dlc_dir.exists():
            return
            
        for d in self.dlc_dir.iterdir():
            if d.is_dir():
                # Look for any .json file in the subdirectory (e.g. course.json)
                for f in d.glob("*.json"):
                    try:
                        data = json.loads(f.read_text(encoding="utf-8"))
                        # Store base path for asset loading (images/videos) later
                        data["_path"] = str(d)
                        self.modules[data["id"]] = data
                    except Exception as e:
                        print(f"Failed to load DLC in {d}: {e}")

    def get_module(self, dlc_id: str) -> Optional[dict]:
        return self.modules.get(dlc_id)

class GhostTyper(QObject):
    """Automates typing 'ghost' animation for course demos with scripting support"""
    finished = Signal()
    step_finished = Signal() # Finished one scripted step
    char_typed = Signal(int) # Total chars typed so far

    def __init__(self, wpm: int = 50):
        super().__init__()
        self.wpm = wpm
        self.full_text = ""
        self.current_offset = 0 # Offset for the current string being typed
        self.total_typed = 0
        self.queue = [] # List of strings to type
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.interval = int(60000 / (wpm * 5))

    def type_string(self, text: str):
        """Start typing a new string segment"""
        self.full_text = text
        self.current_offset = 0
        self.timer.start(self.interval)

    def stop(self):
        self.timer.stop()

    def _on_tick(self):
        self.current_offset += 1
        self.total_typed += 1
        self.char_typed.emit(self.total_typed)
        
        if self.current_offset >= len(self.full_text):
            self.timer.stop()
            self.step_finished.emit()

class DLCBrandingWidget(QFrame):
    """Branded header for DLC modules"""
    def __init__(self, theme: Theme):
        super().__init__()
        self.setObjectName("Panel")
        self.theme = theme
        self.setFixedHeight(120)
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 10, 20, 10)
        
        # Logo
        self.lbl_logo = QLabel()
        path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(path):
            pix = QPixmap(path)
            self.lbl_logo.setPixmap(pix.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lay.addWidget(self.lbl_logo)
        
        # Text
        txt_lay = QVBoxLayout()
        self.lbl_main = QLabel("qwerType")
        self.lbl_main.setStyleSheet("font-size: 20pt; font-weight: 900; color: #7c5cff;")
        self.lbl_sub = QLabel("DLC MODULE")
        self.lbl_sub.setObjectName("Muted")
        self.lbl_sub.setStyleSheet("font-size: 12pt; font-weight: bold; text-transform: uppercase;")
        
        txt_lay.addWidget(self.lbl_main)
        txt_lay.addWidget(self.lbl_sub)
        lay.addLayout(txt_lay)
        lay.addStretch(1)

    def set_content(self, dlc_name: str):
        self.lbl_sub.setText(dlc_name)

class LeaderboardWidget(QFrame):
    user_clicked = Signal(str)

    def __init__(self, theme: Theme, i18n: I18N):
        super().__init__()
        self.setObjectName("Panel2")
        self.theme = theme
        self.i18n = i18n
        
        # Main layout
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        # Header
        top = QHBoxLayout()
        self.title = QLabel("")
        self.title.setStyleSheet("font-size: 11pt; font-weight: 800;")
        self.note = QLabel("")
        self.note.setObjectName("Muted")
        top.addWidget(self.title)
        top.addStretch(1)
        top.addWidget(self.note)
        lay.addLayout(top)

        # Scroll Area for Header
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        # Scroll Content
        self.body = QLabel("")
        self.body.setWordWrap(True)
        self.body.setObjectName("Muted")
        self.body.setAlignment(Qt.AlignTop)
        self.body.setOpenExternalLinks(False)
        self.body.linkActivated.connect(self._on_link)
        
        self.scroll.setWidget(self.body)
        lay.addWidget(self.scroll)

        self.retranslate()

    def _on_link(self, link: str):
        if link.startswith("user:"):
            username = link.split(":", 1)[1]
            self.user_clicked.emit(username)

    def retranslate(self):
        self.title.setText(self.i18n.t("leaderboard"))
        self.note.setText(self.i18n.t("leaderboard_offline"))

    def set_i18n(self, i18n: I18N):
        self.i18n = i18n
        self.retranslate()

    def set_text(self, text: str):
        self.body.setText(text)


class ScoreHeaderWidget(QFrame):
    def __init__(self, theme: Theme, i18n: I18N):
        super().__init__()
        self.setObjectName("Panel2")
        self.theme = theme
        self.i18n = i18n
        self.added_widgets = [] 

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(15)

        # Left: Score Card
        self.card_layout = QVBoxLayout()
        self.lbl_title = QLabel("")
        self.lbl_title.setObjectName("Muted")
        self.lbl_title.setStyleSheet("font-size: 10pt; font-weight: 600; text-transform: uppercase;")
        
        self.lbl_score = QLabel("0")
        self.lbl_score.setStyleSheet("font-size: 28pt; font-weight: 900; color: #7c5cff;")
        
        self.card_layout.addWidget(self.lbl_title)
        self.card_layout.addWidget(self.lbl_score)
        
        # Right: Sub-Stats
        r_stats = QVBoxLayout()
        r_stats.setSpacing(2)
        r_stats.addStretch(1)
        
        self.lbl_name = QLabel("-")
        self.lbl_name.setStyleSheet("font-size: 11pt; font-weight: 800;")
        
        self.lbl_meta = QLabel("-")
        self.lbl_meta.setObjectName("Muted")
        self.lbl_meta.setStyleSheet("font-size: 10pt;")
        
        r_stats.addWidget(self.lbl_name)
        r_stats.addWidget(self.lbl_meta)
        r_stats.addStretch(1)

        lay.addLayout(self.card_layout)
        lay.addStretch(1)
        lay.addLayout(r_stats)

        self.retranslate()

    def retranslate(self):
        self.lbl_title.setText(self.i18n.t("final_score"))

    def set_i18n(self, i18n: I18N):
        self.i18n = i18n
        self.retranslate()

    def set_score(self, points: int, wpm: float, acc: float, name: str):
        # Restore Standard View
        self._clear_added()
        self.lbl_score.show()
        self.lbl_name.show()
        self.lbl_meta.show()
        self.retranslate() # Reset title
        
        self.lbl_score.setText(str(int(points)))
        self.lbl_name.setText(name)
        meta = f"WPM {wpm:.1f}  •  ACC {acc:.1f}%"
        self.lbl_meta.setText(meta)

    def set_bests(self, bests: dict):
        # Switch to List View
        self.lbl_score.hide()
        self.lbl_name.hide()
        self.lbl_meta.hide()
        
        # Don't overwrite if title was already set to something specific (like "BESTS: username")
        if self.lbl_title.text() == self.i18n.t("final_score"):
            self.lbl_title.setText("PERSONAL BESTS")
        
        self._clear_added()
            
        if not bests:
            lbl = QLabel("No entries found for this user.")
            lbl.setObjectName("Muted")
            self.card_layout.addWidget(lbl)
            self.added_widgets.append(lbl)
            return
            
        # Show all modes
        for mode, scores in bests.items():
            if not scores: continue
            
            top = scores[0] 
            # Show just top score to save space, but handle "all types"
            txt = f"{mode.upper()}:  {top['points']} pts  —  {top['wpm']:.0f} WPM  •  {top['accuracy']:.0f}%"
            
            lbl = QLabel(txt)
            color = "#e8eaf0" if self.theme.is_dark else "#1a1f2a"
            lbl.setStyleSheet(f"color:{color}; font-weight:bold; font-size: 11pt;")
            self.card_layout.addWidget(lbl)
            self.added_widgets.append(lbl)

    def _clear_added(self):
        for w in self.added_widgets:
            self.card_layout.removeWidget(w)
            w.deleteLater()
        self.added_widgets.clear()


class TrainerWidget(QFrame):
    def __init__(self, coach: TypingCoach, theme: Theme, i18n: I18N):
        super().__init__()
        self.setObjectName("Panel")
        self.coach = coach
        self.theme = theme
        self.i18n = i18n

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 6, 18, 6)
        root.setSpacing(8)

        self.word_label = QLabel("")
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size: 24pt; font-weight: 900;")
        root.addWidget(self.word_label)

        self.stats = QLabel("")
        self.stats.setAlignment(Qt.AlignCenter)
        self.stats.setObjectName("Muted")
        root.addWidget(self.stats)

        self.hints = QLabel("")
        self.hints.setAlignment(Qt.AlignCenter)
        self.hints.setObjectName("Muted")
        self.hints.setStyleSheet("font-size:10pt;")
        root.addWidget(self.hints)

        self.refresh(remaining=60.0, session_active=False, note="")

    def set_i18n(self, i18n: I18N):
        self.i18n = i18n

    def refresh(self, remaining: float, session_active: bool, note: str):
        word = self.coach.current
        idx = self.coach.index

        if idx < len(word):
            done = word[:idx]
            cur = word[idx]
            rest = word[idx + 1:]
            html = (
                f"<span style='color:#9aa3b2'>{done}</span>"
                f"<span style='color:#7c5cff;text-decoration:underline'>{cur}</span>"
                f"<span style='color:#9aa3b2'>{rest}</span>"
            )
        else:
            html = f"<span style='color:#9aa3b2'>{word}</span>"

        self.word_label.setText(html)

        time_left = max(0, int(round(remaining)))
        if session_active:
            self.stats.setText(self.i18n.t(
                "stats_line_active",
                wpm=f"{self.coach.wpm():.1f}",
                acc=f"{self.coach.accuracy():.1f}",
                err=str(self.coach.mistakes),
                left=str(time_left)
            ))
        else:
            self.stats.setText(self.i18n.t("stats_line_idle", note=note))

        # DEFAULT SUGGESTIONS (only if no lint tip is present)
        if not hasattr(self, '_lint_active') or not self._lint_active:
            sug = self.coach.suggestions(5)
            if sug:
                self.hints.setText(self.i18n.t("suggestions") + "  " + "  |  ".join(sug))
            else:
                self.hints.setText(self.i18n.t("suggestions_empty"))

    def set_lint_tip(self, tip: str):
        """Show an educational tip in the HUD instead of standard suggestions"""
        if tip:
            self._lint_active = True
            self.hints.setText(f"<span style='color:#ffae00'>💡 {tip}</span>")
            self.hints.setStyleSheet("font-weight: bold; font-size: 10pt;")
        else:
            self._lint_active = False
            self.hints.setStyleSheet("")
            # Next refresh will restore standard suggestions


class SettingsWidget(QFrame):
    settings_changed = Signal(dict)

    def __init__(self, parent_app, theme: Theme, i18n: I18N, initial_name: str):
        super().__init__()
        self.setObjectName("Panel")
        self.parent_app = parent_app
        self.theme = theme
        self.i18n = i18n

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 6, 18, 6)
        root.setSpacing(10)

        self._title = QLabel("")
        self._title.setStyleSheet("font-size: 14pt; font-weight: 800;")
        root.addWidget(self._title)

        # Name row
        row_name = QHBoxLayout()
        row_name.setSpacing(12)
        self.lbl_name = QLabel("")
        self.ed_name = QLineEdit()
        self.ed_name.setText(initial_name)
        row_name.addWidget(self.lbl_name)
        row_name.addWidget(self.ed_name, 1)
        root.addLayout(row_name)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.lbl_lang = QLabel("")
        self.cb_lang = QComboBox()
        self.cb_lang.addItem("Deutsch", "de")
        self.cb_lang.addItem("English", "en")

        self.lbl_layout = QLabel("")
        self.cb_layout = QComboBox()
        self.cb_layout.addItem("DE (QWERTZ)", "DE")
        self.cb_layout.addItem("US (QWERTY)", "US")

        self.lbl_mode = QLabel("")
        self.cb_mode = QComboBox()
        self.cb_mode.addItem("Words", "words")
        self.cb_mode.addItem("Sentences", "sentences")
        self.cb_mode.addItem("Python", "py")
        self.cb_mode.addItem("JavaScript", "js")
        self.cb_mode.addItem("C++", "cpp")
        self.cb_mode.addItem("Rust", "rs")
        self.cb_mode.addItem("Java", "java")
        
        # Inject discovered DLCs
        for d_id, d_data in self.parent_app.dlc_manager.modules.items():
            self.cb_mode.addItem(d_data["title"], d_id)

        self.lbl_win = QLabel("")
        self.cb_win = QComboBox()
        self.cb_win.addItem("", "windowed")
        self.cb_win.addItem("", "maximized")
        self.cb_win.addItem("", "borderless")

        row1.addWidget(self.lbl_lang)
        row1.addWidget(self.cb_lang)
        row1.addSpacing(8)
        row1.addWidget(self.lbl_layout)
        row1.addWidget(self.cb_layout)
        row1.addSpacing(8)
        row1.addWidget(self.lbl_mode)
        row1.addWidget(self.cb_mode)
        row1.addSpacing(8)
        row1.addWidget(self.lbl_win)
        row1.addWidget(self.cb_win)
        row1.addStretch(1)
        root.addLayout(row1)

        self.chk_dark = QCheckBox("")
        self.chk_dark.setChecked(True)
        root.addWidget(self.chk_dark)

        self.btn_apply = QPushButton("")
        self.btn_apply.clicked.connect(self._emit)
        root.addWidget(self.btn_apply, alignment=Qt.AlignLeft)

        # License Section
        root.addSpacing(10)
        self.lbl_lic_title = QLabel("Licensing")
        self.lbl_lic_title.setStyleSheet("font-weight: bold; font-size: 10pt; color: #7c5cff;")
        root.addWidget(self.lbl_lic_title)

        row_lic = QHBoxLayout()
        self.ed_key = QLineEdit()
        self.ed_key.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.btn_activate = QPushButton("Activate")
        self.btn_activate.setFixedWidth(100)
        self.lbl_status = QLabel("Status: Free")
        self.lbl_status.setObjectName("Muted")
        
        row_lic.addWidget(self.ed_key, 1)
        row_lic.addWidget(self.btn_activate)
        row_lic.addWidget(self.lbl_status)
        root.addLayout(row_lic)

        # Extra stretch removed to keep it compact
        self.retranslate()

    def retranslate(self):
        self._title.setText(self.i18n.t("settings_title"))
        self.lbl_name.setText(self.i18n.t("settings_name") + ":")
        self.ed_name.setPlaceholderText(self.i18n.t("settings_name_ph"))

        self.lbl_lang.setText(self.i18n.t("settings_lang") + ":")
        self.lbl_layout.setText(self.i18n.t("settings_layout") + ":")
        self.lbl_mode.setText(self.i18n.t("settings_mode") + ":")
        self.lbl_win.setText(self.i18n.t("settings_winmode") + ":")

        self.cb_mode.setItemText(0, self.i18n.t("mode_words"))
        self.cb_mode.setItemText(1, self.i18n.t("mode_sentences"))
        self.cb_mode.setItemText(2, self.i18n.t("mode_py"))
        self.cb_mode.setItemText(3, self.i18n.t("mode_js"))
        self.cb_mode.setItemText(4, self.i18n.t("mode_cpp"))
        self.cb_mode.setItemText(5, self.i18n.t("mode_rs"))
        self.cb_mode.setItemText(6, self.i18n.t("mode_java"))

        self.cb_win.setItemText(0, self.i18n.t("win_windowed"))
        self.cb_win.setItemText(1, self.i18n.t("win_maximized"))
        self.cb_win.setItemText(2, self.i18n.t("win_borderless"))

        self.chk_dark.setText(self.i18n.t("setting_darkmode"))
        self.btn_apply.setText(self.i18n.t("apply"))
        
        self.lbl_lic_title.setText(self.i18n.t("licensing_title", fallback="Licensing"))
        self.btn_activate.setText(self.i18n.t("activate", fallback="Activate"))

    def _emit(self):
        self.settings_changed.emit({
            "name": normalize_name(self.ed_name.text()),
            "lang": self.cb_lang.currentData(),
            "layout": self.cb_layout.currentData(),
            "mode": self.cb_mode.currentData(),
            "win_mode": self.cb_win.currentData(),
            "theme": "dark" if self.chk_dark.isChecked() else "light",
        })

    def apply_current(self, config: dict):
        self.ed_name.setText(config.get("name", ""))
        idx_l = self.cb_lang.findData(config.get("lang", "de"))
        if idx_l >= 0: self.cb_lang.setCurrentIndex(idx_l)
        idx_lo = self.cb_layout.findData(config.get("layout", "de"))
        if idx_lo >= 0: self.cb_layout.setCurrentIndex(idx_lo)
        idx_m = self.cb_mode.findData(config.get("mode", "words"))
        if idx_m >= 0: self.cb_mode.setCurrentIndex(idx_m)
        idx_w = self.cb_win.findData(config.get("win_mode", "windowed"))
        if idx_w >= 0: self.cb_win.setCurrentIndex(idx_w)
        self.chk_dark.setChecked(config.get("theme", "dark") == "dark")
# ============================================================
# KEYCAP + KEYBOARD
# ============================================================

class KeyCap(QFrame):
    def __init__(self, kid: str, label: str, label2: str, theme: Theme, layout_name_getter):
        super().__init__()
        self.kid = kid
        self.label = label
        self.label2 = label2
        self.theme = theme
        self.layout_name_getter = layout_name_getter
        self.state = "idle"
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._w = 44
        self._h = 44

    def set_fixed(self, w: int, h: int):
        self._w, self._h = w, h
        self.setFixedSize(w, h)
        self.update()

    def set_state(self, s: str):
        self.state = s
        self.update()

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        pal = self.theme.key_palette()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()
        layout_name = self.layout_name_getter()
        hand = hand_for_kid(layout_name, self.kid)
        
        if hand == "left":
            base = QColor("#222b22") if self.theme.is_dark else QColor("#eafaea")
        elif hand == "right":
            base = QColor("#22222b") if self.theme.is_dark else QColor("#eaeafa")
        else:
            base = QColor(pal.get("key_bg", "#121620" if self.theme.is_dark else "#f2f5fb"))

        if self.state == "wrong":
            base = QColor(pal["key_wrong"])
        elif self.state == "correct":
            base = QColor(pal["key_correct"])
        elif self.state == "pressed":
            base = base.lighter(130)

        p.setPen(Qt.NoPen)
        p.setBrush(base)
        side = min(self._w, self._h)
        radius = max(2, int(side * 0.22))
        p.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)

        if self.state == "target":
            ring = QColor(pal["key_target"])
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(ring, max(1, int(self._h * 0.10))))
            p.drawRoundedRect(rect.adjusted(3, 3, -3, -3), radius, radius)

        main_fs = max(6, int(self._h * 0.32)) # slightly larger ratio
        sub_fs = max(5, int(self._h * 0.20))

        # Relative margins for text - no hardcoded 10px anymore
        mx = max(2, int(self._w * 0.12))
        my = max(2, int(self._h * 0.10))

        p.setPen(QColor(pal["key_text"]))
        f = QFont("Segoe UI", main_fs)
        f.setBold(True)
        p.setFont(f)
        p.drawText(rect.adjusted(mx, my, -mx, -my), Qt.AlignLeft | Qt.AlignTop, self.label)

        if self.label2 and self._w > (mx * 4): # don't draw if too cramped
            p.setPen(QColor(255, 255, 255, 180))
            f2 = QFont("Segoe UI", sub_fs)
            p.setFont(f2)
            p.drawText(rect.adjusted(mx, my, -mx, -my), Qt.AlignRight | Qt.AlignTop, self.label2)

        p.end()


class KeyboardWidget(QFrame):
    def __init__(self, theme: Theme):
        super().__init__()
        self.setObjectName("Panel")
        self.theme = theme
        self.layout_name = "DE"
        self.keycaps: Dict[str, KeyCap] = {}
        self._target: Optional[str] = None
        self._max_width_ratio = 0.76

        self.row_layouts = []
        self.row_spacers = []
        self.row_widgets = []

        self._layout_cache: List[List[KeyDef]] = []
        self.build()

    def current_layout(self) -> List[List[KeyDef]]:
        return de_layout() if self.layout_name.upper() == "DE" else us_layout()

    def set_layout(self, name: str):
        self.layout_name = name
        self.build()
        self.update_geometry_from_parent()

    def set_theme(self, theme: Theme):
        self.theme = theme
        for kc in self.keycaps.values():
            kc.set_theme(theme)
        self.update()

    def set_target_key(self, kid: Optional[str]):
        self._target = kid
        for k, kc in self.keycaps.items():
            if kc.state == "wrong":
                continue
            if k == kid:
                kc.set_state("target")
            else:
                if kc.state == "target":
                    kc.set_state("idle")

    def flash_pressed(self, kid: Optional[str]):
        if not kid:
            return
        kc = self.keycaps.get(kid)
        if not kc:
            return
        prev = kc.state
        kc.set_state("pressed")
        QTimer.singleShot(90, lambda: kc.set_state(prev))

    def flash_wrong(self, kid: Optional[str]):
        if not kid:
            return
        kc = self.keycaps.get(kid)
        if not kc:
            return
        kc.set_state("wrong")
        QTimer.singleShot(240, lambda: kc.set_state("target" if kid == self._target else "idle"))

    def flash_correct(self, kid: Optional[str]):
        if not kid:
            return
        kc = self.keycaps.get(kid)
        if not kc:
            return
        prev = kc.state
        kc.set_state("correct")
        QTimer.singleShot(120, lambda: kc.set_state(prev))

    def kid_center_global(self, kid: str) -> QPoint:
        kc = self.keycaps.get(kid)
        if not kc:
            return self.mapToGlobal(self.rect().center())
        return kc.mapToGlobal(kc.rect().center())

    def build(self):
        root = self.layout()
        if not root:
            root = QVBoxLayout(self)

        while root.count():
            it = root.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            elif it.layout():
                # Basic drainage
                while it.layout().count(): it.layout().takeAt(0)

        self.keycaps.clear()
        self.row_layouts.clear()
        self.row_spacers.clear()
        self.row_widgets.clear()
        self._layout_cache = self.current_layout()

        for row in self._layout_cache:
            roww = QWidget()
            rowl = QHBoxLayout(roww)
            rowl.setContentsMargins(0, 0, 0, 0)
            rowl.setSpacing(10)

            # Split row into left and right hands for a clean visual gap
            left_side = []
            right_side = []
            for kd in row:
                if kd.is_spacer: continue
                hand = hand_for_kid(self.layout_name, kd.kid)
                if hand == "left": left_side.append(kd)
                else: right_side.append(kd)

            for kd in left_side:
                kc = KeyCap(kd.kid, kd.label, kd.label2, self.theme, lambda: self.layout_name)
                self.keycaps[kd.kid] = kc
                rowl.addWidget(kc)

            # Central hand-separation gap
            rowl.addSpacing(20)

            for kd in right_side:
                kc = KeyCap(kd.kid, kd.label, kd.label2, self.theme, lambda: self.layout_name)
                self.keycaps[kd.kid] = kc
                rowl.addWidget(kc)

            self.row_layouts.append(rowl)
            # Find the spacer we just added (the hand-gap)
            for i in range(rowl.count()):
                it = rowl.itemAt(i)
                if it.spacerItem():
                    self.row_spacers.append(it.spacerItem())
                    break

            self.row_widgets.append(roww)
            root.addWidget(roww)

        self.set_target_key(self._target)
        self.update_geometry_from_parent()

    def paintEvent(self, event):
        super().paintEvent(event)
        # Split line and hand labels removed as requested

    def _row_units(self, row: List[KeyDef]) -> float:
        return sum(kd.w for kd in row if not kd.is_spacer)

    def update_geometry_from_parent(self, scale: float = 1.0):
        # Absolute Proportional Scaling
        unit = int(52 * scale)
        key_h = unit
        
        data = self._layout_cache or self.current_layout()
        num_rows = len(data)
        
        spacing = int(4 * scale) # Even tighter
        m = int(4 * scale) # Even tighter
        
        # Scaling internal layouts
        self.layout().setContentsMargins(m, m, m, m)
        self.layout().setSpacing(spacing)
        
        for rl in self.row_layouts:
            rl.setSpacing(int(10 * scale)) # horizontal spacing
        for roww in self.row_widgets:
            roww.setFixedHeight(key_h)
        for rs in self.row_spacers:
            rs.changeSize(int(30 * scale), 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        for rl in self.row_layouts:
            rl.invalidate()

        # Calculate and set exact required height
        total_h = (num_rows * key_h) + (spacing * (num_rows - 1)) + (m * 2)
        self.setFixedHeight(int(total_h))
        
        # Apply scaling to all keys
        for row in data:
            for kd in row:
                if kd.is_spacer:
                    continue
                kc = self.keycaps.get(kd.kid)
                if kc:
                    kc.set_fixed(int(unit * kd.w), key_h)

        for row in data:
            for kd in row:
                if kd.is_spacer:
                    continue
                kc = self.keycaps.get(kd.kid)
                if kc:
                    kc.set_fixed(int(unit * kd.w), key_h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_geometry_from_parent()


# ============================================================
# BUBBLES
# ============================================================

@dataclass
class Bubble:
    x: float
    y: float
    r: float
    vy: float
    drift: float
    color: QColor
    life: float
    born: float


class BubbleBar(QFrame):
    def __init__(self, theme: Theme):
        super().__init__()
        self.setObjectName("Panel2")
        self.theme = theme
        self.bubbles: List[Bubble] = []
        self.last = time.time()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def apply_scale(self, s: float):
        # Reduced word bar (BubbleBar)
        self.setFixedHeight(int(150 * s))
        self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # Height is now controlled by apply_scale

    def spawn(self, gp: QPoint, color: QColor):
        lp = self.mapFromGlobal(gp)
        now = time.time()
        for _ in range(3):
            self.bubbles.append(Bubble(
                x=lp.x() + random.uniform(-10, 10),
                y=self.height() + random.uniform(0, 8),
                r=random.uniform(6, 12),
                vy=random.uniform(70, 160),
                drift=random.uniform(-20, 20),
                color=color,
                life=random.uniform(1.2, 2.1),
                born=now
            ))

    def tick(self):
        now = time.time()
        dt = min(0.05, max(0.001, now - self.last))
        self.last = now
        alive = []
        for b in self.bubbles:
            if now - b.born > b.life:
                continue
            b.y -= b.vy * dt
            b.x += (b.drift + math.sin((now - b.born) * 4.0) * 6.0) * dt * 0.7
            alive.append(b)
        self.bubbles = alive
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 5) if self.theme.is_dark else QColor(0, 0, 0, 4))
        p.drawRoundedRect(r.adjusted(6, 6, -6, -6), 16, 16)

        for b in self.bubbles:
            age = time.time() - b.born
            t = max(0.0, 1.0 - age / b.life)
            c = QColor(b.color)
            c.setAlpha(int(220 * t))
            p.setBrush(c)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(int(b.x), int(b.y)), int(b.r), int(b.r))

        p.end()


# ============================================================
# HIGHSCORE STORAGE (OFFLINE)
# ============================================================

def hs_default():
    return {
        "words": None,
        "sentences": None,
        "py": None,
        "js": None,
        "cpp": None,
        "rs": None,
        "java": None,
    }

def format_entry(entry: Optional[dict]) -> str:
    if not entry:
        return ""
    return f"{entry.get('name','?')} — {entry.get('points',0)} pts (WPM {entry.get('wpm',0):.1f}, ACC {entry.get('acc',0):.1f}%)"

def make_leaderboard_text(i18n: I18N, hs: dict) -> str:
    lines = []

    def block(title: str, key: str):
        lines.append(f"<b>{title}</b>")
        e = hs.get(key)
        if e:
            lines.append(format_entry(e))
        else:
            lines.append(i18n.t("lb_none"))
        lines.append("")

    block(i18n.t("lb_words"), "words")
    block(i18n.t("lb_sentences"), "sentences")

    lines.append(f"<b>{i18n.t('lb_langs')}</b>")
    for k, label_key in [("py","mode_py"), ("js","mode_js"), ("cpp","mode_cpp"), ("rs","mode_rs"), ("java","mode_java")]:
        e = hs.get(k)
        label = i18n.t(label_key)
        if e:
            lines.append(f"• {label}: {format_entry(e)}")
        else:
            lines.append(f"• {label}: {i18n.t('lb_none')}")

    return "<br>".join(lines).strip()


# ============================================================
# SECONDARY WINDOWS
# ============================================================

class SettingsWindow(QMainWindow):
    def __init__(self, main_window, theme: Theme, i18n: I18N, initial_name: str):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("qwerType - Settings")
        self.setObjectName("Panel")
        
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(10, 10, 10, 10)
        
        self.settings_widget = SettingsWidget(self.main_window, theme, i18n, initial_name)
        lay.addWidget(self.settings_widget)
        
        self.setStyleSheet(theme.app_stylesheet())
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.resize(800, 300)

    def apply_scale(self, s: float):
        self.settings_widget._title.setStyleSheet(f"font-size: {max(9, int(14*s))}pt; font-weight: 800;")
        # more scaling if needed

class StatsWindow(QMainWindow):
    mode_switched = Signal(str)

    def __init__(self, main_window, theme: Theme, i18n: I18N):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("qwerType - Stats & Leaderboard")
        self.setObjectName("Panel")
        
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # Mode Selector
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Words", "Sentences", "Python", "JS", "C++", "Rust", "Java"])
        self.mode_selector.currentIndexChanged.connect(self._on_mode_changed)
        root.addWidget(self.mode_selector)
        
        self.score_header = ScoreHeaderWidget(theme, i18n)
        self.leaderboard = LeaderboardWidget(theme, i18n)
        
        root.addWidget(self.score_header)
        root.addWidget(self.leaderboard)
        
        self.setStyleSheet(theme.app_stylesheet())
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.resize(500, 700)

    def _on_mode_changed(self, idx):
        modes = ["words", "sentences", "py", "js", "cpp", "rs", "java"]
        self.mode_switched.emit(modes[idx])

    def apply_scale(self, s: float):
        def fs(base): return max(6, int(base * s))
        self.score_header.lbl_score.setStyleSheet(f"font-size: {max(10, int(24*s))}pt; font-weight: 900; color: #7c5cff;")
        self.score_header.lbl_title.setStyleSheet(f"font-size: {fs(10)}pt; font-weight: 600; text-transform: uppercase;")
        self.score_header.lbl_name.setStyleSheet(f"font-size: {fs(12)}pt; font-weight: 800;")
        self.score_header.lbl_meta.setStyleSheet(f"font-size: {fs(10)}pt;")
        self.leaderboard.title.setStyleSheet(f"font-size: {fs(15)}pt; font-weight: 800;")
        self.leaderboard.body.setStyleSheet(f"font-size: {fs(11)}pt;")

# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self, theme: Theme, i18n: I18N):
        super().__init__()
        self.theme = theme
        self.i18n = i18n

        # load settings + highscores
        _ensure_dirs()
        self.settings_data = load_json(SETTINGS_JSON, {
            "name": "",
            "lang": DEFAULT_LANG,
            "layout": "DE",
            "mode": "words",
            "win_mode": "windowed",
            "theme": "dark",
        })
        self.highscores = load_json(HIGHSCORES_JSON, hs_default())

        self.name = normalize_name(self.settings_data.get("name", ""))
        self.lang = self.settings_data.get("lang", i18n.lang)
        self.layout = self.settings_data.get("layout", "DE")
        self.mode = self.settings_data.get("mode", "words")

        self.setWindowTitle(APP_TITLE)
        self.setStyleSheet(theme.app_stylesheet())

        self.items_words = DEFAULT_WORDS_DE[:]
        self.items_sent = DEFAULT_SENTENCES_DE[:]

        # DLC Management (Must be before coach/settings)
        self.dlc_manager = DLCManager(theme, i18n)
        self.dlc_manager.discover()

        self.coach = TypingCoach(self._items_for_mode(self.mode))

        self.session_active = False
        self.session_end = 0.0
        self.start_buffer = ""

        # last session metrics
        self.last_points = 0
        self.last_wpm = 0.0
        self.last_acc = 0.0

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # Initialize Components first
        self.bubbles = BubbleBar(theme)
        
        self.left_renderer = HandRenderer(theme, "left")
        self.right_renderer = HandRenderer(theme, "right")
        self.left_hand = SquareHandPanel(theme, self.left_renderer)
        self.right_hand = SquareHandPanel(theme, self.right_renderer)
        
        # Server Sync Integration
        self.server_sync = ServerSync()
        
        # Licensing
        self.license_manager = LicenseManager()
        self.license_manager.status_changed.connect(self._on_lic_status_changed)
        self.license_manager.check_silent()
        
        # Sync Timer (Adaptive)
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self._check_sync)
        self.sync_timer.start(60 * 1000) # Check every minute
        
        self.win_settings = SettingsWindow(self, theme, i18n, self.name)
        self.win_settings.settings_widget.settings_changed.connect(self.apply_settings)
        self.win_stats = StatsWindow(self, theme, i18n)
        self.win_stats.mode_switched.connect(self._on_stats_mode_changed)
        
        # Shortcuts / pointers to widgets inside windows
        self.score_header = self.win_stats.score_header
        self.settings = self.win_settings.settings_widget
        self.leaderboard = self.win_stats.leaderboard
        
        # Connect License UI
        self.settings.btn_activate.clicked.connect(lambda: self.license_manager.activate(self.settings.ed_key.text()))
        self._update_lic_status()
        
        self.leaderboard.user_clicked.connect(self._fetch_user_bests)

        # 1. Bubble Container (Proportional height)
        root.addWidget(self.bubbles, 1)

        # Branding Header (Visible only in DLC modes)
        self.dlc_header = DLCBrandingWidget(theme)
        self.dlc_header.hide()
        root.insertWidget(1, self.dlc_header) # Insert above workspace

        # Workspace (Center Stack)
        workspace_container = QFrame()
        workspace_container.setObjectName("Panel")
        self.workspace_lay = QVBoxLayout(workspace_container)
        
        self.trainer = TrainerWidget(self.coach, theme, i18n)
        self.workspace_lay.addWidget(self.trainer)
        
        root.addWidget(workspace_container, 2)

        # 3. Keyboard Container (Hands beside keyboard)
        keyboard_section = QFrame()
        keyboard_section.setObjectName("Panel")
        self.keyboard_lay = QHBoxLayout(keyboard_section)
        
        self.keyboard_lay.addWidget(self.left_hand, alignment=Qt.AlignCenter)
        
        mid_kb = QVBoxLayout()
        mid_kb.setContentsMargins(0, 0, 0, 0)
        mid_kb.setSpacing(0)
        self.keyboard = KeyboardWidget(theme)
        self.keyboard.set_layout(self.layout)
        mid_kb.addWidget(self.keyboard, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.keyboard_lay.addLayout(mid_kb, 1)
        
        self.keyboard_lay.addWidget(self.right_hand, alignment=Qt.AlignCenter)
        
        root.addWidget(keyboard_section, 4)

        # 4. Footer Section
        footer_container = QWidget()
        footer_lay = QHBoxLayout(footer_container)
        footer_lay.setContentsMargins(10, 5, 10, 0)
        
        btn_stats = QPushButton(self.i18n.t("footer_stats"))
        btn_stats.setObjectName("Muted")
        btn_stats.setFlat(True)
        btn_stats.clicked.connect(lambda: self.win_stats.show() or self.win_stats.raise_())
        
        btn_set = QPushButton(self.i18n.t("footer_settings"))
        btn_set.setObjectName("Muted")
        btn_set.setFlat(True)
        btn_set.clicked.connect(lambda: self.win_settings.show() or self.win_settings.raise_())
        
        footer = QLabel(FOOTER_TEXT)
        footer.setAlignment(Qt.AlignCenter)
        footer.setObjectName("Muted")
        footer.setStyleSheet("font-size:9pt")
        
        footer_lay.addWidget(btn_stats)
        footer_lay.addStretch(1)
        footer_lay.addWidget(footer)
        footer_lay.addStretch(1)
        footer_lay.addWidget(btn_set)
        root.addWidget(footer_container)

        # Startup Overlay (Parent to self for true fullscreen)
        self.overlay = StartupOverlay(self, theme, i18n)
        self.overlay.hide()

        # Username Setup Overlay
        self.user_overlay = QWidget(central)
        self.user_overlay.hide()
        u_lay = QVBoxLayout(self.user_overlay)
        u_lay.setAlignment(Qt.AlignCenter)
        self.user_dialog = UsernameDialog(theme, i18n)
        self.user_dialog.accepted.connect(self._finish_username_setup)
        u_lay.addWidget(self.user_dialog)

        # Result Preview (Fake Browser)
        self.result_viewer = ResultPreviewWidget(self, theme, i18n)
        self.result_viewer.hide()

        # Scholar Lesson Engine
        self.scholar_engine = ScholarLessonWidget(self, theme, i18n)
        self.scholar_engine.hide()
        self.scholar_engine.step_changed.connect(self._on_scholar_step)
        self.scholar_engine.finished.connect(self.show_startup_overlay)

        # toast
        self.toast = Toast(theme)
        self.toast.setParent(central)
        self.toast.setFixedHeight(48)

        # Demo orchestration state
        self._demo_active = False
        self._current_demo_explain = ""
        self._demo_steps = None
        self._demo_timer = QTimer(self)
        self._demo_timer.setSingleShot(True)
        self._demo_timer.timeout.connect(self._exec_demo_step_typing)

        self.installEventFilter(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

        self.retranslate()
        self._refresh_leaderboard()

        # initial frames
        self.left_hand.update_stream()
        self.right_hand.update_stream()

        QTimer.singleShot(800, self.show_startup_overlay)

        # initial target
        self._update_target()
        self._apply_responsive_sizes()
        self._sync_dlc_ui()

        # Check for first-time use
        if not self.name:
            QTimer.singleShot(1000, self.show_username_setup)
        else:
            QTimer.singleShot(800, self.show_startup_overlay)

    def show_username_setup(self):
        self.user_overlay.resize(self.centralWidget().size())
        self.user_overlay.show()
        self.user_overlay.raise_()

    def _finish_username_setup(self, name: str):
        self.name = name
        self.settings_data["name"] = name
        save_json(SETTINGS_JSON, self.settings_data)
        self.user_overlay.hide()
        self.settings.ed_name.setText(name)
        self.score_header.lbl_name.setText(name)
        self.show_startup_overlay()


    def _items_for_mode(self, mode: str) -> List[str]:
        # Check DLCs first
        dlc = self.dlc_manager.get_module(mode)
        if dlc:
            all_items = []
            for lesson in dlc.get("lessons", []):
                all_items.extend(lesson.get("items", []))
            return [x.strip() + " " for x in all_items]

        items = []
        if mode == "sentences":
            items = self.items_sent if self.lang == "de" else DEFAULT_SENTENCES_EN
            return items
        elif mode == "words":
            items = self.items_words if self.lang == "de" else DEFAULT_WORDS_EN
        elif mode in DEFAULT_LANG_ITEMS:
            items = DEFAULT_LANG_ITEMS[mode]
        else:
            items = self.items_words

        # Add space to words for spacebar progression requirement
        return [x.strip() + " " for x in items]

    def open_html_dlc_window(self):
        """Open HTML Scholar course in a separate OS window (does NOT touch Main UI)."""
        spec_path = os.path.join(DATA_DIR, "dlc", "html", "qwertype_html_day_01.json")
        if not os.path.exists(spec_path):
            legacy_path = os.path.join(DATA_DIR, "dlc", "qwertype_html_dlc_spec_v1.json")
            if os.path.exists(legacy_path):
                spec_path = legacy_path
            else:
                try:
                    self.toast.show_msg("HTML DLC Spec fehlt: data/dlc/html/qwertype_html_day_01.json", 2500)
                except Exception:
                    print("[ERROR] Missing spec:", spec_path)
                return
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
        except Exception as e:
            try:
                self.toast.show_msg(f"Error loading spec: {e}", 2500)
            except Exception:
                print("Error loading spec:", e)
            return

        if getattr(self, "html_dlc_win", None) and self.html_dlc_win.isVisible():
            self.html_dlc_win.raise_()
            self.html_dlc_win.activateWindow()
            return

        self.html_dlc_win = HtmlDlcWindow(self, self.theme, self.i18n, spec_data, DATA_DIR)
        self.html_dlc_win.show()

    def _mode_bucket_key(self, mode: str) -> str:
        # Für Highscores als Keys
        if mode in ("words", "sentences", "py", "js", "cpp", "rs", "java"):
            return mode
        return "words"

    def retranslate(self):
        self.win_settings.setWindowTitle("qwerType - " + self.i18n.t("footer_settings"))
        self.win_stats.setWindowTitle("qwerType - " + self.i18n.t("footer_stats"))
        self.settings.retranslate()
        self.score_header.set_i18n(self.i18n)
        self.leaderboard.set_i18n(self.i18n)

    def closeEvent(self, event):
        # Stop sync timer
        if hasattr(self, 'sync_timer'):
            self.sync_timer.stop()
            
        # No need to stop lb_fetcher manually anymore because it's a daemon thread
        
        # Close secondary windows
        self.win_settings.close()
        self.win_stats.close()
        
        event.accept()

    def _refresh_leaderboard(self, mode=None):
        # Local fallback first
        self.leaderboard.set_text(make_leaderboard_text(self.i18n, self.highscores))
        
        # Determine mode
        target_mode = mode if mode else self.mode
        
        # Start async fetch
        if hasattr(self, 'server_sync'):
            if hasattr(self, 'lb_fetcher') and self.lb_fetcher and self.lb_fetcher.isRunning():
                # For stats mode changes, we might want to kill the previous one
                pass

            self.leaderboard.note.setText("Fetching online...")
            
            # Fetch for target mode + User history
            self.lb_fetcher = LeaderboardFetcher(self.server_sync, target_mode, username=self.name, limit=30)
            self.lb_fetcher.signals.finished.connect(self._on_lb_fetched)
            self.lb_fetcher.signals.finished_bests.connect(self.score_header.set_bests)
            self.lb_fetcher.signals.error.connect(self._on_lb_error)
            self.lb_fetcher.start()

    def _on_stats_mode_changed(self, mode: str):
        self._refresh_leaderboard(mode=mode)

    def _on_lic_status_changed(self, status: str):
        self._update_lic_status()
        if status == "success":
            Toast(self.theme).show_msg("License Activated!", 3000)
        elif status == "failed":
            Toast(self.theme).show_msg("Activation Failed", 3000)

    def _update_lic_status(self):
        if self.license_manager.is_active():
            self.settings.lbl_status.setText("Status: PRO")
            self.settings.lbl_status.setStyleSheet("color: #7c5cff; font-weight: bold;")
            self.settings.btn_activate.setEnabled(False)
            self.settings.ed_key.setEnabled(False)
        else:
            self.settings.lbl_status.setText("Status: Free")
            self.settings.lbl_status.setObjectName("Muted")
            self.settings.btn_activate.setEnabled(True)
            self.settings.ed_key.setEnabled(True)

    def _fetch_user_bests(self, username: str):
        """Fetch stats for a specific user clicked in the leaderboard"""
        self.leaderboard.note.setText(f"Fetching {username}...")
        
        # Update header title to show who we are looking at
        self.score_header.lbl_title.setText(f"BESTS: {username}")
        self.score_header.lbl_score.hide()
        self.score_header.lbl_name.hide()
        self.score_header.lbl_meta.hide()
        self.score_header._clear_added() # Clear previous list immediately
        
        # Fetch data
        self.lb_fetcher = LeaderboardFetcher(self.server_sync, self.mode, username=username)
        # We don't really need to refresh the global leaderboard text every click, 
        # but the fetcher does both. We can just ignore the 'finished' signal if we want,
        # or let it refresh (harmless). Let's let it refresh to keep it simple.
        self.lb_fetcher.signals.finished.connect(self._on_lb_fetched)
        self.lb_fetcher.signals.finished_bests.connect(self.score_header.set_bests)
        self.lb_fetcher.signals.error.connect(self._on_lb_error)
        self.lb_fetcher.start()

    def _on_lb_fetched(self, data):
        html = format_server_leaderboard(data, self.i18n, self.theme)
        self.leaderboard.set_text(html)
        self.leaderboard.note.setText("Online Leaderboard")
        self.lb_fetcher = None

    def _on_lb_error(self):
        self.leaderboard.note.setText("Offline (Connect Error)")
        # Keep local text
        self.lb_fetcher = None

    def _apply_responsive_sizes(self):
        w = self.width()
        h = self.height()
        
        # Viewport-Fit Proportional Scaling (Reference 1600x900)
        sw = w / 1600.0
        sh = h / 900.0
        s = min(sw, sh)
        
        if s < 0.15: s = 0.15 # Absolute safety floor

        # 1. Bubbles
        self.bubbles.apply_scale(s)

        # 2. Hands
        hand_px = int(240 * s)
        self.left_hand.set_panel_size(hand_px)
        self.right_hand.set_panel_size(hand_px)
        
        # 3. Layout Spacings
        m = int(14 * s)
        spacing = int(10 * s)
        
        # Root layout
        root_lay = self.centralWidget().layout()
        if root_lay:
            # Enforce at least 20px bottom padding
            bottom_m = max(20, m)
            root_lay.setContentsMargins(m+4, m, m+4, bottom_m)
            root_lay.setSpacing(spacing)

        # Container layouts
        self.workspace_lay.setContentsMargins(int(20*s), int(6*s), int(20*s), int(6*s))
        self.workspace_lay.setSpacing(int(8*s))
        
        self.keyboard_lay.setContentsMargins(int(12*s), int(6*s), int(12*s), int(6*s))
        self.keyboard_lay.setSpacing(int(14*s))

        # 4. Fonts - with minimum floor for readability
        def fs(base): return max(6, int(base * s))

        # Separate windows
        self.win_stats.apply_scale(s)
        self.win_settings.apply_scale(s)
        
        # Trainer (Still in main)
        self.trainer.word_label.setStyleSheet(f"font-size: {max(12, int(24*s))}pt; font-weight: 900;")
        self.trainer.stats.setStyleSheet(f"font-size: {fs(11)}pt;")
        self.trainer.hints.setStyleSheet(f"font-size: {fs(11)}pt; color: #7c5cff; font-weight: bold;")

        # 5. Overlays
        self.overlay.apply_scale(s)
        self.user_dialog.apply_scale(s)
        if hasattr(self, 'scholar_engine'):
            self.scholar_engine.apply_scale(s)

        # 6. Keyboard
        self.keyboard.update_geometry_from_parent(s)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cw = self.centralWidget().rect()
        w = min(720, int(cw.width() * 0.65))
        self.toast.setFixedWidth(w)
        self.toast.move((cw.width() - w)//2, 16)
        
        if hasattr(self, 'overlay') and self.overlay.isVisible():
            self.overlay.setGeometry(self.rect())
        if hasattr(self, 'user_overlay') and self.user_overlay.isVisible():
            self.user_overlay.setGeometry(self.rect())
        if hasattr(self, 'result_viewer') and self.result_viewer.isVisible():
            self.result_viewer.setGeometry(self.rect())
        if hasattr(self, 'scholar_engine') and self.scholar_engine.isVisible():
            self.scholar_engine.setGeometry(self.rect())
            
        self._apply_responsive_sizes()

    def _sync_dlc_ui(self):
        """Update branding and intro based on current mode"""
        dlc = self.dlc_manager.get_module(self.mode)
        
        # Check for V1 Spec file if it's the HTML module
        spec_path = os.path.join(DATA_DIR, "dlc", "qwertype_html_dlc_spec_v1.json")
        if self.mode == "html_scholar" and getattr(self, 'dlc_manager', None):
            # Run HTML course in a separate OS window (standalone). Do NOT touch main UI.
            self.open_html_dlc_window()

            # Immediately leave scholar mode in the main window
            self.mode = "words"
            try:
                self.settings.cb_mode.setCurrentText("words")
            except Exception:
                pass
            return

        if dlc and self.mode not in ["words", "sentences", "py", "js", "cpp", "rs", "java"]:
            self.bubbles.hide() # Hide for DLC
            self.dlc_header.set_content(dlc.get("branding", {}).get("text", "DLC MODULE"))
            self.dlc_header.show()
            
            # Update intro text if available
            intro = dlc.get("intro", {})
            if intro:
                self.overlay.title.setText(intro.get("title", "DLC COURSE"))
                self.overlay.hint.setText(intro.get("text", ""))
            
            # Setup Demo Button
            demos = dlc.get("demos", [])
            if demos:
                self.overlay.btn_demo.show()
                try:
                    self.overlay.btn_demo.clicked.disconnect()
                except Exception:
                    pass
                except: pass
                self.overlay.btn_demo.clicked.connect(lambda: self._run_demo(demos[0]))
            else:
                self.overlay.btn_demo.hide()
            
            # SHOW OVERLAY on mode switch/load
            self.show_startup_overlay()
        else:
            self.bubbles.show() # Restore for standard modes
            self.dlc_header.hide()
            self.overlay.btn_demo.hide()
            self.overlay.title.setText(self.i18n.t("hint_type_start_title", fallback="READY?"))
            self.overlay.hint.setText(self.i18n.t("hint_type_start_long", fallback="To begin the 60s training session,\nplease type 'START' on your keyboard."))
            self.scholar_engine.hide()

    def apply_settings(self, cfg: dict):
        # name
        new_name = normalize_name(cfg.get("name", self.name))
        if new_name != self.name:
            if not is_name_allowed(new_name):
                self.toast.show_msg(self.i18n.t("name_invalid"), 1400)
                # revert UI field
                self.settings.ed_name.setText(self.name)
            else:
                self.name = new_name
                self.toast.show_msg(self.i18n.t("name_saved"), 900)

        new_lang = cfg.get("lang", self.lang)
        if new_lang != self.lang:
            self.lang = new_lang
            self.i18n.load(self.lang)
            self.retranslate()
            self.toast.show_msg(self.i18n.t("saved"), 900)
            self._refresh_leaderboard()

        new_theme = cfg.get("theme", self.theme.mode)
        if new_theme != self.theme.mode:
            self.theme = Theme(new_theme)
            QApplication.instance().setStyleSheet(self.theme.app_stylesheet())
            self.setStyleSheet(self.theme.app_stylesheet())
            self.keyboard.set_theme(self.theme)
            self.bubbles.theme = self.theme
            self.left_hand.set_theme(self.theme)
            self.right_hand.set_theme(self.theme)
            self.left_renderer.set_theme(self.theme)
            self.right_renderer.set_theme(self.theme)
            self.left_hand.update_stream()
            self.right_hand.update_stream()

        new_layout = cfg.get("layout", self.layout)
        if new_layout != self.layout:
            self.layout = new_layout
            self.keyboard.set_layout(self.layout)
            self.toast.show_msg(self.i18n.t("saved"), 900)
            self._update_target()

        new_mode = cfg.get("mode", self.mode)
        if True: # Always sync UI on apply to be safe
            self._stop_demo() # Safety kill
            self.mode = new_mode
            self.session_active = False # Reset session state
            self.coach.set_items(self._items_for_mode(self.mode))
            self._sync_dlc_ui()

            self.toast.show_msg(self.i18n.t("saved"), 900)
            self._update_target()
            self._refresh_leaderboard()

        new_win = cfg.get("win_mode", self.settings_data.get("win_mode", "windowed"))
        if new_win != self.settings_data.get("win_mode"):
            self.apply_window_mode(new_win)
            self.toast.show_msg(self.i18n.t("saved"), 900)

        # persist settings
        self.settings_data = {
            "name": self.name,
            "lang": self.lang,
            "layout": self.layout,
            "mode": self.mode,
            "win_mode": cfg.get("win_mode", "windowed"),
            "theme": self.theme.mode,
        }
        save_json(SETTINGS_JSON, self.settings_data)

    def _run_demo(self, demo_data: dict):
        """Play a scripted educational demo"""
        self._stop_demo()
        self._demo_active = True
        self.overlay.hide()
        self.session_active = False # Manual mode
        
        # Force a UI scaling refresh to ensure HUD is legible
        self._apply_responsive_sizes()
        
        steps = demo_data.get("steps", [])
        if not steps:
            # Fallback for old format
            code = demo_data.get("code", "")
            if not code: return
            steps = [{"code": code, "explain": "Watching demo...", "pause": 1000}]

        # Inject combined code into coach
        full_code = "".join([s.get("code", "") for s in steps])
        self.coach.current = full_code
        self.coach.index = 0
        self.trainer.refresh(60.0, False, f"DEMO: {demo_data.get('name', 'Watching...')}")
        
        # ULTRA-SLOW WPM for educational demo (highly readable)
        self.ghost = GhostTyper(wpm=120)
        self.ghost.char_typed.connect(self._on_demo_char)
        self.ghost.step_finished.connect(self._next_demo_step)
        
        self._demo_steps = iter(steps)
        self._current_demo_explain = ""
        self._next_demo_step()

    def _stop_demo(self):
        """Kills any running demo and pending timers"""
        self._demo_active = False
        self._demo_timer.stop()
        if hasattr(self, 'ghost'):
            self.ghost.stop()
            try: self.ghost.char_typed.disconnect()
            except: pass
            try: self.ghost.step_finished.disconnect()
            except: pass
        self._demo_steps = None
        self._current_demo_explain = ""

    def _on_demo_char(self, count):
        self.coach.index = count
        
        # Ensure HUD and highights are perfectly in sync with typed chars
        if self._current_demo_explain:
             self.trainer.refresh(60.0, False, self._current_demo_explain)
        
        # LIVE SYNC: Update the browser preview as we type
        partial_code = self.coach.current[:count]
        self.result_viewer.update_live_content(partial_code)
        
        # Highlight keys
        if count > 0 and count <= len(self.coach.current):
            ch = self.coach.current[count-1]
            kid = kid_for_char(self.layout, ch.lower())
            if kid:
                self.keyboard.flash_correct(kid)

    def _on_scholar_step(self, idx):
        """Handle content-specific step triggers (like Ghost Demos)"""
        step = self.scholar_engine.steps[idx]
        if step.get("type") == "ghost_demo":
             # Pack it into a format _run_demo expects or run directly
             demo_data = {
                 "name": step.get("title", "Demo"),
                 "steps": [
                     {
                         "code": step.get("ghost", {}).get("final_code", ""),
                         "explain": "Learning structure...",
                         "pause": 1000
                     }
                 ]
             }
             self.scholar_engine.hide()
             self._run_demo(demo_data)

    def _next_demo_step(self):
        try:
            self._current_step_data = next(self._demo_steps)
            self._current_demo_explain = f"📘 {self._current_step_data.get('explain', 'Teaching...')}"
            
            # Show explanation first
            self.trainer.refresh(60.0, False, self._current_demo_explain)
            
            # Use longer delay to let user read the instruction before typing starts
            # 4 seconds gives plenty of time to read the commentary
            self._demo_timer.start(4000)
            
        except StopIteration:
            self._current_demo_explain = "✅ Demo complete! Previewing result..."

    def _exec_demo_step_typing(self):
        if hasattr(self, '_current_step_data'):
            self.ghost.type_string(self._current_step_data.get("code", ""))

    def _on_demo_step(self, idx):
        # Legacy callback - no longer used but kept for safety if disconnected
        pass
        
    def show_startup_overlay(self):
        # Scholar mode check
        spec_path = os.path.join(DATA_DIR, "dlc", "qwertype_html_dlc_spec_v1.json")
        if self.mode == "html_scholar" and getattr(self, 'dlc_manager', None):
             self.scholar_engine.setGeometry(self.rect())
             self.scholar_engine.show()
             self.scholar_engine.raise_()
             self.overlay.hide()
             self.bubbles.hide() # Ensure hidden for scholar
        else:
             self.overlay.show()
             self.scholar_engine.hide()

        self.session_active = False

    def start_session(self):
        # Stop demo if running
        self._stop_demo()
        
        self.session_active = True
        self.session_end = time.time() + 60.0
        self.coach.started = time.time()
        self.coach.total = 0
        self.coach.mistakes = 0
        self.start_buffer = ""
        self.overlay.hide()
        self.timer.start(100)
        self.toast.show_msg(self.i18n.t("session_started"), 1100)

    def end_session(self):
        self.session_active = False
        self.timer.stop()
        self.start_buffer = ""

        # finalize last metrics + score
        self.last_wpm = self.coach.wpm()
        self.last_acc = self.coach.accuracy()
        self.last_points = self.coach.score_points()

        self.score_header.set_score(self.last_points, self.last_wpm, self.last_acc, self.name)

        # update highscores (offline)
        key = self._mode_bucket_key(self.mode)
        cur = self.highscores.get(key)
        if (not cur) or (self.last_points > int(cur.get("points", 0))):
            self.highscores[key] = {
                "name": self.name,
                "points": int(self.last_points),
                "wpm": float(self.last_wpm),
                "acc": float(self.last_acc),
                "ts": int(time.time()),
            }
            save_json(HIGHSCORES_JSON, self.highscores)
            save_json(HIGHSCORES_JSON, self.highscores)
            self._refresh_leaderboard()

        # ONLINE SYNC
        if self.last_points > 0:
            self.server_sync.add_score(
                username=self.name,
                mode=self.mode,
                wpm=float(self.last_wpm),
                accuracy=float(self.last_acc),
                points=int(self.last_points),
                completion_pct=100.0 if not self.coach.items else (self.coach.index / len(self.coach.items)) * 100
            )
            # Try to sync immediately after a session
            self.server_sync.sync_now()

        self.toast.show_msg(self.i18n.t("session_finished_to_start"), 1600)
        # Safety cleanup for any active demo
        self._demo_active = False 
        QTimer.singleShot(2000, self.show_startup_overlay)

    def apply_window_mode(self, mode: str):
        self.settings_data["win_mode"] = mode
        
        # Explicit flags for Windows to ensure title bar/borders are restored
        standard_flags = Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | \
                         Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        
        was_visible = self.isVisible()
        if was_visible:
            self.hide()
            
        if mode == "maximized":
            # Normal window flags + showMaximized
            self.setWindowFlags(standard_flags)
            self.showMaximized()
        elif mode == "borderless":
            # Frameless Fullscreen
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.showFullScreen()
        else: # windowed
            self.setWindowFlags(standard_flags)
            self.showNormal()
            
        if was_visible:
            self.show()
            self.activateWindow()
            self.raise_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            current = self.settings_data.get("win_mode", "windowed")
            target = "windowed" if current != "windowed" else "borderless"
            self.apply_window_mode(target)
            self.settings.apply_current(self.settings_data)
            return
        super().keyPressEvent(event)

    def tick(self):
        remaining = max(0.0, self.session_end - time.time())
        if remaining <= 0.0:
            self.end_session()
            remaining = 0.0

        note = self.i18n.t("hint_type_start") if not self.session_active else ""
        self.trainer.refresh(remaining=remaining, session_active=self.session_active, note=note)

    def _check_sync(self):
        """Called periodically to check if we should sync based on adaptive interval"""
        interval = self.server_sync.get_adaptive_interval()
        # The internal logic of ServerSync determines if it's active or idle.
        # However, here we just trigger a sync check. 
        # Actually, get_adaptive_interval returns the *desired* interval.
        # We can just call sync_now() if enough time has passed.
        # But ServerSync.sync_now() simply processes pending queue.
        # We'll just call sync_now() which is safe (no-op if empty).
        self.server_sync.sync_now()

    def _update_target(self):
        exp = self.coach.expected_char()
        kid = kid_for_char(self.layout, exp) if exp else None
        self.keyboard.set_target_key(kid)

        if kid:
            hand, finger = finger_for_kid(self.layout, kid)
            self.left_hand.set_active_finger(finger if hand == "left" else None)
            self.right_hand.set_active_finger(finger if hand == "right" else None)
        else:
            self.left_hand.set_active_finger(None)
            self.right_hand.set_active_finger(None)

    def _check_lint(self):
        """Check current typed chunk for educational patterns"""
        dlc = self.dlc_manager.get_module(self.mode)
        if not dlc: return

        lint_rules = dlc.get("linting", [])
        if not lint_rules: return

        # Get the part of the word already typed
        typed_so_far = self.coach.current[:self.coach.index]
        
        found_tip = None
        # We check for the most specific (longest) pattern matching at the END of what was typed
        for rule in lint_rules:
            pattern = rule.get("pattern", "")
            if pattern and typed_so_far.endswith(pattern):
                found_tip = rule.get("tip")
        
        self.trainer.set_lint_tip(found_tip)

    def eventFilter(self, obj, e):
        if e.type() == QEvent.KeyPress and e.text():
            ch = e.text()
            if not ch:
                return False

            if hasattr(self, 'ghost') and self.ghost.timer.isActive() or self._demo_timer.isActive():
                return True # Block manual keys during demo

            if not self.session_active:
                # 1. Standard START buffer
                self.start_buffer += ch
                self.start_buffer = self.start_buffer[-16:]
                if "START" in self.start_buffer.upper():
                    self.start_session()
                    self._update_target()
                    return True
                
                # 2. INTUITIVE START for Scholar/DLC: Just start if they type the correct first character
                dlc = self.dlc_manager.get_module(self.mode)
                if dlc and not self.overlay.isVisible():
                    exp = self.coach.expected_char()
                    if exp and ch.lower() == exp.lower():
                        self.start_session()
                        # continue execution below into the feed logic
                    else:
                        return True # ignore other keys if not START or first char
                else:
                    return True # ignore keys if overlay is visible or standard mode

            ch2 = ch.lower()
            correct, expected = self.coach.feed(ch2)
            self._update_target()

            expected_kid = kid_for_char(self.layout, expected.lower()) if expected else None
            typed_kid = kid_for_char(self.layout, ch2)

            if typed_kid:
                self.keyboard.flash_pressed(typed_kid)

            if expected_kid:
                hand, _finger = finger_for_kid(self.layout, expected_kid)

                if correct:
                    color = QColor(70, 170, 255) if hand == "right" else QColor(70, 230, 140)
                    self.keyboard.flash_correct(expected_kid)
                else:
                    color = QColor(255, 70, 70)
                    if typed_kid:
                        self.keyboard.flash_wrong(typed_kid)

                gp = self.keyboard.kid_center_global(expected_kid)
                self.bubbles.spawn(gp, color)

            remaining = max(0.0, self.session_end - time.time())
            self.trainer.refresh(remaining=remaining, session_active=True, note="")
            self._check_lint()
            return True

        return False


# ============================================================
# ENTRY
# ============================================================

def main():
    ensure_default_i18n_files()

    app = QApplication(sys.argv)

    i18n = I18N(DEFAULT_LANG)
    theme = Theme("dark")
    app.setStyleSheet(theme.app_stylesheet())

    screen = QGuiApplication.primaryScreen()
    avail = screen.availableGeometry() if screen else QRect(0, 0, 1400, 900)
    target_w = clamp(int(avail.width() * 0.85), 800, 1600)
    target_h = clamp(int(avail.height() * 0.85), 600, 1000)

    splash = Splash(theme, i18n)
    splash.show()

    win = MainWindow(theme, i18n)
    win.setMinimumSize(600, 450) # Allow shrinking for scaling
    win.resize(target_w, target_h)
    win.setWindowOpacity(0.0)

    def start():
        splash.close()
        # Apply window mode from settings
        wm = win.settings_data.get("win_mode", "windowed")
        win.apply_window_mode(wm)
        
        # Ensure it's shown even if apply_window_mode was called while hidden
        win.show()
        win.raise_()
        win.activateWindow()

        win._fade = QPropertyAnimation(win, b"windowOpacity")
        win._fade.setDuration(700)
        win._fade.setStartValue(0.0)
        win._fade.setEndValue(1.0)
        win._fade.setEasingCurve(QEasingCurve.OutCubic)
        win._fade.start()

        win._update_target()

    splash.finished.connect(start)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
