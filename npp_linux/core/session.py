"""
Session manager for Notepad++ Linux.
Saves open files, active tab, cursor positions, and preferences.
"""
import os
import json
from typing import List, Dict, Any

SESSION_DIR = os.path.expanduser("~/.config/notepad-plus-plus-linux")
SESSION_FILE = os.path.join(SESSION_DIR, "session.json")
CONFIG_FILE = os.path.join(SESSION_DIR, "config.json")


def save_session(files: List[Dict[str, Any]], active_index: int):
    """Save open document paths and state."""
    try:
        os.makedirs(SESSION_DIR, exist_ok=True)
        data = {
            "active_index": active_index,
            "files": files
        }
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save session: {e}")


def load_session() -> Dict[str, Any]:
    """Load previously open files and state."""
    if not os.path.exists(SESSION_FILE):
        return {"active_index": 0, "files": []}
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load session: {e}")
        return {"active_index": 0, "files": []}


def save_config(config: Dict[str, Any]):
    """Save user preferences (theme, font, dark mode, etc.)."""
    try:
        os.makedirs(SESSION_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")


def load_config() -> Dict[str, Any]:
    """Load user preferences."""
    default_config = {
        "dark_mode": False,
        "theme": "Classic Default",
        "font_family": "Monospace",
        "font_size": 11,
        "tab_size": 4,
        "show_line_numbers": True,
        "show_bookmarks": True,
        "show_folding": True,
        "show_whitespaces": False,
        "show_eol": False,
        "show_indent_guides": True,
        "word_wrap": False,
        "recent_files": []
    }
    if not os.path.exists(CONFIG_FILE):
        return default_config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_config.update(data)
            return default_config
    except Exception as e:
        print(f"Failed to load config: {e}")
        return default_config
