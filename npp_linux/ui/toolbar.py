"""
Notepad++ Iconic Toolbar component.
"""
import os
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QToolBar, QAction, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, pyqtSignal


def get_icon(icon_name: str, is_dark: bool = False) -> QIcon:
    """Load authentic icon from Notepad++ resource directory."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    res_icons = os.path.join(base_dir, "resources", "icons")

    # Mapping of logical names to dark & standard filenames
    dark_map = {
        "new": "new_off.ico", "open": "open_off.ico", "save": "save_off.ico", "save_all": "saveall_off.ico",
        "close": "close_off.ico", "close_all": "closeall_off.ico", "print": "print_off.ico",
        "cut": "cut_off.ico", "copy": "copy_off.ico", "paste": "paste_off.ico",
        "undo": "undo_off.ico", "redo": "redo_off.ico",
        "find": "find_off.ico", "replace": "findrep_off.ico",
        "zoom_in": "zoomIn_off.ico", "zoom_out": "zoomOut_off.ico",
        "sync_v": "syncV_off.ico", "sync_h": "syncH_off.ico",
        "wrap": "wrap_off.ico", "all_chars": "allChars_off.ico", "indent_guide": "indentGuide_off.ico",
        "doc_map": "docMap_off.ico", "doc_list": "docList_off.ico", "func_list": "funcList_off.ico",
        "file_browser": "fileBrowser_off.ico",
        "macro_start": "startrecord_off.ico", "macro_stop": "stoprecord_off.ico",
        "macro_play": "playrecord_off.ico", "macro_multi": "playrecord_m_off.ico",
    }

    std_map = {
        "new": "newFile.bmp", "open": "openFile.bmp", "save": "saveFile.bmp", "save_all": "saveAll.bmp",
        "close": "closeFile.bmp", "close_all": "closeAll.bmp", "print": "print.bmp",
        "cut": "cut.bmp", "copy": "copy.bmp", "paste": "paste.bmp",
        "undo": "undo.bmp", "redo": "redo.bmp",
        "find": "find.bmp", "replace": "findReplace.bmp",
        "zoom_in": "zoomIn.bmp", "zoom_out": "zoomOut.bmp",
        "sync_v": "syncV.bmp", "sync_h": "syncH.bmp",
        "wrap": "wrap.bmp", "all_chars": "allChars.bmp", "indent_guide": "indentGuide.bmp",
        "doc_map": "docMap.bmp", "doc_list": "docList.bmp", "func_list": "funcList.bmp",
        "file_browser": "fileBrowser.bmp",
        "macro_start": "startRecord.bmp", "macro_stop": "stopRecord.bmp",
        "macro_play": "playRecord.bmp", "macro_multi": "playRecord_m.bmp",
    }

    if is_dark:
        path = os.path.join(res_icons, "dark", "toolbar", "filled", dark_map.get(icon_name, ""))
        if os.path.exists(path):
            return QIcon(path)

    # Fallback to standard
    std_path = os.path.join(res_icons, "standard", "toolbar", std_map.get(icon_name, ""))
    if os.path.exists(std_path):
        return QIcon(std_path)

    # Fallback to dark regular or filled
    dark_path = os.path.join(res_icons, "dark", "toolbar", "filled", dark_map.get(icon_name, ""))
    if os.path.exists(dark_path):
        return QIcon(dark_path)

    return QIcon()


class NppToolBar(QToolBar):
    """Notepad++ Main Toolbar with full toolset."""

    def __init__(self, main_window, is_dark: bool = False, parent=None):
        super().__init__("Notepad++ Toolbar", parent)
        self.main_window = main_window
        self.is_dark = is_dark
        self.setIconSize(QSize(18, 18))
        self.setMovable(True)
        self.setFloatable(False)
        self._build_actions()

    def update_icons(self, is_dark: bool):
        self.is_dark = is_dark
        # Refresh all action icons
        for name, act in self.action_map.items():
            act.setIcon(get_icon(name, is_dark))

    def _build_actions(self):
        mw = self.main_window
        self.action_map: Dict[str, QAction] = {}

        def add_btn(name: str, tooltip: str, shortcut: str, trigger_fn, is_check: bool = False) -> QAction:
            icon = get_icon(name, self.is_dark)
            act = QAction(icon, tooltip, self)
            if shortcut:
                act.setShortcut(shortcut)
            act.setToolTip(f"{tooltip} ({shortcut})" if shortcut else tooltip)
            if is_check:
                act.setCheckable(True)
            act.triggered.connect(trigger_fn)
            self.addAction(act)
            self.action_map[name] = act
            return act

        # File actions
        add_btn("new", "Yeni (New)", "Ctrl+N", mw.file_new)
        add_btn("open", "Aç (Open)", "Ctrl+O", mw.file_open)
        add_btn("save", "Kaydet (Save)", "Ctrl+S", mw.file_save)
        add_btn("save_all", "Tümünü Kaydet (Save All)", "Ctrl+Shift+S", mw.file_save_all)
        add_btn("close", "Kapat (Close)", "Ctrl+W", mw.file_close)
        add_btn("close_all", "Tümünü Kapat (Close All)", "Ctrl+Shift+W", mw.file_close_all)
        add_btn("print", "Yazdır (Print)", "Ctrl+P", mw.file_print)

        self.addSeparator()

        # Edit actions
        add_btn("cut", "Kes (Cut)", "Ctrl+X", mw.edit_cut)
        add_btn("copy", "Kopyala (Copy)", "Ctrl+C", mw.edit_copy)
        add_btn("paste", "Yapıştır (Paste)", "Ctrl+V", mw.edit_paste)

        self.addSeparator()

        # History actions
        add_btn("undo", "Geri Al (Undo)", "Ctrl+Z", mw.edit_undo)
        add_btn("redo", "Yinele (Redo)", "Ctrl+Y", mw.edit_redo)

        self.addSeparator()

        # Search actions
        add_btn("find", "Bul (Find)", "Ctrl+F", mw.search_find)
        add_btn("replace", "Değiştir (Replace)", "Ctrl+H", mw.search_replace)

        self.addSeparator()

        # Zoom actions
        add_btn("zoom_in", "Yakınlaştır (Zoom In)", "Ctrl++", mw.view_zoom_in)
        add_btn("zoom_out", "Uzaklaştır (Zoom Out)", "Ctrl+-", mw.view_zoom_out)

        self.addSeparator()

        # View actions
        add_btn("wrap", "Sözcük Kaydır (Word Wrap)", "", mw.toggle_word_wrap, is_check=True)
        add_btn("all_chars", "Tüm Karakterleri Göster (Show All Characters)", "", mw.toggle_whitespaces, is_check=True)
        add_btn("indent_guide", "Girinti Kılavuzunu Göster (Indent Guide)", "", mw.toggle_indent_guides, is_check=True)

        self.addSeparator()

        # Dock panels
        add_btn("doc_map", "Belge Haritası (Document Map)", "", mw.toggle_document_map, is_check=True)
        add_btn("func_list", "Fonksiyon Listesi (Function List)", "", mw.toggle_function_list, is_check=True)
        add_btn("file_browser", "Çalışma Alanı Dosya Tarayıcısı (Folder as Workspace)", "", mw.toggle_file_browser, is_check=True)

        self.addSeparator()

        # Macro actions
        add_btn("macro_start", "Kaydı Başlat (Start Recording)", "Ctrl+Shift+R", mw.macro_start)
        add_btn("macro_stop", "Kaydı Durdur (Stop Recording)", "Ctrl+Shift+S", mw.macro_stop)
        add_btn("macro_play", "Kaydı Oynat (Playback)", "Ctrl+Shift+P", mw.macro_playback)
        add_btn("macro_multi", "Makroyu Çok Kez Çalıştır (Run Macro Multiple Times)", "", mw.macro_run_multiple)
