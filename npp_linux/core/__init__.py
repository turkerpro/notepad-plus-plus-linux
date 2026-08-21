"""
Notepad++ Linux Core package.
"""
from .document import Document
from .editor import NppEditor
from .encoding import ENCODINGS, EOL_WINDOWS, EOL_UNIX, EOL_MAC
from .highlighter import NppHighlighter
from .macro import MacroManager
from .session import save_session, load_session, save_config, load_config

__all__ = [
    "Document",
    "NppEditor",
    "ENCODINGS",
    "EOL_WINDOWS",
    "EOL_UNIX",
    "EOL_MAC",
    "NppHighlighter",
    "MacroManager",
    "save_session",
    "load_session",
    "save_config",
    "load_config",
]
