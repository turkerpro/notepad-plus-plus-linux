"""
Notepad++ Find / Replace / Find in Files / Mark Dialog.
"""
import os
import re
from typing import Optional, List
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QRadioButton, QButtonGroup,
    QGroupBox, QFileDialog, QMessageBox, QTextEdit, QApplication
)
from PyQt5.QtGui import QTextCursor, QTextDocument, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from ..core.editor import NppEditor


class FindReplaceDialog(QDialog):
    """Notepad++ 4-Tab Find & Replace Window."""

    find_in_files_results = pyqtSignal(str, list)  # query, list of (file, line_num, text)

    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("Bul (Find)")
        self.resize(540, 360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # Tab 1: Bul (Find)
        self.tab_find = QWidget()
        self._build_find_tab()
        self.tabs.addTab(self.tab_find, "Bul (Find)")

        # Tab 2: Değiştir (Replace)
        self.tab_replace = QWidget()
        self._build_replace_tab()
        self.tabs.addTab(self.tab_replace, "Değiştir (Replace)")

        # Tab 3: Dosyalarda Bul (Find in Files)
        self.tab_files = QWidget()
        self._build_files_tab()
        self.tabs.addTab(self.tab_files, "Dosyalarda Bul (Find in Files)")

        # Tab 4: İşaretle (Mark)
        self.tab_mark = QWidget()
        self._build_mark_tab()
        self.tabs.addTab(self.tab_mark, "İşaretle (Mark)")

        # Common Options Group at Bottom
        options_layout = QHBoxLayout()

        # Checkboxes
        chk_box = QGroupBox("Seçenekler (Options)")
        chk_layout = QVBoxLayout(chk_box)
        self.chk_match_case = QCheckBox("Büyük/küçük harf eşleştir (Match case)")
        self.chk_whole_word = QCheckBox("Tam sözcük (Match whole word)")
        self.chk_wrap = QCheckBox("Başa dön (Wrap around)")
        self.chk_wrap.setChecked(True)
        chk_layout.addWidget(self.chk_match_case)
        chk_layout.addWidget(self.chk_whole_word)
        chk_layout.addWidget(self.chk_wrap)
        options_layout.addWidget(chk_box)

        # Search Mode
        mode_box = QGroupBox("Arama Kipi (Search Mode)")
        mode_layout = QVBoxLayout(mode_box)
        self.rb_normal = QRadioButton("Normal")
        self.rb_extended = QRadioButton("Genişletilmiş (\\n, \\r, \\t, \\0)")
        self.rb_regex = QRadioButton("Düzenli İfade (Regular expression)")
        self.rb_normal.setChecked(True)

        mode_layout.addWidget(self.rb_normal)
        mode_layout.addWidget(self.rb_extended)
        mode_layout.addWidget(self.rb_regex)
        options_layout.addWidget(mode_box)

        main_layout.addLayout(options_layout)

        # Status line
        self.lbl_status = QLabel("", self)
        self.lbl_status.setStyleSheet("color: #0066CC; font-weight: bold;")
        main_layout.addWidget(self.lbl_status)

    def _build_find_tab(self):
        layout = QHBoxLayout(self.tab_find)

        left = QVBoxLayout()
        left.addWidget(QLabel("Aranan (Find what):"))
        self.txt_find = QLineEdit()
        left.addWidget(self.txt_find)
        left.addStretch()
        layout.addLayout(left, 3)

        right = QVBoxLayout()
        btn_next = QPushButton("Sonrakini Bul (Find Next)")
        btn_prev = QPushButton("Öncekini Bul (Find Prev)")
        btn_count = QPushButton("Say (Count)")
        btn_close = QPushButton("Kapat (Close)")

        btn_next.clicked.connect(self.find_next)
        btn_prev.clicked.connect(self.find_prev)
        btn_count.clicked.connect(self.count_matches)
        btn_close.clicked.connect(self.hide)

        right.addWidget(btn_next)
        right.addWidget(btn_prev)
        right.addWidget(btn_count)
        right.addWidget(btn_close)
        right.addStretch()
        layout.addLayout(right, 1)

    def _build_replace_tab(self):
        layout = QHBoxLayout(self.tab_replace)

        left = QVBoxLayout()
        left.addWidget(QLabel("Aranan (Find what):"))
        self.txt_replace_find = QLineEdit()
        left.addWidget(self.txt_replace_find)

        left.addWidget(QLabel("Değiştirilecek (Replace with):"))
        self.txt_replace_with = QLineEdit()
        left.addWidget(self.txt_replace_with)
        left.addStretch()
        layout.addLayout(left, 3)

        right = QVBoxLayout()
        btn_next = QPushButton("Sonrakini Bul (Find Next)")
        btn_replace = QPushButton("Değiştir (Replace)")
        btn_rep_all = QPushButton("Tümünü Değiştir (Replace All)")
        btn_close = QPushButton("Kapat (Close)")

        btn_next.clicked.connect(self.find_next)
        btn_replace.clicked.connect(self.replace_one)
        btn_rep_all.clicked.connect(self.replace_all)
        btn_close.clicked.connect(self.hide)

        right.addWidget(btn_next)
        right.addWidget(btn_replace)
        right.addWidget(btn_rep_all)
        right.addWidget(btn_close)
        right.addStretch()
        layout.addLayout(right, 1)

    def _build_files_tab(self):
        layout = QHBoxLayout(self.tab_files)

        left = QVBoxLayout()
        left.addWidget(QLabel("Aranan (Find what):"))
        self.txt_files_find = QLineEdit()
        left.addWidget(self.txt_files_find)

        left.addWidget(QLabel("Filtreler (Filters):"))
        self.txt_files_filter = QLineEdit("*.*")
        left.addWidget(self.txt_files_filter)

        left.addWidget(QLabel("Dizin (Directory):"))
        dir_layout = QHBoxLayout()
        self.txt_files_dir = QLineEdit(os.getcwd())
        btn_browse = QPushButton("...")
        btn_browse.setMaximumWidth(32)
        btn_browse.clicked.connect(self._browse_dir)
        dir_layout.addWidget(self.txt_files_dir)
        dir_layout.addWidget(btn_browse)
        left.addLayout(dir_layout)
        left.addStretch()
        layout.addLayout(left, 3)

        right = QVBoxLayout()
        btn_find_files = QPushButton("Tümünü Bul (Find All)")
        btn_close = QPushButton("Kapat (Close)")
        btn_find_files.clicked.connect(self.find_in_files)
        btn_close.clicked.connect(self.hide)

        right.addWidget(btn_find_files)
        right.addWidget(btn_close)
        right.addStretch()
        layout.addLayout(right, 1)

    def _build_mark_tab(self):
        layout = QHBoxLayout(self.tab_mark)

        left = QVBoxLayout()
        left.addWidget(QLabel("İşaretlenecek (Mark what):"))
        self.txt_mark_find = QLineEdit()
        left.addWidget(self.txt_mark_find)
        left.addStretch()
        layout.addLayout(left, 3)

        right = QVBoxLayout()
        btn_mark = QPushButton("Tümünü İşaretle (Mark All)")
        btn_clear = QPushButton("Tümünü Temizle (Clear All)")
        btn_close = QPushButton("Kapat (Close)")

        btn_mark.clicked.connect(self.mark_all)
        btn_clear.clicked.connect(self.clear_marks)
        btn_close.clicked.connect(self.hide)

        right.addWidget(btn_mark)
        right.addWidget(btn_clear)
        right.addWidget(btn_close)
        right.addStretch()
        layout.addLayout(right, 1)

    def show_tab(self, tab_index: int):
        self.tabs.setCurrentIndex(tab_index)
        editor = self.main_window.tab_manager.active_editor()
        if editor and editor.textCursor().hasSelection():
            sel = editor.textCursor().selectedText()
            self.txt_find.setText(sel)
            self.txt_replace_find.setText(sel)
            self.txt_files_find.setText(sel)
            self.txt_mark_find.setText(sel)
        self.show()
        self.activateWindow()

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Dizin Seç", self.txt_files_dir.text())
        if d:
            self.txt_files_dir.setText(d)

    def _get_query_and_flags(self, explicit_query: Optional[str] = None) -> tuple:
        if explicit_query is not None:
            query = explicit_query
        else:
            cur_tab = self.tabs.currentIndex()
            if cur_tab == 0:
                query = self.txt_find.text()
            elif cur_tab == 1:
                query = self.txt_replace_find.text() or self.txt_find.text()
            elif cur_tab == 2:
                query = self.txt_files_find.text() or self.txt_find.text()
            else:
                query = self.txt_mark_find.text() or self.txt_find.text()

        flags = QTextDocument.FindFlags()
        if self.chk_match_case.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.chk_whole_word.isChecked():
            flags |= QTextDocument.FindWholeWords

        if self.rb_extended.isChecked():
            query = query.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\0", "\0")

        return query, flags

    def find_next(self):
        editor = self.main_window.tab_manager.active_editor()
        if not editor: return
        query, flags = self._get_query_and_flags()
        if not query: return

        found = editor.find(query, flags)
        if not found and self.chk_wrap.isChecked():
            # Move to start and find again
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            editor.setTextCursor(cursor)
            found = editor.find(query, flags)

        if found:
            self.lbl_status.setText("Bulundu.")
        else:
            self.lbl_status.setText(f"'{query}' bulunamadı.")

    def find_prev(self):
        editor = self.main_window.tab_manager.active_editor()
        if not editor: return
        query, flags = self._get_query_and_flags()
        if not query: return

        flags |= QTextDocument.FindBackward
        found = editor.find(query, flags)
        if not found and self.chk_wrap.isChecked():
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            editor.setTextCursor(cursor)
            found = editor.find(query, flags)

        if found:
            self.lbl_status.setText("Bulundu.")
        else:
            self.lbl_status.setText(f"'{query}' bulunamadı.")

    def count_matches(self):
        editor = self.main_window.tab_manager.active_editor()
        if not editor: return
        query, _ = self._get_query_and_flags()
        if not query: return

        text = editor.toPlainText()
        if self.chk_match_case.isChecked():
            count = text.count(query)
        else:
            count = text.lower().count(query.lower())
        self.lbl_status.setText(f"Toplam {count} eşleşme bulundu.")

    def replace_one(self):
        editor = self.main_window.tab_manager.active_editor()
        if not editor: return
        query = self.txt_replace_find.text() or self.txt_find.text()
        query, flags = self._get_query_and_flags(query)
        if not query: return
        replace_text = self.txt_replace_with.text()
        if self.rb_extended.isChecked():
            replace_text = replace_text.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")

        cursor = editor.textCursor()
        if cursor.hasSelection() and (
            cursor.selectedText() == query or
            (not self.chk_match_case.isChecked() and cursor.selectedText().lower() == query.lower())
        ):
            cursor.insertText(replace_text)
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        editor = self.main_window.tab_manager.active_editor()
        if not editor: return
        query = self.txt_replace_find.text() or self.txt_find.text()
        query, flags = self._get_query_and_flags(query)
        if not query: return
        replace_text = self.txt_replace_with.text()
        if self.rb_extended.isChecked():
            replace_text = replace_text.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")

        cursor = editor.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

        count = 0
        while editor.find(query, flags):
            editor.textCursor().insertText(replace_text)
            count += 1

        cursor.endEditBlock()
        self.lbl_status.setText(f"{count} öğe değiştirildi.")

    def mark_all(self):
        editor = self.main_window.tab_manager.active_editor()
        if not editor: return
        query, _ = self._get_query_and_flags()
        if not query: return
        editor.highlighter.set_search_highlight_word(query)
        self.lbl_status.setText(f"'{query}' tüm belgede işaretlendi.")

    def clear_marks(self):
        editor = self.main_window.tab_manager.active_editor()
        if editor:
            editor.highlighter.set_search_highlight_word("")
        self.lbl_status.setText("İşaretler temizlendi.")

    def find_in_files(self):
        query = self.txt_files_find.text()
        directory = self.txt_files_dir.text()
        pattern = self.txt_files_filter.text()
        if not query or not os.path.isdir(directory):
            return

        results = []
        import fnmatch
        patterns = [p.strip() for p in pattern.split(";") if p.strip()]

        for root, _, files in os.walk(directory):
            for fname in files:
                if any(fnmatch.fnmatch(fname, p) for p in patterns) or "*.*" in patterns:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                if (query in line if self.chk_match_case.isChecked() else query.lower() in line.lower()):
                                    results.append((fpath, idx, line.strip()))
                    except Exception:
                        pass

        self.find_in_files_results.emit(query, results)
        self.lbl_status.setText(f"{len(results)} dosya satırı bulundu.")
