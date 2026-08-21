#!/usr/bin/env bash
# Notepad++ Linux Desktop Installation Script
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Notepad++ Linux kuruluyor..."

# 1. Ensure directories exist
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"

# 2. Link binary
ln -sf "$DIR/bin/notepad-plus-plus" "$HOME/.local/bin/notepad-plus-plus"
ln -sf "$DIR/bin/notepad-plus-plus" "$HOME/.local/bin/npp"

# 3. Copy Icon
cp "$DIR/npp_linux/resources/icons/notepad-plus-plus.png" "$HOME/.local/share/icons/hicolor/128x128/apps/notepad-plus-plus.png"

# 4. Install Desktop Entry
sed -e "s|@INSTALL_DIR@|$DIR|g" "$DIR/notepad-plus-plus.desktop" > "$HOME/.local/share/applications/notepad-plus-plus.desktop"
chmod +x "$HOME/.local/share/applications/notepad-plus-plus.desktop"

# 5. Update Desktop Database if available
if which update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" || true
fi

echo "Kurulum tamamlandı!"
echo "Terminalden 'notepad-plus-plus' veya 'npp' yazarak veya Uygulamalar menünüzden başlatabilirsiniz."
