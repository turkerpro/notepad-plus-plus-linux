"""
Notepad++ Go to Line / Offset Dialog (Ctrl+G).
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QGroupBox
)
from PyQt5.QtCore import Qt


class GoToLineDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Satıra Git (Go to Line)")
        self.resize(320, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        cur_line = editor.textCursor().blockNumber() + 1
        max_lines = editor.blockCount()

        info_box = QGroupBox("Konum (Position)")
        info_layout = QVBoxLayout(info_box)
        self.lbl_curr = QLabel(f"Geçerli satır: {cur_line}")
        self.lbl_target = QLabel(f"Hedef satır (1 - {max_lines}):")
        self.txt_target = QLineEdit(str(cur_line))
        self.txt_target.selectAll()

        info_layout.addWidget(self.lbl_curr)
        info_layout.addWidget(self.lbl_target)
        info_layout.addWidget(self.txt_target)
        layout.addWidget(info_box)

        btn_layout = QHBoxLayout()
        btn_go = QPushButton("Git (Go)")
        btn_cancel = QPushButton("İptal (Cancel)")
        btn_go.setDefault(True)

        btn_go.clicked.connect(self._go)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_go)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _go(self):
        try:
            val = int(self.txt_target.text().strip())
            self.editor.go_to_line(val)
            self.accept()
        except ValueError:
            pass
