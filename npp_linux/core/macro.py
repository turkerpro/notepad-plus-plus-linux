"""
Macro recording and playback engine for Notepad++ Linux.
"""
from typing import List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor


class MacroAction:
    def __init__(self, action_type: str, data: Any = None):
        self.action_type = action_type  # "insert_text", "key", "command"
        self.data = data


class MacroManager(QObject):
    """Manages recording and executing macros."""

    recording_state_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.recorded_actions: List[MacroAction] = []

    def start_recording(self):
        self.recorded_actions.clear()
        self.is_recording = True
        self.recording_state_changed.emit(True)

    def stop_recording(self):
        self.is_recording = False
        self.recording_state_changed.emit(False)

    def record_action(self, action_type: str, data: Any = None):
        if self.is_recording:
            self.recorded_actions.append(MacroAction(action_type, data))

    def play_macro(self, editor):
        """Execute recorded actions on target editor."""
        if not self.recorded_actions or not editor:
            return

        cursor = editor.textCursor()
        cursor.beginEditBlock()
        for act in self.recorded_actions:
            if act.action_type == "insert_text":
                editor.insertPlainText(act.data)
            elif act.action_type == "command":
                cmd = getattr(editor, act.data, None)
                if callable(cmd):
                    cmd()
        cursor.endEditBlock()

    def play_macro_n_times(self, editor, count: int):
        for _ in range(count):
            self.play_macro(editor)
