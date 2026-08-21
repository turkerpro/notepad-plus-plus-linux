"""
Notepad++ Themes, Color Schemes, and Qt Stylesheets.
"""
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any


# Built-in fallback color palettes matching official Notepad++ themes
THEME_PRESETS = {
    "Classic Default": {
        "background": "#FFFFFF",
        "foreground": "#000000",
        "current_line": "#E8E8FF",
        "selection_bg": "#C0C0C0",
        "selection_fg": "#000000",
        "caret": "#000000",
        "line_num_bg": "#ECE9D8",
        "line_num_fg": "#808080",
        "margin_bg": "#ECE9D8",
        "indent_guide": "#D3D3D3",
        "keyword": "#0000FF",       # Blue bold
        "function": "#95004A",      # Magenta / Purple
        "type": "#8000FF",          # Violet
        "string": "#808080",        # Grey / Reddish
        "number": "#FF8000",        # Orange
        "comment": "#008000",       # Green
        "operator": "#000080",      # Dark Blue
        "preprocessor": "#804000",  # Brown
        "tag": "#000080",
        "attribute": "#FF0000",
        "bracket_match": "#3399FF",
    },
    "DarkModeDefault": {
        "background": "#202020",
        "foreground": "#E0E0E0",
        "current_line": "#2D2D2D",
        "selection_bg": "#404040",
        "selection_fg": "#FFFFFF",
        "caret": "#FFFFFF",
        "line_num_bg": "#2B2B2B",
        "line_num_fg": "#787878",
        "margin_bg": "#2B2B2B",
        "indent_guide": "#3F3F3F",
        "keyword": "#569CD6",
        "function": "#DCDCAA",
        "type": "#4EC9B0",
        "string": "#CE9178",
        "number": "#B5CEA8",
        "comment": "#6A9955",
        "operator": "#D4D4D4",
        "preprocessor": "#C586C0",
        "tag": "#569CD6",
        "attribute": "#9CDCFE",
        "bracket_match": "#0E639C",
    },
    "Monokai": {
        "background": "#272822",
        "foreground": "#F8F8F2",
        "current_line": "#3E3D32",
        "selection_bg": "#49483E",
        "selection_fg": "#F8F8F2",
        "caret": "#F8F8F0",
        "line_num_bg": "#1E1F1C",
        "line_num_fg": "#75715E",
        "margin_bg": "#1E1F1C",
        "indent_guide": "#49483E",
        "keyword": "#F92672",
        "function": "#A6E22E",
        "type": "#66D9EF",
        "string": "#E6DB74",
        "number": "#AE81FF",
        "comment": "#75715E",
        "operator": "#F92672",
        "preprocessor": "#FD971F",
        "tag": "#F92672",
        "attribute": "#A6E22E",
        "bracket_match": "#FD971F",
    },
    "Bespin": {
        "background": "#28211C",
        "foreground": "#BAAE9E",
        "current_line": "#362F29",
        "selection_bg": "#544538",
        "selection_fg": "#FFFFFF",
        "caret": "#FFFFFF",
        "line_num_bg": "#1E1815",
        "line_num_fg": "#6B5A4B",
        "margin_bg": "#1E1815",
        "indent_guide": "#3B322A",
        "keyword": "#5EA6EA",
        "function": "#937121",
        "type": "#937121",
        "string": "#54BE0D",
        "number": "#CF6A4C",
        "comment": "#666666",
        "operator": "#E4BE6B",
        "preprocessor": "#E86F2C",
        "tag": "#5EA6EA",
        "attribute": "#937121",
        "bracket_match": "#E86F2C",
    },
    "Obsidian": {
        "background": "#293134",
        "foreground": "#E0E2E4",
        "current_line": "#2F393C",
        "selection_bg": "#404E51",
        "selection_fg": "#E0E2E4",
        "caret": "#FFFFFF",
        "line_num_bg": "#222729",
        "line_num_fg": "#66747B",
        "margin_bg": "#222729",
        "indent_guide": "#3F4B4E",
        "keyword": "#93C763",
        "function": "#678CB1",
        "type": "#678CB1",
        "string": "#EC7600",
        "number": "#FFCD22",
        "comment": "#66747B",
        "operator": "#E8E2B7",
        "preprocessor": "#A082BD",
        "tag": "#8CBBAD",
        "attribute": "#B3D6C9",
        "bracket_match": "#FFCD22",
    },
    "Zenburn": {
        "background": "#3F3F3F",
        "foreground": "#DCDCCC",
        "current_line": "#4F4F4F",
        "selection_bg": "#2A332B",
        "selection_fg": "#FEFEFE",
        "caret": "#DCDCCC",
        "line_num_bg": "#333333",
        "line_num_fg": "#7F9F7F",
        "margin_bg": "#333333",
        "indent_guide": "#5F5F5F",
        "keyword": "#F0DFAF",
        "function": "#DFAF8F",
        "type": "#7CB8BB",
        "string": "#CC9393",
        "number": "#8CD0D3",
        "comment": "#7F9F7F",
        "operator": "#F0EFD0",
        "preprocessor": "#FFCFBF",
        "tag": "#E89393",
        "attribute": "#DFAF8F",
        "bracket_match": "#F0DFAF",
    },
    "Deep Black": {
        "background": "#000000",
        "foreground": "#FFFFFF",
        "current_line": "#1A1A1A",
        "selection_bg": "#333333",
        "selection_fg": "#FFFFFF",
        "caret": "#FFFFFF",
        "line_num_bg": "#111111",
        "line_num_fg": "#555555",
        "margin_bg": "#111111",
        "indent_guide": "#2A2A2A",
        "keyword": "#00AAFF",
        "function": "#FFFF00",
        "type": "#55FF55",
        "string": "#FFAA00",
        "number": "#FF5555",
        "comment": "#888888",
        "operator": "#FFFFFF",
        "preprocessor": "#FF00FF",
        "tag": "#00AAFF",
        "attribute": "#FFFF00",
        "bracket_match": "#FF5555",
    }
}


