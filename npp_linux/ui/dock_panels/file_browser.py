"""
Folder as Workspace / File Browser dock panel for Notepad++ Linux.
"""
import os
from PyQt5.QtWidgets import (
    QDockWidget, QTreeView, QFileSystemModel, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex


class FileBrowserDock(QDockWidget):
    """File Tree / Workspace dock panel."""

    file_open_requested = pyqtSignal(str)

    def __init__(self, root_path: str = os.getcwd(), parent=None):
        super().__init__("Çalışma Alanı (Folder as Workspace)", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        # Top Bar with change directory button
        top_layout = QHBoxLayout()
        self.btn_open_folder = QPushButton("Klasör Aç... (Open Folder...)")
        self.btn_open_folder.clicked.connect(self._select_folder)
        top_layout.addWidget(self.btn_open_folder)
        layout.addLayout(top_layout)

        # File system model & tree
        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_path))
        self.tree.setHeaderHidden(True)
        # Hide Size, Type, Date columns, keep only Name
        for col in range(1, 4):
            self.tree.hideColumn(col)

        self.tree.doubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)

        self.setWidget(widget)

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç (Select Folder)", self.model.rootPath())
        if folder:
            self.set_root_folder(folder)

    def set_root_folder(self, folder_path: str):
        if os.path.isdir(folder_path):
            self.model.setRootPath(folder_path)
            self.tree.setRootIndex(self.model.index(folder_path))

    def _on_item_double_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.file_open_requested.emit(path)
