"""
Main NppEditor Component for Notepad++ Linux.
Full-featured code editor with line numbers, bookmarks, folding, whitespace symbols,
indent guides, smart highlighting, and rich text editing shortcuts.
"""
import re
from typing import Set, Dict, List, Optional
from PyQt5.QtWidgets import (
    QPlainTextEdit, QWidget, QTextEdit, QApplication
)
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QTextFormat, QTextCursor, QFontMetrics,
    QPaintEvent, QKeyEvent, QMouseEvent, QWheelEvent, QPen
)
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal

from .document import Document
from .highlighter import NppHighlighter
from ..styles.themes import THEME_PRESETS


class LineNumberMargin(QWidget):
    """Gutter margin for line numbers, bookmarks, and folding indicators."""

    def __init__(self, editor: 'NppEditor'):
        super().__init__(editor)
        self.editor = editor
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:
        return QSize(self.editor.margin_width(), 0)

    def paintEvent(self, event: QPaintEvent):
        self.editor.margin_paint_event(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.editor.margin_mouse_press_event(event)


class NppEditor(QPlainTextEdit):
    """
    Notepad++ Native Editor widget.
    """

    cursor_position_changed = pyqtSignal(int, int, int)  # line, col, total_chars
    selection_length_changed = pyqtSignal(int)
    lines_count_changed = pyqtSignal(int, int)  # doc_len, line_count
    bookmarks_changed = pyqtSignal()

    def __init__(self, document: Optional[Document] = None, parent=None):
        super().__init__(parent)
        self.document_model = document or Document()
        self.margin = LineNumberMargin(self)

        # Editor visual options
        self.show_line_numbers = True
        self.show_bookmarks = True
        self.show_folding = True
        self.show_whitespaces = False
        self.show_eol = False
        self.show_indent_guides = True
        self.auto_indent = True
        self.tab_size = 4
        self.use_spaces_for_tab = False
        self.zoom_level = 0
        self.base_font_size = 11

        # Theme & Color options
        self.theme_colors = dict(THEME_PRESETS["Classic Default"])

        # Editor fonts
        font = QFont("Monospace", self.base_font_size)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(' ') * self.tab_size)

        # Syntax Highlighter
        self.highlighter = NppHighlighter(self.document(), self.document_model.language, self.theme_colors)

        # Folded lines set (0-based line indices)
        self.folded_blocks: Set[int] = set()

        # Connect document events
        self.blockCountChanged.connect(self.update_margin_width)
        self.updateRequest.connect(self.update_margin_area)
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.selectionChanged.connect(self.on_selection_changed)

        # Load initial text if available
        if self.document_model.initial_content:
            self.setPlainText(self.document_model.initial_content)
            self.document_model.is_modified = False

        self.textChanged.connect(self.on_text_changed)
        self.document_model.language_changed.connect(self.highlighter.set_language)

        self.update_margin_width(0)
        self.apply_theme(self.theme_colors)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

    def apply_theme(self, theme_colors: Dict[str, str]):
        """Apply color palette to editor and highlighter."""
        self.theme_colors = theme_colors
        bg = theme_colors.get("background", "#FFFFFF")
        fg = theme_colors.get("foreground", "#000000")
        sel_bg = theme_colors.get("selection_bg", "#C0C0C0")
        sel_fg = theme_colors.get("selection_fg", "#000000")

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {bg};
                color: {fg};
                selection-background-color: {sel_bg};
                selection-color: {sel_fg};
                border: none;
            }}
        """)
        self.highlighter.set_theme(theme_colors)
        self.highlight_current_line()
        self.margin.update()

    def set_zoom(self, zoom_delta: int):
        """Increase, decrease, or reset editor font size."""
        if zoom_delta == 0:
            self.zoom_level = 0
        else:
            self.zoom_level = max(-6, min(20, self.zoom_level + zoom_delta))

        new_size = max(6, self.base_font_size + self.zoom_level)
        f = self.font()
        f.setPointSize(new_size)
        self.setFont(f)
        self.setTabStopDistance(QFontMetrics(f).horizontalAdvance(' ') * self.tab_size)
        self.update_margin_width(0)

    # -------------------------------------------------------------------------
    # Margin & Gutter Painting (Line Numbers, Bookmarks, Fold Markers)
    # -------------------------------------------------------------------------

    def margin_width(self) -> int:
        digits = max(1, len(str(max(1, self.blockCount()))))
        # bookmark area (18px) + line number width + fold margin (16px) + padding
        char_width = self.fontMetrics().horizontalAdvance('9')
        line_num_w = digits * char_width + 12
        bookmark_w = 20 if self.show_bookmarks else 0
        fold_w = 16 if self.show_folding else 0
        return bookmark_w + line_num_w + fold_w + 4

    def update_margin_width(self, _):
        self.setViewportMargins(self.margin_width(), 0, 0, 0)

    def update_margin_area(self, rect: QRect, dy: int):
        if dy:
            self.margin.scroll(0, dy)
        else:
            self.margin.update(0, rect.y(), self.margin.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_margin_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.margin.setGeometry(QRect(cr.left(), cr.top(), self.margin_width(), cr.height()))

    def margin_paint_event(self, event: QPaintEvent):
        painter = QPainter(self.margin)
        painter.setFont(self.font())

        margin_bg = QColor(self.theme_colors.get("line_num_bg", "#ECE9D8"))
        line_num_fg = QColor(self.theme_colors.get("line_num_fg", "#808080"))
        current_line_num_fg = QColor(self.theme_colors.get("foreground", "#000000"))
        bookmark_color = QColor("#4682B4")  # Notepad++ Classic Blue Sphere Bookmark
        fold_color = QColor(self.theme_colors.get("line_num_fg", "#808080"))

        painter.fillRect(event.rect(), margin_bg)

        # Draw vertical separator line
        sep_color = QColor(self.theme_colors.get("indent_guide", "#D0D0D0"))
        painter.setPen(sep_color)
        painter.drawLine(self.margin.width() - 1, event.rect().top(),
                         self.margin.width() - 1, event.rect().bottom())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        current_block_number = self.textCursor().blockNumber()

        digits = max(1, len(str(max(1, self.blockCount()))))
        char_width = self.fontMetrics().horizontalAdvance('9')
        line_num_w = digits * char_width + 8
        bookmark_w = 20 if self.show_bookmarks else 0

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                # 1. Draw Bookmark if present
                if self.show_bookmarks and block_number in self.document_model.bookmarks:
                    painter.setBrush(bookmark_color)
                    painter.setPen(bookmark_color.darker(130))
                    # Draw a nice glossy circular bookmark ball
                    painter.drawEllipse(3, top + (self.fontMetrics().height() - 12) // 2, 12, 12)
                    painter.setBrush(QColor(255, 255, 255, 180))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(5, top + (self.fontMetrics().height() - 12) // 2 + 2, 4, 4)

                # 2. Draw Line Number
                if self.show_line_numbers:
                    painter.setPen(current_line_num_fg if block_number == current_block_number else line_num_fg)
                    number_str = str(block_number + 1)
                    painter.drawText(
                        bookmark_w, top, line_num_w, self.fontMetrics().height(),
                        Qt.AlignRight | Qt.AlignVCenter, number_str
                    )

                # 3. Draw Fold Marker if block has children/indent
                if self.show_folding and self._is_foldable_block(block):
                    fold_x = bookmark_w + line_num_w + 4
                    fold_y = top + (self.fontMetrics().height() - 10) // 2
                    is_folded = block_number in self.folded_blocks
                    painter.setPen(fold_color)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(fold_x, fold_y, 9, 9)
                    # draw minus or plus
                    painter.drawLine(fold_x + 2, fold_y + 4, fold_x + 7, fold_y + 4)
                    if is_folded:
                        painter.drawLine(fold_x + 4, fold_y + 2, fold_x + 4, fold_y + 7)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def margin_mouse_press_event(self, event: QMouseEvent):
        """Handle clicks on margin (bookmark toggle or folding)."""
        cursor = self.cursorForPosition(event.pos())
        block_number = cursor.blockNumber()

        bookmark_w = 20 if self.show_bookmarks else 0
        if event.x() <= bookmark_w:
            # Clicked bookmark area
            self.toggle_bookmark(block_number)
        else:
            # Clicked line number area -> select line
            cursor.select(QTextCursor.LineUnderCursor)
            self.setTextCursor(cursor)

    def _is_foldable_block(self, block) -> bool:
        """Check if block is the start of a foldable block (e.g. opens block or has higher indent)."""
        text = block.text()
        if any(text.rstrip().endswith(c) for c in [":", "{", "(", "["]):
            return True
        next_b = block.next()
        if next_b.isValid() and len(next_b.text()) > len(text) and next_b.text().startswith("    "):
            return True
        return False

    # -------------------------------------------------------------------------
    # Editor Paint & Visual Overlays (Whitespace, Indent Guides, Line Highlight)
    # -------------------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if not (self.show_whitespaces or self.show_eol or self.show_indent_guides):
            return

        painter = QPainter(self.viewport())
        font_metrics = self.fontMetrics()
        char_w = font_metrics.horizontalAdvance(' ')
        line_h = font_metrics.height()

        guide_color = QColor(self.theme_colors.get("indent_guide", "#D0D0D0"))
        ws_color = QColor(self.theme_colors.get("line_num_fg", "#808080"))
        ws_color.setAlpha(120)

        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                text = block.text()

                # Indentation guides
                if self.show_indent_guides:
                    painter.setPen(QPen(guide_color, 1, Qt.DotLine))
                    leading_spaces = len(text) - len(text.lstrip(' '))
                    indent_levels = leading_spaces // self.tab_size
                    for lvl in range(1, indent_levels + 1):
                        gx = lvl * self.tab_size * char_w
                        painter.drawLine(gx, top, gx, bottom)

                # Whitespace / Tab / EOL markers
                if self.show_whitespaces:
                    painter.setPen(ws_color)
                    for i, ch in enumerate(text):
                        cx = i * char_w + (char_w // 2)
                        cy = top + (line_h // 2)
                        if ch == ' ':
                            painter.drawPoint(cx, cy)
                        elif ch == '\t':
                            tx = i * char_w
                            painter.drawLine(tx + 2, cy, tx + char_w * self.tab_size - 2, cy)
                            painter.drawLine(tx + char_w * self.tab_size - 4, cy - 2, tx + char_w * self.tab_size - 2, cy)
                            painter.drawLine(tx + char_w * self.tab_size - 4, cy + 2, tx + char_w * self.tab_size - 2, cy)

                if self.show_eol:
                    painter.setPen(ws_color)
                    eol_text = self.document_model.eol
                    ex = len(text) * char_w + 4
                    painter.drawText(ex, top + line_h - 2, f"[{eol_text}]")

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())

    def highlight_current_line(self):
        """Highlight current active line subtly."""
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.theme_colors.get("current_line", "#E8E8FF"))
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        # Highlight matching brackets
        self._highlight_matching_brackets(extra_selections)
        self.setExtraSelections(extra_selections)

    def _highlight_matching_brackets(self, extra_selections: List[QTextEdit.ExtraSelection]):
        cursor = self.textCursor()
        doc = self.document()
        pos = cursor.position()
        text = doc.toPlainText()
        if not text or pos >= len(text):
            return

        char = text[pos] if pos < len(text) else ""
        prev_char = text[pos - 1] if pos > 0 else ""

        pairs = {'(': ')', '[': ']', '{': '}'}
        rev_pairs = {')': '(', ']': '[', '}': '{'}

        match_pos = -1
        cur_bracket_pos = -1

        if char in pairs:
            cur_bracket_pos = pos
            target = pairs[char]
            depth = 1
            for i in range(pos + 1, len(text)):
                if text[i] == char: depth += 1
                elif text[i] == target:
                    depth -= 1
                    if depth == 0:
                        match_pos = i
                        break
        elif prev_char in rev_pairs:
            cur_bracket_pos = pos - 1
            target = rev_pairs[prev_char]
            depth = 1
            for i in range(pos - 2, -1, -1):
                if text[i] == prev_char: depth += 1
                elif text[i] == target:
                    depth -= 1
                    if depth == 0:
                        match_pos = i
                        break

        if match_pos != -1 and cur_bracket_pos != -1:
            match_color = QColor(self.theme_colors.get("bracket_match", "#3399FF"))
            for p in [cur_bracket_pos, match_pos]:
                sel = QTextEdit.ExtraSelection()
                c = QTextCursor(doc)
                c.setPosition(p)
                c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)
                sel.cursor = c
                sel.format.setBackground(match_color)
                sel.format.setFontWeight(QFont.Bold)
                extra_selections.append(sel)

    # -------------------------------------------------------------------------
    # Event Handlers & Signals
    # -------------------------------------------------------------------------

    def on_cursor_position_changed(self):
        self.highlight_current_line()
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        pos = cursor.position()
        self.cursor_position_changed.emit(line, col, pos)
        self.margin.update()

    def on_selection_changed(self):
        cursor = self.textCursor()
        sel_text = cursor.selectedText()
        self.selection_length_changed.emit(len(sel_text))

        # Smart highlight word
        if sel_text.isalnum() and len(sel_text) >= 2:
            self.highlighter.set_search_highlight_word(sel_text)
        elif not sel_text:
            self.highlighter.set_search_highlight_word("")

    def on_text_changed(self):
        self.document_model.is_modified = True
        doc_len = len(self.toPlainText())
        lines = self.blockCount()
        self.lines_count_changed.emit(doc_len, lines)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # Handle Tab and Shift+Tab
        if key == Qt.Key_Tab and not modifiers:
            if self.use_spaces_for_tab:
                self.insertPlainText(" " * self.tab_size)
                return
            else:
                self.insertPlainText("\t")
                return

        # Auto Indentation on Enter
        if key in (Qt.Key_Return, Qt.Key_Enter):
            if self.auto_indent:
                cursor = self.textCursor()
                line_text = cursor.block().text()
                # Find leading whitespace
                indent = ""
                for ch in line_text:
                    if ch in (' ', '\t'):
                        indent += ch
                    else:
                        break
                # Extra indent if ending with : or {
                if line_text.rstrip().endswith((':', '{', '(')):
                    indent += " " * self.tab_size if self.use_spaces_for_tab else "\t"

                super().keyPressEvent(event)
                self.insertPlainText(indent)
                return

        # Zoom with Ctrl + Key_Plus / Minus / 0
        if modifiers & Qt.ControlModifier:
            if key in (Qt.Key_Plus, Qt.Key_Equal):
                self.set_zoom(1)
                return
            elif key == Qt.Key_Minus:
                self.set_zoom(-1)
                return
            elif key == Qt.Key_0:
                self.set_zoom(0)
                return

        # Overwrite mode toggle with Insert key
        if key == Qt.Key_Insert:
            self.setOverwriteMode(not self.overwriteMode())
            return

        super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        # Zoom with Ctrl + Mouse Wheel
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.set_zoom(1)
            elif delta < 0:
                self.set_zoom(-1)
            event.accept()
            return
        super().wheelEvent(event)

    # -------------------------------------------------------------------------
    # Bookmarks Operations
    # -------------------------------------------------------------------------

    def toggle_bookmark(self, line_number: Optional[int] = None):
        """Toggle bookmark on line (0-based). Default: current line."""
        if line_number is None:
            line_number = self.textCursor().blockNumber()
        if line_number in self.document_model.bookmarks:
            self.document_model.bookmarks.remove(line_number)
        else:
            self.document_model.bookmarks.add(line_number)
        self.margin.update()
        self.bookmarks_changed.emit()

    def next_bookmark(self):
        """Navigate to next bookmark."""
        if not self.document_model.bookmarks:
            return
        cur_line = self.textCursor().blockNumber()
        sorted_bm = sorted(list(self.document_model.bookmarks))
        for bm in sorted_bm:
            if bm > cur_line:
                self.go_to_line(bm + 1)
                return
        # Wrap around to first
        self.go_to_line(sorted_bm[0] + 1)

    def prev_bookmark(self):
        """Navigate to previous bookmark."""
        if not self.document_model.bookmarks:
            return
        cur_line = self.textCursor().blockNumber()
        sorted_bm = sorted(list(self.document_model.bookmarks), reverse=True)
        for bm in sorted_bm:
            if bm < cur_line:
                self.go_to_line(bm + 1)
                return
        # Wrap around to last
        self.go_to_line(sorted_bm[0] + 1)

    def clear_all_bookmarks(self):
        self.document_model.bookmarks.clear()
        self.margin.update()
        self.bookmarks_changed.emit()

    # -------------------------------------------------------------------------
    # Advanced Editing Commands (Duplicate, Move, Case, Comment, Sort)
    # -------------------------------------------------------------------------

    def duplicate_current_line(self):
        """Duplicate current line or selection (Ctrl+D)."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.clearSelection()
            cursor.insertText(text)
        else:
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            line = cursor.selectedText()
            cursor.clearSelection()
            cursor.insertText("\n" + line)
        self.setTextCursor(cursor)

    def move_line_up(self):
        """Move line up (Ctrl+Shift+Up)."""
        cursor = self.textCursor()
        block = cursor.block()
        prev_block = block.previous()
        if not prev_block.isValid():
            return
        cursor.beginEditBlock()
        cur_text = block.text()
        prev_text = prev_block.text()

        cursor.movePosition(QTextCursor.PreviousBlock)
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(cur_text + "\n")
        cursor.endEditBlock()

    def move_line_down(self):
        """Move line down (Ctrl+Shift+Down)."""
        cursor = self.textCursor()
        block = cursor.block()
        next_block = block.next()
        if not next_block.isValid():
            return
        cursor.beginEditBlock()
        cur_text = block.text()
        next_text = next_block.text()

        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.movePosition(QTextCursor.NextBlock)
        cursor.insertText(cur_text + "\n")
        cursor.endEditBlock()

    def delete_current_line(self):
        """Delete current line (Ctrl+Shift+L)."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        self.setTextCursor(cursor)

    def toggle_comment(self):
        """Toggle comment for selection or current line (Ctrl+Q)."""
        lang = self.document_model.language
        comment_symbols = {
            "Python": "#", "Bash/Shell": "#", "Ruby": "#", "Perl": "#", "YAML": "#", "TOML": "#",
            "C": "//", "C++": "//", "C#": "//", "Java": "//", "JavaScript": "//",
            "TypeScript": "//", "Rust": "//", "Go": "//", "PHP": "//", "Swift": "//", "Kotlin": "//", "Dart": "//",
            "SQL": "--", "Lua": "--", "HTML": "<!--", "XML": "<!--", "CSS": "/*"
        }
        sym = comment_symbols.get(lang, "//")
        cursor = self.textCursor()
        cursor.beginEditBlock()

        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        c = QTextCursor(self.document())
        c.setPosition(start)
        start_block = c.blockNumber()
        c.setPosition(end)
        end_block = c.blockNumber()

        for b_num in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(b_num)
            text = block.text()
            c.setPosition(block.position())
            c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            if text.lstrip().startswith(sym):
                # Remove comment
                new_text = text.replace(sym + " ", "", 1) if (sym + " ") in text else text.replace(sym, "", 1)
                c.insertText(new_text)
            else:
                # Add comment
                c.insertText(sym + " " + text)

        cursor.endEditBlock()

    def convert_case_upper(self):
        """Convert selected text (or current word) to UPPERCASE (Ctrl+Shift+U)."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        if cursor.hasSelection():
            start = cursor.selectionStart()
            text = cursor.selectedText()
            cursor.insertText(text.upper())
            cursor.setPosition(start)
            cursor.setPosition(start + len(text), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)

    def convert_case_lower(self):
        """Convert selected text (or current word) to lowercase (Ctrl+U)."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        if cursor.hasSelection():
            start = cursor.selectionStart()
            text = cursor.selectedText()
            cursor.insertText(text.lower())
            cursor.setPosition(start)
            cursor.setPosition(start + len(text), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)

    def convert_case_title(self):
        """Convert selected text (or current word) to Title Case."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        if cursor.hasSelection():
            start = cursor.selectionStart()
            text = cursor.selectedText()
            cursor.insertText(text.title())
            cursor.setPosition(start)
            cursor.setPosition(start + len(text), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)

    def trim_trailing_spaces(self):
        """Trim trailing spaces on all lines."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        doc = self.document()
        for i in range(doc.blockCount()):
            block = doc.findBlockByNumber(i)
            text = block.text()
            rstripped = text.rstrip(' \t')
            if len(text) != len(rstripped):
                c = QTextCursor(doc)
                c.setPosition(block.position())
                c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                c.insertText(rstripped)
        cursor.endEditBlock()

    def sort_lines_ascending(self):
        """Sort selected lines or entire document alphabetically."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        if cursor.hasSelection():
            lines = cursor.selectedText().split('\u2029')
            lines.sort()
            cursor.insertText('\n'.join(lines))
        else:
            lines = self.toPlainText().split('\n')
            lines.sort()
            self.setPlainText('\n'.join(lines))
        cursor.endEditBlock()

    def go_to_line(self, line_number: int):
        """Go to line number (1-based)."""
        line_number = max(1, min(self.blockCount(), line_number))
        block = self.document().findBlockByNumber(line_number - 1)
        cursor = QTextCursor(block)
        self.setTextCursor(cursor)
        self.centerCursor()