def load_theme_xml(xml_path: str) -> Dict[str, str]:
    """Parse Notepad++ styler XML to extract color mapping."""
    theme = dict(THEME_PRESETS["Classic Default"])
    if not os.path.exists(xml_path):
        return theme

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Find GlobalStyles
        for lexer in root.findall(".//LexerType"):
            if lexer.get("name") == "Global Styles":
                for style in lexer.findall("WordsStyle"):
                    sname = style.get("name", "")
                    fg = style.get("fgColor", "")
                    bg = style.get("bgColor", "")
                    if sname == "Default Style":
                        if bg: theme["background"] = f"#{bg}"
                        if fg: theme["foreground"] = f"#{fg}"
                    elif sname == "Current line background colour":
                        if bg: theme["current_line"] = f"#{bg}"
                    elif sname == "Selected text colour":
                        if bg: theme["selection_bg"] = f"#{bg}"
                        if fg: theme["selection_fg"] = f"#{fg}"
                    elif sname == "Caret colour":
                        if fg: theme["caret"] = f"#{fg}"
                    elif sname == "Line numbers margin":
                        if bg: theme["line_num_bg"] = f"#{bg}"
                        if fg: theme["line_num_fg"] = f"#{fg}"
                    elif sname == "Fold margin":
                        if bg: theme["margin_bg"] = f"#{bg}"
                    elif sname == "Indent guideline style":
                        if fg: theme["indent_guide"] = f"#{fg}"
    except Exception as e:
        print(f"Error parsing theme {xml_path}: {e}")

    return theme


