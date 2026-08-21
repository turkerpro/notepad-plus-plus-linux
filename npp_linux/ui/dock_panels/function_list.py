"""
Function List and Code Symbols dock panel for Notepad++ Linux.
"""
import re
from typing import Optional
from PyQt5.QtWidgets import (
    QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
    QLineEdit, QHBoxLayout, QPushButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from ...core.editor import NppEditor


class FunctionListDock(QDockWidget):
    """Function List dock window."""

    def __init__(self, parent=None):
        super().__init__("Fonksiyon Listesi (Function List)", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.current_editor: Optional[NppEditor] = None

        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        # Filter bar
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Sembol filtrele...")
        self.txt_filter.textChanged.connect(self._filter_tree)
        layout.addWidget(self.txt_filter)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)

        self.setWidget(widget)

    def set_active_editor(self, editor: Optional[NppEditor]):
        if self.current_editor and self.current_editor != editor:
            try:
                self.current_editor.textChanged.disconnect(self.refresh_symbols)
            except Exception:
                pass

        self.current_editor = editor
        if editor:
            editor.textChanged.connect(self.refresh_symbols)
            self.refresh_symbols()
        else:
            self.tree.clear()

    def refresh_symbols(self):
        self.tree.clear()
        if not self.current_editor:
            return

        text = self.current_editor.toPlainText()
        lang = self.current_editor.document_model.language

        # Regex patterns for different languages
        patterns = []
        if lang == "Python":
            patterns = [
                (r'^(?:async\s+)?def\s+([a-zA-Z0-9_]+)\s*\(', "def"),
                (r'^class\s+([a-zA-Z0-9_]+)', "class")
            ]
        elif lang in ("C", "C++", "C/C++ Header", "Java", "C#", "Rust", "Go"):
            patterns = [
                (r'^\s*(?:[\w\<\>\*]+\s+)+([a-zA-Z0-9_]+)\s*\([^;]*\)\s*\{?', "fn"),
                (r'^\s*(?:class|struct|interface|enum)\s+([a-zA-Z0-9_]+)', "class"),
                (r'^\s*fn\s+([a-zA-Z0-9_]+)', "fn"),
                (r'^\s*func\s+(?:\([^\)]+\)\s+)?([a-zA-Z0-9_]+)', "fn")
            ]
        elif lang in ("JavaScript", "TypeScript", "React JSX", "React TSX", "PHP"):
            patterns = [
                (r'^\s*(?:function|async\s+function)\s+([a-zA-Z0-9_]+)', "fn"),
                (r'^\s*(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', "fn"),
                (r'^\s*class\s+([a-zA-Z0-9_]+)', "class")
            ]
        else:
            # Generic function match
            patterns = [
                (r'^\s*(?:def|function|func|fn|class)\s+([a-zA-Z0-9_]+)', "symbol")
            ]

        lines = text.split('\n')
        for idx, line in enumerate(lines, 1):
            for pat, sym_type in patterns:
                m = re.search(pat, line)
                if m:
                    name = m.group(1)
                    prefix = "🏷️ " if sym_type == "class" else "⚡ "
                    item = QTreeWidgetItem(self.tree, [f"{prefix}{name} (Satır {idx})"])
                    item.setData(0, Qt.UserRole, idx)
                    break

        self.tree.expandAll()

    def _filter_tree(self, query: str):
        query = query.lower()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            match = query in item.text(0).lower()
            item.setHidden(not match)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        line = item.data(0, Qt.UserRole)
        if line and self.current_editor:
            self.current_editor.go_to_line(line)
