# Notepad++ for Linux (Native Qt Edition) 🦎

A high-performance, native source code and text editor for Linux operating systems, inspired by and based on the official [Notepad++](https://github.com/notepad-plus-plus/notepad-plus-plus) repository, featuring authentic icons, color themes, and multi-language support.

![Notepad++ Chameleon Logo](npp_linux/resources/icons/notepad-plus-plus.png)

---

## 🌟 Key Features

### 📝 1. Advanced Code & Text Editor
- **Custom Gutter & Margins**:
  - Line numbers with active line highlighting.
  - **Bookmarks**: Authentic blue spherical bookmark icons. Toggle by clicking the margin or pressing `Ctrl+F2`; navigate with `F2` (Next) / `Shift+F2` (Previous).
  - **Code Folding**: Expand and collapse functions, classes, and indented blocks with `[+]` and `[-]` indicators.
- **Word Wrap** & **Indentation Guides** (vertical dotted guidelines).
- **Whitespace & EOL Symbols**: Display space dots, tab arrows, and line endings (`[CRLF]`, `[LF]`).
- **Fast Editing Shortcuts**:
  - Duplicate Line: `Ctrl+D`
  - Move Line Up / Down: `Ctrl+Shift+Up` / `Ctrl+Shift+Down`
  - Delete Current Line: `Ctrl+Shift+L`
  - Toggle Line / Block Comment: `Ctrl+K` or `Ctrl+Q`
  - Case Conversions: UPPERCASE (`Ctrl+Shift+U`), lowercase (`Ctrl+U`), Title Case
  - Sort Lines (A-Z) & Trim Trailing Whitespace
  - Matching Bracket Highlight (`()`, `[]`, `{}`) & Smart Word Highlighting

### 📑 2. Multi-Tab Management & Dual View (Split Screen)
- **Authentic Notepad++ Tab Bar**:
  - 💾 **Blue Floppy Disk**: Saved document.
  - 🔴 **Red Floppy Disk**: Modified / unsaved document.
  - 🔒 **Lock Icon**: Read-only document.
- **Tab Context Menu & Actions**: Middle-click to close, Close Others, Close to the Right / Left, Open Containing Folder, Copy File Path.
- **Split Screen / Dual View**:
  - *Move to Other View* (Horizontal / Vertical Split)
  - *Clone to Other View* (Simultaneous synchronized dual editing)

### 🔍 3. 4-Tab Advanced Find & Replace
- **Find**: `Ctrl+F` (Find Next `F3`, Find Prev `Shift+F3`, Count occurrences)
- **Replace**: `Ctrl+H` (Replace Single, Replace All)
- **Find in Files**: `Ctrl+Shift+F` (Directory-wide recursive search with file filters e.g. `*.py;*.cpp;*.txt`, results panel)
- **Mark**: Highlight all occurrences across the document with customizable highlighter overlay.
- **Search Modes**: Normal, Extended (`\n`, `\r`, `\t`, `\0`), and Regular Expression (Regex).

### 🌐 4. Encoding & Line Ending Conversion
- **Automatic Encoding Detection** via `chardet` (`UTF-8`, `UTF-8 with BOM`, `Turkish Windows-1254`, `ISO-8859-9`, `UTF-16 LE/BE`, `ANSI`, `ASCII`, etc.).
- **Live Line Ending Converter**: `Windows (CR LF)` ⮀ `Unix (LF)` ⮀ `Macintosh (CR)`.
- **6-Panel Status Bar**: Position (Ln/Col/Sel), Length/Line Count, EOL Format, Encoding, Language, INS/OVR Mode.

### 🎨 5. Themes & Style Configurator
- **Official Notepad++ Themes**:
  - `Classic Default`
  - `DarkModeDefault`
  - `Monokai`
  - `Bespin`
  - `Obsidian`
  - `Zenburn`
  - `Deep Black`
- **Dark Mode UI**: Sleek dark toolbars, tabs, menus, and status bar.
- Custom Monospace font family and font size selection.

### 📌 6. Dock Panels
- **Document Map (Minimap)**: Real-time miniature code overview with interactive viewport slider.
- **Function List**: Tree view of classes, methods, and functions with instant jump-to-line on double-click.
- **Folder as Workspace / File Browser**: Project workspace tree explorer.
- **Search Results Panel**: Docked results output with clickable file paths and line snippets.

### ⚡ 7. Macro Engine & External Run
- **Macro Engine**: Start Recording (`Ctrl+Shift+R`), Stop Recording (`Ctrl+Shift+S`), Playback (`Ctrl+Shift+P`), Run Multiple Times.
- **Run External Commands**: Run Python, Bash scripts, or open in browser with `F5`.

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- PyQt5
- Pygments
- chardet
- Pillow

On Ubuntu / Debian:
```bash
sudo apt update
sudo apt install python3-pyqt5 python3-pygments python3-chardet python3-pil
```

### Installation
```bash
# Clone the repository:
git clone https://github.com/turkerpro/notepad-plus-plus-linux.git
cd notepad-plus-plus-linux

# Run the installation script:
./install.sh
```

### Launching Notepad++
```bash
# From terminal:
notepad-plus-plus
# or using the shortcut:
npp

# Open specific files:
npp main.py

# Open a file at a specific line number:
npp -n 42 main.py
```
You can also launch Notepad++ directly from your desktop **Applications Menu**.

---

## 📁 Project Structure

```
notepad-plus-plus-linux/
├── npp_linux/
│   ├── core/              # Editor, Encoding, Highlighter, Macro, Document & Session
│   ├── ui/                # Main Window, Tabs, Toolbars, Status Bar, Search, Dock Panels
│   ├── resources/         # Official NPP Icons, XML Themes, Localization files
│   └── styles/            # Dark / Light UI Stylesheets and Themes
├── bin/
│   └── notepad-plus-plus  # Executable Launcher Script
├── tests/                 # Unit & Integration Test Suite
├── install.sh             # Desktop & System Integration Installer
└── notepad-plus-plus.desktop # Linux Desktop Launcher Entry
```

---

## 🧪 Running Tests

To run the automated test suite:
```bash
export PYTHONPATH=".:$PYTHONPATH"
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## ⚖️ License

This project is licensed under the **GNU General Public License v3** (GPLv3), in alignment with the original Notepad++ project.
Original Notepad++ Copyright (C) Don HO <don.h@free.fr> and Notepad++ contributors.
