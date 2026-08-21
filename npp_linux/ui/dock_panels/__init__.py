"""
Dock panels for Notepad++ Linux.
"""
from .document_map import DocumentMapDock
from .function_list import FunctionListDock
from .file_browser import FileBrowserDock
from .search_results import SearchResultsDock

__all__ = [
    "DocumentMapDock",
    "FunctionListDock",
    "FileBrowserDock",
    "SearchResultsDock",
]