def get_app_stylesheet(is_dark: bool = False) -> str:
    """Return Qt Application Stylesheet for Dark or Classic Light mode."""
    if is_dark:
        return """
        QMainWindow {
            background-color: #2D2D30;
            color: #F1F1F1;
        }
        QMenuBar {
            background-color: #1E1E1E;
            color: #DCDCDC;
            border-bottom: 1px solid #3E3E42;
            padding: 2px 4px;
        }
        QMenuBar::item:selected {
            background-color: #333337;
            color: #FFFFFF;
            border-radius: 3px;
        }
        QMenu {
            background-color: #1E1E1E;
            color: #DCDCDC;
            border: 1px solid #3E3E42;
            padding: 4px;
        }
        QMenu::item:selected {
            background-color: #094771;
            color: #FFFFFF;
            border-radius: 2px;
        }
        QMenu::separator {
            height: 1px;
            background-color: #3E3E42;
            margin: 4px 6px;
        }
        QToolBar {
            background-color: #252526;
            border-bottom: 1px solid #3E3E42;
            spacing: 2px;
            padding: 2px;
        }
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 3px;
            margin: 1px;
        }
        QToolButton:hover {
            background-color: #3E3E42;
            border: 1px solid #007ACC;
        }
        QToolButton:pressed {
            background-color: #007ACC;
        }
        QStatusBar {
            background-color: #007ACC;
            color: #FFFFFF;
            font-size: 11px;
        }
        QStatusBar QLabel {
            color: #FFFFFF;
            padding: 0 6px;
        }
        QTabBar::tab {
            background-color: #2D2D30;
            color: #969696;
            border: 1px solid #3E3E42;
            border-bottom: none;
            padding: 4px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border-top: 2px solid #007ACC;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #383838;
            color: #DCDCDC;
        }
        QTabWidget::pane {
            border: 1px solid #3E3E42;
            top: -1px;
            background-color: #1E1E1E;
        }
        QDockWidget {
            titlebar-close-icon: url();
            color: #DCDCDC;
            font-weight: bold;
        }
        QDockWidget::title {
            background-color: #252526;
            border: 1px solid #3E3E42;
            padding: 4px;
            text-align: left;
        }
        QTreeView, QListWidget, QTreeWidget {
            background-color: #252526;
            color: #DCDCDC;
            border: 1px solid #3E3E42;
            outline: none;
        }
        QTreeView::item:hover, QListWidget::item:hover {
            background-color: #2A2D2E;
        }
        QTreeView::item:selected, QListWidget::item:selected {
            background-color: #094771;
            color: #FFFFFF;
        }
        QSplitter::handle {
            background-color: #3E3E42;
        }
        QScrollBar:vertical {
            background-color: #1E1E1E;
            width: 12px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background-color: #424242;
            min-height: 20px;
            border-radius: 4px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #686868;
        }
        QScrollBar:horizontal {
            background-color: #1E1E1E;
            height: 12px;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background-color: #424242;
            min-width: 20px;
            border-radius: 4px;
            margin: 2px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #686868;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            width: 0px;
            height: 0px;
        }
        """
    else:
        return """
        QMainWindow {
            background-color: #F0F0F0;
            color: #000000;
        }
        QMenuBar {
            background-color: #F5F5F5;
            color: #000000;
            border-bottom: 1px solid #CCCCCC;
            padding: 2px 4px;
        }
        QMenuBar::item:selected {
            background-color: #CCE8FF;
            color: #000000;
            border-radius: 2px;
        }
        QMenu {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            padding: 4px;
        }
        QMenu::item:selected {
            background-color: #91C9F7;
            color: #000000;
            border-radius: 2px;
        }
        QMenu::separator {
            height: 1px;
            background-color: #E0E0E0;
            margin: 4px 6px;
        }
        QToolBar {
            background-color: #EDEDED;
            border-bottom: 1px solid #CCCCCC;
            spacing: 2px;
            padding: 2px;
        }
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 3px;
            margin: 1px;
        }
        QToolButton:hover {
            background-color: #E0EEF9;
            border: 1px solid #70C0E7;
        }
        QToolButton:pressed {
            background-color: #BEE6FD;
            border: 1px solid #3C7FB1;
        }
        QStatusBar {
            background-color: #EAEAEA;
            color: #333333;
            border-top: 1px solid #CCCCCC;
            font-size: 11px;
        }
        QStatusBar QLabel {
            color: #333333;
            padding: 0 6px;
        }
        QTabBar::tab {
            background-color: #E1E1E1;
            color: #333333;
            border: 1px solid #C0C0C0;
            border-bottom: none;
            padding: 4px 12px;
            margin-right: 2px;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #000000;
            border-top: 2px solid #FF8000;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #ECECEC;
        }
        QTabWidget::pane {
            border: 1px solid #C0C0C0;
            top: -1px;
            background-color: #FFFFFF;
        }
        QDockWidget {
            color: #000000;
            font-weight: bold;
        }
        QDockWidget::title {
            background-color: #E6E6E6;
            border: 1px solid #D0D0D0;
            padding: 4px;
            text-align: left;
        }
        QTreeView, QListWidget, QTreeWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QSplitter::handle {
            background-color: #D8D8D8;
        }
        """
