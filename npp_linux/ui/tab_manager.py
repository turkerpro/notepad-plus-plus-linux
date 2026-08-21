"""
Custom TabBar and Document Tab Management for Notepad++ Linux.
Features blue/red floppy disk modified indicators, close buttons, right-click context menu,
and dual-view (split-screen) capabilities.
"""
import os
import subprocess
from typing import Optional, List, Dict, Tuple
from PyQt5.QtWidgets import (
    QTabWidget, QTabBar, QMenu, QAction, QApplication, QMessageBox,
    QWidget, QVBoxLayout, QSplitter, QLabel
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QPoint

from ..core.document import Document
from ..core.editor import NppEditor


def create_floppy_icon(is_modified: bool, is_readonly: bool = False) -> QIcon:
    """Create authentic Notepad++ floppy disk status icon."""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, False)

    # Disk body color: Blue for saved, Red for modified, Grey for readonly
    if is_readonly:
        body_color = QColor("#808080")
        label_color = QColor("#CCCCCC")
    elif is_modified:
        body_color = QColor("#D32F2F")  # Red
        label_color = QColor("#FFCDD2")
    else:
        body_color = QColor("#1976D2")  # Blue
        label_color = QColor("#BBDEFB")

    # Main disk rectangle
    painter.setPen(body_color.darker(150))
    painter.setBrush(body_color)
    painter.drawRect(1, 1, 13, 13)

    # Top shutter / metal slider
    painter.setPen(QColor("#B0BEC5"))
    painter.setBrush(QColor("#CFD8DC"))
    painter.drawRect(3, 1, 7, 5)
    painter.setPen(QColor("#455A64"))
    painter.drawLine(5, 2, 5, 5)

    # Bottom paper label
    painter.setPen(body_color.darker(130))
    painter.setBrush(label_color)
    painter.drawRect(3, 8, 9, 6)

    # Label lines
    painter.setPen(body_color.darker(110))
    painter.drawLine(4, 10, 10, 10)
    painter.drawLine(4, 12, 10, 12)

    painter.end()
    return QIcon(pixmap)


class NppTabBar(QTabBar):
    """Custom tab bar supporting middle click close and context menu."""

    tab_close_requested = pyqtSignal(int)
    open_folder_requested = pyqtSignal(int)
    copy_path_requested = pyqtSignal(int)
    copy_name_requested = pyqtSignal(int)
    move_to_other_view_requested = pyqtSignal(int)
    clone_to_other_view_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.tabCloseRequested.connect(self.tab_close_requested.emit)

    def mouseReleaseEvent(self, event):
        # Middle-click to close tab
        if event.button() == Qt.MiddleButton:
            tab_index = self.tabAt(event.pos())
            if tab_index != -1:
                self.tab_close_requested.emit(tab_index)
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def show_context_menu(self, pos: QPoint):
        tab_index = self.tabAt(pos)
        if tab_index == -1:
            return

        menu = QMenu(self)
        act_close = menu.addAction("Kapat (Close)")
        act_close_others = menu.addAction("Diğerlerini Kapat (Close Others)")
        act_close_right = menu.addAction("Sağdakileri Kapat (Close to the Right)")
        act_close_left = menu.addAction("Soldakileri Kapat (Close to the Left)")
        menu.addSeparator()
        act_open_folder = menu.addAction("Dosya Konumunu Aç (Open Containing Folder)")
        act_copy_path = menu.addAction("Tam Dosya Yolunu Kopyala (Copy Full Path)")
        act_copy_name = menu.addAction("Dosya Adını Kopyala (Copy File Name)")
        menu.addSeparator()
        act_move_other = menu.addAction("Diğer Görünüme Taşı (Move to Other View)")
        act_clone_other = menu.addAction("Diğer Görünüme Klonla (Clone to Other View)")

        action = menu.exec_(self.mapToGlobal(pos))
        if not action:
            return

        if action == act_close:
            self.tab_close_requested.emit(tab_index)
        elif action == act_close_others:
            for i in range(self.count() - 1, -1, -1):
                if i != tab_index:
                    self.tab_close_requested.emit(i)
        elif action == act_close_right:
            for i in range(self.count() - 1, tab_index, -1):
                self.tab_close_requested.emit(i)
        elif action == act_close_left:
            for i in range(tab_index - 1, -1, -1):
                self.tab_close_requested.emit(i)
        elif action == act_open_folder:
            self.open_folder_requested.emit(tab_index)
        elif action == act_copy_path:
            self.copy_path_requested.emit(tab_index)
        elif action == act_copy_name:
            self.copy_name_requested.emit(tab_index)
        elif action == act_move_other:
            self.move_to_other_view_requested.emit(tab_index)
        elif action == act_clone_other:
            self.clone_to_other_view_requested.emit(tab_index)


