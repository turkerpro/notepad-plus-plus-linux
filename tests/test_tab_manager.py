"""
Unit tests for TabManager and Split View.
"""
import unittest
from PyQt5.QtWidgets import QApplication
from npp_linux.core.document import Document
from npp_linux.ui.tab_manager import NppTabManager

app = QApplication.instance() or QApplication([])


class TestTabManager(unittest.TestCase):

    def test_tab_operations_and_split(self):
        tm = NppTabManager()
        doc1 = Document()
        doc2 = Document()

        ed1 = tm.add_document(doc1)
        ed2 = tm.add_document(doc2)

        self.assertEqual(len(tm.all_editors()), 2)
        self.assertEqual(tm.primary_view.count(), 2)
        self.assertFalse(tm.secondary_view.isVisible())

        # Move to other view (Split view)
        tm.move_tab(tm.primary_view, tm.secondary_view, 1)
        self.assertEqual(tm.primary_view.count(), 1)
        self.assertEqual(tm.secondary_view.count(), 1)
        self.assertFalse(tm.secondary_view.isHidden())


if __name__ == "__main__":
    unittest.main()
