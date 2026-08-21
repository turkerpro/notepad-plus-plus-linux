"""
Unit tests for Syntax Highlighter and Themes.
"""
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextDocument

from npp_linux.core.highlighter import NppHighlighter
from npp_linux.styles.themes import THEME_PRESETS

# Headless Qt application instance
app = QApplication.instance() or QApplication([])


class TestHighlighter(unittest.TestCase):

    def test_highlighter_initialization(self):
        doc = QTextDocument()
        doc.setPlainText("def hello_world():\n    print('Notepad++ on Linux')\n")

        highlighter = NppHighlighter(doc, "Python", THEME_PRESETS["Classic Default"])
        self.assertIsNotNone(highlighter.lexer)

        # Switch theme
        highlighter.set_theme(THEME_PRESETS["Monokai"])
        self.assertEqual(highlighter.theme_colors["background"], "#272822")

        # Switch language
        highlighter.set_language("C++")
        self.assertIsNotNone(highlighter.lexer)

        highlighter.set_language("Plain Text")
        self.assertIsNone(highlighter.lexer)


if __name__ == "__main__":
    unittest.main()