class NppTabWidget(QTabWidget):
    """Container tab widget hosting multiple NppEditors."""

    current_editor_changed = pyqtSignal(object)  # emits NppEditor

    def __init__(self, parent=None):
        super().__init__(parent)
        self.custom_tab_bar = NppTabBar(self)
        self.setTabBar(self.custom_tab_bar)

        self.custom_tab_bar.tab_close_requested.connect(self.close_tab)
        self.custom_tab_bar.open_folder_requested.connect(self.open_containing_folder)
        self.custom_tab_bar.copy_path_requested.connect(self.copy_file_path)
        self.custom_tab_bar.copy_name_requested.connect(self.copy_file_name)
        self.currentChanged.connect(self.on_current_changed)

    def add_editor(self, editor: NppEditor, title: Optional[str] = None) -> int:
        doc = editor.document_model
        display_title = title or doc.title
        icon = create_floppy_icon(doc.is_modified, doc.is_readonly)
        index = self.addTab(editor, icon, display_title)

        doc.modified_changed.connect(lambda mod: self.update_tab_icon(editor))
        doc.title_changed.connect(lambda t: self.update_tab_title(editor, t))
        doc.readonly_changed.connect(lambda ro: self.update_tab_icon(editor))

        self.setCurrentIndex(index)
        return index

    def current_editor(self) -> Optional[NppEditor]:
        widget = self.currentWidget()
        if isinstance(widget, NppEditor):
            return widget
        return None

    def get_editor(self, index: int) -> Optional[NppEditor]:
        widget = self.widget(index)
        if isinstance(widget, NppEditor):
            return widget
        return None

    def on_current_changed(self, index: int):
        ed = self.get_editor(index)
        self.current_editor_changed.emit(ed)

    def update_tab_icon(self, editor: NppEditor):
        index = self.indexOf(editor)
        if index != -1:
            doc = editor.document_model
            icon = create_floppy_icon(doc.is_modified, doc.is_readonly)
            self.setTabIcon(index, icon)

    def update_tab_title(self, editor: NppEditor, title: str):
        index = self.indexOf(editor)
        if index != -1:
            self.setTabText(index, title)

    def close_tab(self, index: int) -> bool:
        editor = self.get_editor(index)
        if not editor:
            return False

        doc = editor.document_model
        if doc.is_modified:
            res = QMessageBox.question(
                self,
                "Kaydet (Save)",
                f"'{doc.title}' değiştirildi. Kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            if res == QMessageBox.Yes:
                if not doc.file_path:
                    # Request save as from parent window
                    return False
                doc.save(editor.toPlainText())
            elif res == QMessageBox.Cancel:
                return False

        self.removeTab(index)
        return True

    def open_containing_folder(self, index: int):
        editor = self.get_editor(index)
        if editor and editor.document_model.file_path:
            folder = os.path.dirname(editor.document_model.file_path)
            try:
                subprocess.Popen(["xdg-open", folder])
            except Exception as e:
                print(f"Cannot open folder: {e}")

    def copy_file_path(self, index: int):
        editor = self.get_editor(index)
        if editor and editor.document_model.file_path:
            QApplication.clipboard().setText(editor.document_model.file_path)

    def copy_file_name(self, index: int):
        editor = self.get_editor(index)
        if editor:
            QApplication.clipboard().setText(editor.document_model.title)


class NppTabManager(QWidget):
    """
    Dual View / Split View Tab Manager supporting primary and secondary split panes.
    """

    active_editor_changed = pyqtSignal(object)  # emits active NppEditor

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal, self)
        layout.addWidget(self.splitter)

        self.primary_view = NppTabWidget(self)
        self.secondary_view = NppTabWidget(self)
        self.secondary_view.hide()

        self.splitter.addWidget(self.primary_view)
        self.splitter.addWidget(self.secondary_view)

        self.primary_view.current_editor_changed.connect(self._on_editor_activated)
        self.secondary_view.current_editor_changed.connect(self._on_editor_activated)

        # Tab actions
        self.primary_view.custom_tab_bar.move_to_other_view_requested.connect(
            lambda idx: self.move_tab(self.primary_view, self.secondary_view, idx)
        )
        self.primary_view.custom_tab_bar.clone_to_other_view_requested.connect(
            lambda idx: self.clone_tab(self.primary_view, self.secondary_view, idx)
        )
        self.secondary_view.custom_tab_bar.move_to_other_view_requested.connect(
            lambda idx: self.move_tab(self.secondary_view, self.primary_view, idx)
        )
        self.secondary_view.custom_tab_bar.clone_to_other_view_requested.connect(
            lambda idx: self.clone_tab(self.secondary_view, self.primary_view, idx)
        )

        self._active_tab_widget = self.primary_view

    def active_editor(self) -> Optional[NppEditor]:
        return self._active_tab_widget.current_editor()

    def all_editors(self) -> List[NppEditor]:
        editors = []
        for i in range(self.primary_view.count()):
            ed = self.primary_view.get_editor(i)
            if ed: editors.append(ed)
        for i in range(self.secondary_view.count()):
            ed = self.secondary_view.get_editor(i)
            if ed: editors.append(ed)
        return editors

    def _on_editor_activated(self, editor: Optional[NppEditor]):
        sender = self.sender()
        if sender in (self.primary_view, self.secondary_view):
            self._active_tab_widget = sender
        self.active_editor_changed.emit(editor)

    def add_document(self, doc: Document) -> NppEditor:
        editor = NppEditor(doc, self)
        self._active_tab_widget.add_editor(editor)
        return editor

    def move_tab(self, source_view: NppTabWidget, target_view: NppTabWidget, index: int):
        editor = source_view.get_editor(index)
        if not editor:
            return
        source_view.removeTab(index)
        target_view.show()
        target_view.add_editor(editor)
        self.splitter.setSizes([self.width() // 2, self.width() // 2])

        if source_view.count() == 0 and source_view == self.secondary_view:
            self.secondary_view.hide()

    def clone_tab(self, source_view: NppTabWidget, target_view: NppTabWidget, index: int):
        editor = source_view.get_editor(index)
        if not editor:
            return
        # Create a new editor sharing the exact same QTextDocument
        clone_ed = NppEditor(editor.document_model, self)
        clone_ed.setDocument(editor.document())
        target_view.show()
        target_view.add_editor(clone_ed)
        self.splitter.setSizes([self.width() // 2, self.width() // 2])
