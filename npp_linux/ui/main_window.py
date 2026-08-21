"""
Main Application Window for Notepad++ Linux.
"""
import os
import sys
import subprocess
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
    QApplication, QInputDialog
)
from PyQt5.QtGui import QIcon, QKeySequence, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QUrl

from ..core.document import Document
from ..core.editor import NppEditor
from ..core.encoding import ENCODINGS, EOL_WINDOWS, EOL_UNIX, EOL_MAC
from ..core.macro import MacroManager
from ..core.session import save_session, load_session, save_config, load_config
from ..styles.themes import THEME_PRESETS, get_app_stylesheet

from .tab_manager import NppTabManager
from .status_bar import NppStatusBar
from .toolbar import NppToolBar, get_icon
from .find_replace import FindReplaceDialog
from .goto_line import GoToLineDialog
from .style_configurator import StyleConfiguratorDialog
from .about_dialog import AboutDialog
from .dock_panels import (
    DocumentMapDock, FunctionListDock, FileBrowserDock, SearchResultsDock
)


class NppMainWindow(QMainWindow):
    """Notepad++ Main Application Window."""

    def __init__(self, files_to_open: Optional[List[str]] = None, initial_line: Optional[int] = None):
        super().__init__()
        self.setWindowTitle("Notepad++ (Linux)")
        self.resize(1100, 720)
        self.setAcceptDrops(True)

        # Set Window Chameleon Icon
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "resources", "icons", "npp.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Load Preferences
        self.config = load_config()
        self.macro_manager = MacroManager(self)

        # Central Tab Manager
        self.tab_manager = NppTabManager(self)
        self.setCentralWidget(self.tab_manager)

        # Status Bar
        self.status_bar = NppStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Dock Panels
        self._init_dock_panels()

        # Toolbar
        self.toolbar = NppToolBar(self, is_dark=self.config.get("dark_mode", False), parent=self)
        self.addToolBar(self.toolbar)

        # Menu Bar
        self._build_menu_bar()

        # Connect signals
        self.tab_manager.active_editor_changed.connect(self._on_active_editor_changed)
        self.status_bar.eol_change_requested.connect(self._on_status_bar_eol_change)
        self.status_bar.encoding_change_requested.connect(self._on_status_bar_encoding_change)

        # Dialogs
        self.find_dialog = FindReplaceDialog(self)
        self.find_dialog.find_in_files_results.connect(self.dock_search_results.set_results)

        # Apply initial theme and style
        self.apply_theme(
            self.config.get("theme", "Classic Default"),
            self.config.get("dark_mode", False),
            self.config.get("font_family", "Monospace"),
            self.config.get("font_size", 11),
            self.config.get("tab_size", 4)
        )

        # Open initial files or restore session
        if files_to_open:
            for f in files_to_open:
                if os.path.exists(f):
                    self.open_file(f)
        else:
            self._restore_session()

        # Ensure at least one tab exists
        if len(self.tab_manager.all_editors()) == 0:
            self.file_new()

        if initial_line and self.tab_manager.active_editor():
            self.tab_manager.active_editor().go_to_line(initial_line)

    def _init_dock_panels(self):
        # 1. Document Map
        self.dock_doc_map = DocumentMapDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_doc_map)
        self.dock_doc_map.hide()

        # 2. Function List
        self.dock_func_list = FunctionListDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_func_list)
        self.dock_func_list.hide()

        # 3. File Browser
        self.dock_file_browser = FileBrowserDock(os.getcwd(), self)
        self.dock_file_browser.file_open_requested.connect(self.open_file)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_file_browser)
        self.dock_file_browser.hide()

        # 4. Search Results
        self.dock_search_results = SearchResultsDock(self)
        self.dock_search_results.result_selected.connect(self._on_search_result_selected)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_search_results)
        self.dock_search_results.hide()

    def _build_menu_bar(self):
        menubar = self.menuBar()

        # 1. Dosya (File)
        m_file = menubar.addMenu("&Dosya")
        self._add_action(m_file, "&Yeni", "Ctrl+N", self.file_new)
        self._add_action(m_file, "&Aç...", "Ctrl+O", self.file_open)
        self._add_action(m_file, "Dosya Konumunu Aç", "", self.file_open_containing_folder)
        m_file.addSeparator()
        self._add_action(m_file, "&Kaydet", "Ctrl+S", self.file_save)
        self._add_action(m_file, "Farklı &Kaydet...", "Ctrl+Alt+S", self.file_save_as)
        self._add_action(m_file, "&Tümünü Kaydet", "Ctrl+Shift+S", self.file_save_all)
        m_file.addSeparator()
        self._add_action(m_file, "K&apat", "Ctrl+W", self.file_close)
        self._add_action(m_file, "Tümünü Kapat", "Ctrl+Shift+W", self.file_close_all)
        m_file.addSeparator()
        self._add_action(m_file, "&Yazdır...", "Ctrl+P", self.file_print)
        m_file.addSeparator()
        self._add_action(m_file, "&Çıkış", "Ctrl+Q", self.close)

        # 2. Düzen (Edit)
        m_edit = menubar.addMenu("Dü&zen")
        self._add_action(m_edit, "&Geri Al", "Ctrl+Z", self.edit_undo)
        self._add_action(m_edit, "&Yinele", "Ctrl+Y", self.edit_redo)
        m_edit.addSeparator()
        self._add_action(m_edit, "Ke&s", "Ctrl+X", self.edit_cut)
        self._add_action(m_edit, "&Kopyala", "Ctrl+C", self.edit_copy)
        self._add_action(m_edit, "&Yapıştır", "Ctrl+V", self.edit_paste)
        self._add_action(m_edit, "&Sil", "Del", self.edit_delete)
        self._add_action(m_edit, "&Tümünü Seç", "Ctrl+A", self.edit_select_all)
        m_edit.addSeparator()

        # Submenu: Satır İşlemleri
        m_line_ops = m_edit.addMenu("Satır İşlemleri")
        self._add_action(m_line_ops, "Satırı Çoğalt", "Ctrl+D", self.edit_duplicate_line)
        self._add_action(m_line_ops, "Satırı Yukarı Taşı", "Ctrl+Shift+Up", self.edit_move_line_up)
        self._add_action(m_line_ops, "Satırı Aşağı Taşı", "Ctrl+Shift+Down", self.edit_move_line_down)
        self._add_action(m_line_ops, "Geçerli Satırı Sil", "Ctrl+Shift+L", self.edit_delete_line)
        self._add_action(m_line_ops, "Satırları Sırala (A-Z)", "", self.edit_sort_lines)

        # Submenu: Harf İşlemleri
        m_case = m_edit.addMenu("Harfleri Çevir")
        self._add_action(m_case, "BÜYÜK HARF", "Ctrl+Shift+U", self.edit_case_upper)
        self._add_action(m_case, "küçük harf", "Ctrl+U", self.edit_case_lower)
        self._add_action(m_case, "Başlık Düzeni (Title Case)", "", self.edit_case_title)

        # Submenu: Boşluk İşlemleri
        m_blank = m_edit.addMenu("Boşluk İşlemleri")
        self._add_action(m_blank, "Sondaki Boşlukları Temizle", "", self.edit_trim_trailing)

        self._add_action(m_edit, "Yorum Ekle/Kaldır", "Ctrl+K", self.edit_toggle_comment)
        self._add_action(m_edit, "Satıra Git...", "Ctrl+G", self.search_goto_line)

        # 3. Ara (Search)
        m_search = menubar.addMenu("&Ara")
        self._add_action(m_search, "&Bul...", "Ctrl+F", self.search_find)
        self._add_action(m_search, "&Sonrakini Bul", "F3", self.search_find_next)
        self._add_action(m_search, "&Öncekini Bul", "Shift+F3", self.search_find_prev)
        self._add_action(m_search, "&Değiştir...", "Ctrl+H", self.search_replace)
        self._add_action(m_search, "Dosyalarda Bul...", "Ctrl+Shift+F", self.search_find_in_files)
        self._add_action(m_search, "İşaretle...", "", self.search_mark)
        m_search.addSeparator()

        # Submenu: Yer İmleri
        m_bm = m_search.addMenu("Yer İmleri (Bookmarks)")
        self._add_action(m_bm, "Yer İmi Ekle/Kaldır", "Ctrl+F2", self.bookmark_toggle)
        self._add_action(m_bm, "Sonraki Yer İmi", "F2", self.bookmark_next)
        self._add_action(m_bm, "Önceki Yer İmi", "Shift+F2", self.bookmark_prev)
        self._add_action(m_bm, "Tüm Yer İmlerini Temizle", "", self.bookmark_clear_all)

        # 4. Görünüm (View)
        m_view = menubar.addMenu("&Görünüm")
        self.act_always_top = self._add_action(m_view, "Her Zaman Üstte", "", self.toggle_always_on_top, checkable=True)
        self.act_fullscreen = self._add_action(m_view, "Tam Ekran", "F11", self.toggle_fullscreen, checkable=True)
        m_view.addSeparator()
        self._add_action(m_view, "Yakınlaştır", "Ctrl++", self.view_zoom_in)
        self._add_action(m_view, "Uzaklaştır", "Ctrl+-", self.view_zoom_out)
        self._add_action(m_view, "Varsayılan Yakınlaştırma", "Ctrl+0", self.view_zoom_reset)
        m_view.addSeparator()
        self.act_wrap = self._add_action(m_view, "Sözcük Kaydır (Word Wrap)", "", self.toggle_word_wrap, checkable=True)
        self.act_chars = self._add_action(m_view, "Tüm Karakterleri Göster", "", self.toggle_whitespaces, checkable=True)
        self.act_eol = self._add_action(m_view, "Satır Sonunu Göster (EOL)", "", self.toggle_eol, checkable=True)
        self.act_indent = self._add_action(m_view, "Girinti Kılavuzunu Göster", "", self.toggle_indent_guides, checkable=True)
        self.act_indent.setChecked(True)
        m_view.addSeparator()
        self._add_action(m_view, "Belge Haritası (Minimap)", "", self.toggle_document_map)
        self._add_action(m_view, "Fonksiyon Listesi", "", self.toggle_function_list)
        self._add_action(m_view, "Çalışma Alanı Dosya Tarayıcısı", "", self.toggle_file_browser)

        # 5. Kodlama (Encoding)
        m_enc = menubar.addMenu("&Kodlama")
        for name, _ in ENCODINGS[:10]:
            self._add_action(m_enc, name, "", lambda checked, n=name: self._set_encoding(n))
        m_enc.addSeparator()
        self._add_action(m_enc, "Satır Sonunu Dönüştür -> Windows (CR LF)", "", lambda: self._set_eol(EOL_WINDOWS))
        self._add_action(m_enc, "Satır Sonunu Dönüştür -> Unix (LF)", "", lambda: self._set_eol(EOL_UNIX))
        self._add_action(m_enc, "Satır Sonunu Dönüştür -> Mac (CR)", "", lambda: self._set_eol(EOL_MAC))

        # 6. Diller (Language)
        m_lang = menubar.addMenu("&Diller")
        popular_langs = [
            "Plain Text", "Python", "C", "C++", "C#", "Java", "JavaScript", "TypeScript",
            "HTML", "XML", "CSS", "JSON", "YAML", "Bash/Shell", "SQL", "Rust", "Go",
            "PHP", "Ruby", "Markdown", "INI Config", "Diff", "Batch"
        ]
        for plang in popular_langs:
            self._add_action(m_lang, plang, "", lambda checked, l=plang: self._set_language(l))

        # 7. Ayarlar (Settings)
        m_settings = menubar.addMenu("&Ayarlar")
        self._add_action(m_settings, "Stil Yapılandırıcı (Style Configurator)...", "", self.open_style_configurator)
        self.act_dark_mode = self._add_action(m_settings, "Karanlık Mod (Dark Mode)", "", self.toggle_dark_mode, checkable=True)
        self.act_dark_mode.setChecked(self.config.get("dark_mode", False))

        # 8. Makrolar (Macro)
        m_macro = menubar.addMenu("&Makrolar")
        self._add_action(m_macro, "Kaydı Başlat", "Ctrl+Shift+R", self.macro_start)
        self._add_action(m_macro, "Kaydı Durdur", "Ctrl+Shift+S", self.macro_stop)
        self._add_action(m_macro, "Oynat", "Ctrl+Shift+P", self.macro_playback)
        self._add_action(m_macro, "Çok Kez Çalıştır...", "", self.macro_run_multiple)

        # 9. Çalıştır (Run)
        m_run = menubar.addMenu("&Çalıştır")
        self._add_action(m_run, "Dosyayı Çalıştır (Run Script)", "F5", self.run_current_file)
        self._add_action(m_run, "Varsayılan Tarayıcıda Aç", "", self.run_in_browser)

        # 10. Hakkında (Help)
        m_help = menubar.addMenu("&Hakkında")
        self._add_action(m_help, "Notepad++ Hakkında...", "", self.open_about)

    def _add_action(self, menu: QMenu, title: str, shortcut: str, slot, checkable: bool = False) -> QAction:
        act = QAction(title, self)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut))
        if checkable:
            act.setCheckable(True)
        act.triggered.connect(slot)
        menu.addAction(act)
        return act

    # -------------------------------------------------------------------------
    # Document / Editor Lifecycle
    # -------------------------------------------------------------------------

    def file_new(self):
        doc = Document()
        editor = self.tab_manager.add_document(doc)
        editor.apply_theme(self.current_theme_colors)
        return editor

    def file_open(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Dosya Aç (Open File)", os.getcwd(), "Tüm Dosyalar (*.*)")
        for p in paths:
            self.open_file(p)

    def open_file(self, file_path: str):
        # Check if already open
        for ed in self.tab_manager.all_editors():
            if ed.document_model.file_path == file_path:
                # Switch to it
                idx = self.tab_manager.primary_view.indexOf(ed)
                if idx != -1:
                    self.tab_manager.primary_view.setCurrentIndex(idx)
                return ed

        doc = Document(file_path)
        editor = self.tab_manager.add_document(doc)
        editor.apply_theme(self.current_theme_colors)
        return editor

    def file_save(self):
        ed = self.tab_manager.active_editor()
        if not ed: return
        doc = ed.document_model
        if not doc.file_path:
            self.file_save_as()
        else:
            doc.save(ed.toPlainText())

    def file_save_as(self):
        ed = self.tab_manager.active_editor()
        if not ed: return
        path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", os.getcwd(), "Tüm Dosyalar (*.*)")
        if path:
            ed.document_model.save(ed.toPlainText(), target_path=path)

    def file_save_all(self):
        for ed in self.tab_manager.all_editors():
            if ed.document_model.is_modified:
                if not ed.document_model.file_path:
                    path, _ = QFileDialog.getSaveFileName(self, f"{ed.document_model.title} Farklı Kaydet", os.getcwd())
                    if path:
                        ed.document_model.save(ed.toPlainText(), target_path=path)
                else:
                    ed.document_model.save(ed.toPlainText())

    def file_close(self):
        tw = self.tab_manager._active_tab_widget
        cur_idx = tw.currentIndex()
        if cur_idx != -1:
            tw.close_tab(cur_idx)

    def file_close_all(self):
        for tw in [self.tab_manager.primary_view, self.tab_manager.secondary_view]:
            for i in range(tw.count() - 1, -1, -1):
                tw.close_tab(i)

    def file_open_containing_folder(self):
        ed = self.tab_manager.active_editor()
        if ed and ed.document_model.file_path:
            folder = os.path.dirname(ed.document_model.file_path)
            subprocess.Popen(["xdg-open", folder])

    def file_print(self):
        ed = self.tab_manager.active_editor()
        if not ed: return
        from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
        printer = QPrinter()
        dlg = QPrintDialog(printer, self)
        if dlg.exec_() == QPrintDialog.Accepted:
            ed.print_(printer)

    # -------------------------------------------------------------------------
    # Active Editor Signal Routing & Status Bar Updates
    # -------------------------------------------------------------------------

    def _on_active_editor_changed(self, editor: Optional[NppEditor]):
        if not editor:
            self.dock_doc_map.set_active_editor(None)
            self.dock_func_list.set_active_editor(None)
            return

        doc = editor.document_model
        self.setWindowTitle(f"{doc.title} - Notepad++")

        # Update dock panels
        self.dock_doc_map.set_active_editor(editor)
        self.dock_func_list.set_active_editor(editor)

        # Update status bar
        cursor = editor.textCursor()
        self.status_bar.update_position(cursor.blockNumber() + 1, cursor.positionInBlock() + 1, cursor.position())
        self.status_bar.update_length(len(editor.toPlainText()), editor.blockCount())
        self.status_bar.update_eol(doc.eol)
        self.status_bar.update_encoding(doc.encoding)
        self.status_bar.update_language(doc.language)
        self.status_bar.update_mode(editor.overwriteMode())

        # Connect editor signals to status bar
        editor.cursor_position_changed.connect(
            lambda line, col, pos: self.status_bar.update_position(line, col, pos, len(editor.textCursor().selectedText()))
        )
        editor.lines_count_changed.connect(self.status_bar.update_length)
        doc.eol_changed.connect(self.status_bar.update_eol)
        doc.encoding_changed.connect(self.status_bar.update_encoding)
        doc.language_changed.connect(self.status_bar.update_language)

    def _on_status_bar_eol_change(self, eol: str):
        self._set_eol(eol)

    def _on_status_bar_encoding_change(self, enc: str):
        self._set_encoding(enc)

    def _set_eol(self, eol: str):
        ed = self.tab_manager.active_editor()
        if ed:
            ed.document_model.set_eol(eol)
            ed.document_model.is_modified = True

    def _set_encoding(self, enc: str):
        ed = self.tab_manager.active_editor()
        if ed:
            ed.document_model.set_encoding(enc)
            ed.document_model.is_modified = True

    def _set_language(self, lang: str):
        ed = self.tab_manager.active_editor()
        if ed:
            ed.document_model.set_language(lang)

    # -------------------------------------------------------------------------
    # Edit Commands
    # -------------------------------------------------------------------------

    def edit_undo(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.undo()

    def edit_redo(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.redo()

    def edit_cut(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.cut()

    def edit_copy(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.copy()

    def edit_paste(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.paste()

    def edit_delete(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.textCursor().removeSelectedText()

    def edit_select_all(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.selectAll()

    def edit_duplicate_line(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.duplicate_current_line()

    def edit_move_line_up(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.move_line_up()

    def edit_move_line_down(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.move_line_down()

    def edit_delete_line(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.delete_current_line()

    def edit_toggle_comment(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.toggle_comment()

    def edit_case_upper(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.convert_case_upper()

    def edit_case_lower(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.convert_case_lower()

    def edit_case_title(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.convert_case_title()

    def edit_trim_trailing(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.trim_trailing_spaces()

    def edit_sort_lines(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.sort_lines_ascending()

    # -------------------------------------------------------------------------
    # Search / Bookmarks Commands
    # -------------------------------------------------------------------------

    def search_find(self):
        self.find_dialog.show_tab(0)

    def search_find_next(self):
        self.find_dialog.find_next()

    def search_find_prev(self):
        self.find_dialog.find_prev()

    def search_replace(self):
        self.find_dialog.show_tab(1)

    def search_find_in_files(self):
        self.find_dialog.show_tab(2)

    def search_mark(self):
        self.find_dialog.show_tab(3)

    def search_goto_line(self):
        ed = self.tab_manager.active_editor()
        if ed:
            dlg = GoToLineDialog(ed, self)
            dlg.exec_()

    def bookmark_toggle(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.toggle_bookmark()

    def bookmark_next(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.next_bookmark()

    def bookmark_prev(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.prev_bookmark()

    def bookmark_clear_all(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.clear_all_bookmarks()

    def _on_search_result_selected(self, file_path: str, line_num: int):
        ed = self.open_file(file_path)
        if ed:
            ed.go_to_line(line_num)

    # -------------------------------------------------------------------------
    # View Toggles & Zoom
    # -------------------------------------------------------------------------

    def view_zoom_in(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.set_zoom(1)

    def view_zoom_out(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.set_zoom(-1)

    def view_zoom_reset(self):
        ed = self.tab_manager.active_editor()
        if ed: ed.set_zoom(0)

    def toggle_word_wrap(self, checked: bool):
        for ed in self.tab_manager.all_editors():
            ed.setLineWrapMode(NppEditor.WidgetWidth if checked else NppEditor.NoWrap)

    def toggle_whitespaces(self, checked: bool):
        for ed in self.tab_manager.all_editors():
            ed.show_whitespaces = checked
            ed.viewport().update()

    def toggle_eol(self, checked: bool):
        for ed in self.tab_manager.all_editors():
            ed.show_eol = checked
            ed.viewport().update()

    def toggle_indent_guides(self, checked: bool):
        for ed in self.tab_manager.all_editors():
            ed.show_indent_guides = checked
            ed.viewport().update()

    def toggle_always_on_top(self, checked: bool):
        flags = self.windowFlags()
        if checked:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        self.show()

    def toggle_fullscreen(self, checked: bool):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_document_map(self):
        self.dock_doc_map.setVisible(not self.dock_doc_map.isVisible())

    def toggle_function_list(self):
        self.dock_func_list.setVisible(not self.dock_func_list.isVisible())

    def toggle_file_browser(self):
        self.dock_file_browser.setVisible(not self.dock_file_browser.isVisible())

    # -------------------------------------------------------------------------
    # Theming & Styles
    # -------------------------------------------------------------------------

    def apply_theme(self, theme_name: str, is_dark: bool, font_family: str, font_size: int, tab_size: int):
        self.current_theme_colors = dict(THEME_PRESETS.get(theme_name, THEME_PRESETS["Classic Default"]))
        self.config["theme"] = theme_name
        self.config["dark_mode"] = is_dark
        self.config["font_family"] = font_family
        self.config["font_size"] = font_size
        self.config["tab_size"] = tab_size

        # Apply QSS
        qss = get_app_stylesheet(is_dark)
        app_inst = QApplication.instance()
        if app_inst:
            app_inst.setStyleSheet(qss)

        # Update toolbar icons
        self.toolbar.update_icons(is_dark)

        # Update all editors
        for ed in self.tab_manager.all_editors():
            ed.base_font_size = font_size
            ed.tab_size = tab_size
            f = ed.font()
            f.setFamily(font_family)
            f.setPointSize(font_size)
            ed.setFont(f)
            ed.apply_theme(self.current_theme_colors)

        save_config(self.config)

    def open_style_configurator(self):
        dlg = StyleConfiguratorDialog(
            current_theme=self.config.get("theme", "Classic Default"),
            is_dark=self.config.get("dark_mode", False),
            font_family=self.config.get("font_family", "Monospace"),
            font_size=self.config.get("font_size", 11),
            tab_size=self.config.get("tab_size", 4),
            parent=self
        )
        dlg.theme_changed.connect(self.apply_theme)
        dlg.exec_()

    def toggle_dark_mode(self, checked: bool):
        theme_name = "DarkModeDefault" if checked else "Classic Default"
        self.apply_theme(
            theme_name, checked,
            self.config.get("font_family", "Monospace"),
            self.config.get("font_size", 11),
            self.config.get("tab_size", 4)
        )

    # -------------------------------------------------------------------------
    # Macro Engine
    # -------------------------------------------------------------------------

    def macro_start(self):
        self.macro_manager.start_recording()
        self.statusBar().showMessage("Makro kaydı başlatıldı...", 3000)

    def macro_stop(self):
        self.macro_manager.stop_recording()
        self.statusBar().showMessage("Makro kaydı durduruldu.", 3000)

    def macro_playback(self):
        ed = self.tab_manager.active_editor()
        if ed:
            self.macro_manager.play_macro(ed)

    def macro_run_multiple(self):
        ed = self.tab_manager.active_editor()
        if not ed: return
        count, ok = QInputDialog.getInt(self, "Makroyu Çok Kez Çalıştır", "Çalıştırma sayısı:", 10, 1, 10000)
        if ok:
            self.macro_manager.play_macro_n_times(ed, count)

    # -------------------------------------------------------------------------
    # External Run / Script Execution
    # -------------------------------------------------------------------------

    def run_current_file(self):
        ed = self.tab_manager.active_editor()
        if not ed or not ed.document_model.file_path:
            QMessageBox.warning(self, "Çalıştır", "Önce dosyayı kaydediniz.")
            return

        fpath = ed.document_model.file_path
        ext = os.path.splitext(fpath)[1].lower()
        if ext == ".py":
            cmd = f'python3 "{fpath}"'
        elif ext in (".sh", ".bash"):
            cmd = f'bash "{fpath}"'
        else:
            cmd = f'xdg-open "{fpath}"'

        try:
            # Launch in external terminal if possible or background process
            subprocess.Popen(["x-terminal-emulator", "-e", f"bash -c '{cmd}; echo -e \"\\n[Program bitti. Kapatmak için Enter a basın]\"; read'"] )
        except Exception:
            try:
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"{cmd}; read"])
            except Exception as e:
                QMessageBox.information(self, "Çalıştır", f"Komut çalıştırıldı: {cmd}")

    def run_in_browser(self):
        ed = self.tab_manager.active_editor()
        if ed and ed.document_model.file_path:
            subprocess.Popen(["xdg-open", ed.document_model.file_path])

    def open_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    # -------------------------------------------------------------------------
    # Drag & Drop Support
    # -------------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            fpath = url.toLocalFile()
            if os.path.isfile(fpath):
                self.open_file(fpath)

    # -------------------------------------------------------------------------
    # Session Persistence
    # -------------------------------------------------------------------------

    def _restore_session(self):
        sess = load_session()
        files = sess.get("files", [])
        for item in files:
            p = item.get("path")
            if p and os.path.exists(p):
                ed = self.open_file(p)
                if ed:
                    ed.document_model.set_encoding(item.get("encoding", "UTF-8"))
                    ed.document_model.set_eol(item.get("eol", EOL_UNIX))
                    ed.go_to_line(item.get("line", 1))

    def closeEvent(self, event):
        # Save session
        files_state = []
        for ed in self.tab_manager.all_editors():
            doc = ed.document_model
            if doc.file_path:
                files_state.append({
                    "path": doc.file_path,
                    "line": ed.textCursor().blockNumber() + 1,
                    "encoding": doc.encoding,
                    "eol": doc.eol
                })
        save_session(files_state, self.tab_manager.primary_view.currentIndex())
        save_config(self.config)

        # Check unsaved changes
        for ed in self.tab_manager.all_editors():
            if ed.document_model.is_modified:
                res = QMessageBox.question(
                    self,
                    "Çıkış (Exit)",
                    f"'{ed.document_model.title}' üzerinde kaydedilmemiş değişiklikler var. Çıkmak istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if res == QMessageBox.No:
                    event.ignore()
                    return
        event.accept()
