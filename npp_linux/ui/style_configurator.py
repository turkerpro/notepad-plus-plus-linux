"""
Notepad++ Style Configurator (Theme, Font, and Display Preferences).
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QSpinBox, QCheckBox, QPushButton, QGroupBox, QFontComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ..styles.themes import THEME_PRESETS


class StyleConfiguratorDialog(QDialog):
    """Notepad++ Style and Theme Configurator."""

    theme_changed = pyqtSignal(str, bool, str, int, int)  # theme_name, is_dark, font_family, font_size, tab_size

    def __init__(self, current_theme: str = "Classic Default", is_dark: bool = False,
                 font_family: str = "Monospace", font_size: int = 11, tab_size: int = 4, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stil Yapılandırıcı (Style Configurator)")
        self.resize(480, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # Theme selection
        box_theme = QGroupBox("Tema Seçimi (Select Theme)")
        layout_theme = QGridLayout(box_theme)

        layout_theme.addWidget(QLabel("Tema (Theme):"), 0, 0)
        self.cmb_theme = QComboBox()
        for tname in THEME_PRESETS.keys():
            self.cmb_theme.addItem(tname)
        self.cmb_theme.setCurrentText(current_theme)
        layout_theme.addWidget(self.cmb_theme, 0, 1)

        self.chk_dark_ui = QCheckBox("Karanlık Mod Arayüzü (Dark Mode UI)")
        self.chk_dark_ui.setChecked(is_dark)
        layout_theme.addWidget(self.chk_dark_ui, 1, 0, 1, 2)
        layout.addWidget(box_theme)

        # Font & Display settings
        box_font = QGroupBox("Yazı Tipi ve Boyutu (Font Style)")
        layout_font = QGridLayout(box_font)

        layout_font.addWidget(QLabel("Yazı Tipi (Font Name):"), 0, 0)
        self.cmb_font = QFontComboBox()
        self.cmb_font.setFontFilters(QFontComboBox.MonospacedFonts)
        self.cmb_font.setCurrentFont(QFont(font_family))
        layout_font.addWidget(self.cmb_font, 0, 1)

        layout_font.addWidget(QLabel("Yazı Boyutu (Font Size):"), 1, 0)
        self.spn_size = QSpinBox()
        self.spn_size.setRange(6, 36)
        self.spn_size.setValue(font_size)
        layout_font.addWidget(self.spn_size, 1, 1)

        layout_font.addWidget(QLabel("Sekme Boyutu (Tab Size):"), 2, 0)
        self.spn_tab = QSpinBox()
        self.spn_tab.setRange(1, 16)
        self.spn_tab.setValue(tab_size)
        layout_font.addWidget(self.spn_tab, 2, 1)

        layout.addWidget(box_font)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Kaydet ve Kapat (Save & Close)")
        btn_apply = QPushButton("Uygula (Apply)")
        btn_cancel = QPushButton("İptal (Cancel)")

        btn_save.clicked.connect(self._save_and_close)
        btn_apply.clicked.connect(self._apply)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _apply(self):
        theme_name = self.cmb_theme.currentText()
        is_dark = self.chk_dark_ui.isChecked()
        font_family = self.cmb_font.currentFont().family()
        font_size = self.spn_size.value()
        tab_size = self.spn_tab.value()
        self.theme_changed.emit(theme_name, is_dark, font_family, font_size, tab_size)

    def _save_and_close(self):
        self._apply()
        self.accept()
