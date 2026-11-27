#!/bin/bash
# Makes the folder buttons in the EPG logo dashboard open THIS copy's raw folder (for your Linux user only).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="$(cd "$HERE/../.." && pwd)/raw"
[ -d "$RAW" ] || { echo "Can't find the raw folder. Keep this folder at tools/folder-button inside the project."; exit 1; }
chmod +x "$HERE/open-raw.sh"
DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$DIR"
cat > "$DIR/roxie-raw.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Roxie raw folder
Exec="$HERE/open-raw.sh" %u
NoDisplay=true
MimeType=x-scheme-handler/roxie-raw;
EOF
xdg-mime default roxie-raw.desktop x-scheme-handler/roxie-raw
update-desktop-database "$DIR" >/dev/null 2>&1 || true
echo "Done. The folder buttons now open: $RAW"
