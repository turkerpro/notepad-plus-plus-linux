"""
Unit tests for Find and Replace logic.
"""
import unittest
from PyQt5.QtWidgets import QApplication
from npp_linux.core.document import Document
from npp_linux.core.editor import NppEditor
from npp_linux.ui.main_window import NppMainWindow

app = QApplication.instance() or QApplication([])


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.main_window = NppMainWindow()
        self.editor = self.main_window.tab_manager.active_editor()
        self.editor.setPlainText("First line with apple\nSecond line with banana\nThird line with apple and orange")

    def test_find_and_replace_all(self):
        dlg = self.main_window.find_dialog
        dlg.txt_replace_find.setText("apple")
        dlg.txt_replace_with.setText("peach")
        dlg.replace_all()

        text = self.editor.toPlainText()
        self.assertNotIn("apple", text)
        self.assertIn("peach", text)
        self.assertEqual(text.count("peach"), 2)


if __name__ == "__main__":
    unittest.main()
