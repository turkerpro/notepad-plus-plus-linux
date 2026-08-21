"""
6-Panel Status Bar matching classic Notepad++ layout.
"""
from PyQt5.QtWidgets import QStatusBar, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, pyqtSignal

from ..core.encoding import EOL_WINDOWS, EOL_UNIX, EOL_MAC, ENCODINGS


class NppStatusBar(QStatusBar):
    """Notepad++ Status Bar with live document indicators."""

    eol_change_requested = pyqtSignal(str)
    encoding_change_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(True)

        # Panel 1: Document Length and Line Count
        self.lbl_length = QLabel("length : 0  lines : 1", self)
        self.lbl_length.setAlignment(Qt.AlignCenter)
        self.lbl_length.setMinimumWidth(180)

        # Panel 2: Line, Column, Position, Selection
        self.lbl_pos = QLabel("Ln : 1  Col : 1  Pos : 1  |  Sel : 0", self)
        self.lbl_pos.setAlignment(Qt.AlignCenter)
        self.lbl_pos.setMinimumWidth(220)

        # Panel 3: Line Ending Format (CRLF / LF / CR)
        self.lbl_eol = QLabel("Windows (CR LF)", self)
        self.lbl_eol.setAlignment(Qt.AlignCenter)
        self.lbl_eol.setMinimumWidth(140)
        self.lbl_eol.setCursor(Qt.PointingHandCursor)
        self.lbl_eol.mouseDoubleClickEvent = self._on_eol_double_clicked

        # Panel 4: Character Encoding
        self.lbl_encoding = QLabel("UTF-8", self)
        self.lbl_encoding.setAlignment(Qt.AlignCenter)
        self.lbl_encoding.setMinimumWidth(120)
        self.lbl_encoding.setCursor(Qt.PointingHandCursor)
        self.lbl_encoding.mousePressEvent = self._on_encoding_clicked

        # Panel 5: Active Syntax Language
        self.lbl_language = QLabel("Plain Text", self)
        self.lbl_language.setAlignment(Qt.AlignCenter)
        self.lbl_language.setMinimumWidth(100)

        # Panel 6: INS / OVR Mode
        self.lbl_mode = QLabel("INS", self)
        self.lbl_mode.setAlignment(Qt.AlignCenter)
        self.lbl_mode.setMinimumWidth(50)

        # Add permanent widgets in order
        self.addPermanentWidget(self.lbl_length)
        self.addPermanentWidget(self.lbl_pos)
        self.addPermanentWidget(self.lbl_eol)
        self.addPermanentWidget(self.lbl_encoding)
        self.addPermanentWidget(self.lbl_language)
        self.addPermanentWidget(self.lbl_mode)

    def update_position(self, line: int, col: int, pos: int, sel_len: int = 0):
        self.lbl_pos.setText(f"Ln : {line}  Col : {col}  Pos : {pos + 1}  |  Sel : {sel_len}")

    def update_length(self, doc_length: int, line_count: int):
        self.lbl_length.setText(f"length : {doc_length:,}  lines : {line_count:,}")

    def update_eol(self, eol: str):
        mapping = {
            EOL_WINDOWS: "Windows (CR LF)",
            EOL_UNIX: "Unix (LF)",
            EOL_MAC: "Macintosh (CR)"
        }
        self.lbl_eol.setText(mapping.get(eol, eol))

    def update_encoding(self, encoding: str):
        self.lbl_encoding.setText(encoding)

    def update_language(self, language: str):
        self.lbl_language.setText(language)

    def update_mode(self, is_overwrite: bool):
        self.lbl_mode.setText("OVR" if is_overwrite else "INS")

    def _on_eol_double_clicked(self, event):
        menu = QMenu(self)
        a_win = menu.addAction("Windows (CR LF)")
        a_unix = menu.addAction("Unix (LF)")
        a_mac = menu.addAction("Macintosh (CR)")
        action = menu.exec_(self.lbl_eol.mapToGlobal(event.pos()))
        if action == a_win:
            self.eol_change_requested.emit(EOL_WINDOWS)
        elif action == a_unix:
            self.eol_change_requested.emit(EOL_UNIX)
        elif action == a_mac:
            self.eol_change_requested.emit(EOL_MAC)

    def _on_encoding_clicked(self, event):
        menu = QMenu(self)
        for friendly_name, _ in ENCODINGS[:8]:  # Top most common
            act = menu.addAction(friendly_name)
            act.triggered.connect(lambda checked, name=friendly_name: self.encoding_change_requested.emit(name))
        menu.exec_(self.lbl_encoding.mapToGlobal(event.pos()))
