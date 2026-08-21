"""
Search Results Output Panel for Find in Files in Notepad++ Linux.
"""
from typing import List, Tuple
from PyQt5.QtWidgets import (
    QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
    QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal


class SearchResultsDock(QDockWidget):
    """Search Results Dock Panel at bottom."""

    result_selected = pyqtSignal(str, int)  # file_path, line_number

    def __init__(self, parent=None):
        super().__init__("Arama Sonuçları (Search results)", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        # Header info
        hdr_layout = QHBoxLayout()
        self.lbl_info = QLabel("Arama sonuçları yok.")
        self.btn_clear = QPushButton("Temizle (Clear)")
        self.btn_clear.clicked.connect(self.clear_results)
        hdr_layout.addWidget(self.lbl_info)
        hdr_layout.addStretch()
        hdr_layout.addWidget(self.btn_clear)
        layout.addLayout(hdr_layout)

        # Results tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Dosya / Eşleşme (File / Match)", "Satır (Line)", "İçerik (Content)"])
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 80)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)

        self.setWidget(widget)

    def set_results(self, query: str, results: List[Tuple[str, int, str]]):
        self.tree.clear()
        self.lbl_info.setText(f"'{query}' için {len(results)} eşleşme bulundu:")

        # Group by file
        file_groups = {}
        for fpath, lnum, ltext in results:
            if fpath not in file_groups:
                file_groups[fpath] = []
            file_groups[fpath].append((lnum, ltext))

        for fpath, matches in file_groups.items():
            parent_item = QTreeWidgetItem(self.tree, [f"📁 {fpath} ({len(matches)} eşleşme)", "", ""])
            parent_item.setData(0, Qt.UserRole, fpath)
            for lnum, ltext in matches:
                child = QTreeWidgetItem(parent_item, ["", str(lnum), ltext])
                child.setData(0, Qt.UserRole, fpath)
                child.setData(1, Qt.UserRole, lnum)

        self.tree.expandAll()
        self.show()

    def clear_results(self):
        self.tree.clear()
        self.lbl_info.setText("Arama sonuçları yok.")

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        fpath = item.data(0, Qt.UserRole)
        lnum = item.data(1, Qt.UserRole)
        if fpath and lnum:
            self.result_selected.emit(fpath, int(lnum))
