"""
Unit tests for Encoding and Line Ending detection and conversion.
"""
import os
import tempfile
import unittest
from npp_linux.core.encoding import (
    detect_line_ending, convert_line_endings, read_file_with_encoding, save_file_with_encoding,
    EOL_WINDOWS, EOL_UNIX, EOL_MAC
)


class TestEncoding(unittest.TestCase):

    def test_eol_detection(self):
        crlf_text = "line1\r\nline2\r\nline3"
        lf_text = "line1\nline2\nline3"
        cr_text = "line1\rline2\rline3"

        self.assertEqual(detect_line_ending(crlf_text), EOL_WINDOWS)
        self.assertEqual(detect_line_ending(lf_text), EOL_UNIX)
        self.assertEqual(detect_line_ending(cr_text), EOL_MAC)

    def test_eol_conversion(self):
        text = "line1\r\nline2\nline3\rline4"
        win = convert_line_endings(text, EOL_WINDOWS)
        self.assertEqual(win, "line1\r\nline2\r\nline3\r\nline4")

        unix = convert_line_endings(text, EOL_UNIX)
        self.assertEqual(unix, "line1\nline2\nline3\nline4")

        mac = convert_line_endings(text, EOL_MAC)
        self.assertEqual(mac, "line1\rline2\rline3\rline4")

    def test_utf8_bom_and_turkish(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            turkish_text = "Notepad++ Linux Türkçe Desteği: Ş, Ğ, Ü, Ç, Ö, İ, ı, ş, ğ, ü, ç, ö\r\nİkinci satır"
            save_file_with_encoding(tmp_path, turkish_text, "UTF-8 with BOM", EOL_WINDOWS)

            content, enc, eol = read_file_with_encoding(tmp_path)
            self.assertEqual(enc, "UTF-8 with BOM")
            self.assertEqual(eol, EOL_WINDOWS)
            self.assertIn("Ş, Ğ, Ü", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
