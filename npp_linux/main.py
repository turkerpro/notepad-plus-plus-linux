"""
Entry point for Notepad++ Linux application.
"""
import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Ensure package path is included
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from npp_linux.ui.main_window import NppMainWindow


def main():
    parser = argparse.ArgumentParser(description="Notepad++ for Linux (Native Qt Edition)")
    parser.add_argument("files", nargs="*", help="Dosya yolları (Files to open)")
    parser.add_argument("-n", "--line", type=int, default=None, help="Açılışta gidilecek satır numarası (Go to line number)")
    parser.add_argument("-v", "--version", action="version", version="Notepad++ Linux v8.9.7")

    args, unknown = parser.parse_known_args()

    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Notepad++")
    app.setOrganizationName("Notepad++")

    # Combine known file args and unknown positional arguments if any
    all_files = list(args.files)
    for u in unknown:
        if not u.startswith("-") and os.path.exists(u):
            all_files.append(u)

    window = NppMainWindow(files_to_open=all_files, initial_line=args.line)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
