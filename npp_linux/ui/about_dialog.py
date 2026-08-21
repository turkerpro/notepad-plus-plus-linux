"""
About Dialog for Notepad++ Linux.
"""
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notepad++ Hakkında (About Notepad++)")
        self.resize(460, 240)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QHBoxLayout(self)

        # Chameleon Icon
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "resources", "icons", "npp.ico")
        lbl_icon = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_icon.setPixmap(pixmap)
        lbl_icon.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        layout.addWidget(lbl_icon, 1)

        # Text Info
        right_layout = QVBoxLayout()

        lbl_title = QLabel("Notepad++ for Linux")
        font_title = QFont()
        font_title.setPointSize(16)
        font_title.setBold(True)
        lbl_title.setFont(font_title)
        right_layout.addWidget(lbl_title)

        lbl_version = QLabel("Sürüm / Version 8.9.7 (64-bit Linux Native)\nQt5 / Python GUI Engine")
        lbl_version.setStyleSheet("color: #666666; font-size: 11px;")
        right_layout.addWidget(lbl_version)

        lbl_desc = QLabel(
            "Notepad++ is a free (as in 'free speech' and also as in 'free beer') "
            "source code editor for Linux.\n\n"
            "Orijinal Notepad++ Don HO <don.h@free.fr> tarafından geliştirilmiştir.\n"
            "Lisans: GNU General Public License v3"
        )
        lbl_desc.setWordWrap(True)
        right_layout.addWidget(lbl_desc)

        right_layout.addStretch()
        btn_ok = QPushButton("Tamam (OK)")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)
        right_layout.addWidget(btn_ok, 0, Qt.AlignRight)

        layout.addLayout(right_layout, 3)
