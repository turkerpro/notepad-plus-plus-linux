"""
Unit tests for NppEditor and Document Model.
"""
import unittest
from PyQt5.QtWidgets import QApplication
from npp_linux.core.document import Document
from npp_linux.core.editor import NppEditor

app = QApplication.instance() or QApplication([])


class TestEditor(unittest.TestCase):

    def test_editor_actions(self):
        doc = Document()
        editor = NppEditor(doc)
        editor.setPlainText("Hello World\nLine 2\nLine 3")

        # Bookmark toggle
        editor.toggle_bookmark(0)
        self.assertIn(0, doc.bookmarks)
        editor.toggle_bookmark(0)
        self.assertNotIn(0, doc.bookmarks)

        # Duplicate line
        editor.go_to_line(1)
        editor.duplicate_current_line()
        self.assertEqual(editor.blockCount(), 4)

        # Case conversions
        editor.selectAll()
        editor.convert_case_upper()
        self.assertIn("HELLO WORLD", editor.toPlainText())

        editor.convert_case_lower()
        self.assertIn("hello world", editor.toPlainText())


if __name__ == "__main__":
    unittest.main()
