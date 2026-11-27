#!/bin/bash
# Makes the folder buttons in the EPG logo dashboard open THIS copy's raw folder in Finder (for your Mac user only).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="$(cd "$HERE/../.." && pwd)/raw"
[ -d "$RAW" ] || { echo "Can't find the raw folder. Keep this folder at tools/folder-button inside the project."; exit 1; }
chmod +x "$HERE/open-raw.sh"
APP="$HOME/Applications/Roxie Raw Folder.app"
mkdir -p "$HOME/Applications"
rm -rf "$APP"
SCRIPT="$(mktemp -t roxieraw)"
cat > "$SCRIPT" <<EOF
on open location theURL
	do shell script "/bin/bash " & quoted form of "$HERE/open-raw.sh" & " " & quoted form of theURL & " >/dev/null 2>&1 &"
end open location
EOF
osacompile -o "$APP" "$SCRIPT"
rm -f "$SCRIPT"
PL="$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Delete :CFBundleURLTypes" "$PL" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes array" -c "Add :CFBundleURLTypes:0 dict" \
  -c "Add :CFBundleURLTypes:0:CFBundleURLName string Roxie raw folder" \
  -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string roxie-raw" "$PL"
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier info.roxiestreams.rawfolder" "$PL" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string info.roxiestreams.rawfolder" "$PL"
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PL" >/dev/null 2>&1 || true
codesign --force --sign - "$APP" >/dev/null 2>&1 || true
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP"
echo "Done. The folder buttons now open: $RAW"
