"""
Syntax Highlighter for Notepad++ Linux using Pygments lexers and Notepad++ color themes.
"""
from typing import Dict, Any, Optional
from PyQt5.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextDocument
)
from PyQt5.QtCore import Qt

from pygments.lexers import get_lexer_by_name, find_lexer_class_by_name
from pygments.token import (
    Token, Comment, Keyword, Name, String, Number, Operator, Punctuation, Text, Generic
)


# Language Name to Pygments Lexer alias
LANG_TO_LEXER = {
    "Plain Text": None,
    "Python": "python",
    "C": "c",
    "C++": "cpp",
    "C/C++ Header": "cpp",
    "C++ Header": "cpp",
    "C#": "csharp",
    "Java": "java",
    "JavaScript": "javascript",
    "React JSX": "jsx",
    "TypeScript": "typescript",
    "React TSX": "tsx",
    "HTML": "html",
    "XML": "xml",
    "XML/SVG": "xml",
    "CSS": "css",
    "SCSS": "scss",
    "Sass": "sass",
    "Less": "less",
    "JSON": "json",
    "YAML": "yaml",
    "Bash/Shell": "bash",
    "Zsh": "zsh",
    "SQL": "sql",
    "PHP": "php",
    "Ruby": "ruby",
    "Rust": "rust",
    "Go": "go",
    "Lua": "lua",
    "Perl": "perl",
    "Markdown": "markdown",
    "INI Config": "ini",
    "Configuration": "ini",
    "TOML": "toml",
    "Batch": "bat",
    "PowerShell": "powershell",
    "Diff": "diff",
    "R": "r",
    "Dart": "dart",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Assembly": "nasm",
    "CMake": "cmake",
    "Makefile": "makefile",
    "Dockerfile": "docker",
}


class NppHighlighter(QSyntaxHighlighter):
    """Multi-language syntax highlighter styled with Notepad++ theme palettes."""

    def __init__(self, document: QTextDocument, language: str = "Plain Text", theme_colors: Optional[Dict[str, str]] = None):
        super().__init__(document)
        self.language = language
        self.theme_colors = theme_colors or {}
        self.lexer = None
        self._formats: Dict[Any, QTextCharFormat] = {}
        self._highlight_word = ""
        self._highlight_format = QTextCharFormat()
        self._highlight_format.setBackground(QColor("#50FF8000" if "dark" in str(theme_colors).lower() else "#A0FFEC8B"))

        self.set_language(language)

    def set_theme(self, theme_colors: Dict[str, str]):
        self.theme_colors = theme_colors
        self._rebuild_formats()
        self.rehighlight()

    def set_language(self, language: str):
        self.language = language
        lexer_name = LANG_TO_LEXER.get(language)
        if lexer_name:
            try:
                self.lexer = get_lexer_by_name(lexer_name, stripnl=False)
            except Exception:
                self.lexer = None
        else:
            self.lexer = None
        self._rebuild_formats()
        self.rehighlight()

    def set_search_highlight_word(self, word: str):
        if self._highlight_word != word:
            self._highlight_word = word
            self.rehighlight()

    def _rebuild_formats(self):
        self._formats.clear()
        tc = self.theme_colors

        kw_color = QColor(tc.get("keyword", "#0000FF"))
        fn_color = QColor(tc.get("function", "#95004A"))
        tp_color = QColor(tc.get("type", "#8000FF"))
        str_color = QColor(tc.get("string", "#808080"))
        num_color = QColor(tc.get("number", "#FF8000"))
        com_color = QColor(tc.get("comment", "#008000"))
        op_color = QColor(tc.get("operator", "#000080"))
        prep_color = QColor(tc.get("preprocessor", "#804000"))
        tag_color = QColor(tc.get("tag", "#000080"))
        attr_color = QColor(tc.get("attribute", "#FF0000"))

        def make_fmt(color: QColor, bold: bool = False, italic: bool = False) -> QTextCharFormat:
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            if bold:
                fmt.setFontWeight(QFont.Bold)
            if italic:
                fmt.setFontItalic(True)
            return fmt

        # Keywords
        kw_fmt = make_fmt(kw_color, bold=True)
        self._formats[Keyword] = kw_fmt
        self._formats[Keyword.Constant] = kw_fmt
        self._formats[Keyword.Declaration] = kw_fmt
        self._formats[Keyword.Namespace] = kw_fmt
        self._formats[Keyword.Pseudo] = kw_fmt
        self._formats[Keyword.Reserved] = kw_fmt
        self._formats[Keyword.Type] = make_fmt(tp_color, bold=True)

        # Names / Functions / Classes
        self._formats[Name.Function] = make_fmt(fn_color)
        self._formats[Name.Class] = make_fmt(tp_color, bold=True)
        self._formats[Name.Builtin] = make_fmt(fn_color)
        self._formats[Name.Builtin.Pseudo] = make_fmt(kw_color)
        self._formats[Name.Tag] = make_fmt(tag_color, bold=True)
        self._formats[Name.Attribute] = make_fmt(attr_color)
        self._formats[Name.Decorator] = make_fmt(prep_color, italic=True)

        # Literals
        self._formats[String] = make_fmt(str_color)
        self._formats[String.Doc] = make_fmt(com_color, italic=True)
        self._formats[String.Escape] = make_fmt(num_color, bold=True)
        self._formats[String.Regex] = make_fmt(num_color)
        self._formats[Number] = make_fmt(num_color)

        # Comments
        self._formats[Comment] = make_fmt(com_color, italic=True)
        self._formats[Comment.Single] = make_fmt(com_color, italic=True)
        self._formats[Comment.Multiline] = make_fmt(com_color, italic=True)
        self._formats[Comment.Preproc] = make_fmt(prep_color)

        # Operators
        self._formats[Operator] = make_fmt(op_color, bold=True)
        self._formats[Operator.Word] = make_fmt(kw_color, bold=True)
        self._formats[Punctuation] = make_fmt(op_color)

        # Generic / Diff
        self._formats[Generic.Inserted] = make_fmt(QColor("#00AA00"))
        self._formats[Generic.Deleted] = make_fmt(QColor("#FF0000"))
        self._formats[Generic.Heading] = make_fmt(QColor("#0000FF"), bold=True)

    def highlightBlock(self, text: str):
        if not text:
            return

        # Syntax token highlighting
        if self.lexer:
            tokens = self.lexer.get_tokens_unprocessed(text)
            for index, token_type, token_value in tokens:
                fmt = self._get_format_for_token(token_type)
                if fmt:
                    self.setFormat(index, len(token_value), fmt)

        # Smart occurrence highlighting (e.g. for search / selected word)
        if self._highlight_word and len(self._highlight_word) >= 2:
            start = 0
            w_len = len(self._highlight_word)
            lower_text = text.lower()
            lower_word = self._highlight_word.lower()
            while True:
                idx = lower_text.find(lower_word, start)
                if idx == -1:
                    break
                # Apply highlight overlay
                cur_fmt = self.format(idx)
                overlay = QTextCharFormat(cur_fmt)
                overlay.setBackground(self._highlight_format.background())
                self.setFormat(idx, w_len, overlay)
                start = idx + w_len

    def _get_format_for_token(self, token_type):
        while token_type:
            if token_type in self._formats:
                return self._formats[token_type]
            token_type = token_type.parent
        return None
