"""
Document representation for Notepad++ Linux.
"""
import os
from typing import Optional, Set
from PyQt5.QtCore import QObject, pyqtSignal

from .encoding import (
    EOL_UNIX, EOL_WINDOWS, EOL_MAC,
    read_file_with_encoding, save_file_with_encoding
)


class Document(QObject):
    """Represents a single open file or unsaved buffer in Notepad++."""

    modified_changed = pyqtSignal(bool)
    title_changed = pyqtSignal(str)
    encoding_changed = pyqtSignal(str)
    eol_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)
    readonly_changed = pyqtSignal(bool)

    _new_doc_counter = 1

    def __init__(self, file_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._is_modified = False
        self._is_readonly = False
        self.encoding = "UTF-8"
        self.eol = EOL_UNIX
        self.language = "Plain Text"
        self.bookmarks: Set[int] = set()  # set of 0-based line numbers
        self.initial_content = ""

        if self.file_path:
            self.title = os.path.basename(self.file_path)
            self._load_from_disk()
            self._detect_language()
        else:
            self.title = f"new {Document._new_doc_counter}"
            Document._new_doc_counter += 1
            self.initial_content = ""
            self.eol = EOL_WINDOWS  # Windows CRLF by default in Notepad++

    def _load_from_disk(self):
        if not self.file_path or not os.path.exists(self.file_path):
            return
        content, enc, eol = read_file_with_encoding(self.file_path)
        self.initial_content = content
        self.encoding = enc
        self.eol = eol
        self._is_readonly = not os.access(self.file_path, os.W_OK)

    def _detect_language(self):
        if not self.file_path:
            return
        ext = os.path.splitext(self.file_path)[1].lower()
        mapping = {
            ".py": "Python",
            ".c": "C",
            ".cpp": "C++",
            ".cc": "C++",
            ".cxx": "C++",
            ".h": "C/C++ Header",
            ".hpp": "C++ Header",
            ".cs": "C#",
            ".java": "Java",
            ".js": "JavaScript",
            ".jsx": "React JSX",
            ".ts": "TypeScript",
            ".tsx": "React TSX",
            ".html": "HTML",
            ".htm": "HTML",
            ".xml": "XML",
            ".svg": "XML/SVG",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "Sass",
            ".less": "Less",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".sh": "Bash/Shell",
            ".bash": "Bash/Shell",
            ".zsh": "Zsh",
            ".sql": "SQL",
            ".php": "PHP",
            ".rb": "Ruby",
            ".rs": "Rust",
            ".go": "Go",
            ".lua": "Lua",
            ".pl": "Perl",
            ".md": "Markdown",
            ".markdown": "Markdown",
            ".ini": "INI Config",
            ".conf": "Configuration",
            ".cfg": "Configuration",
            ".toml": "TOML",
            ".bat": "Batch",
            ".cmd": "Batch",
            ".ps1": "PowerShell",
            ".diff": "Diff",
            ".patch": "Diff",
            ".r": "R",
            ".dart": "Dart",
            ".kt": "Kotlin",
            ".swift": "Swift",
            ".asm": "Assembly",
            ".vhd": "VHDL",
            ".verilog": "Verilog",
            ".cmake": "CMake",
            ".makefile": "Makefile",
        }
        if os.path.basename(self.file_path).lower() in ["makefile", "cmakelists.txt", "dockerfile"]:
            fname = os.path.basename(self.file_path).lower()
            if fname == "makefile":
                self.language = "Makefile"
            elif fname == "cmakelists.txt":
                self.language = "CMake"
            elif fname == "dockerfile":
                self.language = "Dockerfile"
        else:
            self.language = mapping.get(ext, "Plain Text")

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, val: bool):
        if self._is_modified != val:
            self._is_modified = val
            self.modified_changed.emit(val)

    @property
    def is_readonly(self) -> bool:
        return self._is_readonly

    @is_readonly.setter
    def is_readonly(self, val: bool):
        if self._is_readonly != val:
            self._is_readonly = val
            self.readonly_changed.emit(val)

    def set_encoding(self, enc: str):
        if self.encoding != enc:
            self.encoding = enc
            self.encoding_changed.emit(enc)

    def set_eol(self, eol: str):
        if self.eol != eol:
            self.eol = eol
            self.eol_changed.emit(eol)

    def set_language(self, lang: str):
        if self.language != lang:
            self.language = lang
            self.language_changed.emit(lang)

    def save(self, content: str, target_path: Optional[str] = None) -> bool:
        """Save document content to disk."""
        save_path = target_path or self.file_path
        if not save_path:
            return False
        try:
            save_file_with_encoding(save_path, content, self.encoding, self.eol)
            self.file_path = save_path
            self.title = os.path.basename(save_path)
            self.title_changed.emit(self.title)
            self._detect_language()
            self.language_changed.emit(self.language)
            self.is_modified = False
            return True
        except Exception as e:
            print(f"Error saving file {save_path}: {e}")
            return False
