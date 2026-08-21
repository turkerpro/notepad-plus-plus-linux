"""
Document Map (Minimap) dock panel for Notepad++ Linux.
"""
from PyQt5.QtWidgets import QDockWidget, QPlainTextEdit, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont, QColor, QPainter, QMouseEvent
from PyQt5.QtCore import Qt, QRect

from ...core.editor import NppEditor


class MinimapView(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor: NppEditor = None
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        font = QFont("Monospace", 2)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setStyleSheet("background-color: #1E1E1E; color: #707070; border: none;")

    def set_editor(self, editor: NppEditor):
        self.editor = editor
        if editor:
            self.setDocument(editor.document())
            self.editor.verticalScrollBar().valueChanged.connect(self._sync_scroll)
        else:
            self.clear()

    def _sync_scroll(self, val):
        if not self.editor: return
        max_ed = self.editor.verticalScrollBar().maximum()
        max_map = self.verticalScrollBar().maximum()
        if max_ed > 0:
            ratio = val / max_ed
            self.verticalScrollBar().setValue(int(ratio * max_map))
        self.viewport().update()

    def mousePressEvent(self, event: QMouseEvent):
        if not self.editor: return
        # Calculate line from click position
        cursor = self.cursorForPosition(event.pos())
        target_line = cursor.blockNumber() + 1
        self.editor.go_to_line(target_line)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.mousePressEvent(event)


class DocumentMapDock(QDockWidget):
    """Document Map (Minimap) Dock Widget."""

    def __init__(self, parent=None):
        super().__init__("Belge Haritası (Document Map)", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.minimap = MinimapView(self)
        self.setWidget(self.minimap)

    def set_active_editor(self, editor: NppEditor):
        self.minimap.set_editor(editor)
